#!/usr/bin/env python3
"""
Unified Launcher - Single Entry Point for OS Dashboard AI Assistant

This script provides a unified interface to launch all components of the
OS Dashboard AI Assistant system, including:
- Backend API server
- Frontend dev server
- Project orchestrator
- Terminal shell
- Auto-fix monitors

Usage:
    python scripts/unified_launcher.py [mode]

Modes:
    web        - Launch backend + frontend (default)
    orchestrator - Launch project orchestrator in daemon mode
    shell      - Launch interactive terminal shell
    autofix    - Launch auto-fix monitors for all projects
    all        - Launch everything
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent


def launch_backend(port: int = 8000) -> subprocess.Popen:
    """Launch the FastAPI backend server."""
    print("🚀 Starting backend API server...")
    return subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "backend_api.main:app",
            "--host",
            "0.0.0.0",
            "--port",
            str(port),
            "--reload",
        ],
        cwd=REPO_ROOT,
    )


def launch_frontend() -> subprocess.Popen:
    """Launch the frontend dev server."""
    print("🚀 Starting frontend dev server...")
    frontend_dir = REPO_ROOT / "frontend"
    if not (frontend_dir / "package.json").exists():
        print("⚠️  Frontend directory not found. Skipping frontend launch.")
        return None
    
    return subprocess.Popen(
        ["npm", "run", "dev:web"],
        cwd=frontend_dir,
    )


def launch_orchestrator(daemon: bool = True, auto_fix: bool = True) -> subprocess.Popen:
    """Launch the project orchestrator."""
    print("🚀 Starting project orchestrator...")
    cmd = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "unified_project_orchestrator.py"),
    ]
    
    if daemon:
        cmd.append("--daemon")
    if auto_fix:
        cmd.append("--auto-fix")
    
    return subprocess.Popen(cmd, cwd=REPO_ROOT)


def launch_shell() -> int:
    """Launch the interactive terminal shell."""
    print("🚀 Starting unified terminal shell...")
    return subprocess.call(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "unified_terminal_shell.py"),
        ],
        cwd=REPO_ROOT,
    )


def launch_autofix() -> subprocess.Popen:
    """Launch auto-fix monitors for all projects."""
    print("🚀 Starting auto-fix monitors...")
    return subprocess.Popen(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "unified_project_orchestrator.py"),
            "--auto-fix",
            "--daemon",
        ],
        cwd=REPO_ROOT,
    )


def main():
    parser = argparse.ArgumentParser(
        description="Unified Launcher for OS Dashboard AI Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "mode",
        nargs="?",
        default="web",
        choices=["web", "orchestrator", "shell", "autofix", "all"],
        help="Launch mode",
    )
    parser.add_argument(
        "--backend-port",
        type=int,
        default=8000,
        help="Backend API port",
    )
    parser.add_argument(
        "--no-frontend",
        action="store_true",
        help="Skip frontend launch",
    )
    parser.add_argument(
        "--no-orchestrator",
        action="store_true",
        help="Skip orchestrator launch",
    )
    
    args = parser.parse_args()
    
    processes: List[subprocess.Popen] = []
    
    try:
        if args.mode == "web" or args.mode == "all":
            backend_proc = launch_backend(args.backend_port)
            processes.append(backend_proc)
            
            if not args.no_frontend:
                frontend_proc = launch_frontend()
                if frontend_proc:
                    processes.append(frontend_proc)
            
            if not args.no_orchestrator and args.mode == "all":
                orchestrator_proc = launch_orchestrator()
                processes.append(orchestrator_proc)
            
            print("\n✅ All services started!")
            print(f"   Backend: http://localhost:{args.backend_port}")
            print(f"   Frontend: http://localhost:5173")
            print(f"   API Docs: http://localhost:{args.backend_port}/swagger")
            print("\nPress Ctrl+C to stop all services...\n")
            
            # Wait for all processes
            try:
                while True:
                    time.sleep(1)
                    # Check if any process has died
                    for proc in processes:
                        if proc.poll() is not None:
                            print(f"⚠️  Process {proc.pid} exited unexpectedly")
            except KeyboardInterrupt:
                print("\n⏹️  Shutting down all services...")
        
        elif args.mode == "orchestrator":
            orchestrator_proc = launch_orchestrator()
            processes.append(orchestrator_proc)
            print("\n✅ Project orchestrator started!")
            print("Press Ctrl+C to stop...\n")
            orchestrator_proc.wait()
        
        elif args.mode == "shell":
            return launch_shell()
        
        elif args.mode == "autofix":
            autofix_proc = launch_autofix()
            processes.append(autofix_proc)
            print("\n✅ Auto-fix monitors started!")
            print("Press Ctrl+C to stop...\n")
            autofix_proc.wait()
        
    except KeyboardInterrupt:
        print("\n⏹️  Interrupted by user")
    finally:
        # Cleanup all processes
        for proc in processes:
            try:
                proc.terminate()
                proc.wait(timeout=5)
            except Exception:
                proc.kill()
        print("👋 All services stopped")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
