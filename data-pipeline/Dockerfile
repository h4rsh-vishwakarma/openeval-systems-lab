FROM python:3.11-slim-bookworm
RUN apt-get update && apt-get install -y --no-install-recommends openjdk-17-jre-headless procps && rm -rf /var/lib/apt/lists/*
WORKDIR /workspace
COPY data-pipeline/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
CMD ["python", "data-pipeline/pyspark/pipeline.py", "--input", "data-pipeline/sample-data/trades.jsonl", "--output", "data-pipeline/output", "--quarantine", "data-pipeline/quarantine", "--report", "data-pipeline/reports/sample.json"]
