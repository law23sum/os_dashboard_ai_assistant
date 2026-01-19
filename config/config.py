from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


def load_dotenv(path: Path | str = ".env", *, override: bool = False) -> None:
    """Lightweight .env loader to avoid external dependency."""

    env_path = Path(path)
    if not env_path.exists():
        return
    if env_path.name == "env.new":
        os.environ["OSDASH_ENV_NEW_LOADED"] = "1"

    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if override:
            os.environ[key] = value
        else:
            os.environ.setdefault(key, value)


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


def load_dotenv_chain() -> None:
    """Load environment variables from a prioritized list of env files."""
    for path in _iter_env_files():
        load_dotenv(path)


# Load environment variables
load_dotenv_chain()


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


def _env_bool(key: str, default: bool) -> bool:
    value = os.getenv(key)
    if value is None:
        return default
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "y", "on"}:
        return True
    if normalized in {"0", "false", "no", "n", "off"}:
        return False
    return default


def _fetch_db_key(meta_key: str) -> Optional[str]:
    """Try to fetch a key from the database."""
    if os.getenv("PYTEST_CURRENT_TEST") or "pytest" in sys.modules:
        return None
    last_error: Optional[Exception] = None
    try:
        # Delayed import to avoid circular dependencies and partial init states.
        import importlib

        module_names = ("assistant_hub_gui.assistant_hub.db", "assistant_hub.db")
        for module_name in module_names:
            try:
                module = sys.modules.get(module_name)
                if module is not None:
                    spec = getattr(module, "__spec__", None)
                    if getattr(spec, "_initializing", False):
                        continue
                if module is None:
                    module = importlib.import_module(module_name)

                init_db = getattr(module, "init_db", None)
                get_meta = getattr(module, "get_meta", None)
                if not callable(init_db) or not callable(get_meta):
                    continue
                # Use existing DB path if possible
                conn = init_db(DB_PATH)
                try:
                    return get_meta(conn, meta_key)
                finally:
                    try:
                        conn.close()
                    except Exception:
                        pass
            except Exception as exc:
                last_error = exc
                continue
    except Exception as exc:
        last_error = exc

    if last_error:
        error_text = str(last_error).lower()
        if os.getenv("ASSISTANT_HUB_CONFIG_DEBUG") and "partially initialized" not in error_text:
            print(f"DB Fetch Error: {last_error}")
    return None


