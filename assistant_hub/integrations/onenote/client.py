"""OneNote client built on top of Microsoft Graph."""

from __future__ import annotations

from typing import Any, Dict, List

from ..msgraph.client import GraphClient


class OneNoteClient:
    """Expose OneNote-specific Graph endpoints."""

    def __init__(self, graph: GraphClient | None = None):
        self.graph = graph or GraphClient()

    def list_notebooks(self) -> List[Dict[str, Any]]:
        return self.graph.get("/me/onenote/notebooks").get("value", [])

    def list_sections(self, notebook_id: str) -> List[Dict[str, Any]]:
        return self.graph.get(f"/me/onenote/notebooks/{notebook_id}/sections").get(
            "value", []
        )

    def list_pages(self, section_id: str) -> List[Dict[str, Any]]:
        return self.graph.get(f"/me/onenote/sections/{section_id}/pages").get(
            "value", []
        )

    def get_page_html(self, page_id: str) -> str:
        return self.graph.get(f"/me/onenote/pages/{page_id}/content")  # type: ignore[return-value]

    def update_page_html(self, page_id: str, html: str) -> None:
        payload = [{"target": "body", "action": "replace", "content": html}]
        self.graph.patch(f"/me/onenote/pages/{page_id}/content", json=payload)

    # Backwards compatibility methods
    def get_page_content(self, page_id: str) -> str:
        """Get page content (backwards compatibility alias for get_page_html)."""
        return self.get_page_html(page_id)

    def update_page_content(self, page_id: str, html: str) -> None:
        """Update page content (backwards compatibility alias for update_page_html)."""
        self.update_page_html(page_id, html)
