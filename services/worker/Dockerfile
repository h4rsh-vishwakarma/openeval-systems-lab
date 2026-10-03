FROM gcc:12-bookworm AS cpp-build
RUN apt-get update && apt-get install -y --no-install-recommends nlohmann-json3-dev && rm -rf /var/lib/apt/lists/*
WORKDIR /src
COPY algorithms/evaluator.hpp algorithms/evaluator.cpp algorithms/evaluator_cli.cpp ./
RUN g++ -std=c++17 -O2 -Wall -Wextra -Werror evaluator.cpp evaluator_cli.cpp -o /openeval-cpp-evaluator

FROM python:3.11-slim
WORKDIR /app
COPY services/api-python/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY --from=cpp-build /openeval-cpp-evaluator /usr/local/bin/openeval-cpp-evaluator
COPY services/api-python/app /app/app
COPY services/evaluator /app/evaluator
COPY services/worker /app/worker
ENV PYTHONPATH=/app
CMD ["python", "-m", "worker.worker"]
