from pathlib import Path

from fastapi.testclient import TestClient

from assistant_hub.api.server import create_app


def _client(tmp_path: Path) -> TestClient:
    db_path = tmp_path / "test.db"
    app = create_app(db_path=db_path)
    return TestClient(app)


def test_health_includes_correlation_id(tmp_path):
    client = _client(tmp_path)
    resp = client.get("/health")
    assert resp.status_code == 200
    cid_header = resp.headers.get("x-correlation-id")
    assert cid_header
    body = resp.json()
    assert body.get("correlation_id")


def test_ready_reports_ok_and_correlation(tmp_path):
    client = _client(tmp_path)
    resp = client.get("/ready")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] in {"ok", "degraded"}
    assert body.get("correlation_id")


def test_harness_report_endpoint_returns_placeholder(tmp_path, monkeypatch):
    monkeypatch.setenv("OSDASH_HARNESS_LOG_DIR", str(tmp_path / "logs"))
    client = _client(tmp_path)
    resp = client.get("/runtime/harness-report")
    assert resp.status_code == 200
    payload = resp.json()
    assert "total_projects" in payload
    assert payload["total_projects"] == 0
