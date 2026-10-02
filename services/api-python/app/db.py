import json
import logging
import time
from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import DATABASE_URL

engine = create_engine(DATABASE_URL, pool_pre_ping=True, connect_args={"connect_timeout": 2})
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
query_log = logging.getLogger("openeval.db")


@event.listens_for(engine, "before_cursor_execute")
def before_query(conn, cursor, statement, parameters, context, executemany):
    conn.info.setdefault("query_starts", []).append(time.perf_counter())


@event.listens_for(engine, "after_cursor_execute")
def after_query(conn, cursor, statement, parameters, context, executemany):
    elapsed_ms = round((time.perf_counter() - conn.info["query_starts"].pop()) * 1000, 2)
    query_log.info(json.dumps({"event": "db_query", "duration_ms": elapsed_ms}))


class Base(DeclarativeBase):
    pass
