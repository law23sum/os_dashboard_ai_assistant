"""Documents API router with workspace uploads and legacy filesystem browsing."""

from __future__ import annotations

import base64
import json
import mimetypes
import shutil
import difflib
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, Response, UploadFile
from pydantic import BaseModel, Field

from assistant_hub_gui.assistant_hub.config import DATA_DIR, ensure_data_directories
from backend_api.deps import get_current_user
from backend_api.security import AuthUser

router = APIRouter()

REPO_ROOT = Path(__file__).resolve().parents[2]
LEGACY_DOCUMENTS_ROOT = (REPO_ROOT / "documents").resolve()
CHAT_DOCUMENTS_DIR = DATA_DIR / "chat_documents"
VERSION_DIR_NAME = "versions"
METADATA_FILENAME = "metadata.json"
TEXT_PREVIEW_BYTES = 4096
TEXT_RETURN_LIMIT = 500_000  # ~500 KB to keep API responses bounded

ensure_data_directories()
CHAT_DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)

def _migrate_legacy_chat_documents() -> None:
    """Move legacy flat document dirs into the demo tenant folder."""
    demo_root = CHAT_DOCUMENTS_DIR / "demo"
    demo_root.mkdir(parents=True, exist_ok=True)
    # Legacy layout: CHAT_DOCUMENTS_DIR/<doc_id>/metadata.json
    for meta_file in CHAT_DOCUMENTS_DIR.glob(f"*/{METADATA_FILENAME}"):
        # If parent is already a user folder (demo/admin/uuid), skip.
        parent = meta_file.parent
        # A user folder would contain multiple doc dirs; doc dir contains metadata.json.
        # We treat any direct child of CHAT_DOCUMENTS_DIR as a doc dir in legacy layout.
        if parent.parent != CHAT_DOCUMENTS_DIR:
            continue
        # parent is doc_id directory
        target = demo_root / parent.name
        if target.exists():
            continue
        try:
            shutil.move(str(parent), str(target))
        except Exception:
            continue


_migrate_legacy_chat_documents()


def _now_iso() -> str:
    return datetime.utcnow().isoformat(timespec="seconds")


ALLOWED_EXTENSIONS = {
    ".doc",
    ".docx",
    ".rtf",
    ".txt",
    ".md",
    ".markdown",
    ".xlsx",
    ".xls",
    ".xlsm",
    ".xlsb",
    ".ppt",
    ".pptx",
    ".pdf",
    ".json",
    ".csv",
    ".tsv",
    ".eml",
    ".msg",
    ".xml",
    ".html",
    ".htm",
    ".one",
    ".onepkg",
}

TEXT_EXTENSIONS = {
    ".txt",
    ".md",
    ".markdown",
    ".json",
    ".csv",
    ".tsv",
    ".xml",
    ".html",
    ".htm",
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".css",
    ".yaml",
    ".yml",
    ".ini",
    ".cfg",
    ".rtf",
    ".log",
}

CATEGORY_BY_EXTENSION = {
    ".doc": "word",
    ".docx": "word",
    ".rtf": "word",
    ".txt": "text",
    ".md": "markdown",
    ".markdown": "markdown",
    ".xlsx": "excel",
    ".xls": "excel",
    ".xlsm": "excel",
    ".xlsb": "excel",
    ".csv": "csv",
    ".tsv": "csv",
    ".ppt": "powerpoint",
    ".pptx": "powerpoint",
    ".pdf": "pdf",
    ".json": "json",
    ".xml": "xml",
    ".html": "html",
    ".htm": "html",
    ".eml": "email",
    ".msg": "email",
    ".one": "onenote",
    ".onepkg": "onenote",
    ".py": "code",
    ".js": "code",
    ".ts": "code",
    ".tsx": "code",
    ".css": "code",
}


def _safe_filename(filename: Optional[str]) -> str:
    if not filename:
        return "unnamed_file"
    keep = "".join(c if c.isalnum() or c in ("-", "_", ".", " ") else "_" for c in filename)
    keep = keep.strip(" .")
    return keep or "unnamed_file"


def _extension(filename: str) -> str:
    return Path(filename).suffix.lower()


def _category_for(filename: str) -> str:
    ext = _extension(filename)
    return CATEGORY_BY_EXTENSION.get(ext, "text" if ext in TEXT_EXTENSIONS else "file")


def _preview_type(filename: str) -> str:
    return "text" if _extension(filename) in TEXT_EXTENSIONS else "binary"


