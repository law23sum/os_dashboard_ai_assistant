<<<<<<< HEAD
"""Word document helpers via Microsoft Graph."""

from __future__ import annotations

from typing import Any, Dict, Optional
=======
"""Word document access through Microsoft Graph files API."""

from __future__ import annotations

from typing import Any, Dict, List
>>>>>>> develop

from ..msgraph.client import GraphClient


<<<<<<< HEAD
class GraphWordClient:
    """Wrapper for Graph file interactions focused on Word documents."""

    def __init__(self, graph_client: Optional[GraphClient] = None):
        self.graph = graph_client or GraphClient()

    def list_word_documents(self) -> Dict[str, Any]:
        # Lists drive items; callers can filter by mime type.
        return self.graph.get("/me/drive/root/children")

    def download_content(self, item_id: str) -> bytes:
        response = self.graph.get(f"/me/drive/items/{item_id}/content", expect_json=False)
        if isinstance(response, (bytes, bytearray)):
            return bytes(response)
        return b""

    def upload_content(self, item_id: str, content: bytes) -> Dict[str, Any]:
        payload = {"@microsoft.graph.conflictBehavior": "replace"}
        return self.graph.put(f"/me/drive/items/{item_id}/content", payload=content)
=======
class WordCloudClient:
    """Minimal client for working with cloud-hosted Word documents."""

    def __init__(self, graph: GraphClient | None = None):
        self.graph = graph or GraphClient()

    def list_documents(self) -> List[Dict[str, Any]]:
        return self.graph.get("/me/drive/root/children").get("value", [])

    def download_content(self, item_id: str) -> bytes:
        response = self.graph.get(f"/me/drive/items/{item_id}/content")  # type: ignore[return-value]
        return response
>>>>>>> develop
