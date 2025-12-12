#!/usr/bin/env python3
"""Fan out ai_auto_fix monitors to every git repo in the workspace.

The orchestrator searches for directories that contain a `.git` folder (or file)
and tries to launch `scripts/ai_auto_fix.py` inside each repo. This lets a single
terminal session act as a mission control for every project, ensuring self-healing
automations stay online even when new repos appear in the workspace.

Example:
    # Scan the ~/Projects workspace and auto-launch all monitors in parallel
    python scripts/project_autofix_orchestrator.py --root ~/Projects

    # Sequentially start monitors, pass additional ai_auto_fix arguments
    python scripts/project_autofix_orchestrator.py \\
        --mode sequential \\
        --root ./ \\
        --ai-args "--logs-only --performance-threshold-ms 750"

The script is intentionally conservative: if a repo does not ship its own
`scripts/ai_auto_fix.py`, the orchestrator documents the gap instead of failing.
This matches the blueprint mandate for graceful degradation when optional
capabilities are missing.
"""

from __future__ import annotations

import argparse
import os
import shlex
import signal
import subprocess
import sys
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", ".mypy_cache"}


def parse_env_pairs(items: Sequence[str]) -> Dict[str, str]:
    env: Dict[str, str] = {}
    for raw in items:
        if "=" not in raw:
            raise argparse.ArgumentTypeError(f"Invalid --env value '{raw}', expected KEY=VALUE.")
        key, value = raw.split("=", 1)
        env[key.strip()] = value
    return env


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Detect git repos and fan out ai_auto_fix monitors across them.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=REPO_ROOT,
        help="Workspace root to scan for git repositories.",
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=4,
        help="Maximum directory depth (relative to --root) to search for .git markers.",
    )
    parser.add_argument(
        "--include",
        action="append",
        default=[],
        metavar="SUBSTRING",
        help="Only run monitors where the repo path contains this substring (repeatable).",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        metavar="SUBSTRING",
        help="Skip repos whose path contains this substring (repeatable).",
    )
    parser.add_argument(
        "--mode",
        choices=("parallel", "sequential"),
        default="parallel",
        help="Choose how monitors are launched.",
    )
    parser.add_argument(
        "--scan-only",
        action="store_true",
        help="List detected repos and exit without launching monitors.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned monitor commands without launching them.",
    )
    parser.add_argument(
        "--ai-args",
        default="",
        help="Extra arguments passed to each ai_auto_fix invocation.",
    )
    parser.add_argument(
        "--env",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="Environment variables injected into child monitor processes.",
    )
    parser.add_argument(
        "--health-log",
        type=Path,
        default=REPO_ROOT / "logs" / "autofix_orchestrator.log",
        help="Path to append health + status events.",
    )
    parser.add_argument(
        "--skip-dir",
        action="append",
        default=[],
        help="Additional directory names to skip while scanning.",
    )
    parser.add_argument(
        "--max-repos",
        type=int,
        default=0,
        help="Ceiling for number of repos to launch (0 = no limit).",
    )
    return parser.parse_args()


@dataclass
class RepoTarget:
    path: Path
    autofix_script: Optional[Path]

    @property
    def name(self) -> str:
        return self.path.name

    def command(self, extra_args: Sequence[str]) -> List[str]:
        if not self.autofix_script:
            raise RuntimeError(f"{self.path} does not have scripts/ai_auto_fix.py")
        return [sys.executable, str(self.autofix_script), *extra_args]


def discover_git_repos(root: Path, max_depth: int, skip_dirs: Iterable[str]) -> List[Path]:
    root = root.expanduser().resolve()
    results: List[Path] = []
    skip = set(skip_dirs)
    queue: List[tuple[Path, int]] = [(root, 0)]

    while queue:
        current, depth = queue.pop()
        git_marker = current / ".git"
        if git_marker.exists():
            results.append(current)
            continue
        if max_depth and depth >= max_depth:
            continue
        try:
            for child in current.iterdir():
                if not child.is_dir():
                    continue
                if child.name in skip:
                    continue
                queue.append((child, depth + 1))
        except PermissionError:
            continue
    return sorted(set(results))


def resolve_targets(paths: Iterable[Path]) -> List[RepoTarget]:
    targets: List[RepoTarget] = []
    for repo_path in paths:
        script_path = repo_path / "scripts" / "ai_auto_fix.py"
        targets.append(RepoTarget(path=repo_path, autofix_script=script_path if script_path.exists() else None))
    return targets


