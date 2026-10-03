import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from services.evaluator.core import EvaluatorRegistry, GoldenEvaluator, evaluate, golden


def test_golden_is_deterministic_and_passes():
    first = evaluate("golden")
    assert first == evaluate("golden")
    assert first["score"] == 1.0


def test_defective_variants_fail_for_specific_reasons():
    duplicate = evaluate("defective_duplicate")
    validation = evaluate("defective_validation")
    assert duplicate["score"] < 1.0
    assert validation["score"] < 1.0
    assert any(c["name"] == "duplicate" and not c["passed"] for c in duplicate["checks"])
    assert any(c["name"] == "invalid" and not c["passed"] for c in validation["checks"])


def test_golden_rejects_boolean_amount_and_duplicate_id():
    assert golden([{"id": "a", "amount": True}, {"id": "b", "amount": 1}, {"id": "b", "amount": 1}]) == {"stored_ids": ["b"], "stored_count": 1, "rejected_count": 1}


def test_registry_selects_strategies_and_rejects_unknown_names():
    registry = EvaluatorRegistry({"golden": GoldenEvaluator()})
    assert registry.get("golden").evaluate([{"id": "x", "amount": 1}]) == golden([{"id": "x", "amount": 1}])
    try:
        registry.get("missing")
    except ValueError as exc:
        assert str(exc) == "Unknown implementation"
    else:
        raise AssertionError("unknown strategy should fail")
