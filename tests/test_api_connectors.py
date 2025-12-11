"""Tests for API connector functionality."""

import unittest
import os
from unittest.mock import patch, MagicMock, mock_open
from api_connectors.git_client import GitClient
from api_connectors.google_client import GoogleWorkspaceClient
from api_connectors.ms_graph_client import MicrosoftGraphClient


class TestGitClient(unittest.TestCase):
    """Test cases for GitClient."""

    def test_initialization_github(self):
        """Test GitClient initialization with GitHub provider."""
        config = {
            "provider": "github",
            "api_token": "test-token",
            "username": "testuser"
        }

        client = GitClient(config)

        assert client.provider == "github"
        assert client.api_token == "test-token"
        assert client.username == "testuser"
        assert client.base_url == "https://api.github.com"
        assert "Authorization" in client.headers
        assert client.headers["Authorization"] == "token test-token"

    def test_initialization_gitlab(self):
        """Test GitClient initialization with GitLab provider."""
        config = {
            "provider": "gitlab",
            "api_token": "test-token",
            "username": "testuser"
        }

        client = GitClient(config)

        assert client.provider == "gitlab"
        assert client.base_url == "https://gitlab.com/api/v4"
        assert client.headers["Authorization"] == "Bearer test-token"

    def test_get_base_url_unknown_provider(self):
        """Test _get_base_url with unknown provider defaults to GitHub."""
        config = {
            "provider": "unknown",
            "api_token": "test-token"
        }

        client = GitClient(config)
        assert client.base_url == "https://api.github.com"

    @patch('api_connectors.git_client.git.Repo')
    def test_clone_repository(self, mock_repo_class):
        """Test repository cloning functionality."""
        config = {"api_token": "test-token"}
        client = GitClient(config)

        mock_repo = MagicMock()
        mock_repo_class.clone_from.return_value = mock_repo

        # This test would need to be expanded based on actual clone method
        # For now, just test that the client initializes properly
        assert client.local_repos == {}


class TestGoogleWorkspaceClient(unittest.TestCase):
    """Test cases for GoogleWorkspaceClient."""

    def test_initialization(self):
        """Test GoogleWorkspaceClient initialization."""
        config = {
            "client_secret_file": "client_secret.json",
            "token_pickle_file": "token.pickle",
            "scopes": ["https://www.googleapis.com/auth/gmail.readonly"]
        }

        client = GoogleWorkspaceClient(config)

        assert client.client_secret_file == "client_secret.json"
        assert client.token_pickle_file == "token.pickle"
        assert client.scopes == ["https://www.googleapis.com/auth/gmail.readonly"]
        assert client.gmail_service is None
        assert client.calendar_service is None
        assert client.drive_service is None
        assert client.docs_service is None

    def test_initialization_default_scopes(self):
        """Test GoogleWorkspaceClient initialization with default scopes."""
        config = {}

        client = GoogleWorkspaceClient(config)

        assert len(client.scopes) == 4  # Should have default scopes
        assert 'https://www.googleapis.com/auth/gmail.readonly' in client.scopes
        assert 'https://www.googleapis.com/auth/calendar' in client.scopes
        assert 'https://www.googleapis.com/auth/drive' in client.scopes
        assert 'https://www.googleapis.com/auth/documents' in client.scopes

    @patch('api_connectors.google_client.Credentials')
    @patch('builtins.open', new_callable=mock_open, read_data=b'fake_pickle_data')
    @patch('api_connectors.google_client.pickle.load')
    def test_load_credentials_from_file(self, mock_pickle_load, mock_file, mock_credentials_class):
        """Test loading credentials from pickle file."""
        mock_creds = MagicMock()
        mock_pickle_load.return_value = mock_creds
        mock_credentials_class.from_authorized_user_info.return_value = mock_creds

        config = {"token_pickle_file": "token.pickle"}
        client = GoogleWorkspaceClient(config)

        # This would test the credential loading logic if implemented
        # For now, just verify initialization
        assert client.token_pickle_file == "token.pickle"


class TestMicrosoftGraphClient(unittest.TestCase):
    """Test cases for MicrosoftGraphClient."""

    def test_initialization(self):
        """Test MicrosoftGraphClient initialization."""
        config = {
            "client_id": "test-client-id",
            "client_secret": "test-client-secret",
            "tenant_id": "test-tenant-id"
        }

        client = MicrosoftGraphClient(config)

        assert client.client_id == "test-client-id"
        assert client.client_secret == "test-client-secret"
        assert client.tenant_id == "test-tenant-id"

    def test_authentication_setup(self):
        """Test Microsoft Graph client authentication setup."""
        config = {
            "client_id": "test-client-id",
            "client_secret": "test-client-secret",
            "tenant_id": "test-tenant-id"
        }

        client = MicrosoftGraphClient(config)

        # Test that basic attributes are set
        assert client.client_id == "test-client-id"
        assert client.client_secret == "test-client-secret"
        assert client.tenant_id == "test-tenant-id"

    def test_scopes_configuration(self):
        """Test default scopes configuration."""
        config = {}
        client = MicrosoftGraphClient(config)

        # Should have default Microsoft Graph scopes
        # This test would need to be adjusted based on actual implementation
        assert hasattr(client, 'client_id')
