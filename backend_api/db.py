"""Database helpers for FastAPI routes.

Provides a lightweight context manager that yields a thread-local SQLite
connection configured exactly like the desktop app. We reuse the schema
initialization logic from ``assistant_hub_gui.assistant_hub.db`` once at
import time, then open lean connections for every request.
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from typing import Iterator

from assistant_hub_gui.assistant_hub import db as gui_db
from assistant_hub.demo_seed import ensure_demo_data

_DB_INITIALIZED = False


def _ensure_initialized() -> None:
    """Make sure the schema exists before handing out lightweight handles."""
    global _DB_INITIALIZED
    if _DB_INITIALIZED:
        return
    conn = gui_db.init_db()
    ensure_demo_data(conn)
    conn.close()
    _DB_INITIALIZED = True


def _connect() -> sqlite3.Connection:
    """Create a new SQLite connection with the desktop row factory + pragmas."""
    conn = sqlite3.connect(gui_db.DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 5000")
    return conn


@contextmanager
def db_session() -> Iterator[sqlite3.Connection]:
    """Yield a fresh SQLite connection tied to the current thread."""
    _ensure_initialized()
    conn = _connect()
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()