def format_repo(repo: RepoTarget) -> str:
    status = "READY" if repo.autofix_script else "MISSING ai_auto_fix.py"
    return f"{repo.path} — {status}"


class Monitor:
    """Wrap subprocess and stream forwarding so we can stop them cleanly."""

    def __init__(self, repo: RepoTarget, command: Sequence[str], env: Dict[str, str], logger):
        self.repo = repo
        self.command = list(command)
        self.env = env
        self.logger = logger
        self.process: Optional[subprocess.Popen[str]] = None
        self._pump_thread: Optional[threading.Thread] = None

    def start(self) -> None:
        self.logger(f"{self.repo.path}: launching {' '.join(self.command)}")
        self.process = subprocess.Popen(
            self.command,
            cwd=self.repo.path,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            env=self.env,
        )
        assert self.process.stdout is not None
        self._pump_thread = threading.Thread(
            target=self._pump,
            args=(self.process.stdout,),
            name=f"{self.repo.name}-pump",
            daemon=True,
        )
        self._pump_thread.start()

    def _pump(self, stream) -> None:
        for line in stream:
            text = line.rstrip()
            if text:
                self.logger(f"{self.repo.name}: {text}")
        code = self.process.returncode if self.process else None
        self.logger(f"{self.repo.path}: process ended with code {code}")

    def stop(self, timeout: float = 5.0) -> None:
        if not self.process:
            return
        if self.process.poll() is None:
            self.logger(f"{self.repo.path}: stopping monitor")
            try:
                self.process.terminate()
                self.process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                self.logger(f"{self.repo.path}: force killing unresponsive monitor")
                self.process.kill()
        self.process = None


def should_include(repo: RepoTarget, includes: Sequence[str], excludes: Sequence[str]) -> bool:
    text = str(repo.path)
    if includes and not any(marker in text for marker in includes):
        return False
    if excludes and any(marker in text for marker in excludes):
        return False
    return True


def ensure_log_directory(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def make_logger(log_path: Path):
    ensure_log_directory(log_path)

    def _log(message: str) -> None:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{timestamp}] {message}"
        print(line)
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")

    return _log


def main() -> None:
    args = parse_args()
    extra_args = shlex.split(args.ai_args)
    env = os.environ.copy()
    env.update(parse_env_pairs(args.env))

    skip_dirs = DEFAULT_SKIP_DIRS | set(args.skip_dir)
    repos = discover_git_repos(args.root, args.max_depth, skip_dirs)
    targets = [target for target in resolve_targets(repos) if should_include(target, args.include, args.exclude)]

    if args.max_repos and len(targets) > args.max_repos:
        targets = targets[: args.max_repos]

    logger = make_logger(args.health_log)
    logger(f"Discovered {len(targets)} repositories under {args.root}")
    for repo in targets:
        logger(format_repo(repo))

    if args.scan_only:
        return

    ready = [repo for repo in targets if repo.autofix_script]
    if not ready:
        logger("No repositories with scripts/ai_auto_fix.py were found. Exiting.")
        return

    if args.dry_run:
        for repo in ready:
            logger(f"[dry-run] {' '.join(repo.command(extra_args))} @ {repo.path}")
        return

    monitors = [Monitor(repo, repo.command(extra_args), env, logger) for repo in ready]

    try:
        if args.mode == "sequential":
            for monitor in monitors:
                monitor.start()
                if monitor.process:
                    monitor.process.wait()
        else:
            for monitor in monitors:
                monitor.start()
            wait_for_interrupt(logger)
    except KeyboardInterrupt:
        logger("Received interrupt, stopping monitors...")
    finally:
        for monitor in monitors:
            monitor.stop()


def wait_for_interrupt(logger) -> None:
    stop_event = threading.Event()

    def _signal_handler(signum, frame):
        logger(f"Signal {signum} received — shutting down orchestrator.")
        stop_event.set()

    previous_sigint = signal.signal(signal.SIGINT, _signal_handler)
    previous_sigterm = signal.signal(signal.SIGTERM, _signal_handler)
    try:
        while not stop_event.is_set():
            time.sleep(0.5)
    finally:
        signal.signal(signal.SIGINT, previous_sigint)
        signal.signal(signal.SIGTERM, previous_sigterm)


if __name__ == "__main__":
    main()
