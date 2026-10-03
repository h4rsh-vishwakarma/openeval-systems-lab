"""Bridge to the compiled C++ golden evaluator used by worker processes."""
import json
import os
import subprocess
from pathlib import Path
from typing import Any


def _binary_path() -> str:
    configured = os.environ.get("OPEN_EVAL_CPP_EVALUATOR")
    if configured:
        return configured
    installed = Path("/usr/local/bin/openeval-cpp-evaluator")
    if installed.is_file():
        return str(installed)
    repository_binary = Path(__file__).resolve().parents[2] / "algorithms" / "build" / "openeval-cpp-evaluator"
    if os.name == "nt":
        repository_binary = repository_binary.with_suffix(".exe")
    return str(repository_binary)


def evaluate_cpp_golden(events: list[dict[str, Any]]) -> dict[str, Any]:
    if not isinstance(events, list) or any(not isinstance(event, dict) for event in events):
        raise ValueError("input.events must be a list of objects")
    try:
        completed = subprocess.run(
            [_binary_path()],
            input=json.dumps(events, ensure_ascii=True, separators=(",", ":")),
            text=True,
            capture_output=True,
            check=False,
            timeout=10,
        )
    except FileNotFoundError as exc:
        raise ValueError("C++ evaluator binary is not installed") from exc
    except subprocess.TimeoutExpired as exc:
        raise TimeoutError("C++ evaluator timed out") from exc

    if completed.returncode != 0:
        detail = completed.stderr.strip()[:256] or "C++ evaluator rejected its input"
        raise ValueError(detail)
    try:
        result = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise ValueError("C++ evaluator returned invalid JSON") from exc
    if not isinstance(result, dict) or not {"stored_ids", "stored_count", "rejected_count"}.issubset(result):
        raise ValueError("C++ evaluator returned an invalid result shape")
    return result
