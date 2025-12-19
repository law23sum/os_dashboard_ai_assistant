"""Admin endpoints (Django-admin-like schema + data inspection).

These endpoints are protected by JWT admin role.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from backend_api.db import db_session
from backend_api.deps import require_admin
from backend_api.security import AuthUser

router = APIRouter()


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

