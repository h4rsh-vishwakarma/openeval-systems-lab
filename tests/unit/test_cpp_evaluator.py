import json
from pathlib import Path

import pytest

from services.evaluator.cpp import _binary_path, evaluate_cpp_golden
from services.evaluator.core import evaluate, golden


pytestmark = pytest.mark.skipif(not Path(_binary_path()).is_file(), reason="Compile the C++ evaluator before running its bridge tests")


def test_cpp_golden_matches_python_for_valid_duplicate_and_invalid_events():
    events = [
        {"id": "a", "amount": 10},
        {"id": "a", "amount": 10},
        {"id": "b", "amount": 0.5},
        {"id": "", "amount": 1},
        {"id": "negative", "amount": -1},
        {"id": "boolean", "amount": True},
        {"id": "東京", "amount": 2},
    ]
    assert evaluate_cpp_golden(events) == golden(events)


def test_cpp_golden_is_registered_and_passes_the_shared_fixtures():
    result = evaluate("cpp_golden")
    assert result["score"] == 1.0
    assert result["passed"] == result["total"] == 4


def test_cpp_golden_rejects_non_object_event():
    with pytest.raises(ValueError, match="list of objects"):
        evaluate_cpp_golden(["not-an-object"])
