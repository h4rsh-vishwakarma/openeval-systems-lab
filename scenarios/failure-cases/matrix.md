# Failure matrix

| Scenario | Initial state | Injection | Expected recovery | Test |
|---|---|---|---|---|
| Duplicate create | none | same idempotency key | same task ID | integration workflow |
| Conflicting replay | created | same key, different body | HTTP 409 | integration workflow |
| Duplicate submit | queued | same payload | unchanged task | integration workflow |
| Transient timeout | queued | first attempt timeout | retry, then complete | retry and dead letter |
| Persistent timeout | queued | every attempt timeout | dead letter at limit | manual/UI scenario |
| Invalid evaluator output | running | invalid output flag | dead letter | retry and dead letter |
| Worker stopped | queued | stop worker process | task completes once after restart | `scripts/failure_drill.py` |
| Redis unavailable | queued | stop Redis | health 503 then 200 after restore | `scripts/failure_drill.py` |
| Database unavailable | any | stop PostgreSQL | health 503 then 200 after restore | `scripts/failure_drill.py` |
| Malformed pipeline row | raw | bad range or field | quarantine and reconcile | pipeline test |
| Conflicting duplicate row | raw | same ID, different data | quarantine both | pipeline code |

The outage drill stops and restarts local Compose services and restores each service in a `finally` block. It does not delete volumes. See `docs/RUNBOOK.md` for inspection and recovery.
