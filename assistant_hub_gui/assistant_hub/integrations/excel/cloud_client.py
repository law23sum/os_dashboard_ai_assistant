"""Excel endpoints via Microsoft Graph."""

from __future__ import annotations

from typing import Any, Dict, List

from ..msgraph.client import GraphClient


class ExcelCloudClient:
    """Interact with Excel workbooks stored in OneDrive or SharePoint."""

    def __init__(self, graph: GraphClient | None = None):
        self.graph = graph or GraphClient()

    def list_workbooks(self) -> List[Dict[str, Any]]:
        return self.graph.get("/me/drive/root/children").get("value", [])

    def list_worksheets(self, item_id: str) -> List[Dict[str, Any]]:
        return self.graph.get(f"/me/drive/items/{item_id}/workbook/worksheets").get("value", [])

    def get_range(self, item_id: str, worksheet_id: str, address: str) -> Dict[str, Any]:
        return self.graph.get(
            f"/me/drive/items/{item_id}/workbook/worksheets/{worksheet_id}/range(address='{address}')"
        )

    def update_range(self, item_id: str, worksheet_id: str, address: str, values: List[List[Any]]) -> None:
        self.graph.patch(
            f"/me/drive/items/{item_id}/workbook/worksheets/{worksheet_id}/range(address='{address}')",
            json={"values": values},
        )
