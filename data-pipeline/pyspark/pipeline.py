"""Local or Spark cluster batch pipeline. Replaces output on each full input snapshot."""
import argparse
import json
import time
from pathlib import Path

from pyspark.sql import SparkSession, functions as F, types as T

SCHEMA = T.StructType([
    T.StructField("event_id", T.StringType()),
    T.StructField("symbol", T.StringType()),
    T.StructField("timestamp", T.StringType()),
    T.StructField("price", T.DoubleType()),
    T.StructField("quantity", T.IntegerType()),
])


def run(input_path: str, output_path: str, quarantine_path: str, report_path: str) -> dict:
    started = time.perf_counter()
    spark = SparkSession.builder.master("local[2]").appName("OpenEvalTradePipeline").config("spark.sql.shuffle.partitions", "2").config("spark.ui.enabled", "false").getOrCreate()
    try:
        if input_path.endswith(".csv"):
            raw = spark.read.option("header", True).csv(input_path)
        else:
            raw = spark.read.json(input_path)
        required = {field.name for field in SCHEMA.fields}
        missing = sorted(required - set(raw.columns))
        if missing:
            raise ValueError(f"Missing required source columns: {missing}")
        selected = raw.select(
            F.col("event_id").cast("string"), F.col("symbol").cast("string"),
            F.col("timestamp").cast("string"), F.col("price").cast("double"),
            F.col("quantity").cast("int"),
        ).withColumn("parsed_at", F.to_timestamp("timestamp"))
        invalid = (
            F.col("event_id").isNull() | (F.length(F.trim("event_id")) == 0) |
            F.col("symbol").isNull() | (F.length(F.trim("symbol")) == 0) |
            ~F.col("symbol").rlike("^[A-Za-z0-9._-]{1,20}$") |
            F.col("parsed_at").isNull() | F.col("price").isNull() |
            (F.col("price") <= 0) | F.col("quantity").isNull() | (F.col("quantity") <= 0)
        )
        rejected = selected.filter(invalid).withColumn("reason", F.lit("required field, format, or range check failed"))
        valid = selected.filter(~invalid)
        # Conflicting rows are quarantined to avoid arbitrary winner selection.
        variants = valid.groupBy("event_id").agg(F.countDistinct(F.struct("symbol", "timestamp", "price", "quantity")).alias("variants"))
        conflict_ids = variants.filter(F.col("variants") > 1).select("event_id")
        conflicts = valid.join(conflict_ids, "event_id", "inner").withColumn("reason", F.lit("conflicting duplicate event ID"))
        candidates = valid.join(conflict_ids, "event_id", "left_anti")
        deduped = candidates.dropDuplicates(["event_id"])
        final = deduped.withColumn("year", F.year("parsed_at")).withColumn("month", F.month("parsed_at"))
        input_count = selected.count()
        invalid_count = rejected.count()
        conflict_count = conflicts.count()
        valid_count = final.count()
        duplicate_count = input_count - invalid_count - conflict_count - valid_count
        final.select("event_id", "symbol", "parsed_at", "price", "quantity", "year", "month").write.mode("overwrite").partitionBy("symbol", "year", "month").parquet(output_path)
        rejected.unionByName(conflicts).write.mode("overwrite").json(quarantine_path)
        output_size = sum(file.stat().st_size for file in Path(output_path).rglob("*.parquet")) if "://" not in output_path else None
        report = {"input_records": input_count, "successful_records": valid_count, "rejected_records": invalid_count + conflict_count, "duplicate_records": duplicate_count, "reconciled": input_count == valid_count + invalid_count + conflict_count + duplicate_count, "processing_seconds": round(time.perf_counter() - started, 3), "output_size_bytes": output_size, "output_path": output_path, "quarantine_path": quarantine_path}
        if not report["reconciled"]:
            raise AssertionError("Row count reconciliation failed")
        Path(report_path).parent.mkdir(parents=True, exist_ok=True)
        Path(report_path).write_text(json.dumps(report, indent=2), encoding="utf-8")
        return report
    finally:
        spark.stop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--quarantine", required=True)
    parser.add_argument("--report", required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.input, args.output, args.quarantine, args.report)))
