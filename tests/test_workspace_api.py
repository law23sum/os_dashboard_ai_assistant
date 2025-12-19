from __future__ import annotations

from pathlib import Path
import sys
import types

import assistant_hub.ui.terminal.harness as harness
from fastapi.testclient import TestClient


def _install_msgraph_stubs() -> None:
    """Provide lightweight stubs so create_app imports succeed without heavy deps."""

    msgraph_module = types.ModuleType("msgraph")

    class _GraphServiceClient:
        def __init__(self, *args, **kwargs) -> None:
            self.args = args
            self.kwargs = kwargs

    msgraph_module.GraphServiceClient = _GraphServiceClient
    sys.modules["msgraph"] = msgraph_module
    sys.modules["msgraph.generated"] = types.ModuleType("msgraph.generated")
    sys.modules["msgraph.generated.models"] = types.ModuleType("msgraph.generated.models")

    drive_item_module = types.ModuleType("msgraph.generated.models.drive_item")
    drive_item_module.DriveItem = object
    workbook_module = types.ModuleType("msgraph.generated.models.workbook")
    workbook_module.Workbook = object
    notebook_module = types.ModuleType("msgraph.generated.models.notebook")
    notebook_module.Notebook = object

    sys.modules["msgraph.generated.models.drive_item"] = drive_item_module
    sys.modules["msgraph.generated.models.workbook"] = workbook_module
    sys.modules["msgraph.generated.models.notebook"] = notebook_module

    msal_module = types.ModuleType("msal")

    class _ConfidentialClientApplication:
        def __init__(self, *args, **kwargs) -> None:
            self.args = args
            self.kwargs = kwargs

        def acquire_token_for_client(self, scopes=None):
            return {"access_token": "stub"}

    msal_module.ConfidentialClientApplication = _ConfidentialClientApplication
    sys.modules["msal"] = msal_module


_install_msgraph_stubs()
from assistant_hub.api.server import create_app  # noqa: E402


def _fake_profile(tmp_path: Path) -> harness.ProjectProfile:
    return harness.ProjectProfile(
        name="demo",
        root=tmp_path,
        commands={"test": [["echo", "ok"]]},
        autofix_script=None,
    )


def test_workspace_scan_api(monkeypatch, tmp_path: Path) -> None:
    """API should surface scan results from the harness."""

    profile = _fake_profile(tmp_path)
    monkeypatch.setattr(harness, "discover_profiles", lambda base, max_depth=2: [profile])

    app = create_app(db_path=tmp_path / "db.sqlite")
    client = TestClient(app)

    response = client.get("/api/workspace/scan", params={"root": str(tmp_path)})
    assert response.status_code == 200
    data = response.json()
    assert data["projects"][0]["name"] == "demo"


def test_workspace_checks_api(monkeypatch, tmp_path: Path) -> None:
    """Dry-run checks should return aggregated summary without executing commands."""

    profile = _fake_profile(tmp_path)
    monkeypatch.setattr(harness, "discover_profiles", lambda base, max_depth=2: [profile])

    app = create_app(db_path=tmp_path / "db.sqlite")
    client = TestClient(app)

    response = client.post("/api/workspace/checks", json={"root": str(tmp_path), "categories": ["test"], "dry_run": True})
    assert response.status_code == 200
    data = response.json()
    assert data["summary"]["skipped"] >= 1
    assert data["summary"]["failed"] == 0
