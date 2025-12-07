#!/usr/bin/env python3
"""Central configuration helpers for Assistant Hub."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable

PACKAGE_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_ROOT.parent
_DEFAULT_DATA_DIR = Path(os.getenv("ASSISTANT_HUB_HOME", PROJECT_ROOT)).expanduser()


def _path_from_env(key: str, fallback: Path) -> Path:
    value = os.getenv(key)
    return Path(value).expanduser() if value else fallback


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

