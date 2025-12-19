#!/usr/bin/env python3
"""
Unified Terminal Shell - Interactive Interface for All Projects

Provides a seamless, intuitive terminal interface that:
- Discovers all Git projects automatically
- Provides unified commands for all projects
- Integrates with auto-fix scripts
- Offers real-time project health monitoring
- Enables cross-project operations

Usage:
    python scripts/unified_terminal_shell.py

Commands:
    list          - List all discovered projects
    status        - Show health status for all projects
    monitor <name> - Start auto-fix monitor for a project
    stop <name>   - Stop auto-fix monitor for a project
    test <name>   - Run tests for a project
    fix <name>    - Trigger manual auto-fix for a project
    report        - Generate comprehensive report
    help          - Show this help message
    exit/quit     - Exit the shell
"""

from __future__ import annotations

import argparse
import cmd
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.unified_project_orchestrator import (
    UnifiedProjectOrchestrator,
    discover_git_repos,
    create_project_status,
)


class UnifiedTerminalShell(cmd.Cmd):
    """Interactive shell for managing all projects."""
    
    intro = """
╔═══════════════════════════════════════════════════════════════╗
║     OS Dashboard AI Assistant - Unified Terminal Shell        ║
║     Seamless Interface for All Git Projects                   ║
╚═══════════════════════════════════════════════════════════════╝

Type 'help' for available commands.
Type 'exit' or 'quit' to exit.
"""
    prompt = "osdash> "
    
    def __init__(self, root: Path = REPO_ROOT, max_depth: int = 5):
        super().__init__()
        self.root = root
        self.max_depth = max_depth
        self.orchestrator = UnifiedProjectOrchestrator(root=root, max_depth=max_depth)
        self.orchestrator.discover_projects()
        self._refresh_projects()
    
    def _refresh_projects(self):
        """Refresh the project list."""
        self.orchestrator.discover_projects()
        self.projects = self.orchestrator.discovered_projects
    
    def do_list(self, arg: str):
        """List all discovered projects."""
        self._refresh_projects()
        if not self.projects:
            print("No projects discovered.")
            return
        
        print(f"\n📦 Found {len(self.projects)} projects:\n")
        for name, project in sorted(self.projects.items()):
            status_icon = "✅" if project.has_autofix else "⚠️"
            health_icon = {
                "healthy": "🟢",
                "degraded": "🟡",
                "unhealthy": "🔴",
                "unknown": "⚪",
            }.get(project.health, "⚪")
            
            print(f"  {status_icon} {health_icon} {name}")
            print(f"     Path: {project.path}")
            print(f"     Language: {project.metadata.get('language', 'unknown')}")
            print(f"     Health: {project.health}")
            if project.has_autofix:
                print(f"     Auto-Fix: Available")
            if project.metadata.get("has_tests"):
                print(f"     Tests: Available")
            print()
    
    def do_status(self, arg: str):
        """Show health status for all projects."""
        self._refresh_projects()
        report = self.orchestrator.generate_report()
        
        print("\n📊 Project Health Status:\n")
        print(f"Total Projects: {report['total_projects']}")
        print(f"Healthy: {report['summary'].get('healthy', 0)}")
        print(f"Degraded: {report['summary'].get('degraded', 0)}")
        print(f"Unhealthy: {report['summary'].get('unhealthy', 0)}")
        print(f"Unknown: {report['summary'].get('unknown', 0)}")
        print(f"With Auto-Fix: {report['summary'].get('with_autofix', 0)}")
        print(f"With Tests: {report['summary'].get('with_tests', 0)}")
        print()
    
    def do_monitor(self, arg: str):
        """Start auto-fix monitor for a project: monitor <project_name>"""
        if not arg:
            print("❌ Usage: monitor <project_name>")
            return
        
        project_name = arg.strip()
        if project_name not in self.projects:
            print(f"❌ Project '{project_name}' not found.")
            print("   Use 'list' to see available projects.")
            return
        
        project = self.projects[project_name]
        if not project.has_autofix:
            print(f"❌ Project '{project_name}' does not have auto-fix capability.")
            return
        
        try:
            self.orchestrator.auto_fix = True
            self.orchestrator.start_monitors()
            print(f"✅ Started auto-fix monitor for {project_name}")
        except Exception as e:
            print(f"❌ Failed to start monitor: {e}")
    
    def do_stop(self, arg: str):
        """Stop auto-fix monitor for a project: stop <project_name>"""
        if not arg:
            print("❌ Usage: stop <project_name>")
            return
        
        project_name = arg.strip()
        try:
            self.orchestrator.stop_monitors()
            print(f"✅ Stopped monitors for {project_name}")
        except Exception as e:
            print(f"❌ Failed to stop monitor: {e}")
    
    def do_test(self, arg: str):
        """Run tests for a project: test <project_name>"""
        if not arg:
            print("❌ Usage: test <project_name>")
            return
        
        project_name = arg.strip()
        if project_name not in self.projects:
            print(f"❌ Project '{project_name}' not found.")
            return
        
        project = self.projects[project_name]
        
        # Detect test command
        test_cmd = None
        if project.metadata.get("has_pytest"):
            test_cmd = [sys.executable, "-m", "pytest", "-q"]
        elif project.metadata.get("has_npm_tests"):
            test_cmd = ["npm", "test", "--", "--runInBand"]
        else:
            print(f"❌ No test infrastructure detected for {project_name}")
            return
        
        print(f"🧪 Running tests for {project_name}...")
        try:
            result = subprocess.run(
                test_cmd,
                cwd=project.path,
                capture_output=True,
                text=True,
            )
            print(result.stdout)
            if result.stderr:
                print(result.stderr, file=sys.stderr)
            if result.returncode == 0:
                print(f"✅ Tests passed for {project_name}")
            else:
                print(f"❌ Tests failed for {project_name}")
        except Exception as e:
            print(f"❌ Error running tests: {e}")
    
    def do_fix(self, arg: str):
        """Trigger manual auto-fix for a project: fix <project_name>"""
        if not arg:
            print("❌ Usage: fix <project_name>")
            return
        
        project_name = arg.strip()
        if project_name not in self.projects:
            print(f"❌ Project '{project_name}' not found.")
            return
        
        project = self.projects[project_name]
        if not project.has_autofix:
            print(f"❌ Project '{project_name}' does not have auto-fix capability.")
            return
        
        autofix_script = project.autofix_script
        if not autofix_script or not autofix_script.exists():
            print(f"❌ Auto-fix script not found for {project_name}")
            return
        
        print(f"🔧 Running auto-fix for {project_name}...")
        try:
            result = subprocess.run(
                [sys.executable, str(autofix_script), "--logs-only", "--no-daemon"],
                cwd=project.path,
                text=True,
            )
            if result.returncode == 0:
                print(f"✅ Auto-fix completed for {project_name}")
            else:
                print(f"⚠️  Auto-fix exited with code {result.returncode}")
        except Exception as e:
            print(f"❌ Error running auto-fix: {e}")
    
    def do_report(self, arg: str):
        """Generate comprehensive report."""
        self._refresh_projects()
        report = self.orchestrator.generate_report()
        
        output_file = None
        if arg:
            output_file = Path(arg.strip())
        
        report_json = json.dumps(report, indent=2)
        
        if output_file:
            output_file.write_text(report_json, encoding="utf-8")
            print(f"📄 Report saved to {output_file}")
        else:
            print("\n📊 Comprehensive Project Report:\n")
            print(report_json)
            print()
    
    def do_refresh(self, arg: str):
        """Refresh project discovery."""
        print("🔄 Refreshing project list...")
        self._refresh_projects()
        print(f"✅ Found {len(self.projects)} projects")
    
    def do_help(self, arg: str):
        """Show help message."""
        if arg:
            # Try to get help for a specific command
            try:
                func = getattr(self, f'do_{arg}')
                doc = func.__doc__
                if doc:
                    print(doc)
                else:
                    print(f"No help available for '{arg}'")
            except AttributeError:
                print(f"Unknown command: {arg}")
        else:
            print("""
Available Commands:
  list              - List all discovered projects
  status            - Show health status for all projects
  monitor <name>    - Start auto-fix monitor for a project
  stop <name>       - Stop auto-fix monitor for a project
  test <name>       - Run tests for a project
  fix <name>        - Trigger manual auto-fix for a project
  report [file]     - Generate comprehensive report (optionally save to file)
  refresh           - Refresh project discovery
  help [command]    - Show help for a command
  exit/quit         - Exit the shell
""")
    
    def do_exit(self, arg: str):
        """Exit the shell."""
        print("\n👋 Goodbye!")
        return True
    
    def do_quit(self, arg: str):
        """Exit the shell."""
        return self.do_exit(arg)
    
    def default(self, line: str):
        """Handle unknown commands."""
        print(f"❌ Unknown command: {line}")
        print("   Type 'help' for available commands.")


def main():
    parser = argparse.ArgumentParser(
        description="Unified Terminal Shell for OS Dashboard AI Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=REPO_ROOT,
        help="Workspace root to scan",
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=5,
        help="Maximum directory depth",
    )
    
    args = parser.parse_args()
    
    shell = UnifiedTerminalShell(root=args.root, max_depth=args.max_depth)
    
    try:
        shell.cmdloop()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        return 0
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
