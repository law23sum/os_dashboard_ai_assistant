#!/usr/bin/env python3
"""Scan the workspace for Git projects and attach OS Dashboard auto-healing scripts.

The Technical Spec Sheet (v6) calls for every checked out project to inherit the
same resiliency guardrails that this repository uses.  This helper discovers all
directories containing a `.git` folder, determines which automation scripts are
available, and (optionally) executes the right self-healing routines.

Examples
--------
Plan-only report (default):
    python scripts/workspace_auto_guard.py --root ~/Projects

Execute the detected routines sequentially:
    python scripts/workspace_auto_guard.py --root ~/Projects --execute

Force-run the existing ai_auto_fix.py in the OS Dashboard repo for everything:
    python scripts/workspace_auto_guard.py --root ~/Projects \
        --fallback os_dashboard_ai_assistant/scripts/ai_auto_fix.py
"""

from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Sequence

REPO_ROOT = Path(__file__).resolve().parent.parent


@dataclass
class RepoCommand:
    """Executable command attached to a Git repository."""

    name: str
    cmd: Sequence[str]
    cwd: Path
    description: str


def discover_git_repos(root: Path, max_depth: int) -> List[Path]:
    """Return directories that directly contain a `.git` folder."""
    repos: List[Path] = []
    root = root.expanduser().resolve()
    queue: List[tuple[Path, int]] = [(root, 0)]
    seen: set[Path] = set()

    while queue:
        current, depth = queue.pop()
        if current in seen:
            continue
        seen.add(current)
        git_dir = current / ".git"
        if git_dir.is_dir():
            repos.append(current)
            continue
        if depth >= max_depth:
            continue
        for child in current.iterdir():
            if not child.is_dir():
                continue
            if child.name.startswith(".") or child.name in {"node_modules", "__pycache__"}:
                continue
            queue.append((child, depth + 1))
    return sorted(repos)


def _repo_has_python_tests(repo: Path) -> bool:
    return (repo / "pytest.ini").exists() or (repo / "tests").is_dir()


def _repo_has_node_tests(repo: Path) -> bool:
    return (repo / "package.json").exists()


def detect_commands(repo: Path, fallback: Path | None) -> List[RepoCommand]:
    """Build a prioritized list of automation commands for `repo`."""
    commands: List[RepoCommand] = []
    python = os.environ.get("PYTHON", sys.executable)

    ai_auto_fix = repo / "scripts" / "ai_auto_fix.py"
    if ai_auto_fix.is_file():
        commands.append(
            RepoCommand(
                name="ai-auto-fix",
                cmd=[python, str(ai_auto_fix), "--logs-only"],
                cwd=repo,
                description="Tail logs and auto-patch regressions",
            )
        )

    run_tests_with_autofix = repo / "scripts" / "run_tests_with_autofix.py"
    if run_tests_with_autofix.is_file():
        commands.append(
            RepoCommand(
                name="regression-suite",
                cmd=[python, str(run_tests_with_autofix)],
                cwd=repo,
                description="Run curated regression tests with AI auto-fix fallback",
            )
        )

    if _repo_has_python_tests(repo):
        commands.append(
            RepoCommand(
                name="pytest",
                cmd=[python, "-m", "pytest", "-q"],
                cwd=repo,
                description="Generic Python test sweep (auto-detected)",
            )
        )

    if _repo_has_node_tests(repo):
        commands.append(
            RepoCommand(
                name="npm-test",
                cmd=["npm", "test", "--", "--runInBand"],
                cwd=repo,
                description="Node/TypeScript tests (auto-detected)",
            )
        )

    if not commands and fallback:
        commands.append(
            RepoCommand(
                name="workspace-fallback",
                cmd=[sys.executable, str(fallback)],
                cwd=repo,
                description="Fallback auto-fix inherited from OS Dashboard AI Assistant",
            )
        )
    return commands


def run_command(command: RepoCommand) -> Dict[str, object]:
    """Execute the provided command, capturing stdout/stderr."""
    print(f"▶️  [{command.cwd}] {command.name}: {shlex.join(command.cmd)}")
    proc = subprocess.run(
        command.cmd,
        cwd=command.cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    status = "passed" if proc.returncode == 0 else "failed"
    print(f"    ↳ status: {status}")
    return {
        "name": command.name,
        "status": status,
        "returncode": proc.returncode,
        "output": proc.stdout,
    }


def orchestrate(root: Path, max_depth: int, execute: bool, fallback: Path | None) -> Dict[str, object]:
    """Discover repos and optionally execute automation commands."""
    repos = discover_git_repos(root, max_depth=max_depth)
    report: Dict[str, object] = {"root": str(root), "projects": []}

    for repo in repos:
        commands = detect_commands(repo, fallback)
        project_entry: Dict[str, object] = {
            "path": str(repo),
            "commands": [c.name for c in commands],
            "results": [],
        }
        if execute:
            for command in commands:
                project_entry["results"].append(run_command(command))
        report["projects"].append(project_entry)

    return report


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Attach OS Dashboard auto-healing scripts to every Git project in a workspace.")
    parser.add_argument(
        "--root",
        type=Path,
        default=REPO_ROOT,
        help="Workspace root to scan. Defaults to the OS Dashboard repo.",
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=3,
        help="Maximum directory depth to traverse when discovering Git repos.",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Execute the detected automation commands. Otherwise, only print the plan.",
    )
    parser.add_argument(
        "--fallback",
        type=Path,
        default=None,
        help="Optional fallback script to run when a repo lacks native automation hooks.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional path to dump the discovery JSON report.",
    )
    args = parser.parse_args(argv)
    fallback = args.fallback
    if fallback is not None:
        fallback = fallback.expanduser().resolve()
        if not fallback.exists():
            parser.error(f"Fallback script not found: {fallback}")

    report = orchestrate(
        root=args.root.expanduser().resolve(),
        max_depth=max(0, args.max_depth),
        execute=args.execute,
        fallback=fallback,
    )
    print(json.dumps(report, indent=2))
    if args.output:
        args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
