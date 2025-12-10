"""Document operations (AI governance) API router."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
from pathlib import Path
import sys

parent_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_dir))

from assistant_hub_gui.assistant_hub.db import (
    DocumentOperation,
    db_record_document_operation,
    db_update_document_operation_status,
    db_list_document_operations,
    OPERATION_STATUS_OPTIONS,
)
from assistant_hub_gui.assistant_hub.api_bridge import summarize_operation_counts
from backend_api.db import db_session

router = APIRouter()


class DocumentOperationCreate(BaseModel):
    title: str
    project_id: str
    integration_type: str
    external_id: str
    operation: str
    persona: str = "AIC"
    status: str = "queued"
    version_tag: Optional[str] = None
    diff_path: Optional[str] = None
    external_company: Optional[str] = None
    notes: Optional[str] = ""


class DocumentOperationUpdate(BaseModel):
    status: Optional[str] = None
    version_tag: Optional[str] = None
    diff_path: Optional[str] = None
    external_company: Optional[str] = None
    notes: Optional[str] = None
    mark_complete: bool = False


class DocumentOperationResponse(BaseModel):
    id: int
    title: str
    project_id: str
    integration_type: str
    external_id: str
    operation: str
    status: str
    persona: str
    version_tag: Optional[str]
    diff_path: Optional[str]
    external_company: Optional[str]
    started_at: str
    completed_at: Optional[str]
    notes: str

    class Config:
        from_attributes = True


class DocumentOperationSummary(BaseModel):
    queued: int
    running: int
    succeeded: int
    failed: int
    needs_review: int


def _fetch_operation(db, operation_id: int) -> DocumentOperation:
    cursor = db.execute("SELECT * FROM document_operations WHERE id = ?", (operation_id,))
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Operation not found")
    return DocumentOperation(
        id=row["id"],
        title=row["title"],
        project_id=row["project_id"],
        integration_type=row["integration_type"],
        external_id=row["external_id"],
        operation=row["operation"],
        status=row["status"],
        persona=row["persona"],
        version_tag=row["version_tag"],
        diff_path=row["diff_path"],
        external_company=row["external_company"],
        started_at=row["started_at"],
        completed_at=row["completed_at"],
        notes=row["notes"] or "",
    )


@router.get("/", response_model=List[DocumentOperationResponse])
async def list_document_operations(
    limit: int = 50,
    status: Optional[str] = None,
    integration_type: Optional[str] = None,
):
    """Return recent document operations for dashboards and governance feeds."""
    if status and status not in OPERATION_STATUS_OPTIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of {OPERATION_STATUS_OPTIONS}",
        )
    with db_session() as db:
        operations = db_list_document_operations(
            db, limit=limit, status=status, integration_type=integration_type
        )
    return operations


@router.post("/", response_model=DocumentOperationResponse, status_code=201)
async def create_document_operation(operation: DocumentOperationCreate):
    """Record a new document operation initiated by an integration/daemon."""
    if operation.status and operation.status not in OPERATION_STATUS_OPTIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of {OPERATION_STATUS_OPTIONS}",
        )
    with db_session() as db:
        op_id = db_record_document_operation(
            db,
            title=operation.title,
            project_id=operation.project_id,
            integration_type=operation.integration_type,
            external_id=operation.external_id,
            operation=operation.operation,
            status=operation.status,
            persona=operation.persona,
            version_tag=operation.version_tag,
            diff_path=operation.diff_path,
            external_company=operation.external_company,
            notes=operation.notes or "",
        )
        return _fetch_operation(db, op_id)


@router.patch("/{operation_id}", response_model=DocumentOperationResponse)
async def update_document_operation(
    operation_id: int,
    operation_update: DocumentOperationUpdate,
):
    """Update status/metadata for an existing document operation."""
    update_dict = operation_update.model_dump(exclude_unset=True)
    status = update_dict.get("status")
    if status and status not in OPERATION_STATUS_OPTIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of {OPERATION_STATUS_OPTIONS}",
        )
    with db_session() as db:
        db_update_document_operation_status(
            db,
            operation_id,
            status=status,
            version_tag=update_dict.get("version_tag"),
            diff_path=update_dict.get("diff_path"),
            external_company=update_dict.get("external_company"),
            notes=update_dict.get("notes"),
            mark_complete=update_dict.get("mark_complete", False),
        )
        return _fetch_operation(db, operation_id)


@router.get("/summary", response_model=DocumentOperationSummary)
async def get_operation_summary():
    """Return aggregate counts of operations by status."""
    with db_session() as db:
        counts = summarize_operation_counts(db)
    return counts
