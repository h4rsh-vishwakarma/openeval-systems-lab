import os
import time
import uuid

import httpx
import pytest

BASE = os.getenv("TEST_API_URL", "http://localhost:8000")
TOKEN = os.getenv("API_TOKEN", "")


@pytest.fixture(scope="module")
def client():
    if not TOKEN:
        pytest.skip("Set API_TOKEN for integration tests")
    with httpx.Client(base_url=BASE, headers={"Authorization": f"Bearer {TOKEN}"}, timeout=5) as session:
        yield session


def create(client, key, events=None):
    return client.post("/tasks", headers={"Idempotency-Key": key}, json={"scenario": "webhook_once", "input": {"events": events or []}})


def wait_for(client, task_id, target, timeout=25):
    until = time.monotonic() + timeout
    while time.monotonic() < until:
        task = client.get(f"/tasks/{task_id}").json()
        if task["state"] == target:
            return task
        time.sleep(0.5)
    pytest.fail(f"Task {task_id} did not reach {target}")


def test_idempotency_and_golden_workflow(client):
    key = str(uuid.uuid4())
    events = [{"id": "a", "amount": 1}, {"id": "a", "amount": 1}]
    first = create(client, key, events)
    assert first.status_code == 201
    second = create(client, key, events)
    assert second.json()["id"] == first.json()["id"]
    assert create(client, key, [{"id": "b", "amount": 2}]).status_code == 409
    task_id = first.json()["id"]
    payload = {"implementation": "golden", "inject_failure": "none"}
    assert client.post(f"/tasks/{task_id}/submit", json=payload).status_code == 200
    assert client.post(f"/tasks/{task_id}/submit", json=payload).status_code == 200
    task = wait_for(client, task_id, "completed")
    assert task["result"]["score"] == 1.0
    assert task["attempts"] == 1
    first_page = client.get(f"/tasks/{task_id}/result", params={"offset": 0, "limit": 2}).json()
    second_page = client.get(f"/tasks/{task_id}/result", params={"offset": 2, "limit": 2}).json()
    assert len(first_page["result"]["checks"]) == 2
    assert first_page["pagination"] == {"offset": 0, "limit": 2, "total": 4, "has_more": True}
    assert len(second_page["result"]["checks"]) == 2
    assert second_page["pagination"]["has_more"] is False
    assert client.get(f"/tasks/{task_id}/result", params={"limit": 0}).status_code == 400
    assert client.get(f"/tasks/{task_id}/events").json()[-1]["state"] == "completed"


def test_validation_unknown_id_and_defective_variant(client):
    assert httpx.get(f"{BASE}/tasks/{uuid.uuid4()}").status_code == 401
    assert client.post("/tasks", headers={"Idempotency-Key": str(uuid.uuid4())}, json={"scenario": "unknown"}).status_code == 400
    assert client.get(f"/tasks/{uuid.uuid4()}").status_code == 404
    task_id = create(client, str(uuid.uuid4())).json()["id"]
    client.post(f"/tasks/{task_id}/submit", json={"implementation": "defective_duplicate"})
    assert wait_for(client, task_id, "completed")["result"]["score"] < 1.0


def test_retry_and_dead_letter(client):
    transient_id = create(client, str(uuid.uuid4())).json()["id"]
    client.post(f"/tasks/{transient_id}/submit", json={"implementation": "golden", "inject_failure": "transient"})
    assert wait_for(client, transient_id, "completed")["attempts"] == 2
    dead_id = create(client, str(uuid.uuid4())).json()["id"]
    client.post(f"/tasks/{dead_id}/submit", json={"implementation": "golden", "inject_failure": "invalid_output"})
    assert wait_for(client, dead_id, "dead_letter")["attempts"] == 1


def test_persistent_timeout_and_malformed_input(client):
    timeout_id = create(client, str(uuid.uuid4())).json()["id"]
    client.post(f"/tasks/{timeout_id}/submit", json={"implementation": "golden", "inject_failure": "timeout"})
    timeout_task = wait_for(client, timeout_id, "dead_letter", timeout=30)
    assert timeout_task["attempts"] == 3
    assert "timeout" in timeout_task["error"].lower()
    malformed_id = create(client, str(uuid.uuid4()), ["not-an-object"]).json()["id"]
    client.post(f"/tasks/{malformed_id}/submit", json={"implementation": "golden"})
    malformed_task = wait_for(client, malformed_id, "dead_letter")
    assert malformed_task["attempts"] == 1
    assert "list of objects" in malformed_task["error"]
