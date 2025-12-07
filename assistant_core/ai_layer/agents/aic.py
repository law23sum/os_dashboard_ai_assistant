"""AIC: architecture and critique agent."""

from __future__ import annotations

from typing import Optional
from ...db import Project
from ...core.routing import Intent
from ..prompts import AIC_SYSTEM_PROMPT
from ..openai_client import get_default_client


def plan_actions(context: str, model: str = "gpt-4.1-mini") -> str:
    """Generate a high-level plan for the provided context."""

    client = get_default_client()
    response = client.chat(
        model=model,
        messages=[
            {"role": "system", "content": AIC_SYSTEM_PROMPT},
            {"role": "user", "content": context},
        ],
    )
    return response.choices[0].message.content


def handle_report(project: Project, intent: Optional[Intent] = None, model: str = "gpt-4.1-mini") -> str:
    """Generate a high-level report about a project, focusing on structure, automations, and next actions."""
    client = get_default_client()
    
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
    
    response = client.chat(model=model, messages=messages)
    return response.choices[0].message.content
