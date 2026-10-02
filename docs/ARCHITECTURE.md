# Architecture

## Task lifecycle

`created → queued → running → completed` or `running → retry_wait → queued`, ending in `dead_letter` after the attempt limit. Each transition is committed with a `task_events` row. The API writes the submission, `queued` state, and outbox row in one PostgreSQL transaction. The worker publishes outbox rows and marks them published. Redis may receive duplicate messages after a crash, so a worker only claims `queued` rows under `SELECT FOR UPDATE`.

The worker consumes with Redis `BRPOP`. A crash after pop leaves a `running` row; a later sweep recovers it after `TASK_TIMEOUT_SECONDS`. The sweep also schedules retries. This gives at least once execution, with duplicate delivery protection for state transitions. Evaluator computations are pure and have no external side effects. A future side effectful evaluator must use its own idempotency ledger.

## Data model

`tasks` has a unique `(tenant_id, idempotency_key)` constraint, a request hash to detect conflicting replays, status and attempt fields, JSON spec/submission/result, and timestamps. `task_events` provides transition history. `outbox` tracks pending queue publication. The API uses a fixed demo tenant named `demo` with a single bearer token.

## Boundaries

The React app calls FastAPI through Nginx `/api`. The TypeScript service is an independent typed gateway/client demonstration. PostgreSQL is authoritative for task state; Redis carries delivery hints. The PySpark batch pipeline is independent and emits Parquet, quarantine records, and a count report. Neither pipeline nor API uses live financial data.

## Recovery

Outbox publication can be repeated. Queue deliveries can be repeated. A stale running task can be reclaimed. These cases are safe because the pure evaluator is repeatable and database state transitions are locked. If the process dies after evaluation but before committing the result, evaluation runs again. Failed Redis or database calls are logged and retried by the worker loop.
