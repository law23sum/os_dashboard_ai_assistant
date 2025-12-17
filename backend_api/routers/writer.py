"""Writer workspace API router."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from assistant_hub.writer_workspace import WriterWorkspaceState

router = APIRouter()

_WRITER_STATE = WriterWorkspaceState()


class CreateDocumentRequest(BaseModel):
    title: str
    doc_type: str = "Article"
    summary: Optional[str] = None
    theme: Optional[str] = None


class SaveDocumentRequest(BaseModel):
    content: str


class GenerateNarrativeRequest(BaseModel):
    doc_type: str = "Article"
    theme: str = "adventure"
    genre: str = "Creative"
    title: str = "Untitled Narrative"


class CanonEntryRequest(BaseModel):
    category: str
    title: str
    description: str
    meta: Optional[str] = None


class PipelineEntryRequest(BaseModel):
    title: str
    summary: str
    target: str
    status: str = "Draft"


@router.get("/snapshot")
async def get_writer_snapshot():
    """Return the full writer workspace snapshot for React clients."""
    return _WRITER_STATE.snapshot()


@router.post("/documents")
async def create_writer_document(request: CreateDocumentRequest):
    """Create a new writer document."""
    doc = _WRITER_STATE.create_document(
        request.title,
        request.doc_type,
        summary=request.summary,
        theme=request.theme,
    )
    return {"document": doc, "workspace": _WRITER_STATE.snapshot()}


@router.get("/documents/{document_id}")
async def get_writer_document(document_id: str):
    """Fetch a stored document."""
    try:
        return _WRITER_STATE.get_document(document_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Document not found")


@router.put("/documents/{document_id}")
async def save_writer_document(document_id: str, request: SaveDocumentRequest):
    """Persist edits to an existing document."""
    try:
        document = _WRITER_STATE.save_document(document_id, request.content)
    except KeyError:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"document": document, "workspace": _WRITER_STATE.snapshot()}


@router.post("/generate")
async def generate_writer_narrative(request: GenerateNarrativeRequest):
    """Generate a narrative draft template."""
    content = _WRITER_STATE.generate_narrative(
        request.doc_type, request.theme, request.genre, request.title
    )
    return {"content": content}


@router.post("/canon")
async def add_canon_entry(request: CanonEntryRequest):
    """Add canon metadata as outlined in Writer Workspace spec."""
    entry = _WRITER_STATE.add_canon_entry(
        request.category,
        request.title,
        request.description,
        meta=request.meta,
    )
    return {"entry": entry, "workspace": _WRITER_STATE.snapshot()}


@router.post("/pipeline")
async def queue_pipeline_entry(request: PipelineEntryRequest):
    """Queue a publishing pipeline entry."""
    entry = _WRITER_STATE.queue_pipeline_entry(
        request.title, request.summary, request.target, request.status
    )
    return {"entry": entry, "workspace": _WRITER_STATE.snapshot()}


@router.delete("/documents/{document_id}")
async def delete_writer_document(document_id: str):
    """Delete a writer document."""
    deleted = _WRITER_STATE.delete_document(document_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"success": True, "workspace": _WRITER_STATE.snapshot()}
