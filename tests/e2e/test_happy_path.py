from __future__ import annotations

import os
if os.path.exists("test.db"): os.remove("test.db")
from uuid import uuid4

from fastapi.testclient import TestClient

os.environ["DATABASE_URL"] = "sqlite:///./test.db"

from api.main import app  # noqa: E402
from infra.db import SessionLocal, Event
from infra.redis import queue
from core.pipeline.jobs import normalize_event_job

client = TestClient(app)


def run_job(func, *args, **kwargs):
    func(*args, **kwargs)


# patch queue.enqueue to run job synchronously
queue.enqueue = run_job  # type: ignore


def test_ingest_and_heatmap(tmp_path):
    trace = str(uuid4())
    payload = {
        "schema_version": "2025.08.1",
        "source": "test",
        "asset": "XAUUSD",
        "kind": "indicator",
        "ingested_at": "2024-01-01T00:00:00Z",
        "payload": {"key": "macro", "value": 5},
        "trace_id": trace,
    }
    resp = client.post("/ingest/events", json={"events": [payload]})
    assert resp.status_code == 202

    # repost same trace_id
    resp = client.post("/ingest/events", json={"events": [payload]})
    assert resp.status_code == 202

    with SessionLocal() as s:
        count = s.query(Event).count()
        assert count == 1

    # retrieve heatmap
    resp = client.get("/heatmap", params={"asset": "XAUUSD"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["score"] == 5
    macro = next(p for p in data["pillars"] if p["name"] == "Macro")
    assert macro["score"] == 5
    assert macro["components"][0]["score"] == 5
