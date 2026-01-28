"""
Pytest configuration and fixtures for OS Dashboard tests.
Provides shared fixtures for database, API client, and test data.
"""

import asyncio
import os
import sqlite3
import tempfile
from pathlib import Path
from typing import AsyncGenerator, Generator

import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient

# Add parent directory to path
import sys
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from backend_api.main import app
from backend_api.db import db_session


def pytest_configure(config):
    """Relax coverage thresholds for focused PMS-only runs."""
    cov_fail_under = getattr(config.option, "cov_fail_under", None)
    if not cov_fail_under:
        return
    args = [str(arg) for arg in getattr(config, "args", [])]
    if args and all("test_pms_core.py" in arg for arg in args):
        config.option.cov_fail_under = 0


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
    os.environ["TEST_DB_FILE"] = str(test_db)
    
    with TestClient(app) as client:
        yield client
    
    # Restore original
    if original_db_file:
        os.environ["TEST_DB_FILE"] = original_db_file
    else:
        os.environ.pop("TEST_DB_FILE", None)


@pytest.fixture
async def async_client(test_db: Path) -> AsyncGenerator[AsyncClient, None]:
    """Create async test client."""
    # Override database path for testing
    original_db_file = os.environ.get("TEST_DB_FILE")
    os.environ["TEST_DB_FILE"] = str(test_db)
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    
    # Restore original
    if original_db_file:
        os.environ["TEST_DB_FILE"] = original_db_file
    else:
        os.environ.pop("TEST_DB_FILE", None)


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
    """Configure custom pytest markers."""
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
