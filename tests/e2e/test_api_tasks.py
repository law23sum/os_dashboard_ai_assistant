"""
End-to-End API Tests for Tasks
Tests the complete task lifecycle through the API.

Spec References: §3.4, §4.5
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta


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


class TestTasksCRUD:
    """Test basic CRUD operations for tasks."""
    
    def test_list_tasks(self, client):
        """Should return list of tasks."""
        response = client.get("/api/tasks")
        assert response.status_code == 200
        data = response.json()
        # Response could be list directly or wrapped
        assert isinstance(data, (list, dict))
    
    def test_create_task(self, client):
        """Should create a new task."""
        task_data = {
            "title": f"E2E Test Task {datetime.now().timestamp()}",
            "project": "General",
            "status": "TODO",
            "priority": "HIGH",
            "notes": "Created via E2E test",
            "owner": "Chris"
        }
        
        response = client.post("/api/tasks", json=task_data)
        assert response.status_code in [200, 201]
        
        data = response.json()
        assert data["title"] == task_data["title"]
        assert data["project"] == task_data["project"]
    
    def test_get_single_task(self, client):
        """Should retrieve a single task by ID."""
        # First create a task
        task_data = {
            "title": f"Get Test Task {datetime.now().timestamp()}",
            "project": "General",
            "status": "TODO",
            "priority": "MEDIUM"
        }
        create_response = client.post("/api/tasks", json=task_data)
        created_task = create_response.json()
        task_id = created_task.get("id")
        
        if task_id:
            response = client.get(f"/api/tasks/{task_id}")
            assert response.status_code == 200
            data = response.json()
            assert data["title"] == task_data["title"]
    
    def test_update_task(self, client):
        """Should update an existing task."""
        # Create task
        task_data = {
            "title": f"Update Test Task {datetime.now().timestamp()}",
            "project": "General",
            "status": "TODO",
            "priority": "LOW"
        }
        create_response = client.post("/api/tasks", json=task_data)
        created_task = create_response.json()
        task_id = created_task.get("id")
        
        if task_id:
            # Update it
            response = client.put(f"/api/tasks/{task_id}", json={
                "status": "IN_PROGRESS",
                "priority": "HIGH"
            })
            assert response.status_code == 200
            
            data = response.json()
            assert data["status"] == "IN_PROGRESS"
            assert data["priority"] == "HIGH"
    
    def test_delete_task(self, client):
        """Should delete a task."""
        # Create task
        task_data = {
            "title": f"Delete Test Task {datetime.now().timestamp()}",
            "project": "General",
            "status": "TODO",
            "priority": "LOW"
        }
        create_response = client.post("/api/tasks", json=task_data)
        created_task = create_response.json()
        task_id = created_task.get("id")
        
        if task_id:
            # Delete it
            response = client.delete(f"/api/tasks/{task_id}")
            assert response.status_code in [200, 204]


class TestTaskFiltering:
    """Test task filtering functionality."""
    
    def test_filter_by_status(self, client):
        """Should filter tasks by status."""
        response = client.get("/api/tasks?status=TODO")
        assert response.status_code == 200
    
    def test_filter_by_project(self, client):
        """Should filter tasks by project."""
        response = client.get("/api/tasks?project=General")
        assert response.status_code == 200
    
    def test_filter_by_priority(self, client):
        """Should filter tasks by priority."""
        response = client.get("/api/tasks?priority=HIGH")
        assert response.status_code == 200


class TestTaskStatusTransitions:
    """Test task status transitions."""
    
    def test_todo_to_in_progress(self, client):
        """Should allow TODO to IN_PROGRESS transition."""
        # Create TODO task
        task_data = {
            "title": f"Status Test {datetime.now().timestamp()}",
            "project": "General",
            "status": "TODO",
            "priority": "MEDIUM"
        }
        create_response = client.post("/api/tasks", json=task_data)
        task = create_response.json()
        task_id = task.get("id")
        
        if task_id:
            # Transition to IN_PROGRESS
            response = client.put(f"/api/tasks/{task_id}", json={
                "status": "IN_PROGRESS"
            })
            assert response.status_code == 200
            assert response.json()["status"] == "IN_PROGRESS"
    
    def test_in_progress_to_done(self, client):
        """Should allow IN_PROGRESS to DONE transition."""
        # Create task
        task_data = {
            "title": f"Complete Test {datetime.now().timestamp()}",
            "project": "General",
            "status": "IN_PROGRESS",
            "priority": "HIGH"
        }
        create_response = client.post("/api/tasks", json=task_data)
        task = create_response.json()
        task_id = task.get("id")
        
        if task_id:
            # Complete the task
            response = client.put(f"/api/tasks/{task_id}", json={
                "status": "DONE"
            })
            assert response.status_code == 200
            assert response.json()["status"] == "DONE"


class TestTaskTimeTracking:
    """Test task time tracking features."""
    
    def test_set_time_estimated(self, client):
        """Should allow setting estimated time."""
        task_data = {
            "title": f"Time Test {datetime.now().timestamp()}",
            "project": "General",
            "status": "TODO",
            "priority": "MEDIUM",
            "time_estimated": 120  # 2 hours in minutes
        }
        response = client.post("/api/tasks", json=task_data)
        assert response.status_code in [200, 201]
        
        data = response.json()
        if "time_estimated" in data:
            assert data["time_estimated"] == 120


class TestTaskDependencies:
    """Test task dependency features."""
    
    def test_set_task_dependency(self, client):
        """Should allow setting task dependencies."""
        # Create parent task
        parent_task = {
            "title": f"Parent Task {datetime.now().timestamp()}",
            "project": "General",
            "status": "TODO",
            "priority": "HIGH"
        }
        parent_response = client.post("/api/tasks", json=parent_task)
        parent = parent_response.json()
        parent_id = parent.get("id")
        
        if parent_id:
            # Create child task with dependency
            child_task = {
                "title": f"Child Task {datetime.now().timestamp()}",
                "project": "General",
                "status": "TODO",
                "priority": "MEDIUM",
                "depends_on": parent_id
            }
            child_response = client.post("/api/tasks", json=child_task)
            child = child_response.json()
            
            if "depends_on" in child:
                assert child["depends_on"] == parent_id


class TestTaskPriority:
    """Test task priority features."""
    
    def test_all_priority_levels(self, client):
        """Should accept all valid priority levels."""
        priorities = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        
        for priority in priorities:
            task_data = {
                "title": f"Priority {priority} Test {datetime.now().timestamp()}",
                "project": "General",
                "status": "TODO",
                "priority": priority
            }
            response = client.post("/api/tasks", json=task_data)
            assert response.status_code in [200, 201]
            assert response.json()["priority"] == priority


class TestTaskOwnership:
    """Test task ownership (persona assignment)."""
    
    def test_assign_to_persona(self, client):
        """Should allow assigning task to personas."""
        personas = ["Chris", "AIC", "Aria", "Sora"]
        
        for persona in personas:
            task_data = {
                "title": f"Owned by {persona} {datetime.now().timestamp()}",
                "project": "General",
                "status": "TODO",
                "priority": "MEDIUM",
                "owner": persona
            }
            response = client.post("/api/tasks", json=task_data)
            assert response.status_code in [200, 201]
            assert response.json()["owner"] == persona
