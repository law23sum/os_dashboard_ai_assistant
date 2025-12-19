#!/usr/bin/env python3
"""
Health Check Utility

Comprehensive health check for the Master Orchestrator system.
Verifies all components are working correctly.

Usage:
    python scripts/health_check.py [--verbose] [--fix]
"""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Tuple, Dict, Any

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


class HealthCheck:
    """Performs comprehensive health checks."""
    
    def __init__(self, verbose: bool = False, auto_fix: bool = False):
        self.verbose = verbose
        self.auto_fix = auto_fix
        self.checks_passed = 0
        self.checks_failed = 0
        self.warnings = 0
    
    def log(self, message: str, level: str = "info"):
        """Log a message."""
        if level == "error":
            print(f"❌ {message}")
        elif level == "warning":
            print(f"⚠️  {message}")
        elif level == "success":
            print(f"✅ {message}")
        else:
            print(f"ℹ️  {message}")
    
    def verbose_log(self, message: str):
        """Log only in verbose mode."""
        if self.verbose:
            print(f"   {message}")
    
    def check_python_version(self) -> bool:
        """Check Python version."""
        self.log("Checking Python version...")
        
        version = sys.version_info
        if version.major >= 3 and version.minor >= 8:
            self.log(f"Python {version.major}.{version.minor}.{version.micro}", "success")
            self.checks_passed += 1
            return True
        else:
            self.log(f"Python {version.major}.{version.minor} is too old (need 3.8+)", "error")
            self.checks_failed += 1
            return False
    
    def check_dependencies(self) -> bool:
        """Check required Python dependencies."""
        self.log("Checking Python dependencies...")
        
        required = [
            "fastapi",
            "uvicorn",
            "pathlib",
            "pytest",
        ]
        
        all_found = True
        for module in required:
            try:
                __import__(module)
                self.verbose_log(f"✓ {module}")
            except ImportError:
                self.log(f"Missing: {module}", "warning")
                self.warnings += 1
                all_found = False
                
                if self.auto_fix:
                    self.log(f"Installing {module}...", "info")
                    try:
                        subprocess.run(
                            [sys.executable, "-m", "pip", "install", module],
                            check=True,
                            capture_output=True,
                        )
                        self.log(f"Installed {module}", "success")
                    except subprocess.CalledProcessError:
                        self.log(f"Failed to install {module}", "error")
        
        if all_found:
            self.log("All dependencies found", "success")
            self.checks_passed += 1
        else:
            self.log("Some dependencies missing", "warning")
        
        return all_found
    
    def check_files(self) -> bool:
        """Check required files exist."""
        self.log("Checking required files...")
        
        required_files = [
            "os_dashboard_ai_assistant.py",
            "start_ui.py",
            "scripts/codex_spawner.py",
            "scripts/interactive_shell.py",
            "scripts/self_healing_engine.py",
            "scripts/ai_auto_fix.py",
            "backend_api/main.py",
            "backend_api/routers/orchestrator.py",
        ]
        
        all_found = True
        for file_path in required_files:
            full_path = REPO_ROOT / file_path
            if full_path.exists():
                self.verbose_log(f"✓ {file_path}")
            else:
                self.log(f"Missing: {file_path}", "error")
                self.checks_failed += 1
                all_found = False
        
        if all_found:
            self.log("All required files found", "success")
            self.checks_passed += 1
        
        return all_found
    
    def check_directories(self) -> bool:
        """Check required directories exist."""
        self.log("Checking directories...")
        
        required_dirs = [
            "logs",
            "scripts",
            "backend_api",
            "frontend",
        ]
        
        all_found = True
        for dir_path in required_dirs:
            full_path = REPO_ROOT / dir_path
            if full_path.exists() and full_path.is_dir():
                self.verbose_log(f"✓ {dir_path}")
            else:
                self.log(f"Missing: {dir_path}", "warning")
                self.warnings += 1
                
                if self.auto_fix:
                    full_path.mkdir(parents=True, exist_ok=True)
                    self.log(f"Created: {dir_path}", "success")
                else:
                    all_found = False
        
        if all_found:
            self.log("All directories found", "success")
            self.checks_passed += 1
        
        return all_found
    
    def check_orchestrator_running(self) -> bool:
        """Check if orchestrator is running."""
        self.log("Checking orchestrator status...")
        
        status_file = REPO_ROOT / "logs" / "status_report.json"
        
        if not status_file.exists():
            self.log("Orchestrator not running (no status report)", "warning")
            self.warnings += 1
            return False
        
        try:
            # Check if file is recent (within last 10 minutes)
            age = time.time() - status_file.stat().st_mtime
            if age > 600:
                self.log(f"Status report is stale ({int(age/60)} minutes old)", "warning")
                self.warnings += 1
                return False
            
            with status_file.open("r") as f:
                status = json.load(f)
            
            total_projects = status.get("total_projects", 0)
            active_monitors = status.get("monitors", {}).get("running", 0) + status.get("monitors", {}).get("healthy", 0)
            
            self.log(f"Orchestrator running: {total_projects} projects, {active_monitors} monitors", "success")
            self.checks_passed += 1
            return True
            
        except Exception as e:
            self.log(f"Error reading status: {e}", "error")
            self.checks_failed += 1
            return False
    
    def check_api_running(self) -> bool:
        """Check if API is accessible."""
        self.log("Checking API status...")
        
        try:
            import urllib.request
            
            response = urllib.request.urlopen("http://localhost:8000/api/health", timeout=5)
            data = json.loads(response.read())
            
            if data.get("status") == "ok":
                self.log("API is running", "success")
                self.checks_passed += 1
                return True
            else:
                self.log("API returned unexpected status", "warning")
                self.warnings += 1
                return False
                
        except Exception as e:
            self.log(f"API not accessible: {e}", "warning")
            self.warnings += 1
            return False
    
    def check_permissions(self) -> bool:
        """Check file permissions."""
        self.log("Checking permissions...")
        
        executable_files = [
            "os_dashboard_ai_assistant.py",
            "start_ui.py",
            "launch_orchestrator.sh",
            "scripts/codex_spawner.py",
            "scripts/interactive_shell.py",
            "scripts/self_healing_engine.py",
            "scripts/ai_auto_fix.py",
        ]
        
        all_ok = True
        for file_path in executable_files:
            full_path = REPO_ROOT / file_path
            if not full_path.exists():
                continue
            
            if os.access(full_path, os.X_OK):
                self.verbose_log(f"✓ {file_path} is executable")
            else:
                self.log(f"Not executable: {file_path}", "warning")
                self.warnings += 1
                
                if self.auto_fix:
                    full_path.chmod(0o755)
                    self.log(f"Made executable: {file_path}", "success")
                else:
                    all_ok = False
        
        if all_ok:
            self.log("All permissions OK", "success")
            self.checks_passed += 1
        
        return all_ok
    
    def check_git_repositories(self) -> bool:
        """Check if .git is recognized."""
        self.log("Checking git configuration...")
        
        git_dir = REPO_ROOT / ".git"
        if git_dir.exists():
            self.log("Git repository detected", "success")
            self.checks_passed += 1
            return True
        else:
            self.log("Not a git repository", "warning")
            self.warnings += 1
            return False
    
    def run_all_checks(self) -> Tuple[int, int, int]:
        """Run all health checks."""
        print("=" * 80)
        print("🏥 Master Orchestrator Health Check")
        print("=" * 80)
        print()
        
        # Run checks
        self.check_python_version()
        print()
        
        self.check_dependencies()
        print()
        
        self.check_files()
        print()
        
        self.check_directories()
        print()
        
        self.check_permissions()
        print()
        
        self.check_git_repositories()
        print()
        
        self.check_orchestrator_running()
        print()
        
        self.check_api_running()
        print()
        
        # Summary
        print("=" * 80)
        print("📊 Summary")
        print("=" * 80)
        print(f"✅ Checks Passed: {self.checks_passed}")
        print(f"⚠️  Warnings: {self.warnings}")
        print(f"❌ Checks Failed: {self.checks_failed}")
        print()
        
        if self.checks_failed == 0:
            print("🎉 All critical checks passed!")
            if self.warnings > 0:
                print(f"⚠️  {self.warnings} warnings (non-critical)")
        else:
            print(f"❌ {self.checks_failed} critical checks failed")
            print("Please fix the issues above before running the orchestrator.")
        
        print("=" * 80)
        
        return self.checks_passed, self.warnings, self.checks_failed


def main():
    parser = argparse.ArgumentParser(
        description="Health check for Master Orchestrator system"
    )
    
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output",
    )
    
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Automatically fix issues where possible",
    )
    
    args = parser.parse_args()
    
    health = HealthCheck(verbose=args.verbose, auto_fix=args.fix)
    passed, warnings, failed = health.run_all_checks()
    
    # Exit code: 0 if all passed, 1 if any failed
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
