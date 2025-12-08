"""Stub Word connector following the shared interface."""
from __future__ import annotations

from ai_os.app.connectors.base import StorageBackedConnector


class WordConnector(StorageBackedConnector):
    system_name = "word"
    node_type = "document"
    doc_type = "word"


__all__ = ["WordConnector"]
