import os
import json

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://openeval:openeval@localhost:5432/openeval")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
API_TOKEN = os.getenv("API_TOKEN", "")
API_TOKENS = json.loads(os.getenv("API_TOKENS_JSON") or "{}")
ALLOWED_ORIGINS = [s.strip() for s in os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")]
MAX_ATTEMPTS = max(1, int(os.getenv("MAX_ATTEMPTS", "3")))
TASK_TIMEOUT_SECONDS = max(1, int(os.getenv("TASK_TIMEOUT_SECONDS", "30")))
