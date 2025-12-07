"""Configuration package initializer.

Provides convenient accessors for API settings and paths defined in
``config.py`` so modules can simply ``import config``.
"""

from .config import (
    APISettings,
    ATTACHMENTS_DIR,
    DATA_DIR,
    DB_PATH,
    FILE_CACHE_DIR,
    INTEGRATIONS_DIR,
    ensure_data_directories,
    get_api_config,
    get_attachment_path,
    get_integration_path,
    validate_api_config,
)

__all__ = [
    "APISettings",
    "ATTACHMENTS_DIR",
    "DATA_DIR",
    "DB_PATH",
    "FILE_CACHE_DIR",
    "INTEGRATIONS_DIR",
    "ensure_data_directories",
    "get_api_config",
    "get_attachment_path",
    "get_integration_path",
    "validate_api_config",
]
