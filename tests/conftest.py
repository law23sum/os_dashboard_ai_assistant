"""
Pytest configuration and fixtures for AI OS tests.
Provides shared fixtures for database, API client, and test data.
"""

import asyncio
from functools import wraps
import importlib.util
import inspect
import os
import sqlite3
import tempfile
import sys
from pathlib import Path
from typing import AsyncGenerator, Generator

# Add parent directory to path
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))


def _load_repo_sitecustomize() -> None:
    sitecustomize_path = parent_dir / "sitecustomize.py"
    if not sitecustomize_path.exists():
        return
    spec = importlib.util.spec_from_file_location("osdash_sitecustomize", sitecustomize_path)
    if not spec or not spec.loader:
        return
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)


_load_repo_sitecustomize()

def _ensure_httpx_app_param() -> None:
    try:
        import httpx
    except Exception:
        return

    def _wrap_client_init(client_cls: type, sentinel: str) -> None:
        if getattr(client_cls.__init__, sentinel, False):
            return
        try:
            signature = inspect.signature(client_cls.__init__)
        except (TypeError, ValueError):
            return
        if "app" in signature.parameters:
            return

        original_init = client_cls.__init__

        @wraps(original_init)
        def _init(self, *args, **kwargs):
            app = kwargs.pop("app", None)
            transport = kwargs.pop("transport", None)
            if app is not None and transport is None:
                transport = httpx.ASGITransport(app=app)
            return original_init(self, *args, transport=transport, **kwargs)

        setattr(_init, sentinel, True)
        client_cls.__init__ = _init

    _wrap_client_init(httpx.Client, "_osdash_httpx_app_patch")
    _wrap_client_init(httpx.AsyncClient, "_osdash_httpx_app_patch")


_ensure_httpx_app_param()

import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient

os.environ.setdefault("OSDASH_ALLOW_ANON", "1")

TEST_RUNTIME_ROOT = Path(tempfile.mkdtemp(prefix="osdash-tests-"))
TEST_LOG_DIR = TEST_RUNTIME_ROOT / "logs"
TEST_DB_PATH = TEST_RUNTIME_ROOT / "assistant_hub.db"
_RUNTIME_ENV = {
    "ASSISTANT_HUB_HOME": TEST_RUNTIME_ROOT,
    "ASSISTANT_HUB_DATA_DIR": TEST_RUNTIME_ROOT,
    "ASSISTANT_HUB_DB": TEST_DB_PATH,
    "ASSISTANT_HUB_ATTACHMENTS_DIR": TEST_RUNTIME_ROOT / "attachments",
    "ASSISTANT_HUB_INTEGRATIONS_DIR": TEST_RUNTIME_ROOT / "integrations",
    "ASSISTANT_HUB_FILE_CACHE_DIR": TEST_RUNTIME_ROOT / "file_cache",
    "OSDASH_HOME": TEST_RUNTIME_ROOT,
    "OSDASH_DATA_DIR": TEST_RUNTIME_ROOT,
    "OSDASH_LOG_DIR": TEST_LOG_DIR,
    "TEST_DB_FILE": TEST_DB_PATH,
}
for key, path in _RUNTIME_ENV.items():
    os.environ.setdefault(key, str(path))
for required in (
    TEST_RUNTIME_ROOT,
    TEST_LOG_DIR,
    _RUNTIME_ENV["ASSISTANT_HUB_ATTACHMENTS_DIR"],
    _RUNTIME_ENV["ASSISTANT_HUB_INTEGRATIONS_DIR"],
    _RUNTIME_ENV["ASSISTANT_HUB_FILE_CACHE_DIR"],
):
    Path(required).mkdir(parents=True, exist_ok=True)

from backend_api.main import app
from backend_api.db import db_session


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def test_db() -> Generator[Path, None, None]:
    """Create a temporary test database."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = Path(tmp.name)
    
    # Initialize schema
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE projects (
            name TEXT PRIMARY KEY,
            description TEXT,
            status TEXT,
            priority TEXT,
            order_num INTEGER DEFAULT 0
        )
    """)
    conn.execute("""
        CREATE TABLE tasks (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'TODO',
            priority TEXT DEFAULT 'MEDIUM',
            project TEXT,
            due_date TEXT,
            owner TEXT,
            created_at TEXT,
            updated_at TEXT,
            FOREIGN KEY (project) REFERENCES projects(name)
        )
    """)
    conn.execute("""
        CREATE TABLE project_ledger (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            event_type TEXT NOT NULL,
            entity_type TEXT,
            entity_id TEXT,
            payload TEXT,
            created_at TEXT NOT NULL,
            hash_prev TEXT,
            hash_curr TEXT NOT NULL,
            FOREIGN KEY (project_id) REFERENCES projects(name)
        )
    """)
    conn.execute("""
        CREATE TABLE note_links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id TEXT NOT NULL,
            integration_type TEXT NOT NULL,
            title TEXT,
            description TEXT,
            external_id TEXT,
            created_at TEXT,
            last_synced TEXT,
            FOREIGN KEY (project_id) REFERENCES projects(name)
        )
    """)
    conn.commit()
    conn.close()
    
    yield db_path
    
    # Cleanup
    if db_path.exists():
        db_path.unlink()