def _user_documents_dir(user_id: str) -> Path:
    return CHAT_DOCUMENTS_DIR / user_id


def _doc_dir(user_id: str, doc_id: str) -> Path:
    return _user_documents_dir(user_id) / doc_id


def _metadata_path(user_id: str, doc_id: str) -> Path:
    return _doc_dir(user_id, doc_id) / METADATA_FILENAME


def _versions_dir(user_id: str, doc_id: str) -> Path:
    return _doc_dir(user_id, doc_id) / VERSION_DIR_NAME


def _file_path_from_metadata(user_id: str, metadata: Dict[str, Any]) -> Path:
    return _doc_dir(user_id, metadata["id"]) / metadata["filename"]


def _load_metadata(user_id: str, doc_id: str) -> Dict[str, Any]:
    meta_path = _metadata_path(user_id, doc_id)
    if not meta_path.exists():
        raise HTTPException(status_code=404, detail="Document not found")
    try:
        return json.loads(meta_path.read_text())
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=500, detail="Corrupt document metadata") from exc


def _persist_metadata(user_id: str, doc: Dict[str, Any]) -> None:
    meta_path = _metadata_path(user_id, doc["id"])
    meta_path.parent.mkdir(parents=True, exist_ok=True)
    meta_path.write_text(json.dumps(doc, ensure_ascii=False, indent=2))


def _build_document_payload(user_id: str, doc: Dict[str, Any]) -> Dict[str, Any]:
    file_path = _file_path_from_metadata(user_id, doc)
    size_bytes = file_path.stat().st_size if file_path.exists() else 0
    preview = doc.get("content_preview")
    if preview is None and doc.get("preview_type") == "text" and file_path.exists():
        preview = _read_text_preview(file_path)
        doc["content_preview"] = preview
        _persist_metadata(user_id, doc)
    return {
        "id": doc["id"],
        "filename": doc["filename"],
        "original_name": doc["original_name"],
        "file_type": doc["file_type"],
        "category": doc["category"],
        "size_bytes": size_bytes,
        "preview_type": doc["preview_type"],
        "uploaded_at": doc["uploaded_at"],
        "content_preview": preview,
        "metadata": doc.get("metadata", {}),
    }


def _list_chat_documents(user_id: str) -> List[Dict[str, Any]]:
    documents: List[Dict[str, Any]] = []
    user_root = _user_documents_dir(user_id)
    if not user_root.exists():
        return []
    for meta_file in user_root.glob(f"*/{METADATA_FILENAME}"):
        try:
            doc = json.loads(meta_file.read_text())
        except Exception:
            continue
        try:
            documents.append(_build_document_payload(user_id, doc))
        except Exception:
            continue
    documents.sort(key=lambda d: d.get("uploaded_at") or "", reverse=True)
    return documents


def _read_text_preview(path: Path) -> str:
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as handle:
            return handle.read(TEXT_PREVIEW_BYTES)
    except Exception:
        return ""


def _snapshot_version(user_id: str, doc: Dict[str, Any]) -> Optional[str]:
    file_path = _file_path_from_metadata(user_id, doc)
    if not file_path.exists():
        return None
    versions_dir = _versions_dir(user_id, doc["id"])
    versions_dir.mkdir(parents=True, exist_ok=True)
    version_label = f"v{doc.get('version', 1)}-{_now_iso().replace(':', '').replace('-', '')}"
    snapshot_name = f"{version_label}{file_path.suffix or ''}"
    snapshot_path = versions_dir / snapshot_name
    shutil.copy2(file_path, snapshot_path)
    doc.setdefault("versions", []).append(
        {
            "version": doc.get("version", 1),
            "saved_at": _now_iso(),
            "path": str(snapshot_path),
            "id": snapshot_name,
        }
    )
    _persist_metadata(user_id, doc)
    return snapshot_name


class ChatDocument(BaseModel):
    id: str
    filename: str
    original_name: str
    file_type: str
    category: str
    size_bytes: int
    preview_type: str
    uploaded_at: str
    content_preview: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DocumentContentResponse(BaseModel):
    document_id: str
    filename: str
    content_type: str
    content: str
    encoding: str


class DocumentModifyRequest(BaseModel):
    document_id: str
    prompt: str
    persona: str = "AIC"


class DocumentModifyResponse(BaseModel):
    document_id: str
    success: bool
    modified_content: Optional[str] = None
    changes_summary: str
    new_version_id: Optional[str] = None


class DocumentEntry(BaseModel):
    name: str
    relative_path: str
    is_directory: bool
    size_bytes: int
    modified_at: Optional[str]


