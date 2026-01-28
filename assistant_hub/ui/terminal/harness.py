"""Lightweight execution harness for osdash."""
from __future__ import annotations

import json
import os
import shlex
import socket
import subprocess
import sys
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

REPO_ROOT = Path(__file__).resolve().parents[3]
LOG_DIR_ENV = "OSDASH_HARNESS_LOG_DIR"
DEFAULT_LOG_DIR = REPO_ROOT / "logs" / "osdash"
SKIP_DIRS = {".git", ".hg", ".svn", "__pycache__", "node_modules", "dist", "build"}
DEFAULT_TIMEOUT_SECONDS = 300


def _log_dir() -> Path:
    """Resolve the harness log directory, honoring overrides."""

    override = os.environ.get(LOG_DIR_ENV)
    if override:
        return Path(override).expanduser().resolve()
    return DEFAULT_LOG_DIR


@dataclass
class CheckResult:
    category: str
    command: List[str]
    status: str
    exit_code: Optional[int]
    duration_seconds: float
    output: str
    ran_at: float
    run_id: str
    timeout_seconds: int
    error: Optional[str] = None

    def as_dict(self) -> Dict[str, object]:
        return {
            "category": self.category,
            "command": self.command,
            "status": self.status,
            "exit_code": self.exit_code,
            "duration_seconds": round(self.duration_seconds, 2),
            "output": self.output,
            "ran_at": self.ran_at,
            "run_id": self.run_id,
            "timeout_seconds": self.timeout_seconds,
            "error": self.error,
        }


@dataclass
class ProjectProfile:
    name: str
    root: Path
    commands: Dict[str, List[List[str]]] = field(default_factory=dict)
    autofix_script: Optional[Path] = None

    def as_dict(self) -> Dict[str, object]:
        return {
            "name": self.name,
            "root": str(self.root),
            "commands": self.commands,
            "autofix_script": str(self.autofix_script) if self.autofix_script else None,
        }


def _load_scripts(package_json: Path) -> Dict[str, str]:
    try:
        data = json.loads(package_json.read_text())
        scripts = data.get("scripts", {})
        return scripts if isinstance(scripts, dict) else {}
    except Exception:
        return {}


def _discover_git_roots(base: Path, max_depth: int = 2) -> List[Path]:
    discovered: List[Path] = []
    seen: set[Path] = set()

    def _scan(current: Path, depth: int) -> None:
        resolved = current.resolve()
        if resolved in seen:
            return
        seen.add(resolved)
        if (resolved / ".git").exists():
            discovered.append(resolved)
            return
        if depth <= 0:
            return
        for child in resolved.iterdir():
            if not child.is_dir():
                continue
            if child.name in SKIP_DIRS or child.name.startswith("."):
                continue
            _scan(child, depth - 1)

    _scan(base, max_depth)
    return sorted(discovered)


def _detect_frontend_commands(repo: Path) -> Dict[str, List[List[str]]]:
    commands: Dict[str, List[List[str]]] = {"lint": [], "test": [], "build": []}
    frontend_pkg = repo / "frontend" / "package.json"
    if not frontend_pkg.exists():
        return commands
    scripts = _load_scripts(frontend_pkg)
    if "lint" in scripts:
        commands["lint"].append(["npm", "run", "lint", "--prefix", "frontend"])
    commands["test"].append(["npm", "run", "test", "--prefix", "frontend", "--", "--runInBand"])
    commands["build"].append(["npm", "run", "build", "--prefix", "frontend"])
    return commands


def _detect_python_commands(repo: Path) -> Dict[str, List[List[str]]]:
    commands: Dict[str, List[List[str]]] = {"lint": [], "test": [], "security": []}
    pyproject = repo / "pyproject.toml"
    requirements = repo / "requirements.txt"
    if pyproject.exists() or requirements.exists():
        commands["lint"].append([sys.executable, "-m", "flake8", "assistant_core", "backend_api", "tests"])
        commands["test"].append([sys.executable, "-m", "pytest", "-q"])
        commands["security"].append([sys.executable, "-m", "pip", "check"])
    return commands


def detect_project_profile(repo: Path) -> ProjectProfile:
    commands: Dict[str, List[List[str]]] = {
        "lint": [],
        "test": [],
        "build": [],
        "security": [],
    }
    python_cmds = _detect_python_commands(repo)
    frontend_cmds = _detect_frontend_commands(repo)

    for key in commands:
        commands[key].extend(python_cmds.get(key, []))
        commands[key].extend(frontend_cmds.get(key, []))

    autofix_script = repo / "scripts" / "ai_auto_fix.py"
    if not autofix_script.exists():
        autofix_script = None

    return ProjectProfile(
        name=repo.name,
        root=repo,
        commands={k: v for k, v in commands.items() if v},
        autofix_script=autofix_script,
    )


