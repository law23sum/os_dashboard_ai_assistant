"""Excel Graph client stub."""
from assistant_hub.integrations.msgraph.client import GraphClient


class ExcelCloudClient:
    def __init__(self, graph: GraphClient):
        self.graph = graph

    def list_workbooks(self) -> list[dict]:
        return [{"id": "wb1", "name": "Sample.xlsx"}]
