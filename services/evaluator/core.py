"""Deterministic, fixture based software evaluation. No model judgment is used for scoring."""
from dataclasses import dataclass
from typing import Any, Protocol

from .review import local_mock_review


@dataclass(frozen=True)
class Check:
    name: str
    passed: bool
    reason: str


def golden(events: list[dict[str, Any]]) -> dict[str, Any]:
    seen: set[str] = set()
    stored: list[str] = []
    rejected = 0
    for event in events:
        event_id, amount = event.get("id"), event.get("amount")
        if not isinstance(event_id, str) or not event_id or type(amount) not in (int, float) or amount < 0:
            rejected += 1
        elif event_id not in seen:
            seen.add(event_id)
            stored.append(event_id)
    return {"stored_ids": stored, "stored_count": len(stored), "rejected_count": rejected}


def defective_duplicate(events: list[dict[str, Any]]) -> dict[str, Any]:
    stored = [e["id"] for e in events if isinstance(e.get("id"), str) and isinstance(e.get("amount"), (int, float))]
    return {"stored_ids": stored, "stored_count": len(stored), "rejected_count": len(events) - len(stored)}


def defective_validation(events: list[dict[str, Any]]) -> dict[str, Any]:
    seen = list(dict.fromkeys(str(e.get("id")) for e in events))
    return {"stored_ids": seen, "stored_count": len(seen), "rejected_count": 0}


class EvaluatorStrategy(Protocol):
    def evaluate(self, events: list[dict[str, Any]]) -> dict[str, Any]: ...


@dataclass(frozen=True)
class GoldenEvaluator:
    def evaluate(self, events: list[dict[str, Any]]) -> dict[str, Any]:
        return golden(events)


@dataclass(frozen=True)
class DefectiveDuplicateEvaluator:
    def evaluate(self, events: list[dict[str, Any]]) -> dict[str, Any]:
        return defective_duplicate(events)


@dataclass(frozen=True)
class DefectiveValidationEvaluator:
    def evaluate(self, events: list[dict[str, Any]]) -> dict[str, Any]:
        return defective_validation(events)


class EvaluatorRegistry:
    """Maps supported implementation identifiers to interchangeable strategies."""

    def __init__(self, strategies: dict[str, EvaluatorStrategy] | None = None):
        self._strategies = strategies or {
            "golden": GoldenEvaluator(),
            "defective_duplicate": DefectiveDuplicateEvaluator(),
            "defective_validation": DefectiveValidationEvaluator(),
        }

    def get(self, implementation: str) -> EvaluatorStrategy:
        try:
            return self._strategies[implementation]
        except KeyError as exc:
            raise ValueError("Unknown implementation") from exc


REGISTRY = EvaluatorRegistry()
FIXTURES = [
    ("valid", [{"id": "a", "amount": 10}, {"id": "b", "amount": 0}]),
    ("duplicate", [{"id": "a", "amount": 10}, {"id": "a", "amount": 10}]),
    ("invalid", [{"id": "", "amount": 1}, {"id": "b", "amount": -1}, {"id": "c", "amount": "3"}]),
    ("mixed", [{"id": "x", "amount": 3}, {"id": "x", "amount": 3}, {"id": "y", "amount": -2}]),
]
EXPECTED = {name: golden(events) for name, events in FIXTURES}


def evaluate(implementation: str, supplied: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    strategy = REGISTRY.get(implementation)
    fixtures = list(FIXTURES)
    if supplied is not None:
        fixtures.append(("submitted_input", supplied))
    checks: list[Check] = []
    for name, events in fixtures:
        expected = EXPECTED[name] if name in EXPECTED else golden(events)
        try:
            actual = strategy.evaluate(events)
            checks.append(Check(name, actual == expected, "ok" if actual == expected else f"expected {expected}; got {actual}"))
        except Exception as exc:
            checks.append(Check(name, False, f"raised {type(exc).__name__}"))
    passed = sum(check.passed for check in checks)
    check_rows = [check.__dict__ for check in checks]
    return {"implementation": implementation, "score": passed / len(checks), "passed": passed, "total": len(checks), "checks": check_rows, "review": local_mock_review(check_rows)}
