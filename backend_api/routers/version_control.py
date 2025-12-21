"""Version control system with diff comparison and merging capabilities."""

from __future__ import annotations

import difflib
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend_api.routers.auth import get_current_user
from assistant_hub_gui.assistant_hub.config import DATA_DIR, ensure_data_directories

ensure_data_directories()

router = APIRouter()

VERSIONS_DIR = DATA_DIR / "document_versions"
VERSIONS_DIR.mkdir(parents=True, exist_ok=True)


class VersionInfo(BaseModel):
    version_id: str
    document_id: str
    version_number: int
    created_at: str
    created_by: Optional[str]
    file_path: str
    file_size: int
    checksum: str
    description: Optional[str]
    metadata: Dict[str, Any]


class DiffResult(BaseModel):
    version_a: VersionInfo
    version_b: VersionInfo
    diff_type: str  # "text" | "binary" | "json" | "structured"
    changes: Dict[str, Any]
    unified_diff: Optional[str] = None
    html_diff: Optional[str] = None


class VersionComparison(BaseModel):
    versions: List[VersionInfo]
    comparisons: List[DiffResult]
    merge_suggestions: List[Dict[str, Any]]


def calculate_checksum(file_path: Path) -> str:
    """Calculate SHA256 checksum of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def create_version(
    document_id: str,
    file_path: Path,
    created_by: Optional[str] = None,
    description: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> VersionInfo:
    """Create a new version snapshot."""
    version_dir = VERSIONS_DIR / document_id
    version_dir.mkdir(parents=True, exist_ok=True)
    
    # Get next version number
    existing_versions = list(version_dir.glob("v*.json"))
    version_number = len(existing_versions) + 1
    
    # Copy file to version directory
    version_file = version_dir / f"v{version_number}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}{file_path.suffix}"
    import shutil
    shutil.copy2(file_path, version_file)
    
    file_size = version_file.stat().st_size
    checksum = calculate_checksum(version_file)
    version_id = f"{document_id}_v{version_number}"
    
    version_info = VersionInfo(
        version_id=version_id,
        document_id=document_id,
        version_number=version_number,
        created_at=datetime.utcnow().isoformat(),
        created_by=created_by,
        file_path=str(version_file),
        file_size=file_size,
        checksum=checksum,
        description=description,
        metadata=metadata or {}
    )
    
    # Save metadata
    metadata_file = version_dir / f"v{version_number}.json"
    metadata_file.write_text(json.dumps(version_info.dict(), indent=2))
    
    return version_info


def get_versions(document_id: str) -> List[VersionInfo]:
    """Get all versions for a document."""
    version_dir = VERSIONS_DIR / document_id
    if not version_dir.exists():
        return []
    
    versions = []
    for metadata_file in sorted(version_dir.glob("v*.json")):
        try:
            data = json.loads(metadata_file.read_text())
            versions.append(VersionInfo(**data))
        except Exception:
            continue
    
    return sorted(versions, key=lambda v: v.version_number)


def compute_text_diff(text_a: str, text_b: str) -> Dict[str, Any]:
    """Compute diff between two text strings."""
    lines_a = text_a.splitlines(keepends=True)
    lines_b = text_b.splitlines(keepends=True)
    
    diff = list(difflib.unified_diff(
        lines_a, lines_b,
        fromfile="version_a",
        tofile="version_b",
        lineterm=""
    ))
    
    unified_diff = "".join(diff)
    
    # Create HTML diff
    html_diff_parts = []
    for line in difflib.HtmlDiff().make_file(
        lines_a, lines_b,
        fromdesc="Version A",
        todesc="Version B",
        context=True,
        numlines=3
    ):
        html_diff_parts.append(line)
    html_diff = "".join(html_diff_parts)
    
    # Calculate statistics
    added = sum(1 for line in diff if line.startswith("+") and not line.startswith("+++"))
    removed = sum(1 for line in diff if line.startswith("-") and not line.startswith("---"))
    
    return {
        "unified_diff": unified_diff,
        "html_diff": html_diff,
        "statistics": {
            "lines_added": added,
            "lines_removed": removed,
            "lines_changed": min(added, removed),
            "total_changes": added + removed
        }
    }


def compute_binary_diff(file_a: Path, file_b: Path) -> Dict[str, Any]:
    """Compute diff between two binary files."""
    size_a = file_a.stat().st_size
    size_b = file_b.stat().st_size
    
    checksum_a = calculate_checksum(file_a)
    checksum_b = calculate_checksum(file_b)
    
    return {
        "size_a": size_a,
        "size_b": size_b,
        "size_difference": size_b - size_a,
        "checksum_a": checksum_a,
        "checksum_b": checksum_b,
        "identical": checksum_a == checksum_b
    }


def compare_versions(version_a: VersionInfo, version_b: VersionInfo) -> DiffResult:
    """Compare two versions and generate diff."""
    file_a = Path(version_a.file_path)
    file_b = Path(version_b.file_path)
    
    # Determine diff type based on file extension
    ext = file_a.suffix.lower()
    
    if ext in [".txt", ".md", ".py", ".js", ".ts", ".json", ".csv", ".xml", ".html"]:
        # Text-based diff
        try:
            text_a = file_a.read_text(encoding="utf-8", errors="ignore")
            text_b = file_b.read_text(encoding="utf-8", errors="ignore")
            
            diff_data = compute_text_diff(text_a, text_b)
            
            return DiffResult(
                version_a=version_a,
                version_b=version_b,
                diff_type="text",
                changes=diff_data,
                unified_diff=diff_data.get("unified_diff"),
                html_diff=diff_data.get("html_diff")
            )
        except Exception:
            # Fall back to binary diff
            pass
    
    elif ext == ".json":
        # JSON structured diff
        try:
            json_a = json.loads(file_a.read_text())
            json_b = json.loads(file_b.read_text())
            
            # Simple JSON diff
            changes = {
                "added": {},
                "removed": {},
                "modified": {}
            }
            
            # Compare keys
            keys_a = set(json_a.keys())
            keys_b = set(json_b.keys())
            
            for key in keys_b - keys_a:
                changes["added"][key] = json_b[key]
            
            for key in keys_a - keys_b:
                changes["removed"][key] = json_a[key]
            
            for key in keys_a & keys_b:
                if json_a[key] != json_b[key]:
                    changes["modified"][key] = {
                        "old": json_a[key],
                        "new": json_b[key]
                    }
            
            return DiffResult(
                version_a=version_a,
                version_b=version_b,
                diff_type="json",
                changes=changes
            )
        except Exception:
            pass
    
    # Binary diff fallback
    diff_data = compute_binary_diff(file_a, file_b)
    
    return DiffResult(
        version_a=version_a,
        version_b=version_b,
        diff_type="binary",
        changes=diff_data
    )


@router.post("/documents/{document_id}/versions", response_model=VersionInfo)
async def create_document_version(
    document_id: str,
    description: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Create a new version snapshot of a document."""
    # Find the document file
    from backend_api.routers.documents import _load_metadata, _file_path_from_metadata
    
    try:
        doc = _load_metadata(document_id)
        file_path = _file_path_from_metadata(doc)
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Document file not found")
        
        version_info = create_version(
            document_id=document_id,
            file_path=file_path,
            created_by=current_user.get("username"),
            description=description,
            metadata={"user_id": current_user.get("id")}
        )
        
        return version_info
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create version: {str(e)}")


