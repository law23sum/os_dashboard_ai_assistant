"""Unified Logging System API Router.

Combines all executable thread logs into one endless log ordered by timestamp.
Provides real-time log streaming and service interaction tracking.
"""

from __future__ import annotations

import json
import sqlite3
import threading
from collections import deque
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Deque
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Query, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field

from backend_api.db import db_session

router = APIRouter()

# In-memory log buffer for real-time streaming
LOG_BUFFER: Deque[Dict[str, Any]] = deque(maxlen=10000)
LOG_SUBSCRIBERS: List[WebSocket] = []
_log_lock = threading.Lock()


def _now_iso() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


class LogEntry(BaseModel):
    """Unified log entry."""
    id: str
    timestamp: str
    level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    source: str  # Service/component name
    thread_id: Optional[str] = None
    request_id: Optional[str] = None
    user_id: Optional[str] = None
    action: str
    message: str
    details: Optional[Dict[str, Any]] = None
    duration_ms: Optional[int] = None
    tags: List[str] = Field(default_factory=list)


class LogFilter(BaseModel):
    """Log filtering options."""
    levels: Optional[List[str]] = None
    sources: Optional[List[str]] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    search: Optional[str] = None
    tags: Optional[List[str]] = None
    user_id: Optional[str] = None


class ServiceMetric(BaseModel):
    """Service health metric."""
    service_name: str
    total_requests: int
    success_count: int
    error_count: int
    avg_duration_ms: float
    p95_duration_ms: float
    last_activity: str


def _ensure_log_tables(conn: sqlite3.Connection) -> None:
    """Ensure logging tables exist."""
    c = conn.cursor()
    
    # Unified log table
    c.execute("""
        CREATE TABLE IF NOT EXISTS unified_logs (
            id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL,
            level TEXT NOT NULL DEFAULT 'INFO',
            source TEXT NOT NULL,
            thread_id TEXT,
            request_id TEXT,
            user_id TEXT,
            action TEXT NOT NULL,
            message TEXT NOT NULL,
            details_json TEXT,
            duration_ms INTEGER,
            tags_json TEXT
        )
    """)
    
    # Indexes for efficient querying
    c.execute("CREATE INDEX IF NOT EXISTS idx_unified_logs_time ON unified_logs(timestamp DESC)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_unified_logs_source ON unified_logs(source, timestamp DESC)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_unified_logs_level ON unified_logs(level, timestamp DESC)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_unified_logs_request ON unified_logs(request_id)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_unified_logs_user ON unified_logs(user_id, timestamp DESC)")
    
    # Service metrics aggregation table
    c.execute("""
        CREATE TABLE IF NOT EXISTS service_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_name TEXT NOT NULL,
            period_start TEXT NOT NULL,
            period_end TEXT NOT NULL,
            total_requests INTEGER DEFAULT 0,
            success_count INTEGER DEFAULT 0,
            error_count INTEGER DEFAULT 0,
            total_duration_ms INTEGER DEFAULT 0,
            min_duration_ms INTEGER,
            max_duration_ms INTEGER,
            p95_duration_ms INTEGER
        )
    """)
    
    c.execute("CREATE INDEX IF NOT EXISTS idx_service_metrics_name ON service_metrics(service_name, period_start DESC)")
    
    conn.commit()


async def broadcast_log(log_entry: Dict[str, Any]) -> None:
    """Broadcast log entry to all WebSocket subscribers."""
    disconnected = []
    for ws in LOG_SUBSCRIBERS:
        try:
            await ws.send_json(log_entry)
        except Exception:
            disconnected.append(ws)
    
    for ws in disconnected:
        if ws in LOG_SUBSCRIBERS:
            LOG_SUBSCRIBERS.remove(ws)


