"""Small local retrieval and mock review provider; no external model call or code execution."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Rule:
    check: str
    guidance: str
    reference: str


RULES = (
    Rule("duplicate", "Keep a durable event ID ledger and make the downstream operation idempotent.", "scenarios/golden/webhook_once.md"),
    Rule("invalid", "Validate ID and amount before persistence; count rejected records separately.", "scenarios/golden/webhook_once.md"),
    Rule("mixed", "Apply validation before deduplication and preserve first seen order.", "scenarios/golden/webhook_once.md"),
)


def local_mock_review(checks: list[dict]) -> list[dict[str, str]]:
    """Retrieve relevant local rules and compose deterministic review suggestions."""
    failed = {check["name"] for check in checks if not check["passed"]}
    return [{"check": rule.check, "suggestion": rule.guidance, "source": rule.reference, "provider": "local_mock"} for rule in RULES if rule.check in failed]
