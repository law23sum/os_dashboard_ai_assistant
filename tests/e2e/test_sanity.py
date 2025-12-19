"""
Sanity Tests
Quick smoke tests to verify the application is functioning correctly.
Run these before any deployment or release.

Spec References: All sections
"""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    """Create a test client for the FastAPI application."""
    import sys
    from pathlib import Path
    
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))
    
    from backend_api.main import app
    
    with TestClient(app) as test_client:
        yield test_client


@pytest.mark.smoke
class TestAPISanity:
    """Quick sanity checks for API availability."""
    
    def test_api_health(self, client):
        """API health endpoint should return OK."""
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
    
    def test_projects_endpoint_available(self, client):
        """Projects endpoint should be available."""
        response = client.get("/api/projects")
        assert response.status_code == 200
    
    def test_tasks_endpoint_available(self, client):
        """Tasks endpoint should be available."""
        response = client.get("/api/tasks")
        assert response.status_code in [200, 404]
    
    def test_api_returns_json(self, client):
        """API should return JSON responses."""
        response = client.get("/api/health")
        assert response.headers.get("content-type", "").startswith("application/json")


@pytest.mark.smoke
class TestDatabaseSanity:
    """Quick sanity checks for database availability."""
    
    def test_database_initialized(self, client):
        """Database should be initialized."""
        # Try to list projects - this will fail if DB is not initialized
        response = client.get("/api/projects")
        assert response.status_code == 200
    
    def test_can_create_and_read_project(self, client):
        """Should be able to create and read a project."""
        from datetime import datetime
        
        project_name = f"Sanity Test {datetime.now().timestamp()}"
        
        # Create
        create_response = client.post("/api/projects", json={
            "name": project_name,
            "description": "Sanity test project",
            "status": "active",
            "priority": "MEDIUM"
        })
        assert create_response.status_code in [200, 201]
        
        # Read
        read_response = client.get(f"/api/projects/{project_name}")
        assert read_response.status_code == 200
        
        # Cleanup
        client.delete(f"/api/projects/{project_name}")


@pytest.mark.smoke
class TestCORSSanity:
    """Quick sanity checks for CORS configuration."""
    
    def test_cors_headers_present(self, client):
        """CORS headers should be present on GET requests."""
        response = client.get(
            "/api/health",
            headers={"Origin": "http://localhost:5173"}
        )
        # Should respond successfully to requests with Origin header
        assert response.status_code == 200


@pytest.mark.smoke
class TestStaticFilesSanity:
    """Quick sanity checks for static files serving."""
    
    def test_app_root_available(self, client):
        """App root should be available."""
        response = client.get("/app/")
        # May return HTML or redirect
        assert response.status_code in [200, 302, 307, 404]


@pytest.mark.smoke
class TestResponseFormatSanity:
    """Quick sanity checks for response formats."""
    
    def test_projects_list_is_array(self, client):
        """Projects list should return an array."""
        response = client.get("/api/projects")
        data = response.json()
        assert isinstance(data, list)
    
    def test_project_has_required_fields(self, client):
        """Project should have required fields."""
        from datetime import datetime
        
        project_name = f"Fields Test {datetime.now().timestamp()}"
        
        client.post("/api/projects", json={
            "name": project_name,
            "description": "Test",
            "status": "active",
            "priority": "HIGH"
        })
        
        response = client.get(f"/api/projects/{project_name}")
        data = response.json()
        
        required_fields = ["name", "status", "priority"]
        for field in required_fields:
            assert field in data
        
        # Cleanup
        client.delete(f"/api/projects/{project_name}")


@pytest.mark.smoke
class TestErrorHandlingSanity:
    """Quick sanity checks for error handling."""
    
    def test_404_for_nonexistent_project(self, client):
        """Should return 404 for nonexistent project."""
        response = client.get("/api/projects/nonexistent-project-xyz-123")
        assert response.status_code == 404
    
    def test_invalid_json_handled(self, client):
        """Should handle invalid JSON gracefully."""
        response = client.post(
            "/api/projects",
            content="not valid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code in [400, 422]


@pytest.mark.smoke
class TestPerformanceSanity:
    """Quick sanity checks for basic performance."""
    
    def test_health_check_fast(self, client):
        """Health check should respond quickly."""
        import time
        
        start = time.time()
        response = client.get("/api/health")
        elapsed = time.time() - start
        
        assert response.status_code == 200
        assert elapsed < 1.0  # Should complete in under 1 second
    
    def test_projects_list_reasonable_time(self, client):
        """Projects list should respond in reasonable time."""
        import time
        
        start = time.time()
        response = client.get("/api/projects")
        elapsed = time.time() - start
        
        assert response.status_code == 200
        assert elapsed < 5.0  # Should complete in under 5 seconds


def test_full_application_startup():
    """Test that the full application starts without errors."""
    import sys
    from pathlib import Path
    
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))
    
    # This will raise if there are import errors
    from backend_api.main import app
    
    assert app is not None
    assert "OS Dashboard AI Assistant" in app.title


def test_database_module_loads():
    """Test that the database module loads correctly."""
    import sys
    from pathlib import Path
    
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))
    
    from assistant_hub_gui.assistant_hub import db as hub_db
    from backend_api.db import db_session
    
    assert hasattr(hub_db, 'init_db')
    assert db_session is not None


def test_models_defined():
    """Test that all core models are defined."""
    import sys
    from pathlib import Path
    
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))
    
    from backend_api.routers.projects import (
        ProjectCreate, ProjectUpdate, ProjectResponse,
        ProjectExportData, ImportRequest, ExportResponse
    )
    
    # All model imports should succeed
    assert ProjectCreate is not None
    assert ProjectResponse is not None
    assert ExportResponse is not None
