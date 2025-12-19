"""Django-style admin interface for viewing all components, tables, schemas, and objects."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from backend_api.db import db_session
from backend_api.routers.auth import get_current_admin_user

router = APIRouter()


class TableSchema(BaseModel):
    name: str
    columns: List[Dict[str, Any]]
    row_count: int
    indexes: List[Dict[str, Any]]


class DatabaseStats(BaseModel):
    total_tables: int
    total_rows: int
    database_size_bytes: int
    last_updated: str


class UserStats(BaseModel):
    total_users: int
    active_users: int
    admin_users: int
    dummy_data_users: int
    production_users: int


class SystemOverview(BaseModel):
    database_stats: DatabaseStats
    user_stats: UserStats
    tables: List[TableSchema]
    recent_audit_logs: List[Dict[str, Any]]
    system_health: Dict[str, Any]


def get_table_schemas() -> List[TableSchema]:
    """Get schema information for all tables."""
    schemas = []
    
    with db_session() as conn:
        # Get all table names
        cursor = conn.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        for table_name in tables:
            # Get column information
            cursor = conn.execute(f"PRAGMA table_info({table_name})")
            columns = []
            for col in cursor.fetchall():
                columns.append({
                    "name": col[1],
                    "type": col[2],
                    "not_null": bool(col[3]),
                    "default_value": col[4],
                    "primary_key": bool(col[5])
                })
            
            # Get row count
            cursor = conn.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]
            
            # Get indexes
            cursor = conn.execute(f"PRAGMA index_list({table_name})")
            indexes = []
            for idx in cursor.fetchall():
                idx_name = idx[1]
                cursor_idx = conn.execute(f"PRAGMA index_info({idx_name})")
                idx_columns = [col[1] for col in cursor_idx.fetchall()]
                indexes.append({
                    "name": idx_name,
                    "unique": bool(idx[2]),
                    "columns": idx_columns
                })
            
            schemas.append(TableSchema(
                name=table_name,
                columns=columns,
                row_count=row_count,
                indexes=indexes
            ))
    
    return schemas


def get_database_stats() -> DatabaseStats:
    """Get database statistics."""
    with db_session() as conn:
        # Get table count
        cursor = conn.execute("""
            SELECT COUNT(*) FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
        """)
        total_tables = cursor.fetchone()[0]
        
        # Get total row count across all tables
        cursor = conn.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
        """)
        tables = [row[0] for row in cursor.fetchall()]
        total_rows = 0
        for table in tables:
            try:
                cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
                total_rows += cursor.fetchone()[0]
            except Exception:
                pass
        
        # Get database file size
        import os
        from assistant_hub_gui.assistant_hub.config import DB_PATH
        db_size = os.path.getsize(DB_PATH) if os.path.exists(DB_PATH) else 0
        
        return DatabaseStats(
            total_tables=total_tables,
            total_rows=total_rows,
            database_size_bytes=db_size,
            last_updated=datetime.utcnow().isoformat()
        )


def get_user_stats() -> UserStats:
    """Get user statistics."""
    with db_session() as conn:
        try:
            cursor = conn.execute("SELECT COUNT(*) FROM users")
            total_users = cursor.fetchone()[0]
            
            cursor = conn.execute("SELECT COUNT(*) FROM users WHERE is_active = 1")
            active_users = cursor.fetchone()[0]
            
            cursor = conn.execute("SELECT COUNT(*) FROM users WHERE is_admin = 1")
            admin_users = cursor.fetchone()[0]
            
            # Dummy data users (users with metadata indicating dummy/test data)
            cursor = conn.execute("""
                SELECT COUNT(*) FROM users 
                WHERE metadata LIKE '%"is_dummy": true%' OR metadata LIKE '%"is_test": true%'
            """)
            dummy_data_users = cursor.fetchone()[0]
            
            # Production users (active users not marked as dummy)
            cursor = conn.execute("""
                SELECT COUNT(*) FROM users 
                WHERE is_active = 1 
                AND (metadata NOT LIKE '%"is_dummy": true%' AND metadata NOT LIKE '%"is_test": true%')
            """)
            production_users = cursor.fetchone()[0]
        except Exception:
            # If users table doesn't exist yet
            return UserStats(
                total_users=0,
                active_users=0,
                admin_users=0,
                dummy_data_users=0,
                production_users=0
            )
    
    return UserStats(
        total_users=total_users,
        active_users=active_users,
        admin_users=admin_users,
        dummy_data_users=dummy_data_users,
        production_users=production_users
    )


@router.get("/overview", response_model=SystemOverview)
async def get_system_overview(
    current_user: dict = Depends(get_current_admin_user)
):
    """Get holistic system overview."""
    db_stats = get_database_stats()
    user_stats = get_user_stats()
    tables = get_table_schemas()
    
    # Get recent audit logs
    with db_session() as conn:
        try:
            cursor = conn.execute("""
                SELECT * FROM audit_logs 
                ORDER BY created_at DESC 
                LIMIT 50
            """)
            recent_logs = []
            for row in cursor.fetchall():
                recent_logs.append({
                    "id": row[0],
                    "user_id": row[1],
                    "action": row[2],
                    "resource_type": row[3],
                    "resource_id": row[4],
                    "details": json.loads(row[5] or "{}"),
                    "ip_address": row[6],
                    "user_agent": row[7],
                    "created_at": row[8]
                })
        except Exception:
            recent_logs = []
    
    # System health metrics
    system_health = {
        "database_connected": True,
        "api_status": "operational",
        "timestamp": datetime.utcnow().isoformat()
    }
    
    return SystemOverview(
        database_stats=db_stats,
        user_stats=user_stats,
        tables=tables,
        recent_audit_logs=recent_logs,
        system_health=system_health
    )


