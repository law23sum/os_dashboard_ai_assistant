"""Regression tests for the realtime Office integration API."""
import importlib.util
from pathlib import Path
import os
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _load_repo_sitecustomize() -> None:
    sitecustomize_path = REPO_ROOT / "sitecustomize.py"
    if not sitecustomize_path.exists():
        return
    spec = importlib.util.spec_from_file_location("osdash_sitecustomize", sitecustomize_path)
    if not spec or not spec.loader:
        return
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)


_load_repo_sitecustomize()

if __name__ == "__main__":
    os.environ.setdefault("OSDASH_ROUTER_ALLOWLIST", "office")

from fastapi.testclient import TestClient
from backend_api.main import app

client = TestClient(app)


def test_office_summary_includes_documents():
    response = client.get("/api/office/realtime/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["documents"], "Expected at least one document in the realtime summary"
    assert data["manifest_preview"].startswith("<OfficeApp")
    assert data["docs_links"]


def test_office_ai_generate_round_trip():
    response = client.post(
        "/api/office/realtime/ai",
        json={"operation": "generate", "payload": {"document_type": "powerpoint"}},
    )
    assert response.status_code == 200
    payload = response.json()
    assert "job" in payload and "result" in payload
    assert payload["job"]["job_id"]
    assert payload["result"] is None or isinstance(payload["result"], dict)


def test_office_overview_aliases_summary():
    response = client.get("/api/office/realtime/overview")
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload.get("documents"), list)
    assert payload.get("manifest_preview", "").startswith("<OfficeApp")


if __name__ == "__main__":
    test_office_summary_includes_documents()
    test_office_ai_generate_round_trip()
