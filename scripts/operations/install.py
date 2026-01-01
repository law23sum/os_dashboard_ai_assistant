"""
Installation operations for OS Dashboard AI Assistant
"""

import sys
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

from .base import BaseOperation, OperationResult, OperationStatus, OperationError


class InstallOperation(BaseOperation):
    """Handles installation of dependencies and setup"""
    
    def __init__(self, project_root: Optional[Path] = None, verbose: bool = False):
        super().__init__(project_root, verbose)
        self.venv_path = self.project_root / "venv"
        self.requirements_file = self.project_root / "requirements.txt"
        self.package_json = self.frontend_dir / "package.json"
    
    def check_prerequisites(self) -> OperationResult:
        """Check installation prerequisites"""
        missing = []
        
        # Check Python
        if sys.version_info < (3, 9):
            missing.append(f"Python 3.9+ (found: {sys.version})")
        
        # Check Node.js (optional but recommended)
        if not self.check_command("node"):
            self.logger.warning("Node.js not found - frontend installation will be skipped")
        else:
            result = self.run_command("node --version", capture=True, check=False)
            if result.returncode == 0:
                version = result.stdout.strip()
                self.logger.info(f"Found Node.js: {version}")
        
        # Check npm (optional but recommended)
        if not self.check_command("npm"):
            self.logger.warning("npm not found - frontend installation will be skipped")
        else:
            result = self.run_command("npm --version", capture=True, check=False)
            if result.returncode == 0:
                version = result.stdout.strip()
                self.logger.info(f"Found npm: {version}")
        
        if missing:
            return OperationResult(
                status=OperationStatus.FAILED,
                message=f"Missing prerequisites: {', '.join(missing)}",
                exit_code=1
            )
        
        return OperationResult(
            status=OperationStatus.SUCCESS,
            message="Prerequisites check passed"
        )
    
    def create_venv(self, force: bool = False) -> OperationResult:
        """Create Python virtual environment"""
        if self.venv_path.exists() and not force:
            self.logger.info(f"Virtual environment already exists at {self.venv_path}")
            return OperationResult(
                status=OperationStatus.SUCCESS,
                message="Virtual environment already exists"
            )
        
        self.logger.info("Creating Python virtual environment...")
        try:
            # Remove existing venv if forcing
            if self.venv_path.exists() and force:
                import shutil
                shutil.rmtree(self.venv_path)
                self.logger.info("Removed existing virtual environment")
            
            # Create new venv
            self.run_command(f"{sys.executable} -m venv {self.venv_path}", check=True)
            
            return OperationResult(
                status=OperationStatus.SUCCESS,
                message=f"Virtual environment created at {self.venv_path}"
            )
        except Exception as e:
            return OperationResult(
                status=OperationStatus.FAILED,
                message=f"Failed to create virtual environment: {str(e)}",
                exit_code=1
            )
    
    def get_pip_command(self) -> str:
        """Get the appropriate pip command (from venv if it exists)"""
        if sys.platform == "win32":
            pip_path = self.venv_path / "Scripts" / "pip"
        else:
            pip_path = self.venv_path / "bin" / "pip"
        
        if pip_path.exists():
            return str(pip_path)
        return "pip"
    
    def install_python_dependencies(
        self,
        upgrade_pip: bool = True,
        use_venv: bool = True
    ) -> OperationResult:
        """Install Python dependencies"""
        if not self.requirements_file.exists():
            return OperationResult(
                status=OperationStatus.SKIPPED,
                message=f"Requirements file not found: {self.requirements_file}"
            )
        
        start_time = time.time()
        self.logger.info("Installing Python dependencies...")
        
        try:
            pip_cmd = self.get_pip_command() if use_venv and self.venv_path.exists() else "pip"
            
            # Upgrade pip first
            if upgrade_pip:
                self.logger.info("Upgrading pip...")
                self.run_command(f"{pip_cmd} install --upgrade pip", check=False)
            
            # Install requirements
            self.logger.info(f"Installing from {self.requirements_file}...")
            self.run_command(
                f"{pip_cmd} install -r {self.requirements_file}",
                check=True,
                timeout=600  # 10 minute timeout
            )
            
            duration = time.time() - start_time
            return OperationResult(
                status=OperationStatus.SUCCESS,
                message="Python dependencies installed successfully",
                duration=duration
            )
        except Exception as e:
            duration = time.time() - start_time
            return OperationResult(
                status=OperationStatus.FAILED,
                message=f"Failed to install Python dependencies: {str(e)}",
                exit_code=1,
                duration=duration
            )
    
    def install_frontend_dependencies(self) -> OperationResult:
        """Install frontend dependencies"""
        if not self.package_json.exists():
            return OperationResult(
                status=OperationStatus.SKIPPED,
                message=f"package.json not found: {self.package_json}"
            )
        
        if not self.check_command("npm"):
            return OperationResult(
                status=OperationStatus.SKIPPED,
                message="npm not found - skipping frontend installation"
            )
        
        start_time = time.time()
        self.logger.info("Installing frontend dependencies...")
        
        try:
            self.run_command(
                "npm install",
                cwd=self.frontend_dir,
                check=True,
                timeout=600  # 10 minute timeout
            )
            
            duration = time.time() - start_time
            return OperationResult(
                status=OperationStatus.SUCCESS,
                message="Frontend dependencies installed successfully",
                duration=duration
            )
        except Exception as e:
            duration = time.time() - start_time
            return OperationResult(
                status=OperationStatus.FAILED,
                message=f"Failed to install frontend dependencies: {str(e)}",
                exit_code=1,
                duration=duration
            )
    
    def install_python_package(self, editable: bool = True) -> OperationResult:
        """Install the Python package itself"""
        setup_py = self.project_root / "setup.py"
        pyproject_toml = self.project_root / "pyproject.toml"
        
        if not setup_py.exists() and not pyproject_toml.exists():
            return OperationResult(
                status=OperationStatus.SKIPPED,
                message="No setup.py or pyproject.toml found - skipping package installation"
            )
        
        self.logger.info("Installing Python package...")
        start_time = time.time()
        
        try:
            pip_cmd = self.get_pip_command() if self.venv_path.exists() else "pip"
            install_flag = "-e" if editable else ""
            
            if pyproject_toml.exists():
                self.run_command(
                    f"{pip_cmd} install {install_flag} .",
                    check=True,
                    timeout=300
                )
            else:
                self.run_command(
                    f"{pip_cmd} install {install_flag} .",
                    check=True,
                    timeout=300
                )
            
            duration = time.time() - start_time
            return OperationResult(
                status=OperationStatus.SUCCESS,
                message="Python package installed successfully",
                duration=duration
            )
        except Exception as e:
            duration = time.time() - start_time
            return OperationResult(
                status=OperationStatus.FAILED,
                message=f"Failed to install Python package: {str(e)}",
                exit_code=1,
                duration=duration
            )
    
    def execute(
        self,
        create_venv: bool = True,
        install_python: bool = True,
        install_frontend: bool = True,
        install_package: bool = False,
        upgrade_pip: bool = True,
        use_venv: bool = True,
        force_venv: bool = False,
        **kwargs
    ) -> OperationResult:
        """
        Execute installation
        
        Args:
            create_venv: Create virtual environment
            install_python: Install Python dependencies
            install_frontend: Install frontend dependencies
            install_package: Install the Python package itself
            upgrade_pip: Upgrade pip before installing
            use_venv: Use virtual environment if available
            force_venv: Force recreation of virtual environment
        """
        start_time = time.time()
        results = []
        
        self.logger.info("=" * 60)
        self.logger.info("Starting Installation")
        self.logger.info("=" * 60)
        
        # Check prerequisites
        prereq_result = self.check_prerequisites()
        if prereq_result.failed:
            return prereq_result
        results.append(("Prerequisites", prereq_result))
        
        # Create virtual environment
        if create_venv:
            venv_result = self.create_venv(force=force_venv)
            results.append(("Virtual Environment", venv_result))
            if venv_result.failed:
                return venv_result
        
        # Install Python dependencies
        if install_python:
            python_result = self.install_python_dependencies(
                upgrade_pip=upgrade_pip,
                use_venv=use_venv
            )
            results.append(("Python Dependencies", python_result))
            if python_result.failed:
                return python_result
        
        # Install frontend dependencies
        if install_frontend:
            frontend_result = self.install_frontend_dependencies()
            results.append(("Frontend Dependencies", frontend_result))
            # Don't fail if frontend install is skipped (npm might not be available)
        
        # Install package
        if install_package:
            package_result = self.install_python_package()
            results.append(("Python Package", package_result))
            # Don't fail if package install is skipped (no setup.py)
        
        # Summary
        duration = time.time() - start_time
        failed = [name for name, result in results if result.failed]
        skipped = [name for name, result in results if result.status == OperationStatus.SKIPPED]
        
        if failed:
            message = f"Installation completed with failures: {', '.join(failed)}"
            status = OperationStatus.FAILED
            exit_code = 1
        else:
            message = "Installation completed successfully"
            status = OperationStatus.SUCCESS
            exit_code = 0
        
        if skipped:
            message += f" (skipped: {', '.join(skipped)})"
        
        self.logger.info("=" * 60)
        self.logger.info("Installation Summary")
        self.logger.info("=" * 60)
        for name, result in results:
            status_icon = "✓" if result.success else "✗" if result.failed else "⊘"
            self.logger.info(f"{status_icon} {name}: {result.message}")
        self.logger.info(f"Total duration: {duration:.2f}s")
        self.logger.info("=" * 60)
        
        return OperationResult(
            status=status,
            message=message,
            details={"results": results, "duration": duration},
            exit_code=exit_code,
            duration=duration
        )


