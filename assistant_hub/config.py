#!/usr/bin/env python3
"""Central configuration helpers for Assistant Hub."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Iterable, Optional
from pydantic import Field

try:  # Prefer the dedicated package when available (Pydantic v2+).
    from pydantic_settings import BaseSettings, SettingsConfigDict  # type: ignore
    _SETTINGS_BACKEND = "pydantic_settings"
except Exception:  # pragma: no cover - fall back for older environments
    try:
        from pydantic import BaseSettings  # type: ignore
        SettingsConfigDict = None
        _SETTINGS_BACKEND = "pydantic"
    except Exception:  # pragma: no cover - final fallback to BaseModel semantics
        from pydantic import BaseModel

        SettingsConfigDict = None
        _SETTINGS_BACKEND = "base_model"

        class BaseSettings(BaseModel):  # type: ignore
            """Minimal shim so legacy configs still import without pydantic-settings."""

            class Config:
                env_file = ".env"
                case_sensitive = False
from dotenv import load_dotenv


def _env_field(*, default: Any, env: str):
    if _SETTINGS_BACKEND == "pydantic_settings":
        return Field(default=default, validation_alias=env)
    if _SETTINGS_BACKEND == "pydantic":
        return Field(default=default, env=env)
    return Field(default=default)


def _iter_env_files() -> list[Path]:
    candidates: list[Path] = []
    explicit = (
        os.getenv("ASSISTANT_HUB_ENV_FILE")
        or os.getenv("OSDASH_ENV_FILE")
        or os.getenv("ENV_FILE")
    )
    if explicit:
        candidates.append(Path(explicit))
    env_name = os.getenv("ENVIRONMENT") or os.getenv("ENV")
    if env_name:
        candidates.append(Path(f".env.{env_name}"))
        candidates.append(Path(f"env.{env_name}.example"))
    candidates.extend(
        [
            Path("env.new"),
            Path(".env"),
            Path(".env.local"),
            Path("env.dev.example"),
        ]
    )
    repo_root = Path(__file__).resolve().parent.parent
    seen: set[Path] = set()
    ordered: list[Path] = []
    for path in candidates:
        path = path.expanduser()
        if path not in seen:
            seen.add(path)
            ordered.append(path)
        if not path.is_absolute():
            repo_candidate = repo_root / path
            if repo_candidate not in seen:
                seen.add(repo_candidate)
                ordered.append(repo_candidate)
    return ordered


def _load_env_chain() -> None:
    for path in _iter_env_files():
        if path.exists() and path.name == "env.new":
            os.environ["OSDASH_ENV_NEW_LOADED"] = "1"
        load_dotenv(path, override=False)


# Load environment variables
_load_env_chain()


def _hydrate_openai_key() -> None:
    prefer_codex = os.getenv("OSDASH_ENV_NEW_LOADED") == "1"
    current = os.getenv("OPENAI_API_KEY")
    codex1 = os.getenv("OPENAI_API_KEY_CODEX1")
    codex2 = os.getenv("OPENAI_API_KEY_CODEX2o")
    if current and (current == codex1 or current == codex2):
        return
    if current and not prefer_codex:
        return
    for key in ("OPENAI_API_KEY_CODEX1", "OPENAI_API_KEY_CODEX2o"):
        value = os.getenv(key)
        if value:
            os.environ["OPENAI_API_KEY"] = value
            return


_hydrate_openai_key()


def _hydrate_model_defaults() -> None:
    mapping = {
        "OPENAI_MODEL": "OPENAI_MODELS",
        "ANTHROPIC_MODEL": "ANTHROPIC_MODELS",
        "GOOGLE_MODEL": "GOOGLE_MODELS",
        "XAI_MODEL": "XAI_MODELS",
        "GROQ_MODEL": "GROQ_MODELS",
        "COHERE_MODEL": "COHERE_MODELS",
        "DEEPSEEK_MODEL": "DEEPSEEK_MODELS",
    }
    for target, source in mapping.items():
        if os.getenv(target):
            continue
        raw = os.getenv(source)
        if not raw:
            continue
        first = raw.split(",", 1)[0].strip()
        if first:
            os.environ[target] = first


_hydrate_model_defaults()

PACKAGE_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_ROOT.parent
# Default to user data dir so runtime artifacts are not written inside the repo.
_DEFAULT_DATA_DIR = Path(os.getenv("ASSISTANT_HUB_HOME", "~/.osdash/data")).expanduser()


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
    # Ensure DB parent exists even if DB_PATH points outside DATA_DIR.
    DB_PATH.expanduser().parent.mkdir(parents=True, exist_ok=True)


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
    openai_api_key: Optional[str] = _env_field(default=None, env="OPENAI_API_KEY")
    openai_organization: Optional[str] = _env_field(default=None, env="OPENAI_ORGANIZATION")
    openai_model: str = _env_field(default="gpt-5-mini", env="OPENAI_MODEL")

    # Microsoft Graph API Configuration
    microsoft_client_id: Optional[str] = _env_field(default=None, env="MICROSOFT_CLIENT_ID")
    microsoft_client_secret: Optional[str] = _env_field(
        default=None, env="MICROSOFT_CLIENT_SECRET"
    )
    microsoft_tenant_id: Optional[str] = _env_field(default=None, env="MICROSOFT_TENANT_ID")
    microsoft_redirect_uri: str = _env_field(
        default="http://localhost:8000/auth/callback", env="MICROSOFT_REDIRECT_URI"
    )

    # Google APIs Configuration
    google_credentials_file: Optional[str] = _env_field(
        default="credentials.json", env="GOOGLE_CREDENTIALS_FILE"
    )
    google_token_file: str = _env_field(default="token.json", env="GOOGLE_TOKEN_FILE")
    google_scopes: list = Field(
        default=[
            "https://www.googleapis.com/auth/gmail.readonly",
            "https://www.googleapis.com/auth/gmail.send",
            "https://www.googleapis.com/auth/calendar",
        ]
    )

    # GitHub Configuration
    github_token: Optional[str] = _env_field(default=None, env="GITHUB_TOKEN")
    github_username: Optional[str] = _env_field(default=None, env="GITHUB_USERNAME")

    # Adobe Configuration
    adobe_client_id: Optional[str] = _env_field(default=None, env="ADOBE_CLIENT_ID")
    adobe_client_secret: Optional[str] = _env_field(default=None, env="ADOBE_CLIENT_SECRET")
    adobe_organization_id: Optional[str] = _env_field(
        default=None, env="ADOBE_ORGANIZATION_ID"
    )
    adobe_account_id: Optional[str] = _env_field(default=None, env="ADOBE_ACCOUNT_ID")
    adobe_private_key_file: Optional[str] = _env_field(
        default="private.key", env="ADOBE_PRIVATE_KEY_FILE"
    )

    # Apple Calendar (CalDAV) Configuration
    caldav_url: Optional[str] = _env_field(default=None, env="CALDAV_URL")
    caldav_username: Optional[str] = _env_field(default=None, env="CALDAV_USERNAME")
    caldav_password: Optional[str] = _env_field(default=None, env="CALDAV_PASSWORD")

    # Application Settings
    app_name: str = Field(default="AI OS")
    log_level: str = _env_field(default="INFO", env="LOG_LEVEL")
    cache_ttl: int = _env_field(default=3600, env="CACHE_TTL")  # 1 hour

    if SettingsConfigDict is not None:
        model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="allow")
    else:
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
