"""Git integration endpoints for change monitoring widgets."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import List

from fastapi import APIRouter
from pydantic import BaseModel
from backend_api.db import db_session

router = APIRouter()

REPO_ROOT = Path(__file__).resolve().parents[2]


class ChangeLogResponse(BaseModel):
    working_tree: str
    recent_commits: str
    agent_activity: str


def _run_git_command(args: List[str], fallback: str) -> str:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=REPO_ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        output = result.stdout.strip()
        return output or fallback
    except (subprocess.CalledProcessError, FileNotFoundError):
        return fallback


def _fetch_agent_activity(limit: int = 10) -> str:
    query = """
        SELECT agent, action_type, output_summary, created_at
        FROM agent_runs
        ORDER BY datetime(created_at) DESC
        LIMIT ?
    """
    try:
        with db_session() as conn:
            rows = conn.execute(query, (limit,)).fetchall()
    except Exception:
        rows = []
    if not rows:
        return "No recent agent commands yet."
    lines = []
    for row in rows:
        timestamp = row["created_at"] or ""
        agent = row["agent"] or "agent"
        action = row["action_type"] or "activity"
        summary = row["output_summary"] or ""
        snippet = summary.splitlines()[0] if summary else ""
        lines.append(f"[{timestamp}] {agent}: {action} {snippet}".strip())
    if lines:
        return "\n".join(lines)
    return "No recent agent commands yet."


@router.get("/git/change-log", response_model=ChangeLogResponse)
async def get_change_log() -> ChangeLogResponse:
    working_tree = _run_git_command(
        ["status", "--short"],
        "Working tree clean.",
    )
    recent_commits = _run_git_command(
        ["log", "-n", "5", "--pretty=format:%h %s (%cr)"],
        "No commits available.",
    )
    agent_activity = _fetch_agent_activity()
    return ChangeLogResponse(
        working_tree=working_tree,
        recent_commits=recent_commits,
        agent_activity=agent_activity,
    )
