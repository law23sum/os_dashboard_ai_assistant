#!/usr/bin/env python3
"""
Interactive Shell - Universal terminal interface for all projects

This provides a unified shell that can interact with all discovered projects,
run commands, view logs, manage TODOs, and spawn AI assistants.

Usage:
    python scripts/interactive_shell.py
"""

from __future__ import annotations

import cmd
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Dict, Any

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


class ProjectShell(cmd.Cmd):
    """Interactive shell for managing multiple projects."""
    
    intro = """
═══════════════════════════════════════════════════════════════════════════════
    🚀 AI OS - Interactive Shell
═══════════════════════════════════════════════════════════════════════════════

Welcome to the unified project management shell!

Available commands:
    • list          - List all discovered projects
    • use <project> - Switch to a specific project
    • status        - Show orchestrator status
    • todos         - Show pending TODOs
    • spawn         - Spawn codex for TODOs
    • run <cmd>     - Run command in current project
    • logs          - View project logs
    • health        - Check project health
    • help          - Show detailed help
    • exit/quit     - Exit the shell

Type 'help <command>' for detailed information about a command.
═══════════════════════════════════════════════════════════════════════════════
    """
    
    prompt = "(all-projects) $ "
    
    def __init__(self):
        super().__init__()
        self.current_project: Optional[str] = None
        self.current_project_path: Optional[Path] = None
        self.projects: Dict[str, Dict[str, Any]] = {}
        self.status_file = REPO_ROOT / "logs" / "status_report.json"
        self._load_projects()
    
    def _load_projects(self):
        """Load project information from status report."""
        if not self.status_file.exists():
            print("⚠️  Status report not found. Run os_dashboard_ai_assistant.py first.")
            print(f"   Expected location: {self.status_file}")
            return
        
        try:
            with self.status_file.open("r", encoding="utf-8") as f:
                status = json.load(f)
            self.projects = status.get("projects", {})
            print(f"✅ Loaded {len(self.projects)} projects")
        except Exception as e:
            print(f"❌ Error loading projects: {e}")
    
    def _refresh_projects(self):
        """Reload project information."""
        self._load_projects()
    
    def do_list(self, arg):
        """List all discovered projects.
        
        Usage: list [--filter <status>]
        
        Examples:
            list                    # List all projects
            list --filter running   # List only running projects
        """
        if not self.projects:
            print("No projects loaded. Run os_dashboard_ai_assistant.py first.")
            return
        
        # Parse filter argument
        filter_status = None
        if arg:
            parts = arg.split()
            if len(parts) >= 2 and parts[0] == "--filter":
                filter_status = parts[1]
        
        print("\n" + "─" * 80)
        print(f"{'Project':<30} {'Status':<15} {'TODOs':<10} {'Path'}")
        print("─" * 80)
        
        for name, info in sorted(self.projects.items()):
            status = info.get("status", "unknown")
            
            if filter_status and status != filter_status:
                continue
            
            todo_count = info.get("todo_count", 0)
            path = info.get("path", "")
            
            # Color-code status
            status_color = {
                "running": "\033[94m",  # Blue
                "healthy": "\033[92m",  # Green
                "stopped": "\033[90m",  # Gray
                "error": "\033[91m",    # Red
            }.get(status, "")
            reset = "\033[0m"
            
            print(f"{name:<30} {status_color}{status:<15}{reset} {todo_count:<10} {path}")
        
        print("─" * 80)
        print(f"Total: {len([p for p in self.projects.values() if not filter_status or p.get('status') == filter_status])} projects")
        print()
    
    def do_use(self, project_name):
        """Switch to a specific project.
        
        Usage: use <project_name>
        
        Example: use my-awesome-project
        """
        if not project_name:
            print("Usage: use <project_name>")
            print("Available projects:")
            for name in sorted(self.projects.keys()):
                print(f"  • {name}")
            return
        
        if project_name not in self.projects:
            print(f"❌ Project '{project_name}' not found")
            print("Available projects:")
            for name in sorted(self.projects.keys()):
                print(f"  • {name}")
            return
        
        project_info = self.projects[project_name]
        self.current_project = project_name
        self.current_project_path = Path(project_info["path"])
        self.prompt = f"({project_name}) $ "
        
        print(f"✅ Switched to project: {project_name}")
        print(f"   Path: {self.current_project_path}")
        print(f"   Status: {project_info.get('status', 'unknown')}")
        print(f"   Branch: {project_info.get('branch', 'N/A')}")
    
    def do_status(self, arg):
        """Show master orchestrator status.
        
        Usage: status
        """
        if not self.status_file.exists():
            print("❌ Status report not found")
            return
        
        try:
            with self.status_file.open("r", encoding="utf-8") as f:
                status = json.load(f)
            
            print("\n" + "═" * 80)
            print("MASTER ORCHESTRATOR STATUS")
            print("═" * 80)
            print(f"Timestamp: {status.get('timestamp', 'N/A')}")
            print(f"Workspace: {status.get('root', 'N/A')}")
            print(f"Total Projects: {status.get('total_projects', 0)}")
            print()
            
            monitors = status.get("monitors", {})
            print("MONITORS:")
            print(f"  Running: {monitors.get('running', 0)}")
            print(f"  Healthy: {monitors.get('healthy', 0)}")
            print(f"  Stopped: {monitors.get('stopped', 0)}")
            print(f"  Errors: {monitors.get('error', 0)}")
            print()
            
            todos = status.get("todos", {})
            print("TODOS:")
            print(f"  Total: {todos.get('total', 0)}")
            print(f"  Completed: {todos.get('completed', 0)}")
            by_priority = todos.get("by_priority", {})
            print(f"  Critical: {by_priority.get('critical', 0)}")
            print(f"  High: {by_priority.get('high', 0)}")
            print(f"  Normal: {by_priority.get('normal', 0)}")
            print(f"  Low: {by_priority.get('low', 0)}")
            print("═" * 80)
            print()
        except Exception as e:
            print(f"❌ Error reading status: {e}")
    
    def do_todos(self, arg):
        """Show pending TODOs.
        
        Usage: todos [project_name]
        
        Examples:
            todos                   # Show all TODOs
            todos my-project        # Show TODOs for specific project
        """
        if not self.status_file.exists():
            print("❌ Status report not found")
            return
        
        project_filter = arg.strip() if arg else None
        
        print("\n" + "═" * 80)
        print("PENDING TODOS")
        print("═" * 80)
        
        for name, info in sorted(self.projects.items()):
            if project_filter and name != project_filter:
                continue
            
            todo_count = info.get("todo_count", 0)
            if todo_count == 0:
                continue
            
            print(f"\n📋 {name} ({todo_count} TODOs)")
            print(f"   Path: {info.get('path', '')}")
            print()
        
        print("═" * 80)
        print()
        print("💡 Tip: Use 'spawn' to create AI assistant sessions for these TODOs")
        print()
    
    def do_spawn(self, arg):
        """Spawn codex sessions for pending TODOs.
        
        Usage: spawn [--priority <level>] [--project <name>] [--max <count>]
        
        Examples:
            spawn                           # Spawn for all high-priority TODOs
            spawn --priority critical       # Spawn for critical TODOs only
            spawn --project my-project      # Spawn for specific project
            spawn --max 1                   # Spawn only 1 session
        """
        cmd = [sys.executable, str(REPO_ROOT / "scripts" / "codex_spawner.py")]
        
        # Parse arguments
        if arg:
            cmd.extend(arg.split())
        
        print("🚀 Spawning codex sessions...")
        print()
        
        try:
            result = subprocess.run(
                cmd,
                cwd=REPO_ROOT,
                capture_output=False,
                text=True,
            )
            
            if result.returncode != 0:
                print(f"\n❌ Codex spawner exited with code {result.returncode}")
        except Exception as e:
            print(f"❌ Error spawning codex: {e}")
    
    def do_run(self, command):
        """Run a command in the current project.
        
        Usage: run <command>
        
        Examples:
            run git status
            run npm test
            run python main.py
        """
        if not self.current_project:
            print("❌ No project selected. Use 'use <project>' first.")
            return
        
        if not command:
            print("Usage: run <command>")
            return
        
        print(f"Running in {self.current_project}: {command}")
        print()
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.current_project_path,
                text=True,
            )
            
            if result.returncode != 0:
                print(f"\n❌ Command exited with code {result.returncode}")
        except Exception as e:
            print(f"❌ Error running command: {e}")
    
    def do_logs(self, arg):
        """View project logs.
        
        Usage: logs [project_name] [--lines <count>]
        
        Examples:
            logs                    # View logs for current project
            logs my-project         # View logs for specific project
            logs --lines 50         # View last 50 lines
        """
        project = self.current_project
        lines = 100
        
        # Parse arguments
        if arg:
            parts = arg.split()
            if parts:
                if not parts[0].startswith("--"):
                    project = parts[0]
                    parts = parts[1:]
                
                for i, part in enumerate(parts):
                    if part == "--lines" and i + 1 < len(parts):
                        try:
                            lines = int(parts[i + 1])
                        except ValueError:
                            pass
        
        if not project:
            print("❌ No project specified. Use 'logs <project>' or 'use <project>' first.")
            return
        
        log_file = REPO_ROOT / "logs" / f"{project}_monitor.log"
        
        if not log_file.exists():
            print(f"❌ Log file not found: {log_file}")
            return
        
        try:
            with log_file.open("r", encoding="utf-8") as f:
                all_lines = f.readlines()
            
            recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
            
            print(f"\n{'─' * 80}")
            print(f"LOGS: {project} (last {len(recent_lines)} lines)")
            print("─" * 80)
            
            for line in recent_lines:
                print(line.rstrip())
            
            print("─" * 80)
            print()
        except Exception as e:
            print(f"❌ Error reading logs: {e}")
    
    def do_health(self, arg):
        """Check project health.
        
        Usage: health [project_name]
        
        Examples:
            health                  # Check current project
            health my-project       # Check specific project
        """
        project = arg.strip() if arg else self.current_project
        
        if not project:
            print("❌ No project specified")
            return
        
        if project not in self.projects:
            print(f"❌ Project '{project}' not found")
            return
        
        info = self.projects[project]
        
        print(f"\n{'─' * 80}")
        print(f"HEALTH CHECK: {project}")
        print("─" * 80)
        print(f"Status: {info.get('status', 'unknown')}")
        print(f"Path: {info.get('path', '')}")
        print(f"Branch: {info.get('branch', 'N/A')}")
        print(f"Has AI Auto-fix: {'✅' if info.get('has_ai_autofix') else '❌'}")
        print(f"Has Tests: {'✅' if info.get('has_tests') else '❌'}")
        print(f"Pending TODOs: {info.get('todo_count', 0)}")
        print("─" * 80)
        print()
    
    def do_refresh(self, arg):
        """Refresh project information.
        
        Usage: refresh
        """
        print("🔄 Refreshing project information...")
        self._refresh_projects()
    
    def do_exit(self, arg):
        """Exit the shell."""
        print("\n👋 Goodbye!")
        return True
    
    def do_quit(self, arg):
        """Exit the shell."""
        return self.do_exit(arg)
    
    def do_EOF(self, arg):
        """Exit on Ctrl+D."""
        print()
        return self.do_exit(arg)
    
    def emptyline(self):
        """Do nothing on empty line."""
        pass


def main():
    """Main entry point."""
    try:
        shell = ProjectShell()
        shell.cmdloop()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        return 0
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
