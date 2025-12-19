"""Document Version Control API Router.

Provides endpoints for:
- Version history management
- Multi-version comparison (diff stacking)
- Version merging
- Content diff generation
"""

from __future__ import annotations

import difflib
import hashlib
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from assistant_hub_gui.assistant_hub.config import DATA_DIR

router = APIRouter()

CHAT_DOCUMENTS_DIR = DATA_DIR / "chat_documents"
VERSION_DIR_NAME = "versions"
METADATA_FILENAME = "metadata.json"


def _now_iso() -> str:
    return datetime.utcnow().isoformat(timespec="seconds")


class DocumentVersion(BaseModel):
    """Version information for a document."""
    id: str
    document_id: str
    version_number: int
    created_at: str
    created_by: str
    change_summary: str
    is_ai_generated: bool
    confidence_score: Optional[float] = None
    file_size: int
    checksum: str


class VersionDiff(BaseModel):
    """Diff between two versions."""
    base_version_id: str
    compare_version_id: str
    base_version_number: int
    compare_version_number: int
    additions: int
    deletions: int
    changes: List[Dict[str, Any]]
    unified_diff: str


class VersionMergeRequest(BaseModel):
    """Request to merge two versions."""
    base_version_id: str
    merge_version_id: str
    merge_strategy: str = "smart"  # "smart", "base_priority", "merge_priority"


class VersionMergeResult(BaseModel):
    """Result of merging two versions."""
    success: bool
    new_version_id: str
    merged_content: str
    conflicts: List[Dict[str, Any]]
    merge_summary: str


class MultiVersionComparison(BaseModel):
    """Comparison across multiple versions."""
    document_id: str
    versions: List[DocumentVersion]
    diffs: List[VersionDiff]
    timeline: List[Dict[str, Any]]


def _doc_dir(doc_id: str) -> Path:
    return CHAT_DOCUMENTS_DIR / doc_id


def _versions_dir(doc_id: str) -> Path:
    return _doc_dir(doc_id) / VERSION_DIR_NAME


def _metadata_path(doc_id: str) -> Path:
    return _doc_dir(doc_id) / METADATA_FILENAME


def _load_metadata(doc_id: str) -> Dict[str, Any]:
    meta_path = _metadata_path(doc_id)
    if not meta_path.exists():
        raise HTTPException(status_code=404, detail="Document not found")
    return json.loads(meta_path.read_text())


def _persist_metadata(doc: Dict[str, Any]) -> None:
    meta_path = _metadata_path(doc["id"])
    meta_path.write_text(json.dumps(doc, ensure_ascii=False, indent=2))