default_data_dir = _path_from_env("ASSISTANT_HUB_DATA_DIR", _DEFAULT_DATA_DIR)
DATA_DIR = default_data_dir
DB_PATH = _path_from_env(
    "ASSISTANT_HUB_DB",
    PROJECT_ROOT / "assistant_hub_gui" / "assistant_hub" / "assistant_hub.db",
)
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

    # Anthropic Configuration
    anthropic_api_key: Optional[str] = field(default=None)
    anthropic_model: str = field(default="claude-3-opus-20240229")

    # Google Gemini Configuration
    google_api_key: Optional[str] = field(default=None)
    google_model: str = field(default="gemini-1.5-pro-latest")

    # xAI (Grok) Configuration
    xai_api_key: Optional[str] = field(default=None)
    xai_model: str = field(default="grok-1")

    # Cohere Configuration
    cohere_api_key: Optional[str] = field(default=None)

    # DeepSeek Configuration
    deepseek_api_key: Optional[str] = field(default=None)

    # Groq Configuration
    groq_api_key: Optional[str] = field(default=None)
    groq_model: str = field(default="llama3-70b-8192")

    # Perplexity Configuration
    perplexity_api_key: Optional[str] = field(default=None)

    # Mistral Configuration
    mistral_api_key: Optional[str] = field(default=None)

    # Together AI Configuration
    together_api_key: Optional[str] = field(default=None)

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
    app_name: str = field(default="AI OS")
    log_level: str = field(default="INFO")
    cache_ttl: int = field(default=3600)

    def __post_init__(self) -> None:
        # Populate from environment where present, fallback to DB
        self.openai_api_key = _env("OPENAI_API_KEY", self.openai_api_key) or _fetch_db_key("openai.api_key")
        self.openai_organization = _env("OPENAI_ORGANIZATION", self.openai_organization)
        self.openai_model = _env("OPENAI_MODEL", self.openai_model)

        self.anthropic_api_key = _env("ANTHROPIC_API_KEY", self.anthropic_api_key) or _fetch_db_key("anthropic.api_key")
        self.anthropic_model = _env("ANTHROPIC_MODEL", self.anthropic_model)

        self.google_api_key = _env("GOOGLE_API_KEY", self.google_api_key) or _fetch_db_key("google.api_key")
        self.google_model = _env("GOOGLE_MODEL", self.google_model)

        self.xai_api_key = _env("XAI_API_KEY", self.xai_api_key) or _fetch_db_key("xai.api_key")
        self.xai_model = _env("XAI_MODEL", self.xai_model)

        self.cohere_api_key = _env("COHERE_API_KEY", self.cohere_api_key) or _fetch_db_key("cohere.api_key")
        self.deepseek_api_key = _env("DEEPSEEK_API_KEY", self.deepseek_api_key) or _fetch_db_key("deepseek.api_key")
        self.groq_api_key = _env("GROQ_API_KEY", self.groq_api_key) or _fetch_db_key("groq.api_key")
        self.perplexity_api_key = _env("PERPLEXITY_API_KEY", self.perplexity_api_key) or _fetch_db_key("perplexity.api_key")
        self.mistral_api_key = _env("MISTRAL_API_KEY", self.mistral_api_key) or _fetch_db_key("mistral.api_key")
        self.together_api_key = _env("TOGETHER_API_KEY", self.together_api_key) or _fetch_db_key("together.api_key")

        self.microsoft_client_id = _env("MICROSOFT_CLIENT_ID", self.microsoft_client_id) or _fetch_db_key("azure.client_id")
        self.microsoft_client_secret = _env("MICROSOFT_CLIENT_SECRET", self.microsoft_client_secret) or _fetch_db_key("azure.client_secret")
        self.microsoft_tenant_id = _env("MICROSOFT_TENANT_ID", self.microsoft_tenant_id) or _fetch_db_key("azure.tenant_id")
        self.microsoft_redirect_uri = _env("MICROSOFT_REDIRECT_URI", self.microsoft_redirect_uri)

        self.google_credentials_file = _env("GOOGLE_CREDENTIALS_FILE", self.google_credentials_file)
        self.google_token_file = _env("GOOGLE_TOKEN_FILE", self.google_token_file)

        self.github_token = _env("GITHUB_TOKEN", self.github_token) or _fetch_db_key("github.token")
        self.github_username = _env("GITHUB_USERNAME", self.github_username)

        self.adobe_client_id = _env("ADOBE_CLIENT_ID", self.adobe_client_id) or _fetch_db_key("adobe.client_id")
        self.adobe_client_secret = _env("ADOBE_CLIENT_SECRET", self.adobe_client_secret) or _fetch_db_key("adobe.client_secret")
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


_api_config: Optional[APISettings] = None


def _get_api_config() -> APISettings:
    global _api_config
    if _api_config is None:
        _api_config = _build_api_config()
    return _api_config


def get_api_config() -> APISettings:
    """Get the global API configuration instance"""
    return _get_api_config()


