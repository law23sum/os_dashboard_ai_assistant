"""
Admin router - Django-style admin panel for managing all system components.
Provides comprehensive visibility into tables, schemas, objects, users, and system state.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Any, Optional
from datetime import datetime
import sqlite3
import json
from pathlib import Path

from backend_api.auth import User, get_current_admin_user, get_user_db
from backend_api.db import db_session

router = APIRouter()


@router.get("/admin/dashboard")
async def admin_dashboard(admin_user: User = Depends(get_current_admin_user)):
    """
    Get comprehensive admin dashboard with system overview.
    """
    stats = {}
    
    # User statistics
    with get_user_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM users")
        stats["total_users"] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE is_active = 1")
        stats["active_users"] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
        stats["admin_users"] = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM users 
            WHERE last_login >= datetime('now', '-24 hours')
        """)
        stats["active_24h"] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM user_activity")
        stats["total_activities"] = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM user_activity 
            WHERE timestamp >= datetime('now', '-24 hours')
        """)
        stats["activities_24h"] = cursor.fetchone()[0]
    
    # Application data statistics
    with db_session() as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM tasks")
        stats["total_tasks"] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM projects")
        stats["total_projects"] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM chat_messages")
        stats["total_chat_messages"] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM documents")
        stats["total_documents"] = cursor.fetchone()[0]
    
    return {
        "dashboard": stats,
        "timestamp": datetime.utcnow().isoformat(),
        "admin_user": admin_user.username
    }


@router.get("/admin/tables")
async def list_tables(
    database: str = Query("main", description="Database to inspect: main, users"),
    admin_user: User = Depends(get_current_admin_user)
):
    """
    List all tables in the specified database with schema information.
    """
    if database == "users":
        conn_context = get_user_db()
    else:
        conn_context = db_session()
    
    with conn_context as conn:
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("""
            SELECT name, sql FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """)
        
        tables = []
        for row in cursor.fetchall():
            table_name = row[0]
            table_sql = row[1]
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]
            
            # Get column information
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = []
            for col_row in cursor.fetchall():
                columns.append({
                    "cid": col_row[0],
                    "name": col_row[1],
                    "type": col_row[2],
                    "not_null": bool(col_row[3]),
                    "default_value": col_row[4],
                    "primary_key": bool(col_row[5])
                })
            
            tables.append({
                "name": table_name,
                "row_count": row_count,
                "columns": columns,
                "schema": table_sql
            })
        
        return {
            "database": database,
            "tables": tables,
            "total_tables": len(tables)
        }


@router.get("/admin/tables/{table_name}/data")
async def get_table_data(
    table_name: str,
    database: str = Query("main", description="Database: main, users"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    admin_user: User = Depends(get_current_admin_user)
):
    """
    Get paginated data from a specific table.
    """
    if database == "users":
        conn_context = get_user_db()
    else:
        conn_context = db_session()
    
    with conn_context as conn:
        cursor = conn.cursor()
        
        # Verify table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name = ?
        """, (table_name,))
        
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found")
        
        # Get total count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        total_rows = cursor.fetchone()[0]
        
        # Get paginated data
        offset = (page - 1) * page_size
        cursor.execute(f"""
            SELECT * FROM {table_name}
            LIMIT ? OFFSET ?
        """, (page_size, offset))
        
        # Convert rows to dictionaries
        columns = [description[0] for description in cursor.description]
        rows = []
        for row in cursor.fetchall():
            rows.append(dict(zip(columns, row)))
        
        return {
            "table": table_name,
            "database": database,
            "page": page,
            "page_size": page_size,
            "total_rows": total_rows,
            "total_pages": (total_rows + page_size - 1) // page_size,
            "rows": rows
        }


@router.get("/admin/tables/{table_name}/schema")
async def get_table_schema(
    table_name: str,
    database: str = Query("main"),
    admin_user: User = Depends(get_current_admin_user)
):
    """
    Get detailed schema information for a table.
    """
    if database == "users":
        conn_context = get_user_db()
    else:
        conn_context = db_session()
    
    with conn_context as conn:
        cursor = conn.cursor()
        
        # Get table schema
        cursor.execute("""
            SELECT sql FROM sqlite_master 
            WHERE type='table' AND name = ?
        """, (table_name,))
        
        result = cursor.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found")
        
        schema_sql = result[0]
        
        # Get column details
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = []
        for row in cursor.fetchall():
            columns.append({
                "cid": row[0],
                "name": row[1],
                "type": row[2],
                "not_null": bool(row[3]),
                "default_value": row[4],
                "primary_key": bool(row[5])
            })
        
        # Get foreign keys
        cursor.execute(f"PRAGMA foreign_key_list({table_name})")
        foreign_keys = []
        for row in cursor.fetchall():
            foreign_keys.append({
                "id": row[0],
                "seq": row[1],
                "table": row[2],
                "from": row[3],
                "to": row[4],
                "on_update": row[5],
                "on_delete": row[6],
                "match": row[7]
            })
        
        # Get indexes
        cursor.execute(f"PRAGMA index_list({table_name})")
        indexes = []
        for row in cursor.fetchall():
            indexes.append({
                "seq": row[0],
                "name": row[1],
                "unique": bool(row[2]),
                "origin": row[3],
                "partial": bool(row[4])
            })
        
        return {
            "table": table_name,
            "database": database,
            "schema_sql": schema_sql,
            "columns": columns,
            "foreign_keys": foreign_keys,
            "indexes": indexes
        }


