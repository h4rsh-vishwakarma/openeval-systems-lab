# ADR 001: PostgreSQL state and Redis delivery

Status: accepted for the demo.

The API commits a task and an outbox row together in PostgreSQL. A worker publishes outbox rows to Redis and consumes task IDs. PostgreSQL remains authoritative; Redis is a delivery mechanism. This design covers the API crash window between persistence and enqueueing. A replay can still produce duplicate queue items, so workers claim only `queued` tasks under a row lock.

Tradeoffs: the worker polls the outbox; queue latency depends on its loop. There is no separate scheduler or dedicated outbox publisher. The result is suitable for a small demonstration and is not a claim of exactly once execution across arbitrary external systems.
