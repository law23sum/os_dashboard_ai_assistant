"""Terminal command runner API."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from assistant_hub.terminal import run_bash_command
from assistant_hub.command_catalog import command_catalog

router = APIRouter()


class TerminalCommandRequest(BaseModel):
    command: str
    cwd: Optional[str] = None
    timeout: Optional[int] = None


@router.get("/commands")
async def get_command_catalog():
    """Return curated command metadata for the Tools page."""

    return command_catalog()


@router.post("/")
async def execute_terminal_command(payload: TerminalCommandRequest):
    """Execute a shell command and stream the result back to the client."""

    command = payload.command.strip()
    if not command:
        raise HTTPException(status_code=400, detail="Command cannot be empty")

    result = run_bash_command(
        command,
        cwd=payload.cwd,
        timeout=payload.timeout or 180,
    )
    return {
        "command": command,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "exit_code": result.returncode,
        "shell": result.shell_path,
        "cwd": result.cwd,
        "ok": result.ok,
    }
