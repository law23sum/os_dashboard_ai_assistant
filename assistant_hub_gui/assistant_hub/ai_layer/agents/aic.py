"""AIC: architecture and critique agent."""

from __future__ import annotations

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
