#!/usr/bin/env python3
"""Watch backend/frontend logs and let the AI auto-patch regressions."""

from __future__ import annotations

import argparse
import queue
import re
import shlex
import subprocess
import sys
import threading
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Deque, Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from assistant_core.ai import generate_ai_reply, openai_available  # type: ignore
from assistant_core.db import ChatMessage  # type: ignore


@dataclass
class ProcessSpec:
    name: str
    command: List[str]


class LineBuffer:
    """Keep a rolling buffer of log lines per component."""

    def __init__(self, max_lines: int = 400) -> None:
        self.lines: Deque[str] = deque(maxlen=max_lines)
        self.lock = threading.Lock()

    def push(self, line: str) -> None:
        with self.lock:
            self.lines.append(line.rstrip("\n"))

    def snapshot(self, limit: Optional[int] = None) -> str:
        with self.lock:
            data = list(self.lines)
        if limit is not None:
            data = data[-limit:]
        return "\n".join(data)


class ProcessRunner:
    """Launch a long-running command and stream logs to the orchestrator."""

    def __init__(
        self,
        spec: ProcessSpec,
        line_callback,
        exit_callback,
    ) -> None:
        self.spec = spec
        self.line_callback = line_callback
        self.exit_callback = exit_callback
        self.process: Optional[subprocess.Popen] = None
        self.thread: Optional[threading.Thread] = None
        self.emit_exit_events = True

    def start(self) -> None:
        if self.process:
            raise RuntimeError(f"{self.spec.name} already running")
        self.process = subprocess.Popen(
            self.spec.command,
            cwd=REPO_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
        )
        self.emit_exit_events = True
        self.thread = threading.Thread(target=self._pump, daemon=True)
        self.thread.start()

    def _pump(self) -> None:
        assert self.process is not None
        assert self.process.stdout is not None
        for raw in self.process.stdout:
            if raw is None:
                break
            self.line_callback(self.spec.name, raw)
        self.process.wait()
        code = self.process.returncode
        if self.emit_exit_events and code not in (0, None):
            self.exit_callback(self.spec.name, code)

    def stop(self) -> None:
        if not self.process:
            return
        self.emit_exit_events = False
        if self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1)
        self.process = None
        self.thread = None


