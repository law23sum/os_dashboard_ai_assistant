"""Sora: project and strategy agent."""

from __future__ import annotations

from ..prompts import SORA_SYSTEM_PROMPT
from ..openai_client import get_default_client


def prioritize_tasks(context: str, model: str = "gpt-4.1-mini") -> str:
    """Return prioritized recommendations for the given project context."""

    client = get_default_client()
    response = client.chat(
        model=model,
        messages=[
            {"role": "system", "content": SORA_SYSTEM_PROMPT},
            {"role": "user", "content": context},
        ],
    )
    return response.choices[0].message.content
