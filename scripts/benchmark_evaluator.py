"""Measure the deterministic evaluator with a fixed workload and emit JSON."""
import json
import platform
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from services.evaluator.core import evaluate

ITERATIONS = 10000
EVENTS = [{"id": f"event-{i % 80}", "amount": i % 20} for i in range(100)]


def main():
    start = time.perf_counter()
    last = None
    for _ in range(ITERATIONS):
        last = evaluate("golden", EVENTS)
    elapsed = time.perf_counter() - start
    print(json.dumps({"workload": "golden evaluation on 100 synthetic events", "iterations": ITERATIONS, "input_events_per_iteration": len(EVENTS), "successful_events_per_iteration": 80, "rejected_events_per_iteration": 0, "duplicate_events_per_iteration": 20, "retry_count": 0, "output_bytes": len(json.dumps(last).encode()), "elapsed_seconds": round(elapsed, 4), "evaluations_per_second": round(ITERATIONS / elapsed, 2), "score": last["score"], "python": platform.python_version(), "platform": platform.platform()}, indent=2))


if __name__ == "__main__":
    main()
