import importlib.util
from pathlib import Path

import pytest

pytest.importorskip("pyspark")
PATH = Path(__file__).resolve().parents[2] / "data-pipeline" / "pyspark" / "pipeline.py"
spec = importlib.util.spec_from_file_location("pipeline", PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_sample_reconciles_and_rerun_is_stable(tmp_path):
    source = str(Path(__file__).resolve().parents[2] / "data-pipeline" / "sample-data" / "trades.jsonl")
    output = str(tmp_path / "output")
    quarantine = str(tmp_path / "quarantine")
    report = str(tmp_path / "report.json")
    first = module.run(source, output, quarantine, report)
    second = module.run(source, output, quarantine, report)
    assert {k: first[k] for k in ("input_records", "successful_records", "rejected_records", "duplicate_records", "reconciled", "output_size_bytes")} == {k: second[k] for k in ("input_records", "successful_records", "rejected_records", "duplicate_records", "reconciled", "output_size_bytes")}
    assert (first["input_records"], first["successful_records"], first["rejected_records"], first["duplicate_records"]) == (5, 2, 2, 1)
    assert first["reconciled"]
