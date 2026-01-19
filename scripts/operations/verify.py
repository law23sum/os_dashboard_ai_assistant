"""
Verification operations for AI OS
"""

import sys
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

from .base import BaseOperation, OperationResult, OperationStatus, OperationError


class VerifyOperation(BaseOperation):
    """Handles verification and health checks"""
    
    def check_prerequisites(self) -> OperationResult:
        """Check verification prerequisites"""
        return OperationResult(
            status=OperationStatus.SUCCESS,
            message="Verification prerequisites check passed"
        )
    
    def verify_installation(self) -> OperationResult:
        """Verify that installation is correct"""
        self.logger.info("Verifying installation...")
        start_time = time.time()
        
        checks = []
        
        # Check Python packages
        required_packages = ["fastapi", "uvicorn", "pydantic"]
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
                checks.append((f"Python package: {package}", True))
            except ImportError:
                missing_packages.append(package)
                checks.append((f"Python package: {package}", False))
        
        # Check frontend dependencies
        node_modules = self.frontend_dir / "node_modules"
        if node_modules.exists():
            checks.append(("Frontend dependencies", True))
        else:
            checks.append(("Frontend dependencies", False))
        
        # Check build artifacts (optional)
        dist_dir = self.frontend_dir / "dist"
        if dist_dir.exists():
            checks.append(("Frontend build artifacts", True))
        else:
            checks.append(("Frontend build artifacts", False))  # Not required, just info
        
        # Summary
        failed = [name for name, passed in checks if not passed]
        duration = time.time() - start_time
        
        if missing_packages:
            return OperationResult(
                status=OperationStatus.FAILED,
                message=f"Missing required Python packages: {', '.join(missing_packages)}",
                details={"checks": checks},
                exit_code=1,
                duration=duration
            )
        
        return OperationResult(
            status=OperationStatus.SUCCESS,
            message="Installation verification passed",
            details={"checks": checks},
            duration=duration
        )
    
    def verify_backend_health(
        self,
        base_url: str = "http://127.0.0.1:8000",
        timeout: int = 5
    ) -> OperationResult:
        """Verify backend server health"""
        if not HAS_REQUESTS:
            return OperationResult(
                status=OperationStatus.SKIPPED,
                message="requests library not available - skipping backend health check",
                exit_code=0
            )
        
        self.logger.info(f"Verifying backend health at {base_url}...")
        start_time = time.time()
        
        checks = []
        
        try:
            # Check health endpoint
            health_url = f"{base_url}/api/orchestrator/health"
            try:
                response = requests.get(health_url, timeout=timeout)
                if response.status_code == 200:
                    checks.append(("Health endpoint", True))
                else:
                    checks.append(("Health endpoint", False))
            except requests.RequestException:
                checks.append(("Health endpoint", False))
            
            # Check API docs
            docs_url = f"{base_url}/docs"
            try:
                response = requests.get(docs_url, timeout=timeout)
                if response.status_code == 200:
                    checks.append(("API documentation", True))
                else:
                    checks.append(("API documentation", False))
            except requests.RequestException:
                checks.append(("API documentation", False))
            
            # Check status endpoint
            status_url = f"{base_url}/api/orchestrator/status"
            try:
                response = requests.get(status_url, timeout=timeout)
                if response.status_code == 200:
                    data = response.json()
                    checks.append(("Status endpoint", True))
                    checks.append((f"Status data: {len(str(data))} bytes", True))
                else:
                    checks.append(("Status endpoint", False))
            except requests.RequestException:
                checks.append(("Status endpoint", False))
            
        except Exception as e:
            return OperationResult(
                status=OperationStatus.FAILED,
                message=f"Backend health check failed: {str(e)}",
                details={"checks": checks},
                exit_code=1,
                duration=time.time() - start_time
            )
        
        failed = [name for name, passed in checks if not passed]
        duration = time.time() - start_time
        
        if failed:
            return OperationResult(
                status=OperationStatus.FAILED,
                message=f"Backend health check failed: {', '.join(failed)}",
                details={"checks": checks},
                exit_code=1,
                duration=duration
            )
        
        return OperationResult(
            status=OperationStatus.SUCCESS,
            message="Backend health check passed",
            details={"checks": checks, "base_url": base_url},
            duration=duration
        )
    
    def verify_frontend_build(self) -> OperationResult:
        """Verify frontend build artifacts"""
        self.logger.info("Verifying frontend build...")
        start_time = time.time()
        
        dist_dir = self.frontend_dir / "dist"
        
        if not dist_dir.exists():
            return OperationResult(
                status=OperationStatus.FAILED,
                message=f"Build directory not found: {dist_dir}. Run build first.",
                exit_code=1,
                duration=time.time() - start_time
            )
        
        checks = []
        
        # Check for index.html
        index_html = dist_dir / "index.html"
        checks.append(("index.html exists", index_html.exists()))
        
        # Check for assets directory
        assets_dir = dist_dir / "assets"
        checks.append(("assets directory exists", assets_dir.exists()))
        
        # Count files
        file_count = len(list(dist_dir.rglob("*")))
        checks.append((f"Total files in build: {file_count}", file_count > 0))
        
        failed = [name for name, passed in checks if not passed]
        duration = time.time() - start_time
        
        if failed:
            return OperationResult(
                status=OperationStatus.FAILED,
                message=f"Frontend build verification failed: {', '.join(failed)}",
                details={"checks": checks},
                exit_code=1,
                duration=duration
            )
        
        return OperationResult(
            status=OperationStatus.SUCCESS,
            message="Frontend build verification passed",
            details={"checks": checks, "build_dir": str(dist_dir)},
            duration=duration
        )
    
    def verify_project_structure(self) -> OperationResult:
        """Verify project structure"""
        self.logger.info("Verifying project structure...")
        start_time = time.time()
        
        required_paths = [
            ("Project root", self.project_root),
            ("Frontend directory", self.frontend_dir),
            ("Scripts directory", self.scripts_dir),
            ("Tests directory", self.tests_dir),
            ("Requirements file", self.project_root / "requirements.txt"),
            ("Frontend package.json", self.frontend_dir / "package.json"),
        ]
        
        checks = []
        for name, path in required_paths:
            exists = path.exists()
            checks.append((name, exists))
        
        failed = [name for name, passed in checks if not passed]
        duration = time.time() - start_time
        
        if failed:
            return OperationResult(
                status=OperationStatus.FAILED,
                message=f"Project structure verification failed: {', '.join(failed)}",
                details={"checks": checks},
                exit_code=1,
                duration=duration
            )
        
        return OperationResult(
            status=OperationStatus.SUCCESS,
            message="Project structure verification passed",
            details={"checks": checks},
            duration=duration
        )
    
    def execute(
        self,
        check_installation: bool = True,
        check_backend: bool = False,
        check_frontend_build: bool = False,
        check_structure: bool = True,
        backend_url: str = "http://127.0.0.1:8000",
        **kwargs
    ) -> OperationResult:
        """
        Execute verification operation
        
        Args:
            check_installation: Check installation
            check_backend: Check backend health
            check_frontend_build: Check frontend build artifacts
            check_structure: Check project structure
            backend_url: Backend URL for health checks
        """
        start_time = time.time()
        
        self.logger.info("=" * 60)
        self.logger.info("Starting Verification")
        self.logger.info("=" * 60)
        
        results = []
        
        # Check project structure
        if check_structure:
            structure_result = self.verify_project_structure()
            results.append(("Project Structure", structure_result))
            if structure_result.failed:
                return structure_result
        
        # Check installation
        if check_installation:
            install_result = self.verify_installation()
            results.append(("Installation", install_result))
            if install_result.failed:
                return install_result
        
        # Check frontend build
        if check_frontend_build:
            build_result = self.verify_frontend_build()
            results.append(("Frontend Build", build_result))
            # Don't fail overall if build check fails (build might not exist)
        
        # Check backend health
        if check_backend:
            backend_result = self.verify_backend_health(base_url=backend_url)
            results.append(("Backend Health", backend_result))
            # Don't fail overall if backend check fails (backend might not be running)
        
        # Summary
        duration = time.time() - start_time
        failed = [name for name, result in results if result.failed]
        
        if failed:
            message = f"Verification completed with failures: {', '.join(failed)}"
            status = OperationStatus.FAILED
            exit_code = 1
        else:
            message = "All verifications passed"
            status = OperationStatus.SUCCESS
            exit_code = 0
        
        self.logger.info("=" * 60)
        self.logger.info("Verification Summary")
        self.logger.info("=" * 60)
        for name, result in results:
            status_icon = "✓" if result.success else "✗" if result.failed else "⊘"
            self.logger.info(f"{status_icon} {name}: {result.message}")
        self.logger.info(f"Total duration: {duration:.2f}s")
        self.logger.info("=" * 60)
        
        return OperationResult(
            status=status,
            message=message,
            details={"results": results},
            exit_code=exit_code,
            duration=duration
        )

