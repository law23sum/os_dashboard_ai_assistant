"""
Pytest configuration for E2E tests.
Provides shared fixtures and configuration for all E2E tests.
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture(scope="session")
def test_environment():
    """Define the test environment configuration."""
    return {
        "environment": "test",
        "api_base_url": "http://localhost:8000/api",
        "timeout": 10,
        "retries": 1,
    }


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """
    Setup test database before running tests.
    This ensures the database is initialized and has a clean state.
    """
    try:
        from assistant_hub_gui.assistant_hub.db_fixed import init_db
        
        # Initialize the database
        conn = init_db()
        conn.close()
    except Exception as e:
        print(f"Warning: Could not initialize test database: {e}")
    
    yield
    
    # Cleanup if needed (optional - keep data for debugging)


@pytest.fixture
def unique_timestamp():
    """Generate a unique timestamp for test data."""
    from datetime import datetime
    return datetime.now().timestamp()


@pytest.fixture
def sample_project(unique_timestamp):
    """Generate sample project data."""
    return {
        "name": f"Test Project {unique_timestamp}",
        "description": "Generated test project",
        "status": "active",
        "priority": "MEDIUM",
        "order_num": 0,
    }


@pytest.fixture
def sample_task(unique_timestamp):
    """Generate sample task data."""
    return {
        "title": f"Test Task {unique_timestamp}",
        "project": "General",
        "status": "TODO",
        "priority": "HIGH",
        "notes": "Generated test task",
        "owner": "Chris",
    }


@pytest.fixture
def sample_import_data(unique_timestamp):
    """Generate sample import data."""
    return {
        "projects": [
            {
                "name": f"Import Test 1 {unique_timestamp}",
                "description": "First import test",
                "status": "active",
                "priority": "HIGH",
                "tasks": [
                    {
                        "title": "Imported Task A",
                        "status": "TODO",
                        "priority": "HIGH",
                    },
                    {
                        "title": "Imported Task B",
                        "status": "IN_PROGRESS",
                        "priority": "MEDIUM",
                    },
                ],
            },
            {
                "name": f"Import Test 2 {unique_timestamp}",
                "description": "Second import test",
                "status": "planning",
                "priority": "LOW",
            },
        ],
        "overwrite_existing": False,
        "import_tasks": True,
        "import_links": True,
    }


# Markers for categorizing tests
def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "slow: marks tests as slow running")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "regression: marks tests as regression tests")
    config.addinivalue_line("markers", "smoke: marks tests as smoke tests")
