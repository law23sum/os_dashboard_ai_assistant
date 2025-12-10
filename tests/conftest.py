"""Pytest configuration and fixtures."""

import pytest
import sys
import os

pytest_plugins = ("pytest_asyncio",)

# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

@pytest.fixture
def sample_data():
    """Provide sample test data."""
    return {
        "test_key": "test_value",
        "numbers": [1, 2, 3, 4, 5]
    }

@pytest.fixture
def mock_config():
    """Provide mock configuration for tests."""
    return {
        "api_refresh_interval": 300,
        "log_level": "DEBUG",
        "database_path": ":memory:"
    }