@router.get("/admin/users/stats")
async def get_user_statistics(admin_user: User = Depends(get_current_admin_user)):
    """
    Get detailed user statistics and analytics.
    """
    with get_user_db() as conn:
        cursor = conn.cursor()
        
        # User counts by role
        cursor.execute("""
            SELECT role, COUNT(*) as count
            FROM users
            GROUP BY role
        """)
        users_by_role = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Active vs inactive users
        cursor.execute("""
            SELECT is_active, COUNT(*) as count
            FROM users
            GROUP BY is_active
        """)
        users_by_status = {
            "active" if row[0] else "inactive": row[1] 
            for row in cursor.fetchall()
        }
        
        # Recent signups (last 7 days)
        cursor.execute("""
            SELECT DATE(created_at) as date, COUNT(*) as count
            FROM users
            WHERE created_at >= datetime('now', '-7 days')
            GROUP BY DATE(created_at)
            ORDER BY date DESC
        """)
        recent_signups = [{"date": row[0], "count": row[1]} for row in cursor.fetchall()]
        
        # Most active users (by activity count)
        cursor.execute("""
            SELECT u.username, u.email, COUNT(ua.id) as activity_count
            FROM users u
            LEFT JOIN user_activity ua ON u.id = ua.user_id
            GROUP BY u.id
            ORDER BY activity_count DESC
            LIMIT 10
        """)
        most_active = [
            {"username": row[0], "email": row[1], "activity_count": row[2]}
            for row in cursor.fetchall()
        ]
        
        # Activity breakdown
        cursor.execute("""
            SELECT action, COUNT(*) as count
            FROM user_activity
            GROUP BY action
            ORDER BY count DESC
        """)
        activity_breakdown = {row[0]: row[1] for row in cursor.fetchall()}
        
        return {
            "users_by_role": users_by_role,
            "users_by_status": users_by_status,
            "recent_signups": recent_signups,
            "most_active_users": most_active,
            "activity_breakdown": activity_breakdown
        }


@router.get("/admin/system/info")
async def get_system_info(admin_user: User = Depends(get_current_admin_user)):
    """
    Get comprehensive system information.
    """
    import sys
    import platform
    import psutil
    
    # System info
    system_info = {
        "platform": platform.platform(),
        "python_version": sys.version,
        "cpu_count": psutil.cpu_count(),
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory": {
            "total": psutil.virtual_memory().total,
            "available": psutil.virtual_memory().available,
            "percent": psutil.virtual_memory().percent,
            "used": psutil.virtual_memory().used
        },
        "disk": {
            "total": psutil.disk_usage('/').total,
            "used": psutil.disk_usage('/').used,
            "free": psutil.disk_usage('/').free,
            "percent": psutil.disk_usage('/').percent
        }
    }
    
    # Database info
    db_info = {}
    
    # Main database
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
        db_info["main_db_size"] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
        db_info["main_db_tables"] = cursor.fetchone()[0]
    
    # Users database
    with get_user_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
        db_info["users_db_size"] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
        db_info["users_db_tables"] = cursor.fetchone()[0]
    
    return {
        "system": system_info,
        "databases": db_info,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.post("/admin/query")
async def execute_query(
    query_data: dict,
    admin_user: User = Depends(get_current_admin_user)
):
    """
    Execute a custom SQL query (admin only - use with caution).
    
    Supports SELECT queries only for safety.
    """
    query = query_data.get("query", "").strip()
    database = query_data.get("database", "main")
    
    if not query:
        raise HTTPException(status_code=400, detail="Query is required")
    
    # Only allow SELECT queries for safety
    if not query.upper().startswith("SELECT"):
        raise HTTPException(
            status_code=400,
            detail="Only SELECT queries are allowed through this endpoint"
        )
    
    if database == "users":
        conn_context = get_user_db()
    else:
        conn_context = db_session()
    
    try:
        with conn_context as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            
            columns = [description[0] for description in cursor.description] if cursor.description else []
            rows = []
            for row in cursor.fetchall():
                rows.append(dict(zip(columns, row)))
            
            return {
                "success": True,
                "columns": columns,
                "rows": rows,
                "row_count": len(rows)
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/admin/data/export")
async def export_data(
    table: str = Query(..., description="Table name to export"),
    database: str = Query("main"),
    format: str = Query("json", description="Export format: json or csv"),
    admin_user: User = Depends(get_current_admin_user)
):
    """
    Export table data in JSON or CSV format.
    """
    from fastapi.responses import StreamingResponse
    import io
    import csv
    
    if database == "users":
        conn_context = get_user_db()
    else:
        conn_context = db_session()
    
    with conn_context as conn:
        cursor = conn.cursor()
        
        # Verify table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name = ?
        """, (table,))
        
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail=f"Table '{table}' not found")
        
        # Get all data
        cursor.execute(f"SELECT * FROM {table}")
        columns = [description[0] for description in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        if format == "csv":
            # Create CSV
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=columns)
            writer.writeheader()
            writer.writerows(rows)
            
            return StreamingResponse(
                io.BytesIO(output.getvalue().encode()),
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename={table}.csv"}
            )
        else:
            # Return JSON
            return {
                "table": table,
                "database": database,
                "rows": rows,
                "count": len(rows)
            }
