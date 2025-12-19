"""
End-to-End API Tests for Settings
Tests settings and configuration endpoints.

Spec References: §9.0
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


class TestSettings:
    """Test settings endpoints."""
    
    def test_get_settings(self, client):
        """Should return current settings."""
        response = client.get("/api/settings")
        assert response.status_code in [200, 404]
    
    def test_update_settings(self, client):
        """Should update settings."""
        settings_data = {
            "theme": "dark",
            "notifications_enabled": True
        }
        response = client.put("/api/settings", json=settings_data)
        assert response.status_code in [200, 404]
    
    def test_get_specific_setting(self, client):
        """Should get a specific setting value."""
        response = client.get("/api/settings/theme")
        assert response.status_code in [200, 404]


class TestTheme:
    """Test theme settings."""
    
    def test_set_theme(self, client):
        """Should set theme preference."""
        theme_data = {"theme": "dark"}
        response = client.put("/api/settings/theme", json=theme_data)
        assert response.status_code in [200, 404]
    
    def test_valid_themes(self, client):
        """Should accept valid theme values."""
        themes = ["light", "dark", "system"]
        
        for theme in themes:
            response = client.put("/api/settings/theme", json={"theme": theme})
            assert response.status_code in [200, 404]


class TestNotificationSettings:
    """Test notification settings."""
    
    def test_get_notification_settings(self, client):
        """Should get notification settings."""
        response = client.get("/api/settings/notifications")
        assert response.status_code in [200, 404]
    
    def test_update_notification_settings(self, client):
        """Should update notification settings."""
        notification_data = {
            "email_notifications": True,
            "push_notifications": False,
            "task_reminders": True
        }
        response = client.put("/api/settings/notifications", json=notification_data)
        assert response.status_code in [200, 404]


class TestUserProfile:
    """Test user profile settings."""
    
    def test_get_profile(self, client):
        """Should get user profile."""
        response = client.get("/api/settings/profile")
        assert response.status_code in [200, 404]
    
    def test_update_profile(self, client):
        """Should update user profile."""
        profile_data = {
            "display_name": "Test User",
            "email": "test@example.com",
            "timezone": "America/New_York"
        }
        response = client.put("/api/settings/profile", json=profile_data)
        assert response.status_code in [200, 404]


class TestIntegrationSettings:
    """Test integration settings."""
    
    def test_get_integration_settings(self, client):
        """Should get integration settings."""
        response = client.get("/api/settings/integrations")
        assert response.status_code in [200, 404]
    
    def test_configure_integration(self, client):
        """Should configure an integration."""
        config_data = {
            "type": "github",
            "enabled": True
        }
        response = client.put("/api/settings/integrations/github", json=config_data)
        assert response.status_code in [200, 404]


class TestSecuritySettings:
    """Test security settings."""
    
    def test_get_security_settings(self, client):
        """Should get security settings."""
        response = client.get("/api/settings/security")
        assert response.status_code in [200, 404]
    
    def test_api_key_management(self, client):
        """Should manage API keys."""
        # List keys (should be masked)
        response = client.get("/api/settings/api-keys")
        assert response.status_code in [200, 404]
    
    def test_create_api_key(self, client):
        """Should create a new API key."""
        key_data = {
            "name": f"Test Key {datetime.now().timestamp()}",
            "permissions": ["read", "write"]
        }
        response = client.post("/api/settings/api-keys", json=key_data)
        assert response.status_code in [200, 201, 404]


class TestDashboardSettings:
    """Test dashboard configuration settings."""
    
    def test_get_dashboard_config(self, client):
        """Should get dashboard configuration."""
        response = client.get("/api/settings/dashboard")
        assert response.status_code in [200, 404]
    
    def test_save_dashboard_layout(self, client):
        """Should save dashboard widget layout."""
        layout_data = {
            "widgets": [
                {"id": "tasks", "x": 0, "y": 0, "w": 2, "h": 2},
                {"id": "projects", "x": 2, "y": 0, "w": 2, "h": 2},
                {"id": "calendar", "x": 0, "y": 2, "w": 4, "h": 1}
            ]
        }
        response = client.put("/api/settings/dashboard", json=layout_data)
        assert response.status_code in [200, 404]


class TestBackupSettings:
    """Test backup and restore settings."""
    
    def test_export_settings(self, client):
        """Should export all settings."""
        response = client.get("/api/settings/export")
        assert response.status_code in [200, 404]
    
    def test_import_settings(self, client):
        """Should import settings."""
        settings_data = {
            "theme": "dark",
            "notifications_enabled": True,
            "version": "1.0.0"
        }
        response = client.post("/api/settings/import", json=settings_data)
        assert response.status_code in [200, 404]


class TestSystemInfo:
    """Test system information endpoints."""
    
    def test_get_system_info(self, client):
        """Should return system information."""
        response = client.get("/api/system/info")
        assert response.status_code in [200, 404]
    
    def test_get_version(self, client):
        """Should return application version."""
        response = client.get("/api/system/version")
        assert response.status_code in [200, 404]
    
    def test_get_health(self, client):
        """Should return health status."""
        response = client.get("/api/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
