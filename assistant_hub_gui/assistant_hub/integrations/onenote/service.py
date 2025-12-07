"""High-level OneNote workflows that combine Graph + GPT."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional

from ...ai import get_openai_client, openai_available
from ...config import get_integration_path
from ...versioning.git_async import enqueue_commit
from ..msgraph.client import GraphClient
from .client import OneNoteClient

DEFAULT_MODEL = "gpt-4o-mini"


class OneNoteService:
    """Coordinates OneNote reads/writes and local mirrors."""

    def __init__(self, *, graph_client: Optional[GraphClient] = None):
        self.graph_client = graph_client or GraphClient()
        self.client = OneNoteClient(self.graph_client)

    def mirror_page(self, page_id: str, *, actor: str = "AIC") -> Path:
        """Persist a OneNote page locally for auditing and versioning."""

        html = self.client.get_page_content(page_id)
        mirror_root = get_integration_path("onenote_mirror")
        mirror_path = mirror_root / f"page_{page_id}.html"
        mirror_path.parent.mkdir(parents=True, exist_ok=True)
        mirror_path.write_text(html, encoding="utf-8")
        enqueue_commit([str(mirror_path)], actor=actor, reason="Mirror OneNote page", tag="onenote")
        return mirror_path

    def summarize_page(self, page_id: str, *, actor: str = "AIC") -> Dict[str, str]:
        """Generate a summary of a OneNote page and update the mirror."""

        html = self.client.get_page_content(page_id)
        if not openai_available():
            raise RuntimeError("OpenAI API is not configured; cannot summarize page.")

        client = get_openai_client()
        messages = [
            {"role": "system", "content": "Summarize the OneNote page content clearly."},
            {"role": "user", "content": html},
        ]
        response = client.chat.completions.create(model=DEFAULT_MODEL, messages=messages)
        summary = response.choices[0].message.content or ""

        summary_path = self.mirror_page(page_id, actor=actor).with_suffix(".summary.txt")
        summary_path.write_text(summary, encoding="utf-8")
        enqueue_commit([str(summary_path)], actor=actor, reason="Summarize OneNote page", tag="onenote")
        return {"summary": summary}

    def rewrite_page(self, page_id: str, instruction: str, *, actor: str = "AIC") -> Dict[str, str]:
        """Rewrite a OneNote page body using GPT and push via Graph."""

        html = self.client.get_page_content(page_id)
        if not openai_available():
            raise RuntimeError("OpenAI API is not configured; cannot rewrite page.")

        client = get_openai_client()
        messages = [
            {
                "role": "system",
                "content": (
                    "You are an assistant that restructures OneNote page HTML. "
                    "Preserve equations and lists, but clean up headings and structure."
                ),
            },
            {"role": "user", "content": f"Instruction: {instruction}\n\n{html}"},
        ]
        response = client.chat.completions.create(model=DEFAULT_MODEL, messages=messages)
        rewritten = response.choices[0].message.content or html

        self.client.update_page_content(page_id, rewritten)
        mirror_path = self.mirror_page(page_id, actor=actor)
        mirror_path.write_text(rewritten, encoding="utf-8")
        enqueue_commit([str(mirror_path)], actor=actor, reason="Rewrite OneNote page", tag="onenote")
        return {"new_body": rewritten[:400]}
