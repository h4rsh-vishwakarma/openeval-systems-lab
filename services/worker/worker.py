import json
import logging
import os
import time
from datetime import datetime, timedelta, timezone

from redis import Redis
from sqlalchemy import select

from app.config import MAX_ATTEMPTS, REDIS_URL, TASK_TIMEOUT_SECONDS
from app.db import Base, SessionLocal, engine
from app.models import Event, Outbox, State, Task, now
from evaluator.core import evaluate

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger("openeval.worker")
redis = Redis.from_url(REDIS_URL, decode_responses=True)
QUEUE = "openeval:tasks"


def emit(event: str, task_id: str, **details):
    log.info(json.dumps({"event": event, "task_id": task_id, **details}))


def dispatch():
    # Replaying after a crash can enqueue twice; state locking makes duplicate delivery harmless.
    with SessionLocal.begin() as session:
        rows = session.scalars(select(Outbox).where(Outbox.published_at.is_(None)).order_by(Outbox.id).limit(50).with_for_update(skip_locked=True)).all()
        for row in rows:
            redis.lpush(QUEUE, row.task_id)
            row.published_at = now()
            emit("enqueued", row.task_id)


def recover():
    current = now()
    with SessionLocal.begin() as session:
        rows = session.scalars(select(Task).where(
            ((Task.state == State.retry_wait) & (Task.next_run_at <= current)) |
            ((Task.state == State.running) & (Task.started_at <= current - timedelta(seconds=TASK_TIMEOUT_SECONDS)))
        ).limit(50).with_for_update(skip_locked=True)).all()
        for task in rows:
            if task.state == State.running and task.attempts >= MAX_ATTEMPTS:
                task.state = State.dead_letter
                task.error = "Worker lease expired after maximum attempts"
                session.add(Event(task_id=task.id, state=State.dead_letter, detail=task.error))
                continue
            task.state = State.queued
            task.next_run_at = None
            session.add(Event(task_id=task.id, state=State.queued, detail="retry or lease recovery"))
            session.add(Outbox(task_id=task.id))


def process(task_id: str):
    with SessionLocal.begin() as session:
        task = session.scalar(select(Task).where(Task.id == task_id).with_for_update())
        if task is None or task.state != State.queued:
            emit("duplicate_ignored", task_id)
            return
        task.state = State.running
        queue_latency_ms = round((now() - task.updated_at).total_seconds() * 1000, 2)
        task.attempts += 1
        task.started_at = now()
        session.add(Event(task_id=task.id, state=State.running, detail=f"attempt {task.attempts}"))
        attempt = task.attempts
        submission = task.submission
        spec = task.spec
    emit("started", task_id, attempt=attempt, queue_latency_ms=queue_latency_ms)
    try:
        failure = submission.get("inject_failure", "none")
        if failure == "timeout" or (failure == "transient" and attempt == 1):
            raise TimeoutError("Injected evaluator timeout")
        events = spec.get("input", {}).get("events")
        if events is not None and (not isinstance(events, list) or any(not isinstance(e, dict) for e in events)):
            raise ValueError("input.events must be a list of objects")
        result = evaluate(submission["implementation"], events)
        if failure == "invalid_output":
            raise ValueError("Injected invalid evaluator output")
        with SessionLocal.begin() as session:
            task = session.scalar(select(Task).where(Task.id == task_id).with_for_update())
            if task.state != State.running or task.attempts != attempt:
                return
            task.result = result
            task.state = State.completed
            task.error = None
            session.add(Event(task_id=task.id, state=State.completed, detail="evaluation complete"))
        emit("completed", task_id, score=result["score"])
    except (TimeoutError, ValueError) as exc:
        with SessionLocal.begin() as session:
            task = session.scalar(select(Task).where(Task.id == task_id).with_for_update())
            if task.state != State.running or task.attempts != attempt:
                return
            task.error = str(exc)
            task.state = State.dead_letter if attempt >= MAX_ATTEMPTS or isinstance(exc, ValueError) else State.retry_wait
            if task.state == State.retry_wait:
                task.next_run_at = now() + timedelta(seconds=min(60, 2 ** attempt))
            session.add(Event(task_id=task.id, state=task.state, detail=task.error[:256]))
        emit("failed", task_id, attempt=attempt, error=str(exc))


def main():
    Base.metadata.create_all(engine)
    while True:
        try:
            recover()
            dispatch()
            item = redis.brpop(QUEUE, timeout=2)
            if item:
                process(item[1])
        except Exception as exc:
            log.exception(json.dumps({"event": "worker_loop_error", "error": str(exc)}))
            time.sleep(2)


if __name__ == "__main__":
    main()
