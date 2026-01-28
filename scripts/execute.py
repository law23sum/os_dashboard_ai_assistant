#!/usr/bin/env python3
"""
Unified execution orchestrator for OS Dashboard AI Assistant
Provides a single entry point for install, build, test, launch, and verify operations
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

# Add scripts directory to path for imports
scripts_dir = Path(__file__).parent
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))

from operations import (
    InstallOperation,
    BuildOperation,
    TestOperation,
    LaunchOperation,
    VerifyOperation,
    OperationResult,
    OperationStatus
)


def print_banner():
    """Print welcome banner"""
    print("=" * 60)
    print("  OS Dashboard AI Assistant - Unified Execution Pipeline")
    print("=" * 60)
    print()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Unified execution pipeline for OS Dashboard AI Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full installation
  python scripts/execute.py install

  # Build web version
  python scripts/execute.py build --target web

  # Run all tests
  python scripts/execute.py test --type all

  # Launch web development mode
  python scripts/execute.py launch --mode web

  # Verify installation and structure
  python scripts/execute.py verify

  # Full pipeline: install -> build -> test -> verify
  python scripts/execute.py pipeline
        """
    )
    
    # Common arguments
    parser.add_argument(
        "--project-root",
        type=Path,
        default=None,
        help="Project root directory (default: auto-detect)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Install command
    install_parser = subparsers.add_parser("install", help="Install dependencies")
    install_parser.add_argument("--no-venv", action="store_true", help="Don't create virtual environment")
    install_parser.add_argument("--no-python", action="store_true", help="Don't install Python dependencies")
    install_parser.add_argument("--no-frontend", action="store_true", help="Don't install frontend dependencies")
    install_parser.add_argument("--package", action="store_true", help="Install Python package itself")
    install_parser.add_argument("--force-venv", action="store_true", help="Force recreation of virtual environment")
    
    # Build command
    build_parser = subparsers.add_parser("build", help="Build application")
    build_parser.add_argument(
        "--target",
        default="web",
        choices=["web", "desktop:linux", "desktop:windows", "desktop:mac", "desktop:all", "all"],
        help="Build target (default: web)"
    )
    build_parser.add_argument("--no-deps", action="store_true", help="Don't install dependencies before building")
    build_parser.add_argument("--executable", action="store_true", help="Also build Python executable")
    
    # Test command
    test_parser = subparsers.add_parser("test", help="Run tests")
    test_parser.add_argument(
        "--type",
        default="all",
        choices=["all", "unit", "integration", "e2e", "frontend", "backend", "smoke", "regression"],
        help="Test type (default: all)"
    )
    test_parser.add_argument("--coverage", action="store_true", help="Generate coverage reports")
    test_parser.add_argument("--env", default="local", help="Test environment (for E2E tests)")
    test_parser.add_argument("--markers", nargs="+", help="Pytest markers")
    
    # Launch command
    launch_parser = subparsers.add_parser("launch", help="Launch application")
    launch_parser.add_argument(
        "--mode",
        default="web",
        choices=["web", "desktop", "web-build", "desktop-build", "orchestrator", "backend-only"],
        help="Launch mode (default: web)"
    )
    launch_parser.add_argument("--workspace", type=Path, help="Workspace root (for orchestrator)")
    launch_parser.add_argument("--host", default="127.0.0.1", help="Backend host")
    launch_parser.add_argument("--port", type=int, default=8000, help="Backend port")
    launch_parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    launch_parser.add_argument("--ui", action="store_true", help="Enable UI (for orchestrator)")
    
    # Verify command
    verify_parser = subparsers.add_parser("verify", help="Verify installation and setup")
    verify_parser.add_argument("--no-installation", action="store_true", help="Skip installation check")
    verify_parser.add_argument("--backend", action="store_true", help="Check backend health")
    verify_parser.add_argument("--frontend-build", action="store_true", help="Check frontend build")
    verify_parser.add_argument("--no-structure", action="store_true", help="Skip structure check")
    verify_parser.add_argument("--backend-url", default="http://127.0.0.1:8000", help="Backend URL")
    
    # Pipeline command
    pipeline_parser = subparsers.add_parser("pipeline", help="Run full pipeline: install -> build -> test -> verify")
    pipeline_parser.add_argument("--skip-install", action="store_true", help="Skip installation step")
    pipeline_parser.add_argument("--skip-build", action="store_true", help="Skip build step")
    pipeline_parser.add_argument("--skip-test", action="store_true", help="Skip test step")
    pipeline_parser.add_argument("--skip-verify", action="store_true", help="Skip verify step")
    pipeline_parser.add_argument("--build-target", default="web", help="Build target")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    print_banner()
    
    try:
        # Execute command
        if args.command == "install":
            op = InstallOperation(project_root=args.project_root, verbose=args.verbose)
            result = op.execute(
                create_venv=not args.no_venv,
                install_python=not args.no_python,
                install_frontend=not args.no_frontend,
                install_package=args.package,
                force_venv=args.force_venv
            )
            return result.exit_code
        
        elif args.command == "build":
            op = BuildOperation(project_root=args.project_root, verbose=args.verbose)
            result = op.execute(
                target=args.target,
                install_deps=not args.no_deps,
                build_executable=args.executable
            )
            return result.exit_code
        
        elif args.command == "test":
            op = TestOperation(project_root=args.project_root, verbose=args.verbose)
            result = op.execute(
                test_type=args.type,
                verbose=args.verbose,
                coverage=args.coverage,
                environment=args.env,
                markers=args.markers
            )
            return result.exit_code
        
        elif args.command == "launch":
            op = LaunchOperation(project_root=args.project_root, verbose=args.verbose)
            result = op.execute(
                mode=args.mode,
                workspace_root=args.workspace,
                host=args.host,
                port=args.port,
                reload=args.reload,
                ui=args.ui
            )
            return result.exit_code
        
        elif args.command == "verify":
            op = VerifyOperation(project_root=args.project_root, verbose=args.verbose)
            result = op.execute(
                check_installation=not args.no_installation,
                check_backend=args.backend,
                check_frontend_build=args.frontend_build,
                check_structure=not args.no_structure,
                backend_url=args.backend_url
            )
            return result.exit_code
        
        elif args.command == "pipeline":
            # Run full pipeline
            exit_code = 0
            
            # Install
            if not args.skip_install:
                print("\n" + "=" * 60)
                print("STEP 1/4: Installation")
                print("=" * 60)
                op = InstallOperation(project_root=args.project_root, verbose=args.verbose)
                result = op.execute()
                if result.failed:
                    print(f"\n❌ Installation failed: {result.message}")
                    return result.exit_code
                exit_code = max(exit_code, result.exit_code)
            
            # Build
            if not args.skip_build:
                print("\n" + "=" * 60)
                print("STEP 2/4: Build")
                print("=" * 60)
                op = BuildOperation(project_root=args.project_root, verbose=args.verbose)
                result = op.execute(target=args.build_target)
                if result.failed:
                    print(f"\n❌ Build failed: {result.message}")
                    return result.exit_code
                exit_code = max(exit_code, result.exit_code)
            
            # Test
            if not args.skip_test:
                print("\n" + "=" * 60)
                print("STEP 3/4: Tests")
                print("=" * 60)
                op = TestOperation(project_root=args.project_root, verbose=args.verbose)
                result = op.execute(test_type="all")
                if result.failed:
                    print(f"\n❌ Tests failed: {result.message}")
                    return result.exit_code
                exit_code = max(exit_code, result.exit_code)
            
            # Verify
            if not args.skip_verify:
                print("\n" + "=" * 60)
                print("STEP 4/4: Verification")
                print("=" * 60)
                op = VerifyOperation(project_root=args.project_root, verbose=args.verbose)
                result = op.execute()
                if result.failed:
                    print(f"\n❌ Verification failed: {result.message}")
                    return result.exit_code
                exit_code = max(exit_code, result.exit_code)
            
            print("\n" + "=" * 60)
            if exit_code == 0:
                print("✅ Pipeline completed successfully!")
            else:
                print("⚠️  Pipeline completed with warnings")
            print("=" * 60)
            
            return exit_code
        
        else:
            print(f"Unknown command: {args.command}")
            return 1
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user")
        return 130
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

