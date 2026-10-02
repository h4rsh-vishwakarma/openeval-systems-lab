# Synthetic incident: evaluator timeout

Scenario: a submitted task injects a transient timeout. Initial state: `queued`. The first worker attempt enters `running` and raises `TimeoutError`. Observed by design: `retry_wait` with a stored error and scheduled backoff. Recovery: the sweep returns it to `queued`; the second attempt completes. Permanent timeouts reach `dead_letter` after `MAX_ATTEMPTS`. Duplicate queue messages are ignored when the task is not `queued`.

Root cause in this exercise is deliberate failure injection. The permanent fix for a real external evaluator would include a bounded timeout, provider health checks, a circuit breaker, and an idempotency key on any side effect. Test: `tests/integration/test_workflow.py::test_retry_and_dead_letter`. This is a synthetic report, not a production incident.
