from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


def load_dotenv(path: Path | str = ".env") -> None:
    """Lightweight .env loader to avoid external dependency."""

    env_path = Path(path)
    if not env_path.exists():
        return

    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


# Load environment variables
load_dotenv()

PACKAGE_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_ROOT.parent
_DEFAULT_DATA_DIR = Path(os.getenv("ASSISTANT_HUB_HOME", PROJECT_ROOT)).expanduser()


def _path_from_env(key: str, fallback: Path) -> Path:
    value = os.getenv(key)
    return Path(value).expanduser() if value else fallback


def _env(key: str, default: Optional[str] = None) -> Optional[str]:
    return os.getenv(key, default)


def _env_int(key: str, default: int) -> int:
    try:
        return int(os.getenv(key, default))
    except (TypeError, ValueError):
        return default


default_data_dir = _path_from_env("ASSISTANT_HUB_DATA_DIR", _DEFAULT_DATA_DIR)
DATA_DIR = default_data_dir
DB_PATH = _path_from_env("ASSISTANT_HUB_DB", DATA_DIR / "assistant_hub.db")
ATTACHMENTS_DIR = _path_from_env("ASSISTANT_HUB_ATTACHMENTS_DIR", DATA_DIR / "attachments")
INTEGRATIONS_DIR = _path_from_env("ASSISTANT_HUB_INTEGRATIONS_DIR", DATA_DIR / "integrations")
FILE_CACHE_DIR = _path_from_env("ASSISTANT_HUB_FILE_CACHE_DIR", DATA_DIR / "file_cache")


def ensure_data_directories() -> None:
    """Create the runtime data directories if they are missing."""
    for path in (DATA_DIR, ATTACHMENTS_DIR, INTEGRATIONS_DIR, FILE_CACHE_DIR):
        path.mkdir(parents=True, exist_ok=True)


def get_integration_path(*parts: str) -> Path:
    """Return a path under the integrations directory."""
    ensure_data_directories()
    return INTEGRATIONS_DIR.joinpath(*parts)


def get_attachment_path(*parts: str) -> Path:
    """Return a path under the attachments directory."""
    ensure_data_directories()
    return ATTACHMENTS_DIR.joinpath(*parts)


@dataclass
class APISettings:
    """Configuration class for all API credentials and settings."""

    # OpenAI/ChatGPT Configuration
    openai_api_key: Optional[str] = field(default=None)
    openai_organization: Optional[str] = field(default=None)
    openai_model: str = field(default="gpt-5-mini")

    # Microsoft Graph API Configuration
    microsoft_client_id: Optional[str] = field(default=None)
    microsoft_client_secret: Optional[str] = field(default=None)
    microsoft_tenant_id: Optional[str] = field(default=None)
    microsoft_redirect_uri: str = field(default="http://localhost:8000/auth/callback")

    # Google APIs Configuration
    google_credentials_file: Optional[str] = field(default="credentials.json")
    google_token_file: str = field(default="token.json")
    google_scopes: list = field(
        default_factory=lambda: [
            "https://www.googleapis.com/auth/gmail.readonly",
            "https://www.googleapis.com/auth/gmail.send",
            "https://www.googleapis.com/auth/calendar",
        ]
    )

    # GitHub Configuration
    github_token: Optional[str] = field(default=None)
    github_username: Optional[str] = field(default=None)

    # Adobe Configuration
    adobe_client_id: Optional[str] = field(default=None)
    adobe_client_secret: Optional[str] = field(default=None)
    adobe_organization_id: Optional[str] = field(default=None)
    adobe_account_id: Optional[str] = field(default=None)
    adobe_private_key_file: Optional[str] = field(default="private.key")

    # Apple Calendar (CalDAV) Configuration
    caldav_url: Optional[str] = field(default=None)
    caldav_username: Optional[str] = field(default=None)
    caldav_password: Optional[str] = field(default=None)

    # Application Settings
    app_name: str = field(default="OS Dashboard AI Assistant")
    log_level: str = field(default="INFO")
    cache_ttl: int = field(default=3600)

    def __post_init__(self) -> None:
        # Populate from environment where present
        self.openai_api_key = _env("OPENAI_API_KEY", self.openai_api_key)
        self.openai_organization = _env("OPENAI_ORGANIZATION", self.openai_organization)
        self.openai_model = _env("OPENAI_MODEL", self.openai_model)

        self.microsoft_client_id = _env("MICROSOFT_CLIENT_ID", self.microsoft_client_id)
        self.microsoft_client_secret = _env("MICROSOFT_CLIENT_SECRET", self.microsoft_client_secret)
        self.microsoft_tenant_id = _env("MICROSOFT_TENANT_ID", self.microsoft_tenant_id)
        self.microsoft_redirect_uri = _env("MICROSOFT_REDIRECT_URI", self.microsoft_redirect_uri)

        self.google_credentials_file = _env("GOOGLE_CREDENTIALS_FILE", self.google_credentials_file)
        self.google_token_file = _env("GOOGLE_TOKEN_FILE", self.google_token_file)

        self.github_token = _env("GITHUB_TOKEN", self.github_token)
        self.github_username = _env("GITHUB_USERNAME", self.github_username)

        self.adobe_client_id = _env("ADOBE_CLIENT_ID", self.adobe_client_id)
        self.adobe_client_secret = _env("ADOBE_CLIENT_SECRET", self.adobe_client_secret)
        self.adobe_organization_id = _env("ADOBE_ORGANIZATION_ID", self.adobe_organization_id)
        self.adobe_account_id = _env("ADOBE_ACCOUNT_ID", self.adobe_account_id)
        self.adobe_private_key_file = _env("ADOBE_PRIVATE_KEY_FILE", self.adobe_private_key_file)

        self.caldav_url = _env("CALDAV_URL", self.caldav_url)
        self.caldav_username = _env("CALDAV_USERNAME", self.caldav_username)
        self.caldav_password = _env("CALDAV_PASSWORD", self.caldav_password)

        self.app_name = _env("APP_NAME", self.app_name)
        self.log_level = _env("LOG_LEVEL", self.log_level or "INFO")
        self.cache_ttl = _env_int("CACHE_TTL", self.cache_ttl)


def _build_api_config() -> APISettings:
    ensure_data_directories()
    return APISettings()


# Global configuration instances
api_config = _build_api_config()


def get_api_config() -> APISettings:
    """Get the global API configuration instance"""
    return api_config


def validate_api_config() -> dict[str, bool]:
    """Validate that required API credentials are present"""
    validation_results = {
        "openai": bool(api_config.openai_api_key),
        "microsoft": bool(
            api_config.microsoft_client_id
            and api_config.microsoft_client_secret
            and api_config.microsoft_tenant_id
        ),
        "google": bool(os.path.exists(api_config.google_credentials_file or "credentials.json")),
        "github": bool(api_config.github_token),
        "adobe": bool(api_config.adobe_client_id and api_config.adobe_client_secret),
        "caldav": bool(api_config.caldav_url and api_config.caldav_username and api_config.caldav_password),
    }
    return validation_results
