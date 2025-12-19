"""Admin Panel API Router - Django-like Admin Interface.

Provides comprehensive admin capabilities including:
- User management
- Database schema viewing (tables, schemas, objects)
- Real-time system monitoring
- Unified logging view
- Demo vs production data separation
"""

from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from backend_api.db import db_session
from backend_api.routers.auth import require_admin, _ensure_auth_tables, _hash_password, _log_activity

router = APIRouter()


class AdminStats(BaseModel):
    """Admin dashboard statistics."""
    total_users: int
    active_users: int
    demo_users: int
    production_users: int
    total_sessions: int
    active_sessions: int
    total_tasks: int
    total_projects: int
    total_documents: int
    total_operations: int
    system_health: str


class UserAdminResponse(BaseModel):
    """User data for admin view."""
    id: str
    username: str
    email: str
    display_name: Optional[str]
    is_admin: bool
    is_active: bool
    is_demo_user: bool
    created_at: str
    last_login: Optional[str]
    login_count: int
    session_count: int


class UserAdminUpdate(BaseModel):
    """User update from admin."""
    display_name: Optional[str] = None
    is_admin: Optional[bool] = None
    is_active: Optional[bool] = None
    is_demo_user: Optional[bool] = None


class TableSchema(BaseModel):
    """Database table schema."""
    name: str
    columns: List[Dict[str, Any]]
    row_count: int
    indexes: List[Dict[str, Any]]


class SystemLog(BaseModel):
    """Unified system log entry."""
    id: int
    timestamp: str
    log_type: str
    source: str
    user_id: Optional[str]
    username: Optional[str]
    action: str
    details: Optional[str]
    ip_address: Optional[str]
    severity: str


def _now_iso() -> str:
    return datetime.utcnow().isoformat(timespec="seconds")


def _ensure_admin_tables(conn: sqlite3.Connection) -> None:
    """Ensure admin-specific tables exist."""
    _ensure_auth_tables(conn)
    c = conn.cursor()
    
    # Unified system logs table
    c.execute("""
        CREATE TABLE IF NOT EXISTS system_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            log_type TEXT NOT NULL,
            source TEXT NOT NULL,
            user_id TEXT,
            action TEXT NOT NULL,
            details TEXT,
            ip_address TEXT,
            severity TEXT DEFAULT 'info',
            thread_id TEXT,
            request_id TEXT
        )
    """)
    
    # Service health metrics
    c.execute("""
        CREATE TABLE IF NOT EXISTS service_health (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_name TEXT NOT NULL,
            status TEXT NOT NULL,
            response_time_ms INTEGER,
            error_count INTEGER DEFAULT 0,
            last_check TEXT NOT NULL,
            metadata_json TEXT
        )
    """)
    
    # Service interactions for dependency tracking
    c.execute("""
        CREATE TABLE IF NOT EXISTS service_interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_service TEXT NOT NULL,
            target_service TEXT NOT NULL,
            interaction_type TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            duration_ms INTEGER,
            success INTEGER DEFAULT 1,
            request_id TEXT,
            metadata_json TEXT
        )
    """)
    
    c.execute("CREATE INDEX IF NOT EXISTS idx_system_logs_timestamp ON system_logs(timestamp DESC)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_system_logs_type ON system_logs(log_type, timestamp DESC)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_service_health_name ON service_health(service_name)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_service_interactions_time ON service_interactions(timestamp DESC)")
    
    conn.commit()


