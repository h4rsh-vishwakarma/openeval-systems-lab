# Verification record

## Focused change and acceptance criteria

The selected improvement is a stable, non-leaking API validation error and regression coverage for invalid request boundaries. Acceptance criteria:

- Schema and required-header errors return HTTP 400 with `{"error":{"code":"validation","message":"Invalid request"}}`.
- Validation responses do not include submitted field values.
- Unknown tasks return HTTP 404 with the documented error envelope.
- Retry behavior reaches completion after one transient failure; permanent invalid output reaches `dead_letter` without retry.

The worker retry/dead-letter acceptance cases already exist in `tests/integration/test_workflow.py`; this change adds the API boundary assertions alongside them. The error message is now deliberately generic because Pydantic validation details can contain the submitted input.

## Test matrix

| Input/failure case | Expected | Automated coverage | Result in this run |
|---|---|---|---|
| Unknown scenario with sensitive extra value | 400 validation envelope, no echoed value | `test_validation_unknown_id_and_defective_variant` | Passed in integration run |
| Missing `Idempotency-Key` | 400 validation envelope | `test_validation_unknown_id_and_defective_variant` | Passed in integration run |
| Unknown implementation | 400 validation envelope | `test_validation_unknown_id_and_defective_variant` | Passed in integration run |
| Unknown task ID | 404 task-not-found envelope | `test_validation_unknown_id_and_defective_variant` | Passed in integration run |
| Transient evaluator failure, then success | Completed after 2 attempts | `test_retry_and_dead_letter` | Passed in integration run |
| Permanent invalid evaluator output | `dead_letter` after 1 attempt | `test_retry_and_dead_letter` | Passed in integration run |
| Golden evaluator repeatability | Identical repeated output, score 1.0 | `test_golden_is_deterministic_and_passes` | Included in unit run |

## Local run evidence

Command: `python -m pytest tests/unit -q`

Result on 2026-10-05: **4 passed, 4 skipped in 0.07s**. Skips include the pipeline suite when optional PySpark/Java dependencies are unavailable and C++ bridge checks when the compiled evaluator binary is absent. This command does not exercise the database/Redis-backed API integration suite.

Command: `$env:API_TOKEN='openeval-local-integration-token-2026'; python -m pytest tests/integration -q`, with the local Compose stack healthy.

Result on 2026-10-05: **5 passed in 27.24s**. This exercised API validation/error envelopes, task workflow, retry, and dead-letter behavior against local PostgreSQL and Redis containers.

Command: `python scripts/benchmark_evaluator.py`

Result: Python 3.10.11 on Windows 10 build 26300, 10,000 evaluations of 100 events, 80 valid unique events and 20 duplicates per iteration, score 1.0, 0.5295 seconds, 18,885.14 evaluations/second. This is one local run, not a production throughput measurement. See [benchmark notes](BENCHMARKS.md).

## Reproduce the integration cases

Install dependencies as described in the root README, create `.env` from `.env.example`, choose local credentials, and run `docker compose -f infra/docker/compose.yml up --build -d --wait`. Set `API_TOKEN` in the shell to the same token as `.env`, then run `python -m pytest tests/integration -q`. The integration cases use PostgreSQL and Redis from Compose and can take up to 30 seconds for persistent timeout recovery.
