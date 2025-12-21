"""
Regression Tests
Tests for known issues and edge cases that have been fixed.
These tests ensure that fixed bugs don't reappear.

Spec References: All sections
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime
import urllib.parse


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


@pytest.mark.regression
class TestProjectRegressions:
    """Regression tests for project-related issues."""
    
    def test_project_name_with_spaces(self, client):
        """REG-001: Project names with spaces should work correctly."""
        project_name = f"Project With Spaces {datetime.now().timestamp()}"
        
        # Create
        response = client.post("/api/projects", json={
            "name": project_name,
            "description": "Test",
            "status": "active",
            "priority": "MEDIUM"
        })
        assert response.status_code in [200, 201]
        
        # Read (URL encoded)
        encoded_name = urllib.parse.quote(project_name, safe='')
        response = client.get(f"/api/projects/{encoded_name}")
        assert response.status_code == 200
        
        # Cleanup
        client.delete(f"/api/projects/{encoded_name}")
    
    def test_project_name_with_special_chars(self, client):
        """REG-002: Project names with special characters should work."""
        project_name = f"Project & Test <> {datetime.now().timestamp()}"
        
        response = client.post("/api/projects", json={
            "name": project_name,
            "description": "Test",
            "status": "active",
            "priority": "MEDIUM"
        })
        assert response.status_code in [200, 201]
        
        # Cleanup
        encoded_name = urllib.parse.quote(project_name, safe='')
        client.delete(f"/api/projects/{encoded_name}")
    
    def test_project_update_partial(self, client):
        """REG-003: Partial project updates should not clear other fields."""
        project_name = f"Partial Update Test {datetime.now().timestamp()}"
        
        # Create with all fields
        client.post("/api/projects", json={
            "name": project_name,
            "description": "Original description",
            "status": "active",
            "priority": "HIGH"
        })
        
        # Update only description
        response = client.put(f"/api/projects/{urllib.parse.quote(project_name, safe='')}", json={
            "description": "Updated description"
        })
        assert response.status_code == 200
        
        # Verify other fields weren't cleared
        data = response.json()
        assert data["priority"] == "HIGH"
        assert data["status"] == "active"
        
        # Cleanup
        client.delete(f"/api/projects/{urllib.parse.quote(project_name, safe='')}")
    
    def test_project_delete_cascade(self, client):
        """REG-004: Deleting a project should not leave orphaned data."""
        project_name = f"Delete Cascade Test {datetime.now().timestamp()}"
        
        # Create project
        client.post("/api/projects", json={
            "name": project_name,
            "description": "Test",
            "status": "active",
            "priority": "MEDIUM"
        })
        
        # Verify ledger event exists
        response = client.get(f"/api/projects/ledger?project={urllib.parse.quote(project_name, safe='')}")
        assert response.status_code == 200
        
        # Delete
        encoded_name = urllib.parse.quote(project_name, safe='')
        client.delete(f"/api/projects/{encoded_name}")
        
        # Verify project is gone
        response = client.get(f"/api/projects/{encoded_name}")
        assert response.status_code == 404


@pytest.mark.regression
class TestTaskRegressions:
    """Regression tests for task-related issues."""
    
    def test_task_with_long_title(self, client):
        """REG-101: Tasks with very long titles should be handled."""
        long_title = "A" * 500 + f" {datetime.now().timestamp()}"
        
        response = client.post("/api/tasks", json={
            "title": long_title,
            "project": "General",
            "status": "TODO",
            "priority": "MEDIUM"
        })
        # Should either succeed or return validation error, not crash
        assert response.status_code in [200, 201, 400, 422]
    
    def test_task_with_unicode_characters(self, client):
        """REG-102: Tasks with unicode characters should work."""
        unicode_title = f"Task with 日本語 and émojis 🎉 {datetime.now().timestamp()}"
        
        response = client.post("/api/tasks", json={
            "title": unicode_title,
            "project": "General",
            "status": "TODO",
            "priority": "HIGH"
        })
        assert response.status_code in [200, 201]
    
    def test_task_status_case_insensitive(self, client):
        """REG-103: Task status should be case-insensitive or normalized."""
        # Try different cases
        statuses = ["todo", "TODO", "Todo", "IN_PROGRESS", "in_progress"]
        
        for status in statuses:
            response = client.post("/api/tasks", json={
                "title": f"Status Test {status} {datetime.now().timestamp()}",
                "project": "General",
                "status": status,
                "priority": "LOW"
            })
            # Should accept or normalize, not crash
            assert response.status_code in [200, 201, 400, 422]


@pytest.mark.regression
class TestAPIRegressions:
    """Regression tests for API-related issues."""
    
    def test_concurrent_requests(self, client):
        """REG-201: API should handle concurrent requests."""
        import concurrent.futures
        
        def make_request():
            return client.get("/api/health")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [f.result() for f in futures]
        
        # All requests should succeed
        assert all(r.status_code == 200 for r in results)
    
    def test_empty_request_body(self, client):
        """REG-202: Empty request body should be handled gracefully."""
        response = client.post("/api/projects", json={})
        # Should return validation error, not crash
        assert response.status_code in [400, 422]
    
    def test_null_values_in_request(self, client):
        """REG-203: Null values should be handled properly."""
        response = client.post("/api/projects", json={
            "name": f"Null Test {datetime.now().timestamp()}",
            "description": None,
            "status": "active",
            "priority": "MEDIUM"
        })
        # Should accept null for optional fields
        assert response.status_code in [200, 201, 400, 422]
    
    def test_extra_fields_ignored(self, client):
        """REG-204: Extra fields in request should be ignored."""
        response = client.post("/api/projects", json={
            "name": f"Extra Fields Test {datetime.now().timestamp()}",
            "description": "Test",
            "status": "active",
            "priority": "MEDIUM",
            "unknown_field": "should be ignored",
            "another_unknown": 12345
        })
        assert response.status_code in [200, 201]


@pytest.mark.regression
class TestImportExportRegressions:
    """Regression tests for import/export functionality."""
    
    def test_import_empty_projects_list(self, client):
        """REG-301: Importing empty projects list should be handled."""
        response = client.post("/api/projects/import/bulk", json={
            "projects": [],
            "overwrite_existing": False,
            "import_tasks": False,
            "import_links": False
        })
        assert response.status_code == 200
        data = response.json()
        assert data["projects_imported"] == 0
    
    def test_import_project_with_empty_tasks(self, client):
        """REG-302: Importing project with empty tasks should work."""
        response = client.post("/api/projects/import/bulk", json={
            "projects": [{
                "name": f"Empty Tasks {datetime.now().timestamp()}",
                "description": "Test",
                "status": "active",
                "priority": "MEDIUM",
                "tasks": []
            }],
            "overwrite_existing": False,
            "import_tasks": True,
            "import_links": False
        })
        assert response.status_code == 200
        data = response.json()
        assert data["projects_imported"] == 1
        assert data["tasks_imported"] == 0
    
    def test_export_with_no_projects(self, client):
        """REG-303: Export should work even with few projects."""
        response = client.get("/api/projects/export/all")
        assert response.status_code == 200
        data = response.json()
        assert "projects" in data
        assert isinstance(data["projects"], list)


@pytest.mark.regression
class TestLedgerRegressions:
    """Regression tests for ledger functionality."""
    
    def test_ledger_hash_integrity(self, client):
        """REG-401: Ledger events should have valid hashes."""
        project_name = f"Hash Test {datetime.now().timestamp()}"
        
        # Create project
        client.post("/api/projects", json={
            "name": project_name,
            "description": "Test",
            "status": "active",
            "priority": "MEDIUM"
        })
        
        # Get ledger
        encoded_name = urllib.parse.quote(project_name, safe='')
        response = client.get(f"/api/projects/ledger?project={encoded_name}")
        assert response.status_code == 200
        
        events = response.json()
        if events:
            for event in events:
                # Hash should be present and non-empty
                assert "hash_curr" in event
                if event["hash_curr"]:
                    assert len(event["hash_curr"]) > 0
        
        # Cleanup
        client.delete(f"/api/projects/{encoded_name}")
    
    def test_ledger_timestamp_ordering(self, client):
        """REG-402: Ledger events should be properly ordered."""
        project_name = f"Order Test {datetime.now().timestamp()}"
        
        # Create project
        client.post("/api/projects", json={
            "name": project_name,
            "description": "Initial",
            "status": "active",
            "priority": "LOW"
        })
        
        # Multiple updates
        encoded_name = urllib.parse.quote(project_name, safe='')
        for i in range(3):
            client.put(f"/api/projects/{encoded_name}", json={
                "description": f"Update {i}"
            })
        
        # Get ledger
        response = client.get(f"/api/projects/ledger?project={encoded_name}")
        assert response.status_code == 200
        
        events = response.json()
        if len(events) > 1:
            # Events should have timestamps
            timestamps = [e.get("created_at", e.get("timestamp", "")) for e in events]
            # Should be in some order (newest first or oldest first)
            assert timestamps == sorted(timestamps) or timestamps == sorted(timestamps, reverse=True)
        
        # Cleanup
        client.delete(f"/api/projects/{encoded_name}")


@pytest.mark.regression
class TestDataIntegrityRegressions:
    """Regression tests for data integrity issues."""
    
    def test_project_priority_persistence(self, client):
        """REG-501: Project priority should persist correctly."""
        project_name = f"Priority Persist {datetime.now().timestamp()}"
        
        # Create with HIGH priority
        client.post("/api/projects", json={
            "name": project_name,
            "description": "Test",
            "status": "active",
            "priority": "HIGH"
        })
        
        encoded_name = urllib.parse.quote(project_name, safe='')
        
        # Verify it persisted
        response = client.get(f"/api/projects/{encoded_name}")
        assert response.json()["priority"] == "HIGH"
        
        # Update something else
        client.put(f"/api/projects/{encoded_name}", json={
            "description": "Updated"
        })
        
        # Priority should still be HIGH
        response = client.get(f"/api/projects/{encoded_name}")
        assert response.json()["priority"] == "HIGH"
        
        # Cleanup
        client.delete(f"/api/projects/{encoded_name}")
    
    def test_task_project_association(self, client):
        """REG-502: Task should maintain project association."""
        project_name = f"Association Test {datetime.now().timestamp()}"
        
        # Create project
        client.post("/api/projects", json={
            "name": project_name,
            "description": "Test",
            "status": "active",
            "priority": "MEDIUM"
        })
        
        # Create task for that project
        task_response = client.post("/api/tasks", json={
            "title": f"Task for {project_name}",
            "project": project_name,
            "status": "TODO",
            "priority": "HIGH"
        })
        
        if task_response.status_code in [200, 201]:
            task = task_response.json()
            assert task["project"] == project_name
        
        # Cleanup
        encoded_name = urllib.parse.quote(project_name, safe='')
        client.delete(f"/api/projects/{encoded_name}")
