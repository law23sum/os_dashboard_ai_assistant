#!/usr/bin/env python3
"""AI OS Unified Launcher - Master entry point for all system modes.

This launcher provides a unified interface for starting and managing
the AI OS in various modes:

1. **Development Mode**: Backend + Frontend dev servers with hot reload
2. **Desktop Mode**: Electron desktop application
3. **Web Mode**: Production web server
4. **Guardian Mode**: Auto-fix monitoring across all projects
5. **Orchestrator Mode**: Run unified project orchestrator
6. **Daemon Mode**: Background continuation daemon

Per Technical Spec V6:
- Section 0.3: Deployment Modes Overview
- Section 1.7: AI OS - Driver-Aware Orchestrator
- Section 7.10: Operator & SRE Workspace

Examples:
    # Interactive mode selector
    python scripts/osdash_launcher.py

    # Direct mode launch
    python scripts/osdash_launcher.py --mode dev
    python scripts/osdash_launcher.py --mode desktop
    python scripts/osdash_launcher.py --mode guardian
    python scripts/osdash_launcher.py --mode orchestrator --execute

    # Pre-flight checks before launch
    python scripts/osdash_launcher.py --preflight

    # Health dashboard in terminal
    python scripts/osdash_launcher.py --status
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import signal
import subprocess
import sys
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence

REPO_ROOT = Path(__file__).resolve().parent.parent
PYTHON = sys.executable

# ANSI colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def colorize(text: str, color: str) -> str:
    """Colorize text for terminal output."""
    return f"{color}{text}{Colors.ENDC}"


@dataclass
class LaunchMode:
    """Definition of a launch mode."""
    name: str
    description: str
    command: Callable[["OSDashLauncher"], int]
    requires_deps: List[str]


class OSDashLauncher:
    """Unified launcher for AI OS."""
    
    BANNER = """
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║   ██████  ███████     ██████   █████  ███████ ██   ██             ║
║  ██    ██ ██          ██   ██ ██   ██ ██      ██   ██             ║
║  ██    ██ ███████     ██   ██ ███████ ███████ ███████             ║
║  ██    ██      ██     ██   ██ ██   ██      ██ ██   ██             ║
║   ██████  ███████     ██████  ██   ██ ███████ ██   ██             ║
║                                                                   ║
║              AI Assistant - Technical Spec V6                     ║
║          "Governed AI OS for Knowledge & Execution Work"          ║
╚═══════════════════════════════════════════════════════════════════╝
"""
    
    def __init__(
        self,
        workspace: Path = REPO_ROOT,
        verbose: bool = True,
    ):
        self.workspace = workspace
        self.verbose = verbose
        self._processes: List[subprocess.Popen] = []
        self._stop_event = threading.Event()
        
        # Register signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        self._log(f"\n{colorize('Received shutdown signal...', Colors.YELLOW)}")
        self._stop_event.set()
        self._cleanup()
    
    def _cleanup(self):
        """Clean up all spawned processes."""
        for proc in self._processes:
            if proc.poll() is None:
                try:
                    proc.terminate()
                    proc.wait(timeout=5)
                except:
                    proc.kill()
        self._processes.clear()
    
    def _log(self, message: str) -> None:
        """Print a log message if verbose."""
        if self.verbose:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] {message}")
    
    def _run_command(
        self,
        cmd: Sequence[str],
        cwd: Optional[Path] = None,
        env: Optional[Dict[str, str]] = None,
        background: bool = False,
    ) -> Optional[subprocess.Popen]:
        """Run a command, optionally in the background."""
        cwd = cwd or self.workspace
        run_env = os.environ.copy()
        if env:
            run_env.update(env)
        
        self._log(f"{colorize('Running:', Colors.CYAN)} {' '.join(str(c) for c in cmd)}")
        
        if background:
            proc = subprocess.Popen(
                [str(c) for c in cmd],
                cwd=cwd,
                env=run_env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            self._processes.append(proc)
            return proc
        else:
            result = subprocess.run(
                [str(c) for c in cmd],
                cwd=cwd,
                env=run_env,
            )
            return None
    
    def check_dependencies(self) -> Dict[str, Any]:
        """Check all required dependencies and return status."""
        checks = {
            "python": {"path": shutil.which("python3") or shutil.which("python"), "required": True},
            "node": {"path": shutil.which("node"), "required": True},
            "npm": {"path": shutil.which("npm"), "required": True},
            "git": {"path": shutil.which("git"), "required": True},
            "openai_key": {"value": bool(os.environ.get("OPENAI_API_KEY")), "required": False},
        }
        
        # Check Python packages
        try:
            import fastapi
            checks["fastapi"] = {"installed": True, "required": True}
        except ImportError:
            checks["fastapi"] = {"installed": False, "required": True}
        
        try:
            import uvicorn
            checks["uvicorn"] = {"installed": True, "required": True}
        except ImportError:
            checks["uvicorn"] = {"installed": False, "required": True}
        
        # Check frontend
        package_json = self.workspace / "frontend" / "package.json"
        node_modules = self.workspace / "frontend" / "node_modules"
        checks["frontend_deps"] = {
            "installed": node_modules.exists() and package_json.exists(),
            "required": True,
        }
        
        return checks
    
    def print_status(self) -> None:
        """Print system status overview."""
        print(self.BANNER)
        
        # Check dependencies
        deps = self.check_dependencies()
        print(colorize("\n📋 Dependency Status:", Colors.BOLD))
        for name, info in deps.items():
            if "path" in info:
                status = colorize("✓", Colors.GREEN) if info["path"] else colorize("✗", Colors.RED)
                print(f"  {status} {name}: {info.get('path', 'not found')}")
            elif "installed" in info:
                status = colorize("✓", Colors.GREEN) if info["installed"] else colorize("✗", Colors.RED)
                print(f"  {status} {name}")
            elif "value" in info:
                status = colorize("✓", Colors.GREEN) if info["value"] else colorize("○", Colors.YELLOW)
                print(f"  {status} {name}")
        
        # Check workspace health
        print(colorize("\n📁 Workspace:", Colors.BOLD))
        print(f"  Root: {self.workspace}")
        
        # Check for key files
        key_files = [
            ("Technical Spec", "Technical Spec Sheet (Version 6 Latest Version).txt"),
            ("Backend API", "backend_api/main.py"),
            ("Frontend", "frontend/package.json"),
            ("Orchestrator", "scripts/unified_project_orchestrator.py"),
            ("Auto-fix", "scripts/ai_auto_fix.py"),
            ("Continuation Daemon", "scripts/codex_continuation_daemon.py"),
        ]
        
        for label, path in key_files:
            full_path = self.workspace / path
            status = colorize("✓", Colors.GREEN) if full_path.exists() else colorize("✗", Colors.RED)
            print(f"  {status} {label}")
        
        # Check for continuation payload
        continuation_file = self.workspace / ".osdash-continuation.json"
        if continuation_file.exists():
            try:
                data = json.loads(continuation_file.read_text())
                if data.get("continuation_required"):
                    print(colorize("\n⚠️  Continuation Required!", Colors.YELLOW))
                    print(f"  Priority TODOs: {len(data.get('priority_todos', []))}")
                    print(f"  Failed Projects: {len(data.get('failed_projects', []))}")
            except:
                pass
    
    def run_preflight(self) -> bool:
        """Run preflight checks before launch."""
        print(colorize("\n🔍 Running preflight checks...", Colors.BOLD))
        
        issues = []
        deps = self.check_dependencies()
        
        for name, info in deps.items():
            if info.get("required"):
                if "path" in info and not info["path"]:
                    issues.append(f"{name} is not installed")
                elif "installed" in info and not info["installed"]:
                    issues.append(f"{name} is not installed")
        
        if issues:
            print(colorize("\n❌ Preflight failed:", Colors.RED))
            for issue in issues:
                print(f"  • {issue}")
            return False
        
        print(colorize("\n✅ All preflight checks passed!", Colors.GREEN))
        return True
    
    def install_dependencies(self) -> int:
        """Install all required dependencies."""
        self._log(colorize("Installing Python dependencies...", Colors.CYAN))
        self._run_command([PYTHON, "-m", "pip", "install", "-r", "requirements.txt"])
        
        frontend_dir = self.workspace / "frontend"
        if frontend_dir.exists():
            self._log(colorize("Installing Node dependencies...", Colors.CYAN))
            self._run_command(["npm", "install"], cwd=frontend_dir)
        
        return 0
    
    def launch_dev(self) -> int:
        """Launch development mode with hot reload."""
        print(colorize("\n🚀 Launching Development Mode", Colors.BOLD))
        
        # Start backend
        self._log("Starting backend server...")
        backend_proc = self._run_command(
            [PYTHON, "-m", "uvicorn", "backend_api.main:app", "--reload", "--port", "8000"],
            background=True,
        )
        
        # Give backend time to start
        time.sleep(2)
        
        # Start frontend
        frontend_dir = self.workspace / "frontend"
        if frontend_dir.exists():
            self._log("Starting frontend dev server...")
            frontend_proc = self._run_command(
                ["npm", "run", "dev:web"],
                cwd=frontend_dir,
                background=True,
            )
        
        print(colorize("\n✅ Development servers running!", Colors.GREEN))
        print(f"  Backend:  http://localhost:8000")
        print(f"  Frontend: http://localhost:5173")
        print(f"  API Docs: http://localhost:8000/swagger")
        print(colorize("\nPress Ctrl+C to stop...", Colors.YELLOW))
        
        # Wait for stop signal
        while not self._stop_event.is_set():
            time.sleep(1)
            # Check if processes are still running
            for proc in self._processes:
                if proc.poll() is not None:
                    self._log(colorize("A process exited unexpectedly", Colors.RED))
        
        self._cleanup()
        return 0
    
    def launch_desktop(self) -> int:
        """Launch desktop (Electron) application."""
        print(colorize("\n🖥️  Launching Desktop Mode", Colors.BOLD))
        
        frontend_dir = self.workspace / "frontend"
        if not frontend_dir.exists():
            self._log(colorize("Frontend directory not found!", Colors.RED))
            return 1
        
        # Build if needed
        dist_dir = frontend_dir / "dist"
        if not dist_dir.exists():
            self._log("Building frontend...")
            self._run_command(["npm", "run", "build"], cwd=frontend_dir)
        
        # Start Electron
        self._log("Starting Electron...")
        self._run_command(["npm", "run", "dev:desktop"], cwd=frontend_dir)
        
        return 0
    
    def launch_guardian(self) -> int:
        """Launch Guardian mode - auto-fix monitoring across all projects."""
        print(colorize("\n🛡️  Launching Guardian Mode", Colors.BOLD))
        
        orchestrator_script = self.workspace / "scripts" / "project_autofix_orchestrator.py"
        if not orchestrator_script.exists():
            self._log(colorize("Orchestrator script not found!", Colors.RED))
            return 1
        
        self._log("Starting auto-fix orchestrator...")
        self._run_command([
            PYTHON, str(orchestrator_script),
            "--root", str(self.workspace),
            "--mode", "parallel",
        ])
        
        return 0
    
    def launch_orchestrator(self, execute: bool = False, continue_todos: bool = False) -> int:
        """Launch unified project orchestrator."""
        print(colorize("\n🎯 Launching Unified Orchestrator", Colors.BOLD))
        
        script = self.workspace / "scripts" / "unified_project_orchestrator.py"
        if not script.exists():
            self._log(colorize("Unified orchestrator script not found!", Colors.RED))
            return 1
        
        cmd = [PYTHON, str(script), "--root", str(self.workspace)]
        
        if execute:
            cmd.append("--execute")
        
        if continue_todos:
            cmd.append("--continue-todos")
        
        self._run_command(cmd)
        
        return 0
    
    def launch_daemon(self, method: str = "manual") -> int:
        """Launch continuation daemon."""
        print(colorize("\n🔄 Launching Continuation Daemon", Colors.BOLD))
        
        script = self.workspace / "scripts" / "codex_continuation_daemon.py"
        if not script.exists():
            self._log(colorize("Continuation daemon script not found!", Colors.RED))
            return 1
        
        self._run_command([
            PYTHON, str(script),
            "--watch",
            "--method", method,
            "--workspace", str(self.workspace),
        ])
        
        return 0
    
    def interactive_menu(self) -> int:
        """Show interactive mode selection menu."""
        print(self.BANNER)
        print(colorize("Select a launch mode:", Colors.BOLD))
        print()
        
        modes = [
            ("1", "dev", "Development Mode (Backend + Frontend with hot reload)"),
            ("2", "desktop", "Desktop Mode (Electron application)"),
            ("3", "guardian", "Guardian Mode (Auto-fix monitoring)"),
            ("4", "orchestrator", "Orchestrator Mode (Run unified orchestrator)"),
            ("5", "daemon", "Daemon Mode (Continuation daemon)"),
            ("6", "status", "Show System Status"),
            ("7", "install", "Install Dependencies"),
            ("0", "exit", "Exit"),
        ]
        
        for key, mode, desc in modes:
            print(f"  [{key}] {colorize(mode, Colors.CYAN):20} - {desc}")
        
        print()
        choice = input(colorize("Enter choice: ", Colors.BOLD)).strip()
        
        mode_map = {m[0]: m[1] for m in modes}
        selected_mode = mode_map.get(choice)
        
        if selected_mode == "exit" or not selected_mode:
            return 0
        
        if selected_mode == "dev":
            return self.launch_dev()
        elif selected_mode == "desktop":
            return self.launch_desktop()
        elif selected_mode == "guardian":
            return self.launch_guardian()
        elif selected_mode == "orchestrator":
            return self.launch_orchestrator(execute=True, continue_todos=True)
        elif selected_mode == "daemon":
            return self.launch_daemon()
        elif selected_mode == "status":
            self.print_status()
            return self.interactive_menu()
        elif selected_mode == "install":
            self.install_dependencies()
            return self.interactive_menu()
        
        return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="AI OS Unified Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Modes:
  dev          Start development servers (backend + frontend)
  desktop      Start Electron desktop application
  guardian     Start auto-fix monitoring across projects
  orchestrator Run unified project orchestrator
  daemon       Start continuation daemon

Examples:
  python scripts/osdash_launcher.py                    # Interactive menu
  python scripts/osdash_launcher.py --mode dev         # Development mode
  python scripts/osdash_launcher.py --mode guardian    # Guardian mode
  python scripts/osdash_launcher.py --status           # Show status
        """
    )
    
    parser.add_argument(
        "--mode",
        choices=["dev", "desktop", "guardian", "orchestrator", "daemon"],
        help="Launch mode",
    )
    parser.add_argument(
        "--workspace",
        type=Path,
        default=REPO_ROOT,
        help="Workspace root directory",
    )
    parser.add_argument(
        "--preflight",
        action="store_true",
        help="Run preflight checks only",
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show system status",
    )
    parser.add_argument(
        "--install",
        action="store_true",
        help="Install dependencies",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="For orchestrator mode: execute fixes",
    )
    parser.add_argument(
        "--continue-todos",
        action="store_true",
        help="For orchestrator mode: trigger continuation",
    )
    parser.add_argument(
        "--daemon-method",
        choices=["manual", "cursor", "vscode", "terminal", "api"],
        default="manual",
        help="For daemon mode: continuation trigger method",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress verbose output",
    )
    
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    
    launcher = OSDashLauncher(
        workspace=args.workspace,
        verbose=not args.quiet,
    )
    
    if args.status:
        launcher.print_status()
        return 0
    
    if args.preflight:
        return 0 if launcher.run_preflight() else 1
    
    if args.install:
        return launcher.install_dependencies()
    
    if args.mode:
        if args.mode == "dev":
            return launcher.launch_dev()
        elif args.mode == "desktop":
            return launcher.launch_desktop()
        elif args.mode == "guardian":
            return launcher.launch_guardian()
        elif args.mode == "orchestrator":
            return launcher.launch_orchestrator(
                execute=args.execute,
                continue_todos=args.continue_todos,
            )
        elif args.mode == "daemon":
            return launcher.launch_daemon(method=args.daemon_method)
    
    # Interactive mode
    return launcher.interactive_menu()


if __name__ == "__main__":
    raise SystemExit(main())
