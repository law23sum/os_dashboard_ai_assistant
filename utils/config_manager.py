"""Enhanced configuration management with validation and type safety.

This module provides a centralized, type-safe configuration management system
that validates settings, provides defaults, and supports environment-based
configuration.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

try:
    from pydantic import BaseSettings, Field, validator
except ImportError:
    # Fallback for older pydantic versions
    BaseSettings = None  # type: ignore
    Field = None  # type: ignore
    validator = None  # type: ignore

from dotenv import load_dotenv

from utils.exceptions import ConfigurationError


# Load environment variables
load_dotenv()


@dataclass
class PathConfig:
    """Configuration for file system paths."""
    
    repo_root: Path = field(default_factory=lambda: Path(__file__).resolve().parent.parent)
    data_dir: Path = field(default_factory=lambda: Path.home() / ".osdash" / "data")
    logs_dir: Path = field(default_factory=lambda: Path.home() / ".osdash" / "logs")
    cache_dir: Path = field(default_factory=lambda: Path.home() / ".osdash" / "cache")
    attachments_dir: Path = field(default_factory=lambda: Path.home() / ".osdash" / "attachments")
    integrations_dir: Path = field(default_factory=lambda: Path.home() / ".osdash" / "integrations")
    
    def __post_init__(self) -> None:
        """Ensure all directories exist."""
        for path in [
            self.data_dir,
            self.logs_dir,
            self.cache_dir,
            self.attachments_dir,
            self.integrations_dir,
        ]:
            path.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def from_env(cls) -> PathConfig:
        """Create PathConfig from environment variables."""
        repo_root = Path(os.getenv("OSDASH_REPO_ROOT", Path(__file__).resolve().parent.parent))
        base_dir = Path(os.getenv("OSDASH_HOME", Path.home() / ".osdash"))
        
        return cls(
            repo_root=repo_root,
            data_dir=Path(os.getenv("OSDASH_DATA_DIR", base_dir / "data")),
            logs_dir=Path(os.getenv("OSDASH_LOGS_DIR", base_dir / "logs")),
            cache_dir=Path(os.getenv("OSDASH_CACHE_DIR", base_dir / "cache")),
            attachments_dir=Path(os.getenv("OSDASH_ATTACHMENTS_DIR", base_dir / "attachments")),
            integrations_dir=Path(os.getenv("OSDASH_INTEGRATIONS_DIR", base_dir / "integrations")),
        )


@dataclass
class APIConfig:
    """Configuration for API endpoints and services."""
    
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False
    ssl_enabled: bool = False
    ssl_cert_file: Optional[Path] = None
    ssl_key_file: Optional[Path] = None
    
    @classmethod
    def from_env(cls) -> APIConfig:
        """Create APIConfig from environment variables."""
        cert_dir = Path(os.getenv("OSDASH_CERTS_DIR", "certs"))
        cert_file = cert_dir / "cert.pem"
        key_file = cert_dir / "key.pem"
        ssl_enabled = cert_file.exists() and key_file.exists()
        
        return cls(
            host=os.getenv("OSDASH_API_HOST", "0.0.0.0"),
            port=int(os.getenv("OSDASH_API_PORT", "8000")),
            reload=os.getenv("OSDASH_API_RELOAD", "false").lower() == "true",
            ssl_enabled=ssl_enabled,
            ssl_cert_file=cert_file if ssl_enabled else None,
            ssl_key_file=key_file if ssl_enabled else None,
        )
    
    def validate(self) -> None:
        """Validate API configuration."""
        if not (1 <= self.port <= 65535):
            raise ConfigurationError(
                f"Invalid port number: {self.port}",
                error_code="INVALID_PORT",
                context={"port": self.port},
            )
        
        if self.ssl_enabled:
            if not self.ssl_cert_file or not self.ssl_cert_file.exists():
                raise ConfigurationError(
                    "SSL enabled but certificate file not found",
                    error_code="MISSING_SSL_CERT",
                    context={"cert_file": str(self.ssl_cert_file)},
                )
            if not self.ssl_key_file or not self.ssl_key_file.exists():
                raise ConfigurationError(
                    "SSL enabled but key file not found",
                    error_code="MISSING_SSL_KEY",
                    context={"key_file": str(self.ssl_key_file)},
                )


@dataclass
class OrchestratorConfig:
    """Configuration for the master orchestrator."""
    
    root: Path = field(default_factory=lambda: Path.home() / "Projects")
    max_depth: int = 4
    watch_todos: bool = True
    todo_check_interval: int = 300  # seconds
    enable_dashboard: bool = True
    health_port: int = 9000
    auto_spawn_codex: bool = True
    max_repos: Optional[int] = None
    
    @classmethod
    def from_env(cls) -> OrchestratorConfig:
        """Create OrchestratorConfig from environment variables."""
        root = Path(os.getenv("OSDASH_WORKSPACE_ROOT", str(Path.home() / "Projects")))
        
        return cls(
            root=root,
            max_depth=int(os.getenv("OSDASH_MAX_DEPTH", "4")),
            watch_todos=os.getenv("OSDASH_WATCH_TODOS", "true").lower() == "true",
            todo_check_interval=int(os.getenv("OSDASH_TODO_CHECK_INTERVAL", "300")),
            enable_dashboard=os.getenv("OSDASH_ENABLE_DASHBOARD", "true").lower() == "true",
            health_port=int(os.getenv("OSDASH_HEALTH_PORT", "9000")),
            auto_spawn_codex=os.getenv("OSDASH_AUTO_SPAWN_CODEX", "true").lower() == "true",
            max_repos=int(os.getenv("OSDASH_MAX_REPOS")) if os.getenv("OSDASH_MAX_REPOS") else None,
        )
    
    def validate(self) -> None:
        """Validate orchestrator configuration."""
        if not self.root.exists():
            raise ConfigurationError(
                f"Workspace root does not exist: {self.root}",
                error_code="INVALID_WORKSPACE_ROOT",
                context={"root": str(self.root)},
            )
        
        if not (1 <= self.max_depth <= 20):
            raise ConfigurationError(
                f"Invalid max_depth: {self.max_depth} (must be 1-20)",
                error_code="INVALID_MAX_DEPTH",
                context={"max_depth": self.max_depth},
            )
        
        if not (1 <= self.todo_check_interval <= 3600):
            raise ConfigurationError(
                f"Invalid todo_check_interval: {self.todo_check_interval} (must be 1-3600)",
                error_code="INVALID_TODO_INTERVAL",
                context={"interval": self.todo_check_interval},
            )


class AppConfig:
    """Application-wide configuration manager."""
    
    def __init__(self) -> None:
        """Initialize configuration from environment."""
        self.paths = PathConfig.from_env()
        self.api = APIConfig.from_env()
        self.orchestrator = OrchestratorConfig.from_env()
        self._validate_all()
    
    def _validate_all(self) -> None:
        """Validate all configuration sections."""
        try:
            self.api.validate()
            self.orchestrator.validate()
        except ConfigurationError:
            raise
        except Exception as e:
            raise ConfigurationError(
                "Configuration validation failed",
                error_code="VALIDATION_ERROR",
                cause=e,
            ) from e
    
    def reload(self) -> None:
        """Reload configuration from environment."""
        load_dotenv(override=True)
        self.paths = PathConfig.from_env()
        self.api = APIConfig.from_env()
        self.orchestrator = OrchestratorConfig.from_env()
        self._validate_all()
    
    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "paths": {
                "repo_root": str(self.paths.repo_root),
                "data_dir": str(self.paths.data_dir),
                "logs_dir": str(self.paths.logs_dir),
                "cache_dir": str(self.paths.cache_dir),
            },
            "api": {
                "host": self.api.host,
                "port": self.api.port,
                "ssl_enabled": self.api.ssl_enabled,
            },
            "orchestrator": {
                "root": str(self.orchestrator.root),
                "max_depth": self.orchestrator.max_depth,
                "watch_todos": self.orchestrator.watch_todos,
            },
        }


# Global configuration instance
_config: Optional[AppConfig] = None


def get_config() -> AppConfig:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = AppConfig()
    return _config


def reload_config() -> AppConfig:
    """Reload and return the global configuration."""
    global _config
    if _config is None:
        _config = AppConfig()
    else:
        _config.reload()
    return _config