def discover_profiles(base: Path, max_depth: int = 2) -> List[ProjectProfile]:
    profiles: List[ProjectProfile] = []
    for repo in _discover_git_roots(base, max_depth=max_depth):
        profile = detect_project_profile(repo)
        if profile.commands:
            profiles.append(profile)
    return profiles


def _run_command(
    command: List[str],
    cwd: Path,
    *,
    run_id: Optional[str] = None,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
) -> CheckResult:
    start = time.time()
    joined = shlex.join(command)
    resolved_run_id = run_id or str(uuid.uuid4())
    try:
        proc = subprocess.run(
            command,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=timeout_seconds,
        )
        status = "passed" if proc.returncode == 0 else "failed"
        output = proc.stdout or ""
        exit_code: Optional[int] = proc.returncode
        error: Optional[str] = None
    except subprocess.TimeoutExpired as exc:
        status = "failed"
        output = exc.stdout or f"timed out after {timeout_seconds}s"
        exit_code = None
        error = f"timeout: {joined}"
    except FileNotFoundError as exc:
        status = "skipped"
        output = f"command not found: {exc.filename}"
        exit_code = None
        error = output
    duration = time.time() - start
    return CheckResult(
        category="runtime",
        command=command,
        status=status,
        exit_code=exit_code,
        duration_seconds=duration,
        output=output,
        ran_at=start,
        run_id=resolved_run_id,
        timeout_seconds=timeout_seconds,
        error=error,
    )


