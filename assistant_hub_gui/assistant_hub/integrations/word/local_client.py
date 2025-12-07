"""Local Word document utilities using python-docx when available."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

try:
    import docx  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    docx = None  # type: ignore


class LocalWordError(RuntimeError):
    """Raised when python-docx is missing or a doc cannot be processed."""


def require_docx() -> None:
    if docx is None:
        raise LocalWordError("python-docx is required for local Word operations.")


def read_document_text(path: str | Path) -> str:
    require_docx()
    document = docx.Document(Path(path))
    return "\n".join(paragraph.text for paragraph in document.paragraphs)


def write_document_text(path: str | Path, text: str) -> None:
    require_docx()
    document = docx.Document()
    for line in text.splitlines():
        document.add_paragraph(line)
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    document.save(output_path)
