"""Utility modules for OS Dashboard AI Assistant.

This package provides common utilities including:
- Exception hierarchy
- Configuration management
- Enhanced logging
- Common helpers
"""

from utils.exceptions import (
    OSDashBaseException,
    ConfigurationError,
    DatabaseError,
    ProjectDiscoveryError,
    MonitorError,
    OrchestratorError,
    APIError,
    IntegrationError,
    AuthenticationError,
    ValidationError,
    ResourceNotFoundError,
    TimeoutError,
    NetworkError,
    FileSystemError,
    ProcessError,
)

from utils.config_manager import (
    AppConfig,
    APIConfig,
    OrchestratorConfig,
    PathConfig,
    get_config,
    reload_config,
)

from utils.logger import (
    LogContext,
    ContextLoggerAdapter,
    setup_logger,
    get_logger,
    log_exception,
    configure_logging,
    get_app_logger,
    request_id_ctx,
    correlation_id_ctx,
)

__all__ = [
    # Exceptions
    "OSDashBaseException",
    "ConfigurationError",
    "DatabaseError",
    "ProjectDiscoveryError",
    "MonitorError",
    "OrchestratorError",
    "APIError",
    "IntegrationError",
    "AuthenticationError",
    "ValidationError",
    "ResourceNotFoundError",
    "TimeoutError",
    "NetworkError",
    "FileSystemError",
    "ProcessError",
    # Configuration
    "AppConfig",
    "APIConfig",
    "OrchestratorConfig",
    "PathConfig",
    "get_config",
    "reload_config",
    # Logging
    "LogContext",
    "ContextLoggerAdapter",
    "setup_logger",
    "get_logger",
    "log_exception",
    "configure_logging",
    "get_app_logger",
    "request_id_ctx",
    "correlation_id_ctx",
]
