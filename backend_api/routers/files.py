"""Filesystem browse endpoints (safe within workspace root).

These power the document viewer's server-file preview and AI context scanning.
"""

from __future__ import annotations

import base64
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from backend_api.deps import get_current_user
from backend_api.security import AuthUser

router = APIRouter()

REPO_ROOT = Path(__file__).resolve().parents[2]


def _workspace_root() -> Path:
    override = os.getenv("OSDASH_WORKSPACE_ROOT")
    if override:
        return Path(override).expanduser().resolve()
    return REPO_ROOT


def _resolve_within_root(path: str | None) -> Path:
    root = _workspace_root()
    target = Path(path or ".")
    if target.is_absolute():
        resolved = target.resolve()
    else:
        resolved = (root / target).resolve()
    # prevent path traversal
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Path escapes workspace root") from exc
    return resolved


class FileEntry(BaseModel):
    name: str
    path: str
    is_dir: bool
    size_bytes: int = 0
    modified_at: Optional[str] = None


@router.get("/files/tree", response_model=List[FileEntry])
async def list_tree(
    path: Optional[str] = Query(None),
    _: AuthUser = Depends(get_current_user),
) -> List[FileEntry]:
    root = _workspace_root()
    directory = _resolve_within_root(path)
    if not directory.exists():
        raise HTTPException(status_code=404, detail="Not found")
    if not directory.is_dir():
        raise HTTPException(status_code=400, detail="Path is not a directory")
    entries: List[FileEntry] = []
    for child in sorted(directory.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower())):
        try:
            st = child.stat()
            modified = datetime.fromtimestamp(st.st_mtime).isoformat(timespec="seconds")
            size = st.st_size if child.is_file() else 0
        except Exception:
            modified = None
            size = 0
        rel = str(child.relative_to(root))
        entries.append(FileEntry(name=child.name, path=rel, is_dir=child.is_dir(), size_bytes=size, modified_at=modified))
    return entries


class FilePreviewResponse(BaseModel):
    path: str
    content: str
    encoding: str = "utf-8"
    mtime: Optional[str] = None


@router.get("/files/preview", response_model=FilePreviewResponse)
async def preview_file(
    path: str = Query(...),
    max_bytes: int = Query(500_000, ge=1, le=2_000_000),
    _: AuthUser = Depends(get_current_user),
) -> FilePreviewResponse:
    target = _resolve_within_root(path)
    if not target.exists():
        raise HTTPException(status_code=404, detail="File not found")
    if target.is_dir():
        raise HTTPException(status_code=400, detail="Path is a directory")
    try:
        st = target.stat()
        mtime = datetime.fromtimestamp(st.st_mtime).isoformat(timespec="seconds")
    except Exception:
        mtime = None
    # Heuristic: try utf-8 read, else return base64
    raw = target.read_bytes()
    raw = raw[:max_bytes]
    try:
        text = raw.decode("utf-8")
        return FilePreviewResponse(path=str(path), content=text, encoding="utf-8", mtime=mtime)
    except Exception:
        return FilePreviewResponse(
            path=str(path),
            content=base64.b64encode(raw).decode("ascii"),
            encoding="base64",
            mtime=mtime,
        )

