"""Monitor management module for the master orchestrator.

This module handles launching, monitoring, and managing project monitors.
"""

from __future__ import annotations

import os
import subprocess
import sys
import threading
from pathlib import Path
from typing import Dict, Optional

from utils.exceptions import MonitorError, ProcessError
from utils.logger import get_logger, LogContext

from orchestrator.project_discovery import ProjectInfo

logger = get_logger(__name__)


class MonitorManager:
    """Manages project monitor processes."""
    
    def __init__(self, log_dir: Path) -> None:
        """Initialize monitor manager.
        
        Args:
            log_dir: Directory for monitor log files
        """
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.monitors: Dict[str, subprocess.Popen] = {}
        self.monitor_threads: Dict[str, threading.Thread] = {}
    
    def launch_monitor(self, project: ProjectInfo) -> bool:
        """Launch an AI auto-fix monitor for a project.
        
        Args:
            project: Project information
        
        Returns:
            True if monitor launched successfully
        
        Raises:
            MonitorError: If monitor launch fails
        """
        if not project.has_ai_autofix:
            logger.warning(
                f"{project.name}: No ai_auto_fix.py script found",
                extra={"context": LogContext(project_id=project.name)},
            )
            return False
        
        script_path = project.path / "scripts" / "ai_auto_fix.py"
        
        if not script_path.exists():
            raise MonitorError(
                f"Monitor script not found: {script_path}",
                error_code="SCRIPT_NOT_FOUND",
                context={"project": project.name, "script": str(script_path)},
            )
        
        # Build command
        cmd = [
            sys.executable,
            str(script_path),
            "--logs-only",
            "--daemon",
            "--max-attempts", "0",  # Unlimited
        ]
        
        try:
            logger.info(
                f"Launching monitor for {project.name}",
                extra={"context": LogContext(project_id=project.name)},
            )
            
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
            self.monitor_threads[project.name] = thread
            
            logger.info(
                f"Monitor launched for {project.name} (PID: {process.pid})",
                extra={"context": LogContext(project_id=project.name)},
            )
            return True
            
        except Exception as e:
            raise MonitorError(
                f"Failed to launch monitor for {project.name}",
                error_code="LAUNCH_FAILED",
                context={"project": project.name, "command": " ".join(cmd)},
                cause=e,
            ) from e
    
    def _monitor_output(self, project: ProjectInfo, process: subprocess.Popen) -> None:
        """Monitor the output of a project's AI auto-fix process.
        
        Args:
            project: Project information
            process: Monitor process
        """
        assert process.stdout is not None
        project_log = self.log_dir / f"{project.name}_monitor.log"
        
        context = LogContext(project_id=project.name, operation="monitor_output")
        
        try:
            for line in process.stdout:
                line = line.rstrip()
                if line:
                    # Log to project-specific log file
                    with project_log.open("a", encoding="utf-8") as f:
                        from datetime import datetime
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        f.write(f"[{timestamp}] {line}\n")
            
            # Process ended
            returncode = process.wait()
            logger.warning(
                f"Monitor for {project.name} ended (code: {returncode})",
                extra={"context": context},
            )
            project.status = "stopped"
            
        except Exception as e:
            logger.error(
                f"Error monitoring {project.name}: {e}",
                extra={"context": context},
            )
            project.status = "error"
    
    def stop_monitor(self, project_name: str, timeout: int = 5) -> bool:
        """Stop a monitor for a project.
        
        Args:
            project_name: Name of the project
            timeout: Timeout in seconds for graceful shutdown
        
        Returns:
            True if monitor stopped successfully
        """
        if project_name not in self.monitors:
            return False
        
        process = self.monitors[project_name]
        context = LogContext(project_id=project_name, operation="stop_monitor")
        
        try:
            logger.info(f"Stopping monitor for {project_name}", extra={"context": context})
            process.terminate()
            process.wait(timeout=timeout)
            del self.monitors[project_name]
            if project_name in self.monitor_threads:
                del self.monitor_threads[project_name]
            logger.info(f"Monitor stopped for {project_name}", extra={"context": context})
            return True
            
        except subprocess.TimeoutExpired:
            logger.warning(
                f"Force killing monitor for {project_name}",
                extra={"context": context},
            )
            process.kill()
            process.wait()
            del self.monitors[project_name]
            if project_name in self.monitor_threads:
                del self.monitor_threads[project_name]
            return True
            
        except Exception as e:
            logger.error(
                f"Error stopping monitor for {project_name}: {e}",
                extra={"context": context},
            )
            return False
    
    def stop_all(self, timeout: int = 5) -> None:
        """Stop all monitors.
        
        Args:
            timeout: Timeout in seconds for graceful shutdown
        """
        project_names = list(self.monitors.keys())
        for project_name in project_names:
            self.stop_monitor(project_name, timeout)
    
    def get_status(self) -> Dict[str, str]:
        """Get status of all monitors.
        
        Returns:
            Dictionary mapping project names to status strings
        """
        status: Dict[str, str] = {}
        
        for project_name, process in self.monitors.items():
            if process.poll() is not None:
                status[project_name] = "stopped"
            else:
                status[project_name] = "running"
        
        return status


