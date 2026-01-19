#!/usr/bin/env python3
"""Terminal helpers to execute commands in a bash shell."""

from __future__ import annotations

import os
import shutil
import subprocess
from hashlib import sha256
from dataclasses import dataclass
from typing import Optional

DEFAULT_SHELL = os.environ.get("ASSISTANT_HUB_SHELL", "bash")  # Default to bash


@dataclass
class CommandResult:
    command: str
    cwd: str
    returncode: int
    stdout: str
    stderr: str
    shell_path: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0

    def summary(self) -> str:
        status = "ok" if self.ok else f"exit {self.returncode}"
        return f"[{status}] {self.command}"


def _resolve_shell() -> str:
    shell = DEFAULT_SHELL
    # Prefer bash as default
    for candidate in ("/bin/bash", "/usr/local/bin/bash", "/opt/homebrew/bin/bash"):
        if os.path.exists(candidate):
            return candidate
    # Fallback to shell from env or other options
    if shell and shutil.which(shell):
        return shutil.which(shell) or shell
    for candidate in ("/bin/zsh", "/bin/sh"):
        if os.path.exists(candidate):
            return candidate
    return "/bin/sh"


def run_bash_command(
    command: str, *, cwd: Optional[str] = None, timeout: int = 180
) -> CommandResult:
    """Run a command through bash -lc and capture output for the terminal pane."""
    shell_path = _resolve_shell()
    exec_cmd = [shell_path, "-lc", command]
    workdir = cwd or os.getcwd()
    emitter = None
    op_ctx = None
    try:
        from assistant_hub.audit.sdk import get_default_emitter, new_correlation_id
        from assistant_hub.audit.redaction import redact_payload

        emitter = get_default_emitter(agent_id="os_dashboard")
        redacted_command = redact_payload(command)
        op_ctx = emitter.operation(
            "command_execution",
            intent_type="COMMAND_INTENT",
            outcome_type="COMMAND_OUTCOME",
            message="Command execution",
            payload={"command": redacted_command, "cwd": workdir},
            correlation_id=new_correlation_id(),
        )
    except Exception:
        op_ctx = None

    if op_ctx is not None:
        with op_ctx as op:
            try:
                completed = subprocess.run(
                    exec_cmd,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=workdir,
                )
                stdout = completed.stdout
                stderr = completed.stderr
                returncode = completed.returncode
                stdout_hash = sha256(stdout.encode("utf-8")).hexdigest() if stdout else None
                stderr_hash = sha256(stderr.encode("utf-8")).hexdigest() if stderr else None
                op.add_outcome(
                    exit_code=returncode,
                    stdout_hash=stdout_hash,
                    stderr_hash=stderr_hash,
                    stdout_bytes=len(stdout.encode("utf-8")) if stdout else 0,
                    stderr_bytes=len(stderr.encode("utf-8")) if stderr else 0,
                    success=returncode == 0,
                )
            except subprocess.TimeoutExpired as exc:
                stdout = exc.stdout or ""
                stderr = (exc.stderr or "") + f"\nCommand timed out after {timeout} seconds."
                returncode = -1
                op.add_outcome(
                    exit_code=returncode,
                    error="timeout",
                    stdout_bytes=len(stdout.encode("utf-8")) if stdout else 0,
                    stderr_bytes=len(stderr.encode("utf-8")) if stderr else 0,
                    success=False,
                )
            except FileNotFoundError as exc:
                stdout = ""
                stderr = f"Unable to execute command because the shell '{shell_path}' is missing: {exc}"
                returncode = -1
                op.add_outcome(
                    exit_code=returncode,
                    error="shell_missing",
                    stderr_bytes=len(stderr.encode("utf-8")) if stderr else 0,
                    success=False,
                )
    else:
        try:
            completed = subprocess.run(
                exec_cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=workdir,
            )
            stdout = completed.stdout
            stderr = completed.stderr
            returncode = completed.returncode
        except subprocess.TimeoutExpired as exc:
            stdout = exc.stdout or ""
            stderr = (exc.stderr or "") + f"\nCommand timed out after {timeout} seconds."
            returncode = -1
        except FileNotFoundError as exc:
            stdout = ""
            stderr = f"Unable to execute command because the shell '{shell_path}' is missing: {exc}"
            returncode = -1

    return CommandResult(
        command=command,
        cwd=workdir,
        returncode=returncode,
        stdout=stdout,
        stderr=stderr,
        shell_path=shell_path,
    )
