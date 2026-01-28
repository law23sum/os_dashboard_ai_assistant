"""
Test operations for OS Dashboard AI Assistant
"""

import sys
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from enum import Enum

from .base import BaseOperation, OperationResult, OperationStatus, OperationError


class TestType(Enum):
    """Test type enumeration"""
    ALL = "all"
    UNIT = "unit"
    INTEGRATION = "integration"
    E2E = "e2e"
    FRONTEND = "frontend"
    BACKEND = "backend"
    SMOKE = "smoke"
    REGRESSION = "regression"


class TestOperation(BaseOperation):
    """Handles test execution"""
    
    def check_prerequisites(self) -> OperationResult:
        """Check test prerequisites"""
        missing = []
        
        # Check pytest (for backend tests)
        if not self.check_command("pytest"):
            try:
                result = self.run_command(f"{sys.executable} -m pytest --version", capture=True, check=False)
                if result.returncode != 0:
                    missing.append("pytest")
            except Exception:
                missing.append("pytest")
        
        # Check frontend test setup (npm/node)
        frontend_has_tests = (self.frontend_dir / "package.json").exists()
        if frontend_has_tests:
            if not self.check_command("npm"):
                missing.append("npm (for frontend tests)")
        
        if missing:
            return OperationResult(
                status=OperationStatus.WARNING,
                message=f"Some test prerequisites missing: {', '.join(missing)}. Tests may be skipped."
            )
        
        return OperationResult(
            status=OperationStatus.SUCCESS,
            message="Test prerequisites check passed"
        )
    
    def run_backend_tests(
        self,
        test_type: TestType = TestType.ALL,
        verbose: bool = False,
        coverage: bool = False,
        markers: Optional[List[str]] = None
    ) -> OperationResult:
        """Run backend tests"""
        if not self.tests_dir.exists():
            return OperationResult(
                status=OperationStatus.SKIPPED,
                message=f"Tests directory not found: {self.tests_dir}"
            )
        
        self.logger.info("Running backend tests...")
        start_time = time.time()
        
        # Build pytest command
        pytest_cmd = f"{sys.executable} -m pytest"
        
        if verbose:
            pytest_cmd += " -v"
        
        # Add markers
        if markers:
            pytest_cmd += f" -m {' or '.join(markers)}"
        elif test_type == TestType.SMOKE:
            pytest_cmd += " -m smoke"
        elif test_type == TestType.REGRESSION:
            pytest_cmd += " -m regression"
        
        # Add coverage
        if coverage:
            pytest_cmd += " --cov=. --cov-report=term-missing --cov-report=html"
        
        # Add test directory
        pytest_cmd += f" {self.tests_dir}"
        
        try:
            result = self.run_command(
                pytest_cmd,
                check=False,
                timeout=1800  # 30 minutes
            )
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                return OperationResult(
                    status=OperationStatus.SUCCESS,
                    message="Backend tests passed",
                    exit_code=0,
                    duration=duration
                )
            else:
                return OperationResult(
                    status=OperationStatus.FAILED,
                    message=f"Backend tests failed (exit code: {result.returncode})",
                    exit_code=result.returncode,
                    duration=duration
                )
        except Exception as e:
            duration = time.time() - start_time
            return OperationResult(
                status=OperationStatus.FAILED,
                message=f"Backend tests failed: {str(e)}",
                exit_code=1,
                duration=duration
            )
    
    def run_frontend_tests(
        self,
        verbose: bool = False,
        coverage: bool = False,
        ui: bool = False
    ) -> OperationResult:
        """Run frontend tests"""
        if not (self.frontend_dir / "package.json").exists():
            return OperationResult(
                status=OperationStatus.SKIPPED,
                message=f"Frontend package.json not found: {self.frontend_dir / 'package.json'}"
            )
        
        if not self.check_command("npm"):
            return OperationResult(
                status=OperationStatus.SKIPPED,
                message="npm not found - skipping frontend tests"
            )
        
        self.logger.info("Running frontend tests...")
        start_time = time.time()
        
        # Build npm test command
        if ui:
            test_cmd = "npm run test:ui"
        elif coverage:
            test_cmd = "npm run test:coverage"
        else:
            test_cmd = "npm test"
        
        try:
            result = self.run_command(
                test_cmd,
                cwd=self.frontend_dir,
                check=False,
                timeout=1800  # 30 minutes
            )
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                return OperationResult(
                    status=OperationStatus.SUCCESS,
                    message="Frontend tests passed",
                    exit_code=0,
                    duration=duration
                )
            else:
                return OperationResult(
                    status=OperationStatus.FAILED,
                    message=f"Frontend tests failed (exit code: {result.returncode})",
                    exit_code=result.returncode,
                    duration=duration
                )
        except Exception as e:
            duration = time.time() - start_time
            return OperationResult(
                status=OperationStatus.FAILED,
                message=f"Frontend tests failed: {str(e)}",
                exit_code=1,
                duration=duration
            )
    
    def run_e2e_tests(
        self,
        environment: str = "local",
        verbose: bool = False
    ) -> OperationResult:
        """Run end-to-end tests"""
        e2e_script = self.scripts_dir / "run_e2e_tests.py"
        
        if not e2e_script.exists():
            return OperationResult(
                status=OperationStatus.SKIPPED,
                message=f"E2E test script not found: {e2e_script}"
            )
        
        self.logger.info(f"Running E2E tests (environment: {environment})...")
        start_time = time.time()
        
        cmd = f"{sys.executable} {e2e_script} --env {environment}"
        if verbose:
            cmd += " --verbose"
        
        try:
            result = self.run_command(
                cmd,
                check=False,
                timeout=3600  # 1 hour for E2E tests
            )
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                return OperationResult(
                    status=OperationStatus.SUCCESS,
                    message=f"E2E tests passed (environment: {environment})",
                    exit_code=0,
                    duration=duration
                )
            else:
                return OperationResult(
                    status=OperationStatus.FAILED,
                    message=f"E2E tests failed (exit code: {result.returncode})",
                    exit_code=result.returncode,
                    duration=duration
                )
        except Exception as e:
            duration = time.time() - start_time
            return OperationResult(
                status=OperationStatus.FAILED,
                message=f"E2E tests failed: {str(e)}",
                exit_code=1,
                duration=duration
            )
    
    def execute(
        self,
        test_type: str = "all",
        verbose: bool = False,
        coverage: bool = False,
        environment: str = "local",
        markers: Optional[List[str]] = None,
        **kwargs
    ) -> OperationResult:
        """
        Execute test operation
        
        Args:
            test_type: Test type (all, unit, integration, e2e, frontend, backend, smoke, regression)
            verbose: Enable verbose output
            coverage: Generate coverage reports
            environment: Test environment (for E2E tests)
            markers: Pytest markers to use
        """
        start_time = time.time()
        
        self.logger.info("=" * 60)
        self.logger.info("Starting Tests")
        self.logger.info("=" * 60)
        
        # Check prerequisites
        prereq_result = self.check_prerequisites()
        # Don't fail on warnings, just log them
        if prereq_result.status == OperationStatus.FAILED:
            return prereq_result
        
        # Parse test type
        try:
            test_enum = TestType(test_type)
        except ValueError:
            return OperationResult(
                status=OperationStatus.FAILED,
                message=f"Invalid test type: {test_type}. Valid: {[t.value for t in TestType]}",
                exit_code=1
            )
        
        results = []
        
        # Run tests based on type
        if test_enum == TestType.ALL:
            # Run both backend and frontend
            backend_result = self.run_backend_tests(
                test_type=TestType.ALL,
                verbose=verbose,
                coverage=coverage,
                markers=markers
            )
            results.append(("Backend", backend_result))
            
            frontend_result = self.run_frontend_tests(
                verbose=verbose,
                coverage=coverage
            )
            results.append(("Frontend", frontend_result))
        
        elif test_enum == TestType.BACKEND:
            backend_result = self.run_backend_tests(
                test_type=TestType.ALL,
                verbose=verbose,
                coverage=coverage,
                markers=markers
            )
            results.append(("Backend", backend_result))
        
        elif test_enum == TestType.FRONTEND:
            frontend_result = self.run_frontend_tests(
                verbose=verbose,
                coverage=coverage
            )
            results.append(("Frontend", frontend_result))
        
        elif test_enum == TestType.E2E:
            e2e_result = self.run_e2e_tests(
                environment=environment,
                verbose=verbose
            )
            results.append(("E2E", e2e_result))
        
        elif test_enum in [TestType.SMOKE, TestType.REGRESSION]:
            backend_result = self.run_backend_tests(
                test_type=test_enum,
                verbose=verbose,
                coverage=coverage,
                markers=markers
            )
            results.append((test_enum.value.title(), backend_result))
        
        # Summary
        duration = time.time() - start_time
        failed = [name for name, result in results if result.failed]
        skipped = [name for name, result in results if result.status == OperationStatus.SKIPPED]
        
        if failed:
            message = f"Tests completed with failures: {', '.join(failed)}"
            status = OperationStatus.FAILED
            exit_code = 1
        else:
            message = "All tests passed"
            status = OperationStatus.SUCCESS
            exit_code = 0
        
        if skipped:
            message += f" (skipped: {', '.join(skipped)})"
        
        self.logger.info("=" * 60)
        self.logger.info("Test Summary")
        self.logger.info("=" * 60)
        for name, result in results:
            status_icon = "✓" if result.success else "✗" if result.failed else "⊘"
            self.logger.info(f"{status_icon} {name}: {result.message}")
        self.logger.info(f"Total duration: {duration:.2f}s")
        self.logger.info("=" * 60)
        
        return OperationResult(
            status=status,
            message=message,
            details={"results": results, "test_type": test_type},
            exit_code=exit_code,
            duration=duration
        )


