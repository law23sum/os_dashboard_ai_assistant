"""Database helpers for FastAPI routes.

Provides a lightweight context manager that yields a thread-local SQLite
connection configured exactly like the desktop app. We reuse the unified schema
initialization logic from ``assistant_hub.db`` once at import time, then open
lean connections for every request.

Features:
- Connection pooling for improved performance
- Proper exception handling with rollback on errors
- Thread-safe connection management
"""

from __future__ import annotations

import sqlite3
import threading
import logging
from contextlib import contextmanager
from queue import Queue, Empty
from typing import Iterator, Optional

from assistant_hub import db as hub_db
from assistant_hub.demo_seed import ensure_demo_data

logger = logging.getLogger(__name__)

_DB_INITIALIZED = False
_init_lock = threading.Lock()

# Connection pool settings
_POOL_SIZE = 10
_POOL_TIMEOUT = 30.0  # seconds to wait for a connection
_connection_pool: Optional[Queue] = None
_pool_lock = threading.Lock()


def _ensure_initialized() -> None:
    """Make sure the schema exists before handing out lightweight handles."""
    global _DB_INITIALIZED
    if _DB_INITIALIZED:
        return
    
    with _init_lock:
        # Double-check after acquiring lock
        if _DB_INITIALIZED:
            return
        try:
            conn = hub_db.init_db()
            ensure_demo_data(conn)
            conn.close()
            _DB_INITIALIZED = True
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise


def _create_connection() -> sqlite3.Connection:
    """Create a new SQLite connection with the desktop row factory + pragmas."""
    conn = sqlite3.connect(
        hub_db.DB_FILE, 
        check_same_thread=False,
        timeout=30.0  # Wait up to 30 seconds for locks
    )
    conn.row_factory = sqlite3.Row
    # Performance and reliability pragmas
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 5000")
    conn.execute("PRAGMA journal_mode = WAL")  # Write-ahead logging for better concurrency
    conn.execute("PRAGMA synchronous = NORMAL")  # Balance between safety and speed
    conn.execute("PRAGMA cache_size = -64000")  # 64MB cache
    return conn


def _get_pool() -> Queue:
    """Get or create the connection pool."""
    global _connection_pool
    
    if _connection_pool is None:
        with _pool_lock:
            if _connection_pool is None:
                _connection_pool = Queue(maxsize=_POOL_SIZE)
                # Pre-populate pool with a few connections
                for _ in range(min(3, _POOL_SIZE)):
                    try:
                        conn = _create_connection()
                        _connection_pool.put(conn)
                    except Exception as e:
                        logger.warning(f"Failed to pre-populate connection pool: {e}")
    
    return _connection_pool


def _get_connection() -> sqlite3.Connection:
    """Get a connection from the pool or create a new one."""
    pool = _get_pool()
    
    try:
        # Try to get a connection from the pool
        conn = pool.get_nowait()
        # Verify connection is still valid
        try:
            conn.execute("SELECT 1")
            return conn
        except sqlite3.Error:
            # Connection is stale, create a new one
            try:
                conn.close()
            except Exception:
                pass
            return _create_connection()
    except Empty:
        # Pool is empty, create a new connection
        return _create_connection()


def _return_connection(conn: sqlite3.Connection) -> None:
    """Return a connection to the pool or close it if pool is full."""
    pool = _get_pool()
    
    try:
        # Reset any uncommitted transaction state
        try:
            conn.rollback()
        except sqlite3.Error:
            pass
        
        # Try to return to pool
        pool.put_nowait(conn)
    except Exception:
        # Pool is full, close the connection
        try:
            conn.close()
        except Exception:
            pass


@contextmanager
def db_session() -> Iterator[sqlite3.Connection]:
    """Yield a database connection with proper transaction handling.
    
    This context manager:
    - Gets a connection from the pool (or creates one)
    - Yields it for use
    - Commits on success, rolls back on exception
    - Returns the connection to the pool
    """
    _ensure_initialized()
    conn = _get_connection()
    
    try:
        yield conn
        conn.commit()
    except Exception as e:
        # Rollback on any exception
        try:
            conn.rollback()
        except sqlite3.Error as rollback_error:
            logger.error(f"Failed to rollback transaction: {rollback_error}")
        logger.error(f"Database operation failed: {e}")
        raise
    finally:
        _return_connection(conn)


def close_all_connections() -> None:
    """Close all connections in the pool. Call this during shutdown."""
    global _connection_pool
    
    if _connection_pool is not None:
        with _pool_lock:
            while not _connection_pool.empty():
                try:
                    conn = _connection_pool.get_nowait()
                    conn.close()
                except Exception:
                    pass
            _connection_pool = None
        logger.info("All database connections closed")
