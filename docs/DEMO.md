# Demo and technical walkthrough

Record a short screen capture after starting Compose. Use synthetic fixtures and show the task ID in each step.

1. Open the React client, select `golden`, create a task, and refresh until `completed` with a 100% score.
2. Repeat the same POST with the same `Idempotency-Key` in a terminal and show the same task ID. Reuse the key with a different body and show HTTP 409.
3. Select `defective_duplicate` and show the failed duplicate check and local mock review guidance.
4. Select `transient` and show two attempts, `retry_wait`, and completion in `/tasks/{id}/events`.
5. Select `invalid_output` and show `dead_letter` with one attempt.
6. Run the PySpark sample, open `data-pipeline/reports/sample.json`, and show the 5 = 2 + 2 + 1 reconciliation.
7. Open the GitHub Actions run for the same commit once the repository is pushed.

Walkthrough talking points: PostgreSQL owns task state; the outbox prevents a persisted task from being lost before queue publication; Redis delivery may replay; row locking and state checks discard duplicate deliveries; evaluation is deterministic; PySpark quarantines bad rows and replaces a full output snapshot on rerun. State that the cloud template is only deployed after independent AWS verification. No video file is included because recording requires an interactive capture and a published CI run.