def _resolve_directory(subpath: Optional[str]) -> Path:
    """Resolve a user-provided subpath safely within the documents tree."""
    base = LEGACY_DOCUMENTS_ROOT
    if subpath:
        relative = Path(subpath)
        if relative.is_absolute():
            raise HTTPException(status_code=400, detail="Path must be relative to the documents directory")
        target = (base / relative).resolve()
    else:
        target = base

    base_resolved = base.resolve()
    if not str(target).startswith(str(base_resolved)):
        raise HTTPException(status_code=400, detail="Path escapes the documents directory")
    if not target.exists():
        raise HTTPException(status_code=404, detail="Requested directory not found")
    if not target.is_dir():
        raise HTTPException(status_code=400, detail="Requested path is not a directory")
    return target


def _serialize_entry(path: Path) -> DocumentEntry:
    """Build API metadata for a file or directory."""
    try:
        stats = path.stat()
        modified = datetime.fromtimestamp(stats.st_mtime).isoformat(timespec="seconds")
        size = stats.st_size if path.is_file() else 0
    except FileNotFoundError:
        modified = None
        size = 0

    return DocumentEntry(
        name=path.name,
        relative_path=str(path.relative_to(LEGACY_DOCUMENTS_ROOT)),
        is_directory=path.is_dir(),
        size_bytes=size,
        modified_at=modified,
    )


@router.get("/", response_model=List[ChatDocument])
async def list_workspace_documents(user: AuthUser = Depends(get_current_user)) -> List[ChatDocument]:
    """Return uploaded chat/workspace documents."""
    documents = _list_chat_documents(user.id)
    return [ChatDocument(**doc) for doc in documents]


@router.post("/upload", response_model=ChatDocument, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    persona: str = Form("AIC"),
    user: AuthUser = Depends(get_current_user),
) -> ChatDocument:
    """Upload a document into the workspace storage."""
    original_name = file.filename or "upload"
    safe_name = _safe_filename(original_name)
    ext = _extension(safe_name)
    if ext and ALLOWED_EXTENSIONS and ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    doc_id = uuid4().hex
    doc_dir = _doc_dir(user.id, doc_id)
    doc_dir.mkdir(parents=True, exist_ok=True)
    dest_path = doc_dir / safe_name

    try:
        # Streams upload contents to disk without loading the full payload into memory.
        file.file.seek(0)
        with dest_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    finally:
        file.file.close()

    preview_type = _preview_type(safe_name)
    metadata: Dict[str, Any] = {
        "id": doc_id,
        "filename": safe_name,
        "original_name": original_name,
        "file_type": ext.lstrip(".") if ext else "",
        "category": _category_for(safe_name),
        "size_bytes": dest_path.stat().st_size,
        "preview_type": preview_type,
        "uploaded_at": _now_iso(),
        "metadata": {"persona": persona, "owner_user_id": user.id},
        "version": 1,
    }

    if preview_type == "text":
        metadata["content_preview"] = _read_text_preview(dest_path)

    _persist_metadata(user.id, metadata)
    return ChatDocument(**_build_document_payload(user.id, metadata))


@router.get("/{document_id}/content", response_model=DocumentContentResponse)
async def get_document_content(document_id: str, user: AuthUser = Depends(get_current_user)) -> DocumentContentResponse:
    """Return the raw content of a document for preview/download in the UI."""
    doc = _load_metadata(user.id, document_id)
    file_path = _file_path_from_metadata(user.id, doc)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Document file missing on disk")

    content_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
    if doc.get("preview_type") == "text":
        with file_path.open("r", encoding="utf-8", errors="ignore") as handle:
            content = handle.read(TEXT_RETURN_LIMIT)
        encoding = "utf-8"
    else:
        chunk = file_path.read_bytes()
        content = base64.b64encode(chunk).decode("ascii")
        encoding = "base64"

    return DocumentContentResponse(
        document_id=document_id,
        filename=doc["original_name"],
        content_type=content_type,
        content=content,
        encoding=encoding,
    )


class PutContentRequest(BaseModel):
    content: str
    persona: str = "Chris"


