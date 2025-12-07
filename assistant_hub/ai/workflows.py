"""Example workflows that orchestrate prompts and tools."""
from __future__ import annotations

from pathlib import Path
from textwrap import dedent
from typing import Dict

from assistant_hub.ai.prompts import CLEAN_NOTEBOOK_PROMPT
from assistant_hub.core.audit import AuditLogger


def clean_notebook_workflow(nb_path: str) -> str:
    return (
        f"Workflow: clean notebook at {nb_path}.\n"
        f"Prompt: {CLEAN_NOTEBOOK_PROMPT}"
    )


def knowledge_pipeline(
    notes_path: Path,
    output_dir: Path,
    project: str,
    audit: AuditLogger,
) -> Dict[str, str]:
    """Convert raw notes into a structured, auditable deliverable."""

    output_dir.mkdir(parents=True, exist_ok=True)
    notes_text = notes_path.read_text(encoding="utf-8")

    summary = _summarize_notes(notes_text)
    action_items = _extract_action_items(notes_text)
    output_path = output_dir / f"{notes_path.stem}_structured.md"

    deliverable = dedent(
        f"""
        # Structured Brief: {notes_path.stem}

        ## Project
        {project}

        ## Highlights
        {summary}

        ## Action Items
        {action_items}
        """
    ).strip() + "\n"

    output_path.write_text(deliverable, encoding="utf-8")

    audit_entry = audit.record(
        action="knowledge-pipeline",
        description="Transformed notes into a structured, versionable brief",
        metadata={
            "project": project,
            "source": str(notes_path),
            "output": str(output_path),
        },
        commit_paths=[str(output_path)],
    )

    return {
        "project": project,
        "source": str(notes_path),
        "output": str(output_path),
        "audit_log": str(audit.log_path),
        "commit_status": audit_entry.commit_status or {"status": "not requested"},
    }


def _summarize_notes(notes_text: str) -> str:
    chunks = [line.strip() for line in notes_text.splitlines() if line.strip()]
    if not chunks:
        return "- No content found"
    top = chunks[:3]
    return "\n".join(f"- {line}" for line in top)


def _extract_action_items(notes_text: str) -> str:
    lines = [line.strip() for line in notes_text.splitlines() if line.strip()]
    tasks = [line for line in lines if line.lower().startswith("todo") or line.endswith("?")]
    if not tasks:
        return "- No explicit tasks detected; review highlights."
    return "\n".join(f"- {task}" for task in tasks)
