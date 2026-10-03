import hashlib
import hmac
import asyncio
import json
import logging
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from redis import Redis

from .config import ALLOWED_ORIGINS, API_TOKEN, API_TOKENS, REDIS_URL
from .db import Base, SessionLocal, engine
from .models import Event, Outbox, State, Task
from .schemas import Submission, TaskCreate, TaskView

logging.basicConfig(level=logging.INFO, format='%(message)s')
log = logging.getLogger("openeval.api")


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(engine)
    yield


app = FastAPI(title="OpenEval API", version="0.1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=ALLOWED_ORIGINS, allow_methods=["GET", "POST"], allow_headers=["Authorization", "Idempotency-Key", "Content-Type", "X-Correlation-ID"])


@app.middleware("http")
async def trace(request: Request, call_next):
    correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
    start = time.monotonic()
    if request.url.path != "/health":
        try:
            client_id = request.client.host if request.client else "unknown"
            rate_key = f"rate:{client_id}:{int(time.time() // 60)}"
            count = Redis.from_url(REDIS_URL, socket_timeout=1, socket_connect_timeout=1).incr(rate_key)
            if count == 1:
                Redis.from_url(REDIS_URL, socket_timeout=1, socket_connect_timeout=1).expire(rate_key, 120)
            if count > 120:
                return JSONResponse(status_code=429, content={"error": {"code": "rate_limit", "message": "Too many requests"}})
        except Exception:
            return JSONResponse(status_code=503, content={"error": {"code": "unavailable", "message": "Rate limiter unavailable"}})
    try:
        response = await call_next(request)
    except Exception:
        log.exception(json.dumps({"event": "request_failed", "correlation_id": correlation_id, "path": request.url.path}))
        raise
    response.headers["X-Correlation-ID"] = correlation_id
    log.info(json.dumps({"event": "request", "correlation_id": correlation_id, "path": request.url.path, "status": response.status_code, "duration_ms": round((time.monotonic() - start) * 1000, 2)}))
    return response


@app.exception_handler(HTTPException)
async def http_error(_: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"error": {"code": str(exc.status_code), "message": str(exc.detail)}})


@app.exception_handler(RequestValidationError)
async def validation_error(_: Request, exc: RequestValidationError):
    return JSONResponse(status_code=400, content={"error": {"code": "validation", "message": str(exc.errors())}})


@app.exception_handler(Exception)
async def unexpected_error(request: Request, exc: Exception):
    log.exception(json.dumps({"event": "unhandled_error", "path": request.url.path, "error_type": type(exc).__name__}))
    return JSONResponse(status_code=500, content={"error": {"code": "internal", "message": "Internal server error"}})


def db_session():
    with SessionLocal() as session:
        yield session


def tenant(authorization: str = Header(default="")) -> str:
    if API_TOKEN and hmac.compare_digest(authorization, f"Bearer {API_TOKEN}"):
        return "demo"
    for tenant_id, token in API_TOKENS.items():
        if token and hmac.compare_digest(authorization, f"Bearer {token}"):
            return tenant_id
    raise HTTPException(401, "Invalid API token")


def get_task(session: Session, task_id: str, tenant_id: str, lock: bool = False) -> Task:
    query = select(Task).where(Task.id == task_id, Task.tenant_id == tenant_id)
    task = session.scalar(query.with_for_update() if lock else query)
    if task is None:
        raise HTTPException(404, "Task not found")
    return task


def check_dependencies():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    Redis.from_url(REDIS_URL, socket_timeout=1, socket_connect_timeout=1).ping()


@app.get("/health")
async def health():
    try:
        await asyncio.wait_for(asyncio.to_thread(check_dependencies), timeout=2)
        return {"status": "ok"}
    except Exception:
        return JSONResponse(status_code=503, content={"status": "unhealthy"})


@app.post("/tasks", response_model=TaskView, status_code=201)
def create_task(payload: TaskCreate, idempotency_key: str = Header(min_length=1, max_length=128), tenant_id: str = Depends(tenant), session: Session = Depends(db_session)):
    canonical = payload.model_dump(mode="json")
    request_hash = hashlib.sha256(json.dumps(canonical, sort_keys=True).encode()).hexdigest()
    task = Task(tenant_id=tenant_id, idempotency_key=idempotency_key, request_hash=request_hash, spec=canonical)
    session.add(task)
    try:
        session.flush()
        session.add(Event(task_id=task.id, state=State.created, detail="task created"))
        session.commit()
    except IntegrityError:
        session.rollback()
        previous = session.scalar(select(Task).where(Task.tenant_id == tenant_id, Task.idempotency_key == idempotency_key))
        if previous is None or previous.request_hash != request_hash:
            raise HTTPException(409, "Idempotency key reused with different request")
        return previous
    return task


@app.get("/tasks/{task_id}", response_model=TaskView)
def read_task(task_id: str, tenant_id: str = Depends(tenant), session: Session = Depends(db_session)):
    return get_task(session, task_id, tenant_id)


@app.post("/tasks/{task_id}/submit", response_model=TaskView)
def submit(task_id: str, payload: Submission, tenant_id: str = Depends(tenant), session: Session = Depends(db_session)):
    task = get_task(session, task_id, tenant_id, lock=True)
    submission = payload.model_dump()
    if task.submission is not None:
        if task.submission == submission:
            return task
        raise HTTPException(409, "Task already submitted with different payload")
    if task.state != State.created:
        raise HTTPException(409, "Task cannot be submitted")
    task.submission = submission
    task.state = State.queued
    session.add(Event(task_id=task.id, state=State.queued, detail="submitted"))
    session.add(Outbox(task_id=task.id))
    session.commit()
    return task


@app.get("/tasks/{task_id}/result")
def result(task_id: str, offset: int = Query(default=0, ge=0), limit: int = Query(default=20, ge=1, le=100), tenant_id: str = Depends(tenant), session: Session = Depends(db_session)):
    task = get_task(session, task_id, tenant_id)
    result_data = task.result
    pagination = None
    if result_data is not None:
        checks = result_data.get("checks", [])
        result_data = {**result_data, "checks": checks[offset:offset + limit]}
        pagination = {"offset": offset, "limit": limit, "total": len(checks), "has_more": offset + limit < len(checks)}
    return {"task_id": task.id, "state": task.state, "result": result_data, "pagination": pagination, "error": task.error}


@app.get("/tasks/{task_id}/events")
def events(task_id: str, tenant_id: str = Depends(tenant), session: Session = Depends(db_session)):
    get_task(session, task_id, tenant_id)
    rows = session.scalars(select(Event).where(Event.task_id == task_id).order_by(Event.id)).all()
    return [{"state": row.state, "detail": row.detail, "created_at": row.created_at} for row in rows]