def _compute_checksum(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()[:16]


def _read_version_content(doc_id: str, version_path: str) -> str:
    """Read content from a version file."""
    path = Path(version_path)
    if not path.exists():
        # Try relative to versions dir
        path = _versions_dir(doc_id) / Path(version_path).name
    
    if not path.exists():
        raise HTTPException(status_code=404, detail="Version file not found")
    
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return path.read_bytes().decode("utf-8", errors="ignore")


def _compute_diff(base_content: str, compare_content: str) -> Dict[str, Any]:
    """Compute detailed diff between two versions."""
    base_lines = base_content.splitlines(keepends=True)
    compare_lines = compare_content.splitlines(keepends=True)
    
    # Generate unified diff
    unified = list(difflib.unified_diff(
        base_lines, compare_lines,
        fromfile="base", tofile="compare",
        lineterm=""
    ))
    
    # Compute additions and deletions
    additions = sum(1 for line in unified if line.startswith("+") and not line.startswith("+++"))
    deletions = sum(1 for line in unified if line.startswith("-") and not line.startswith("---"))
    
    # Generate detailed changes
    matcher = difflib.SequenceMatcher(None, base_lines, compare_lines)
    changes = []
    
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue
        
        change = {
            "type": tag,
            "base_start": i1,
            "base_end": i2,
            "compare_start": j1,
            "compare_end": j2,
        }
        
        if tag == "replace":
            change["base_content"] = "".join(base_lines[i1:i2])
            change["compare_content"] = "".join(compare_lines[j1:j2])
        elif tag == "delete":
            change["base_content"] = "".join(base_lines[i1:i2])
        elif tag == "insert":
            change["compare_content"] = "".join(compare_lines[j1:j2])
        
        changes.append(change)
    
    return {
        "additions": additions,
        "deletions": deletions,
        "changes": changes,
        "unified_diff": "\n".join(unified)
    }


def _smart_merge(base_content: str, merge_content: str) -> tuple[str, List[Dict]]:
    """Perform smart merge of two content versions."""
    base_lines = base_content.splitlines(keepends=True)
    merge_lines = merge_content.splitlines(keepends=True)
    
    matcher = difflib.SequenceMatcher(None, base_lines, merge_lines)
    merged = []
    conflicts = []
    
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            merged.extend(base_lines[i1:i2])
        elif tag == "replace":
            # Potential conflict - try to merge intelligently
            base_segment = "".join(base_lines[i1:i2])
            merge_segment = "".join(merge_lines[j1:j2])
            
            # If merge is just an extension, use merge version
            if merge_segment.startswith(base_segment):
                merged.append(merge_segment)
            elif base_segment.startswith(merge_segment):
                merged.append(base_segment)
            else:
                # Record conflict but prefer merge version
                conflicts.append({
                    "line_start": len(merged),
                    "base_content": base_segment,
                    "merge_content": merge_segment,
                    "resolved": "merge"
                })
                merged.extend(merge_lines[j1:j2])
        elif tag == "delete":
            # Content deleted in merge version - keep deletion
            pass
        elif tag == "insert":
            # Content added in merge version - include it
            merged.extend(merge_lines[j1:j2])
    
    return "".join(merged), conflicts


@router.get("/{document_id}/versions", response_model=List[DocumentVersion])
async def list_document_versions(document_id: str) -> List[DocumentVersion]:
    """List all versions of a document."""
    doc = _load_metadata(document_id)
    versions_data = doc.get("versions", [])
    
    versions = []
    for v in versions_data:
        version_path = Path(v.get("path", ""))
        if version_path.exists():
            file_size = version_path.stat().st_size
            content = version_path.read_bytes()
            checksum = _compute_checksum(content)
        else:
            file_size = 0
            checksum = "unknown"
        
        versions.append(DocumentVersion(
            id=v.get("id", f"v{v.get('version', 0)}"),
            document_id=document_id,
            version_number=v.get("version", 0),
            created_at=v.get("saved_at", ""),
            created_by=v.get("created_by", "system"),
            change_summary=v.get("change_summary", "Version saved"),
            is_ai_generated=v.get("is_ai_generated", False),
            confidence_score=v.get("confidence_score"),
            file_size=file_size,
            checksum=checksum
        ))
    
    return sorted(versions, key=lambda x: x.version_number, reverse=True)


@router.get("/{document_id}/versions/{version_id}")
async def get_version_content(document_id: str, version_id: str) -> Dict[str, Any]:
    """Get the content of a specific version."""
    doc = _load_metadata(document_id)
    versions_data = doc.get("versions", [])
    
    # Find version
    version_info = None
    for v in versions_data:
        vid = v.get("id", f"v{v.get('version', 0)}")
        if vid == version_id or str(v.get("version")) == version_id:
            version_info = v
            break
    
    if not version_info:
        raise HTTPException(status_code=404, detail="Version not found")
    
    content = _read_version_content(document_id, version_info["path"])
    
    return {
        "version_id": version_id,
        "document_id": document_id,
        "content": content,
        "metadata": version_info
    }


@router.post("/{document_id}/versions")
async def create_version(
    document_id: str,
    content: Optional[str] = None,
    change_summary: str = "Manual version save",
    created_by: str = "user",
    is_ai_generated: bool = False,
    confidence_score: Optional[float] = None
) -> DocumentVersion:
    """Create a new version of a document."""
    doc = _load_metadata(document_id)
    doc_path = _doc_dir(document_id) / doc["filename"]
    
    # Get current version number
    versions_data = doc.get("versions", [])
    current_version = max([v.get("version", 0) for v in versions_data], default=0)
    new_version = current_version + 1
    
    # Create versions directory
    versions_dir = _versions_dir(document_id)
    versions_dir.mkdir(parents=True, exist_ok=True)
    
    # Save version
    version_id = uuid4().hex[:12]
    timestamp = _now_iso().replace(":", "").replace("-", "")
    ext = doc_path.suffix
    version_filename = f"v{new_version}-{timestamp}{ext}"
    version_path = versions_dir / version_filename
    
    if content:
        version_path.write_text(content, encoding="utf-8")
    elif doc_path.exists():
        shutil.copy2(doc_path, version_path)
    else:
        raise HTTPException(status_code=400, detail="No content to version")
    
    # Update metadata
    version_entry = {
        "id": version_id,
        "version": new_version,
        "saved_at": _now_iso(),
        "path": str(version_path),
        "created_by": created_by,
        "change_summary": change_summary,
        "is_ai_generated": is_ai_generated,
        "confidence_score": confidence_score
    }
    
    doc.setdefault("versions", []).append(version_entry)
    doc["version"] = new_version
    _persist_metadata(doc)
    
    file_size = version_path.stat().st_size
    checksum = _compute_checksum(version_path.read_bytes())
    
    return DocumentVersion(
        id=version_id,
        document_id=document_id,
        version_number=new_version,
        created_at=version_entry["saved_at"],
        created_by=created_by,
        change_summary=change_summary,
        is_ai_generated=is_ai_generated,
        confidence_score=confidence_score,
        file_size=file_size,
        checksum=checksum
    )


@router.get("/{document_id}/diff")
async def compare_versions(
    document_id: str,
    base_version: str = Query(..., description="Base version ID or number"),
    compare_version: str = Query(..., description="Compare version ID or number")
) -> VersionDiff:
    """Compare two versions and get diff."""
    doc = _load_metadata(document_id)
    versions_data = doc.get("versions", [])
    
    # Find versions
    base_info = None
    compare_info = None
    
    for v in versions_data:
        vid = v.get("id", f"v{v.get('version', 0)}")
        if vid == base_version or str(v.get("version")) == base_version:
            base_info = v
        if vid == compare_version or str(v.get("version")) == compare_version:
            compare_info = v
    
    if not base_info or not compare_info:
        raise HTTPException(status_code=404, detail="One or both versions not found")
    
    base_content = _read_version_content(document_id, base_info["path"])
    compare_content = _read_version_content(document_id, compare_info["path"])
    
    diff_result = _compute_diff(base_content, compare_content)
    
    return VersionDiff(
        base_version_id=base_info.get("id", f"v{base_info.get('version')}"),
        compare_version_id=compare_info.get("id", f"v{compare_info.get('version')}"),
        base_version_number=base_info.get("version", 0),
        compare_version_number=compare_info.get("version", 0),
        additions=diff_result["additions"],
        deletions=diff_result["deletions"],
        changes=diff_result["changes"],
        unified_diff=diff_result["unified_diff"]
    )


@router.get("/{document_id}/multi-diff")
async def multi_version_comparison(
    document_id: str,
    versions: str = Query(..., description="Comma-separated version IDs or numbers")
) -> MultiVersionComparison:
    """Compare multiple versions at once (stacked diffs)."""
    version_ids = [v.strip() for v in versions.split(",")]
    
    if len(version_ids) < 2:
        raise HTTPException(status_code=400, detail="At least 2 versions required")
    
    doc = _load_metadata(document_id)
    versions_data = doc.get("versions", [])
    
    # Collect version info
    version_objects = []
    version_map = {}
    
    for v in versions_data:
        vid = v.get("id", f"v{v.get('version', 0)}")
        if vid in version_ids or str(v.get("version")) in version_ids:
            version_path = Path(v.get("path", ""))
            if version_path.exists():
                file_size = version_path.stat().st_size
                checksum = _compute_checksum(version_path.read_bytes())
            else:
                file_size = 0
                checksum = "unknown"
            
            version_obj = DocumentVersion(
                id=vid,
                document_id=document_id,
                version_number=v.get("version", 0),
                created_at=v.get("saved_at", ""),
                created_by=v.get("created_by", "system"),
                change_summary=v.get("change_summary", ""),
                is_ai_generated=v.get("is_ai_generated", False),
                confidence_score=v.get("confidence_score"),
                file_size=file_size,
                checksum=checksum
            )
            version_objects.append(version_obj)
            version_map[vid] = v
            version_map[str(v.get("version"))] = v
    
    # Sort by version number
    version_objects.sort(key=lambda x: x.version_number)
    
    # Generate diffs between consecutive versions
    diffs = []
    for i in range(len(version_objects) - 1):
        base = version_objects[i]
        compare = version_objects[i + 1]
        
        base_info = version_map.get(base.id) or version_map.get(str(base.version_number))
        compare_info = version_map.get(compare.id) or version_map.get(str(compare.version_number))
        
        base_content = _read_version_content(document_id, base_info["path"])
        compare_content = _read_version_content(document_id, compare_info["path"])
        
        diff_result = _compute_diff(base_content, compare_content)
        
        diffs.append(VersionDiff(
            base_version_id=base.id,
            compare_version_id=compare.id,
            base_version_number=base.version_number,
            compare_version_number=compare.version_number,
            additions=diff_result["additions"],
            deletions=diff_result["deletions"],
            changes=diff_result["changes"],
            unified_diff=diff_result["unified_diff"]
        ))
    
    # Build timeline
    timeline = []
    total_additions = 0
    total_deletions = 0
    
    for v, d in zip(version_objects, diffs + [None]):
        entry = {
            "version_id": v.id,
            "version_number": v.version_number,
            "created_at": v.created_at,
            "created_by": v.created_by,
            "change_summary": v.change_summary,
            "cumulative_additions": total_additions,
            "cumulative_deletions": total_deletions
        }
        if d:
            total_additions += d.additions
            total_deletions += d.deletions
            entry["additions_to_next"] = d.additions
            entry["deletions_to_next"] = d.deletions
        timeline.append(entry)
    
    return MultiVersionComparison(
        document_id=document_id,
        versions=version_objects,
        diffs=diffs,
        timeline=timeline
    )


@router.post("/{document_id}/merge")
async def merge_versions(
    document_id: str,
    request: VersionMergeRequest
) -> VersionMergeResult:
    """Merge two document versions."""
    doc = _load_metadata(document_id)
    versions_data = doc.get("versions", [])
    
    # Find versions
    base_info = None
    merge_info = None
    
    for v in versions_data:
        vid = v.get("id", f"v{v.get('version', 0)}")
        if vid == request.base_version_id or str(v.get("version")) == request.base_version_id:
            base_info = v
        if vid == request.merge_version_id or str(v.get("version")) == request.merge_version_id:
            merge_info = v
    
    if not base_info or not merge_info:
        raise HTTPException(status_code=404, detail="One or both versions not found")
    
    base_content = _read_version_content(document_id, base_info["path"])
    merge_content = _read_version_content(document_id, merge_info["path"])
    
    # Perform merge
    if request.merge_strategy == "base_priority":
        merged_content = base_content
        conflicts = []
    elif request.merge_strategy == "merge_priority":
        merged_content = merge_content
        conflicts = []
    else:  # smart merge
        merged_content, conflicts = _smart_merge(base_content, merge_content)
    
    # Create new version with merged content
    new_version = await create_version(
        document_id,
        content=merged_content,
        change_summary=f"Merged v{base_info.get('version')} and v{merge_info.get('version')}",
        created_by="merge_operation",
        is_ai_generated=False
    )
    
    return VersionMergeResult(
        success=True,
        new_version_id=new_version.id,
        merged_content=merged_content,
        conflicts=conflicts,
        merge_summary=f"Merged versions {request.base_version_id} and {request.merge_version_id} "
                      f"using {request.merge_strategy} strategy. {len(conflicts)} conflicts resolved."
    )


@router.post("/{document_id}/versions/{version_id}/restore")
async def restore_version(document_id: str, version_id: str) -> Dict[str, Any]:
    """Restore a document to a specific version."""
    doc = _load_metadata(document_id)
    versions_data = doc.get("versions", [])
    
    # Find version
    version_info = None
    for v in versions_data:
        vid = v.get("id", f"v{v.get('version', 0)}")
        if vid == version_id or str(v.get("version")) == version_id:
            version_info = v
            break
    
    if not version_info:
        raise HTTPException(status_code=404, detail="Version not found")
    
    # Read version content
    version_content = _read_version_content(document_id, version_info["path"])
    
    # Save current as new version first (backup)
    current_path = _doc_dir(document_id) / doc["filename"]
    if current_path.exists():
        await create_version(
            document_id,
            change_summary=f"Backup before restoring to v{version_info.get('version')}",
            created_by="restore_operation"
        )
    
    # Write restored content
    current_path.write_text(version_content, encoding="utf-8")
    
    # Update metadata
    doc["version"] = doc.get("version", 0) + 1
    doc["content_preview"] = version_content[:4096] if len(version_content) > 4096 else version_content
    _persist_metadata(doc)
    
    return {
        "success": True,
        "message": f"Document restored to version {version_id}",
        "restored_version": version_info.get("version")
    }


@router.delete("/{document_id}/versions/{version_id}")
async def delete_version(document_id: str, version_id: str) -> Dict[str, str]:
    """Delete a specific version (keeps minimum 1 version)."""
    doc = _load_metadata(document_id)
    versions_data = doc.get("versions", [])
    
    if len(versions_data) <= 1:
        raise HTTPException(status_code=400, detail="Cannot delete the only version")
    
    # Find and remove version
    new_versions = []
    deleted = False
    
    for v in versions_data:
        vid = v.get("id", f"v{v.get('version', 0)}")
        if vid == version_id or str(v.get("version")) == version_id:
            # Delete file
            version_path = Path(v.get("path", ""))
            if version_path.exists():
                version_path.unlink()
            deleted = True
        else:
            new_versions.append(v)
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Version not found")
    
    doc["versions"] = new_versions
    _persist_metadata(doc)
    
    return {"message": f"Version {version_id} deleted"}
