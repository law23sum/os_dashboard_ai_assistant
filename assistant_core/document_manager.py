#!/usr/bin/env python3
"""Document management module for handling file uploads and organization."""

import os
import shutil
import hashlib
from pathlib import Path
from typing import Optional, Tuple, List, Dict
from datetime import datetime
import sqlite3

from .config import DATA_DIR, ensure_data_directories
from .db import (
    db_create_note_link,
    db_get_note_links,
    db_delete_note_link,
    db_get_note_link,
    db_upsert_project,
    Project,
)
from .versioning import enqueue_commit


# Document type mappings
DOCUMENT_TYPES = {
    "onenote": ("local_onenote", [".one", ".onepkg"]),
    "excel": ("local_excel", [".xlsx", ".xls", ".xlsm", ".xlsb"]),
    "word": ("local_word", [".docx", ".doc", ".rtf"]),
    "pdf": ("local_pdf", [".pdf"]),
}

DOCUMENTS_BASE_DIR = DATA_DIR / "documents"


def get_document_directory(project_name: str, doc_type: str) -> Path:
    """Get the directory path for storing documents of a specific type for a project."""
    ensure_data_directories()
    # Sanitize project name for filesystem
    safe_project = "".join(
        c for c in project_name if c.isalnum() or c in (" ", "-", "_")
    ).strip()
    if not safe_project:
        safe_project = "General"

    doc_dir = DOCUMENTS_BASE_DIR / safe_project / doc_type
    doc_dir.mkdir(parents=True, exist_ok=True)
    return doc_dir


