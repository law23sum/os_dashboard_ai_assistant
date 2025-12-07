"""Lightweight Git connector placeholder."""
from __future__ import annotations

from ai_os.app.connectors.base import StorageBackedConnector


class GitConnector(StorageBackedConnector):
    system_name = "git"
    node_type = "document"
    doc_type = "generic"


__all__ = ["GitConnector"]
