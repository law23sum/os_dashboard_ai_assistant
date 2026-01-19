"""Unified logging system combining all executable threads' logs ordered by timestamp."""

from __future__ import annotations

import asyncio
import json
import logging
import threading
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from backend_api.deps import get_current_user, require_admin
from backend_api.security import AuthUser
from assistant_hub_gui.assistant_hub.config import DATA_DIR, ensure_data_directories

router = APIRouter()

ensure_data_directories()
LOG_DIR = DATA_DIR / "unified_logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# In-memory log buffer (thread-safe)
_log_buffer: deque = deque(maxlen=10000)
_log_lock = threading.Lock()


class LogEntry(BaseModel):
    timestamp: str
    thread_id: str
    thread_name: str
    level: str
    logger_name: str
    message: str
    module: Optional[str] = None
    function: Optional[str] = None
    line_number: Optional[int] = None
    extra_data: Dict[str, Any] = {}


class UnifiedLogHandler(logging.Handler):
    """Custom logging handler that captures all logs and adds them to unified buffer."""
    
    def emit(self, record: logging.LogRecord):
        """Emit a log record."""
        try:
            thread_id = str(threading.get_ident())
            thread_name = threading.current_thread().name
            
            log_entry = LogEntry(
                timestamp=datetime.utcnow().isoformat(),
                thread_id=thread_id,
                thread_name=thread_name,
                level=record.levelname,
                logger_name=record.name,
                message=self.format(record),
                module=record.module,
                function=record.funcName,
                line_number=record.lineno,
                extra_data={
                    "pathname": record.pathname,
                    "process_id": record.process,
                    "process_name": record.processName
                }
            )
            
            payload = log_entry.model_dump() if hasattr(log_entry, "model_dump") else log_entry.dict()
            with _log_lock:
                _log_buffer.append(payload)
        except Exception:
            pass  # Don't let logging errors break the application


# Set up unified logging handler
_unified_handler = UnifiedLogHandler()
_unified_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
_unified_handler.setFormatter(formatter)

# Add handler to root logger
root_logger = logging.getLogger()
root_logger.addHandler(_unified_handler)


