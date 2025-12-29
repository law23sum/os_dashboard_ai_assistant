#!/usr/bin/env python3
"""Launch ai_auto_fix.py for every discovered project workspace.

This manager scans one or more root folders, looks for git repositories that
also ship a ``scripts/ai_auto_fix.py`` entry point, and then spawns the auto-fix
runner for each project.  The manager keeps the child processes alive until it
receives Ctrl+C, ensuring that every project has an AI watchdog ready as soon
as developers start hacking.

Example:
    python scripts/project_auto_fix_manager.py --root ~/Projects --max-depth 2

By default the script assumes each project wants the lightweight ``--backend
none``/``--frontend none`` daemon configuration.  Pass ``--`` followed by any
arguments to override the defaults (they are appended to every invocation).
"""
from __future__ import annotations

import argparse
import os
import signal
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCRIPT = REPO_ROOT / "scripts" / "ai_auto_fix.py"
DEFAULT_AUTOFIX_ARGS = [
    "--backend",
    "none",
    "--frontend",
    "none",
    "--logs-only",
    "--daemon",
]
DEFAULT_IGNORES = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "node_modules",
    "dist",
    "build",
    "__pycache__",
    "logs",
    ".mypy_cache",
}


@dataclass
class ManagedProcess:
    """Metadata for a launched auto-fix worker."""

    name: str
    root: Path
    process: subprocess.Popen[str]


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Start ai_auto_fix.py against every git repo under the supplied roots.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--root",
        action="append",
        dest="roots",
        metavar="PATH",
        help="Root directory to scan (can be repeated). Defaults to this repo's parent folder.",
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=2,
        help="How deep to traverse when scanning for projects.",
    )
    parser.add_argument(
        "--ignore",
        action="append",
        dest="ignores",
        metavar="NAME",
        help="Directory names to skip while crawling.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List the discovered projects without launching ai_auto_fix.py.",
    )
    parser.add_argument(
        "--script-name",
        default="scripts/ai_auto_fix.py",
        help="Path (relative to each project) to the auto-fix entry point.",
    )
    parser.add_argument(
        "autofix_args",
        nargs=argparse.REMAINDER,
        help="Additional arguments appended to every ai_auto_fix.py invocation. "
        "Start the list with '--' to separate them from manager flags.",
    )
    return parser.parse_args(argv)


def normalize_roots(raw_roots: Optional[Iterable[str]]) -> List[Path]:
    if not raw_roots:
        parent = REPO_ROOT.parent
        return [parent]
    roots: List[Path] = []
    for entry in raw_roots:
        path = Path(entry).expanduser().resolve()
        if path.exists():
            roots.append(path)
        else:
            print(f"[manager] ⚠️  Skipping missing root: {path}")
    return roots


def discover_projects(
    roots: Iterable[Path],
    max_depth: int,
    ignores: Set[str],
) -> List[Path]:
    """Breadth-first search for directories that look like repositories."""

    def iter_children(base: Path) -> Iterable[Path]:
        try:
            for child in base.iterdir():
                if child.is_dir() and child.name not in ignores:
                    yield child
        except PermissionError:
            return

    projects: List[Path] = []
    seen: Set[Path] = set()
    for root in roots:
        queue: List[Tuple[Path, int]] = [(root, 0)]
        while queue:
            current, depth = queue.pop(0)
            current = current.resolve()
            if current in seen:
                continue
            seen.add(current)
            if (current / ".git").exists():
                projects.append(current)
                continue
            if depth >= max_depth:
                continue
            for child in iter_children(current):
                queue.append((child, depth + 1))
    return projects


def build_command(
    project_root: Path,
    script_relative: str,
    extra_args: Sequence[str],
) -> Optional[List[str]]:
    script_path = (project_root / script_relative).resolve()
    if not script_path.exists():
        return None
    if not extra_args:
        cmd = [sys.executable, str(script_path), *DEFAULT_AUTOFIX_ARGS]
    else:
        extra = list(extra_args)
        if extra and extra[0] == "--":
            extra = extra[1:]
        cmd = [sys.executable, str(script_path), *extra]
    return cmd


def launch_process(project_root: Path, command: List[str]) -> subprocess.Popen[str]:
    env = os.environ.copy()
    env.setdefault("PYTHONUNBUFFERED", "1")
    return subprocess.Popen(
        command,
        cwd=project_root,
        env=env,
        text=True,
    )


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    ignores = DEFAULT_IGNORES.copy()
    if args.ignores:
        ignores.update(args.ignores)

    roots = normalize_roots(args.roots)
    if not roots:
        print("[manager] ❌ No valid roots to scan.")
        return 1

    projects = discover_projects(roots, max_depth=args.max_depth, ignores=ignores)
    if not projects:
        print("[manager] ⚠️  Did not find any git repositories under the provided roots.")
        return 0

    print("[manager] 📁 Discovered the following projects:")
    for proj in projects:
        print(f"  • {proj}")

    if args.dry_run:
        return 0

    managed: List[ManagedProcess] = []
    for project in projects:
        command = build_command(project, args.script_name, args.autofix_args)
        if not command:
            print(f"[manager] ℹ️  {project} does not contain {args.script_name}. Skipping.")
            continue
        try:
            proc = launch_process(project, command)
            managed.append(ManagedProcess(name=project.name, root=project, process=proc))
            print(f"[manager] 🚀 Started auto-fix for {project} (pid={proc.pid}).")
        except OSError as exc:
            print(f"[manager] ❌ Failed to launch auto-fix for {project}: {exc}")

    if not managed:
        print("[manager] ⚠️  No auto-fix processes were launched.")
        return 1

    def _handle_signal(signum: int, frame) -> None:  # type: ignore[override]
        print(f"\n[manager] ⏹️  Caught signal {signum}. Shutting down...")
        raise KeyboardInterrupt

    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    try:
        while True:
            for entry in managed:
                if entry.process.poll() is not None:
                    print(
                        f"[manager] ⚠️  Auto-fix for {entry.root} exited with code {entry.process.returncode}."
                    )
                    managed.remove(entry)
            if not managed:
                print("[manager] ℹ️  All auto-fix workers have exited.")
                return 0
            time.sleep(1.0)
    except KeyboardInterrupt:
        pass
    finally:
        for entry in managed:
            if entry.process.poll() is None:
                entry.process.terminate()
                try:
                    entry.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    entry.process.kill()
        print("[manager] ✅ Auto-fix manager stopped cleanly.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
