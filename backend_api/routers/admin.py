"""Admin router - Django-style admin panel for managing all system components.

Provides comprehensive visibility into tables, schemas, objects, users, and system state.
These endpoints are protected by JWT admin role.

Goals:
- Admin-only access
- Table/schema introspection for main + users DB
- Safe defaults: mask sensitive fields unless explicitly revealed
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from backend_api.db import db_session
from backend_api.deps import require_admin
from backend_api.security import AuthUser

router = APIRouter()

SENSITIVE_FIELD_HINTS = {
    "password",
    "hashed_password",
    "password_hash",
    "secret",
    "token",
    "refresh_token",
    "access_token",
    "api_key",
    "key",
    "authorization",
}


def _is_sensitive_field(name: str) -> bool:
    n = (name or "").lower()
    return any(hint in n for hint in SENSITIVE_FIELD_HINTS)


def _mask_value(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, (int, float, bool)):
        return value
    s = str(value)
    if len(s) <= 4:
        return "****"
    return s[:2] + "***" + s[-2:]


def _connect(database: str):
    if database in {"users", "main"}:
        return db_session()
    raise HTTPException(status_code=400, detail="Invalid database. Use 'main' or 'users'.")



class ColumnInfo(BaseModel):
    name: str
    type: str
    notnull: bool = False
    pk: bool = False
    default: Optional[str] = None


class TableInfo(BaseModel):
    name: str
    columns: List[ColumnInfo] = Field(default_factory=list)
    row_count: int = 0


class SchemaResponse(BaseModel):
    tables: List[TableInfo]


def _list_tables(conn) -> List[str]:
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
    ).fetchall()
    return [row["name"] for row in rows]


def _table_columns(conn, table: str) -> List[ColumnInfo]:
    try:
        rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid table: {table}") from exc
    cols: List[ColumnInfo] = []
    for r in rows:
        cols.append(
            ColumnInfo(
                name=r["name"],
                type=r["type"] or "",
                notnull=bool(r["notnull"]),
                pk=bool(r["pk"]),
                default=r["dflt_value"],
            )
        )
    return cols


def _row_count(conn, table: str) -> int:
    try:
        row = conn.execute(f"SELECT COUNT(*) as count FROM {table}").fetchone()
        return int(row["count"] if row else 0)
    except Exception:
        return 0


@router.get("/admin/schema", response_model=SchemaResponse)
async def admin_schema(_: AuthUser = Depends(require_admin)) -> SchemaResponse:
    with db_session() as db:
        tables = _list_tables(db)
        payload: List[TableInfo] = []
        for name in tables:
            payload.append(
                TableInfo(
                    name=name,
                    columns=_table_columns(db, name),
                    row_count=_row_count(db, name),
                )
            )
    return SchemaResponse(tables=payload)


class TableRowsResponse(BaseModel):
    table: str
    columns: List[str]
    rows: List[Dict[str, Any]]
    limit: int
    offset: int
    total: int


@router.get("/admin/table/{table}", response_model=TableRowsResponse)
async def admin_table_rows(
    table: str,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    environment: Optional[str] = Query(None, description="Optional: demo|prod"),
    _: AuthUser = Depends(require_admin),
) -> TableRowsResponse:
    with db_session() as db:
        tables = set(_list_tables(db))
        if table not in tables:
            raise HTTPException(status_code=404, detail="Table not found")

        where = ""
        params: List[Any] = []
        # Provide a convenient environment filter when tables have that column.
        cols = [c.name for c in _table_columns(db, table)]
        if environment and "environment" in cols:
            where = "WHERE environment = ?"
            params.append(environment)

        total_row = db.execute(f"SELECT COUNT(*) as count FROM {table} {where}", params).fetchone()
        total = int(total_row["count"] if total_row else 0)

        params2 = list(params)
        params2.extend([limit, offset])
        cursor = db.execute(f"SELECT * FROM {table} {where} LIMIT ? OFFSET ?", params2)
        rows_raw = cursor.fetchall()
        columns = [d[0] for d in cursor.description] if cursor.description else []
        rows: List[Dict[str, Any]] = []
        for r in rows_raw:
            record = {col: r[col] for col in columns}
            rows.append(record)

    return TableRowsResponse(
        table=table,
        columns=columns,
        rows=rows,
        limit=limit,
        offset=offset,
        total=total,
    )


class UserAdminRow(BaseModel):
    id: str
    email: str
    display_name: str
    is_admin: bool
    environment: str
    disabled: bool
    created_at: str
    last_login: Optional[str] = None


@router.get("/admin/users", response_model=List[UserAdminRow])
async def admin_users(
    environment: Optional[str] = Query(None, description="demo|prod"),
    _: AuthUser = Depends(require_admin),
):
    with db_session() as db:
        query = "SELECT id, email, display_name, is_admin, environment, disabled, created_at, last_login FROM users WHERE 1=1"
        params: List[Any] = []
        if environment:
            query += " AND environment = ?"
            params.append(environment)
        query += " ORDER BY datetime(created_at) DESC"
        rows = db.execute(query, params).fetchall()
    return [
        UserAdminRow(
            id=r["id"],
            email=r["email"],
            display_name=r["display_name"] or "",
            is_admin=bool(r["is_admin"] or 0),
            environment=r["environment"] or "demo",
            disabled=bool(r["disabled"] or 0),
            created_at=r["created_at"],
            last_login=r["last_login"],
        )
        for r in rows
    ]

@router.get("/admin/dashboard")
async def admin_dashboard(admin_user: AuthUser = Depends(require_admin)):
    """
    Get comprehensive admin dashboard with system overview.
    """
    stats = {}
    
    # User statistics
    with db_session() as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM users")
        stats["total_users"] = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM users WHERE disabled = 0")
        stats["active_users"] = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM users WHERE is_admin = 1")
        stats["admin_users"] = cur.fetchone()[0]

        # Activity table may not exist in older schemas
        try:
            cur.execute("SELECT COUNT(*) FROM user_activity")
            stats["total_activities"] = cur.fetchone()[0]
        except Exception:
            stats["total_activities"] = 0

    with db_session() as conn:
        cur = conn.cursor()
        for table in ("tasks", "projects", "chat_messages", "documents"):
            try:
                cur.execute(f"SELECT COUNT(*) FROM {table}")
                stats[f"total_{table}"] = cur.fetchone()[0]
            except Exception:
                stats[f"total_{table}"] = 0

    return {
        "dashboard": {
            "total_users": stats.get("total_users", 0),
            "active_users": stats.get("active_users", 0),
            "admin_users": stats.get("admin_users", 0),
            "total_activities": stats.get("total_activities", 0),
            "total_tasks": stats.get("total_tasks", 0),
            "total_projects": stats.get("total_projects", 0),
            "total_chat_messages": stats.get("total_chat_messages", 0),
            "total_documents": stats.get("total_documents", 0),
        },
        "timestamp": datetime.utcnow().isoformat(),
        "admin_user": admin_user.display_name or admin_user.email,
    }


@router.get("/tables")
async def list_tables(
    database: str = Query("main", description="Database to inspect: main or users"),
    _: AuthUser = Depends(require_admin),
):
    """List tables with column info and row counts."""
    with _connect(database) as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
            """
        )
        table_names = [row[0] for row in cur.fetchall()]

        tables: List[Dict[str, Any]] = []
        for name in table_names:
            # row count
            try:
                cur.execute(f"SELECT COUNT(*) FROM {name}")
                row_count = cur.fetchone()[0]
            except Exception:
                row_count = 0

            # schema
            cur.execute(f"PRAGMA table_info({name})")
            cols = []
            for col in cur.fetchall():
                # cid, name, type, notnull, dflt_value, pk
                cols.append(
                    {
                        "name": col[1],
                        "type": col[2],
                        "not_null": bool(col[3]),
                        "primary_key": bool(col[5]),
                        "sensitive": _is_sensitive_field(col[1]),
                    }
                )

            tables.append({"name": name, "row_count": row_count, "columns": cols})

    return {"database": database, "tables": tables}


