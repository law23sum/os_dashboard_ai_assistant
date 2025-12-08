"""PowerPoint connector stub using shared CIR contract."""
from __future__ import annotations

from ai_os.app.connectors.base import StorageBackedConnector


class PowerPointConnector(StorageBackedConnector):
    system_name = "powerpoint"
    node_type = "presentation"
    doc_type = "ppt"


__all__ = ["PowerPointConnector"]