def get_logs_from_buffer(
    limit: int = 1000,
    level: Optional[str] = None,
    thread_id: Optional[str] = None,
    logger_name: Optional[str] = None,
    search: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Get logs from in-memory buffer with filtering."""
    with _log_lock:
        logs = list(_log_buffer)
    
    # Apply filters
    filtered_logs = logs
    
    if level:
        filtered_logs = [log for log in filtered_logs if log.get("level") == level.upper()]
    
    if thread_id:
        filtered_logs = [log for log in filtered_logs if log.get("thread_id") == thread_id]
    
    if logger_name:
        filtered_logs = [log for log in filtered_logs if logger_name.lower() in log.get("logger_name", "").lower()]
    
    if search:
        search_lower = search.lower()
        filtered_logs = [
            log for log in filtered_logs
            if search_lower in log.get("message", "").lower()
            or search_lower in log.get("module", "").lower()
            or search_lower in log.get("function", "").lower()
        ]
    
    # Sort by timestamp (newest first)
    filtered_logs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    
    return filtered_logs[:limit]


def get_persisted_logs(
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    limit: int = 1000
) -> List[Dict[str, Any]]:
    """Get logs from persisted log files."""
    log_files = sorted(LOG_DIR.glob("*.jsonl"), reverse=True)
    all_logs = []
    
    for log_file in log_files[:10]:  # Only check last 10 log files
        try:
            with open(log_file, "r") as f:
                for line in f:
                    try:
                        log_entry = json.loads(line.strip())
                        if start_time and log_entry.get("timestamp") < start_time:
                            continue
                        if end_time and log_entry.get("timestamp") > end_time:
                            continue
                        all_logs.append(log_entry)
                    except json.JSONDecodeError:
                        continue
        except Exception:
            continue
    
    # Sort by timestamp
    all_logs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return all_logs[:limit]


def persist_logs():
    """Persist logs from buffer to disk."""
    with _log_lock:
        logs_to_persist = list(_log_buffer)
        _log_buffer.clear()
    
    if not logs_to_persist:
        return
    
    # Create log file for today
    today = datetime.utcnow().strftime("%Y-%m-%d")
    log_file = LOG_DIR / f"unified_{today}.jsonl"
    
    # Append logs to file
    with open(log_file, "a") as f:
        for log_entry in logs_to_persist:
            f.write(json.dumps(log_entry) + "\n")


# Background task to persist logs periodically
async def log_persister():
    """Background task to persist logs every minute."""
    while True:
        await asyncio.sleep(60)  # Persist every minute
        try:
            persist_logs()
        except Exception:
            pass


@router.get("/logs", response_model=List[LogEntry])
async def get_unified_logs(
    limit: int = Query(1000, le=10000),
    level: Optional[str] = Query(None),
    thread_id: Optional[str] = Query(None),
    logger_name: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    start_time: Optional[str] = Query(None),
    end_time: Optional[str] = Query(None),
    current_user: AuthUser = Depends(get_current_user)
):
    """Get unified logs from all threads, ordered by timestamp."""
    # Get from buffer
    buffer_logs = get_logs_from_buffer(
        limit=limit,
        level=level,
        thread_id=thread_id,
        logger_name=logger_name,
        search=search
    )
    
    # Get from persisted logs if time range specified
    persisted_logs = []
    if start_time or end_time:
        persisted_logs = get_persisted_logs(
            start_time=start_time,
            end_time=end_time,
            limit=limit
        )
    
    # Combine and deduplicate
    all_logs = {}
    for log in buffer_logs + persisted_logs:
        key = f"{log.get('timestamp')}_{log.get('thread_id')}_{log.get('message', '')[:50]}"
        if key not in all_logs:
            all_logs[key] = log
    
    # Sort by timestamp
    sorted_logs = sorted(
        all_logs.values(),
        key=lambda x: x.get("timestamp", ""),
        reverse=True
    )
    
    return [LogEntry(**log) for log in sorted_logs[:limit]]


@router.get("/logs/stats")
async def get_log_stats(
    current_user: AuthUser = Depends(require_admin)
):
    """Get logging statistics."""
    with _log_lock:
        buffer_size = len(_log_buffer)
        buffer_logs = list(_log_buffer)
    
    # Count by level
    level_counts = {}
    thread_counts = {}
    logger_counts = {}
    
    for log in buffer_logs:
        level = log.get("level", "UNKNOWN")
        level_counts[level] = level_counts.get(level, 0) + 1
        
        thread_id = log.get("thread_id", "unknown")
        thread_counts[thread_id] = thread_counts.get(thread_id, 0) + 1
        
        logger_name = log.get("logger_name", "unknown")
        logger_counts[logger_name] = logger_counts.get(logger_name, 0) + 1
    
    # Get persisted log file stats
    log_files = list(LOG_DIR.glob("*.jsonl"))
    total_file_size = sum(f.stat().st_size for f in log_files)
    
    return {
        "buffer_size": buffer_size,
        "level_distribution": level_counts,
        "active_threads": len(thread_counts),
        "thread_distribution": dict(list(thread_counts.items())[:10]),
        "logger_distribution": dict(list(logger_counts.items())[:10]),
        "persisted_files": len(log_files),
        "total_persisted_size_bytes": total_file_size
    }


@router.get("/logs/stream")
async def stream_logs(
    current_user: AuthUser = Depends(require_admin)
):
    """Stream logs in real-time (SSE)."""
    from fastapi.responses import StreamingResponse
    import time
    
    async def generate():
        last_timestamp = datetime.utcnow().isoformat()
        
        while True:
            with _log_lock:
                new_logs = [
                    log for log in _log_buffer
                    if log.get("timestamp", "") > last_timestamp
                ]
            
            if new_logs:
                new_logs.sort(key=lambda x: x.get("timestamp", ""))
                last_timestamp = new_logs[-1].get("timestamp", last_timestamp)
                
                for log in new_logs:
                    yield f"data: {json.dumps(log)}\n\n"
            
            await asyncio.sleep(1)
    
    return StreamingResponse(generate(), media_type="text/event-stream")
