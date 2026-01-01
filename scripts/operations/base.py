"""
Base classes and utilities for operations
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass


class OperationStatus(Enum):
    """Operation status enumeration"""
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    WARNING = "warning"


@dataclass
class OperationResult:
    """Result of an operation"""
    status: OperationStatus
    message: str
    details: Optional[Dict[str, Any]] = None
    exit_code: int = 0
    duration: float = 0.0

    @property
    def success(self) -> bool:
        return self.status == OperationStatus.SUCCESS

    @property
    def failed(self) -> bool:
        return self.status == OperationStatus.FAILED


class OperationError(Exception):
    """Exception raised during operations"""
    pass


class BaseOperation:
    """Base class for all operations"""
    
    def __init__(self, project_root: Optional[Path] = None, verbose: bool = False):
        """
        Initialize base operation
        
        Args:
            project_root: Project root directory (defaults to script parent)
            verbose: Enable verbose logging
        """
        if project_root is None:
            # Default to parent of scripts directory
            self.project_root = Path(__file__).parent.parent.parent.resolve()
        else:
            self.project_root = Path(project_root).resolve()
        
        self.verbose = verbose
        self.logger = self._setup_logger()
        self.frontend_dir = self.project_root / "frontend"
        self.scripts_dir = self.project_root / "scripts"
        self.tests_dir = self.project_root / "tests"
        
    def _setup_logger(self) -> logging.Logger:
        """Setup logger for this operation"""
        logger = logging.getLogger(self.__class__.__name__)
        logger.setLevel(logging.DEBUG if self.verbose else logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def check_command(self, command: str) -> bool:
        """Check if a command exists"""
        return bool(self.run_command(f"command -v {command}", capture=True, check=False).returncode == 0)
    
    def run_command(
        self,
        command: str,
        cwd: Optional[Path] = None,
        capture: bool = False,
        check: bool = True,
        env: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None
    ) -> subprocess.CompletedProcess:
        """
        Run a shell command
        
        Args:
            command: Command to run
            cwd: Working directory (defaults to project_root)
            capture: Capture stdout/stderr
            check: Raise exception on non-zero exit
            env: Environment variables
            timeout: Command timeout in seconds
        
        Returns:
            CompletedProcess result
        """
        if cwd is None:
            cwd = self.project_root
        
        self.logger.debug(f"Running command: {command}")
        self.logger.debug(f"Working directory: {cwd}")
        
        env_vars = os.environ.copy()
        if env:
            env_vars.update(env)
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                capture_output=capture,
                text=True,
                env=env_vars,
                timeout=timeout,
                check=False
            )
            
            if capture and self.verbose:
                if result.stdout:
                    self.logger.debug(f"STDOUT: {result.stdout}")
                if result.stderr:
                    self.logger.debug(f"STDERR: {result.stderr}")
            
            if check and result.returncode != 0:
                error_msg = result.stderr if capture else "Command failed"
                raise OperationError(f"Command failed with exit code {result.returncode}: {error_msg}")
            
            return result
            
        except subprocess.TimeoutExpired as e:
            raise OperationError(f"Command timed out after {timeout} seconds: {command}") from e
        except Exception as e:
            raise OperationError(f"Error running command: {command}") from e
    
    def check_prerequisites(self) -> OperationResult:
        """Check prerequisites for this operation"""
        # Base implementation - override in subclasses
        return OperationResult(
            status=OperationStatus.SUCCESS,
            message="Prerequisites check passed"
        )
    
    def execute(self, **kwargs) -> OperationResult:
        """Execute the operation - must be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement execute method")
    
    def get_project_info(self) -> Dict[str, Any]:
        """Get basic project information"""
        info = {
            "project_root": str(self.project_root),
            "frontend_dir": str(self.frontend_dir),
            "scripts_dir": str(self.scripts_dir),
            "tests_dir": str(self.tests_dir),
        }
        
        # Check Python version
        try:
            python_version = sys.version.split()[0]
            info["python_version"] = python_version
        except Exception:
            info["python_version"] = "unknown"
        
        # Check Node version
        try:
            result = self.run_command("node --version", capture=True, check=False)
            if result.returncode == 0:
                info["node_version"] = result.stdout.strip()
            else:
                info["node_version"] = "not installed"
        except Exception:
            info["node_version"] = "unknown"
        
        # Check npm version
        try:
            result = self.run_command("npm --version", capture=True, check=False)
            if result.returncode == 0:
                info["npm_version"] = result.stdout.strip()
            else:
                info["npm_version"] = "not installed"
        except Exception:
            info["npm_version"] = "unknown"
        
        return info


