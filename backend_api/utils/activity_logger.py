"""Dedicated activity log store and backup utilities."""

from __future__ import annotations

import json
import shutil
import sqlite3
import zipfile
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional

from assistant_hub_gui.assistant_hub.config import DATA_DIR, DB_PATH, ensure_data_directories

ACTIVITY_DB_NAME = "activity_log.db"
ACTIVITY_DB_PATH = DATA_DIR / ACTIVITY_DB_NAME
ACTIVITY_BACKUP_DIR = DATA_DIR / "log_backups"


def _ensure_db() -> sqlite3.Connection:
    """Open or initialize the activity log database."""
    ensure_data_directories()
    conn = sqlite3.connect(
        ACTIVITY_DB_PATH,
        check_same_thread=False,
        timeout=10.0,
    )
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA synchronous = NORMAL")
    conn.execute("PRAGMA cache_size = -32000")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS activity_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_log_id INTEGER,
            timestamp TEXT,
            level TEXT,
            source TEXT,
            actor TEXT,
            thread TEXT,
            process TEXT,
            message TEXT,
            metadata_json TEXT,
            created_at TEXT
        )
        """
    )
    conn.commit()
    return conn


def record_activity_event(
    *,
    event_log_id: int,
    level: str,
    source: str,
    message: str,
    actor: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    thread: Optional[str] = None,
    process: Optional[str] = None,
    timestamp: Optional[str] = None,
) -> int:
    """Persist a structured entry in the dedicated activity log DB."""
    metadata_json = json.dumps(metadata or {}, ensure_ascii=False)
    timestamp = timestamp or datetime.utcnow().isoformat()
    conn = _ensure_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO activity_log (
            event_log_id,
            timestamp,
            level,
            source,
            actor,
            thread,
            process,
            message,
            metadata_json,
            created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            event_log_id,
            timestamp,
            level,
            source,
            actor or "unknown",
            thread,
            process,
            message,
            metadata_json,
            datetime.utcnow().isoformat(),
        ),
    )
    conn.commit()
    entry_id = cursor.lastrowid or 0
    conn.close()
    return entry_id


def get_activity_db_path() -> Path:
    """Return the path to the activity log database."""
    ensure_data_directories()
    return ACTIVITY_DB_PATH


def copy_activity_db(destination: Path) -> Path:
    """Copy the activity DB to a remote destination."""
    ensure_data_directories()
    destination_parent = destination.expanduser().parent
    destination_parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ACTIVITY_DB_PATH, destination)
    return destination


def collect_backup_artifacts(include_main_db: bool = False) -> List[Path]:
    """Return the files that should be included in a backup archive."""
    ensure_data_directories()
    artifacts = [ACTIVITY_DB_PATH]
    if include_main_db and DB_PATH.exists():
        artifacts.append(DB_PATH)
    return artifacts


def create_zipped_backup(
    *,
    backup_root: Path,
    include_main_db: bool = False,
    suffix: str = "",
) -> Path:
    """Write a ZIP archive containing the activity log DB (and optionally the primary DB)."""
    backup_root = backup_root.expanduser()
    backup_root.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    zip_name = f"activity-log-backup{suffix}-{timestamp}.zip"
    target = backup_root / zip_name
    artifacts = collect_backup_artifacts(include_main_db=include_main_db)
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for item in artifacts:
            if item.exists():
                archive.write(item, item.name)
    return target