@pytest.fixture
def sync_client(test_db: Path) -> Generator[TestClient, None, None]:
    """Create synchronous test client."""
    # Override database path for testing
    original_db_file = os.environ.get("TEST_DB_FILE")
    original_assistant_db = os.environ.get("ASSISTANT_HUB_DB")
    os.environ["TEST_DB_FILE"] = str(test_db)
    os.environ["ASSISTANT_HUB_DB"] = str(test_db)
    
    with TestClient(app) as client:
        yield client
    
    # Restore original
    if original_db_file:
        os.environ["TEST_DB_FILE"] = original_db_file
    else:
        os.environ.pop("TEST_DB_FILE", None)
    if original_assistant_db:
        os.environ["ASSISTANT_HUB_DB"] = original_assistant_db
    else:
        os.environ.pop("ASSISTANT_HUB_DB", None)


@pytest.fixture
async def async_client(test_db: Path) -> AsyncGenerator[AsyncClient, None]:
    """Create async test client."""
    # Override database path for testing
    original_db_file = os.environ.get("TEST_DB_FILE")
    original_assistant_db = os.environ.get("ASSISTANT_HUB_DB")
    os.environ["TEST_DB_FILE"] = str(test_db)
    os.environ["ASSISTANT_HUB_DB"] = str(test_db)
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    
    # Restore original
    if original_db_file:
        os.environ["TEST_DB_FILE"] = original_db_file
    else:
        os.environ.pop("TEST_DB_FILE", None)
    if original_assistant_db:
        os.environ["ASSISTANT_HUB_DB"] = original_assistant_db
    else:
        os.environ.pop("ASSISTANT_HUB_DB", None)


@pytest.fixture
def sample_projects():
    """Provide sample project data for tests."""
    return [
        {
            "name": "AI Research Workspace",
            "description": "Advanced AI research and development",
            "status": "active",
            "priority": "HIGH",
            "order_num": 0,
        },
        {
            "name": "Automation Platform",
            "description": "Enterprise automation workflows",
            "status": "active",
            "priority": "HIGH",
            "order_num": 1,
        },
        {
            "name": "Client Readiness",
            "description": "Production readiness checklist",
            "status": "in_progress",
            "priority": "MEDIUM",
            "order_num": 2,
        },
    ]


@pytest.fixture
def sample_tasks():
    """Provide sample task data for tests."""
    return [
        {
            "id": "task-001",
            "title": "Implement authentication",
            "description": "Add OAuth2 authentication flow",
            "status": "TODO",
            "priority": "CRITICAL",
            "project": "Automation Platform",
            "owner": "Chris",
        },
        {
            "id": "task-002",
            "title": "Setup CI/CD pipeline",
            "description": "Configure GitHub Actions",
            "status": "IN_PROGRESS",
            "priority": "HIGH",
            "project": "Automation Platform",
            "owner": "Sora",
        },
        {
            "id": "task-003",
            "title": "Write documentation",
            "description": "API documentation and examples",
            "status": "TODO",
            "priority": "MEDIUM",
            "project": "Client Readiness",
            "owner": "Aria",
        },
    ]


@pytest.fixture
def populated_db(test_db: Path, sample_projects, sample_tasks):
    """Create a test database populated with sample data."""
    conn = sqlite3.connect(test_db)
    
    # Insert projects
    for project in sample_projects:
        conn.execute(
            """INSERT INTO projects (name, description, status, priority, order_num)
               VALUES (?, ?, ?, ?, ?)""",
            (
                project["name"],
                project["description"],
                project["status"],
                project["priority"],
                project["order_num"],
            ),
        )
    
    # Insert tasks
    for task in sample_tasks:
        conn.execute(
            """INSERT INTO tasks (id, title, description, status, priority, project, owner)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                task["id"],
                task["title"],
                task["description"],
                task["status"],
                task["priority"],
                task.get("project"),
                task.get("owner"),
            ),
        )
    
    conn.commit()
    conn.close()
    
    return test_db


# Markers for test organization
def pytest_configure(config):
    """Configure custom pytest markers and coverage relaxations."""
    cov_fail_under = getattr(config.option, "cov_fail_under", None)
    if cov_fail_under:
        args = [str(arg) for arg in getattr(config, "args", [])]
        if args and all("test_pms_core.py" in arg for arg in args):
            config.option.cov_fail_under = 0

    config.addinivalue_line(
        "markers", "e2e: marks tests as end-to-end integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow running"
    )
    config.addinivalue_line(
        "markers", "requires_network: marks tests that require network access"
    )
    config.addinivalue_line(
        "markers", "requires_database: marks tests that require database"
    )
