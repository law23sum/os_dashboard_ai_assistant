"""Admin router (Django-like) for schema/table inspection.

Goals:
- Admin-only access
- Table/schema introspection for main + users DB
- Safe defaults: mask sensitive fields unless explicitly revealed
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from backend_api.auth import User, get_current_admin_user, get_user_db
from backend_api.db import db_session

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
    if database == "users":
        return get_user_db()
    if database == "main":
        return db_session()
    raise HTTPException(status_code=400, detail="Invalid database. Use 'main' or 'users'.")


@router.get("/dashboard")
async def dashboard(admin_user: User = Depends(get_current_admin_user)):
    """High-level admin dashboard counts."""
    stats: Dict[str, Any] = {}

    with get_user_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM users")
        stats["total_users"] = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM users WHERE is_active = 1")
        stats["active_users"] = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
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
        "admin_user": admin_user.username,
    }


@router.get("/tables")
async def list_tables(
    database: str = Query("main", description="Database to inspect: main or users"),
    admin_user: User = Depends(get_current_admin_user),
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
    admin_user: User = Depends(get_current_admin_user),
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
