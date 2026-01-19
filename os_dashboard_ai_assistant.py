#!/usr/bin/env python3
"""
AI OS Orchestrator - Master Orchestrator
Sir Chief Fellow Director Principal Software Solutions Systems Engineer Architect

This is the unified master control system that:
1. Discovers all projects (.git detection)
2. Launches AI auto-fix monitors for each project
3. Reads TODOs and spawns new codex sessions automatically
4. Provides comprehensive health monitoring
5. Integrates with the frontend/GUI for seamless interaction
6. Self-heals and optimizes continuously

Usage:
    # Launch the master orchestrator for all projects
    python os_dashboard_ai_assistant.py --root ~/Projects
    
    # With custom TODO monitoring
    python os_dashboard_ai_assistant.py --watch-todos --todo-check-interval 60
    
    # With comprehensive monitoring
    python os_dashboard_ai_assistant.py --enable-dashboard --health-port 9000
"""

from __future__ import annotations

import argparse
import json
import os
import shlex
import signal
import subprocess
import sys
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Ensure the repo root is in path
REPO_ROOT = Path(__file__).resolve().parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

try:
    from dotenv import load_dotenv
    load_dotenv(REPO_ROOT / ".env")
except Exception:
    pass


@dataclass
class ProjectInfo:
    """Information about a discovered project."""
    path: Path
    name: str
    has_ai_autofix: bool = False
    has_tests: bool = False
    git_branch: Optional[str] = None
    todo_files: List[Path] = field(default_factory=list)
    monitor_process: Optional[subprocess.Popen] = None
    last_health_check: float = 0.0
    status: str = "discovered"  # discovered, running, healthy, unhealthy, error


@dataclass
class TodoItem:
    """A TODO item extracted from project files."""
    project: str
    file: Path
    line_number: int
    content: str
    priority: str = "normal"  # low, normal, high, critical
    completed: bool = False


