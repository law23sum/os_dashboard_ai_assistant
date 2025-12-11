"""Writer workspace API router."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any

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
    return doc


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
        return _WRITER_STATE.save_document(document_id, request.content)
    except KeyError:
        raise HTTPException(status_code=404, detail="Document not found")


@router.post("/generate")
async def generate_writer_narrative(request: GenerateNarrativeRequest):
    """Generate a narrative draft template."""
    content = _WRITER_STATE.generate_narrative(
        request.doc_type, request.theme, request.genre, request.title
    )
    return {"content": content}
