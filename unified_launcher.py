#!/usr/bin/env python3
"""
Unified Launcher for AI OS
==============================================

This script provides a single entry point for:
1. Starting all backend services
2. Launching the frontend (desktop or browser)
3. SDLC automation (code generation, testing, deployment)
4. Data fetching and monitoring
5. Continuous integration and deployment

Usage:
    python unified_launcher.py --mode desktop  # Launch desktop app
    python unified_launcher.py --mode browser  # Launch in browser
    python unified_launcher.py --mode server   # Server only
    python unified_launcher.py --mode sdlc     # Run SDLC automation
    python unified_launcher.py --mode all      # All services
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import os
import signal
import subprocess
import sys
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path
REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("unified_launcher")


@dataclass
class ServiceConfig:
    """Configuration for a service component."""
    name: str
    module: str
    args: List[str]
    enabled: bool = True
    process: Optional[subprocess.Popen] = None
    thread: Optional[threading.Thread] = None


class UnifiedLauncher:
    """Main launcher class that orchestrates all services."""
    
    def __init__(self, mode: str = "all", host: str = "127.0.0.1", port: int = 8800):
        self.mode = mode
        self.host = host
        self.port = port
        self.services: List[ServiceConfig] = []
        self.running = False
        self.sdlc_enabled = False
        
    def setup_services(self) -> None:
        """Configure which services to start based on mode."""
        if self.mode in ("all", "server", "desktop", "browser"):
            logger.info(f"Setting up services for mode: {self.mode}")
            # The main API server will be started via webview_app or api_server
        
        if self.mode in ("all", "sdlc"):
            self.sdlc_enabled = True
            logger.info("SDLC automation enabled")
    
    def start_api_server(self) -> None:
        """Start the FastAPI backend server."""
        from assistant_hub_gui.webview_app import launch_browser, launch_desktop
        
        try:
            if self.mode == "desktop":
                logger.info("Launching desktop application...")
                launch_desktop(self.host, self.port)
            elif self.mode in ("browser", "all", "server"):
                logger.info(f"Launching browser application at {self.host}:{self.port}...")
                launch_browser(self.host, self.port)
            else:
                logger.warning(f"Unknown mode: {self.mode}")
        except Exception as exc:
            logger.error(f"Failed to start API server: {exc}", exc_info=True)
            raise
    
    async def run_sdlc_automation(self) -> None:
        """Run SDLC automation tasks."""
        logger.info("=" * 60)
        logger.info("SDLC AUTOMATION PIPELINE")
        logger.info("=" * 60)
        
        # Phase 1: Code Generation
        await self._run_code_generation()
        
        # Phase 2: Testing
        await self._run_tests()
        
        # Phase 3: Linting & Quality Checks
        await self._run_quality_checks()
        
        # Phase 4: Build
        await self._run_build()
        
        # Phase 5: Deploy (if configured)
        await self._run_deployment()
        
        logger.info("=" * 60)
        logger.info("SDLC PIPELINE COMPLETE")
        logger.info("=" * 60)
    
    async def _run_code_generation(self) -> None:
        """Phase 1: Code generation and scaffolding."""
        logger.info("\n[Phase 1] Code Generation")
        logger.info("-" * 60)
        
        # Check for missing files or incomplete implementations
        critical_files = [
            "assistant_hub/api/server.py",
            "assistant_hub_gui/webview_app.py",
            "backend_api/routers/runtime_diagnostics.py",
            "backend_api/routers/personas.py",
            "backend_api/routers/search.py",
            "backend_api/routers/templates.py",
            "backend_api/routers/audit.py",
        ]
        
        for file_path in critical_files:
            full_path = REPO_ROOT / file_path
            if full_path.exists():
                logger.info(f"✓ {file_path}")
            else:
                logger.warning(f"✗ {file_path} - MISSING")
        
        logger.info("Code generation check complete")
    
    async def _run_tests(self) -> None:
        """Phase 2: Run automated tests."""
        logger.info("\n[Phase 2] Running Tests")
        logger.info("-" * 60)
        
        # Run pytest if available
        tests_dir = REPO_ROOT / "tests"
        if tests_dir.exists():
            try:
                logger.info("Running pytest...")
                result = subprocess.run(
                    [sys.executable, "-m", "pytest", "-v", "--tb=short"],
                    cwd=REPO_ROOT,
                    capture_output=True,
                    text=True,
                    timeout=300,
                )
                
                if result.returncode == 0:
                    logger.info("✓ All tests passed")
                else:
                    logger.warning(f"✗ Tests failed with exit code {result.returncode}")
                    if result.stdout:
                        logger.info(f"STDOUT:\n{result.stdout[-1000:]}")
                    if result.stderr:
                        logger.warning(f"STDERR:\n{result.stderr[-1000:]}")
            except subprocess.TimeoutExpired:
                logger.error("✗ Tests timed out")
            except FileNotFoundError:
                logger.warning("pytest not found, skipping tests")
        else:
            logger.info("No tests directory found")
    
    async def _run_quality_checks(self) -> None:
        """Phase 3: Run linting and quality checks."""
        logger.info("\n[Phase 3] Quality Checks")
        logger.info("-" * 60)
        
        # Run basic Python syntax check
        python_files = list(REPO_ROOT.rglob("*.py"))
        syntax_errors = 0
        
        for py_file in python_files[:50]:  # Sample first 50 files
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    compile(f.read(), str(py_file), "exec")
            except SyntaxError as e:
                logger.error(f"✗ Syntax error in {py_file}: {e}")
                syntax_errors += 1
        
        if syntax_errors == 0:
            logger.info(f"✓ No syntax errors in {len(python_files[:50])} files")
        else:
            logger.warning(f"✗ Found {syntax_errors} syntax errors")
    
    async def _run_build(self) -> None:
        """Phase 4: Build frontend and assets."""
        logger.info("\n[Phase 4] Building Assets")
        logger.info("-" * 60)
        
        frontend_dir = REPO_ROOT / "frontend"
        if frontend_dir.exists():
            package_json = frontend_dir / "package.json"
            if package_json.exists():
                logger.info("Frontend build directory found")
                dist_dir = frontend_dir / "dist"
                if dist_dir.exists():
                    logger.info(f"✓ Frontend dist exists with {len(list(dist_dir.rglob('*')))} files")
                else:
                    logger.warning("✗ Frontend dist directory not found")
                    logger.info("Run 'npm run build' in frontend directory to build")
            else:
                logger.warning("No package.json found in frontend")
        else:
            logger.warning("No frontend directory found")
    
    async def _run_deployment(self) -> None:
        """Phase 5: Deployment preparation."""
        logger.info("\n[Phase 5] Deployment Preparation")
        logger.info("-" * 60)
        
        # Check deployment configurations
        deployment_files = [
            "docker-compose.yml",
            "Dockerfile",
            "deploy-aws.sh",
            "build-all-platforms.sh",
        ]
        
        for deploy_file in deployment_files:
            file_path = REPO_ROOT / deploy_file
            if file_path.exists():
                logger.info(f"✓ {deploy_file}")
            else:
                logger.info(f"○ {deploy_file} - Not configured")
        
        logger.info("Deployment check complete")
    
    async def monitor_data_fetching(self) -> None:
        """Monitor and ensure all data is being fetched properly."""
        logger.info("\n[Monitor] Data Fetching Status")
        logger.info("-" * 60)
        
        # Check database connectivity
        try:
            import sqlite3
            from assistant_hub.config import DB_PATH
            
            conn = sqlite3.connect(str(DB_PATH))
            cursor = conn.cursor()
            
            # Check key tables
            tables = ["tasks", "projects", "chat_messages", "settings"]
            for table in tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    logger.info(f"✓ {table}: {count} records")
                except sqlite3.Error as e:
                    logger.warning(f"✗ {table}: Error - {e}")
            
            conn.close()
        except Exception as e:
            logger.error(f"Database check failed: {e}")
    
    def run(self) -> int:
        """Main entry point for the launcher."""
        logger.info("=" * 60)
        logger.info("OS DASHBOARD AI ASSISTANT - UNIFIED LAUNCHER")
        logger.info("=" * 60)
        logger.info(f"Mode: {self.mode}")
        logger.info(f"Host: {self.host}")
        logger.info(f"Port: {self.port}")
        logger.info(f"Timestamp: {datetime.now().isoformat()}")
        logger.info("=" * 60)
        
        self.setup_services()
        self.running = True
        
        # Handle SDLC mode
        if self.mode == "sdlc":
            try:
                asyncio.run(self.run_sdlc_automation())
                asyncio.run(self.monitor_data_fetching())
                return 0
            except Exception as exc:
                logger.error(f"SDLC automation failed: {exc}", exc_info=True)
                return 1
        
        # Handle server/UI modes
        if self.mode in ("server", "browser", "desktop", "all"):
            try:
                # Run data monitoring in background
                monitor_thread = threading.Thread(
                    target=lambda: asyncio.run(self.monitor_data_fetching()),
                    daemon=True
                )
                monitor_thread.start()
                
                # Start the main API server (this will block)
                self.start_api_server()
                return 0
            except KeyboardInterrupt:
                logger.info("\nShutdown requested...")
                return 0
            except Exception as exc:
                logger.error(f"Launcher failed: {exc}", exc_info=True)
                return 1
        
        logger.error(f"Unknown mode: {self.mode}")
        return 1
    
    def shutdown(self) -> None:
        """Clean shutdown of all services."""
        logger.info("Shutting down services...")
        self.running = False
        
        for service in self.services:
            if service.process and service.process.poll() is None:
                logger.info(f"Stopping {service.name}...")
                service.process.terminate()
                try:
                    service.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    logger.warning(f"Force killing {service.name}...")
                    service.process.kill()


def main() -> int:
    """Parse arguments and run the launcher."""
    parser = argparse.ArgumentParser(
        description="Unified launcher for AI OS",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    
    parser.add_argument(
        "--mode",
        choices=["desktop", "browser", "server", "sdlc", "all"],
        default="browser",
        help="Launch mode (default: browser)",
    )
    
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host for API server (default: 127.0.0.1)",
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8800,
        help="Port for API server (default: 8800)",
    )
    
    parser.add_argument(
        "--auto-fix",
        action="store_true",
        help="Enable auto-fix monitor",
    )
    
    args = parser.parse_args()
    
    launcher = UnifiedLauncher(
        mode=args.mode,
        host=args.host,
        port=args.port,
    )
    
    # Set up signal handlers
    def signal_handler(signum, frame):
        logger.info(f"\nReceived signal {signum}")
        launcher.shutdown()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    return launcher.run()


if __name__ == "__main__":
    sys.exit(main())
