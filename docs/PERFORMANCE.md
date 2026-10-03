# Performance evidence

Performance claims must include the command, workload, date, environment, and raw measured output. Do not estimate unmeasured queue recovery or distributed pipeline behavior.

## Evaluator

The repository includes a repeatable pure in-process evaluator benchmark:

```bash
python scripts/benchmark_evaluator.py
```

The measured before/after comparison for fixed fixture expectation caching is recorded in [BENCHMARKS.md](BENCHMARKS.md). It is a single run on the documented machine and should not be generalized to API or queue throughput.

## Queue recovery and data pipeline

No reproducible baseline/after timing has been recorded for queue recovery or production-scale pipeline processing. The five-row PySpark sample is a correctness fixture with substantial JVM startup overhead. Record the exact Compose configuration, queue depth, injected failure, recovery definition, input size, output counts, and at least repeated wall-clock runs before making a comparison.

For test execution time, capture the command, dependency versions, machine, and repeated wall times. Do not infer performance changes from CI duration because runner load varies.

## Recording a result

Add date, commit, OS/CPU/RAM, runtime versions, workload dimensions, repetitions, median and range, output correctness, duplicate/retry counts, and exact command. Keep raw JSON output with the report when it is small and contains no secrets.