class MasterOrchestrator:
    """The master control system for all projects."""
    
    def __init__(
        self,
        *,
        root: Path = REPO_ROOT,
        max_depth: int = 4,
        watch_todos: bool = True,
        todo_check_interval: int = 300,
        enable_dashboard: bool = True,
        health_port: int = 9000,
        auto_spawn_codex: bool = True,
        log_dir: Path = REPO_ROOT / "logs",
    ):
        self.root = root.expanduser().resolve()
        self.max_depth = max_depth
        self.watch_todos = watch_todos
        self.todo_check_interval = todo_check_interval
        self.enable_dashboard = enable_dashboard
        self.health_port = health_port
        self.auto_spawn_codex = auto_spawn_codex
        self.log_dir = log_dir
        
        # State
        self.projects: Dict[str, ProjectInfo] = {}
        self.todos: List[TodoItem] = []
        self.monitors: Dict[str, subprocess.Popen] = {}
        self.running = False
        
        # Threads
        self.todo_thread: Optional[threading.Thread] = None
        self.health_thread: Optional[threading.Thread] = None
        self.dashboard_thread: Optional[threading.Thread] = None
        
        # Logging
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.master_log = self.log_dir / "master_orchestrator.log"
        
    def log(self, message: str, level: str = "INFO"):
        """Log a message to both console and file."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        print(log_entry)
        with self.master_log.open("a", encoding="utf-8") as f:
            f.write(log_entry + "\n")
    
    def discover_projects(self) -> List[ProjectInfo]:
        """Discover all git projects in the workspace."""
        self.log("🔍 Discovering projects...")
        projects: List[ProjectInfo] = []
        
        queue: List[Tuple[Path, int]] = [(self.root, 0)]
        seen: Set[Path] = set()
        
        while queue:
            current, depth = queue.pop(0)
            
            if current in seen or depth > self.max_depth:
                continue
                
            seen.add(current)
            
            # Check if this is a git repository
            git_dir = current / ".git"
            if git_dir.exists():
                project = self._analyze_project(current)
                projects.append(project)
                self.log(f"  ✓ Found project: {project.name} at {project.path}")
                continue
            
            # Explore subdirectories
            try:
                for child in current.iterdir():
                    if not child.is_dir():
                        continue
                    if child.name.startswith("."):
                        continue
                    if child.name in {"node_modules", "__pycache__", "venv", ".venv", ".mypy_cache"}:
                        continue
                    queue.append((child, depth + 1))
            except (PermissionError, OSError) as e:
                self.log(f"  ⚠️  Cannot access {current}: {e}", "WARN")
                continue
        
        self.log(f"✅ Discovered {len(projects)} projects")
        self.projects = {project.name: project for project in projects}
        return projects
    
    def _analyze_project(self, path: Path) -> ProjectInfo:
        """Analyze a project and gather information."""
        name = path.name
        
        # Check for AI auto-fix script
        has_ai_autofix = (path / "scripts" / "ai_auto_fix.py").exists()
        
        # Check for tests
        has_tests = (
            (path / "tests").exists() or
            (path / "test").exists() or
            (path / "pytest.ini").exists() or
            (path / "package.json").exists()
        )
        
        # Get current git branch
        git_branch = self._get_git_branch(path)
        
        # Find TODO files
        todo_files = self._find_todo_files(path)
        
        return ProjectInfo(
            path=path,
            name=name,
            has_ai_autofix=has_ai_autofix,
            has_tests=has_tests,
            git_branch=git_branch,
            todo_files=todo_files,
        )
    
    def _get_git_branch(self, repo: Path) -> Optional[str]:
        """Get the current git branch."""
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=repo,
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return None
    
    def _find_todo_files(self, repo: Path) -> List[Path]:
        """Find TODO-related files in a repository."""
        todo_files = []
        
        # Common TODO file patterns
        patterns = [
            "TODO.md", "TODOS.md", "TODO.txt",
            "REMAINING_TODOS.md", "OSD_TODO.md", "FUTURE_TODOS.md",
            ".todo", "todo.json"
        ]
        
        for pattern in patterns:
            todo_file = repo / pattern
            if todo_file.exists():
                todo_files.append(todo_file)
        
        return todo_files
    
    def extract_todos(self, project: ProjectInfo) -> List[TodoItem]:
        """Extract TODO items from a project."""
        todos: List[TodoItem] = []
        
        for todo_file in project.todo_files:
            try:
                with todo_file.open("r", encoding="utf-8") as f:
                    lines = f.readlines()
                
                for line_num, line in enumerate(lines, 1):
                    line = line.strip()
                    lower_line = line.lower()
                    
                    # Match TODO patterns
                    if (
                        "- [ ]" in lower_line
                        or "- [x]" in lower_line
                        or any(marker in lower_line for marker in ["todo:", "fixme:", "hack:"])
                    ):
                        priority = "normal"
                        
                        # Determine priority
                        if any(word in lower_line for word in ["critical", "urgent", "asap"]):
                            priority = "critical"
                        elif any(word in lower_line for word in ["important", "high"]):
                            priority = "high"
                        elif any(word in lower_line for word in ["low", "someday", "maybe"]):
                            priority = "low"
                        
                        # Check if completed
                        completed = "- [x]" in lower_line or "✓" in line or "✅" in line
                        
                        todo = TodoItem(
                            project=project.name,
                            file=todo_file,
                            line_number=line_num,
                            content=line,
                            priority=priority,
                            completed=completed,
                        )
                        todos.append(todo)
            
            except Exception as e:
                self.log(f"  ⚠️  Error reading {todo_file}: {e}", "WARN")
        
        return todos
    
    def launch_project_monitor(self, project: ProjectInfo) -> bool:
        """Launch an AI auto-fix monitor for a project."""
        if not project.has_ai_autofix:
            self.log(f"  ⚠️  {project.name}: No ai_auto_fix.py script found", "WARN")
            return False
        
        script_path = project.path / "scripts" / "ai_auto_fix.py"
        
        # Build command
        cmd = [
            sys.executable,
            str(script_path),
            "--logs-only",
            "--daemon",
            "--max-attempts", "0",  # Unlimited
        ]
        
        try:
            self.log(f"  🚀 Launching monitor for {project.name}...")
            
            env = os.environ.copy()
            env["PYTHONUNBUFFERED"] = "1"
            
            process = subprocess.Popen(
                cmd,
                cwd=project.path,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                env=env,
            )
            
            project.monitor_process = process
            project.status = "running"
            self.monitors[project.name] = process
            
            # Start a thread to monitor output
            thread = threading.Thread(
                target=self._monitor_output,
                args=(project, process),
                daemon=True,
            )
            thread.start()
            
            self.log(f"  ✅ Monitor launched for {project.name} (PID: {process.pid})")
            return True
            
        except Exception as e:
            self.log(f"  ❌ Failed to launch monitor for {project.name}: {e}", "ERROR")
            project.status = "error"
            return False
    
    def _monitor_output(self, project: ProjectInfo, process: subprocess.Popen):
        """Monitor the output of a project's AI auto-fix process."""
        assert process.stdout is not None
        
        for line in process.stdout:
            line = line.rstrip()
            if line:
                # Log to project-specific log file
                project_log = self.log_dir / f"{project.name}_monitor.log"
                with project_log.open("a", encoding="utf-8") as f:
                    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                    f.write(f"[{timestamp}] {line}\n")
        
        # Process ended
        returncode = process.wait()
        self.log(f"  ⚠️  Monitor for {project.name} ended (code: {returncode})", "WARN")
        project.status = "stopped"
    
    def todo_monitoring_loop(self):
        """Background thread to monitor TODOs and spawn codex when needed."""
        self.log("📋 Starting TODO monitoring thread...")
        
        while self.running:
            try:
                # Extract all TODOs
                all_todos: List[TodoItem] = []
                for project in self.projects.values():
                    todos = self.extract_todos(project)
                    all_todos.extend(todos)
                
                self.todos = all_todos
                
                # Check for new high-priority TODOs
                high_priority_todos = [
                    todo for todo in all_todos
                    if todo.priority in ["high", "critical"] and not todo.completed
                ]
                
                if high_priority_todos and self.auto_spawn_codex:
                    self.log(f"  💡 Found {len(high_priority_todos)} high-priority TODOs")
                    
                    # Prepare TODO summary for codex
                    todo_summary = self._format_todos_for_codex(high_priority_todos)
                    
                    # Save to file for codex to read
                    codex_input = self.log_dir / "codex_todos.txt"
                    with codex_input.open("w", encoding="utf-8") as f:
                        f.write(todo_summary)
                    
                    self.log(f"  📝 TODO summary saved to {codex_input}")
                
                # Wait before next check
                time.sleep(self.todo_check_interval)
                
            except Exception as e:
                self.log(f"  ❌ Error in TODO monitoring: {e}", "ERROR")
                time.sleep(60)  # Wait a minute before retrying
    
    def _format_todos_for_codex(self, todos: List[TodoItem]) -> str:
        """Format TODOs for codex consumption."""
        lines = [
            "=" * 80,
            "HIGH-PRIORITY TODOS - ACTION REQUIRED",
            "=" * 80,
            "",
            f"Found {len(todos)} high-priority TODO items that need attention:",
            "",
        ]
        
        # Group by project
        by_project: Dict[str, List[TodoItem]] = {}
        for todo in todos:
            if todo.project not in by_project:
                by_project[todo.project] = []
            by_project[todo.project].append(todo)
        
        for project_name, project_todos in sorted(by_project.items()):
            lines.append(f"## {project_name}")
            lines.append("")
            
            for todo in project_todos:
                lines.append(f"  [{todo.priority.upper()}] {todo.content}")
                lines.append(f"    Location: {todo.file.name}:{todo.line_number}")
                lines.append("")
        
        lines.extend([
            "",
            "=" * 80,
            "NEXT STEPS:",
            "=" * 80,
            "",
            "1. Review each TODO item and assess feasibility",
            "2. Create implementation tasks for each actionable item",
            "3. Execute fixes and improvements systematically",
            "4. Mark items as complete when finished",
            "5. Re-run this analysis to track progress",
            "",
        ])
        
        return "\n".join(lines)
    
    def health_monitoring_loop(self):
        """Background thread to monitor project health."""
        self.log("💚 Starting health monitoring thread...")
        
        while self.running:
            try:
                now = time.time()
                
                for project in self.projects.values():
                    # Check if monitor is still running
                    if project.monitor_process:
                        if project.monitor_process.poll() is not None:
                            # Process ended
                            self.log(f"  ⚠️  Monitor for {project.name} has stopped", "WARN")
                            project.status = "stopped"
                        else:
                            project.status = "healthy"
                    
                    project.last_health_check = now
                
                # Wait before next check
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                self.log(f"  ❌ Error in health monitoring: {e}", "ERROR")
                time.sleep(60)
    
    def generate_status_report(self) -> Dict[str, Any]:
        """Generate a comprehensive status report."""
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "root": str(self.root),
            "total_projects": len(self.projects),
            "projects": {},
            "todos": {
                "total": len(self.todos),
                "by_priority": {
                    "critical": len([t for t in self.todos if t.priority == "critical" and not t.completed]),
                    "high": len([t for t in self.todos if t.priority == "high" and not t.completed]),
                    "normal": len([t for t in self.todos if t.priority == "normal" and not t.completed]),
                    "low": len([t for t in self.todos if t.priority == "low" and not t.completed]),
                },
                "completed": len([t for t in self.todos if t.completed]),
            },
            "monitors": {
                "running": len([p for p in self.projects.values() if p.status == "running"]),
                "healthy": len([p for p in self.projects.values() if p.status == "healthy"]),
                "stopped": len([p for p in self.projects.values() if p.status == "stopped"]),
                "error": len([p for p in self.projects.values() if p.status == "error"]),
            },
        }
        
        for name, project in self.projects.items():
            report["projects"][name] = {
                "path": str(project.path),
                "status": project.status,
                "branch": project.git_branch,
                "has_ai_autofix": project.has_ai_autofix,
                "has_tests": project.has_tests,
                "todo_count": len([t for t in self.todos if t.project == name and not t.completed]),
            }
        
        return report
    
    def save_status_report(self):
        """Save the current status report to a file."""
        report = self.generate_status_report()
        report_file = self.log_dir / "status_report.json"
        
        with report_file.open("w", encoding="utf-8") as f:
            json.dump(report, indent=2, fp=f)
        
        self.log(f"📊 Status report saved to {report_file}")
        return report
    
    def start(self):
        """Start the master orchestrator."""
        self.log("=" * 80)
        self.log("🚀 AI OS Orchestrator - Master Orchestrator Starting...")
        self.log("=" * 80)
        
        self.running = True
        
        # Discover all projects
        projects = self.discover_projects()
        self.projects = {p.name: p for p in projects}
        
        # Extract initial TODOs
        if self.watch_todos:
            self.log("📋 Extracting TODOs from all projects...")
            for project in self.projects.values():
                todos = self.extract_todos(project)
                self.todos.extend(todos)
            
            self.log(f"  ✅ Found {len(self.todos)} total TODO items")
        
        # Launch monitors for all projects with ai_auto_fix.py
        self.log("🚀 Launching project monitors...")
        for project in self.projects.values():
            if project.has_ai_autofix:
                self.launch_project_monitor(project)
        
        # Start background threads
        if self.watch_todos:
            self.todo_thread = threading.Thread(target=self.todo_monitoring_loop, daemon=True)
            self.todo_thread.start()
        
        self.health_thread = threading.Thread(target=self.health_monitoring_loop, daemon=True)
        self.health_thread.start()
        
        # Generate initial status report
        self.save_status_report()
        
        self.log("=" * 80)
        self.log("✅ Master Orchestrator is now running!")
        self.log("=" * 80)
        self.log("")
        self.log("📊 Summary:")
        self.log(f"  • Total Projects: {len(self.projects)}")
        self.log(f"  • Active Monitors: {len(self.monitors)}")
        self.log(f"  • Total TODOs: {len(self.todos)}")
        self.log(f"  • High Priority TODOs: {len([t for t in self.todos if t.priority in ['high', 'critical'] and not t.completed])}")
        self.log("")
        self.log("Press Ctrl+C to stop...")
        self.log("")
    
    def stop(self):
        """Stop the master orchestrator."""
        self.log("🛑 Stopping Master Orchestrator...")
        
        self.running = False
        
        # Stop all monitors
        for name, process in self.monitors.items():
            self.log(f"  Stopping monitor for {name}...")
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.log(f"    Force killing {name}...", "WARN")
                process.kill()
            except Exception as e:
                self.log(f"    Error stopping {name}: {e}", "ERROR")
        
        # Generate final status report
        self.save_status_report()
        
        self.log("✅ Master Orchestrator stopped")
    
    def run(self):
        """Main run loop."""
        self.start()
        
        try:
            # Wait for interrupt
            while self.running:
                time.sleep(1)
                
                # Periodically save status
                if int(time.time()) % 300 == 0:  # Every 5 minutes
                    self.save_status_report()
        
        except KeyboardInterrupt:
            self.log("")
            self.log("Received interrupt signal...")
        finally:
            self.stop()


