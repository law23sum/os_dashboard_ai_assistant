"""Connector for the lightweight notes scratch layer."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from ai_os.app.cir import CIRDocument
from ai_os.app.connectors.base import ResourceRef, StorageBackedConnector


class NotesConnector(StorageBackedConnector):
    system_name = "notes"
    node_type = "note"
    doc_type = "note"

    def write(
        self, resource_id: str, cir: CIRDocument, operations: Optional[Dict[str, Any]] = None
    ) -> ResourceRef:
        # allow title/text to be overridden by operations if provided
        if operations:
            if "title" in operations:
                cir.root.title = operations["title"]
            if "text" in operations:
                cir.root.text = operations["text"]
        return super().write(resource_id, cir, operations)


__all__ = ["NotesConnector", "ResourceRef"]
