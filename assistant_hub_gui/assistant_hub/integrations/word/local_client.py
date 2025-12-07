"""Local Word document helpers using python-docx."""

from __future__ import annotations

from typing import Optional

from docx import Document


def load_document(path: str) -> Document:
    return Document(path)


def save_document(doc: Document, path: str) -> None:
    doc.save(path)
