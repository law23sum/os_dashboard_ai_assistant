"""Aria: narrative and communication agent."""

from __future__ import annotations

from typing import Optional
from ...db import Project
from ...core.routing import Intent
from ..prompts import ARIA_SYSTEM_PROMPT
from ..openai_client import chat


def polish_text(text: str, model: str = "gpt-5-mini") -> str:
    """Polish user-facing text while preserving intent."""

    return chat(
        model,
        messages=[
            {"role": "system", "content": ARIA_SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ],
    )


def handle_narrative(
    project: Project, intent: Optional[Intent] = None, model: str = "gpt-5-mini"
) -> str:
    """Write a user-facing narrative about the current state of a project."""

    context = f"Project: {project.name}\nDescription: {project.description}\nStatus: {project.status}"
    if intent and intent.context:
        context += f"\n\nUser request: {intent.context}"

    messages = [
        {"role": "system", "content": ARIA_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                "Write a user-facing narrative about the current state of this project. "
                "Explain it clearly and engagingly.\n\n"
                f"{context}"
            ),
        },
    ]

    return chat(model, messages)
