"""
Unified logging system that aggregates logs from all threads and services.
Provides a centralized view of all system events ordered by timestamp.
"""

from fastapi import APIRouter, Depends, Query
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
import json
import sqlite3
from contextlib import contextmanager
import threading
import logging
import sys

from backend_api.auth import User, get_current_active_user, get_current_admin_user

router = APIRouter()

# Unified log database
LOG_DB_PATH = Path(__file__).parent.parent.parent / "logs" / "unified.db"
LOG_DB_PATH.parent.mkdir(parents=True, exist_ok=True)

_lock = threading.Lock()


@contextmanager
def get_log_db():
    """Context manager for log database connection."""
    conn = sqlite3.connect(str(LOG_DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_log_db():
    """Initialize unified log database."""
    with get_log_db() as conn:
        cursor = conn.cursor()
        
        # Unified logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS unified_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP NOT NULL,
                thread_id TEXT,
                thread_name TEXT,
                process_id INTEGER,
                level TEXT NOT NULL,
                logger_name TEXT NOT NULL,
                module TEXT,
                function TEXT,
                line_number INTEGER,
                message TEXT NOT NULL,
                exception TEXT,
                trace TEXT,
                user_id INTEGER,
                username TEXT,
                request_id TEXT,
                session_id TEXT,
                service TEXT,
                component TEXT,
                action TEXT,
                resource TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes for efficient querying
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp 
            ON unified_logs(timestamp DESC)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_level 
            ON unified_logs(level)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_service 
            ON unified_logs(service)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user 
            ON unified_logs(user_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_request 
            ON unified_logs(request_id)
        """)
        
        # Service health tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS service_health (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_name TEXT UNIQUE NOT NULL,
                status TEXT NOT NULL,
                last_heartbeat TIMESTAMP NOT NULL,
                error_count INTEGER DEFAULT 0,
                warning_count INTEGER DEFAULT 0,
                info_count INTEGER DEFAULT 0,
                metadata TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Dependencies tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS service_dependencies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_name TEXT NOT NULL,
                depends_on TEXT NOT NULL,
                dependency_type TEXT,
                status TEXT,
                last_check TIMESTAMP,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(service_name, depends_on)
            )
        """)
        
        conn.commit()


# Custom logging handler that writes to unified DB
class UnifiedLogHandler(logging.Handler):
    """Custom logging handler that writes to the unified log database."""
    
    def __init__(self):
        super().__init__()
        self.service = "backend_api"
    
    def emit(self, record):
        """Emit a log record to the database."""
        try:
            with _lock:
                with get_log_db() as conn:
                    cursor = conn.cursor()
                    
                    # Extract metadata
                    metadata = {}
                    if hasattr(record, 'metadata'):
                        metadata = record.metadata
                    
                    cursor.execute("""
                        INSERT INTO unified_logs (
                            timestamp, thread_id, thread_name, process_id,
                            level, logger_name, module, function, line_number,
                            message, exception, trace, user_id, username,
                            request_id, session_id, service, component,
                            action, resource, metadata
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        datetime.fromtimestamp(record.created),
                        str(record.thread),
                        record.threadName,
                        record.process,
                        record.levelname,
                        record.name,
                        record.module,
                        record.funcName,
                        record.lineno,
                        self.format(record),
                        str(record.exc_info) if record.exc_info else None,
                        self.formatException(record.exc_info) if record.exc_info else None,
                        metadata.get('user_id'),
                        metadata.get('username'),
                        metadata.get('request_id'),
                        metadata.get('session_id'),
                        self.service,
                        metadata.get('component'),
                        metadata.get('action'),
                        metadata.get('resource'),
                        json.dumps(metadata) if metadata else None
                    ))
                    
                    conn.commit()
        except Exception as e:
            # Don't let logging errors crash the application
            print(f"Error writing to unified log: {e}", file=sys.stderr)


def setup_unified_logging(service_name: str = "backend_api"):
    """Setup unified logging for the application."""
    handler = UnifiedLogHandler()
    handler.service = service_name
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    
    # Add to root logger
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)
    
    return handler


def log_event(
    level: str,
    message: str,
    service: str = "backend_api",
    component: Optional[str] = None,
    action: Optional[str] = None,
    resource: Optional[str] = None,
    user_id: Optional[int] = None,
    username: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
):
    """Log an event to the unified log system."""
    with get_log_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO unified_logs (
                timestamp, level, logger_name, message,
                service, component, action, resource,
                user_id, username, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.utcnow(),
            level,
            service,
            message,
            service,
            component,
            action,
            resource,
            user_id,
            username,
            json.dumps(metadata) if metadata else None
        ))
        
        conn.commit()


@router.get("/logs/unified")
async def get_unified_logs(
    level: Optional[str] = Query(None, description="Filter by log level"),
    service: Optional[str] = Query(None, description="Filter by service name"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    request_id: Optional[str] = Query(None, description="Filter by request ID"),
    since: Optional[datetime] = Query(None, description="Logs since this timestamp"),
    until: Optional[datetime] = Query(None, description="Logs until this timestamp"),
    limit: int = Query(1000, ge=1, le=10000),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get unified logs from all threads and services.
    Logs are ordered by timestamp (most recent first).
    """
    with get_log_db() as conn:
        cursor = conn.cursor()
        
        # Build query with filters
        query = "SELECT * FROM unified_logs WHERE 1=1"
        params = []
        
        if level:
            query += " AND level = ?"
            params.append(level)
        
        if service:
            query += " AND service = ?"
            params.append(service)
        
        if user_id:
            query += " AND user_id = ?"
            params.append(user_id)
        
        if request_id:
            query += " AND request_id = ?"
            params.append(request_id)
        
        if since:
            query += " AND timestamp >= ?"
            params.append(since)
        
        if until:
            query += " AND timestamp <= ?"
            params.append(until)
        
        query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        
        logs = []
        for row in cursor.fetchall():
            log_entry = dict(row)
            # Parse metadata JSON if present
            if log_entry.get('metadata'):
                try:
                    log_entry['metadata'] = json.loads(log_entry['metadata'])
                except:
                    pass
            logs.append(log_entry)
        
        # Get total count
        count_query = "SELECT COUNT(*) FROM unified_logs WHERE 1=1"
        cursor.execute(count_query, params[:-2])  # Exclude limit and offset
        total = cursor.fetchone()[0]
        
        return {
            "logs": logs,
            "total": total,
            "limit": limit,
            "offset": offset
        }


@router.get("/logs/stream")
async def stream_logs(
    level: Optional[str] = None,
    service: Optional[str] = None,
    tail: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get most recent logs (tail-like behavior).
    """
    with get_log_db() as conn:
        cursor = conn.cursor()
        
        query = "SELECT * FROM unified_logs WHERE 1=1"
        params = []
        
        if level:
            query += " AND level = ?"
            params.append(level)
        
        if service:
            query += " AND service = ?"
            params.append(service)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(tail)
        
        cursor.execute(query, params)
        
        logs = []
        for row in cursor.fetchall():
            log_entry = dict(row)
            if log_entry.get('metadata'):
                try:
                    log_entry['metadata'] = json.loads(log_entry['metadata'])
                except:
                    pass
            logs.append(log_entry)
        
        # Reverse to get chronological order
        logs.reverse()
        
        return {"logs": logs}


@router.get("/logs/services")
async def get_services_health(
    admin_user: User = Depends(get_current_admin_user)
):
    """
    Get health status of all tracked services (admin only).
    """
    with get_log_db() as conn:
        cursor = conn.cursor()
        
        # Get service health
        cursor.execute("""
            SELECT * FROM service_health 
            ORDER BY service_name
        """)
        
        services = []
        for row in cursor.fetchall():
            service = dict(row)
            if service.get('metadata'):
                try:
                    service['metadata'] = json.loads(service['metadata'])
                except:
                    pass
            services.append(service)
        
        # Get recent error counts by service
        cursor.execute("""
            SELECT service, level, COUNT(*) as count
            FROM unified_logs
            WHERE timestamp >= datetime('now', '-1 hour')
            GROUP BY service, level
        """)
        
        recent_stats = {}
        for row in cursor.fetchall():
            service_name = row[0]
            if service_name not in recent_stats:
                recent_stats[service_name] = {}
            recent_stats[service_name][row[1]] = row[2]
        
        return {
            "services": services,
            "recent_stats": recent_stats
        }


@router.get("/logs/dependencies")
async def get_service_dependencies(
    admin_user: User = Depends(get_current_admin_user)
):
    """
    Get service dependency graph (admin only).
    """
    with get_log_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM service_dependencies
            ORDER BY service_name, depends_on
        """)
        
        dependencies = []
        for row in cursor.fetchall():
            dep = dict(row)
            if dep.get('metadata'):
                try:
                    dep['metadata'] = json.loads(dep['metadata'])
                except:
                    pass
            dependencies.append(dep)
        
        return {"dependencies": dependencies}


@router.post("/logs/dependencies")
async def register_dependency(
    dependency_data: dict,
    admin_user: User = Depends(get_current_admin_user)
):
    """
    Register a service dependency (admin only).
    """
    with get_log_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO service_dependencies (
                service_name, depends_on, dependency_type, status, last_check, metadata
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            dependency_data.get('service_name'),
            dependency_data.get('depends_on'),
            dependency_data.get('dependency_type'),
            dependency_data.get('status', 'healthy'),
            datetime.utcnow(),
            json.dumps(dependency_data.get('metadata', {}))
        ))
        
        conn.commit()
    
    return {"message": "Dependency registered successfully"}


@router.post("/logs/heartbeat")
async def service_heartbeat(
    heartbeat_data: dict,
    current_user: User = Depends(get_current_active_user)
):
    """
    Update service heartbeat and health status.
    """
    with get_log_db() as conn:
        cursor = conn.cursor()
        
        service_name = heartbeat_data.get('service_name')
        status = heartbeat_data.get('status', 'healthy')
        
        cursor.execute("""
            INSERT OR REPLACE INTO service_health (
                service_name, status, last_heartbeat, metadata
            ) VALUES (?, ?, ?, ?)
        """, (
            service_name,
            status,
            datetime.utcnow(),
            json.dumps(heartbeat_data.get('metadata', {}))
        ))
        
        conn.commit()
    
    return {"message": "Heartbeat recorded"}


@router.get("/logs/analytics")
async def get_log_analytics(
    timeframe: str = Query("24h", description="Timeframe: 1h, 24h, 7d, 30d"),
    admin_user: User = Depends(get_current_admin_user)
):
    """
    Get log analytics and statistics (admin only).
    """
    # Parse timeframe
    timeframe_map = {
        "1h": "-1 hour",
        "24h": "-24 hours",
        "7d": "-7 days",
        "30d": "-30 days"
    }
    time_filter = timeframe_map.get(timeframe, "-24 hours")
    
    with get_log_db() as conn:
        cursor = conn.cursor()
        
        # Logs by level
        cursor.execute(f"""
            SELECT level, COUNT(*) as count
            FROM unified_logs
            WHERE timestamp >= datetime('now', '{time_filter}')
            GROUP BY level
        """)
        by_level = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Logs by service
        cursor.execute(f"""
            SELECT service, COUNT(*) as count
            FROM unified_logs
            WHERE timestamp >= datetime('now', '{time_filter}')
            GROUP BY service
            ORDER BY count DESC
        """)
        by_service = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Logs over time (hourly buckets)
        cursor.execute(f"""
            SELECT 
                strftime('%Y-%m-%d %H:00:00', timestamp) as hour,
                COUNT(*) as count
            FROM unified_logs
            WHERE timestamp >= datetime('now', '{time_filter}')
            GROUP BY hour
            ORDER BY hour
        """)
        over_time = [{"hour": row[0], "count": row[1]} for row in cursor.fetchall()]
        
        # Top errors
        cursor.execute(f"""
            SELECT message, COUNT(*) as count
            FROM unified_logs
            WHERE level = 'ERROR' 
            AND timestamp >= datetime('now', '{time_filter}')
            GROUP BY message
            ORDER BY count DESC
            LIMIT 10
        """)
        top_errors = [{"message": row[0], "count": row[1]} for row in cursor.fetchall()]
        
        # Most active users
        cursor.execute(f"""
            SELECT username, COUNT(*) as count
            FROM unified_logs
            WHERE username IS NOT NULL
            AND timestamp >= datetime('now', '{time_filter}')
            GROUP BY username
            ORDER BY count DESC
            LIMIT 10
        """)
        active_users = [{"username": row[0], "count": row[1]} for row in cursor.fetchall()]
        
        return {
            "timeframe": timeframe,
            "by_level": by_level,
            "by_service": by_service,
            "over_time": over_time,
            "top_errors": top_errors,
            "active_users": active_users
        }


# Initialize database on module import
init_log_db()
