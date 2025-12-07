"""Word document helper."""
from pathlib import Path


def summarize_docx(path: Path) -> str:
    return f"Summarized Word doc at {path}"
