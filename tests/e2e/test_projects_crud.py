"""
End-to-End Tests for Projects CRUD Operations
Tests the full stack from API to database for project management.
"""

import pytest
from httpx import AsyncClient
from fastapi import status


class TestProjectsCRUD:
    """Test suite for Projects CRUD operations."""

    @pytest.mark.asyncio
    async def test_list_projects_empty(self, async_client: AsyncClient):
        """Test listing projects when database is empty."""
        response = await async_client.get("/api/projects/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_create_project(self, async_client: AsyncClient):
        """Test creating a new project."""
        project_data = {
            "name": "Test Project E2E",
            "description": "E2E test project",
            "status": "active",
            "priority": "HIGH",
            "order_num": 1,
        }
        response = await async_client.post("/api/projects/", json=project_data)
        assert response.status_code == status.HTTP_201_CREATED
        
        data = response.json()
        assert data["name"] == project_data["name"]
        assert data["description"] == project_data["description"]
        assert data["status"] == project_data["status"]
        assert data["priority"] == project_data["priority"]

    @pytest.mark.asyncio
    async def test_get_project(self, async_client: AsyncClient):
        """Test retrieving a specific project."""
        # First create a project
        project_data = {
            "name": "Test Get Project",
            "description": "Project for get test",
            "status": "active",
            "priority": "MEDIUM",
        }
        create_response = await async_client.post("/api/projects/", json=project_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        
        # Now get it
        response = await async_client.get(f"/api/projects/{project_data['name']}")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["name"] == project_data["name"]
        assert data["description"] == project_data["description"]

    @pytest.mark.asyncio
    async def test_update_project(self, async_client: AsyncClient):
        """Test updating an existing project."""
        # Create project
        project_data = {
            "name": "Test Update Project",
            "description": "Original description",
            "status": "planning",
            "priority": "LOW",
        }
        create_response = await async_client.post("/api/projects/", json=project_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        
        # Update it
        update_data = {
            "description": "Updated description",
            "status": "active",
            "priority": "HIGH",
        }
        response = await async_client.put(
            f"/api/projects/{project_data['name']}", json=update_data
        )
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["description"] == update_data["description"]
        assert data["status"] == update_data["status"]
        assert data["priority"] == update_data["priority"]

    @pytest.mark.asyncio
    async def test_delete_project(self, async_client: AsyncClient):
        """Test deleting a project."""
        # Create project
        project_data = {
            "name": "Test Delete Project",
            "description": "Project to be deleted",
            "status": "active",
            "priority": "MEDIUM",
        }
        create_response = await async_client.post("/api/projects/", json=project_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        
        # Delete it
        response = await async_client.delete(f"/api/projects/{project_data['name']}")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify it's gone
        get_response = await async_client.get(f"/api/projects/{project_data['name']}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_get_nonexistent_project(self, async_client: AsyncClient):
        """Test getting a project that doesn't exist."""
        response = await async_client.get("/api/projects/NonexistentProject")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_create_duplicate_project(self, async_client: AsyncClient):
        """Test creating a project with duplicate name."""
        project_data = {
            "name": "Duplicate Test",
            "description": "First project",
            "status": "active",
            "priority": "MEDIUM",
        }
        
        # Create first time
        response1 = await async_client.post("/api/projects/", json=project_data)
        assert response1.status_code == status.HTTP_201_CREATED
        
        # Try to create again with same name
        response2 = await async_client.post("/api/projects/", json=project_data)
        # Should succeed as upsert, or fail - depends on implementation
        assert response2.status_code in [
            status.HTTP_201_CREATED,
            status.HTTP_200_OK,
            status.HTTP_409_CONFLICT,
        ]

    @pytest.mark.asyncio
    async def test_project_ledger_creation(self, async_client: AsyncClient):
        """Test that ledger event is created when project is created."""
        project_data = {
            "name": "Ledger Test Project",
            "description": "Test ledger generation",
            "status": "active",
            "priority": "HIGH",
        }
        
        # Create project
        create_response = await async_client.post("/api/projects/", json=project_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        
        # Check ledger
        ledger_response = await async_client.get(
            f"/api/projects/{project_data['name']}/ledger"
        )
        assert ledger_response.status_code == status.HTTP_200_OK
        
        ledger_events = ledger_response.json()
        assert len(ledger_events) > 0
        assert ledger_events[0]["event_type"] == "project_created"

    @pytest.mark.asyncio
    async def test_project_intelligence(self, async_client: AsyncClient):
        """Test project intelligence endpoint."""
        # Create a project
        project_data = {
            "name": "Intelligence Test",
            "description": "Test intelligence metrics",
            "status": "active",
            "priority": "HIGH",
        }
        create_response = await async_client.post("/api/projects/", json=project_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        
        # Get intelligence
        response = await async_client.get(
            f"/api/projects/{project_data['name']}/intelligence"
        )
        assert response.status_code == status.HTTP_200_OK
        
        intel = response.json()
        assert "health_score" in intel
        assert "risk_level" in intel
        assert "completion_ratio" in intel
        assert intel["project_id"] == project_data["name"]

    @pytest.mark.asyncio
    async def test_list_all_project_intelligence(self, async_client: AsyncClient):
        """Test listing intelligence for all projects."""
        response = await async_client.get("/api/projects/intelligence")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert isinstance(data, list)
        
        if len(data) > 0:
            assert "health_score" in data[0]
            assert "risk_level" in data[0]
            assert "project_id" in data[0]


class TestProjectLinks:
    """Test suite for project links (OneNote, documents, etc.)."""

    @pytest.mark.asyncio
    async def test_list_project_links(self, async_client: AsyncClient):
        """Test listing links for all projects."""
        response = await async_client.get("/api/projects/links")
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json(), list)

    @pytest.mark.asyncio
    async def test_get_links_for_specific_project(self, async_client: AsyncClient):
        """Test getting links for a specific project."""
        # Create a project first
        project_data = {
            "name": "Links Test Project",
            "description": "For testing links",
            "status": "active",
            "priority": "MEDIUM",
        }
        create_response = await async_client.post("/api/projects/", json=project_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        
        # Get its links
        response = await async_client.get(
            f"/api/projects/{project_data['name']}/links"
        )
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json(), list)


class TestProjectTRF:
    """Test suite for TRF (Theoretical Reasoning Framework) endpoints."""

    @pytest.mark.asyncio
    async def test_get_project_trf(self, async_client: AsyncClient):
        """Test getting TRF data for a project."""
        # Create a project
        project_data = {
            "name": "TRF Test Project",
            "description": "For testing TRF",
            "status": "active",
            "priority": "HIGH",
        }
        create_response = await async_client.post("/api/projects/", json=project_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        
        # Get TRF data
        response = await async_client.get(f"/api/projects/{project_data['name']}/trf")
        assert response.status_code == status.HTTP_200_OK
        
        trf_data = response.json()
        assert "entropy" in trf_data
        assert "resonance" in trf_data
        assert "continuity" in trf_data
        assert "heuristics" in trf_data
        assert "personas" in trf_data
        assert "traces" in trf_data
        assert trf_data["project_id"] == project_data["name"]


class TestProjectInsights:
    """Test suite for AI-powered project insights."""

    @pytest.mark.asyncio
    async def test_get_project_insights(self, async_client: AsyncClient):
        """Test getting AI insights for a project."""
        # Create a project
        project_data = {
            "name": "Insights Test Project",
            "description": "For testing insights",
            "status": "active",
            "priority": "HIGH",
        }
        create_response = await async_client.post("/api/projects/", json=project_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        
        # Get insights
        response = await async_client.get(
            f"/api/projects/{project_data['name']}/insights"
        )
        assert response.status_code == status.HTTP_200_OK
        
        insights = response.json()
        assert "project" in insights
        assert "risk" in insights
        assert "forecast" in insights
        assert insights["project"] == project_data["name"]
        
        # Check risk structure
        risk = insights["risk"]
        assert "risk_score" in risk
        assert "severity" in risk
        assert "risks" in risk
        assert "recommendations" in risk
        
        # Check forecast structure
        forecast = insights["forecast"]
        assert "confidence" in forecast
        assert "reasoning" in forecast


class TestDataManagement:
    """Test suite for data backup/restore functionality."""

    @pytest.mark.asyncio
    async def test_get_data_stats(self, async_client: AsyncClient):
        """Test getting data statistics."""
        response = await async_client.get("/api/data/stats")
        assert response.status_code == status.HTTP_200_OK
        
        stats = response.json()
        assert "projects" in stats
        assert "tasks" in stats
        assert "ledger_events" in stats
        assert "database_size_mb" in stats

    @pytest.mark.asyncio
    async def test_create_backup(self, async_client: AsyncClient):
        """Test creating a database backup."""
        response = await async_client.post("/api/data/backup")
        assert response.status_code == status.HTTP_200_OK
        
        backup = response.json()
        assert backup["success"] is True
        assert "backup_file" in backup
        assert "timestamp" in backup
        assert "size_bytes" in backup

    @pytest.mark.asyncio
    async def test_list_backups(self, async_client: AsyncClient):
        """Test listing available backups."""
        # Create a backup first
        await async_client.post("/api/data/backup")
        
        # List backups
        response = await async_client.get("/api/data/backups")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "backups" in data
        assert isinstance(data["backups"], list)

    @pytest.mark.asyncio
    async def test_export_to_json(self, async_client: AsyncClient):
        """Test exporting data to JSON."""
        response = await async_client.post("/api/data/export-json")
        assert response.status_code == status.HTTP_200_OK
        assert response.headers["content-type"] == "application/json"
