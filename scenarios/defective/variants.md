# Intentionally defective variants

- `defective_duplicate` accepts duplicate IDs, violating idempotency.
- `defective_validation` stores invalid IDs and fails to count rejected inputs.

These are pure functions selected by name. Users cannot upload executable code. The deterministic validator compares them with the golden output on fixed fixtures and reports each mismatch.
