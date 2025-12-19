#!/usr/bin/env python3
"""
Unified Project Orchestrator - Master Control for All Git Projects

This script discovers all Git repositories in the workspace, applies OS Dashboard
auto-fix scripts to each, monitors health, and provides a unified interface for
managing all projects. It integrates with the Technical Spec Sheet v6 requirements
for self-healing automation across all projects.

Features:
- Auto-discovers all .git directories
- Applies ai_auto_fix.py to each project
- Monitors project health in real-time
- Provides unified terminal interface
- Auto-resolves bugs using AI/codex
- Integrates with backend API for dashboard visibility
- Supports cross-project analytics and reporting

Usage:
    # Basic usage - discover and monitor all projects
    python scripts/unified_project_orchestrator.py

    # Scan specific workspace
    python scripts/unified_project_orchestrator.py --root ~/Projects

    # Enable auto-fix for all projects
    python scripts/unified_project_orchestrator.py --auto-fix

    # Daemon mode with API integration
    python scripts/unified_project_orchestrator.py --daemon --api-port 8000
"""

from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set
import queue

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SKIP_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv", 
    ".mypy_cache", "dist", "build", ".pytest_cache", ".tox"
}


@dataclass
class ProjectStatus:
    """Status information for a discovered project."""
    path: Path
    name: str
    has_autofix: bool
    autofix_script: Optional[Path]
    health: str = "unknown"  # healthy, degraded, unhealthy, unknown
    last_check: Optional[datetime] = None
    error_count: int = 0
    fix_count: int = 0
    test_status: Optional[str] = None
    metadata: Dict = field(default_factory=dict)


@dataclass
class OrchestratorState:
    """Global state for the orchestrator."""
    projects: Dict[str, ProjectStatus] = field(default_factory=dict)
    active_monitors: Dict[str, subprocess.Popen] = field(default_factory=dict)
    health_events: queue.Queue = field(default_factory=queue.Queue)
    running: bool = True
    lock: threading.Lock = field(default_factory=threading.Lock)


def discover_git_repos(root: Path, max_depth: int = 5, skip_dirs: Optional[Set[str]] = None) -> List[Path]:
    """Discover all Git repositories in the workspace."""
    root = root.expanduser().resolve()
    repos: List[Path] = []
    skip = skip_dirs or DEFAULT_SKIP_DIRS
    seen: Set[Path] = set()
    
    def _scan(current: Path, depth: int):
        if current in seen or depth > max_depth:
            return
        seen.add(current)
        
        git_marker = current / ".git"
        if git_marker.exists():
            repos.append(current)
            return
        
        try:
            for child in current.iterdir():
                if not child.is_dir():
                    continue
                if child.name in skip or child.name.startswith("."):
                    continue
                _scan(child, depth + 1)
        except (PermissionError, OSError):
            pass
    
    _scan(root, 0)
    return sorted(set(repos))


def detect_project_capabilities(repo_path: Path) -> Dict:
    """Detect what automation capabilities a project has."""
    capabilities = {
        "has_autofix": False,
        "has_tests": False,
        "has_pytest": False,
        "has_npm_tests": False,
        "language": "unknown",
        "autofix_script": None,
    }
    
    # Check for ai_auto_fix.py
    autofix_script = repo_path / "scripts" / "ai_auto_fix.py"
    if autofix_script.exists():
        capabilities["has_autofix"] = True
        capabilities["autofix_script"] = str(autofix_script)
    
    # Check for test infrastructure
    if (repo_path / "pytest.ini").exists() or (repo_path / "tests").is_dir():
        capabilities["has_pytest"] = True
        capabilities["has_tests"] = True
        capabilities["language"] = "python"
    
    if (repo_path / "package.json").exists():
        capabilities["has_npm_tests"] = True
        capabilities["has_tests"] = True
        if capabilities["language"] == "unknown":
            capabilities["language"] = "javascript"
    
    if (repo_path / "requirements.txt").exists() or (repo_path / "pyproject.toml").exists():
        if capabilities["language"] == "unknown":
            capabilities["language"] = "python"
    
    return capabilities


