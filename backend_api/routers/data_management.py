"""
Data Management API Router - Backup, Restore, Migration
Provides endpoints for data backup, restore, and migration operations.
"""

from __future__ import annotations

import json
import shutil
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel

from backend_api.db import db_session
from assistant_hub_gui.assistant_hub.config import DATA_DIR

router = APIRouter()


class BackupResponse(BaseModel):
    success: bool
    backup_file: str
    timestamp: str
    size_bytes: int
    tables_backed_up: List[str]


class RestoreRequest(BaseModel):
    backup_file: str
    overwrite: bool = False


class RestoreResponse(BaseModel):
    success: bool
    restored_counts: Dict[str, int]
    timestamp: str


class DataStatsResponse(BaseModel):
    projects: int
    tasks: int
    ledger_events: int
    note_links: int
    database_size_mb: float
    last_backup: Optional[str]


def get_backup_dir() -> Path:
    """Get or create the backups directory."""
    backup_dir = Path(DATA_DIR) / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    return backup_dir


def get_database_path() -> Path:
    """Get the main database path."""
    return Path(__file__).parent.parent.parent / "assistant_hub_gui" / "assistant_hub" / "assistant_hub.db"


@router.get("/stats", response_model=DataStatsResponse)
async def get_data_stats():
    """Get statistics about current data storage."""
    db_path = get_database_path()
    
    with db_session() as db:
        projects_count = db.execute("SELECT COUNT(*) FROM projects").fetchone()[0]
        tasks_count = db.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
        
        # Get ledger events count
        try:
            ledger_count = db.execute("SELECT COUNT(*) FROM project_ledger").fetchone()[0]
        except sqlite3.OperationalError:
            ledger_count = 0
        
        # Get note links count
        try:
            links_count = db.execute("SELECT COUNT(*) FROM note_links").fetchone()[0]
        except sqlite3.OperationalError:
            links_count = 0
    
    # Get database size
    db_size_mb = db_path.stat().st_size / (1024 * 1024) if db_path.exists() else 0
    
    # Get last backup
    backup_dir = get_backup_dir()
    backups = sorted(backup_dir.glob("backup_*.db"), key=lambda p: p.stat().st_mtime, reverse=True)
    last_backup = backups[0].name if backups else None
    
    return DataStatsResponse(
        projects=projects_count,
        tasks=tasks_count,
        ledger_events=ledger_count,
        note_links=links_count,
        database_size_mb=round(db_size_mb, 2),
        last_backup=last_backup,
    )


