#!/usr/bin/env python3
"""
Test Script for Unified Project Orchestrator System

Runs comprehensive tests to verify the unified system is working correctly.

Usage:
    python scripts/test_unified_system.py
"""

from __future__ import annotations

import sys
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_imports():
    """Test that all modules can be imported."""
    print("🧪 Testing imports...")
    try:
        sys.path.insert(0, str(REPO_ROOT))
        from scripts.unified_project_orchestrator import (
            UnifiedProjectOrchestrator,
            discover_git_repos,
            create_project_status,
        )
        from scripts.unified_terminal_shell import UnifiedTerminalShell
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False


def test_discovery():
    """Test project discovery."""
    print("\n🧪 Testing project discovery...")
    try:
        from scripts.unified_project_orchestrator import discover_git_repos
        
        repos = discover_git_repos(REPO_ROOT, max_depth=3)
        print(f"✅ Discovered {len(repos)} repositories")
        
        if repos:
            print(f"   Sample repos: {[r.name for r in repos[:3]]}")
        
        return True
    except Exception as e:
        print(f"❌ Discovery failed: {e}")
        return False


def test_orchestrator():
    """Test orchestrator initialization."""
    print("\n🧪 Testing orchestrator...")
    try:
        from scripts.unified_project_orchestrator import UnifiedProjectOrchestrator
        
        orchestrator = UnifiedProjectOrchestrator(
            root=REPO_ROOT,
            max_depth=3,
            auto_fix=False,
            daemon_mode=False,
        )
        
        orchestrator.discover_projects()
        report = orchestrator.generate_report()
        
        print(f"✅ Orchestrator initialized successfully")
        print(f"   Projects discovered: {report['total_projects']}")
        print(f"   Healthy: {report['summary'].get('healthy', 0)}")
        print(f"   With auto-fix: {report['summary'].get('with_autofix', 0)}")
        
        return True
    except Exception as e:
        print(f"❌ Orchestrator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_scripts_executable():
    """Test that scripts are executable."""
    print("\n🧪 Testing script executability...")
    scripts = [
        "scripts/unified_project_orchestrator.py",
        "scripts/unified_terminal_shell.py",
        "scripts/ai_auto_fix.py",
    ]
    
    all_ok = True
    for script_path in scripts:
        script = REPO_ROOT / script_path
        if script.exists():
            # Check if executable (on Unix)
            import os
            if os.access(script, os.X_OK):
                print(f"✅ {script_path} is executable")
            else:
                print(f"⚠️  {script_path} is not executable (will try to fix)")
                os.chmod(script, 0o755)
                print(f"   Fixed: {script_path} is now executable")
        else:
            print(f"❌ {script_path} not found")
            all_ok = False
    
    return all_ok


def test_backend_router():
    """Test backend router can be imported."""
    print("\n🧪 Testing backend router...")
    try:
        sys.path.insert(0, str(REPO_ROOT))
        from backend_api.routers import project_orchestrator
        
        print("✅ Backend router imported successfully")
        return True
    except Exception as e:
        print(f"❌ Backend router import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Unified Project Orchestrator System - Test Suite")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Discovery", test_discovery),
        ("Orchestrator", test_orchestrator),
        ("Script Executability", test_scripts_executable),
        ("Backend Router", test_backend_router),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} test crashed: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
