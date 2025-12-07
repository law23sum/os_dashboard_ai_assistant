"""Example workflows that orchestrate prompts and tools."""
from __future__ import annotations

from assistant_hub.ai.prompts import CLEAN_NOTEBOOK_PROMPT


def clean_notebook_workflow(nb_path: str) -> str:
    return (
        f"Workflow: clean notebook at {nb_path}.\n"
        f"Prompt: {CLEAN_NOTEBOOK_PROMPT}"
    )
