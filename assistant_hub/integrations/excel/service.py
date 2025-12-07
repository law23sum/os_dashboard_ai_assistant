"""Excel service facade."""
from __future__ import annotations

from pathlib import Path

from assistant_hub.integrations.excel.cloud_client import ExcelCloudClient
from assistant_hub.integrations.excel.local_client import summarize_workbook


class ExcelService:
    def __init__(self, cloud: ExcelCloudClient):
        self.cloud = cloud

    def workbooks(self) -> list[dict]:
        return self.cloud.list_workbooks()

    def summarize_local(self, path: str) -> str:
        return summarize_workbook(Path(path))
