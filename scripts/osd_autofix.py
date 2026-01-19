#!/usr/bin/env python3
"""
Universal project runner: detect repo type, run checks, and trigger ai_auto_fix.

Goals
-----
- Work across *any* git repo (Python/Node/mixed).
- Be safe by default: no package installs, no long-lived processes.
- When checks fail: write a log snapshot, invoke `scripts/ai_auto_fix.py` against
  that repo (`--project-root`) and re-run the failing command via `--test`.
- Emit a ready-to-paste "Codex prompt" including failures + global TODO backlogs.
"""

from __future__ import annotations

import argparse
import os
import shlex
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Tuple

OSDASH_ROOT = Path(__file__).resolve().parent.parent
GLOBAL_TODO_FILES = [
    OSDASH_ROOT / "REMAINING_TODOS.md",
    OSDASH_ROOT / "FUTURE_TODOS.md",
]


@dataclass(frozen=True)
class Cmd:
    category: str
    label: str
    argv: List[str]
    cwd: Path


def _shlex_join(parts: Sequence[str]) -> str:
    try:
        return shlex.join(list(parts))  # type: ignore[attr-defined]
    except AttributeError:
        return " ".join(shlex.quote(p) for p in parts)


def _git_root(start: Path) -> Optional[Path]:
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=start,
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            return None
        return Path(proc.stdout.strip()).expanduser().resolve()
    except Exception:
        return None


def _repo_has(path: Path, rel: str) -> bool:
    return (path / rel).exists()


def _detect_commands(repo: Path) -> List[Cmd]:
    cmds: List[Cmd] = []
    # Python
    if _repo_has(repo, "pyproject.toml") or _repo_has(repo, "requirements.txt") or _repo_has(repo, "setup.py"):
        if _repo_has(repo, "tests") or _repo_has(repo, "pytest.ini"):
            cmds.append(Cmd("test", "pytest", [sys.executable, "-m", "pytest", "-q"], repo))
        # Best-effort lint if flake8 is available in env.
        lint_targets: List[str] = []
        for candidate in ("assistant_core", "backend_api", "tests", "src", "app"):
            if (repo / candidate).exists():
                lint_targets.append(candidate)
        if not lint_targets:
            lint_targets = ["."]
        cmds.append(Cmd("lint", "flake8", [sys.executable, "-m", "flake8", *lint_targets], repo))
        cmds.append(Cmd("security", "pip-check", [sys.executable, "-m", "pip", "check"], repo))

    # Node
    if _repo_has(repo, "package.json"):
        # Only run node checks when deps are present; otherwise report via Codex prompt when relevant.
        if (repo / "node_modules").exists():
            cmds.append(Cmd("test", "npm-test", ["npm", "test"], repo))

    # Frontend-in-subdir convention
    if _repo_has(repo, "frontend/package.json"):
        if (repo / "frontend" / "node_modules").exists():
            cmds.append(Cmd("lint", "frontend-lint", ["npm", "run", "lint", "--prefix", "frontend"], repo))
            cmds.append(
                Cmd(
                    "test",
                    "frontend-test",
                    ["npm", "run", "test", "--prefix", "frontend", "--", "--runInBand"],
                    repo,
                )
            )
            cmds.append(Cmd("build", "frontend-build", ["npm", "run", "build", "--prefix", "frontend"], repo))

    # De-dupe while preserving order
    seen: set[Tuple[str, str]] = set()
    deduped: List[Cmd] = []
    for cmd in cmds:
        key = (cmd.category, _shlex_join(cmd.argv))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(cmd)
    return deduped