@router.put("/{document_id}/content", response_model=DocumentModifyResponse)
async def put_document_content(
    document_id: str,
    payload: PutContentRequest,
    user: AuthUser = Depends(get_current_user),
) -> DocumentModifyResponse:
    """Replace the content of a text document (creates a version snapshot first)."""
    doc = _load_metadata(user.id, document_id)
    file_path = _file_path_from_metadata(user.id, doc)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Document file missing on disk")
    if doc.get("preview_type") != "text":
        raise HTTPException(status_code=400, detail="Only text documents can be edited in-app")

    snapshot_name = _snapshot_version(user.id, doc)
    file_path.write_text(payload.content, encoding="utf-8", errors="ignore")
    doc["version"] = doc.get("version", 1) + 1
    doc["size_bytes"] = file_path.stat().st_size
    doc["content_preview"] = _read_text_preview(file_path)
    _persist_metadata(user.id, doc)

    return DocumentModifyResponse(
        document_id=document_id,
        success=True,
        modified_content=doc["content_preview"],
        changes_summary=f"Saved changes by {payload.persona}",
        new_version_id=snapshot_name,
    )


class DocumentVersionRow(BaseModel):
    id: str
    version_number: int
    created_at: str
    created_by: str
    change_summary: str
    is_ai_generated: bool = False
    confidence_score: Optional[float] = None


@router.get("/{document_id}/versions", response_model=List[DocumentVersionRow])
async def list_document_versions(document_id: str, user: AuthUser = Depends(get_current_user)) -> List[DocumentVersionRow]:
    doc = _load_metadata(user.id, document_id)
    versions = doc.get("versions") or []
    persona = (doc.get("metadata") or {}).get("persona") or "system"
    rows: List[DocumentVersionRow] = []
    # Newest first for UI
    for v in reversed(versions):
        rows.append(
            DocumentVersionRow(
                id=v.get("id") or Path(v.get("path") or "").name or "",
                version_number=int(v.get("version") or 0),
                created_at=v.get("saved_at") or doc.get("uploaded_at") or _now_iso(),
                created_by=str(persona),
                change_summary="Snapshot",
                is_ai_generated=str(persona).lower() in ("aic", "aria", "sora"),
            )
        )
    return rows


class DiffResponse(BaseModel):
    from_id: str
    to_id: str
    diff: str
    format: str = "unified"


def _read_version_bytes(user_id: str, doc: Dict[str, Any], version_id: str) -> bytes:
    versions_dir = _versions_dir(user_id, doc["id"])
    candidate = versions_dir / version_id
    if not candidate.exists():
        raise HTTPException(status_code=404, detail="Version not found")
    return candidate.read_bytes()


def _hexdump(raw: bytes, width: int = 16) -> List[str]:
    lines: List[str] = []
    for i in range(0, len(raw), width):
        chunk = raw[i : i + width]
        hex_bytes = " ".join(f"{b:02x}" for b in chunk)
        ascii_bytes = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        lines.append(f"{i:08x}  {hex_bytes:<{width*3}} |{ascii_bytes}|")
    return lines


@router.get("/{document_id}/diff", response_model=DiffResponse)
async def diff_document_versions(
    document_id: str,
    from_id: str,
    to_id: str,
    mode: str = "unified",
    user: AuthUser = Depends(get_current_user),
) -> DiffResponse:
    doc = _load_metadata(user.id, document_id)
    file_path = _file_path_from_metadata(user.id, doc)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Document file missing on disk")

    base_bytes = _read_version_bytes(user.id, doc, from_id) if from_id != "current" else file_path.read_bytes()
    next_bytes = _read_version_bytes(user.id, doc, to_id) if to_id != "current" else file_path.read_bytes()

    if doc.get("preview_type") == "text":
        a = base_bytes.decode("utf-8", errors="ignore").splitlines(keepends=True)
        b = next_bytes.decode("utf-8", errors="ignore").splitlines(keepends=True)
        diff_lines = difflib.unified_diff(a, b, fromfile=from_id, tofile=to_id)
        return DiffResponse(from_id=from_id, to_id=to_id, diff="".join(diff_lines), format="unified")

    # Binary: compare hexdumps.
    a_hex = _hexdump(base_bytes)
    b_hex = _hexdump(next_bytes)
    diff_lines = difflib.unified_diff([l + "\n" for l in a_hex], [l + "\n" for l in b_hex], fromfile=from_id, tofile=to_id)
    return DiffResponse(from_id=from_id, to_id=to_id, diff="".join(diff_lines), format="unified")


class MergeRequest(BaseModel):
    # New API: merge many.
    version_ids: List[str] = Field(default_factory=list, description="Version ids to merge into current")
    # Backward-compat API: merge one into base (UI may send these)
    base_version_id: Optional[str] = None
    merge_version_id: Optional[str] = None
    persona: str = "AIC"