@router.get("/tables", response_model=List[TableSchema])
async def list_tables(
    current_user: dict = Depends(get_current_admin_user)
):
    """List all database tables with their schemas."""
    return get_table_schemas()


@router.get("/tables/{table_name}/data")
async def get_table_data(
    table_name: str,
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_admin_user)
):
    """Get data from a specific table."""
    # Sanitize table name to prevent SQL injection
    if not table_name.replace("_", "").replace("-", "").isalnum():
        raise HTTPException(status_code=400, detail="Invalid table name")
    
    with db_session() as conn:
        # Verify table exists
        cursor = conn.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name = ?
        """, (table_name,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Table not found")
        
        # Get total count
        cursor = conn.execute(f"SELECT COUNT(*) FROM {table_name}")
        total = cursor.fetchone()[0]
        
        # Get data
        cursor = conn.execute(f"SELECT * FROM {table_name} LIMIT ? OFFSET ?", (limit, offset))
        columns = [description[0] for description in cursor.description]
        rows = []
        for row in cursor.fetchall():
            row_dict = {}
            for i, col in enumerate(columns):
                value = row[i]
                # Handle JSON strings
                if isinstance(value, str) and (value.startswith("{") or value.startswith("[")):
                    try:
                        value = json.loads(value)
                    except Exception:
                        pass
                row_dict[col] = value
            rows.append(row_dict)
    
    return {
        "table": table_name,
        "total": total,
        "limit": limit,
        "offset": offset,
        "data": rows
    }


@router.get("/users", response_model=List[Dict[str, Any]])
async def list_users(
    include_dummy: bool = Query(True),
    include_production: bool = Query(True),
    current_user: dict = Depends(get_current_admin_user)
):
    """List all users with filtering options."""
    with db_session() as conn:
        try:
            query = "SELECT id, username, email, full_name, is_admin, is_active, created_at, last_login, metadata FROM users WHERE 1=1"
            params = []
            
            if not include_dummy:
                query += " AND (metadata NOT LIKE '%\"is_dummy\": true%' AND metadata NOT LIKE '%\"is_test\": true%')"
            
            if not include_production:
                query += " AND (metadata LIKE '%\"is_dummy\": true%' OR metadata LIKE '%\"is_test\": true%')"
            
            query += " ORDER BY created_at DESC"
            
            cursor = conn.execute(query, params)
            users = []
            for row in cursor.fetchall():
                metadata = {}
                try:
                    metadata = json.loads(row[8] or "{}")
                except Exception:
                    pass
                
                users.append({
                    "id": row[0],
                    "username": row[1],
                    "email": row[2],
                    "full_name": row[3],
                    "is_admin": bool(row[4]),
                    "is_active": bool(row[5]),
                    "created_at": row[6],
                    "last_login": row[7],
                    "is_dummy": metadata.get("is_dummy", False),
                    "is_test": metadata.get("is_test", False)
                })
            
            return users
        except Exception as e:
            return []


@router.get("/audit-logs")
async def get_audit_logs(
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0),
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    current_user: dict = Depends(get_current_admin_user)
):
    """Get audit logs with filtering."""
    with db_session() as conn:
        try:
            query = "SELECT * FROM audit_logs WHERE 1=1"
            params = []
            
            if user_id:
                query += " AND user_id = ?"
                params.append(user_id)
            
            if action:
                query += " AND action LIKE ?"
                params.append(f"%{action}%")
            
            query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            cursor = conn.execute(query, params)
            logs = []
            for row in cursor.fetchall():
                logs.append({
                    "id": row[0],
                    "user_id": row[1],
                    "action": row[2],
                    "resource_type": row[3],
                    "resource_id": row[4],
                    "details": json.loads(row[5] or "{}"),
                    "ip_address": row[6],
                    "user_agent": row[7],
                    "created_at": row[8]
                })
            
            return {"logs": logs, "limit": limit, "offset": offset}
        except Exception:
            return {"logs": [], "limit": limit, "offset": offset}


@router.get("/stats", response_model=Dict[str, Any])
async def get_detailed_stats(
    current_user: dict = Depends(get_current_admin_user)
):
    """Get detailed statistics for admin dashboard."""
    db_stats = get_database_stats()
    user_stats = get_user_stats()
    
    # Get counts for various entities
    with db_session() as conn:
        stats = {
            "database": db_stats.dict(),
            "users": user_stats.dict(),
            "entities": {}
        }
        
        # Count various entities
        entity_tables = {
            "tasks": "tasks",
            "projects": "projects",
            "chat_messages": "chat_messages",
            "document_operations": "document_operations",
            "agent_runs": "agent_runs"
        }
        
        for key, table in entity_tables.items():
            try:
                cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
                stats["entities"][key] = cursor.fetchone()[0]
            except Exception:
                stats["entities"][key] = 0
    
    return stats