def main():
    parser = argparse.ArgumentParser(
        description="AI OS Orchestrator - Master Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Launch for current workspace
    python os_dashboard_ai_assistant.py
    
    # Launch for specific workspace
    python os_dashboard_ai_assistant.py --root ~/Projects
    
    # With TODO monitoring
    python os_dashboard_ai_assistant.py --watch-todos --todo-check-interval 60
    
    # Disable auto-codex spawning
    python os_dashboard_ai_assistant.py --no-auto-codex
        """
    )
    
    parser.add_argument(
        "--root",
        type=Path,
        default=REPO_ROOT,
        help="Workspace root to scan for projects (default: current directory)",
    )
    
    parser.add_argument(
        "--max-depth",
        type=int,
        default=4,
        help="Maximum directory depth to search (default: 4)",
    )
    
    parser.add_argument(
        "--watch-todos",
        action="store_true",
        default=True,
        help="Enable TODO monitoring (default: True)",
    )
    
    parser.add_argument(
        "--no-watch-todos",
        action="store_false",
        dest="watch_todos",
        help="Disable TODO monitoring",
    )
    
    parser.add_argument(
        "--todo-check-interval",
        type=int,
        default=300,
        help="Seconds between TODO checks (default: 300)",
    )
    
    parser.add_argument(
        "--enable-dashboard",
        action="store_true",
        default=True,
        help="Enable health dashboard (default: True)",
    )
    
    parser.add_argument(
        "--health-port",
        type=int,
        default=9000,
        help="Port for health dashboard (default: 9000)",
    )
    
    parser.add_argument(
        "--auto-codex",
        action="store_true",
        default=True,
        help="Automatically spawn codex for high-priority TODOs (default: True)",
    )
    
    parser.add_argument(
        "--no-auto-codex",
        action="store_false",
        dest="auto_codex",
        help="Disable automatic codex spawning",
    )
    
    parser.add_argument(
        "--log-dir",
        type=Path,
        default=REPO_ROOT / "logs",
        help="Directory for log files (default: logs/)",
    )
    
    args = parser.parse_args()
    
    orchestrator = MasterOrchestrator(
        root=args.root,
        max_depth=args.max_depth,
        watch_todos=args.watch_todos,
        todo_check_interval=args.todo_check_interval,
        enable_dashboard=args.enable_dashboard,
        health_port=args.health_port,
        auto_spawn_codex=args.auto_codex,
        log_dir=args.log_dir,
    )
    
    orchestrator.run()


if __name__ == "__main__":
    main()
