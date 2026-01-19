#!/usr/bin/env python3
"""
E2E Test Runner Script
Runs all end-to-end tests with configurable options.

Usage:
    python scripts/run_e2e_tests.py [OPTIONS]

Options:
    --smoke         Run only smoke tests (quick sanity checks)
    --regression    Run only regression tests
    --full          Run all tests (default)
    --verbose       Enable verbose output
    --html          Generate HTML report
    --coverage      Include coverage reporting
    --env ENV       Target environment (local, alpha, beta, prod)
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime


def get_project_root():
    """Get the project root directory."""
    return Path(__file__).parent.parent


def run_tests(
    test_type: str = "full",
    verbose: bool = False,
    html_report: bool = False,
    coverage: bool = False,
    environment: str = "local"
):
    """Run the E2E tests with specified options."""
    project_root = get_project_root()
    test_dir = project_root / "tests" / "e2e"
    
    # Base pytest command
    cmd = ["python", "-m", "pytest"]
    
    # Add test directory
    cmd.append(str(test_dir))
    
    # Add markers based on test type
    if test_type == "smoke":
        cmd.extend(["-m", "smoke"])
    elif test_type == "regression":
        cmd.extend(["-m", "regression"])
    # "full" runs all tests
    
    # Verbose output
    if verbose:
        cmd.append("-v")
    
    # HTML report
    if html_report:
        report_path = project_root / "test-reports" / f"e2e-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.html"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        cmd.extend(["--html", str(report_path), "--self-contained-html"])
    
    # Coverage
    if coverage:
        cmd.extend([
            "--cov=backend_api",
            "--cov=assistant_hub_gui",
            "--cov-report=term-missing",
            "--cov-report=html:coverage-report"
        ])
    
    # Set environment variable
    env = os.environ.copy()
    env["TEST_ENVIRONMENT"] = environment
    
    # Print command
    print(f"Running: {' '.join(cmd)}")
    print(f"Environment: {environment}")
    print("-" * 60)
    
    # Run tests
    result = subprocess.run(cmd, cwd=project_root, env=env)
    
    return result.returncode


def run_sanity_checks():
    """Run quick sanity checks before main tests."""
    project_root = get_project_root()
    
    print("=" * 60)
    print("RUNNING SANITY CHECKS")
    print("=" * 60)
    
    # Check imports
    print("\n[1/4] Checking imports...")
    try:
        sys.path.insert(0, str(project_root))
        from backend_api.main import app
        print("  ✓ Backend API imports correctly")
    except ImportError as e:
        print(f"  ✗ Backend API import failed: {e}")
        return False
    
    # Check database
    print("\n[2/4] Checking database...")
    try:
        from assistant_hub_gui.assistant_hub import db as hub_db
        conn = hub_db.init_db()
        conn.close()
        print("  ✓ Database initializes correctly")
    except Exception as e:
        print(f"  ✗ Database initialization failed: {e}")
        return False
    
    # Check test files exist
    print("\n[3/4] Checking test files...")
    test_dir = project_root / "tests" / "e2e"
    test_files = list(test_dir.glob("test_*.py"))
    if test_files:
        print(f"  ✓ Found {len(test_files)} test files")
    else:
        print("  ✗ No test files found")
        return False
    
    # Check pytest is installed
    print("\n[4/4] Checking pytest installation...")
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "--version"],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        print(f"  ✓ pytest is installed")
    else:
        print("  ✗ pytest is not installed")
        return False
    
    print("\n" + "=" * 60)
    print("SANITY CHECKS PASSED")
    print("=" * 60 + "\n")
    
    return True


def main():
    parser = argparse.ArgumentParser(description="Run E2E tests for AI OS")
    parser.add_argument("--smoke", action="store_true", help="Run only smoke tests")
    parser.add_argument("--regression", action="store_true", help="Run only regression tests")
    parser.add_argument("--full", action="store_true", help="Run all tests (default)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    parser.add_argument("--html", action="store_true", help="Generate HTML report")
    parser.add_argument("--coverage", action="store_true", help="Include coverage reporting")
    parser.add_argument("--env", default="local", choices=["local", "alpha", "beta", "prod"],
                        help="Target environment")
    parser.add_argument("--skip-sanity", action="store_true", help="Skip sanity checks")
    
    args = parser.parse_args()
    
    # Run sanity checks first
    if not args.skip_sanity:
        if not run_sanity_checks():
            print("Sanity checks failed. Fix issues before running tests.")
            sys.exit(1)
    
    # Determine test type
    if args.smoke:
        test_type = "smoke"
    elif args.regression:
        test_type = "regression"
    else:
        test_type = "full"
    
    print(f"\nRunning {test_type.upper()} tests...")
    print("-" * 60)
    
    exit_code = run_tests(
        test_type=test_type,
        verbose=args.verbose,
        html_report=args.html,
        coverage=args.coverage,
        environment=args.env
    )
    
    # Summary
    print("\n" + "=" * 60)
    if exit_code == 0:
        print("ALL TESTS PASSED ✓")
    else:
        print("SOME TESTS FAILED ✗")
    print("=" * 60)
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