@router.get("/documents/{document_id}/versions", response_model=List[VersionInfo])
async def list_document_versions(
    document_id: str,
    current_user: dict = Depends(get_current_user)
):
    """List all versions of a document."""
    return get_versions(document_id)


@router.get("/documents/{document_id}/versions/compare", response_model=DiffResult)
async def compare_document_versions(
    document_id: str,
    version_a: int,
    version_b: int,
    current_user: dict = Depends(get_current_user)
):
    """Compare two versions of a document."""
    versions = get_versions(document_id)
    
    version_a_info = next((v for v in versions if v.version_number == version_a), None)
    version_b_info = next((v for v in versions if v.version_number == version_b), None)
    
    if not version_a_info or not version_b_info:
        raise HTTPException(status_code=404, detail="One or both versions not found")
    
    return compare_versions(version_a_info, version_b_info)


@router.post("/documents/{document_id}/versions/compare-multiple", response_model=VersionComparison)
async def compare_multiple_versions(
    document_id: str,
    version_numbers: List[int],
    current_user: dict = Depends(get_current_user)
):
    """Compare multiple versions and generate merge suggestions."""
    versions = get_versions(document_id)
    
    selected_versions = [v for v in versions if v.version_number in version_numbers]
    selected_versions.sort(key=lambda v: v.version_number)
    
    if len(selected_versions) < 2:
        raise HTTPException(status_code=400, detail="Need at least 2 versions to compare")
    
    # Compare all pairs
    comparisons = []
    for i in range(len(selected_versions) - 1):
        diff_result = compare_versions(selected_versions[i], selected_versions[i + 1])
        comparisons.append(diff_result)
    
    # Generate merge suggestions
    merge_suggestions = []
    if len(comparisons) > 0:
        # Analyze conflicts and suggest merges
        latest_diff = comparisons[-1]
        if latest_diff.diff_type == "text" and latest_diff.changes.get("statistics"):
            stats = latest_diff.changes["statistics"]
            if stats["total_changes"] > 0:
                merge_suggestions.append({
                    "type": "auto_merge",
                    "confidence": "high" if stats["lines_changed"] < stats["total_changes"] * 0.3 else "medium",
                    "description": f"Auto-merge possible: {stats['lines_added']} additions, {stats['lines_removed']} removals"
                })
    
    return VersionComparison(
        versions=selected_versions,
        comparisons=comparisons,
        merge_suggestions=merge_suggestions
    )
