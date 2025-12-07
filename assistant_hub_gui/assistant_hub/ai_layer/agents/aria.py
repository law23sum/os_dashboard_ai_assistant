"""Aria: narrative and communication agent."""

from __future__ import annotations

from ..prompts import ARIA_SYSTEM_PROMPT
from ..openai_client import get_default_client


def polish_text(text: str, model: str = "gpt-4.1-mini") -> str:
    """Polish user-facing text while preserving intent."""

    client = get_default_client()
    response = client.chat(
        model=model,
        messages=[
            {"role": "system", "content": ARIA_SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ],
    )
    return response.choices[0].message.content
