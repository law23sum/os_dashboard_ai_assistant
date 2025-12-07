"""Excel interactions via Microsoft Graph."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..msgraph.client import GraphClient


class GraphExcelClient:
    """Wrapper for Graph Excel endpoints operating on OneDrive/SharePoint files."""

    def __init__(self, graph_client: Optional[GraphClient] = None):
        self.graph = graph_client or GraphClient()

    def list_workbooks(self) -> List[Dict[str, Any]]:
        response = self.graph.get("/me/drive/root/children")
        items = response.get("value", [])
        return [item for item in items if item.get("file", {}).get("mimeType") == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]

    def list_worksheets(self, item_id: str) -> List[Dict[str, Any]]:
        response = self.graph.get(f"/me/drive/items/{item_id}/workbook/worksheets")
        return response.get("value", [])

    def get_range(self, item_id: str, worksheet_id: str, address: str) -> Dict[str, Any]:
        return self.graph.get(f"/me/drive/items/{item_id}/workbook/worksheets/{worksheet_id}/range(address='{address}')")

    def update_range(self, item_id: str, worksheet_id: str, address: str, values: List[List[Any]]) -> Dict[str, Any]:
        payload = {"values": values}
        return self.graph.patch(
            f"/me/drive/items/{item_id}/workbook/worksheets/{worksheet_id}/range(address='{address}')",
            payload,
        )
