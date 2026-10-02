"""Reproducible local Compose outage drill. Always restores stopped services."""
import os
import subprocess
import time
import uuid

import httpx

COMPOSE = ["docker", "compose", "-f", "infra/docker/compose.yml"]
BASE = os.getenv("TEST_API_URL", "http://localhost:8000")
TOKEN = os.environ["API_TOKEN"]


def service(action: str, name: str):
    subprocess.run([*COMPOSE, action, name], check=True)


def eventually(check, timeout=45):
    until = time.monotonic() + timeout
    while time.monotonic() < until:
        try:
            value = check()
            if value:
                return value
        except (httpx.HTTPError, KeyError):
            pass
        time.sleep(1)
    raise AssertionError("Condition not reached before timeout")


def main():
    client = httpx.Client(base_url=BASE, headers={"Authorization": f"Bearer {TOKEN}"}, timeout=3)
    try:
        service("stop", "worker")
        try:
            created = client.post("/tasks", headers={"Idempotency-Key": str(uuid.uuid4())}, json={"scenario": "webhook_once"})
            created.raise_for_status()
            task_id = created.json()["id"]
            client.post(f"/tasks/{task_id}/submit", json={"implementation": "golden"}).raise_for_status()
            assert client.get(f"/tasks/{task_id}").json()["state"] == "queued"
        finally:
            service("start", "worker")
        task = eventually(lambda: (result if (result := client.get(f"/tasks/{task_id}").json())["state"] == "completed" else None))
        assert task["attempts"] == 1
        print("worker stop/restart: queued task completed once")

        service("stop", "redis")
        try:
            assert eventually(lambda: client.get("/health").status_code == 503)
        finally:
            service("start", "redis")
        assert eventually(lambda: client.get("/health").status_code == 200)
        print("Redis outage/recovery: health returned 503 then 200")

        service("stop", "postgres")
        try:
            assert eventually(lambda: client.get("/health").status_code == 503)
        finally:
            service("start", "postgres")
        assert eventually(lambda: client.get("/health").status_code == 200)
        print("PostgreSQL outage/recovery: health returned 503 then 200")
    finally:
        client.close()


if __name__ == "__main__":
    main()
