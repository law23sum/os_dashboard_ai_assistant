"""High-level OneNote operations that pair Graph with OpenAI."""

from __future__ import annotations

import os
from pathlib import Path
from typing import List

from ...ai_layer.tools import rewrite_html, summarize_text
from ..msgraph.client import GraphClient
from .client import OneNoteClient


class OneNoteService:
    """Encapsulate OneNote read/write flows and local mirroring."""

    def __init__(self, mirror_root: str, client: OneNoteClient | None = None):
        self.client = client or OneNoteClient(GraphClient())
        self.mirror_root = Path(mirror_root)

    def mirror_page(self, page_id: str) -> Path:
        html = self.client.get_page_html(page_id)
        mirror_path = self.mirror_root / f"page_{page_id}.html"
        mirror_path.parent.mkdir(parents=True, exist_ok=True)
        mirror_path.write_text(html, encoding="utf-8")
        return mirror_path

    def clean_page(self, page_id: str, actor: str = "AIC") -> Path:
        html = self.client.get_page_html(page_id)
        cleaned = rewrite_html(html, "Improve structure and clarity for OneNote")
        self.client.update_page_html(page_id, cleaned)
        mirror_path = self.mirror_root / f"page_{page_id}.html"
        mirror_path.parent.mkdir(parents=True, exist_ok=True)
        mirror_path.write_text(cleaned, encoding="utf-8")
        return mirror_path

    def clean_section(self, section_id: str, actor: str = "AIC") -> List[str]:
        paths: List[str] = []
        for page in self.client.list_pages(section_id):
            page_id = page.get("id")
            if not page_id:
                continue
            path = self.clean_page(page_id, actor=actor)
            paths.append(str(path))
        return paths

    def summarize_page(self, page_id: str) -> Path:
        html = self.client.get_page_html(page_id)
        summary = summarize_text(html, style="concise")
        summary_path = self.mirror_root / f"page_{page_id}_summary.txt"
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        summary_path.write_text(summary, encoding="utf-8")
        return summary_path