def log_event(
    source: str,
    action: str,
    message: str,
    level: str = "INFO",
    thread_id: Optional[str] = None,
    request_id: Optional[str] = None,
    user_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    duration_ms: Optional[int] = None,
    tags: Optional[List[str]] = None,
    persist: bool = True
) -> LogEntry:
    """Log an event to the unified log system."""
    log_id = uuid4().hex[:12]
    timestamp = _now_iso()
    
    entry = LogEntry(
        id=log_id,
        timestamp=timestamp,
        level=level.upper(),
        source=source,
        thread_id=thread_id,
        request_id=request_id,
        user_id=user_id,
        action=action,
        message=message,
        details=details,
        duration_ms=duration_ms,
        tags=tags or []
    )
    
    # Add to buffer
    with _log_lock:
        LOG_BUFFER.append(entry.model_dump())
    
    # Persist to database
    if persist:
        try:
            with db_session() as conn:
                _ensure_log_tables(conn)
                c = conn.cursor()
                c.execute("""
                    INSERT INTO unified_logs 
                    (id, timestamp, level, source, thread_id, request_id, user_id, 
                     action, message, details_json, duration_ms, tags_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    log_id, timestamp, level.upper(), source, thread_id, request_id,
                    user_id, action, message,
                    json.dumps(details) if details else None,
                    duration_ms,
                    json.dumps(tags) if tags else None
                ))
                conn.commit()
        except Exception as e:
            # Don't fail the operation if logging fails
            print(f"Failed to persist log: {e}")
    
    return entry


@router.get("/", response_model=List[LogEntry])
async def get_logs(
    limit: int = Query(100, le=10000),
    offset: int = 0,
    level: Optional[str] = None,
    source: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    search: Optional[str] = None,
    user_id: Optional[str] = None,
    request_id: Optional[str] = None,
    tags: Optional[str] = None  # Comma-separated
) -> List[LogEntry]:
    """Get logs with filtering options."""
    with db_session() as conn:
        _ensure_log_tables(conn)
        c = conn.cursor()
        
        conditions = []
        params = []
        
        if level:
            conditions.append("level = ?")
            params.append(level.upper())
        if source:
            conditions.append("source = ?")
            params.append(source)
        if start_time:
            conditions.append("timestamp >= ?")
            params.append(start_time)
        if end_time:
            conditions.append("timestamp <= ?")
            params.append(end_time)
        if search:
            conditions.append("(message LIKE ? OR action LIKE ?)")
            params.extend([f"%{search}%", f"%{search}%"])
        if user_id:
            conditions.append("user_id = ?")
            params.append(user_id)
        if request_id:
            conditions.append("request_id = ?")
            params.append(request_id)
        if tags:
            tag_list = [t.strip() for t in tags.split(",")]
            for tag in tag_list:
                conditions.append("tags_json LIKE ?")
                params.append(f'%"{tag}"%')
        
        where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        
        c.execute(f"""
            SELECT * FROM unified_logs
            {where}
            ORDER BY timestamp DESC, id DESC
            LIMIT ? OFFSET ?
        """, params + [limit, offset])
        
        logs = []
        for row in c.fetchall():
            logs.append(LogEntry(
                id=row["id"],
                timestamp=row["timestamp"],
                level=row["level"],
                source=row["source"],
                thread_id=row["thread_id"],
                request_id=row["request_id"],
                user_id=row["user_id"],
                action=row["action"],
                message=row["message"],
                details=json.loads(row["details_json"]) if row["details_json"] else None,
                duration_ms=row["duration_ms"],
                tags=json.loads(row["tags_json"]) if row["tags_json"] else []
            ))
        
        return logs


@router.get("/stream")
async def get_log_stream(
    limit: int = Query(100, le=1000)
) -> List[Dict[str, Any]]:
    """Get recent logs from memory buffer for real-time viewing."""
    with _log_lock:
        return list(LOG_BUFFER)[-limit:]


@router.websocket("/ws")
async def websocket_logs(websocket: WebSocket):
    """WebSocket endpoint for real-time log streaming."""
    await websocket.accept()
    LOG_SUBSCRIBERS.append(websocket)
    
    try:
        # Send recent logs on connect
        with _log_lock:
            for log in list(LOG_BUFFER)[-50:]:
                await websocket.send_json(log)
        
        # Keep connection alive
        while True:
            try:
                # Wait for client messages (e.g., filters)
                data = await websocket.receive_text()
                # Could implement filtering here based on client preferences
            except WebSocketDisconnect:
                break
    finally:
        if websocket in LOG_SUBSCRIBERS:
            LOG_SUBSCRIBERS.remove(websocket)


@router.get("/sources")
async def get_log_sources() -> List[str]:
    """Get all unique log sources."""
    with db_session() as conn:
        _ensure_log_tables(conn)
        c = conn.cursor()
        c.execute("SELECT DISTINCT source FROM unified_logs ORDER BY source")
        return [row[0] for row in c.fetchall()]


@router.get("/levels")
async def get_log_levels() -> List[str]:
    """Get all log levels with counts."""
    with db_session() as conn:
        _ensure_log_tables(conn)
        c = conn.cursor()
        c.execute("""
            SELECT level, COUNT(*) as count 
            FROM unified_logs 
            GROUP BY level 
            ORDER BY count DESC
        """)
        return [{"level": row[0], "count": row[1]} for row in c.fetchall()]


@router.get("/stats")
async def get_log_stats(
    hours: int = Query(24, le=168)  # Max 1 week
) -> Dict[str, Any]:
    """Get log statistics for the specified time period."""
    with db_session() as conn:
        _ensure_log_tables(conn)
        c = conn.cursor()
        
        cutoff = (datetime.utcnow() - timedelta(hours=hours)).isoformat() + "Z"
        
        # Total counts by level
        c.execute("""
            SELECT level, COUNT(*) as count
            FROM unified_logs
            WHERE timestamp >= ?
            GROUP BY level
        """, (cutoff,))
        by_level = {row[0]: row[1] for row in c.fetchall()}
        
        # Counts by source
        c.execute("""
            SELECT source, COUNT(*) as count
            FROM unified_logs
            WHERE timestamp >= ?
            GROUP BY source
            ORDER BY count DESC
            LIMIT 20
        """, (cutoff,))
        by_source = [{"source": row[0], "count": row[1]} for row in c.fetchall()]
        
        # Error rate over time (hourly)
        c.execute("""
            SELECT 
                strftime('%Y-%m-%d %H:00', timestamp) as hour,
                COUNT(*) as total,
                SUM(CASE WHEN level = 'ERROR' OR level = 'CRITICAL' THEN 1 ELSE 0 END) as errors
            FROM unified_logs
            WHERE timestamp >= ?
            GROUP BY hour
            ORDER BY hour
        """, (cutoff,))
        error_timeline = []
        for row in c.fetchall():
            error_timeline.append({
                "hour": row[0],
                "total": row[1],
                "errors": row[2],
                "error_rate": (row[2] / row[1] * 100) if row[1] > 0 else 0
            })
        
        # Average duration by source
        c.execute("""
            SELECT source, AVG(duration_ms) as avg_duration, MAX(duration_ms) as max_duration
            FROM unified_logs
            WHERE timestamp >= ? AND duration_ms IS NOT NULL
            GROUP BY source
        """, (cutoff,))
        duration_by_source = [
            {"source": row[0], "avg_ms": row[1], "max_ms": row[2]}
            for row in c.fetchall()
        ]
        
        return {
            "period_hours": hours,
            "by_level": by_level,
            "by_source": by_source,
            "error_timeline": error_timeline,
            "duration_by_source": duration_by_source
        }


@router.get("/request/{request_id}")
async def get_request_trace(request_id: str) -> List[LogEntry]:
    """Get all logs for a specific request (request tracing)."""
    with db_session() as conn:
        _ensure_log_tables(conn)
        c = conn.cursor()
        
        c.execute("""
            SELECT * FROM unified_logs
            WHERE request_id = ?
            ORDER BY timestamp ASC
        """, (request_id,))
        
        logs = []
        for row in c.fetchall():
            logs.append(LogEntry(
                id=row["id"],
                timestamp=row["timestamp"],
                level=row["level"],
                source=row["source"],
                thread_id=row["thread_id"],
                request_id=row["request_id"],
                user_id=row["user_id"],
                action=row["action"],
                message=row["message"],
                details=json.loads(row["details_json"]) if row["details_json"] else None,
                duration_ms=row["duration_ms"],
                tags=json.loads(row["tags_json"]) if row["tags_json"] else []
            ))
        
        return logs


@router.get("/services/metrics")
async def get_service_metrics(
    hours: int = Query(24, le=168)
) -> List[ServiceMetric]:
    """Get aggregated metrics for each service."""
    with db_session() as conn:
        _ensure_log_tables(conn)
        c = conn.cursor()
        
        cutoff = (datetime.utcnow() - timedelta(hours=hours)).isoformat() + "Z"
        
        c.execute("""
            SELECT 
                source,
                COUNT(*) as total,
                SUM(CASE WHEN level NOT IN ('ERROR', 'CRITICAL') THEN 1 ELSE 0 END) as success,
                SUM(CASE WHEN level IN ('ERROR', 'CRITICAL') THEN 1 ELSE 0 END) as errors,
                AVG(duration_ms) as avg_duration,
                MAX(timestamp) as last_activity
            FROM unified_logs
            WHERE timestamp >= ?
            GROUP BY source
            ORDER BY total DESC
        """, (cutoff,))
        
        metrics = []
        for row in c.fetchall():
            # Calculate P95 (approximation)
            c.execute("""
                SELECT duration_ms FROM unified_logs
                WHERE source = ? AND timestamp >= ? AND duration_ms IS NOT NULL
                ORDER BY duration_ms DESC
                LIMIT 1 OFFSET (
                    SELECT CAST(COUNT(*) * 0.05 AS INTEGER) FROM unified_logs
                    WHERE source = ? AND timestamp >= ? AND duration_ms IS NOT NULL
                )
            """, (row[0], cutoff, row[0], cutoff))
            p95_row = c.fetchone()
            p95 = p95_row[0] if p95_row else 0
            
            metrics.append(ServiceMetric(
                service_name=row[0],
                total_requests=row[1],
                success_count=row[2] or 0,
                error_count=row[3] or 0,
                avg_duration_ms=row[4] or 0,
                p95_duration_ms=p95,
                last_activity=row[5]
            ))
        
        return metrics


@router.post("/")
async def create_log_entry(entry: LogEntry) -> LogEntry:
    """Create a new log entry (for external services)."""
    return log_event(
        source=entry.source,
        action=entry.action,
        message=entry.message,
        level=entry.level,
        thread_id=entry.thread_id,
        request_id=entry.request_id,
        user_id=entry.user_id,
        details=entry.details,
        duration_ms=entry.duration_ms,
        tags=entry.tags
    )


@router.delete("/cleanup")
async def cleanup_old_logs(
    days: int = Query(30, ge=1, le=365)
) -> Dict[str, Any]:
    """Clean up logs older than specified days."""
    with db_session() as conn:
        _ensure_log_tables(conn)
        c = conn.cursor()
        
        cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat() + "Z"
        
        c.execute("SELECT COUNT(*) FROM unified_logs WHERE timestamp < ?", (cutoff,))
        count_before = c.fetchone()[0]
        
        c.execute("DELETE FROM unified_logs WHERE timestamp < ?", (cutoff,))
        conn.commit()
        
        return {
            "deleted_count": count_before,
            "cutoff_date": cutoff,
            "message": f"Deleted {count_before} logs older than {days} days"
        }
