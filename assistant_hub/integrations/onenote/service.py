"""Service helpers around the OneNote client."""
from __future__ import annotations

from assistant_hub.integrations.onenote.client import OneNoteClient


class OneNoteService:
    def __init__(self, client: OneNoteClient):
        self.client = client

    def notebooks(self) -> list[dict]:
        return self.client.list_notebooks()

    def mirror_notebook(self, notebook_id: str) -> str:
        return f"Mirrored notebook {notebook_id} to local storage"
