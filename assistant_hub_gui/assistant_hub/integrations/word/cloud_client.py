"""Word document access through Microsoft Graph files API."""

from __future__ import annotations

from typing import Any, Dict, List

from ..msgraph.client import GraphClient


class WordCloudClient:
    """Minimal client for working with cloud-hosted Word documents."""

    def __init__(self, graph: GraphClient | None = None):
        self.graph = graph or GraphClient()

    def list_documents(self) -> List[Dict[str, Any]]:
        return self.graph.get("/me/drive/root/children").get("value", [])

    def download_content(self, item_id: str) -> bytes:
        response = self.graph.get(f"/me/drive/items/{item_id}/content")  # type: ignore[return-value]
        return response
