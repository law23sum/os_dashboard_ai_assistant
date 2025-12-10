"""Sora: project and strategy agent."""

from __future__ import annotations

from typing import Optional
from ...db import Project
from ...core.routing import Intent
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


def handle_planning(
    project: Project, intent: Optional[Intent] = None, model: str = "gpt-4.1-mini"
) -> str:
    """Plan the next steps for a project, suggesting concrete actions and integration usage."""
    client = get_default_client()

    context = f"Project: {project.name}\nDescription: {project.description}\nStatus: {project.status}"
    if intent and intent.context:
        context += f"\n\nUser request: {intent.context}"

    messages = [
        {"role": "system", "content": SORA_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                "You are planning the next steps for this project. Suggest a concrete, ordered list of "
                "actions, including which integrations (Excel/OneNote/Word/Git) to use.\n\n"
                f"{context}"
            ),
        },
    ]

    response = client.chat(model=model, messages=messages)
    return response.choices[0].message.content
