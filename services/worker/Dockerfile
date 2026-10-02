FROM python:3.11-slim
WORKDIR /app
COPY services/api-python/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY services/api-python/app /app/app
COPY services/evaluator /app/evaluator
COPY services/worker /app/worker
ENV PYTHONPATH=/app
CMD ["python", "-m", "worker.worker"]
