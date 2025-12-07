"""High-level Word document workflows powered by GPT."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional

from ...ai import get_openai_client, openai_available
from ...versioning.git_async import enqueue_commit
from ..msgraph.client import GraphClient
from .cloud_client import GraphWordClient
from .local_client import read_document_text, write_document_text

DEFAULT_MODEL = "gpt-4o-mini"


class WordService:
    """Coordinates cloud/local Word operations."""

    def __init__(self, *, graph_client: Optional[GraphClient] = None):
        self.graph_client = graph_client or GraphClient()
        self.cloud = GraphWordClient(self.graph_client)

    def rewrite_local_document(
        self,
        path: str | Path,
        *,
        instruction: str,
        actor: str = "Aria",
    ) -> Dict[str, str]:
        """Rewrite a local document using GPT and commit the change."""

        original = read_document_text(path)
        if not openai_available():
            raise RuntimeError("OpenAI API is not configured; cannot rewrite document.")

        client = get_openai_client()
        messages = [
            {"role": "system", "content": "Rewrite the document to follow the instruction."},
            {"role": "user", "content": f"Instruction: {instruction}\n\nDocument:\n{original}"},
        ]
        response = client.chat.completions.create(model=DEFAULT_MODEL, messages=messages)
        rewritten = response.choices[0].message.content or original
        write_document_text(path, rewritten)
        enqueue_commit([str(path)], actor=actor, reason="Rewrite Word document", tag="word")
        return {"preview": rewritten[:400]}

    def draft_from_outline(
        self,
        outline: str,
        *,
        actor: str = "Aria",
    ) -> str:
        """Return a drafted document body from an outline."""

        if not openai_available():
            raise RuntimeError("OpenAI API is not configured; cannot draft content.")

        client = get_openai_client()
        messages = [
            {"role": "system", "content": "Draft a clear, concise document based on the outline."},
            {"role": "user", "content": outline},
        ]
        response = client.chat.completions.create(model=DEFAULT_MODEL, messages=messages)
        return response.choices[0].message.content or ""
