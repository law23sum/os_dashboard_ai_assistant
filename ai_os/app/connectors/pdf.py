"""PDF connector stub that normalizes PDFs into CIR."""
from __future__ import annotations

from ai_os.app.connectors.base import StorageBackedConnector


class PDFConnector(StorageBackedConnector):
    system_name = "pdf"
    node_type = "pdf"
    doc_type = "pdf"


__all__ = ["PDFConnector"]
