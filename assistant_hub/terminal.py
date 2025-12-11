#!/usr/bin/env python3
"""Terminal helpers to execute commands in a bash shell."""

from __future__ import annotations

import os
import shutil
import subprocess
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