@router.get("/tables/{table_name}/data")
async def table_data(
    table_name: str,
    database: str = Query("main"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=250),
    reveal_sensitive: bool = Query(False, description="Reveal sensitive fields (admin-only, explicit)."),
    _: AuthUser = Depends(require_admin),
):
    """Paginated table data with optional masking."""
    if not table_name.replace("_", "").isalnum():
        raise HTTPException(status_code=400, detail="Invalid table name")

    offset = (page - 1) * page_size

    with _connect(database) as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type='table' AND name = ?
            """,
            (table_name,),
        )
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Table not found")

        cur.execute(f"SELECT COUNT(*) FROM {table_name}")
        total_rows = cur.fetchone()[0]

        cur.execute(f"SELECT * FROM {table_name} LIMIT ? OFFSET ?", (page_size, offset))
        columns = [d[0] for d in cur.description]
        rows: List[Dict[str, Any]] = []
        for row in cur.fetchall():
            row_dict: Dict[str, Any] = {}
            for idx, col in enumerate(columns):
                val = row[idx]
                if not reveal_sensitive and _is_sensitive_field(col):
                    val = _mask_value(val)
                row_dict[col] = val
            rows.append(row_dict)

    total_pages = max(1, (total_rows + page_size - 1) // page_size)
    return {
        "table": table_name,
        "database": database,
        "page": page,
        "page_size": page_size,
        "total_rows": total_rows,
        "total_pages": total_pages,
        "rows": rows,
    }


@router.get("/users", response_model=List[Dict[str, Any]])
async def list_users(
    include_dummy: bool = Query(True),
    include_production: bool = Query(True),
    _: AuthUser = Depends(require_admin),
):
    """List all users with filtering options."""
    with db_session() as conn:
        try:
            query = "SELECT id, username, email, display_name, is_admin, disabled, created_at, last_login, environment FROM users WHERE 1=1"
            params = []
            
            if not include_dummy:
                query += " AND environment != 'demo'"
            
            if not include_production:
                query += " AND environment != 'prod'"
            
            query += " ORDER BY created_at DESC"
            
            cursor = conn.execute(query, params)
            users = []
            for row in cursor.fetchall():
                username = row[1] or (row[2].split("@", 1)[0] if row[2] else "")
                users.append({
                    "id": row[0],
                    "username": username,
                    "email": row[2],
                    "full_name": row[3],
                    "display_name": row[3],
                    "is_admin": bool(row[4]),
                    "is_active": not bool(row[5]),
                    "created_at": row[6],
                    "last_login": row[7],
                    "is_dummy": (row[8] or "") == "demo",
                    "is_test": False,
                    "environment": row[8] or "demo",
                })
            
            return users
        except Exception as e:
            return []


@router.get("/audit-logs")
async def get_audit_logs(
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0),
    user_id: Optional[str] = None,
    action: Optional[str] = None,
    _: AuthUser = Depends(require_admin),
):
    """Get audit events with filtering."""
    with db_session() as conn:
        try:
            params = []
            query = """
                SELECT id, user_id, event_type, object_type, object_id, ip, user_agent, created_at, metadata_json
                FROM audit_events
                WHERE 1=1
            """
            if user_id:
                query += " AND user_id = ?"
                params.append(user_id)
            if action:
                query += " AND event_type LIKE ?"
                params.append(f"%{action}%")
            query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])

            cursor = conn.execute(query, params)
            logs = []
            for row in cursor.fetchall():
                metadata = {}
                try:
                    metadata = json.loads(row["metadata_json"] or "{}")
                except Exception:
                    metadata = {}
                logs.append({
                    "id": row["id"],
                    "user_id": row["user_id"],
                    "action": row["event_type"],
                    "resource_type": row["object_type"],
                    "resource_id": row["object_id"],
                    "ip_address": row["ip"],
                    "user_agent": row["user_agent"],
                    "created_at": row["created_at"],
                    "metadata": metadata,
                })
            return {"logs": logs, "limit": limit, "offset": offset}
        except sqlite3.OperationalError:
            return {"logs": [], "limit": limit, "offset": offset}
        except Exception:
            return {"logs": [], "limit": limit, "offset": offset}


@router.get("/stats", response_model=Dict[str, Any])
async def get_detailed_stats(
    _: AuthUser = Depends(require_admin),
):
    """Get detailed statistics for admin dashboard."""
    stats: Dict[str, Any] = {
        "database": {},
        "users": {},
        "entities": {}
    }
    
    # Get counts for various entities
    with db_session() as conn:
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