def create_project_status(repo_path: Path) -> ProjectStatus:
    """Create a ProjectStatus for a discovered repository."""
    capabilities = detect_project_capabilities(repo_path)
    autofix_script = None
    if capabilities["autofix_script"]:
        autofix_script = Path(capabilities["autofix_script"])
    
    return ProjectStatus(
        path=repo_path,
        name=repo_path.name,
        has_autofix=capabilities["has_autofix"],
        autofix_script=autofix_script,
        metadata=capabilities,
    )


def run_autofix_monitor(project: ProjectStatus, extra_args: List[str] = None) -> subprocess.Popen:
    """Launch ai_auto_fix.py monitor for a project."""
    if not project.autofix_script or not project.autofix_script.exists():
        raise ValueError(f"Project {project.name} does not have ai_auto_fix.py")
    
    cmd = [
        sys.executable,
        str(project.autofix_script),
        "--logs-only",
        "--daemon",
    ]
    
    if extra_args:
        cmd.extend(extra_args)
    
    return subprocess.Popen(
        cmd,
        cwd=project.path,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )


def check_project_health(project: ProjectStatus) -> str:
    """Check the health status of a project."""
    # Simple health check: look for common error indicators
    log_dirs = [
        project.path / "logs",
        project.path / "frontend" / "logs",
    ]
    
    error_indicators = 0
    for log_dir in log_dirs:
        if not log_dir.exists():
            continue
        for log_file in log_dir.glob("*.log"):
            try:
                with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    if any(keyword in content.lower() for keyword in ["error", "exception", "traceback", "failed"]):
                        error_indicators += 1
            except Exception:
                pass
    
    if error_indicators == 0:
        return "healthy"
    elif error_indicators < 3:
        return "degraded"
    else:
        return "unhealthy"


