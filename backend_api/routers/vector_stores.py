"""
Vector Store management API endpoints.

Provides CRUD operations for vector stores and file search capabilities.
Uses the enhanced file_tools module for all vector store operations.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from pydantic import BaseModel

from backend_api.deps import get_current_user
from backend_api.security import AuthUser

# Import OpenAI client helper
def get_openai_client():
    """Get OpenAI client instance."""
    from openai import OpenAI
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="OPENAI_API_KEY not configured"
        )
    return OpenAI(api_key=api_key)

from assistant_core.file_tools import (
    FileManager,
    VectorStoreManager,
    ToolResourceBuilder,
    ResponseInspector,
)

router = APIRouter()


# Pydantic models for request/response
class VectorStoreCreate(BaseModel):
    name: str
    file_ids: Optional[List[str]] = None
    expires_after_days: Optional[int] = None


class VectorStoreResponse(BaseModel):
    id: str
    name: str
    created_at: Optional[int] = None
    file_counts: Optional[Dict[str, Any]] = None
    usage_bytes: Optional[int] = None
    expires_after: Optional[Dict[str, Any]] = None


class FileUploadResponse(BaseModel):
    file_id: str
    filename: str
    purpose: str
    bytes: int


class BatchUploadRequest(BaseModel):
    file_ids: Optional[List[str]] = None
    files: Optional[List[Dict[str, Any]]] = None
    chunking_strategy: Optional[Dict[str, Any]] = None


class ChunkingStrategy(BaseModel):
    type: str = "static"
    max_chunk_size_tokens: int = 800
    chunk_overlap_tokens: int = 400


class RankingOptions(BaseModel):
    ranker: Optional[str] = "auto"
    score_threshold: Optional[float] = None
    hybrid_search: Optional[Dict[str, float]] = None


class SearchRequest(BaseModel):
    query: str
    limit: int = 10


class SearchResult(BaseModel):
    file_id: str
    score: Optional[float] = None
    content: Optional[str] = None


class SearchResponse(BaseModel):
    results: List[SearchResult]


def _get_vector_store_manager(user: AuthUser = Depends(get_current_user)) -> VectorStoreManager:
    """Get vector store manager instance."""
    client = get_openai_client()
    return VectorStoreManager(client)


def _get_file_manager(user: AuthUser = Depends(get_current_user)) -> FileManager:
    """Get file manager instance."""
    client = get_openai_client()
    return FileManager(client)


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    purpose: str = Form("assistants"),
    user: AuthUser = Depends(get_current_user),
) -> FileUploadResponse:
    """Upload a file to OpenAI (required before adding to vector store)."""
    file_mgr = _get_file_manager(user)
    
    # Save uploaded file temporarily
    import tempfile
    with tempfile.NamedTemporaryFile(delete=False, suffix=file.filename or "") as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        tmp_path = tmp_file.name
    
    try:
        # Upload to OpenAI
        file_info = file_mgr.upload_file(tmp_path, purpose=purpose)
        return FileUploadResponse(
            file_id=file_info["id"],
            filename=file_info["filename"],
            purpose=file_info["purpose"],
            bytes=file_info["bytes"],
        )
    finally:
        # Clean up temp file
        import os
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


@router.post("/", response_model=VectorStoreResponse)
async def create_vector_store(
    request: VectorStoreCreate,
    user: AuthUser = Depends(get_current_user),
) -> VectorStoreResponse:
    """Create a new vector store."""
    vector_mgr = _get_vector_store_manager(user)
    
    expires_after = None
    if request.expires_after_days:
        expires_after = {
            "anchor": "last_active_at",
            "days": request.expires_after_days,
        }
    
    vector_store = vector_mgr.create_vector_store(
        name=request.name,
        file_ids=request.file_ids,
        expires_after=expires_after,
    )
    
    return VectorStoreResponse(**vector_store)


@router.get("/", response_model=List[VectorStoreResponse])
async def list_vector_stores(
    limit: int = Query(100, ge=1, le=1000),
    order: str = Query("desc", regex="^(asc|desc)$"),
    user: AuthUser = Depends(get_current_user),
) -> List[VectorStoreResponse]:
    """List all vector stores."""
    vector_mgr = _get_vector_store_manager(user)
    stores = vector_mgr.list_vector_stores(limit=limit, order=order)
    return [VectorStoreResponse(**store) for store in stores]


@router.get("/{vector_store_id}", response_model=VectorStoreResponse)
async def get_vector_store(
    vector_store_id: str,
    user: AuthUser = Depends(get_current_user),
) -> VectorStoreResponse:
    """Get vector store details."""
    vector_mgr = _get_vector_store_manager(user)
    store = vector_mgr.get_vector_store(vector_store_id)
    return VectorStoreResponse(**store)


@router.put("/{vector_store_id}", response_model=VectorStoreResponse)
async def update_vector_store(
    vector_store_id: str,
    name: Optional[str] = None,
    expires_after_days: Optional[int] = None,
    user: AuthUser = Depends(get_current_user),
) -> VectorStoreResponse:
    """Update vector store name or expiration policy."""
    vector_mgr = _get_vector_store_manager(user)
    
    expires_after = None
    if expires_after_days is not None:
        expires_after = {
            "anchor": "last_active_at",
            "days": expires_after_days,
        }
    
    store = vector_mgr.update_vector_store(
        vector_store_id=vector_store_id,
        name=name,
        expires_after=expires_after,
    )
    return VectorStoreResponse(**store)


@router.delete("/{vector_store_id}")
async def delete_vector_store(
    vector_store_id: str,
    user: AuthUser = Depends(get_current_user),
) -> Dict[str, bool]:
    """Delete a vector store."""
    vector_mgr = _get_vector_store_manager(user)
    deleted = vector_mgr.delete_vector_store(vector_store_id)
    return {"deleted": deleted}


class AddFilesRequest(BaseModel):
    file_ids: List[str]
    max_chunk_size: Optional[int] = None
    chunk_overlap: Optional[int] = None


@router.post("/{vector_store_id}/files", response_model=Dict[str, Any])
async def add_files_to_vector_store(
    vector_store_id: str,
    request: AddFilesRequest,
    user: AuthUser = Depends(get_current_user),
) -> Dict[str, Any]:
    """Add files to a vector store (with optional chunking config)."""
    vector_mgr = _get_vector_store_manager(user)
    
    chunking_strategy = None
    if request.max_chunk_size is not None or request.chunk_overlap is not None:
        chunking_strategy = {
            "type": "static",
            "max_chunk_size_tokens": request.max_chunk_size or 800,
            "chunk_overlap_tokens": request.chunk_overlap or 400,
        }
    
    results = vector_mgr.add_files_to_vector_store(
        vector_store_id=vector_store_id,
        file_ids=request.file_ids,
        chunking_strategy=chunking_strategy,
    )
    return {"results": results, "count": len(results)}


@router.post("/{vector_store_id}/files/batch", response_model=Dict[str, Any])
async def add_files_batch(
    vector_store_id: str,
    request: BatchUploadRequest,
    user: AuthUser = Depends(get_current_user),
) -> Dict[str, Any]:
    """Add multiple files via batch operation (up to 500 files)."""
    vector_mgr = _get_vector_store_manager(user)
    
    if request.file_ids:
        batch_result = vector_mgr.add_files_to_vector_store_batch(
            vector_store_id=vector_store_id,
            file_ids=request.file_ids,
        )
    elif request.files:
        batch_result = vector_mgr.add_files_to_vector_store_batch(
            vector_store_id=vector_store_id,
            files=request.files,
        )
    else:
        raise HTTPException(status_code=400, detail="Either file_ids or files must be provided")
    
    return batch_result


@router.get("/{vector_store_id}/files", response_model=List[Dict[str, Any]])
async def list_vector_store_files(
    vector_store_id: str,
    limit: int = Query(100, ge=1, le=1000),
    order: str = Query("desc", regex="^(asc|desc)$"),
    user: AuthUser = Depends(get_current_user),
) -> List[Dict[str, Any]]:
    """List files in a vector store."""
    vector_mgr = _get_vector_store_manager(user)
    files = vector_mgr.list_vector_store_files(
        vector_store_id=vector_store_id,
        limit=limit,
        order=order,
    )
    return files


@router.get("/{vector_store_id}/files/{file_id}", response_model=Dict[str, Any])
async def get_vector_store_file(
    vector_store_id: str,
    file_id: str,
    user: AuthUser = Depends(get_current_user),
) -> Dict[str, Any]:
    """Get file details in a vector store."""
    vector_mgr = _get_vector_store_manager(user)
    file_info = vector_mgr.get_vector_store_file(
        vector_store_id=vector_store_id,
        file_id=file_id,
    )
    return file_info


@router.delete("/{vector_store_id}/files/{file_id}")
async def delete_vector_store_file(
    vector_store_id: str,
    file_id: str,
    user: AuthUser = Depends(get_current_user),
) -> Dict[str, bool]:
    """Remove a file from a vector store."""
    vector_mgr = _get_vector_store_manager(user)
    deleted = vector_mgr.delete_vector_store_file(
        vector_store_id=vector_store_id,
        file_id=file_id,
    )
    return {"deleted": deleted}


@router.post("/{vector_store_id}/search", response_model=SearchResponse)
async def search_vector_store(
    vector_store_id: str,
    request: SearchRequest,
    user: AuthUser = Depends(get_current_user),
) -> SearchResponse:
    """Search a vector store."""
    vector_mgr = _get_vector_store_manager(user)
    results = vector_mgr.search_vector_store(
        vector_store_id=vector_store_id,
        query=request.query,
        limit=request.limit,
    )
    return SearchResponse(
        results=[SearchResult(**r) for r in results]
    )


@router.get("/{vector_store_id}/batches/{batch_id}", response_model=Dict[str, Any])
async def get_file_batch(
    vector_store_id: str,
    batch_id: str,
    user: AuthUser = Depends(get_current_user),
) -> Dict[str, Any]:
    """Get file batch operation status."""
    vector_mgr = _get_vector_store_manager(user)
    batch = vector_mgr.get_file_batch(
        vector_store_id=vector_store_id,
        batch_id=batch_id,
    )
    return batch

