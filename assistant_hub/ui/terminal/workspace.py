"""Workspace orchestration helpers for the `osdash` CLI.

These utilities discover git repositories, infer common run/test commands,
and execute standardized workflows (scan/test/run/doctor) across a workspace.
They are intentionally light-weight and avoid external dependencies so they
can run inside CI or constrained dev shells.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Tuple, Dict

REPO_ROOT = Path(__file__).resolve().parents[3]
LOG_PATH = REPO_ROOT / "logs" / "osdash_cli.log"


@dataclass
class RepoProfile:
    """Detected capabilities for a git repository."""

    path: Path
    name: str
    test_commands: List[str] = field(default_factory=list)
    run_commands: List[str] = field(default_factory=list)
    build_commands: List[str] = field(default_factory=list)
    lint_commands: List[str] = field(default_factory=list)
    security_commands: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "path": str(self.path),
            "name": self.name,
            "test_commands": self.test_commands,
            "run_commands": self.run_commands,
            "build_commands": self.build_commands,
            "lint_commands": self.lint_commands,
            "security_commands": self.security_commands,
            "notes": self.notes,
        }


@dataclass
class CommandResult:
    """Result of executing a command in a repo."""

    category: str
    command: str
    returncode: int
    stdout: str
    stderr: str
    duration_seconds: float

    @property
    def ok(self) -> bool:
        return self.returncode == 0


def discover_git_repos(root: Path, max_depth: int = 3, excludes: Optional[Sequence[str]] = None) -> List[Path]:
    """Return all directories under `root` that contain a `.git` folder."""

    excludes = tuple(excludes or [])
    repos: List[Path] = []
    for dirpath, dirnames, _ in os.walk(root):
        rel_parts = Path(dirpath).relative_to(root).parts
        if len(rel_parts) > max_depth:
            dirnames[:] = []
            continue

        # Respect exclude prefixes
        if any(Path(dirpath).as_posix().startswith(Path(root, ex).as_posix()) for ex in excludes):
            dirnames[:] = []
            continue

        if ".git" in dirnames:
            repos.append(Path(dirpath))
            dirnames.remove(".git")
    return repos


def _log_line(message: str) -> None:
    """Append a log entry for workspace orchestration."""

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOG_PATH.touch(exist_ok=True)
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%S")
    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(f"[{timestamp}] {message}\n")


def _append_if_unique(target: List[str], candidate: str) -> None:
    if candidate not in target:
        target.append(candidate)


def _load_package_scripts(package_json: Path) -> Dict[str, str]:
    try:
        payload = json.loads(package_json.read_text(encoding="utf-8"))
        scripts = payload.get("scripts", {})
        return scripts if isinstance(scripts, dict) else {}
    except Exception:
        return {}


def infer_repo_profile(repo_path: Path) -> RepoProfile:
    """Infer likely run/test/build commands for a repository."""

    name = repo_path.name or repo_path.resolve().name
    profile = RepoProfile(path=repo_path, name=name)

    has_pyproject = (repo_path / "pyproject.toml").exists()
    has_requirements = (repo_path / "requirements.txt").exists()
    has_package_json = (repo_path / "package.json").exists()
    has_frontend = (repo_path / "frontend").exists()
    has_start_ui = (repo_path / "start_ui.py").exists()
    has_setup = (repo_path / "setup.py").exists()

    if (repo_path / "scripts" / "run_tests_with_autofix.py").exists():
        _append_if_unique(profile.test_commands, "python scripts/run_tests_with_autofix.py --once")
    if has_pyproject or has_requirements:
        _append_if_unique(profile.test_commands, "pytest -q")
    if has_package_json:
        scripts = _load_package_scripts(repo_path / "package.json")
        if "test" in scripts:
            _append_if_unique(profile.test_commands, "npm test -- --runInBand")
        elif has_package_json:
            _append_if_unique(profile.test_commands, "npm test -- --runInBand")
        if "lint" in scripts:
            _append_if_unique(profile.lint_commands, "npm run lint")
        if "build" in scripts:
            _append_if_unique(profile.build_commands, "npm run build")
    if has_frontend and (repo_path / "frontend" / "package.json").exists():
        frontend_scripts = _load_package_scripts(repo_path / "frontend" / "package.json")
        if "test" in frontend_scripts:
            _append_if_unique(profile.test_commands, "npm test -- --runInBand")
        elif frontend_scripts is not None:
            _append_if_unique(profile.test_commands, "npm test -- --runInBand")
        if "lint" in frontend_scripts:
            _append_if_unique(profile.lint_commands, "npm run lint")
        if "typecheck" in frontend_scripts:
            _append_if_unique(profile.lint_commands, "npm run typecheck")
        if "build" in frontend_scripts:
            _append_if_unique(profile.build_commands, "npm run build")

    if has_start_ui:
        _append_if_unique(profile.run_commands, "python start_ui.py --mode web")
    if has_frontend:
        _append_if_unique(profile.run_commands, "npm run --prefix frontend dev:web")
        _append_if_unique(profile.build_commands, "npm run --prefix frontend build")
    if has_pyproject or has_setup:
        _append_if_unique(profile.build_commands, "python -m build")
    if (repo_path / ".ruff.toml").exists() or (repo_path / "ruff.toml").exists():
        _append_if_unique(profile.lint_commands, "ruff check .")
    if (repo_path / "pyproject.toml").exists() and "bandit" in (repo_path / "pyproject.toml").read_text():
        _append_if_unique(profile.security_commands, "bandit -q -r .")

    if not profile.test_commands:
        profile.notes.append("No obvious tests discovered")
    if not profile.run_commands:
        profile.notes.append("No obvious run command discovered")

    return profile


def scan_workspace(root: Path, max_depth: int = 3, excludes: Optional[Sequence[str]] = None) -> List[RepoProfile]:
    """Discover repos and return their inferred profiles."""

    repos = discover_git_repos(root, max_depth=max_depth, excludes=excludes)
    return [infer_repo_profile(repo) for repo in sorted(repos)]


def _run_shell(command: str, cwd: Path, category: str, timeout: int = 600) -> CommandResult:
    """Run a command and capture its output."""

    start = time.time()
    try:
        proc = subprocess.run(
            command,
            cwd=str(cwd),
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
            check=False,
        )
        duration = time.time() - start
        result = CommandResult(
            category=category,
            command=command,
            returncode=proc.returncode,
            stdout=proc.stdout,
            stderr=proc.stderr,
            duration_seconds=duration,
        )
    except subprocess.TimeoutExpired as exc:
        duration = time.time() - start
        result = CommandResult(
            category=category,
            command=command,
            returncode=-1,
            stdout=exc.stdout or "",
            stderr=f"Timed out after {timeout}s",
            duration_seconds=duration,
        )

    _log_line(f"{category.upper()} {command} ({cwd}) -> {result.returncode} in {result.duration_seconds:.1f}s")
    return result


def execute_tests(profile: RepoProfile, timeout: int = 600) -> Tuple[bool, List[CommandResult]]:
    """Run the best-effort test commands for a repository."""

    results: List[CommandResult] = []
    if not profile.test_commands:
        return True, results

    success = True
    for cmd in profile.test_commands:
        result = _run_shell(cmd, profile.path, category="test", timeout=timeout)
        results.append(result)
        if not result.ok:
            success = False
    return success, results


def execute_run(profile: RepoProfile, override_command: Optional[str] = None, timeout: Optional[int] = None) -> Tuple[int, str, str]:
    """Execute a run command (interactive servers typically left to the caller to stop)."""

    commands = [override_command] if override_command else profile.run_commands
    if not commands:
        raise ValueError(f"No run command available for {profile.name}")
    # Run only the first command; the CLI can be extended for more strategies later
    return _run_shell(commands[0], profile.path, timeout=timeout or 600)


def doctor_workspace(profiles: Iterable[RepoProfile]) -> List[str]:
    """Return diagnostic notes based on detected repo state."""

    notes: List[str] = []
    for profile in profiles:
        env_examples = list(profile.path.glob("env.*.example"))
        if not env_examples:
            notes.append(f"{profile.name}: missing env.*.example – add env templates for onboarding.")
        if not profile.test_commands:
            notes.append(f"{profile.name}: add pytest or npm tests so CI can run deterministically.")
        if "No obvious tests discovered" in profile.notes:
            notes.append(f"{profile.name}: add pytest or npm tests so CI can run deterministically.")
        if (profile.path / "docker-compose.yml").exists():
            notes.append(f"{profile.name}: docker-compose present – ensure health checks + lints in CI.")
    if not notes:
        notes.append("No doctor findings; workspace looks healthy.")
    return notes


def print_profiles(profiles: List[RepoProfile], as_json: bool = False) -> None:
    """Pretty-print repo profiles."""

    if as_json:
        json.dump([p.to_dict() for p in profiles], sys.stdout, indent=2)
        sys.stdout.write("\n")
        return

    for profile in profiles:
        print(f"- {profile.name} ({profile.path})")
        if profile.run_commands:
            print(f"  run: {profile.run_commands}")
        if profile.test_commands:
            print(f"  test: {profile.test_commands}")
        if profile.build_commands:
            print(f"  build: {profile.build_commands}")
        if profile.notes:
            print(f"  notes: {profile.notes}")
