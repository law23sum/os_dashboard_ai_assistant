"""Ensure the assistant_hub FastAPI app exposes the Office realtime endpoints."""
from __future__ import annotations

from pathlib import Path
import sys

import pytest
from fastapi.testclient import TestClient

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from assistant_hub.api.server import create_app  # noqa: E402


@pytest.fixture(scope="module")
def client() -> TestClient:
    app = create_app()
    return TestClient(app)


def test_office_summary_available(client: TestClient) -> None:
    response = client.get("/office/realtime/summary")
    assert response.status_code == 200
    payload = response.json()
    assert payload["documents"], "expected at least one simulated document"
    assert payload["manifest_preview"].startswith("<OfficeApp")


def test_office_ai_endpoint(client: TestClient) -> None:
    response = client.post(
        "/office/realtime/ai",
        json={"operation": "analyze", "payload": {"prompt": "Summarize deck"}},
    )
    assert response.status_code == 200
    data = response.json()
    assert "job" in data and "result" in data
    assert data["job"]["job_id"].startswith("job_")