def log_system_event(
    conn: sqlite3.Connection,
    log_type: str,
    source: str,
    action: str,
    details: Optional[str] = None,
    user_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    severity: str = "info",
    thread_id: Optional[str] = None,
    request_id: Optional[str] = None
) -> int:
    """Log a system event to the unified log."""
    _ensure_admin_tables(conn)
    c = conn.cursor()
    c.execute("""
        INSERT INTO system_logs 
        (timestamp, log_type, source, user_id, action, details, ip_address, severity, thread_id, request_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (_now_iso(), log_type, source, user_id, action, details, ip_address, severity, thread_id, request_id))
    conn.commit()
    return c.lastrowid


def record_service_interaction(
    conn: sqlite3.Connection,
    source_service: str,
    target_service: str,
    interaction_type: str,
    duration_ms: Optional[int] = None,
    success: bool = True,
    request_id: Optional[str] = None,
    metadata: Optional[Dict] = None
) -> int:
    """Record a service-to-service interaction for dependency tracking."""
    _ensure_admin_tables(conn)
    c = conn.cursor()
    c.execute("""
        INSERT INTO service_interactions
        (source_service, target_service, interaction_type, timestamp, duration_ms, success, request_id, metadata_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (source_service, target_service, interaction_type, _now_iso(), duration_ms, 
          1 if success else 0, request_id, json.dumps(metadata) if metadata else None))
    conn.commit()
    return c.lastrowid


# ==================== Admin Dashboard ====================

@router.get("/stats", response_model=AdminStats)
async def get_admin_stats(admin: Dict = Depends(require_admin)) -> AdminStats:
    """Get admin dashboard statistics."""
    with db_session() as conn:
        _ensure_admin_tables(conn)
        c = conn.cursor()
        
        # User stats
        c.execute("SELECT COUNT(*) FROM users")
        total_users = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM users WHERE is_active = 1")
        active_users = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM users WHERE is_demo_user = 1")
        demo_users = c.fetchone()[0]
        
        production_users = total_users - demo_users
        
        # Session stats
        c.execute("SELECT COUNT(*) FROM user_sessions")
        total_sessions = c.fetchone()[0]
        
        c.execute("""
            SELECT COUNT(*) FROM user_sessions 
            WHERE is_active = 1 AND datetime(expires_at) > datetime('now')
        """)
        active_sessions = c.fetchone()[0]
        
        # Content stats
        c.execute("SELECT COUNT(*) FROM tasks")
        total_tasks = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM projects")
        total_projects = c.fetchone()[0]
        
        # Count documents from file system
        from assistant_hub_gui.assistant_hub.config import DATA_DIR
        docs_dir = DATA_DIR / "chat_documents"
        total_documents = len(list(docs_dir.glob("*/metadata.json"))) if docs_dir.exists() else 0
        
        c.execute("SELECT COUNT(*) FROM document_operations")
        total_operations = c.fetchone()[0]
        
        return AdminStats(
            total_users=total_users,
            active_users=active_users,
            demo_users=demo_users,
            production_users=production_users,
            total_sessions=total_sessions,
            active_sessions=active_sessions,
            total_tasks=total_tasks,
            total_projects=total_projects,
            total_documents=total_documents,
            total_operations=total_operations,
            system_health="healthy"
        )


# ==================== User Management ====================

@router.get("/users", response_model=List[UserAdminResponse])
async def list_users(
    admin: Dict = Depends(require_admin),
    include_demo: bool = True,
    include_production: bool = True,
    active_only: bool = False,
    limit: int = 100,
    offset: int = 0
) -> List[UserAdminResponse]:
    """List all users with admin details."""
    with db_session() as conn:
        _ensure_admin_tables(conn)
        c = conn.cursor()
        
        conditions = []
        params = []
        
        if not include_demo:
            conditions.append("is_demo_user = 0")
        if not include_production:
            conditions.append("is_demo_user = 1")
        if active_only:
            conditions.append("is_active = 1")
        
        where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        
        c.execute(f"""
            SELECT u.*, 
                   (SELECT COUNT(*) FROM user_sessions s WHERE s.user_id = u.id AND s.is_active = 1) as session_count
            FROM users u
            {where}
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """, params + [limit, offset])
        
        users = []
        for row in c.fetchall():
            users.append(UserAdminResponse(
                id=row["id"],
                username=row["username"],
                email=row["email"],
                display_name=row["display_name"],
                is_admin=bool(row["is_admin"]),
                is_active=bool(row["is_active"]),
                is_demo_user=bool(row["is_demo_user"]),
                created_at=row["created_at"],
                last_login=row["last_login"],
                login_count=row["login_count"] or 0,
                session_count=row["session_count"]
            ))
        
        return users


@router.get("/users/{user_id}", response_model=UserAdminResponse)
async def get_user_details(
    user_id: str,
    admin: Dict = Depends(require_admin)
) -> UserAdminResponse:
    """Get detailed user information."""
    with db_session() as conn:
        _ensure_admin_tables(conn)
        c = conn.cursor()
        
        c.execute("""
            SELECT u.*, 
                   (SELECT COUNT(*) FROM user_sessions s WHERE s.user_id = u.id AND s.is_active = 1) as session_count
            FROM users u
            WHERE u.id = ?
        """, (user_id,))
        
        row = c.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="User not found")
        
        return UserAdminResponse(
            id=row["id"],
            username=row["username"],
            email=row["email"],
            display_name=row["display_name"],
            is_admin=bool(row["is_admin"]),
            is_active=bool(row["is_active"]),
            is_demo_user=bool(row["is_demo_user"]),
            created_at=row["created_at"],
            last_login=row["last_login"],
            login_count=row["login_count"] or 0,
            session_count=row["session_count"]
        )