class AIFixer:
    """Use the repo's AI helper to propose + apply patches until logs are clean."""

    PATCH_RE = re.compile(r"```(?:patch|diff)\s+([\s\S]*?)```", re.MULTILINE)

    def __init__(
        self,
        *,
        persona: str = "AIC",
        diff_limit: int = 400,
        repo_root: Path = REPO_ROOT,
    ) -> None:
        self.persona = persona
        self.diff_limit = diff_limit
        self.repo_root = repo_root
        self.history: List[ChatMessage] = []

    def try_fix(self, component: str, log_excerpt: str, iteration: int) -> bool:
        if not openai_available():
            print("❌ OpenAI client is not configured. Set OPENAI_API_KEY before running this tool.")
            return False

        status = self._run_text(["git", "status", "-sb"])
        diffstat = self._run_text(["git", "diff", "--stat=120,80"])
        diff = self._trim_diff(self._run_text(["git", "diff"]))

        prompt = (
            "You are the autonomous maintainer for the OS Dashboard AI Assistant. "
            "Backend and frontend dev servers are running and the following component "
            f"reported an error.\n\n"
            f"Component: {component}\n"
            f"Iteration: {iteration}\n\n"
            "Recent logs:\n```\n"
            f"{log_excerpt.strip()}\n"
            "```\n\n"
            "Git status:\n```\n"
            f"{status.strip() or '(clean)'}\n"
            "```\n\n"
            "Diffstat:\n```\n"
            f"{diffstat.strip() or '(no staged changes)'}\n"
            "```\n\n"
            "Unified diff (trimmed):\n```\n"
            f"{diff.strip() or '(no local diff)'}\n"
            "```\n\n"
            "Goal: generate the smallest possible source change that eliminates the runtime error. "
            "Return a short reasoning paragraph followed by the full unified diff wrapped inside "
            "a single ```patch block. The diff must apply cleanly with `git apply --whitespace=fix`. "
            "Only touch files that are necessary for the fix."
        )

        user_msg = ChatMessage(
            id=len(self.history) + 1,
            persona=self.persona,
            role="user",
            kind="chat",
            content=prompt,
        )
        self.history.append(user_msg)
        reply, error, _ = generate_ai_reply(
            self.history,
            persona=self.persona,
            append_prompt=False,
            temperature=0.1,
            max_tokens=1800,
        )
        if error:
            print(f"❌ AI call failed: {error}")
            return False

        assistant_msg = ChatMessage(
            id=len(self.history) + 1,
            persona=self.persona,
            role="assistant",
            kind="chat",
            content=reply,
        )
        self.history.append(assistant_msg)

        patches = self._extract_patches(reply)
        if not patches:
            print("⚠️  AI response did not include a ```patch block. Full reply:\n")
            print(reply)
            return False

        try:
            for idx, patch in enumerate(patches, start=1):
                self._apply_patch(patch, idx)
        except RuntimeError as exc:
            print(f"❌ Failed to apply AI patch: {exc}")
            return False

        print("✅ Patch applied. Re-running monitored processes...")
        return True

    def _trim_diff(self, diff: str) -> str:
        if not diff or not self.diff_limit:
            return diff
        lines = diff.splitlines()
        if len(lines) <= self.diff_limit:
            return diff
        head = max(10, self.diff_limit // 4)
        tail = self.diff_limit - head
        trimmed = lines[:head] + ["... (diff truncated) ..."] + lines[-tail:]
        return "\n".join(trimmed)

    def _run_text(self, cmd: List[str]) -> str:
        proc = subprocess.run(
            cmd,
            cwd=self.repo_root,
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            raise RuntimeError(proc.stderr.strip() or proc.stdout.strip())
        return proc.stdout

    def _extract_patches(self, reply: str) -> List[str]:
        matches = self.PATCH_RE.findall(reply)
        return [block.strip() for block in matches if block.strip()]

    def _apply_patch(self, patch: str, idx: int) -> None:
        proc = subprocess.run(
            ["git", "apply", "--whitespace=fix"],
            input=patch,
            text=True,
            cwd=self.repo_root,
            capture_output=True,
        )
        if proc.returncode != 0:
            raise RuntimeError(proc.stderr.strip() or proc.stdout.strip() or f"patch #{idx} failed")


class AutoFixOrchestrator:
    """Coordinate process monitoring and recursive AI fixes."""

    ERROR_RE = re.compile(r"(error|traceback|exception|unhandled|fatal)", re.IGNORECASE)

    def __init__(
        self,
        specs: List[ProcessSpec],
        fixer: AIFixer,
        *,
        verify_seconds: int = 45,
        buffer_lines: int = 400,
        context_lines: int = 160,
    ) -> None:
        if not specs:
            raise ValueError("At least one process must be specified")
        self.specs = specs
        self.fixer = fixer
        self.verify_seconds = verify_seconds
        self.buffer_lines = buffer_lines
        self.context_lines = context_lines
        self.buffers: Dict[str, LineBuffer] = {}
        self.processes: Dict[str, ProcessRunner] = {}
        self.events: queue.Queue = queue.Queue()

    def run(self, max_attempts: int) -> int:
        for attempt in range(1, max_attempts + 1):
            print(f"\n=== Auto-fix attempt {attempt}/{max_attempts} ===")
            self._start_processes()
            try:
                event = self._wait_for_event()
            finally:
                self._stop_processes()

            if event is None:
                print(f"✅ No errors detected for {self.verify_seconds} seconds. Consider things stable.")
                return 0

            kind, component, payload = event
            print(f"⚠️  Detected {kind} event from {component}. Feeding logs to AI...")
            if not self.fixer.try_fix(component, payload, attempt):
                print("❌ Auto-fix attempt failed. See output above.")
                return 1

        print("❌ Reached maximum attempts without stabilizing.")
        return 2

    def _start_processes(self) -> None:
        self.events = queue.Queue()
        for spec in self.specs:
            self.buffers[spec.name] = LineBuffer(self.buffer_lines)
            runner = ProcessRunner(
                spec,
                line_callback=self._handle_line,
                exit_callback=self._handle_exit,
            )
            runner.start()
            self.processes[spec.name] = runner

    def _stop_processes(self) -> None:
        for runner in self.processes.values():
            runner.stop()
        self.processes.clear()
        # Drain leftover events triggered while shutting down
        while not self.events.empty():
            try:
                self.events.get_nowait()
            except queue.Empty:
                break

    def _wait_for_event(self) -> Optional[Tuple[str, str, str]]:
        try:
            return self.events.get(timeout=self.verify_seconds)
        except queue.Empty:
            return None

    def _handle_line(self, component: str, line: str) -> None:
        text = line.rstrip("\n")
        print(f"[{component}] {text}")
        self.buffers[component].push(text)
        if self.ERROR_RE.search(text):
            snapshot = self.buffers[component].snapshot(self.context_lines)
            self.events.put(("error", component, snapshot))

    def _handle_exit(self, component: str, code: int) -> None:
        snapshot = self.buffers[component].snapshot(self.context_lines)
        context = f"{component} exited with code {code}\n\n{snapshot}"
        self.events.put(("exit", component, context))


def _parse_specs(args: argparse.Namespace) -> List[ProcessSpec]:
    specs: List[ProcessSpec] = []
    if args.backend:
        specs.append(ProcessSpec("backend", shlex.split(args.backend)))
    if args.frontend:
        specs.append(ProcessSpec("frontend", shlex.split(args.frontend)))
    for entry in args.watch or []:
        if "=" not in entry:
            raise ValueError(f"--watch entries must look like label=command (got: {entry})")
        label, raw_cmd = entry.split("=", 1)
        specs.append(ProcessSpec(label.strip(), shlex.split(raw_cmd.strip())))

    if specs:
        return specs

    default_backend = [
        sys.executable,
        "-m",
        "uvicorn",
        "assistant_hub.api.server:create_app",
        "--factory",
        "--reload",
    ]
    default_frontend = ["npm", "run", "dev:web"]
    return [
        ProcessSpec("backend", default_backend),
        ProcessSpec("frontend", default_frontend),
    ]


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Continuously watch dev logs and auto-apply AI patches when errors appear.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python scripts/ai_auto_fix.py --backend \"python start_ui.py --mode web\" --frontend \"npm run dev:web\"\n"
            "  python scripts/ai_auto_fix.py --watch celery=\"celery -A tasks worker\" --verify-seconds 90\n"
        ),
    )
    parser.add_argument(
        "--backend",
        help="Command to run the backend (defaults to uvicorn).",
    )
    parser.add_argument(
        "--frontend",
        help="Command to run the frontend (defaults to `npm run dev:web`).",
    )
    parser.add_argument(
        "--watch",
        action="append",
        metavar="LABEL=CMD",
        help="Additional process to monitor, e.g. --watch worker=\"python worker.py\" (repeatable).",
    )
    parser.add_argument(
        "--verify-seconds",
        type=int,
        default=45,
        help="Consider the system stable when no errors are detected for this many seconds.",
    )
    parser.add_argument(
        "--max-attempts",
        type=int,
        default=5,
        help="Maximum recursive fix attempts before giving up.",
    )
    parser.add_argument(
        "--persona",
        default="AIC",
        help="Persona to use for the AI request (affects model + tone).",
    )
    parser.add_argument(
        "--diff-limit",
        type=int,
        default=400,
        help="Maximum number of diff lines to send to the AI context window.",
    )
    parser.add_argument(
        "--buffer-lines",
        type=int,
        default=400,
        help="How many log lines to retain per process for debugging context.",
    )
    parser.add_argument(
        "--context-lines",
        type=int,
        default=160,
        help="Maximum number of log lines to send to the AI when an error is detected.",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        specs = _parse_specs(args)
    except ValueError as exc:
        parser.error(str(exc))

    fixer = AIFixer(persona=args.persona, diff_limit=args.diff_limit)
    orchestrator = AutoFixOrchestrator(
        specs,
        fixer,
        verify_seconds=args.verify_seconds,
        buffer_lines=args.buffer_lines,
        context_lines=args.context_lines,
    )

    try:
        return orchestrator.run(args.max_attempts)
    except KeyboardInterrupt:
        print("\n⏹️  Interrupted by user, shutting down...")
        orchestrator._stop_processes()
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