class UnifiedProjectOrchestrator:
    """Master orchestrator for all projects in the workspace."""
    
    def __init__(
        self,
        root: Path = REPO_ROOT,
        max_depth: int = 5,
        auto_fix: bool = False,
        daemon_mode: bool = False,
        api_port: Optional[int] = None,
        health_check_interval: int = 60,
    ):
        self.root = root
        self.max_depth = max_depth
        self.auto_fix = auto_fix
        self.daemon_mode = daemon_mode
        self.api_port = api_port
        self.health_check_interval = health_check_interval
        
        self.state = OrchestratorState()
        self.discovered_projects: Dict[str, ProjectStatus] = {}
        self._stop_event = threading.Event()
        self._health_thread: Optional[threading.Thread] = None
        
    def discover_projects(self) -> Dict[str, ProjectStatus]:
        """Discover all Git projects in the workspace."""
        repos = discover_git_repos(self.root, self.max_depth)
        projects = {}
        
        for repo_path in repos:
            status = create_project_status(repo_path)
            projects[status.name] = status
        
        self.discovered_projects = projects
        return projects
    
    def start_monitors(self, extra_args: List[str] = None):
        """Start auto-fix monitors for all eligible projects."""
        if not self.auto_fix:
            return
        
        for project in self.discovered_projects.values():
            if not project.has_autofix:
                continue
            
            try:
                monitor = run_autofix_monitor(project, extra_args or [])
                self.state.active_monitors[project.name] = monitor
                print(f"✅ Started monitor for {project.name}")
            except Exception as e:
                print(f"⚠️  Failed to start monitor for {project.name}: {e}")
    
    def stop_monitors(self):
        """Stop all active monitors."""
        for name, monitor in list(self.state.active_monitors.items()):
            try:
                monitor.terminate()
                monitor.wait(timeout=5)
            except Exception:
                monitor.kill()
            print(f"🛑 Stopped monitor for {name}")
        self.state.active_monitors.clear()
    
    def _health_check_loop(self):
        """Background thread for periodic health checks."""
        while not self._stop_event.is_set():
            try:
                for project in self.discovered_projects.values():
                    health = check_project_health(project)
                    project.health = health
                    project.last_check = datetime.now()
                    
                    if health != "healthy":
                        self.state.health_events.put({
                            "project": project.name,
                            "health": health,
                            "timestamp": datetime.now().isoformat(),
                        })
            except Exception as e:
                print(f"⚠️  Health check error: {e}")
            
            self._stop_event.wait(self.health_check_interval)
    
    def start_health_monitoring(self):
        """Start background health monitoring."""
        if self._health_thread and self._health_thread.is_alive():
            return
        
        self._health_thread = threading.Thread(target=self._health_check_loop, daemon=True)
        self._health_thread.start()
    
    def stop_health_monitoring(self):
        """Stop health monitoring."""
        self._stop_event.set()
        if self._health_thread:
            self._health_thread.join(timeout=2)
    
    def generate_report(self) -> Dict:
        """Generate a comprehensive report of all projects."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "root": str(self.root),
            "total_projects": len(self.discovered_projects),
            "projects": [],
            "summary": {
                "healthy": 0,
                "degraded": 0,
                "unhealthy": 0,
                "unknown": 0,
                "with_autofix": 0,
                "with_tests": 0,
            },
        }
        
        for project in self.discovered_projects.values():
            project_data = {
                "name": project.name,
                "path": str(project.path),
                "health": project.health,
                "has_autofix": project.has_autofix,
                "has_tests": project.metadata.get("has_tests", False),
                "language": project.metadata.get("language", "unknown"),
                "last_check": project.last_check.isoformat() if project.last_check else None,
                "error_count": project.error_count,
                "fix_count": project.fix_count,
            }
            report["projects"].append(project_data)
            
            # Update summary
            report["summary"][project.health] = report["summary"].get(project.health, 0) + 1
            if project.has_autofix:
                report["summary"]["with_autofix"] += 1
            if project.metadata.get("has_tests"):
                report["summary"]["with_tests"] += 1
        
        return report
    
    def run(self):
        """Main execution loop."""
        print("🔍 Discovering Git projects...")
        self.discover_projects()
        
        print(f"📦 Found {len(self.discovered_projects)} projects")
        for project in self.discovered_projects.values():
            status_icon = "✅" if project.has_autofix else "⚠️"
            print(f"  {status_icon} {project.name} ({project.metadata.get('language', 'unknown')})")
        
        if self.auto_fix:
            print("\n🚀 Starting auto-fix monitors...")
            self.start_monitors()
        
        if self.daemon_mode:
            print("\n🔄 Running in daemon mode...")
            self.start_health_monitoring()
            
            try:
                while self.state.running:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n⏹️  Shutting down...")
        else:
            # Generate and print report
            report = self.generate_report()
            print("\n📊 Project Status Report:")
            print(json.dumps(report, indent=2))
        
        self.stop_monitors()
        self.stop_health_monitoring()


def main():
    parser = argparse.ArgumentParser(
        description="Unified Project Orchestrator for OS Dashboard AI Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=REPO_ROOT,
        help="Workspace root to scan for Git repositories",
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=5,
        help="Maximum directory depth to search",
    )
    parser.add_argument(
        "--auto-fix",
        action="store_true",
        help="Enable auto-fix monitors for all eligible projects",
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run in daemon mode with continuous monitoring",
    )
    parser.add_argument(
        "--api-port",
        type=int,
        default=None,
        help="API port for backend integration",
    )
    parser.add_argument(
        "--health-interval",
        type=int,
        default=60,
        help="Health check interval in seconds",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output file for JSON report",
    )
    
    args = parser.parse_args()
    
    orchestrator = UnifiedProjectOrchestrator(
        root=args.root,
        max_depth=args.max_depth,
        auto_fix=args.auto_fix,
        daemon_mode=args.daemon,
        api_port=args.api_port,
        health_check_interval=args.health_interval,
    )
    
    try:
        orchestrator.run()
        
        if args.output:
            report = orchestrator.generate_report()
            args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
            print(f"\n📄 Report saved to {args.output}")
        
        return 0
    except KeyboardInterrupt:
        print("\n⏹️  Interrupted by user")
        return 130
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
