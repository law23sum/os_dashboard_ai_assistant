"""Local Word document helpers using python-docx."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional

from docx import Document


def load_document(path: str) -> Document:
    return Document(path)


def save_document(doc: Document, path: str) -> None:
    doc.save(path)


class LocalDocument:
    """Utility wrapper for a Word document on disk (backwards compatibility)."""

    def __init__(self, path: str) -> None:
        self.path = Path(path)

    def read_text(self) -> str:
        if not self.path.exists():
            return ""
        return self.path.read_text(encoding="utf-8")

    def write_revision(self, content: str, *, note: str = "") -> Path:
        revision_path = self.path.with_suffix(self.path.suffix + ".revision.txt")
        revision_path.write_text(f"Note: {note}\n\n{content}", encoding="utf-8")
        return revision_path

    def metadata(self) -> Dict[str, str]:
        return {"path": str(self.path), "exists": str(self.path.exists())}