@router.put("/users/{user_id}")
async def update_user(
    user_id: str,
    updates: UserAdminUpdate,
    admin: Dict = Depends(require_admin)
) -> Dict[str, str]:
    """Update user details (admin only)."""
    with db_session() as conn:
        _ensure_admin_tables(conn)
        c = conn.cursor()
        
        # Build update query
        set_parts = []
        params = []
        
        if updates.display_name is not None:
            set_parts.append("display_name = ?")
            params.append(updates.display_name)
        if updates.is_admin is not None:
            set_parts.append("is_admin = ?")
            params.append(1 if updates.is_admin else 0)
        if updates.is_active is not None:
            set_parts.append("is_active = ?")
            params.append(1 if updates.is_active else 0)
        if updates.is_demo_user is not None:
            set_parts.append("is_demo_user = ?")
            params.append(1 if updates.is_demo_user else 0)
        
        if not set_parts:
            return {"message": "No updates provided"}
        
        set_parts.append("updated_at = ?")
        params.append(_now_iso())
        params.append(user_id)
        
        c.execute(f"UPDATE users SET {', '.join(set_parts)} WHERE id = ?", params)
        
        if c.rowcount == 0:
            raise HTTPException(status_code=404, detail="User not found")
        
        conn.commit()
        
        log_system_event(conn, "ADMIN_ACTION", "admin_panel", "USER_UPDATE",
                        f"User {user_id} updated by admin", admin["id"])
        
        return {"message": "User updated successfully"}


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    admin: Dict = Depends(require_admin)
) -> Dict[str, str]:
    """Delete a user (admin only)."""
    if user_id == admin["id"]:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    
    with db_session() as conn:
        _ensure_admin_tables(conn)
        c = conn.cursor()
        
        c.execute("DELETE FROM users WHERE id = ?", (user_id,))
        
        if c.rowcount == 0:
            raise HTTPException(status_code=404, detail="User not found")
        
        conn.commit()
        
        log_system_event(conn, "ADMIN_ACTION", "admin_panel", "USER_DELETE",
                        f"User {user_id} deleted by admin", admin["id"])
        
        return {"message": "User deleted successfully"}


