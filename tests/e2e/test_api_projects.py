"""
End-to-End API Tests for Projects
Tests the complete project lifecycle through the API:
- CRUD operations
- Import/Export functionality
- Project intelligence
- Ledger operations

Spec References: §3.3, §7.2, §8.7
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime
import json


@pytest.fixture(scope="module")
def client():
    """Create a test client for the FastAPI application."""
    import sys
    from pathlib import Path
    
    # Add the project root to path
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))
    
    from backend_api.main import app
    
    with TestClient(app) as test_client:
        yield test_client


class TestProjectsCRUD:
    """Test basic CRUD operations for projects."""
    
    def test_list_projects(self, client):
        """Should return list of projects."""
        response = client.get("/api/projects")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_create_project(self, client):
        """Should create a new project."""
        project_data = {
            "name": f"Test Project {datetime.now().timestamp()}",
            "description": "E2E Test Project",
            "status": "active",
            "priority": "MEDIUM",
            "order_num": 99
        }
        
        response = client.post("/api/projects", json=project_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["name"] == project_data["name"]
        assert data["description"] == project_data["description"]
        assert data["status"] == project_data["status"]
        assert data["priority"] == project_data["priority"]
    
    def test_get_single_project(self, client):
        """Should retrieve a single project by name."""
        # First create a project
        project_name = f"Get Test {datetime.now().timestamp()}"
        client.post("/api/projects", json={
            "name": project_name,
            "description": "Test",
            "status": "active",
            "priority": "HIGH"
        })
        
        # Then retrieve it
        response = client.get(f"/api/projects/{project_name}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == project_name
    
    def test_update_project(self, client):
        """Should update an existing project."""
        # Create project
        project_name = f"Update Test {datetime.now().timestamp()}"
        client.post("/api/projects", json={
            "name": project_name,
            "description": "Original",
            "status": "active",
            "priority": "LOW"
        })
        
        # Update it
        response = client.put(f"/api/projects/{project_name}", json={
            "description": "Updated description",
            "priority": "CRITICAL"
        })
        assert response.status_code == 200
        
        data = response.json()
        assert data["description"] == "Updated description"
        assert data["priority"] == "CRITICAL"
    
    def test_delete_project(self, client):
        """Should delete a project."""
        # Create project
        project_name = f"Delete Test {datetime.now().timestamp()}"
        client.post("/api/projects", json={
            "name": project_name,
            "description": "To be deleted",
            "status": "active",
            "priority": "LOW"
        })
        
        # Delete it
        response = client.delete(f"/api/projects/{project_name}")
        assert response.status_code == 204
        
        # Verify it's gone
        response = client.get(f"/api/projects/{project_name}")
        assert response.status_code == 404
    
    def test_get_nonexistent_project(self, client):
        """Should return 404 for nonexistent project."""
        response = client.get("/api/projects/nonexistent-project-12345")
        assert response.status_code == 404


class TestProjectLinks:
    """Test project links (documents) functionality."""
    
    def test_list_project_links(self, client):
        """Should return list of project links."""
        response = client.get("/api/projects/links")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_links_have_required_fields(self, client):
        """Links should have all required fields."""
        response = client.get("/api/projects/links")
        assert response.status_code == 200
        
        data = response.json()
        if data:
            link = data[0]
            required_fields = ["id", "project_id", "integration_type", "title", "label"]
            for field in required_fields:
                assert field in link


class TestProjectLedger:
    """Test project ledger (audit trail) functionality."""
    
    def test_list_ledger_events(self, client):
        """Should return list of ledger events."""
        response = client.get("/api/projects/ledger")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_ledger_events_have_hash(self, client):
        """Ledger events should have hash for integrity."""
        # Create a project to generate a ledger event
        project_name = f"Ledger Test {datetime.now().timestamp()}"
        client.post("/api/projects", json={
            "name": project_name,
            "description": "Test",
            "status": "active",
            "priority": "MEDIUM"
        })
        
        response = client.get(f"/api/projects/ledger?project={project_name}")
        assert response.status_code == 200
        
        data = response.json()
        if data:
            event = data[0]
            assert "hash_curr" in event
            assert event["hash_curr"] is not None
    
    def test_filter_ledger_by_project(self, client):
        """Should filter ledger events by project."""
        # Create project
        project_name = f"Ledger Filter {datetime.now().timestamp()}"
        client.post("/api/projects", json={
            "name": project_name,
            "description": "Test",
            "status": "active",
            "priority": "MEDIUM"
        })
        
        response = client.get(f"/api/projects/ledger?project={project_name}")
        assert response.status_code == 200
        
        data = response.json()
        for event in data:
            assert event["project_id"] == project_name


class TestProjectIntelligence:
    """Test project intelligence metrics."""
    
    def test_list_project_intelligence(self, client):
        """Should return intelligence metrics for all projects."""
        response = client.get("/api/projects/intelligence")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_intelligence_has_health_score(self, client):
        """Intelligence should include health score."""
        response = client.get("/api/projects/intelligence")
        assert response.status_code == 200
        
        data = response.json()
        if data:
            intel = data[0]
            assert "health_score" in intel
            assert "risk_level" in intel
            assert "completion_ratio" in intel


class TestProjectInsights:
    """Test project insights (AI-powered analysis)."""
    
    def test_get_project_insights(self, client):
        """Should return insights for a project."""
        # Create project first
        project_name = f"Insights Test {datetime.now().timestamp()}"
        client.post("/api/projects", json={
            "name": project_name,
            "description": "Test",
            "status": "active",
            "priority": "HIGH"
        })
        
        response = client.get(f"/api/projects/{project_name}/insights")
        assert response.status_code == 200
        
        data = response.json()
        assert "project" in data
        assert "risk" in data
        assert "forecast" in data


class TestProjectTRF:
    """Test project TRF (Theoretical Reasoning Framework) endpoints."""
    
    def test_get_project_trf(self, client):
        """Should return TRF data for a project."""
        # Create project
        project_name = f"TRF Test {datetime.now().timestamp()}"
        client.post("/api/projects", json={
            "name": project_name,
            "description": "Test",
            "status": "active",
            "priority": "MEDIUM"
        })
        
        response = client.get(f"/api/projects/{project_name}/trf")
        assert response.status_code == 200
        
        data = response.json()
        assert "project_id" in data
        assert "entropy" in data
        assert "resonance" in data
        assert "continuity" in data
        assert "personas" in data


class TestProjectImportExport:
    """Test project import/export functionality."""
    
    def test_export_all_projects(self, client):
        """Should export all projects with their data."""
        # Create a project to export
        project_name = f"Export Test {datetime.now().timestamp()}"
        client.post("/api/projects", json={
            "name": project_name,
            "description": "For export",
            "status": "active",
            "priority": "HIGH"
        })
        
        response = client.get("/api/projects/export/all")
        assert response.status_code == 200
        
        data = response.json()
        assert "version" in data
        assert "exported_at" in data
        assert "projects" in data
        assert "total_projects" in data
        assert isinstance(data["projects"], list)
    
    def test_import_projects_bulk(self, client):
        """Should import projects in bulk."""
        import_data = {
            "projects": [
                {
                    "name": f"Imported Project 1 {datetime.now().timestamp()}",
                    "description": "Imported via API",
                    "status": "active",
                    "priority": "MEDIUM",
                    "order_num": 0
                },
                {
                    "name": f"Imported Project 2 {datetime.now().timestamp()}",
                    "description": "Another import",
                    "status": "planning",
                    "priority": "LOW",
                    "order_num": 1
                }
            ],
            "overwrite_existing": False,
            "import_tasks": True,
            "import_links": True
        }
        
        response = client.post("/api/projects/import/bulk", json=import_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "success" in data
        assert "projects_imported" in data
        assert data["projects_imported"] == 2
    
    def test_import_with_tasks(self, client):
        """Should import projects with their tasks."""
        project_name = f"Import With Tasks {datetime.now().timestamp()}"
        import_data = {
            "projects": [
                {
                    "name": project_name,
                    "description": "Has tasks",
                    "status": "active",
                    "priority": "HIGH",
                    "tasks": [
                        {
                            "title": "Imported Task 1",
                            "status": "TODO",
                            "priority": "HIGH",
                            "owner": "Chris"
                        },
                        {
                            "title": "Imported Task 2",
                            "status": "IN_PROGRESS",
                            "priority": "MEDIUM",
                            "owner": "Aria"
                        }
                    ]
                }
            ],
            "overwrite_existing": True,
            "import_tasks": True,
            "import_links": False
        }
        
        response = client.post("/api/projects/import/bulk", json=import_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["tasks_imported"] == 2
    
    def test_import_skip_existing(self, client):
        """Should skip existing projects when overwrite is false."""
        project_name = f"Skip Test {datetime.now().timestamp()}"
        
        # Create project first
        client.post("/api/projects", json={
            "name": project_name,
            "description": "Original",
            "status": "active",
            "priority": "LOW"
        })
        
        # Try to import same project with overwrite=False
        import_data = {
            "projects": [
                {
                    "name": project_name,
                    "description": "Should be skipped",
                    "status": "planning",
                    "priority": "HIGH"
                }
            ],
            "overwrite_existing": False,
            "import_tasks": False,
            "import_links": False
        }
        
        response = client.post("/api/projects/import/bulk", json=import_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["projects_skipped"] == 1
        assert data["projects_imported"] == 0
    
    def test_import_overwrite_existing(self, client):
        """Should overwrite existing projects when overwrite is true."""
        project_name = f"Overwrite Test {datetime.now().timestamp()}"
        
        # Create project first
        client.post("/api/projects", json={
            "name": project_name,
            "description": "Original",
            "status": "active",
            "priority": "LOW"
        })
        
        # Import same project with overwrite=True
        import_data = {
            "projects": [
                {
                    "name": project_name,
                    "description": "Updated via import",
                    "status": "planning",
                    "priority": "CRITICAL"
                }
            ],
            "overwrite_existing": True,
            "import_tasks": False,
            "import_links": False
        }
        
        response = client.post("/api/projects/import/bulk", json=import_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["projects_updated"] == 1
        
        # Verify update
        response = client.get(f"/api/projects/{project_name}")
        project = response.json()
        assert project["description"] == "Updated via import"
        assert project["priority"] == "CRITICAL"


class TestProjectCount:
    """Test project count endpoint."""
    
    def test_get_project_count(self, client):
        """Should return total project count."""
        response = client.get("/api/projects/count")
        assert response.status_code == 200
        
        data = response.json()
        assert "count" in data
        assert isinstance(data["count"], int)


class TestHealthCheck:
    """Test API health check."""
    
    def test_health_endpoint(self, client):
        """Should return healthy status."""
        response = client.get("/api/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "ok"


class TestRegressionScenarios:
    """Regression tests for common scenarios."""
    
    def test_create_update_delete_flow(self, client):
        """Test complete lifecycle of a project."""
        project_name = f"Lifecycle Test {datetime.now().timestamp()}"
        
        # Create
        response = client.post("/api/projects", json={
            "name": project_name,
            "description": "Step 1",
            "status": "planning",
            "priority": "LOW"
        })
        assert response.status_code == 201
        
        # Update status
        response = client.put(f"/api/projects/{project_name}", json={
            "status": "active",
            "priority": "HIGH"
        })
        assert response.status_code == 200
        assert response.json()["status"] == "active"
        
        # Update description
        response = client.put(f"/api/projects/{project_name}", json={
            "description": "Updated description"
        })
        assert response.status_code == 200
        
        # Verify ledger has events
        response = client.get(f"/api/projects/ledger?project={project_name}")
        assert response.status_code == 200
        events = response.json()
        assert len(events) >= 2  # At least create + update events
        
        # Delete
        response = client.delete(f"/api/projects/{project_name}")
        assert response.status_code == 204
    
    def test_special_characters_in_name(self, client):
        """Test handling of special characters in project names."""
        # Note: URL encoding should handle this
        project_name = f"Test Project & Special {datetime.now().timestamp()}"
        
        response = client.post("/api/projects", json={
            "name": project_name,
            "description": "Special chars test",
            "status": "active",
            "priority": "MEDIUM"
        })
        assert response.status_code == 201
        
        # Clean up
        import urllib.parse
        encoded_name = urllib.parse.quote(project_name, safe='')
        response = client.delete(f"/api/projects/{encoded_name}")
        assert response.status_code == 204
    
    def test_empty_project_list_handling(self, client):
        """Test behavior when no projects exist for a filter."""
        response = client.get("/api/projects?status=nonexistent_status_xyz")
        assert response.status_code == 200
        assert response.json() == []