@router.post("/{document_id}/versions/merge", response_model=DocumentVersionRow)
async def merge_versions_into_current(
    document_id: str,
    payload: MergeRequest,
    user: AuthUser = Depends(get_current_user),
) -> DocumentVersionRow:
    doc = _load_metadata(user.id, document_id)
    file_path = _file_path_from_metadata(user.id, doc)
    if doc.get("preview_type") != "text":
        raise HTTPException(status_code=400, detail="Only text documents can be merged in-app")

    # Normalize to a list of version ids to merge.
    version_ids = list(payload.version_ids)
    if payload.merge_version_id:
        version_ids.append(payload.merge_version_id)

    current = file_path.read_text(encoding="utf-8", errors="ignore").splitlines()
    merged = list(current)
    seen = set(current)
    for vid in version_ids:
        if vid == "current":
            continue
        text = _read_version_bytes(user.id, doc, vid).decode("utf-8", errors="ignore").splitlines()
        for line in text:
            if line not in seen:
                merged.append(line)
                seen.add(line)

    snapshot_name = _snapshot_version(user.id, doc)
    file_path.write_text("\n".join(merged) + "\n", encoding="utf-8", errors="ignore")
    doc["version"] = doc.get("version", 1) + 1
    doc["size_bytes"] = file_path.stat().st_size
    doc["content_preview"] = _read_text_preview(file_path)
    _persist_metadata(user.id, doc)

    return DocumentVersionRow(
        id=snapshot_name or f"v{doc.get('version', 0)}",
        version_number=int(doc.get("version", 0)),
        created_at=_now_iso(),
        created_by=payload.persona,
        change_summary=f"Merged {len(version_ids)} version(s) into current",
        is_ai_generated=payload.persona.lower() in ("aic", "aria", "sora"),
        confidence_score=0.85 if payload.persona.lower() in ("aic", "aria", "sora") else None,
    )


@router.post("/{document_id}/modify", response_model=DocumentModifyResponse)
async def modify_document(document_id: str, request: DocumentModifyRequest, user: AuthUser = Depends(get_current_user)) -> DocumentModifyResponse:
    """Apply a simple AI-style modification for demo purposes."""
    doc = _load_metadata(user.id, document_id)
    file_path = _file_path_from_metadata(user.id, doc)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Document file missing on disk")

    if doc.get("preview_type") != "text":
        return DocumentModifyResponse(
            document_id=document_id,
            success=False,
            changes_summary="Binary files cannot be auto-modified. Download and edit locally.",
        )

    snapshot_name = _snapshot_version(user.id, doc)
    update_header = f"\n\n[AI Update by {request.persona} @ {_now_iso()}]\n"
    update_body = request.prompt.strip() or "(No instructions provided.)"
    with file_path.open("a", encoding="utf-8", errors="ignore") as handle:
        handle.write(update_header + update_body + "\n")

    doc["version"] = doc.get("version", 1) + 1
    doc["size_bytes"] = file_path.stat().st_size
    doc["content_preview"] = _read_text_preview(file_path)
    _persist_metadata(user.id, doc)

    return DocumentModifyResponse(
        document_id=document_id,
        success=True,
        modified_content=doc["content_preview"],
        changes_summary=f"Applied prompt to {doc['original_name']}",
        new_version_id=snapshot_name,
    )


@router.delete("/{document_id}", status_code=204, response_class=Response)
async def delete_document(document_id: str, user: AuthUser = Depends(get_current_user)) -> Response:
    """Delete a stored document and its metadata."""
    doc_dir = _doc_dir(user.id, document_id)
    if not doc_dir.exists():
        raise HTTPException(status_code=404, detail="Document not found")
    shutil.rmtree(doc_dir, ignore_errors=True)
    return Response(status_code=204)


@router.get("/tree", response_model=List[DocumentEntry])
async def list_documents_tree(path: Optional[str] = None, user: AuthUser = Depends(get_current_user)) -> List[DocumentEntry]:
    """List document folders/files beneath the repository's documents directory."""
    directory = _resolve_directory(path)
    entries = sorted(directory.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
    return [_serialize_entry(entry) for entry in entries]


@router.get("/tree/", response_model=List[DocumentEntry], include_in_schema=False)
async def list_documents_tree_slash(path: Optional[str] = None, user: AuthUser = Depends(get_current_user)) -> List[DocumentEntry]:
    """Alias with trailing slash for legacy desktop clients."""
    return await list_documents_tree(path=path, user=user)
