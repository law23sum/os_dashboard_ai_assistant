"""OneNote-specific Graph client helpers."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..msgraph.client import GraphClient


class OneNoteClient:
    """Thin wrapper around the Graph OneNote endpoints."""

    def __init__(self, graph_client: Optional[GraphClient] = None):
        self.graph = graph_client or GraphClient()

    def list_notebooks(self) -> List[Dict[str, Any]]:
        response = self.graph.get("/me/onenote/notebooks")
        return response.get("value", [])

    def list_sections(self, notebook_id: str) -> List[Dict[str, Any]]:
        response = self.graph.get(f"/me/onenote/notebooks/{notebook_id}/sections")
        return response.get("value", [])

    def list_pages(self, section_id: str) -> List[Dict[str, Any]]:
        response = self.graph.get(f"/me/onenote/sections/{section_id}/pages")
        return response.get("value", [])

    def get_page_content(self, page_id: str) -> str:
        content_bytes = self.graph.get(f"/me/onenote/pages/{page_id}/content", expect_json=False)
        if isinstance(content_bytes, (bytes, bytearray)):
            return content_bytes.decode("utf-8", errors="ignore")
        return str(content_bytes)

    def update_page_content(self, page_id: str, html: str) -> None:
        payload = [
            {
                "target": "body",
                "action": "replace",
                "content": html,
            }
        ]
        self.graph.patch(f"/me/onenote/pages/{page_id}/content", payload)
