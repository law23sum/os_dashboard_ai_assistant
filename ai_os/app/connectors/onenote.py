"""OneNote connector stub with shared contract."""
from __future__ import annotations

from ai_os.app.connectors.base import StorageBackedConnector


class OneNoteConnector(StorageBackedConnector):
    system_name = "onenote"
    node_type = "section"
    doc_type = "onenote"


__all__ = ["OneNoteConnector"]
