"""OneNote client built on top of the Microsoft Graph API."""
from __future__ import annotations

from typing import Any, Dict, List

from ..msgraph import GraphClient


class OneNoteClient:
    """Lightweight wrapper for common OneNote Graph endpoints."""

    def __init__(self, graph_client: GraphClient) -> None:
        self.graph_client = graph_client

    def list_notebooks(self) -> List[Dict[str, Any]]:
        response = self.graph_client.get("/me/onenote/notebooks")
        return response.json().get("value", [])

    def list_sections(self, notebook_id: str) -> List[Dict[str, Any]]:
        response = self.graph_client.get(f"/me/onenote/notebooks/{notebook_id}/sections")
        return response.json().get("value", [])

    def list_pages(self, section_id: str) -> List[Dict[str, Any]]:
        response = self.graph_client.get(f"/me/onenote/sections/{section_id}/pages")
        return response.json().get("value", [])

    def get_page_content(self, page_id: str) -> str:
        response = self.graph_client.get(f"/me/onenote/pages/{page_id}/content")
        return response.text

    def update_page_content(self, page_id: str, html: str) -> None:
        payload = [
            {
                "target": "body",
                "action": "replace",
                "content": html,
            }
        ]
        self.graph_client.patch(
            f"/me/onenote/pages/{page_id}/content",
            json=payload,
            headers={"Content-Type": "application/json"},
        )
