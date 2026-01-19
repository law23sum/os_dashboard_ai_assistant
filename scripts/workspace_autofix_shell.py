#!/usr/bin/env python3
"""Interactive workspace shell that dispatches ai_auto_fix/test loops per git repo."""

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Dict, Any

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_AUTOFIX_REL = Path("scripts") / "ai_auto_fix.py"
SKIP_DIRS = {
    ".git",
    ".hg",
    ".svn",
    "__pycache__",
    ".venv",
    "node_modules",
    "dist",
    "build",
    "logs",
}
LOG_DIR = REPO_ROOT / "logs" / "workspace_shell"
LOG_DIR.mkdir(parents=True, exist_ok=True)
TELEMETRY_DIR = REPO_ROOT / "logs" / "workspace_shell"
TELEMETRY_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class ProjectProfile:
    name: str
    root: Path
    ai_autofix: Optional[Path]
    test_commands: List[List[str]] = field(default_factory=list)

@dataclass
class CommandResult:
    profile_name: str
    command: List[str]
    exit_code: int
    timestamp: str
    attempt: int
    autofix_invoked: bool = False
    autofix_exit_code: Optional[int] = None

@dataclass
class TelemetrySnapshot:
    timestamp: str
    total_profiles: int
    profiles_run: int
    total_commands: int
    successful_commands: int
    failed_commands: int
    autofix_attempts: int
    latest_failure_timestamp: Optional[str] = None
    results: List[Dict[str, Any]] = field(default_factory=list)


def _timestamp() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S")


def _discover_git_roots(workspaces: Sequence[Path], max_depth: int) -> List[Path]:
    discovered: List[Path] = []
    seen: set[Path] = set()

    def _scan(base: Path, depth: int) -> None:
        resolved = base.resolve()
        if resolved in seen:
            return
        seen.add(resolved)
        if (resolved / ".git").exists():
            discovered.append(resolved)
        if depth <= 0:
            return
        for child in resolved.iterdir():
            if not child.is_dir():
                continue
            if child.name in SKIP_DIRS or child.name.startswith(".") and child.name != ".git":
                continue
            try:
                _scan(child, depth - 1)
            except PermissionError:
                continue

    for workspace in workspaces:
        if workspace.exists():
            _scan(workspace, max_depth)
    return discovered


def _detect_tests(root: Path) -> List[List[str]]:
    commands: List[List[str]] = []
    scripted = root / "scripts" / "run_tests_with_autofix.py"
    if scripted.exists():
        commands.append([sys.executable, str(scripted)])
        return commands
    package_json = root / "package.json"
    if package_json.exists():
        commands.append(["npm", "test", "--", "--runInBand"])
    if (root / "pyproject.toml").exists() or (root / "requirements.txt").exists():
        commands.append([sys.executable, "-m", "pytest", "-q"])
    return commands


def _construct_profiles(
    workspaces: Sequence[Path],
    max_depth: int,
    autofix_rel: Path,
) -> List[ProjectProfile]:
    profiles: List[ProjectProfile] = []
    for repo in _discover_git_roots(workspaces, max_depth):
        ai_path = repo / autofix_rel
        if not ai_path.exists():
            ai_path = REPO_ROOT / autofix_rel
        ai_ref = ai_path if ai_path.exists() else None
        tests = _detect_tests(repo)
        if not tests and not ai_ref:
            continue
        profiles.append(ProjectProfile(name=repo.name, root=repo, ai_autofix=ai_ref, test_commands=tests))
    profiles.sort(key=lambda profile: profile.root.as_posix())
    return profiles


