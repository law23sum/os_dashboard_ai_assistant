from __future__ import annotations

import importlib
import json
from pathlib import Path
from types import ModuleType
from typing import Tuple

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def runtime_env(monkeypatch, tmp_path: Path) -> Tuple[Path, ModuleType, ModuleType]:
    log_file = tmp_path / "runtime.log"
    monkeypatch.setenv("OSDASH_RUNTIME_LOG", str(log_file))
    runtime_module = importlib.reload(importlib.import_module("backend_api.routers.runtime_diagnostics"))
    backend_main = importlib.reload(importlib.import_module("backend_api.main"))
    yield log_file, runtime_module, backend_main
    importlib.reload(runtime_module)
    importlib.reload(backend_main)


def test_runtime_diagnostics_endpoint_writes_log(runtime_env):
    log_file, _, backend_main = runtime_env
    client = TestClient(backend_main.app)
    payload = {
        "source": "jest",
        "message": "Demo error",
        "stack": "traceback",
        "severity": "error",
        "context": {"foo": "bar"},
    }
    response = client.post("/api/runtime/diagnostics", json=payload)
    assert response.status_code == 202
    assert log_file.exists()
    lines = [json.loads(line) for line in log_file.read_text().splitlines() if line.strip()]
    assert lines, "runtime log must contain entries"
    event = lines[-1]
    assert event["source"] == payload["source"]
    assert event["message"] == payload["message"]
    assert event["context"]["foo"] == "bar"
    assert "timestamp" in event


def test_runtime_diagnostics_get_returns_events(runtime_env):
    log_file, _, backend_main = runtime_env
    client = TestClient(backend_main.app)
    payload = {
        "source": "react",
        "message": "UI error",
        "severity": "error",
        "context": {"route": "/observability"},
    }
    client.post("/api/runtime/diagnostics", json=payload)
    response = client.get("/api/runtime/diagnostics")
    assert response.status_code == 200
    body = response.json()
    assert body["events"], "expected diagnostics events"
    assert body["summary"]["total"] >= 1
    assert any(event["source"] == "react" for event in body["events"])
    assert body["summary"]["errors"] >= 1
