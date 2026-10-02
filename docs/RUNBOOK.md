# Runbook

## Start and inspect

1. Set `API_TOKEN` and `POSTGRES_PASSWORD` in `.env`.
2. Run `docker compose -f infra/docker/compose.yml up --build -d --wait`.
3. Check `http://localhost:8000/health` and `http://localhost:8080`.
4. Inspect `docker compose -f infra/docker/compose.yml logs -f worker api-python`.

Logs are JSON lines containing `event`, `task_id` where applicable, correlation ID for HTTP requests, status and duration. Query `/tasks/{id}/events` for committed state transitions.

## Diagnose a stuck task

Check API health, database and Redis health, worker logs, then task events. `retry_wait` returns to the queue when `next_run_at` is due. A `running` task is recovered after the lease timeout. `dead_letter` is terminal in this demo; create a new task with a new idempotency key after fixing the cause.

## Rollback

Keep the previous container image tag. Revert the deployment commit, rebuild or pull the prior image, and start Compose. Database schema changes must be backwards compatible. This version uses `create_all`, so a production rollout would need migrations and a backup before schema changes.

## Cloud

See [AWS deployment](../infra/aws/README.md). Do not put `.env` in Git or expose PostgreSQL and Redis ports.
