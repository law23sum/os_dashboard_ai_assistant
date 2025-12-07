"""OneNote client stub."""
from assistant_hub.integrations.msgraph.client import GraphClient


class OneNoteClient:
    def __init__(self, graph: GraphClient):
        self.graph = graph

    def list_notebooks(self) -> list[dict]:
        return [{"id": "demo", "displayName": "Sample Notebook"}]
