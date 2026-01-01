"""
Launch/Execution operations for OS Dashboard AI Assistant
"""

import sys
import time
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
from enum import Enum

from .base import BaseOperation, OperationResult, OperationStatus, OperationError


class LaunchMode(Enum):
    """Launch mode enumeration"""
    WEB = "web"
    DESKTOP = "desktop"
    WEB_BUILD = "web-build"
    DESKTOP_BUILD = "desktop-build"
    ORCHESTRATOR = "orchestrator"
    BACKEND_ONLY = "backend-only"


class LaunchOperation(BaseOperation):
    """Handles launching and execution of the application"""
    
    def check_prerequisites(self) -> OperationResult:
        """Check launch prerequisites"""
        missing = []
        
        # Check Python
        if sys.version_info < (3, 9):
            missing.append(f"Python 3.9+ (found: {sys.version})")
        
        # Check required Python packages (basic check)
        try:
            import fastapi
        except ImportError:
            missing.append("fastapi (Python package)")
        
        return OperationResult(
            status=OperationStatus.SUCCESS if not missing else OperationStatus.FAILED,
            message="Launch prerequisites check passed" if not missing else f"Missing prerequisites: {', '.join(missing)}",
            exit_code=0 if not missing else 1
        )
    
    def launch_backend(
        self,
        host: str = "127.0.0.1",
        port: int = 8000,
        reload: bool = False
    ) -> subprocess.Popen:
        """Launch FastAPI backend server"""
        self.logger.info(f"Starting backend server on {host}:{port}...")
        
        cmd = [
            sys.executable,
            "-m",
            "uvicorn",
            "assistant_hub.api.server:create_app",
            "--factory",
            "--host", host,
            "--port", str(port)
        ]
        
        if reload:
            cmd.append("--reload")
        
        process = subprocess.Popen(
            cmd,
            cwd=self.project_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        return process
    
    def launch_web_dev(self) -> OperationResult:
        """Launch web development mode"""
        if not self.check_command("npm"):
            return OperationResult(
                status=OperationStatus.FAILED,
                message="npm not found - cannot launch web dev server",
                exit_code=1
            )
        
        self.logger.info("Launching web development server...")
        
        try:
            # Start backend
            backend_process = self.launch_backend(reload=True)
            self.logger.info(f"Backend started (PID: {backend_process.pid})")
            
            # Start frontend dev server
            frontend_process = subprocess.Popen(
                ["npm", "run", "dev:web"],
                cwd=self.frontend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.logger.info(f"Frontend dev server started (PID: {frontend_process.pid})")
            
            return OperationResult(
                status=OperationStatus.SUCCESS,
                message="Web development servers started",
                details={
                    "backend_pid": backend_process.pid,
                    "frontend_pid": frontend_process.pid,
                    "backend_url": "http://127.0.0.1:8000",
                    "frontend_url": "http://localhost:5173"
                }
            )
        except Exception as e:
            return OperationResult(
                status=OperationStatus.FAILED,
                message=f"Failed to launch web dev: {str(e)}",
                exit_code=1
            )
    
    def launch_desktop_dev(self) -> OperationResult:
        """Launch desktop development mode"""
        if not self.check_command("npm"):
            return OperationResult(
                status=OperationStatus.FAILED,
                message="npm not found - cannot launch desktop dev",
                exit_code=1
            )
        
        self.logger.info("Launching desktop development mode...")
        
        try:
            # Start backend
            backend_process = self.launch_backend(reload=True)
            self.logger.info(f"Backend started (PID: {backend_process.pid})")
            
            # Start desktop dev
            desktop_process = subprocess.Popen(
                ["npm", "run", "dev:desktop"],
                cwd=self.frontend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.logger.info(f"Desktop dev started (PID: {desktop_process.pid})")
            
            return OperationResult(
                status=OperationStatus.SUCCESS,
                message="Desktop development mode started",
                details={
                    "backend_pid": backend_process.pid,
                    "desktop_pid": desktop_process.pid,
                    "backend_url": "http://127.0.0.1:8000"
                }
            )
        except Exception as e:
            return OperationResult(
                status=OperationStatus.FAILED,
                message=f"Failed to launch desktop dev: {str(e)}",
                exit_code=1
            )
    
    def launch_web_build(self) -> OperationResult:
        """Launch production web build"""
        dist_dir = self.frontend_dir / "dist"
        
        if not dist_dir.exists():
            return OperationResult(
                status=OperationStatus.FAILED,
                message=f"Build directory not found: {dist_dir}. Please run build first.",
                exit_code=1
            )
        
        self.logger.info("Launching production web build...")
        
        try:
            backend_process = self.launch_backend()
            self.logger.info(f"Backend started (PID: {backend_process.pid})")
            
            return OperationResult(
                status=OperationStatus.SUCCESS,
                message="Production web build launched",
                details={
                    "backend_pid": backend_process.pid,
                    "backend_url": "http://127.0.0.1:8000",
                    "note": "Frontend is served by backend at /app"
                }
            )
        except Exception as e:
            return OperationResult(
                status=OperationStatus.FAILED,
                message=f"Failed to launch web build: {str(e)}",
                exit_code=1
            )
    
    def launch_orchestrator(
        self,
        workspace_root: Optional[Path] = None,
        ui: bool = False
    ) -> OperationResult:
        """Launch master orchestrator"""
        orchestrator_script = self.project_root / "os_dashboard_ai_assistant.py"
        
        if not orchestrator_script.exists():
            return OperationResult(
                status=OperationStatus.FAILED,
                message=f"Orchestrator script not found: {orchestrator_script}",
                exit_code=1
            )
        
        self.logger.info("Launching master orchestrator...")
        
        try:
            cmd = [sys.executable, str(orchestrator_script)]
            
            if workspace_root:
                cmd.extend(["--root", str(workspace_root)])
            
            process = subprocess.Popen(
                cmd,
                cwd=self.project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.logger.info(f"Orchestrator started (PID: {process.pid})")
            
            # If UI is requested, also start the UI
            ui_process = None
            if ui:
                ui_script = self.project_root / "start_ui.py"
                if ui_script.exists():
                    ui_process = subprocess.Popen(
                        [sys.executable, str(ui_script), "--enable-orchestrator"],
                        cwd=self.project_root,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                    self.logger.info(f"UI started (PID: {ui_process.pid})")
            
            details = {
                "orchestrator_pid": process.pid,
                "status_url": "http://localhost:8000/api/orchestrator/status"
            }
            
            if ui_process:
                details["ui_pid"] = ui_process.pid
                details["ui_url"] = "http://localhost:5173/ai/orchestrator"
            
            return OperationResult(
                status=OperationStatus.SUCCESS,
                message="Master orchestrator launched",
                details=details
            )
        except Exception as e:
            return OperationResult(
                status=OperationStatus.FAILED,
                message=f"Failed to launch orchestrator: {str(e)}",
                exit_code=1
            )
    
    def launch_backend_only(
        self,
        host: str = "127.0.0.1",
        port: int = 8000,
        reload: bool = False
    ) -> OperationResult:
        """Launch backend server only"""
        try:
            backend_process = self.launch_backend(host=host, port=port, reload=reload)
            
            return OperationResult(
                status=OperationStatus.SUCCESS,
                message=f"Backend server started on {host}:{port}",
                details={
                    "backend_pid": backend_process.pid,
                    "backend_url": f"http://{host}:{port}",
                    "api_docs": f"http://{host}:{port}/docs",
                    "reload": reload
                }
            )
        except Exception as e:
            return OperationResult(
                status=OperationStatus.FAILED,
                message=f"Failed to launch backend: {str(e)}",
                exit_code=1
            )
    
    def execute(
        self,
        mode: str = "web",
        workspace_root: Optional[Path] = None,
        host: str = "127.0.0.1",
        port: int = 8000,
        reload: bool = False,
        ui: bool = False,
        **kwargs
    ) -> OperationResult:
        """
        Execute launch operation
        
        Args:
            mode: Launch mode (web, desktop, web-build, desktop-build, orchestrator, backend-only)
            workspace_root: Workspace root for orchestrator
            host: Backend host
            port: Backend port
            reload: Enable auto-reload for backend
            ui: Enable UI (for orchestrator mode)
        """
        start_time = time.time()
        
        self.logger.info("=" * 60)
        self.logger.info("Starting Launch")
        self.logger.info("=" * 60)
        
        # Check prerequisites
        prereq_result = self.check_prerequisites()
        if prereq_result.failed:
            return prereq_result
        
        # Parse mode
        try:
            launch_mode = LaunchMode(mode)
        except ValueError:
            return OperationResult(
                status=OperationStatus.FAILED,
                message=f"Invalid launch mode: {mode}. Valid: {[m.value for m in LaunchMode]}",
                exit_code=1
            )
        
        # Launch based on mode
        if launch_mode == LaunchMode.WEB:
            result = self.launch_web_dev()
        elif launch_mode == LaunchMode.DESKTOP:
            result = self.launch_desktop_dev()
        elif launch_mode == LaunchMode.WEB_BUILD:
            result = self.launch_web_build()
        elif launch_mode == LaunchMode.DESKTOP_BUILD:
            result = self.launch_web_build()  # Desktop build uses same backend
        elif launch_mode == LaunchMode.ORCHESTRATOR:
            result = self.launch_orchestrator(workspace_root=workspace_root, ui=ui)
        elif launch_mode == LaunchMode.BACKEND_ONLY:
            result = self.launch_backend_only(host=host, port=port, reload=reload)
        else:
            result = OperationResult(
                status=OperationStatus.FAILED,
                message=f"Unsupported launch mode: {mode}",
                exit_code=1
            )
        
        duration = time.time() - start_time
        result.duration = duration
        
        self.logger.info("=" * 60)
        self.logger.info("Launch Summary")
        self.logger.info("=" * 60)
        status_icon = "✓" if result.success else "✗"
        self.logger.info(f"{status_icon} {result.message}")
        if result.details:
            for key, value in result.details.items():
                self.logger.info(f"  {key}: {value}")
        self.logger.info(f"Duration: {duration:.2f}s")
        self.logger.info("=" * 60)
        
        return result

