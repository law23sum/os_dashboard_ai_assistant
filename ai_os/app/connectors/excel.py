"""Stub Excel connector leveraging the shared storage-backed pattern."""
from __future__ import annotations

from ai_os.app.connectors.base import StorageBackedConnector


class ExcelConnector(StorageBackedConnector):
    system_name = "excel"
    node_type = "spreadsheet"
    doc_type = "excel"


__all__ = ["ExcelConnector"]
