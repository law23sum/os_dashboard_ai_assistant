#!/usr/bin/env python3
"""Document management module for handling file uploads and organization."""

import os
import shutil
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
    safe_project = "".join(c for c in project_name if c.isalnum() or c in (' ', '-', '_')).strip()
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
        filename = filename.replace(char, '_')
    # Remove leading/trailing spaces and dots
    filename = filename.strip(' .')
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
    overwrite: bool = False
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
        project = Project(name=project_name, description="", status="active", priority="MEDIUM")
        db_upsert_project(conn, project)
        
        # Get destination directory
        dest_dir = get_document_directory(project_name, doc_type)
        
        # Sanitize filename
        safe_filename = sanitize_filename(source_path.name)
        dest_path = dest_dir / safe_filename
        
        # Check if file already exists
        if dest_path.exists() and not overwrite:
            return False, f"File already exists: {safe_filename}. Use overwrite=True to replace.", None
        
        # Copy file
        shutil.copy2(source_path, dest_path)
        
        # Create relative path for storage (relative to documents base)
        safe_project = "".join(c for c in project_name if c.isalnum() or c in (' ', '-', '_')).strip()
        if not safe_project:
            safe_project = "General"
        relative_path = f"{safe_project}/{doc_type}/{safe_filename}"
        
        # Get integration type
        integration_type, _ = DOCUMENT_TYPES[doc_type]
        
        # Use provided title or filename
        display_title = title or safe_filename
        
        # Create database link
        link_id = db_create_note_link(
            conn=conn,
            project_id=project_name,
            integration_type=integration_type,
            external_id=relative_path,
            title=display_title,
            description=description or ""
        )
        
        # Auto-commit uploaded file to Git
        try:
            enqueue_commit(
                paths=[str(dest_path)],
                actor="User",
                tag="document-upload",
                reason=f"Upload {doc_type} document '{safe_filename}' to project '{project_name}'"
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
    doc_type: Optional[str] = None
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
    links = db_get_note_links(conn, project_id=project_name, integration_type=integration_type)
    
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
        
        results.append({
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
        })
    
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
    conn: sqlite3.Connection,
    link_id: int,
    delete_file: bool = False
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
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

