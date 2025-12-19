"""Database helpers for FastAPI routes.

Provides a lightweight context manager that yields a thread-local SQLite
connection configured exactly like the desktop app. We reuse the unified schema
initialization logic from ``assistant_hub.db`` once at import time, then open
lean connections for every request.
"""

from __future__ import annotations

import sqlite3
import threading
from contextlib import contextmanager
from typing import Iterator

from assistant_hub import db as hub_db
from assistant_hub.demo_seed import ensure_demo_data

_DB_INITIALIZED = False
_DB_INIT_LOCK = threading.Lock()


def _ensure_initialized() -> None:
    """Make sure the schema exists before handing out lightweight handles.
    
    Thread-safe initialization using a lock to prevent race conditions
    when multiple requests initialize the database simultaneously.
    """
    global _DB_INITIALIZED
    if _DB_INITIALIZED:
        return
    
    with _DB_INIT_LOCK:
        # Double-check pattern to avoid redundant initialization
        if _DB_INITIALIZED:
            return
        try:
            conn = hub_db.init_db()
            ensure_demo_data(conn)
            conn.close()
            _DB_INITIALIZED = True
        except Exception as e:
            # Log error but don't fail silently - let the next attempt retry
            import logging
            logging.error(f"Database initialization failed: {e}", exc_info=True)
            raise


def _connect() -> sqlite3.Connection:
    """Create a new SQLite connection with the desktop row factory + pragmas.
    
    Returns:
        sqlite3.Connection: Configured database connection
        
    Raises:
        sqlite3.Error: If connection cannot be established
    """
    try:
        conn = sqlite3.connect(hub_db.DB_FILE, check_same_thread=False, timeout=10.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA busy_timeout = 5000")
        # Enable WAL mode for better concurrency
        conn.execute("PRAGMA journal_mode = WAL")
        # Optimize for read-heavy workloads
        conn.execute("PRAGMA synchronous = NORMAL")
        conn.execute("PRAGMA cache_size = -64000")  # 64MB cache
        return conn
    except sqlite3.Error as e:
        import logging
        logging.error(f"Failed to connect to database: {e}", exc_info=True)
        raise


@contextmanager
def db_session() -> Iterator[sqlite3.Connection]:
    """Yield a fresh SQLite connection tied to the current thread.
    
    Properly handles transaction rollback on exceptions and ensures
    connections are always closed, even if an error occurs.
    
    Yields:
        sqlite3.Connection: Database connection
        
    Raises:
        sqlite3.Error: If database operations fail
    """
    _ensure_initialized()
    conn = _connect()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