def validate_file_type(file_path: str, doc_type: str) -> Tuple[bool, Optional[str]]:
    """Validate that a file matches the expected document type."""
    if doc_type not in DOCUMENT_TYPES:
        return False, f"Unknown document type: {doc_type}"

    _, valid_extensions = DOCUMENT_TYPES[doc_type]
    file_ext = Path(file_path).suffix.lower()

    if file_ext not in valid_extensions:
        return False, f"Invalid file type. Expected: {', '.join(valid_extensions)}"

    return True, None


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename to be filesystem-safe."""
    # Remove path components
    filename = os.path.basename(filename)
    # Replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, "_")
    # Remove leading/trailing spaces and dots
    filename = filename.strip(" .")
    # Ensure it's not empty
    if not filename:
        filename = "unnamed_file"
    return filename


def upload_document(
    conn: sqlite3.Connection,
    file_path: str,
    project_name: str,
    doc_type: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    overwrite: bool = False,
) -> Tuple[bool, Optional[str], Optional[int]]:
    """
    Upload a document file and create a database link.

    Returns:
        (success, error_message, link_id)
    """
    try:
        # Validate file exists
        source_path = Path(file_path)
        if not source_path.exists():
            return False, "Source file does not exist", None

        # Validate file type
        is_valid, error = validate_file_type(file_path, doc_type)
        if not is_valid:
            return False, error, None

        # Ensure project exists
        project = Project(
            name=project_name, description="", status="active", priority="MEDIUM"
        )
        db_upsert_project(conn, project)

        # Get destination directory
        dest_dir = get_document_directory(project_name, doc_type)

        # Sanitize filename
        safe_filename = sanitize_filename(source_path.name)
        dest_path = dest_dir / safe_filename

        # Create relative path for storage (relative to documents base)
        safe_project = "".join(
            c for c in project_name if c.isalnum() or c in (" ", "-", "_")
        ).strip()
        if not safe_project:
            safe_project = "General"
        relative_path = f"{safe_project}/{doc_type}/{safe_filename}"

        # Get integration type
        integration_type, _ = DOCUMENT_TYPES[doc_type]

        # Check if document already exists (by external_id)
        existing_link = None
        c = conn.cursor()
        c.execute(
            "SELECT id FROM note_links WHERE external_id = ? AND integration_type = ?",
            (relative_path, integration_type),
        )
        row = c.fetchone()
        if row:
            existing_link = row[0]

        # If file exists and we're not overwriting, create a new version instead
        if dest_path.exists() and not overwrite:
            if existing_link:
                # Create a new version of the existing document
                link_id = existing_link
                _create_document_version(conn, link_id, str(dest_path), description)
            else:
                return (
                    False,
                    f"File already exists: {safe_filename}. Use overwrite=True to replace.",
                    None,
                )
        else:
            # If overwriting and file exists, save current version first
            if dest_path.exists() and existing_link:
                _create_document_version(
                    conn, existing_link, str(dest_path), "Auto-saved before overwrite"
                )
                link_id = existing_link
                # Update the link metadata
                c.execute(
                    "UPDATE note_links SET title = ?, description = ? WHERE id = ?",
                    (title or safe_filename, description or "", link_id),
                )
                conn.commit()
            else:
                # Create new document link
                display_title = title or safe_filename
                link_id = db_create_note_link(
                    conn=conn,
                    project_id=project_name,
                    integration_type=integration_type,
                    external_id=relative_path,
                    title=display_title,
                    description=description or "",
                )

        # Copy file (this will overwrite if overwrite=True)
        shutil.copy2(source_path, dest_path)

        # Create version record for the new upload
        _create_document_version(
            conn, link_id, str(dest_path), description or "Document uploaded"
        )

        # Auto-commit uploaded file to Git
        try:
            enqueue_commit(
                paths=[str(dest_path)],
                actor="User",
                tag="document-upload",
                reason=f"Upload {doc_type} document '{safe_filename}' to project '{project_name}'",
            )
        except Exception as e:
            # Don't fail upload if Git commit fails
            print(f"[DocumentManager] Warning: Git auto-commit failed: {e}")

        return True, None, link_id

    except Exception as e:
        return False, str(e), None


def get_project_documents(
    conn: sqlite3.Connection,
    project_name: Optional[str] = None,
    doc_type: Optional[str] = None,
) -> List[Dict]:
    """
    Get all documents for a project (or all projects if project_name is None).

    Returns list of dicts with: id, project_id, integration_type, external_id, title,
    description, file_path, file_size, modified_date
    """
    # Map doc_type to integration_type if needed
    integration_type = None
    if doc_type and doc_type in DOCUMENT_TYPES:
        integration_type, _ = DOCUMENT_TYPES[doc_type]

    # Get note links
    links = db_get_note_links(
        conn, project_id=project_name, integration_type=integration_type
    )

    # Build result with file information
    results = []
    for link in links:
        # Only include local documents (start with "local_")
        if not link.integration_type.startswith("local_"):
            continue

        # Get full file path
        file_path = DOCUMENTS_BASE_DIR / link.external_id

        # Get file metadata
        file_size = 0
        modified_date = ""
        if file_path.exists():
            stat = file_path.stat()
            file_size = stat.st_size
            modified_date = datetime.fromtimestamp(stat.st_mtime).isoformat()

        results.append(
            {
                "id": link.id,
                "project_id": link.project_id,
                "integration_type": link.integration_type,
                "external_id": link.external_id,
                "title": link.title,
                "description": link.description,
                "file_path": str(file_path),
                "file_size": file_size,
                "modified_date": modified_date,
                "created_at": link.created_at,
            }
        )

    return results


def get_document_path(link_id: int, conn: sqlite3.Connection) -> Optional[Path]:
    """Get the full file path for a document link."""
    link = db_get_note_link(conn, link_id)
    if not link:
        return None

    if not link.integration_type.startswith("local_"):
        return None

    return DOCUMENTS_BASE_DIR / link.external_id


def delete_document(
    conn: sqlite3.Connection, link_id: int, delete_file: bool = False
) -> Tuple[bool, Optional[str]]:
    """
    Delete a document link and optionally the file.

    Returns:
        (success, error_message)
    """
    try:
        link = db_get_note_link(conn, link_id)
        if not link:
            return False, "Document link not found"

        # Delete file if requested
        if delete_file:
            file_path = DOCUMENTS_BASE_DIR / link.external_id
            if file_path.exists():
                file_path.unlink()

        # Delete database link
        db_delete_note_link(conn, link_id)

        return True, None

    except Exception as e:
        return False, str(e)


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def _calculate_file_checksum(file_path: Path) -> str:
    """Calculate SHA256 checksum of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def _create_document_version(
    conn: sqlite3.Connection,
    note_link_id: int,
    file_path: str,
    description: Optional[str] = None,
    created_by: Optional[str] = None,
) -> int:
    """Create a version record for a document."""
    c = conn.cursor()

    # Get the next version number
    c.execute(
        "SELECT COALESCE(MAX(version_number), 0) + 1 FROM document_versions WHERE note_link_id = ?",
        (note_link_id,),
    )
    version_number = c.fetchone()[0]

    # Get file metadata
    file_path_obj = Path(file_path)
    file_size = file_path_obj.stat().st_size if file_path_obj.exists() else 0
    checksum = _calculate_file_checksum(file_path_obj) if file_path_obj.exists() else ""

    # Insert version record
    created_at = datetime.now().isoformat(timespec="seconds")
    c.execute(
        """
        INSERT INTO document_versions 
        (note_link_id, version_number, file_path, file_size, checksum, created_at, created_by, description)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            note_link_id,
            version_number,
            file_path,
            file_size,
            checksum,
            created_at,
            created_by,
            description or "",
        ),
    )

    conn.commit()
    return c.lastrowid


def get_document_versions(conn: sqlite3.Connection, note_link_id: int) -> List[Dict]:
    """Get all versions of a document, ordered by version number (newest first)."""
    c = conn.cursor()
    c.execute(
        """
        SELECT id, version_number, file_path, file_size, checksum, created_at, created_by, description
        FROM document_versions
        WHERE note_link_id = ?
        ORDER BY version_number DESC
    """,
        (note_link_id,),
    )

    rows = c.fetchall()
    versions = []
    for row in rows:
        versions.append(
            {
                "id": row[0],
                "version_number": row[1],
                "file_path": row[2],
                "file_size": row[3],
                "checksum": row[4],
                "created_at": row[5],
                "created_by": row[6] or "Unknown",
                "description": row[7] or "",
            }
        )

    return versions


def get_document_version(conn: sqlite3.Connection, version_id: int) -> Optional[Dict]:
    """Get a specific document version by ID."""
    c = conn.cursor()
    c.execute(
        """
        SELECT id, note_link_id, version_number, file_path, file_size, checksum, created_at, created_by, description
        FROM document_versions
        WHERE id = ?
    """,
        (version_id,),
    )

    row = c.fetchone()
    if not row:
        return None

    return {
        "id": row[0],
        "note_link_id": row[1],
        "version_number": row[2],
        "file_path": row[3],
        "file_size": row[4],
        "checksum": row[5],
        "created_at": row[6],
        "created_by": row[7] or "Unknown",
        "description": row[8] or "",
    }


def restore_document_version(
    conn: sqlite3.Connection, version_id: int, create_new_version: bool = True
) -> Tuple[bool, Optional[str]]:
    """
    Restore a document to a specific version.

    Args:
        conn: Database connection
        version_id: ID of the version to restore
        create_new_version: If True, creates a new version from current before restoring

    Returns:
        (success, error_message)
    """
    try:
        # Get version info
        version = get_document_version(conn, version_id)
        if not version:
            return False, "Version not found"

        version_path = Path(version["file_path"])
        if not version_path.exists():
            return False, f"Version file not found: {version_path}"

        # Get the current document link
        link = db_get_note_link(conn, version["note_link_id"])
        if not link:
            return False, "Document link not found"

        # Get current file path
        current_file_path = DOCUMENTS_BASE_DIR / link.external_id

        # If create_new_version is True, save current version first
        if create_new_version and current_file_path.exists():
            _create_document_version(
                conn,
                version["note_link_id"],
                str(current_file_path),
                "Auto-saved before version restore",
            )

        # Restore the version file
        shutil.copy2(version_path, current_file_path)

        # Create a new version record for the restore
        _create_document_version(
            conn,
            version["note_link_id"],
            str(current_file_path),
            f"Restored from version {version['version_number']}",
        )

        return True, None

    except Exception as e:
        return False, str(e)


def delete_document_version(
    conn: sqlite3.Connection, version_id: int, delete_file: bool = False
) -> Tuple[bool, Optional[str]]:
    """
    Delete a document version.

    Args:
        conn: Database connection
        version_id: ID of the version to delete
        delete_file: If True, also delete the version file

    Returns:
        (success, error_message)
    """
    try:
        version = get_document_version(conn, version_id)
        if not version:
            return False, "Version not found"

        # Delete file if requested
        if delete_file:
            version_path = Path(version["file_path"])
            if version_path.exists():
                version_path.unlink()

        # Delete version record
        c = conn.cursor()
        c.execute("DELETE FROM document_versions WHERE id = ?", (version_id,))
        conn.commit()

        return True, None

    except Exception as e:
        return False, str(e)
