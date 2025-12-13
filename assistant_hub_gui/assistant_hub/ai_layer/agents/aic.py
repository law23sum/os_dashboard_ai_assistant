"""AIC: architecture and critique agent."""

from __future__ import annotations

from typing import Optional
from ...db import Project
from ...core.routing import Intent
from ..prompts import AIC_SYSTEM_PROMPT
from ..openai_client import chat


def plan_actions(context: str, model: str = "gpt-5-mini") -> str:
    """Generate a high-level plan for the provided context."""

    return chat(
        model,
        messages=[
            {"role": "system", "content": AIC_SYSTEM_PROMPT},
            {"role": "user", "content": context},
        ],
    )


def handle_report(
    project: Project, intent: Optional[Intent] = None, model: str = "gpt-5-mini"
) -> str:
    """Generate a high-level report about a project, focusing on structure, automations, and next actions."""

    context = f"Project: {project.name}\nDescription: {project.description}\nStatus: {project.status}"
    if intent and intent.context:
        context += f"\n\nUser request: {intent.context}"

    messages = [
        {"role": "system", "content": AIC_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                "Generate a high-level report about the following project, focusing on structure, "
                "possible automations (Excel/OneNote/Word), and next actions.\n\n"
                f"{context}"
            ),
        },
    ]

    return chat(model, messages)
