"""Aria: narrative and communication agent."""

from __future__ import annotations

from typing import Optional
from ...db import Project
from ...core.routing import Intent
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


def handle_narrative(project: Project, intent: Optional[Intent] = None, model: str = "gpt-4.1-mini") -> str:
    """Write a user-facing narrative about the current state of a project."""
    client = get_default_client()
    
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
    
    response = client.chat(model=model, messages=messages)
    return response.choices[0].message.content
