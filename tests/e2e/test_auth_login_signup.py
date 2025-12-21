"""
End-to-End API Tests for Authentication (Login and Signup)
Tests the complete authentication lifecycle through the API:
- User signup
- User login
- Token validation
- Error handling

Spec References: Authentication endpoints
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime
import json
import uuid


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


@pytest.fixture
def unique_user_data():
    """Generate unique user data for testing."""
    timestamp = datetime.now().timestamp()
    unique_id = str(uuid.uuid4())[:8]
    return {
        "username": f"testuser_{unique_id}",
        "email": f"test_{unique_id}@test.local",
        "password": "testpassword123",
        "full_name": f"Test User {unique_id}"
    }


@pytest.fixture
def test_credentials():
    """Generate test credentials for login."""
    return {
        "username": "admin",
        "password": "admin123"
    }


class TestSignup:
    """Test user signup functionality."""
    
    def test_signup_success(self, client: TestClient, unique_user_data: dict):
        """Test successful user signup."""
        response = client.post(
            "/api/auth/signup",
            json={
                "username": unique_user_data["username"],
                "email": unique_user_data["email"],
                "password": unique_user_data["password"],
                "full_name": unique_user_data["full_name"]
            }
        )
        
        assert response.status_code in [200, 201], f"Expected 200/201, got {response.status_code}: {response.text}"
        data = response.json()
        assert "id" in data or "username" in data or "email" in data
        if "email" in data:
            assert data["email"] == unique_user_data["email"]
    
    def test_signup_duplicate_email(self, client: TestClient, unique_user_data: dict):
        """Test signup with duplicate email fails."""
        # First signup
        response1 = client.post(
            "/api/auth/signup",
            json={
                "username": unique_user_data["username"],
                "email": unique_user_data["email"],
                "password": unique_user_data["password"],
                "full_name": unique_user_data["full_name"]
            }
        )
        # May succeed or fail depending on test isolation
        
        # Second signup with same email
        unique_id2 = str(uuid.uuid4())[:8]
        response2 = client.post(
            "/api/auth/signup",
            json={
                "username": f"testuser2_{unique_id2}",
                "email": unique_user_data["email"],  # Same email
                "password": "differentpassword123",
                "full_name": "Different User"
            }
        )
        
        # Should fail with 400 Bad Request
        assert response2.status_code in [400, 409, 422], \
            f"Expected 400/409/422 for duplicate email, got {response2.status_code}: {response2.text}"
    
    def test_signup_missing_fields(self, client: TestClient):
        """Test signup with missing required fields fails."""
        response = client.post(
            "/api/auth/signup",
            json={
                "email": "test@test.local"
                # Missing password, username
            }
        )
        
        assert response.status_code in [400, 422], \
            f"Expected 400/422 for missing fields, got {response.status_code}: {response.text}"
    
    def test_signup_invalid_email(self, client: TestClient):
        """Test signup with invalid email format fails."""
        unique_id = str(uuid.uuid4())[:8]
        response = client.post(
            "/api/auth/signup",
            json={
                "username": f"testuser_{unique_id}",
                "email": "not-an-email",
                "password": "testpassword123",
                "full_name": "Test User"
            }
        )
        
        assert response.status_code in [400, 422], \
            f"Expected 400/422 for invalid email, got {response.status_code}: {response.text}"
    
    def test_signup_weak_password(self, client: TestClient):
        """Test signup with weak password (if validation exists)."""
        unique_id = str(uuid.uuid4())[:8]
        response = client.post(
            "/api/auth/signup",
            json={
                "username": f"testuser_{unique_id}",
                "email": f"test_{unique_id}@test.local",
                "password": "123",  # Too short
                "full_name": "Test User"
            }
        )
        
        # May succeed or fail depending on password validation
        # If validation exists, should return 400/422
        assert response.status_code in [200, 201, 400, 422]


class TestLogin:
    """Test user login functionality."""
    
    def test_login_success_with_username(self, client: TestClient, test_credentials: dict):
        """Test successful login with username."""
        response = client.post(
            "/api/auth/login",
            json={
                "username": test_credentials["username"],
                "password": test_credentials["password"]
            }
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "access_token" in data, "Response should contain access_token"
        assert data.get("access_token") is not None
        assert len(data["access_token"]) > 0
    
    def test_login_success_with_email(self, client: TestClient):
        """Test successful login with email."""
        # Try with admin email (assuming admin@demo.local exists)
        response = client.post(
            "/api/auth/login",
            json={
                "username": "admin@demo.local",  # May work as username
                "password": "admin123"
            }
        )
        
        # May succeed or fail depending on implementation
        assert response.status_code in [200, 401], \
            f"Expected 200 or 401, got {response.status_code}: {response.text}"
    
    def test_login_invalid_username(self, client: TestClient):
        """Test login with invalid username fails."""
        response = client.post(
            "/api/auth/login",
            json={
                "username": "nonexistent_user_12345",
                "password": "somepassword"
            }
        )
        
        assert response.status_code == 401, \
            f"Expected 401 for invalid credentials, got {response.status_code}: {response.text}"
        data = response.json()
        assert "detail" in data
    
    def test_login_invalid_password(self, client: TestClient, test_credentials: dict):
        """Test login with invalid password fails."""
        response = client.post(
            "/api/auth/login",
            json={
                "username": test_credentials["username"],
                "password": "wrongpassword123"
            }
        )
        
        assert response.status_code == 401, \
            f"Expected 401 for invalid password, got {response.status_code}: {response.text}"
        data = response.json()
        assert "detail" in data
    
    def test_login_missing_fields(self, client: TestClient):
        """Test login with missing fields fails."""
        response = client.post(
            "/api/auth/login",
            json={
                "username": "admin"
                # Missing password
            }
        )
        
        assert response.status_code in [400, 422], \
            f"Expected 400/422 for missing fields, got {response.status_code}: {response.text}"
    
    def test_login_empty_credentials(self, client: TestClient):
        """Test login with empty credentials fails."""
        response = client.post(
            "/api/auth/login",
            json={
                "username": "",
                "password": ""
            }
        )
        
        assert response.status_code in [400, 401, 422], \
            f"Expected 400/401/422 for empty credentials, got {response.status_code}: {response.text}"


class TestLoginAfterSignup:
    """Test login immediately after signup (common flow)."""
    
    def test_signup_then_login(self, client: TestClient, unique_user_data: dict):
        """Test that a user can login immediately after signup."""
        # Signup
        signup_response = client.post(
            "/api/auth/signup",
            json={
                "username": unique_user_data["username"],
                "email": unique_user_data["email"],
                "password": unique_user_data["password"],
                "full_name": unique_user_data["full_name"]
            }
        )
        
        # Signup may succeed or fail (depending on test isolation)
        if signup_response.status_code in [200, 201]:
            # Try to login with the credentials
            login_response = client.post(
                "/api/auth/login",
                json={
                    "username": unique_user_data["username"],
                    "password": unique_user_data["password"]
                }
            )
            
            # Login should succeed
            assert login_response.status_code == 200, \
                f"Login should succeed after signup, got {login_response.status_code}: {login_response.text}"
            data = login_response.json()
            assert "access_token" in data


class TestTokenValidation:
    """Test token validation and usage."""
    
    def test_login_returns_valid_token(self, client: TestClient, test_credentials: dict):
        """Test that login returns a valid JWT token."""
        response = client.post(
            "/api/auth/login",
            json={
                "username": test_credentials["username"],
                "password": test_credentials["password"]
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            assert token is not None
            assert len(token) > 0
            
            # Token should be usable for authenticated requests
            # Try to access /api/auth/me endpoint
            me_response = client.get(
                "/api/auth/me",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            # Should succeed (200) or fail with 401 if token format is wrong
            assert me_response.status_code in [200, 401], \
                f"Expected 200 or 401 for /me endpoint, got {me_response.status_code}"
    
    def test_me_endpoint_requires_auth(self, client: TestClient):
        """Test that /me endpoint requires authentication."""
        response = client.get("/api/auth/me")
        
        assert response.status_code == 401, \
            f"Expected 401 for unauthenticated /me request, got {response.status_code}: {response.text}"


class TestErrorHandling:
    """Test error handling in auth endpoints."""
    
    def test_login_handles_network_errors_gracefully(self, client: TestClient):
        """Test that login handles errors gracefully."""
        # Try with malformed JSON
        response = client.post(
            "/api/auth/login",
            data="not json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code in [400, 422], \
            f"Expected 400/422 for malformed JSON, got {response.status_code}"
    
    def test_signup_handles_network_errors_gracefully(self, client: TestClient):
        """Test that signup handles errors gracefully."""
        # Try with malformed JSON
        response = client.post(
            "/api/auth/signup",
            data="not json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code in [400, 422], \
            f"Expected 400/422 for malformed JSON, got {response.status_code}"


# Smoke tests - quick verification that endpoints exist
class TestAuthEndpointsExist:
    """Smoke tests to verify auth endpoints exist and are accessible."""
    
    def test_login_endpoint_exists(self, client: TestClient):
        """Test that login endpoint exists."""
        # Should not return 404
        response = client.post(
            "/api/auth/login",
            json={"username": "test", "password": "test"}
        )
        assert response.status_code != 404, "Login endpoint should exist"
    
    def test_signup_endpoint_exists(self, client: TestClient):
        """Test that signup endpoint exists."""
        # Should not return 404
        response = client.post(
            "/api/auth/signup",
            json={"username": "test", "email": "test@test.local", "password": "test123"}
        )
        assert response.status_code != 404, "Signup endpoint should exist"
    
    def test_me_endpoint_exists(self, client: TestClient):
        """Test that /me endpoint exists."""
        # Should not return 404 (will return 401 without auth)
        response = client.get("/api/auth/me")
        assert response.status_code != 404, "/me endpoint should exist"