@router.post("/backup", response_model=BackupResponse)
async def create_backup():
    """Create a full database backup."""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup_filename = f"backup_{timestamp}.db"
    
    db_path = get_database_path()
    backup_path = get_backup_dir() / backup_filename
    
    if not db_path.exists():
        raise HTTPException(status_code=404, detail="Database file not found")
    
    # Create backup
    shutil.copy2(db_path, backup_path)
    
    # Get table counts
    with sqlite3.connect(backup_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
    
    return BackupResponse(
        success=True,
        backup_file=backup_filename,
        timestamp=timestamp,
        size_bytes=backup_path.stat().st_size,
        tables_backed_up=tables,
    )


@router.post("/restore", response_model=RestoreResponse)
async def restore_backup(request: RestoreRequest):
    """Restore from a backup file."""
    backup_path = get_backup_dir() / request.backup_file
    
    if not backup_path.exists():
        raise HTTPException(status_code=404, detail=f"Backup file not found: {request.backup_file}")
    
    db_path = get_database_path()
    
    # Create a safety backup before restoring
    if db_path.exists() and not request.overwrite:
        safety_backup = get_backup_dir() / f"pre_restore_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.db"
        shutil.copy2(db_path, safety_backup)
    
    # Restore the backup
    shutil.copy2(backup_path, db_path)
    
    # Get counts
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        counts = {}
        for table in ["projects", "tasks", "project_ledger", "note_links"]:
            try:
                count = cursor.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                counts[table] = count
            except sqlite3.OperationalError:
                counts[table] = 0
    
    return RestoreResponse(
        success=True,
        restored_counts=counts,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@router.get("/backups")
async def list_backups():
    """List all available backups."""
    backup_dir = get_backup_dir()
    backups = []
    
    for backup_file in sorted(backup_dir.glob("backup_*.db"), key=lambda p: p.stat().st_mtime, reverse=True):
        stat = backup_file.stat()
        backups.append({
            "filename": backup_file.name,
            "size_bytes": stat.st_size,
            "size_mb": round(stat.st_size / (1024 * 1024), 2),
            "created": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
        })
    
    return {"backups": backups}


@router.get("/download-backup/{filename}")
async def download_backup(filename: str):
    """Download a specific backup file."""
    backup_path = get_backup_dir() / filename
    
    if not backup_path.exists():
        raise HTTPException(status_code=404, detail="Backup file not found")
    
    if not backup_path.name.startswith("backup_") or not backup_path.suffix == ".db":
        raise HTTPException(status_code=400, detail="Invalid backup filename")
    
    return FileResponse(
        path=backup_path,
        filename=filename,
        media_type="application/octet-stream",
    )


@router.post("/export-json")
async def export_to_json():
    """Export all data to JSON format."""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    export_filename = f"export_{timestamp}.json"
    export_path = get_backup_dir() / export_filename
    
    export_data = {
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "version": "1.0",
        "projects": [],
        "tasks": [],
        "ledger_events": [],
        "note_links": [],
    }
    
    with db_session() as db:
        # Export projects
        cursor = db.execute("SELECT * FROM projects")
        columns = [desc[0] for desc in cursor.description]
        for row in cursor.fetchall():
            export_data["projects"].append(dict(zip(columns, row)))
        
        # Export tasks
        cursor = db.execute("SELECT * FROM tasks")
        columns = [desc[0] for desc in cursor.description]
        for row in cursor.fetchall():
            export_data["tasks"].append(dict(zip(columns, row)))
        
        # Export ledger events
        try:
            cursor = db.execute("SELECT * FROM project_ledger")
            columns = [desc[0] for desc in cursor.description]
            for row in cursor.fetchall():
                event = dict(zip(columns, row))
                # Parse payload JSON if it's a string
                if isinstance(event.get("payload"), str):
                    try:
                        event["payload"] = json.loads(event["payload"])
                    except json.JSONDecodeError:
                        pass
                export_data["ledger_events"].append(event)
        except sqlite3.OperationalError:
            pass
        
        # Export note links
        try:
            cursor = db.execute("SELECT * FROM note_links")
            columns = [desc[0] for desc in cursor.description]
            for row in cursor.fetchall():
                export_data["note_links"].append(dict(zip(columns, row)))
        except sqlite3.OperationalError:
            pass
    
    # Write to file
    with open(export_path, "w", encoding="utf-8") as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    return FileResponse(
        path=export_path,
        filename=export_filename,
        media_type="application/json",
    )


@router.post("/import-json")
async def import_from_json(file: UploadFile = File(...)):
    """Import data from JSON export file."""
    try:
        content = await file.read()
        import_data = json.loads(content)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(e)}")
    
    imported_counts = {
        "projects": 0,
        "tasks": 0,
        "ledger_events": 0,
        "note_links": 0,
    }
    
    with db_session() as db:
        # Import projects
        for project in import_data.get("projects", []):
            try:
                db.execute(
                    """INSERT OR REPLACE INTO projects (name, description, status, priority, order_num)
                       VALUES (?, ?, ?, ?, ?)""",
                    (
                        project.get("name"),
                        project.get("description"),
                        project.get("status", "active"),
                        project.get("priority", "MEDIUM"),
                        project.get("order_num", 0),
                    ),
                )
                imported_counts["projects"] += 1
            except Exception as e:
                print(f"Error importing project {project.get('name')}: {e}")
        
        # Import tasks
        for task in import_data.get("tasks", []):
            try:
                db.execute(
                    """INSERT OR REPLACE INTO tasks 
                       (id, title, description, status, priority, project, due_date, owner, created_at, updated_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        task.get("id"),
                        task.get("title"),
                        task.get("description"),
                        task.get("status", "TODO"),
                        task.get("priority", "MEDIUM"),
                        task.get("project"),
                        task.get("due_date"),
                        task.get("owner"),
                        task.get("created_at"),
                        task.get("updated_at"),
                    ),
                )
                imported_counts["tasks"] += 1
            except Exception as e:
                print(f"Error importing task {task.get('id')}: {e}")
        
        db.commit()
    
    return {
        "success": True,
        "imported_counts": imported_counts,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
