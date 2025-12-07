"""Word/Docx helpers via Microsoft Graph."""
from __future__ import annotations

from typing import Any, Dict

from ..msgraph import GraphClient


class CloudWordClient:
    """Minimal helpers for downloading and uploading Word files via Graph."""

    def __init__(self, graph_client: GraphClient) -> None:
        self.graph_client = graph_client

    def download_document(self, drive_item_id: str) -> bytes:
        response = self.graph_client.get(f"/me/drive/items/{drive_item_id}/content")
        return response.content

    def upload_document(self, drive_item_id: str, content: bytes) -> Dict[str, Any]:
        response = self.graph_client.put(
            f"/me/drive/items/{drive_item_id}/content",
            data=content,
            headers={"Content-Type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"},
        )
        return response.json()
