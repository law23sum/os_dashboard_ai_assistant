#!/usr/bin/env python3
"""Portfolio supervisor that applies the AI OS autotest loop to every git repo it can find."""

from __future__ import annotations

import argparse
import os
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Iterable, Iterator, List, Optional, Sequence, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MAX_DEPTH = 4


def _parse_roots(raw_roots: Optional[Sequence[str]]) -> List[Path]:
    if raw_roots:
        candidates = list(raw_roots)
    else:
        env_value = os.getenv("OSDASH_PORTFOLIO_ROOTS")
        candidates = env_value.split(os.pathsep) if env_value else [str(REPO_ROOT)]
    roots: List[Path] = []
    for entry in candidates:
        resolved = Path(entry).expanduser().resolve()
        if resolved.exists() and resolved.is_dir():
            roots.append(resolved)
    if not roots:
        roots.append(REPO_ROOT)
    return roots


def _iter_child_dirs(base: Path, max_depth: int) -> Iterator[Path]:
    queue: List[Tuple[Path, int]] = [(base, 0)]
    seen: set[Path] = set()
    while queue:
        current, depth = queue.pop(0)
        if current in seen:
            continue
        seen.add(current)
        if (current / ".git").is_dir():
            yield current
            # Do not traverse deeper inside git repos.
            continue
        if depth >= max_depth:
            continue
        try:
            entries = [child for child in current.iterdir() if child.is_dir()]
        except (OSError, PermissionError):
            continue
        for child in entries:
            if child.name in {".git", "__pycache__", ".venv", "node_modules", ".idea", ".vscode"}:
                continue
            queue.append((child, depth + 1))


def discover_git_projects(roots: Iterable[Path], max_depth: int) -> List[Path]:
    discovered: List[Path] = []
    seen: set[Path] = set()
    for root in roots:
        for repo in _iter_child_dirs(root, max_depth=max_depth):
            if repo in seen:
                continue
            seen.add(repo)
            discovered.append(repo)
    return discovered


def choose_command(repo: Path) -> Optional[List[str]]:
    tests_with_autofix = repo / "scripts" / "run_tests_with_autofix.py"
    ai_autofix = repo / "scripts" / "ai_auto_fix.py"
    pytest_file = repo / "pytest.ini"
    pyproject = repo / "pyproject.toml"
    package_json = repo / "package.json"

    if tests_with_autofix.exists():
        return [sys.executable, str(tests_with_autofix)]
    if pytest_file.exists() or (pyproject.exists() and (repo / "tests").is_dir()):
        return [sys.executable, "-m", "pytest"]
    if package_json.exists():
        return ["npm", "test"]
    if ai_autofix.exists():
        return [sys.executable, str(ai_autofix)]
    return None


def run_pipeline(repo: Path, cmd: List[str], dry_run: bool = False) -> Tuple[str, int]:
    display = shlex.join(cmd)
    print(f"\n🏗️  Supervising {repo} -> {display}")
    if dry_run:
        print("   (dry-run) Skipping execution.")
        return (display, 0)
    proc = subprocess.run(cmd, cwd=repo)
    return (display, proc.returncode)


def summarize(results: List[Tuple[Path, str, int]]) -> int:
    failures = [item for item in results if item[2] != 0]
    print("\n========== Portfolio Summary ==========")
    for repo, command, code in results:
        status = "✅ OK" if code == 0 else f"❌ FAILED ({code})"
        print(f"{status:<18} {repo} :: {command}")
    if failures:
        print("\n⚠️  Some projects need attention. Inspect the logs above or rerun the supervisor on the failing repos.")
        return 1
    print("\n🎉 All supervised repositories passed their pipelines.")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Traverse coding projects, detect git repos, and run the AI OS autotest pipeline for each.",
    )
    parser.add_argument(
        "--roots",
        nargs="+",
        help="Root directories to scan. Defaults to $OSDASH_PORTFOLIO_ROOTS or the current repo root.",
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=DEFAULT_MAX_DEPTH,
        help=f"Maximum directory depth to walk while searching (default: {DEFAULT_MAX_DEPTH}).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover projects and commands without executing them.",
    )
    args = parser.parse_args(argv)

    roots = _parse_roots(args.roots)
    repos = discover_git_projects(roots, max_depth=max(1, args.max_depth))
    if not repos:
        print("No git repositories detected.")
        return 0

    results: List[Tuple[Path, str, int]] = []
    for repo in repos:
        command = choose_command(repo)
        if not command:
            print(f"⚪ Skipping {repo} (no recognizable pipeline).")
            continue
        display, code = run_pipeline(repo, command, dry_run=args.dry_run)
        results.append((repo, display, code))

    if not results:
        print("Nothing to execute. Provide directories with recognizable pipelines.")
        return 0
    return summarize(results)


if __name__ == "__main__":
    raise SystemExit(main())
