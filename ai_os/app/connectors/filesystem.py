"""Filesystem connector for treating folders as resources."""
from __future__ import annotations

from ai_os.app.connectors.base import StorageBackedConnector


class FilesystemConnector(StorageBackedConnector):
    system_name = "filesystem"
    node_type = "document"
    doc_type = "generic"


__all__ = ["FilesystemConnector"]
