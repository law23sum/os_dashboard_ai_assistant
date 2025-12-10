"""OneNote integration wrapper for GUI."""

import os
from pathlib import Path
from typing import Dict
import sqlite3

from .base import BaseIntegration, IntegrationStatus
from .onenote.service import OneNoteService
from .onenote import OneNoteClient
from .msgraph import GraphClient


class OneNoteIntegration(BaseIntegration):
    """Integration for Microsoft OneNote."""

    def __init__(self, conn: sqlite3.Connection, mirror_root: str = None):
        super().__init__(conn, "OneNote", "onenote")
        self.mirror_root = mirror_root or os.path.expanduser(
            "~/.assistant_hub/onenote_mirror"
        )
        self.client = None
        self.service = None

    def authenticate(self) -> bool:
        """Authenticate with Microsoft Graph for OneNote."""
        try:
            graph_client = GraphClient()
            self.client = OneNoteClient(graph_client)
            self.service = OneNoteService(self.mirror_root, self.client)

            # Try to list notebooks to verify auth
            notebooks = self.client.list_notebooks()
            self.update_status(True, item_count=len(notebooks) if notebooks else 0)
            return True
        except Exception as e:
            error_msg = str(e)
            if "credentials" in error_msg.lower() or "auth" in error_msg.lower():
                self.update_status(
                    False,
                    "Not authenticated. Please configure Microsoft Graph credentials.",
                )
            else:
                self.update_status(False, error_msg)
            return False

    def sync(self) -> int:
        """Sync OneNote notebooks, sections, and pages."""
        if not self.authenticate():
            return 0

        count = 0
        try:
            notebooks = self.client.list_notebooks()
            if not notebooks:
                self.update_status(True, item_count=0)
                return 0

            for notebook in notebooks:
                notebook_id = notebook.get("id")
                notebook_name = notebook.get("displayName", "Unknown")
                if not notebook_id:
                    continue

                sections = self.client.list_sections(notebook_id)
                for section in sections:
                    section_id = section.get("id")
                    section_name = section.get("displayName", "Unknown")
                    if not section_id:
                        continue

                    pages = self.client.list_pages(section_id)
                    for page in pages:
                        page_id = page.get("id")
                        page_title = page.get("title", "Untitled")
                        if not page_id:
                            continue

                        self.record_item(
                            external_id=page_id,
                            item_kind="page",
                            title=f"{notebook_name} > {section_name} > {page_title}",
                            data={
                                "notebook_id": notebook_id,
                                "notebook_name": notebook_name,
                                "section_id": section_id,
                                "section_name": section_name,
                                "page_id": page_id,
                                "page_title": page_title,
                            },
                        )
                        count += 1

            self.update_status(True, item_count=count)
            return count
        except Exception as e:
            self.update_status(False, str(e))
            return 0

    def get_status(self) -> IntegrationStatus:
        """Get current status."""
        if not hasattr(self, "_status") or not self._status:
            self._status = IntegrationStatus()
        return self._status
