"""Lightweight API helpers for surfacing AI document operations.

These helpers provide a simple interface for connectors/daemons to report
activity so the GUI can display real-time progress while third-party files
are being updated.
"""
from typing import Dict, List, Optional

import sqlite3

from .db import (
    DocumentOperation,
    db_record_document_operation,
    db_update_document_operation_status,
    db_list_document_operations,
)


def record_ai_edit(
    conn: sqlite3.Connection,
    *,
    title: str,
    project_id: str,
    integration_type: str,
    external_id: str,
    operation: str,
    persona: str,
    external_company: Optional[str] = None,
    notes: str = "",
) -> int:
    """Register a new AI-driven document operation.

    This is intended to be called by connectors (OneNote/Word/Excel/PDF/etc.)
    whenever an automated edit begins so the dashboard can visualize progress.
    """

    return db_record_document_operation(
        conn,
        title=title,
        project_id=project_id,
        integration_type=integration_type,
        external_id=external_id,
        operation=operation,
        status="running",
        persona=persona,
        external_company=external_company,
        notes=notes,
    )


def mark_ai_edit_complete(
    conn: sqlite3.Connection,
    operation_id: int,
    *,
    version_tag: Optional[str] = None,
    diff_path: Optional[str] = None,
    external_company: Optional[str] = None,
    notes: Optional[str] = None,
    failed: bool = False,
):
    """Update the status of a recorded operation and close it out."""

    db_update_document_operation_status(
        conn,
        operation_id,
        status="failed" if failed else "succeeded",
        diff_path=diff_path,
        version_tag=version_tag,
        external_company=external_company,
        notes=notes,
        mark_complete=True,
    )


def get_operation_feed(
    conn: sqlite3.Connection, *, status: Optional[str] = None, integration_type: Optional[str] = None, limit: int = 50
) -> List[DocumentOperation]:
    """Fetch a list of recent operations for API/GUI consumption."""

    return db_list_document_operations(conn, limit=limit, status=status, integration_type=integration_type)


def summarize_operation_counts(conn: sqlite3.Connection) -> Dict[str, int]:
    """Aggregate operation counts by status for quick badges in the GUI."""

    counts: Dict[str, int] = {"queued": 0, "running": 0, "succeeded": 0, "failed": 0, "needs_review": 0}
    operations = db_list_document_operations(conn, limit=250)
    for op in operations:
        if op.status in counts:
            counts[op.status] += 1
    return counts
