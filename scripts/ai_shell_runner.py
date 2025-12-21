#!/usr/bin/env python3
"""
Bidirectional shell ↔ OpenAI bridge using the Responses API shell tool.

Usage:
    python scripts/ai_shell_runner.py "list orphaned git branches"

This script loops until the model finishes. Each time the model emits a
``shell_call`` item the requested commands are executed locally (with
timeouts) and the raw stdout/stderr/exit codes are fed back via
``shell_call_output`` payloads.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from openai import OpenAI


@dataclass
class CmdResult:
    """Container for shell command results."""

    command: str
    stdout: str
    stderr: str
    exit_code: Optional[int]
    timed_out: bool


class ShellExecutor:
    """Executes commands inside the user-specified working directory."""

    def __init__(self, *, cwd: Path, default_timeout: float = 60.0) -> None:
        self.cwd = cwd
        self.default_timeout = default_timeout

    def run(self, command: str, timeout: Optional[float] = None) -> CmdResult:
        proc = subprocess.Popen(
            command,
            cwd=str(self.cwd),
            shell=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        deadline = timeout or self.default_timeout
        try:
            stdout, stderr = proc.communicate(timeout=deadline)
            return CmdResult(command, stdout or "", stderr or "", proc.returncode, False)
        except subprocess.TimeoutExpired:
            proc.kill()
            stdout, stderr = proc.communicate()
            return CmdResult(command, stdout or "", stderr or "", proc.returncode, True)


class AIShellBridge:
    """Thin wrapper around the Responses API shell tool."""

    def __init__(
        self,
        *,
        model: str,
        instructions: str,
        shell: ShellExecutor,
        max_steps: int = 8,
    ) -> None:
        self.client = OpenAI()
        self.model = model
        self.instructions = instructions
        self.shell = shell
        self.max_steps = max_steps

    def run(self, prompt: str) -> None:
        """Run the agent loop until completion or max-steps reached."""
        response_id: Optional[str] = None
        follow_up_inputs: Optional[List[Dict[str, Any]]] = None

        for step in range(1, self.max_steps + 1):
            if response_id:
                response = self.client.responses.create(
                    model=self.model,
                    response_id=response_id,
                    input=follow_up_inputs or [],
                )
            else:
                response = self.client.responses.create(
                    model=self.model,
                    instructions=self.instructions,
                    input=prompt,
                    tools=[{"type": "shell"}],
                )

            response_id = response.id
            follow_up_inputs = None

            shell_calls = self._collect_shell_calls(response)
            messages = self._collect_assistant_text(response)

            if messages:
                print("\n".join(messages))

            if not shell_calls:
                return

            print(f"\n[agent] step {step}: executing {len(shell_calls)} shell call(s)...")
            follow_up_inputs = self._run_shell_calls(shell_calls)

        print(
            f"\n[agent] Reached max step count ({self.max_steps}) before completion. "
            "Run again if additional work is required."
        )

    def _collect_shell_calls(self, response) -> List[Dict[str, Any]]:
        calls: List[Dict[str, Any]] = []
        for item in getattr(response, "output", []) or []:
            payload = self._to_dict(item)
            if payload.get("type") == "shell_call":
                calls.append(payload)
        return calls

    def _collect_assistant_text(self, response) -> List[str]:
        texts: List[str] = []
        for item in getattr(response, "output", []) or []:
            payload = self._to_dict(item)
            if payload.get("type") != "message":
                continue
            for content in payload.get("content", []):
                if content.get("type") == "output_text":
                    texts.append(content.get("text", ""))
        return [t for t in texts if t]

    def _run_shell_calls(self, calls: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
        inputs: List[Dict[str, Any]] = []
        for call in calls:
            action = call.get("action", {})
            commands = action.get("commands") or []
            timeout_ms = action.get("timeout_ms")
            max_len = action.get("max_output_length")
            outputs = []

            for command in commands:
                timeout = (timeout_ms / 1000.0) if timeout_ms else None
                result = self.shell.run(command, timeout=timeout)
                outcome: Dict[str, Any]
                if result.timed_out:
                    outcome = {"type": "timeout"}
                else:
                    outcome = {"type": "exit", "exit_code": result.exit_code}

                print(f"\n$ {command}")
                if result.stdout.strip():
                    print(result.stdout.rstrip())
                if result.stderr.strip():
                    print(result.stderr.rstrip(), file=sys.stderr)

                outputs.append(
                    {
                        "stdout": result.stdout,
                        "stderr": result.stderr,
                        "outcome": outcome,
                    }
                )

            payload: Dict[str, Any] = {
                "type": "shell_call_output",
                "call_id": call.get("call_id"),
                "output": outputs,
            }
            if max_len is not None:
                payload["max_output_length"] = max_len

            inputs.append({"role": "tool", "content": [payload]})
        return inputs

    @staticmethod
    def _to_dict(item: Any) -> Dict[str, Any]:
        if isinstance(item, dict):
            return item
        if hasattr(item, "model_dump"):
            try:
                return item.model_dump()
            except Exception:
                pass
        if hasattr(item, "to_dict_recursive"):
            try:
                return item.to_dict_recursive()  # type: ignore[attr-defined]
            except Exception:
                pass
        try:
            return json.loads(json.dumps(item))
        except Exception:
            return {}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="AI-powered shell assistant.")
    parser.add_argument(
        "prompt",
        help="Goal or instruction for the assistant (e.g. 'show disk usage for ./logs').",
    )
    parser.add_argument(
        "--model",
        default=os.environ.get("OSDASH_SHELL_MODEL", "gpt-5.1"),
        help="Responses API model to use (default: %(default)s).",
    )
    parser.add_argument(
        "--instructions",
        default=(
            "You can run shell commands on a macOS-like environment. "
            "Use non-interactive utilities and keep outputs concise."
        ),
        help="Custom system instructions passed to the model.",
    )
    parser.add_argument(
        "--cwd",
        type=Path,
        default=Path.cwd(),
        help="Working directory for shell commands.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=90.0,
        help="Default per-command timeout in seconds.",
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=6,
        help="Maximum plan/execute iterations before stopping.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    executor = ShellExecutor(cwd=args.cwd, default_timeout=args.timeout)
    bridge = AIShellBridge(
        model=args.model,
        instructions=args.instructions,
        shell=executor,
        max_steps=args.max_steps,
    )
    bridge.run(args.prompt)


if __name__ == "__main__":
    main()