def run_checks(
    profile: ProjectProfile,
    categories: Sequence[str],
    autofix: bool = False,
    *,
    run_id: Optional[str] = None,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
) -> List[CheckResult]:
    results: List[CheckResult] = []
    resolved_run_id = run_id or str(uuid.uuid4())
    for category in categories:
        for command in profile.commands.get(category, []):
            result = _run_command(
                command,
                cwd=profile.root,
                run_id=resolved_run_id,
                timeout_seconds=timeout_seconds,
            )
            result.category = category
            results.append(result)
            if result.status == "failed" and autofix and profile.autofix_script:
                subprocess.run(
                    [sys.executable, str(profile.autofix_script), "--logs-only"],
                    cwd=profile.root,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
    return results


def write_report(profile: ProjectProfile, results: List[CheckResult]) -> Path:
    log_dir = _log_dir()
    log_dir.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    path = log_dir / f"{profile.name}-report-{timestamp}.json"
    summary = {
        "run_id": results[0].run_id if results else str(uuid.uuid4()),
        "timestamp": timestamp,
        "counts": {
            "total": len(results),
            "passed": len([r for r in results if r.status == "passed"]),
            "failed": len([r for r in results if r.status == "failed"]),
            "skipped": len([r for r in results if r.status == "skipped"]),
        },
    }
    payload = {
        "profile": profile.as_dict(),
        "summary": summary,
        "results": [r.as_dict() for r in results],
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def write_workspace_report(
    root: Path,
    project_results: Sequence[Tuple[ProjectProfile, List[CheckResult]]],
    path: Optional[Path] = None,
    *,
    dry_run: bool = False,
    run_id: Optional[str] = None,
) -> Path:
    """
    Aggregate results for multiple projects into a single JSON report.
    """
    log_dir = _log_dir()
    log_dir.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    report_path = path or log_dir / f"workspace-report-{timestamp}.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    resolved_run_id = run_id
    if not resolved_run_id and project_results and project_results[0][1]:
        resolved_run_id = project_results[0][1][0].run_id

    summary: Dict[str, object] = {
        "root": str(root.resolve()),
        "generated_at": timestamp,
        "run_id": resolved_run_id or str(uuid.uuid4()),
        "projects": len(project_results),
        "checks": 0,
        "failed": 0,
        "passed": 0,
        "skipped": 0,
        "dry_run": dry_run,
        "status": "pending",
    }

    details = []
    failures = []
    for profile, results in project_results:
        summary["checks"] += len(results)
        summary["failed"] += len([r for r in results if r.status == "failed"])
        summary["passed"] += len([r for r in results if r.status == "passed"])
        summary["skipped"] += len([r for r in results if r.status == "skipped"])
        failed_results = [r for r in results if r.status == "failed"]
        project_run_id = results[0].run_id if results else summary["run_id"]
        counts = {
            "total": len(results),
            "failed": len([r for r in results if r.status == "failed"]),
            "passed": len([r for r in results if r.status == "passed"]),
            "skipped": len([r for r in results if r.status == "skipped"]),
        }
        details.append(
            {
                "profile": profile.as_dict(),
                "results": [r.as_dict() for r in results],
                "counts": counts,
                "status": "passed" if not failed_results else "failed",
                "run_id": project_run_id,
            }
        )
        for failure in failed_results:
            failures.append(
                {
                    "project": profile.name,
                    "category": failure.category,
                    "command": failure.command,
                    "status": failure.status,
                    "exit_code": failure.exit_code,
                    "output_tail": failure.output.splitlines()[-5:],
                }
            )

    payload = {
        "summary": {**summary, "status": "passed" if summary["failed"] == 0 else "failed"},
        "projects": details,
        "errors": failures,
        "report_path": str(report_path),
    }
    report_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return report_path


def latest_workspace_report(log_dir: Optional[Path] = None) -> Optional[Dict[str, object]]:
    """Load the newest workspace report if one exists."""

    directory = log_dir or _log_dir()
    if not directory.exists():
        return None
    candidates = sorted(
        directory.glob("workspace-report-*.json"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    for path in candidates:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["report_path"] = str(path)
            return payload
        except (json.JSONDecodeError, OSError):
            continue
    return None


def scan_summary(base: Path, max_depth: int = 2) -> Dict[str, object]:
    profiles = discover_profiles(base, max_depth=max_depth)
    return {
        "root": str(base.resolve()),
        "projects": [profile.as_dict() for profile in profiles],
    }


def _port_open(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.2)
        return sock.connect_ex(("127.0.0.1", port)) == 0


def doctor(base: Path) -> Dict[str, object]:
    checks: List[Dict[str, object]] = []

    def _version_check(label: str, command: List[str]) -> None:
        result = _run_command(command, cwd=base)
        checks.append(
            {
                "label": label,
                "status": result.status,
                "output": result.output.splitlines()[:3],
            }
        )

    _version_check("python", [sys.executable, "--version"])
    _version_check("pip", [sys.executable, "-m", "pip", "--version"])
    _version_check("node", ["node", "--version"])
    _version_check("npm", ["npm", "--version"])

    env_files = [f for f in base.glob("env.*.example")]
    checks.append(
        {
            "label": "env_templates",
            "status": "present" if env_files else "missing",
            "output": [f.name for f in env_files],
        }
    )

    ports = {8000: _port_open(8000), 5173: _port_open(5173)}
    checks.append(
        {
            "label": "ports",
            "status": "ok",
            "output": [f"{port}: {'open' if open_ else 'free'}" for port, open_ in ports.items()],
        }
    )

    return {"checks": checks, "timestamp": time.time()}


def run_workspace_checks(
    base: Path,
    categories: Sequence[str],
    max_depth: int = 2,
    autofix: bool = False,
    dry_run: bool = True,
    report_path: Optional[Path] = None,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
) -> Dict[str, object]:
    """Run standardized checks across all detected repos and emit a consolidated report."""

    selected_categories = list(categories) or ["lint", "test", "build", "security"]
    profiles = discover_profiles(base, max_depth=max_depth)
    run_id = str(uuid.uuid4())

    project_results: List[Tuple[ProjectProfile, List[CheckResult]]] = []
    rendered_results: List[Dict[str, object]] = []

    for profile in profiles:
        if dry_run:
            placeholder: List[CheckResult] = []
            for category in selected_categories:
                for command in profile.commands.get(category, []):
                    placeholder.append(
                        CheckResult(
                            category=category,
                            command=command,
                            status="skipped",
                            exit_code=None,
                            duration_seconds=0.0,
                            output="dry-run (command not executed)",
                            ran_at=time.time(),
                            run_id=run_id,
                            timeout_seconds=timeout_seconds,
                            error=None,
                        )
                    )
            project_results.append((profile, placeholder))
        else:
            results = run_checks(
                profile,
                selected_categories,
                autofix=autofix,
                run_id=run_id,
                timeout_seconds=timeout_seconds,
            )
            project_results.append((profile, results))

    for profile, results in project_results:
        for result in results:
            payload = result.as_dict()
            payload["project"] = profile.name
            rendered_results.append(payload)

    report = write_workspace_report(base, project_results, path=report_path, dry_run=dry_run)
    summary = {
        "root": str(base.resolve()),
        "generated_at": time.time(),
        "report_path": str(report),
        "projects": len(project_results),
        "checks": len(rendered_results),
        "failed": len([r for r in rendered_results if r.get("status") == "failed"]),
        "passed": len([r for r in rendered_results if r.get("status") == "passed"]),
        "skipped": len([r for r in rendered_results if r.get("status") == "skipped"]),
        "run_id": run_id,
        "dry_run": dry_run,
    }
    summary["status"] = "passed" if summary["failed"] == 0 else "failed"

    return {
        "summary": summary,
        "profiles": [profile.as_dict() for profile, _ in project_results],
        "results": rendered_results,
    }


def run_target(profile: ProjectProfile, target: str) -> int:
    commands = {
        "backend": [sys.executable, "-m", "backend_api.main"],
        "frontend": ["npm", "run", "dev:web", "--prefix", "frontend"],
        "desktop": ["npm", "run", "dev:desktop", "--prefix", "frontend"],
    }
    if target not in commands:
        print(f"[osdash] unknown run target: {target}")
        return 1
    cmd = commands[target]
    print(f"[osdash] launching {target} -> {shlex.join(cmd)}")
    proc = subprocess.Popen(cmd, cwd=profile.root)
    try:
        proc.wait()
    except KeyboardInterrupt:
        proc.terminate()
    return proc.returncode or 0
