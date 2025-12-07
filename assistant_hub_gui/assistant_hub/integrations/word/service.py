"""High-level Word document flows."""
from __future__ import annotations

from typing import Dict

from assistant_hub.versioning import enqueue_git_commit

from .cloud_client import CloudWordClient
from .local_client import LocalDocument


def draft_local_revision(path: str, draft: str, *, actor: str = "Aria", note: str = "") -> Dict[str, str]:
    """Write a revision text file next to an existing document and auto-commit."""
    document = LocalDocument(path)
    revision_path = document.write_revision(draft, note=note or f"Drafted by {actor}")
    enqueue_git_commit([revision_path], actor=actor, reason="Word draft", tag="word")
    return {"document": str(document.path), "revision_path": str(revision_path)}


def upload_cloud_revision(client: CloudWordClient, drive_item_id: str, content: bytes, *, actor: str = "Aria") -> Dict[str, str]:
    """Upload a new document version to OneDrive/SharePoint and record metadata."""
    response = client.upload_document(drive_item_id, content)
    return {"drive_item_id": drive_item_id, "status": response.get("id", "uploaded"), "actor": actor}
