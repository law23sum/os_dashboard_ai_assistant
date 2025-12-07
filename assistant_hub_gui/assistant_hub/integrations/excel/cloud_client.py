"""Excel integration via Microsoft Graph (OneDrive/SharePoint)."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..msgraph import GraphClient


class CloudExcelClient:
    """Minimal wrapper over Graph Excel APIs."""

    def __init__(self, graph_client: GraphClient) -> None:
        self.graph_client = graph_client

    def list_workbooks(self) -> List[Dict[str, Any]]:
        response = self.graph_client.get("/me/drive/root/children")
        return [item for item in response.json().get("value", []) if item.get("name", "").endswith(".xlsx")]

    def list_worksheets(self, drive_item_id: str) -> List[Dict[str, Any]]:
        response = self.graph_client.get(f"/me/drive/items/{drive_item_id}/workbook/worksheets")
        return response.json().get("value", [])

    def get_range(self, drive_item_id: str, worksheet_id: str, address: str) -> Dict[str, Any]:
        response = self.graph_client.get(
            f"/me/drive/items/{drive_item_id}/workbook/worksheets/{worksheet_id}/range(address='{address}')"
        )
        return response.json()

    def update_range(
        self,
        drive_item_id: str,
        worksheet_id: str,
        address: str,
        values: List[List[Any]],
    ) -> Dict[str, Any]:
        payload = {"values": values}
        response = self.graph_client.patch(
            f"/me/drive/items/{drive_item_id}/workbook/worksheets/{worksheet_id}/range(address='{address}')",
            json=payload,
        )
        return response.json()

    def call_function(
        self, drive_item_id: str, function_name: str, arguments: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        response = self.graph_client.post(
            f"/me/drive/items/{drive_item_id}/workbook/functions/{function_name}",
            json=arguments or {},
        )
        return response.json()
