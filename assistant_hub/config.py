#!/usr/bin/env python3
"""Central configuration helpers for Assistant Hub."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable, Optional
from pydantic import Field

try:  # Prefer the dedicated package when available (Pydantic v2+).
    from pydantic_settings import BaseSettings  # type: ignore
except Exception:  # pragma: no cover - fall back for older environments
    try:
        from pydantic import BaseSettings  # type: ignore
    except Exception:  # pragma: no cover - final fallback to BaseModel semantics
        from pydantic import BaseModel

        class BaseSettings(BaseModel):  # type: ignore
            """Minimal shim so legacy configs still import without pydantic-settings."""

            class Config:
                env_file = ".env"
                case_sensitive = False
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

PACKAGE_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_ROOT.parent
_DEFAULT_DATA_DIR = Path(os.getenv("ASSISTANT_HUB_HOME", PROJECT_ROOT)).expanduser()


def _path_from_env(key: str, fallback: Path) -> Path:
    value = os.getenv(key)
    return Path(value).expanduser() if value else fallback


default_data_dir = _path_from_env("ASSISTANT_HUB_DATA_DIR", _DEFAULT_DATA_DIR)
DATA_DIR = default_data_dir
DB_PATH = _path_from_env("ASSISTANT_HUB_DB", DATA_DIR / "assistant_hub.db")
ATTACHMENTS_DIR = _path_from_env(
    "ASSISTANT_HUB_ATTACHMENTS_DIR", DATA_DIR / "attachments"
)
INTEGRATIONS_DIR = _path_from_env(
    "ASSISTANT_HUB_INTEGRATIONS_DIR", DATA_DIR / "integrations"
)
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


class APISettings(BaseSettings):
    """Configuration class for all API credentials and settings"""

    # OpenAI/ChatGPT Configuration
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    openai_organization: Optional[str] = Field(default=None, env="OPENAI_ORGANIZATION")
    openai_model: str = Field(default="gpt-5-mini", env="OPENAI_MODEL")

    # Microsoft Graph API Configuration
    microsoft_client_id: Optional[str] = Field(default=None, env="MICROSOFT_CLIENT_ID")
    microsoft_client_secret: Optional[str] = Field(
        default=None, env="MICROSOFT_CLIENT_SECRET"
    )
    microsoft_tenant_id: Optional[str] = Field(default=None, env="MICROSOFT_TENANT_ID")
    microsoft_redirect_uri: str = Field(
        default="http://localhost:8000/auth/callback", env="MICROSOFT_REDIRECT_URI"
    )

    # Google APIs Configuration
    google_credentials_file: Optional[str] = Field(
        default="credentials.json", env="GOOGLE_CREDENTIALS_FILE"
    )
    google_token_file: str = Field(default="token.json", env="GOOGLE_TOKEN_FILE")
    google_scopes: list = Field(
        default=[
            "https://www.googleapis.com/auth/gmail.readonly",
            "https://www.googleapis.com/auth/gmail.send",
            "https://www.googleapis.com/auth/calendar",
        ]
    )

    # GitHub Configuration
    github_token: Optional[str] = Field(default=None, env="GITHUB_TOKEN")
    github_username: Optional[str] = Field(default=None, env="GITHUB_USERNAME")

    # Adobe Configuration
    adobe_client_id: Optional[str] = Field(default=None, env="ADOBE_CLIENT_ID")
    adobe_client_secret: Optional[str] = Field(default=None, env="ADOBE_CLIENT_SECRET")
    adobe_organization_id: Optional[str] = Field(
        default=None, env="ADOBE_ORGANIZATION_ID"
    )
    adobe_account_id: Optional[str] = Field(default=None, env="ADOBE_ACCOUNT_ID")
    adobe_private_key_file: Optional[str] = Field(
        default="private.key", env="ADOBE_PRIVATE_KEY_FILE"
    )

    # Apple Calendar (CalDAV) Configuration
    caldav_url: Optional[str] = Field(default=None, env="CALDAV_URL")
    caldav_username: Optional[str] = Field(default=None, env="CALDAV_USERNAME")
    caldav_password: Optional[str] = Field(default=None, env="CALDAV_PASSWORD")

    # Application Settings
    app_name: str = Field(default="OS Dashboard AI Assistant")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    cache_ttl: int = Field(default=3600, env="CACHE_TTL")  # 1 hour

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"


# Global configuration instances
api_config = APISettings()


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
        "google": bool(
            os.path.exists(api_config.google_credentials_file or "credentials.json")
        ),
        "github": bool(api_config.github_token),
        "adobe": bool(api_config.adobe_client_id and api_config.adobe_client_secret),
        "caldav": bool(
            api_config.caldav_url
            and api_config.caldav_username
            and api_config.caldav_password
        ),
    }
    return validation_results
