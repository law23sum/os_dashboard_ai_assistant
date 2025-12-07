"""Word service."""
from __future__ import annotations

from pathlib import Path

from assistant_hub.integrations.word.local_client import summarize_docx


class WordService:
    def summarize_local(self, path: str) -> str:
        return summarize_docx(Path(path))
