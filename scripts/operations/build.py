"""
Build operations for OS Dashboard AI Assistant
"""

import sys
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from enum import Enum

from .base import BaseOperation, OperationResult, OperationStatus, OperationError


class BuildTarget(Enum):
    """Build target enumeration"""
    WEB = "web"
    DESKTOP_LINUX = "desktop:linux"
    DESKTOP_WINDOWS = "desktop:windows"
    DESKTOP_MAC = "desktop:mac"
    DESKTOP_ALL = "desktop:all"
    ALL = "all"


class BuildOperation(BaseOperation):
    """Handles building of frontend and executables"""
    
    def check_prerequisites(self) -> OperationResult:
        """Check build prerequisites"""
        missing = []
        
        # Check Node.js
        if not self.check_command("node"):
            missing.append("Node.js")
        else:
            result = self.run_command("node --version", capture=True, check=False)
            if result.returncode == 0:
                version = result.stdout.strip()
                self.logger.info(f"Found Node.js: {version}")
        
        # Check npm
        if not self.check_command("npm"):
            missing.append("npm")
        else:
            result = self.run_command("npm --version", capture=True, check=False)
            if result.returncode == 0:
                version = result.stdout.strip()
                self.logger.info(f"Found npm: {version}")
        
        # Check frontend directory
        if not self.frontend_dir.exists():
            missing.append(f"Frontend directory: {self.frontend_dir}")
        
        if not (self.frontend_dir / "package.json").exists():
            missing.append(f"Frontend package.json: {self.frontend_dir / 'package.json'}")
        
        if missing:
            return OperationResult(
                status=OperationStatus.FAILED,
                message=f"Missing prerequisites: {', '.join(missing)}",
                exit_code=1
            )
        
        return OperationResult(
            status=OperationStatus.SUCCESS,
            message="Build prerequisites check passed"
        )
    
    def install_frontend_dependencies(self) -> OperationResult:
        """Ensure frontend dependencies are installed"""
        node_modules = self.frontend_dir / "node_modules"
        
        if node_modules.exists():
            self.logger.info("Frontend dependencies already installed")
            return OperationResult(
                status=OperationStatus.SUCCESS,
                message="Dependencies already installed"
            )
        
        self.logger.info("Installing frontend dependencies...")
        try:
            self.run_command(
                "npm install",
                cwd=self.frontend_dir,
                check=True,
                timeout=600
            )
            return OperationResult(
                status=OperationStatus.SUCCESS,
                message="Frontend dependencies installed"
            )
        except Exception as e:
            return OperationResult(
                status=OperationStatus.FAILED,
                message=f"Failed to install frontend dependencies: {str(e)}",
                exit_code=1
            )
    
    def build_web(self) -> OperationResult:
        """Build web version"""
        self.logger.info("Building web version...")
        start_time = time.time()
        
        try:
            self.run_command(
                "npm run build:web",
                cwd=self.frontend_dir,
                check=True,
                timeout=600
            )
            
            dist_dir = self.frontend_dir / "dist"
            if dist_dir.exists():
                duration = time.time() - start_time
                return OperationResult(
                    status=OperationStatus.SUCCESS,
                    message=f"Web build complete: {dist_dir}",
                    details={"output_dir": str(dist_dir)},
                    duration=duration
                )
            else:
                return OperationResult(
                    status=OperationStatus.FAILED,
                    message=f"Build completed but dist directory not found: {dist_dir}",
                    exit_code=1
                )
        except Exception as e:
            duration = time.time() - start_time
            return OperationResult(
                status=OperationStatus.FAILED,
                message=f"Web build failed: {str(e)}",
                exit_code=1,
                duration=duration
            )
    
    def build_desktop_linux(self) -> OperationResult:
        """Build Linux desktop app"""
        self.logger.info("Building Linux desktop app...")
        start_time = time.time()
        
        try:
            self.run_command(
                "npm run build:desktop:linux",
                cwd=self.frontend_dir,
                check=True,
                timeout=1800  # 30 minutes for desktop builds
            )
            
            dist_dir = self.frontend_dir / "dist-electron"
            duration = time.time() - start_time
            return OperationResult(
                status=OperationStatus.SUCCESS,
                message=f"Linux desktop build complete: {dist_dir}",
                details={"output_dir": str(dist_dir)},
                duration=duration
            )
        except Exception as e:
            duration = time.time() - start_time
            return OperationResult(
                status=OperationStatus.FAILED,
                message=f"Linux desktop build failed: {str(e)}",
                exit_code=1,
                duration=duration
            )
    
    def build_desktop_windows(self) -> OperationResult:
        """Build Windows desktop app"""
        self.logger.info("Building Windows desktop app...")
        start_time = time.time()
        
        try:
            self.run_command(
                "npm run build:desktop:windows",
                cwd=self.frontend_dir,
                check=True,
                timeout=1800  # 30 minutes for desktop builds
            )
            
            dist_dir = self.frontend_dir / "dist-electron"
            duration = time.time() - start_time
            return OperationResult(
                status=OperationStatus.SUCCESS,
                message=f"Windows desktop build complete: {dist_dir}",
                details={"output_dir": str(dist_dir)},
                duration=duration
            )
        except Exception as e:
            duration = time.time() - start_time
            return OperationResult(
                status=OperationStatus.FAILED,
                message=f"Windows desktop build failed: {str(e)}",
                exit_code=1,
                duration=duration
            )
    
    def build_desktop_mac(self) -> OperationResult:
        """Build macOS desktop app"""
        self.logger.info("Building macOS desktop app...")
        start_time = time.time()
        
        try:
            self.run_command(
                "npm run build:desktop:mac",
                cwd=self.frontend_dir,
                check=True,
                timeout=1800  # 30 minutes for desktop builds
            )
            
            dist_dir = self.frontend_dir / "dist-electron"
            duration = time.time() - start_time
            return OperationResult(
                status=OperationStatus.SUCCESS,
                message=f"macOS desktop build complete: {dist_dir}",
                details={"output_dir": str(dist_dir)},
                duration=duration
            )
        except Exception as e:
            duration = time.time() - start_time
            return OperationResult(
                status=OperationStatus.FAILED,
                message=f"macOS desktop build failed: {str(e)}",
                exit_code=1,
                duration=duration
            )
    
    def build_desktop_all(self) -> OperationResult:
        """Build desktop apps for all platforms"""
        self.logger.info("Building desktop apps for all platforms...")
        start_time = time.time()
        
        results = []
        
        # Build Linux
        linux_result = self.build_desktop_linux()
        results.append(("Linux", linux_result))
        
        # Build Windows
        windows_result = self.build_desktop_windows()
        results.append(("Windows", windows_result))
        
        # Build macOS
        mac_result = self.build_desktop_mac()
        results.append(("macOS", mac_result))
        
        duration = time.time() - start_time
        failed = [name for name, result in results if result.failed]
        
        if failed:
            return OperationResult(
                status=OperationStatus.FAILED,
                message=f"Desktop builds completed with failures: {', '.join(failed)}",
                details={"results": results},
                exit_code=1,
                duration=duration
            )
        
        return OperationResult(
            status=OperationStatus.SUCCESS,
            message="All desktop builds completed successfully",
            details={"results": results},
            duration=duration
        )
    
    def build_executable(self) -> OperationResult:
        """Build Python executable using PyInstaller"""
        build_script = self.project_root / "build-executable.py"
        
        if not build_script.exists():
            return OperationResult(
                status=OperationStatus.SKIPPED,
                message=f"Build script not found: {build_script}"
            )
        
        self.logger.info("Building Python executable...")
        start_time = time.time()
        
        try:
            self.run_command(
                f"{sys.executable} {build_script}",
                check=True,
                timeout=1800
            )
            
            dist_dir = self.project_root / "dist"
            duration = time.time() - start_time
            return OperationResult(
                status=OperationStatus.SUCCESS,
                message=f"Executable build complete: {dist_dir}",
                details={"output_dir": str(dist_dir)},
                duration=duration
            )
        except Exception as e:
            duration = time.time() - start_time
            return OperationResult(
                status=OperationStatus.FAILED,
                message=f"Executable build failed: {str(e)}",
                exit_code=1,
                duration=duration
            )
    
    def execute(
        self,
        target: str = "web",
        install_deps: bool = True,
        build_executable: bool = False,
        **kwargs
    ) -> OperationResult:
        """
        Execute build operation
        
        Args:
            target: Build target (web, desktop:linux, desktop:windows, desktop:mac, desktop:all, all)
            install_deps: Install frontend dependencies before building
            build_executable: Also build Python executable
        """
        import sys
        start_time = time.time()
        
        self.logger.info("=" * 60)
        self.logger.info("Starting Build")
        self.logger.info("=" * 60)
        
        # Check prerequisites
        prereq_result = self.check_prerequisites()
        if prereq_result.failed:
            return prereq_result
        
        # Install dependencies if needed
        if install_deps:
            deps_result = self.install_frontend_dependencies()
            if deps_result.failed:
                return deps_result
        
        results = []
        
        # Parse target
        try:
            build_target = BuildTarget(target)
        except ValueError:
            return OperationResult(
                status=OperationStatus.FAILED,
                message=f"Invalid build target: {target}. Valid: {[t.value for t in BuildTarget]}",
                exit_code=1
            )
        
        # Build based on target
        if build_target == BuildTarget.WEB:
            web_result = self.build_web()
            results.append(("Web", web_result))
        
        elif build_target == BuildTarget.DESKTOP_LINUX:
            # Build web first (desktop builds require it)
            web_result = self.build_web()
            results.append(("Web", web_result))
            if not web_result.failed:
                linux_result = self.build_desktop_linux()
                results.append(("Linux Desktop", linux_result))
        
        elif build_target == BuildTarget.DESKTOP_WINDOWS:
            web_result = self.build_web()
            results.append(("Web", web_result))
            if not web_result.failed:
                windows_result = self.build_desktop_windows()
                results.append(("Windows Desktop", windows_result))
        
        elif build_target == BuildTarget.DESKTOP_MAC:
            web_result = self.build_web()
            results.append(("Web", web_result))
            if not web_result.failed:
                mac_result = self.build_desktop_mac()
                results.append(("macOS Desktop", mac_result))
        
        elif build_target == BuildTarget.DESKTOP_ALL:
            web_result = self.build_web()
            results.append(("Web", web_result))
            if not web_result.failed:
                desktop_result = self.build_desktop_all()
                results.append(("All Desktop", desktop_result))
        
        elif build_target == BuildTarget.ALL:
            web_result = self.build_web()
            results.append(("Web", web_result))
            if not web_result.failed:
                desktop_result = self.build_desktop_all()
                results.append(("All Desktop", desktop_result))
        
        # Build executable if requested
        if build_executable:
            exe_result = self.build_executable()
            results.append(("Executable", exe_result))
        
        # Summary
        duration = time.time() - start_time
        failed = [name for name, result in results if result.failed]
        
        if failed:
            message = f"Build completed with failures: {', '.join(failed)}"
            status = OperationStatus.FAILED
            exit_code = 1
        else:
            message = "Build completed successfully"
            status = OperationStatus.SUCCESS
            exit_code = 0
        
        self.logger.info("=" * 60)
        self.logger.info("Build Summary")
        self.logger.info("=" * 60)
        for name, result in results:
            status_icon = "✓" if result.success else "✗" if result.failed else "⊘"
            self.logger.info(f"{status_icon} {name}: {result.message}")
        self.logger.info(f"Total duration: {duration:.2f}s")
        self.logger.info("=" * 60)
        
        return OperationResult(
            status=status,
            message=message,
            details={"results": results, "target": target},
            exit_code=exit_code,
            duration=duration
        )