def validate_api_config() -> dict[str, bool]:
    """Validate that required API credentials are present"""
    api_config = _get_api_config()
    validation_results = {
        "openai": bool(api_config.openai_api_key),
        "anthropic": bool(api_config.anthropic_api_key),
        "google_ai": bool(api_config.google_api_key),
        "xai": bool(api_config.xai_api_key),
        "cohere": bool(api_config.cohere_api_key),
        "deepseek": bool(api_config.deepseek_api_key),
        "groq": bool(api_config.groq_api_key),
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


@dataclass
class AuditSettings:
    """Configuration for audit log segmentation and retention."""

    storage_path: str = field(default="audit_data")
    segment_time_window_minutes: int = field(default=5)
    segment_time_format: str = field(default="%Y%m%d%H%M")
    segment_max_events: int = field(default=5000)
    retention_hot_days: int = field(default=30)
    retention_archive_days: int = field(default=395)
    retention_backup_years: int = field(default=7)
    retention_cloud_years: int = field(default=7)
    signing_key: Optional[str] = field(default=None)
    remote_archive_path: Optional[str] = field(default=None)
    hardware_backup_path: Optional[str] = field(default=None)
    cloud_backup_path: Optional[str] = field(default=None)
    maintenance_enabled: bool = field(default=True)
    maintenance_retention_apply: bool = field(default=False)
    maintenance_retention_interval_hours: int = field(default=24)
    maintenance_compact_interval_hours: int = field(default=24)
    maintenance_parquet_enabled: bool = field(default=False)
    maintenance_parquet_interval_hours: int = field(default=168)
    maintenance_parquet_range_days: int = field(default=1)
    maintenance_tenant_id: Optional[str] = field(default=None)

    def __post_init__(self) -> None:
        self.storage_path = _env("AUDIT_STORAGE_PATH", self.storage_path) or self.storage_path
        self.segment_time_window_minutes = _env_int(
            "AUDIT_SEGMENT_WINDOW_MINUTES", self.segment_time_window_minutes
        )
        self.segment_time_format = _env(
            "AUDIT_SEGMENT_TIME_FORMAT", self.segment_time_format
        ) or self.segment_time_format
        self.segment_max_events = _env_int("AUDIT_SEGMENT_MAX_EVENTS", self.segment_max_events)
        self.retention_hot_days = _env_int("AUDIT_RETENTION_HOT_DAYS", self.retention_hot_days)
        self.retention_archive_days = _env_int(
            "AUDIT_RETENTION_ARCHIVE_DAYS", self.retention_archive_days
        )
        self.retention_backup_years = _env_int(
            "AUDIT_RETENTION_BACKUP_YEARS", self.retention_backup_years
        )
        self.retention_cloud_years = _env_int(
            "AUDIT_RETENTION_CLOUD_YEARS", self.retention_cloud_years
        )
        self.signing_key = _env("AUDIT_SIGNING_KEY", self.signing_key)
        self.remote_archive_path = _env("AUDIT_TIER_REMOTE_ARCHIVE", self.remote_archive_path)
        self.hardware_backup_path = _env("AUDIT_TIER_HARDWARE_BACKUP", self.hardware_backup_path)
        self.cloud_backup_path = _env("AUDIT_TIER_CLOUD_BACKUP", self.cloud_backup_path)
        self.maintenance_enabled = _env_bool(
            "AUDIT_MAINTENANCE_ENABLED", self.maintenance_enabled
        )
        self.maintenance_retention_apply = _env_bool(
            "AUDIT_RETENTION_APPLY", self.maintenance_retention_apply
        )
        self.maintenance_retention_interval_hours = _env_int(
            "AUDIT_RETENTION_INTERVAL_HOURS", self.maintenance_retention_interval_hours
        )
        self.maintenance_compact_interval_hours = _env_int(
            "AUDIT_COMPACTION_INTERVAL_HOURS", self.maintenance_compact_interval_hours
        )
        self.maintenance_parquet_enabled = _env_bool(
            "AUDIT_PARQUET_EXPORT_ENABLED", self.maintenance_parquet_enabled
        )
        self.maintenance_parquet_interval_hours = _env_int(
            "AUDIT_PARQUET_EXPORT_INTERVAL_HOURS",
            self.maintenance_parquet_interval_hours,
        )
        self.maintenance_parquet_range_days = _env_int(
            "AUDIT_PARQUET_EXPORT_RANGE_DAYS",
            self.maintenance_parquet_range_days,
        )
        self.maintenance_tenant_id = _env(
            "AUDIT_MAINTENANCE_TENANT_ID", self.maintenance_tenant_id
        )


def _build_audit_config() -> AuditSettings:
    ensure_data_directories()
    return AuditSettings()


_audit_config: Optional[AuditSettings] = None


def get_audit_config() -> AuditSettings:
    """Get the global audit configuration instance."""
    global _audit_config
    if _audit_config is None:
        _audit_config = _build_audit_config()
    return _audit_config