@router.get("/users/{user_id}/activity")
async def get_user_activity_admin(
    user_id: str,
    limit: int = 50,
    admin: Dict = Depends(require_admin)
) -> List[Dict[str, Any]]:
    """Get user activity log (admin view)."""
    with db_session() as conn:
        _ensure_admin_tables(conn)
        c = conn.cursor()
        
        c.execute("""
            SELECT * FROM user_activity_log
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (user_id, limit))
        
        return [dict(row) for row in c.fetchall()]


@router.get("/users/{user_id}/data-export")
async def export_user_data(
    user_id: str,
    admin: Dict = Depends(require_admin)
) -> Dict[str, Any]:
    """Export all data for a user (GDPR compliance)."""
    with db_session() as conn:
        _ensure_admin_tables(conn)
        c = conn.cursor()
        
        # Get user info
        c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = c.fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_data = dict(user)
        del user_data["password_hash"]
        del user_data["password_salt"]
        
        # Get sessions
        c.execute("SELECT * FROM user_sessions WHERE user_id = ?", (user_id,))
        sessions = [dict(row) for row in c.fetchall()]
        for s in sessions:
            del s["token"]  # Don't expose tokens
        
        # Get activity
        c.execute("SELECT * FROM user_activity_log WHERE user_id = ?", (user_id,))
        activity = [dict(row) for row in c.fetchall()]
        
        return {
            "user": user_data,
            "sessions": sessions,
            "activity": activity,
            "exported_at": _now_iso()
        }


# ==================== Database Schema ====================

@router.get("/schema/tables", response_model=List[TableSchema])
async def get_database_tables(admin: Dict = Depends(require_admin)) -> List[TableSchema]:
    """Get all database tables with schema information."""
    with db_session() as conn:
        _ensure_admin_tables(conn)
        c = conn.cursor()
        
        # Get all tables
        c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in c.fetchall()]
        
        result = []
        for table_name in tables:
            if table_name.startswith("sqlite_"):
                continue
            
            # Get columns
            c.execute(f"PRAGMA table_info({table_name})")
            columns = []
            for col in c.fetchall():
                columns.append({
                    "cid": col[0],
                    "name": col[1],
                    "type": col[2],
                    "notnull": bool(col[3]),
                    "default": col[4],
                    "pk": bool(col[5])
                })
            
            # Get row count
            c.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = c.fetchone()[0]
            
            # Get indexes
            c.execute(f"PRAGMA index_list({table_name})")
            indexes = []
            for idx in c.fetchall():
                indexes.append({
                    "name": idx[1],
                    "unique": bool(idx[2]),
                    "origin": idx[3] if len(idx) > 3 else "unknown"
                })
            
            result.append(TableSchema(
                name=table_name,
                columns=columns,
                row_count=row_count,
                indexes=indexes
            ))
        
        return result


@router.get("/schema/tables/{table_name}/data")
async def get_table_data(
    table_name: str,
    limit: int = Query(50, le=1000),
    offset: int = 0,
    admin: Dict = Depends(require_admin)
) -> Dict[str, Any]:
    """Get data from a specific table."""
    # Validate table name to prevent SQL injection
    with db_session() as conn:
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        if not c.fetchone():
            raise HTTPException(status_code=404, detail="Table not found")
        
        c.execute(f"SELECT COUNT(*) FROM {table_name}")
        total = c.fetchone()[0]
        
        c.execute(f"SELECT * FROM {table_name} LIMIT ? OFFSET ?", (limit, offset))
        rows = [dict(row) for row in c.fetchall()]
        
        return {
            "table": table_name,
            "total": total,
            "limit": limit,
            "offset": offset,
            "rows": rows
        }


# ==================== Unified Logging ====================

@router.get("/logs", response_model=List[SystemLog])
async def get_unified_logs(
    admin: Dict = Depends(require_admin),
    log_type: Optional[str] = None,
    source: Optional[str] = None,
    severity: Optional[str] = None,
    user_id: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    limit: int = Query(100, le=1000),
    offset: int = 0
) -> List[SystemLog]:
    """Get unified system logs with filtering."""
    with db_session() as conn:
        _ensure_admin_tables(conn)
        c = conn.cursor()
        
        conditions = []
        params = []
        
        if log_type:
            conditions.append("l.log_type = ?")
            params.append(log_type)
        if source:
            conditions.append("l.source = ?")
            params.append(source)
        if severity:
            conditions.append("l.severity = ?")
            params.append(severity)
        if user_id:
            conditions.append("l.user_id = ?")
            params.append(user_id)
        if start_time:
            conditions.append("l.timestamp >= ?")
            params.append(start_time)
        if end_time:
            conditions.append("l.timestamp <= ?")
            params.append(end_time)
        
        where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        
        c.execute(f"""
            SELECT l.*, u.username
            FROM system_logs l
            LEFT JOIN users u ON l.user_id = u.id
            {where}
            ORDER BY l.timestamp DESC, l.id DESC
            LIMIT ? OFFSET ?
        """, params + [limit, offset])
        
        logs = []
        for row in c.fetchall():
            logs.append(SystemLog(
                id=row["id"],
                timestamp=row["timestamp"],
                log_type=row["log_type"],
                source=row["source"],
                user_id=row["user_id"],
                username=row["username"],
                action=row["action"],
                details=row["details"],
                ip_address=row["ip_address"],
                severity=row["severity"]
            ))
        
        return logs


@router.get("/logs/types")
async def get_log_types(admin: Dict = Depends(require_admin)) -> List[str]:
    """Get all unique log types."""
    with db_session() as conn:
        _ensure_admin_tables(conn)
        c = conn.cursor()
        c.execute("SELECT DISTINCT log_type FROM system_logs ORDER BY log_type")
        return [row[0] for row in c.fetchall()]


@router.get("/logs/sources")
async def get_log_sources(admin: Dict = Depends(require_admin)) -> List[str]:
    """Get all unique log sources."""
    with db_session() as conn:
        _ensure_admin_tables(conn)
        c = conn.cursor()
        c.execute("SELECT DISTINCT source FROM system_logs ORDER BY source")
        return [row[0] for row in c.fetchall()]


# ==================== Service Monitoring ====================

@router.get("/services/health")
async def get_services_health(admin: Dict = Depends(require_admin)) -> List[Dict[str, Any]]:
    """Get health status of all tracked services."""
    with db_session() as conn:
        _ensure_admin_tables(conn)
        c = conn.cursor()
        
        c.execute("""
            SELECT * FROM service_health
            ORDER BY service_name
        """)
        
        return [dict(row) for row in c.fetchall()]


@router.get("/services/interactions")
async def get_service_interactions(
    admin: Dict = Depends(require_admin),
    source_service: Optional[str] = None,
    target_service: Optional[str] = None,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """Get service-to-service interaction log."""
    with db_session() as conn:
        _ensure_admin_tables(conn)
        c = conn.cursor()
        
        conditions = []
        params = []
        
        if source_service:
            conditions.append("source_service = ?")
            params.append(source_service)
        if target_service:
            conditions.append("target_service = ?")
            params.append(target_service)
        
        where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        
        c.execute(f"""
            SELECT * FROM service_interactions
            {where}
            ORDER BY timestamp DESC
            LIMIT ?
        """, params + [limit])
        
        return [dict(row) for row in c.fetchall()]


@router.get("/services/dependency-graph")
async def get_dependency_graph(admin: Dict = Depends(require_admin)) -> Dict[str, Any]:
    """Get service dependency graph data."""
    with db_session() as conn:
        _ensure_admin_tables(conn)
        c = conn.cursor()
        
        # Get unique services
        c.execute("""
            SELECT DISTINCT source_service as service FROM service_interactions
            UNION
            SELECT DISTINCT target_service as service FROM service_interactions
        """)
        nodes = [{"id": row[0], "label": row[0]} for row in c.fetchall()]
        
        # Get edges with counts
        c.execute("""
            SELECT source_service, target_service, 
                   COUNT(*) as interaction_count,
                   AVG(duration_ms) as avg_duration,
                   SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as error_count
            FROM service_interactions
            GROUP BY source_service, target_service
        """)
        edges = []
        for row in c.fetchall():
            edges.append({
                "source": row[0],
                "target": row[1],
                "count": row[2],
                "avg_duration_ms": row[3],
                "error_count": row[4]
            })
        
        return {"nodes": nodes, "edges": edges}


# ==================== Demo Data Management ====================

@router.post("/demo/seed")
async def seed_demo_data(admin: Dict = Depends(require_admin)) -> Dict[str, Any]:
    """Seed demo data for testing."""
    with db_session() as conn:
        _ensure_admin_tables(conn)
        c = conn.cursor()
        
        # Create demo users
        demo_users_created = 0
        demo_users = [
            ("demo_user_1", "demo1@example.com", "Demo User 1"),
            ("demo_user_2", "demo2@example.com", "Demo User 2"),
            ("demo_analyst", "analyst@example.com", "Demo Analyst"),
        ]
        
        for username, email, display_name in demo_users:
            c.execute("SELECT id FROM users WHERE username = ?", (username,))
            if c.fetchone():
                continue
            
            user_id = uuid4().hex
            password_hash, password_salt = _hash_password("demo123")
            c.execute("""
                INSERT INTO users (id, username, email, password_hash, password_salt,
                                  display_name, is_demo_user, created_at)
                VALUES (?, ?, ?, ?, ?, ?, 1, ?)
            """, (user_id, username, email, password_hash, password_salt, display_name, _now_iso()))
            demo_users_created += 1
        
        conn.commit()
        
        log_system_event(conn, "ADMIN_ACTION", "admin_panel", "SEED_DEMO_DATA",
                        f"Created {demo_users_created} demo users", admin["id"])
        
        return {
            "message": "Demo data seeded",
            "users_created": demo_users_created
        }


@router.delete("/demo/cleanup")
async def cleanup_demo_data(admin: Dict = Depends(require_admin)) -> Dict[str, Any]:
    """Remove all demo data."""
    with db_session() as conn:
        _ensure_admin_tables(conn)
        c = conn.cursor()
        
        # Delete demo users and their data
        c.execute("DELETE FROM user_activity_log WHERE user_id IN (SELECT id FROM users WHERE is_demo_user = 1)")
        c.execute("DELETE FROM user_sessions WHERE user_id IN (SELECT id FROM users WHERE is_demo_user = 1)")
        c.execute("DELETE FROM users WHERE is_demo_user = 1")
        
        deleted_count = c.rowcount
        conn.commit()
        
        log_system_event(conn, "ADMIN_ACTION", "admin_panel", "CLEANUP_DEMO_DATA",
                        f"Removed {deleted_count} demo users", admin["id"])
        
        return {
            "message": "Demo data cleaned up",
            "users_deleted": deleted_count
        }


# ==================== Admin Setup ====================

@router.post("/setup/create-admin")
async def create_initial_admin() -> Dict[str, Any]:
    """Create initial admin account if none exists."""
    with db_session() as conn:
        _ensure_admin_tables(conn)
        c = conn.cursor()
        
        # Check if any admin exists
        c.execute("SELECT COUNT(*) FROM users WHERE is_admin = 1")
        if c.fetchone()[0] > 0:
            raise HTTPException(status_code=400, detail="Admin account already exists")
        
        # Create admin account
        admin_id = uuid4().hex
        password_hash, password_salt = _hash_password("admin123")  # Default password - CHANGE THIS!
        
        c.execute("""
            INSERT INTO users (id, username, email, password_hash, password_salt,
                              display_name, is_admin, created_at)
            VALUES (?, ?, ?, ?, ?, ?, 1, ?)
        """, (admin_id, "admin", "admin@osdashboard.local", password_hash, password_salt,
              "System Administrator", _now_iso()))
        
        conn.commit()
        
        return {
            "message": "Admin account created",
            "username": "admin",
            "password": "admin123",
            "warning": "IMPORTANT: Change this password immediately after first login!"
        }
