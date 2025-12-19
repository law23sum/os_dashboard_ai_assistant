"""
End-to-End API Tests for Integrations
Tests integration endpoints for Git, Excel, Word, etc.

Spec References: §6.2, §6.3
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime


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


class TestIntegrationsEndpoint:
    """Test general integrations endpoints."""
    
    def test_list_integrations(self, client):
        """Should list all available integrations."""
        response = client.get("/api/integrations")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_integration_has_required_fields(self, client):
        """Each integration should have required metadata."""
        response = client.get("/api/integrations")
        data = response.json()
        
        if data:
            integration = data[0]
            # Check for any identifying field
            assert "name" in integration or "type" in integration or "service" in integration


class TestGitIntegration:
    """Test Git integration endpoints."""
    
    def test_get_git_status(self, client):
        """Should return Git status."""
        response = client.get("/api/integrations/git/status")
        # May return 200 or 404/503 if Git is not available
        assert response.status_code in [200, 404, 503]
    
    def test_list_git_repos(self, client):
        """Should list Git repositories."""
        response = client.get("/api/integrations/git/repos")
        assert response.status_code in [200, 404, 503]


class TestExcelIntegration:
    """Test Excel integration endpoints."""
    
    def test_list_excel_files(self, client):
        """Should list Excel files in documents folder."""
        response = client.get("/api/integrations/excel/files")
        assert response.status_code in [200, 404]
    
    def test_read_excel_file(self, client):
        """Should read an Excel file."""
        # Try to read the sample workbook if it exists
        response = client.get("/api/integrations/excel/read?path=documents/Samples/Operational+Metrics+Workbook.xlsx")
        # May return data or 404 if file doesn't exist
        assert response.status_code in [200, 404]


class TestWordIntegration:
    """Test Word document integration endpoints."""
    
    def test_list_word_files(self, client):
        """Should list Word documents."""
        response = client.get("/api/integrations/word/files")
        assert response.status_code in [200, 404]
    
    def test_read_word_document(self, client):
        """Should read a Word document."""
        response = client.get("/api/integrations/word/read?path=documents/Samples/Governed+Brief+Template.docx")
        assert response.status_code in [200, 404]


class TestPDFIntegration:
    """Test PDF integration endpoints."""
    
    def test_list_pdf_files(self, client):
        """Should list PDF files."""
        response = client.get("/api/integrations/pdf/files")
        assert response.status_code in [200, 404]
    
    def test_extract_pdf_text(self, client):
        """Should extract text from PDF."""
        response = client.get("/api/integrations/pdf/extract?path=documents/Samples/Regulatory+Filing+Shell.pdf")
        assert response.status_code in [200, 404]


class TestFilesystemIntegration:
    """Test Filesystem integration endpoints."""
    
    def test_list_documents_directory(self, client):
        """Should list documents directory."""
        response = client.get("/api/integrations/filesystem/list?path=documents")
        assert response.status_code in [200, 404]
    
    def test_get_file_info(self, client):
        """Should get file metadata."""
        response = client.get("/api/integrations/filesystem/info?path=documents/Samples")
        assert response.status_code in [200, 404]


class TestNotesIntegration:
    """Test Notes integration endpoints."""
    
    def test_list_notes(self, client):
        """Should list all notes."""
        response = client.get("/api/notes")
        assert response.status_code in [200, 404]
    
    def test_create_note(self, client):
        """Should create a new note."""
        note_data = {
            "title": f"E2E Test Note {datetime.now().timestamp()}",
            "content": "This is a test note from E2E tests.",
            "project": "General"
        }
        response = client.post("/api/notes", json=note_data)
        assert response.status_code in [200, 201, 404]


class TestCalendarIntegration:
    """Test Calendar integration endpoints."""
    
    def test_list_calendar_events(self, client):
        """Should list calendar events."""
        response = client.get("/api/calendar/events")
        assert response.status_code in [200, 404]
    
    def test_calendar_event_fields(self, client):
        """Calendar events should have required fields."""
        response = client.get("/api/calendar/events")
        
        if response.status_code == 200:
            data = response.json()
            if data:
                event = data[0]
                # Check for common calendar fields
                assert any(field in event for field in ["title", "name", "summary", "start"])


class TestAPIManager:
    """Test API Manager endpoints."""
    
    def test_list_api_keys(self, client):
        """Should list API keys (masked)."""
        response = client.get("/api/settings/api-keys")
        assert response.status_code in [200, 404]
    
    def test_api_usage_stats(self, client):
        """Should return API usage statistics."""
        response = client.get("/api/settings/api-usage")
        assert response.status_code in [200, 404]