def _log_dir(repo: Path) -> Path:
    path = repo / "logs" / "osdash_autofix"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _run_cmd(cmd: Cmd, *, timeout_seconds: int) -> Tuple[int, str]:
    display = _shlex_join(cmd.argv)
    start = time.time()
    try:
        proc = subprocess.run(
            cmd.argv,
            cwd=cmd.cwd,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
        out = (proc.stdout or "") + (("\n" + proc.stderr) if proc.stderr else "")
        duration = time.time() - start
        out = f"$ {display}\n(cwd={cmd.cwd})\n(duration={duration:.1f}s)\n\n{out}".strip() + "\n"
        return proc.returncode, out
    except subprocess.TimeoutExpired as exc:
        duration = time.time() - start
        out = (exc.stdout or "") + (("\n" + exc.stderr) if exc.stderr else "")
        return 124, f"$ {display}\n(cwd={cmd.cwd})\n(timeout={timeout_seconds}s, duration={duration:.1f}s)\n\n{out}\n"
    except FileNotFoundError as exc:
        return 127, f"$ {display}\n(cwd={cmd.cwd})\n\ncommand not found: {exc.filename}\n"


def _write_failure_log(repo: Path, label: str, output: str) -> Path:
    stamp = time.strftime("%Y%m%d-%H%M%S")
    path = _log_dir(repo) / f"{label}-{stamp}.log"
    path.write_text(output, encoding="utf-8")
    return path


def _invoke_ai_autofix(
    *,
    repo: Path,
    failing_cmd: Cmd,
    log_dir: Path,
    attempts: int,
    verify_seconds: int,
    extra_args: Sequence[str],
) -> int:
    ai = OSDASH_ROOT / "scripts" / "ai_auto_fix.py"
    if not ai.exists():
        return 127
    # Re-run failing command as a "test" so ai_auto_fix can iterate.
    test_arg = f"{failing_cmd.label}={_shlex_join(failing_cmd.argv)}"
    cmd = [
        sys.executable,
        str(ai),
        "--project-root",
        str(repo),
        "--logs-only",
        "--log-dir",
        str(log_dir),
        "--disable-binary-monitor",
        "--no-daemon",
        "--verify-seconds",
        str(verify_seconds),
        "--max-attempts",
        str(attempts),
        "--test",
        test_arg,
    ]
    cmd.extend(extra_args)
    proc = subprocess.run(cmd, cwd=repo)
    return proc.returncode


def _read_text(path: Path, limit_chars: int = 200_000) -> str:
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8", errors="replace")
    if len(text) <= limit_chars:
        return text
    return text[:limit_chars] + "\n\n... (truncated) ...\n"


def _build_codex_prompt(
    *,
    repo: Path,
    failures: List[Tuple[Cmd, Path]],
    extra_todo_files: Sequence[Path],
) -> str:
    todo_sections: List[str] = []
    for todo_path in list(GLOBAL_TODO_FILES) + list(extra_todo_files):
        content = _read_text(todo_path)
        if not content.strip():
            continue
        todo_sections.append(f"### TODO file: {todo_path}\n\n{content}\n")

    failure_sections: List[str] = []
    for cmd, log_path in failures:
        failure_sections.append(
            "### Failure\n"
            f"- repo: {repo}\n"
            f"- command: {_shlex_join(cmd.argv)}\n"
            f"- log: {log_path}\n\n"
            f"{_read_text(log_path, limit_chars=120_000)}\n"
        )

    return (
        "You are an autonomous coding agent.\n"
        "Fix the failing checks for the target repo. Apply minimal, correct changes.\n"
        "After fixes, re-run the failing commands and ensure they pass.\n\n"
        f"Target repo: {repo}\n\n"
        + ("\n\n".join(failure_sections) if failure_sections else "No failures were captured.\n")
        + "\n\n"
        + ("\n\n".join(todo_sections) if todo_sections else "No TODO files found.\n")
    )


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run checks and trigger AI OS auto-fix across any repo.")
    parser.add_argument("--repo", type=Path, default=Path.cwd(), help="Repo path (defaults to CWD).")
    parser.add_argument("--categories", default="lint,test", help="Comma-separated categories to run.")
    parser.add_argument("--timeout", type=int, default=300, help="Per-command timeout seconds.")
    parser.add_argument("--autofix", action="store_true", help="Invoke ai_auto_fix when a command fails.")
    parser.add_argument("--autofix-attempts", type=int, default=2, help="Max ai_auto_fix attempts for a failure.")
    parser.add_argument("--autofix-verify-seconds", type=int, default=20, help="ai_auto_fix stability window.")
    parser.add_argument("--autofix-arg", action="append", default=[], help="Extra args forwarded to ai_auto_fix.")
    parser.add_argument("--todo", action="append", default=[], type=Path, help="Additional TODO file(s) to include in Codex prompt.")
    parser.add_argument(
        "--write-codex-prompt",
        type=Path,
        default=None,
        help="Write a Codex-ready prompt file when failures occur.",
    )
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    repo_in = args.repo.expanduser().resolve()
    repo = _git_root(repo_in) or repo_in
    categories = [c.strip() for c in str(args.categories).split(",") if c.strip()]

    cmds = [c for c in _detect_commands(repo) if c.category in categories]
    if not cmds:
        print(f"[osd] No commands detected for categories={categories} in {repo}")
        return 0

    failures: List[Tuple[Cmd, Path]] = []
    for cmd in cmds:
        code, output = _run_cmd(cmd, timeout_seconds=max(5, int(args.timeout)))
        if code == 0:
            print(f"[osd] ✅ {cmd.category}/{cmd.label}: ok")
            continue

        print(f"[osd] ❌ {cmd.category}/{cmd.label}: exit={code}")
        log_path = _write_failure_log(repo, cmd.label, output)
        failures.append((cmd, log_path))

        if args.autofix:
            print(f"[osd] 🤖 attempting auto-fix for {cmd.label} ...")
            _invoke_ai_autofix(
                repo=repo,
                failing_cmd=cmd,
                log_dir=_log_dir(repo),
                attempts=max(1, int(args.autofix_attempts)),
                verify_seconds=max(5, int(args.autofix_verify_seconds)),
                extra_args=list(args.autofix_arg),
            )

            # Re-run once after auto-fix
            rerun_code, _ = _run_cmd(cmd, timeout_seconds=max(5, int(args.timeout)))
            if rerun_code == 0:
                print(f"[osd] ✅ {cmd.category}/{cmd.label}: fixed")
            else:
                print(f"[osd] ⚠️  {cmd.category}/{cmd.label}: still failing after auto-fix")

    if failures and args.write_codex_prompt:
        prompt = _build_codex_prompt(
            repo=repo,
            failures=failures,
            extra_todo_files=[p.expanduser().resolve() for p in args.todo],
        )
        args.write_codex_prompt.parent.mkdir(parents=True, exist_ok=True)
        args.write_codex_prompt.write_text(prompt, encoding="utf-8")
        print(f"[osd] 🧾 wrote Codex prompt: {args.write_codex_prompt}")

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