def _run_command(command: List[str], cwd: Path, log_path: Path) -> int:
    display = shlex.join(command)
    print(f"[shell] ▶️  {cwd.name}: {display}")
    proc = subprocess.run(
        command,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(f"[{_timestamp()}] $ {display}\n")
        handle.write(proc.stdout or "")
        handle.write(f"\n[{_timestamp()}] exit={proc.returncode}\n")
        handle.write("-" * 80 + "\n")
    if proc.returncode == 0:
        print(f"[shell] ✅ {cwd.name}: success")
    else:
        print(f"[shell] ❌ {cwd.name}: exit {proc.returncode} — see {log_path}")
    return proc.returncode


def _invoke_autofix(
    profile: ProjectProfile,
    failing_cmd: List[str],
    log_path: Path,
    extra_args: Sequence[str],
) -> None:
    if not profile.ai_autofix:
        print(f"[shell] ⚠️  {profile.name}: ai_auto_fix.py not found, skipping automated repair.")
        return
    label = f"{profile.name}-auto"
    cmd = [
        sys.executable,
        str(profile.ai_autofix),
        "--logs-only",
        "--no-daemon",
        "--test",
        f"{label}={shlex.join(failing_cmd)}",
    ]
    cmd.extend(extra_args)
    print(f"[shell] 🤖 {profile.name}: launching auto-fix -> {' '.join(cmd)}")
    proc = subprocess.run(cmd, cwd=profile.root, text=True)
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(f"[{_timestamp()}] auto-fix cmd: {' '.join(cmd)}\n")
        handle.write(f"[{_timestamp()}] auto-fix exit={proc.returncode}\n")
        handle.write("-" * 80 + "\n")


def _prompt_selection(profiles: List[ProjectProfile]) -> List[ProjectProfile]:
    if not profiles:
        return []
    print("\n=== Workspace Auto-Fix Shell ===")
    for idx, profile in enumerate(profiles, start=1):
        tests = f"{len(profile.test_commands)} test suites" if profile.test_commands else "no tests"
        autofix = "auto-fix ready" if profile.ai_autofix else "no ai_auto_fix"
        print(f"[{idx}] {profile.name:<20} • {tests} • {autofix}")
    print("[A] Run all projects")
    print("[Q] Quit")
    while True:
        choice = input("Select project(s) (comma-separated index): ").strip().lower()
        if choice in {"q", "quit"}:
            return []
        if choice in {"a", "all"}:
            return profiles
        if not choice:
            continue
        try:
            indices = [int(part) for part in choice.split(",")]
        except ValueError:
            print("Enter comma-separated numbers, 'A' for all, or 'Q' to quit.")
            continue
        selected: List[ProjectProfile] = []
        for idx in indices:
            if 1 <= idx <= len(profiles):
                selected.append(profiles[idx - 1])
        if selected:
            return selected
        print("No valid selections. Try again.")


def _export_telemetry_json(snapshot: TelemetrySnapshot, output_path: Path) -> None:
    """Export structured JSON telemetry for observability collectors."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(asdict(snapshot), f, indent=2, default=str)
    print(f"[telemetry] Exported JSON snapshot to {output_path}")


def _run_profiles(
    targets: List[ProjectProfile],
    attempts: int,
    autofix_enabled: bool,
    extra_autofix_args: Sequence[str],
    export_json: bool = False,
) -> TelemetrySnapshot:
    snapshot = TelemetrySnapshot(
        timestamp=_timestamp(),
        total_profiles=len(targets),
        profiles_run=0,
        total_commands=0,
        successful_commands=0,
        failed_commands=0,
        autofix_attempts=0,
    )
    
    for profile in targets:
        log_path = LOG_DIR / f"{profile.name}.log"
        snapshot.profiles_run += 1
        
        if not profile.test_commands:
            print(f"[shell] ℹ️  {profile.name}: no tests detected. Triggering auto-fix daemon only.")
            autofix_exit = None
            try:
                _invoke_autofix(
                    profile,
                    [sys.executable, "-c", "import sys; sys.exit(0)"],
                    log_path,
                    extra_autofix_args,
                )
                autofix_exit = 0
            except Exception as e:
                print(f"[shell] ⚠️  Auto-fix error: {e}")
                autofix_exit = 1
            
            if export_json:
                result = CommandResult(
                    profile_name=profile.name,
                    command=["daemon-only"],
                    exit_code=0,
                    timestamp=_timestamp(),
                    attempt=1,
                    autofix_invoked=True,
                    autofix_exit_code=autofix_exit,
                )
                snapshot.results.append(asdict(result))
                if autofix_exit is not None:
                    snapshot.autofix_attempts += 1
            continue
            
        for command in profile.test_commands:
            snapshot.total_commands += 1
            attempt = 0
            command_succeeded = False
            
            while attempt < max(1, attempts):
                attempt += 1
                print(f"[shell] {profile.name}: attempt {attempt}/{attempts} for {shlex.join(command)}")
                result_code = _run_command(command, profile.root, log_path)
                
                if result_code == 0:
                    command_succeeded = True
                    snapshot.successful_commands += 1
                    if export_json:
                        result = CommandResult(
                            profile_name=profile.name,
                            command=command,
                            exit_code=0,
                            timestamp=_timestamp(),
                            attempt=attempt,
                            autofix_invoked=False,
                        )
                        snapshot.results.append(asdict(result))
                    break
                    
                if autofix_enabled:
                    autofix_exit = None
                    try:
                        _invoke_autofix(profile, command, log_path, extra_autofix_args)
                        autofix_exit = 0
                        snapshot.autofix_attempts += 1
                    except Exception as e:
                        print(f"[shell] ⚠️  Auto-fix error: {e}")
                        autofix_exit = 1
                        snapshot.autofix_attempts += 1
                    
                    if export_json:
                        result = CommandResult(
                            profile_name=profile.name,
                            command=command,
                            exit_code=result_code,
                            timestamp=_timestamp(),
                            attempt=attempt,
                            autofix_invoked=True,
                            autofix_exit_code=autofix_exit,
                        )
                        snapshot.results.append(asdict(result))
            else:
                if not command_succeeded:
                    snapshot.failed_commands += 1
                    snapshot.latest_failure_timestamp = _timestamp()
                    print(f"[shell] ⚠️  {profile.name}: exhausted attempts for {shlex.join(command)}")
    
    return snapshot


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scan git repositories and run tests + ai_auto_fix loops.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--workspace",
        action="append",
        type=Path,
        help="Workspace root to scan (repeatable). Defaults to repo root.",
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=3,
        help="Maximum depth when crawling for git repositories.",
    )
    parser.add_argument(
        "--autofix-rel",
        type=Path,
        default=DEFAULT_AUTOFIX_REL,
        help="Relative path to ai_auto_fix.py inside each repo.",
    )
    parser.add_argument(
        "--project",
        action="append",
        help="Limit execution to repositories matching this name (exact match, repeatable).",
    )
    parser.add_argument(
        "--run-all",
        action="store_true",
        help="Run every discovered profile without prompting.",
    )
    parser.add_argument(
        "--attempts",
        type=int,
        default=2,
        help="Retries per test command before declaring failure.",
    )
    parser.add_argument(
        "--no-autofix",
        action="store_true",
        help="Skip invoking ai_auto_fix when tests fail.",
    )
    parser.add_argument(
        "--autofix-arg",
        action="append",
        default=[],
        help="Additional arguments forwarded to every ai_auto_fix invocation.",
    )
    parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Run in batch mode (same as --run-all) and exit.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Export structured JSON telemetry alongside log files for observability collectors.",
    )
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    workspaces = args.workspace or [REPO_ROOT]
    workspaces = [path.expanduser().resolve() for path in workspaces]
    profiles = _construct_profiles(workspaces, args.max_depth, args.autofix_rel)
    if args.project:
        allowed = {name.lower() for name in args.project}
        profiles = [profile for profile in profiles if profile.name.lower() in allowed]
    if not profiles:
        print("[shell] No eligible repositories found. Ensure they contain tests or ai_auto_fix.py.")
        return 1
    if args.run_all or args.non_interactive:
        selected = profiles
    else:
        selected = _prompt_selection(profiles)
    if not selected:
        print("[shell] Nothing selected. Exiting.")
        return 0
    
    snapshot = _run_profiles(
        selected,
        attempts=max(1, args.attempts),
        autofix_enabled=not args.no_autofix,
        extra_autofix_args=list(args.autofix_arg),
        export_json=args.json,
    )
    
    if args.json:
        telemetry_path = TELEMETRY_DIR / f"telemetry_{int(time.time())}.json"
        _export_telemetry_json(snapshot, telemetry_path)
        # Also write latest snapshot
        latest_path = TELEMETRY_DIR / "telemetry_latest.json"
        _export_telemetry_json(snapshot, latest_path)
        print(f"\n[telemetry] Summary: {snapshot.successful_commands} successful, {snapshot.failed_commands} failed, {snapshot.autofix_attempts} autofix attempts")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
