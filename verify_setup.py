#!/usr/bin/env python3
"""
Verification script to check that all endpoints are properly configured.
This script verifies the codebase without requiring all dependencies to be installed.
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent

def check_file_exists(file_path: str) -> bool:
    """Check if a file exists."""
    full_path = REPO_ROOT / file_path
    return full_path.exists()

def check_import_in_file(file_path: str, import_name: str) -> bool:
    """Check if an import statement exists in a file."""
    full_path = REPO_ROOT / file_path
    if not full_path.exists():
        return False
    
    try:
        content = full_path.read_text(encoding="utf-8")
        return import_name in content
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False

def check_router_included(file_path: str, router_name: str) -> bool:
    """Check if a router is included in the server."""
    full_path = REPO_ROOT / file_path
    if not full_path.exists():
        return False
    
    try:
        content = full_path.read_text(encoding="utf-8")
        # Check if router is imported
        import_pattern = f"import.*{router_name}"
        # Check if router is included
        include_pattern = f"app.include_router({router_name}"
        
        import re
        has_import = bool(re.search(import_pattern, content))
        has_include = bool(re.search(include_pattern, content))
        
        return has_import and has_include
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False

def main():
    print("=" * 70)
    print("OS DASHBOARD AI ASSISTANT - SETUP VERIFICATION")
    print("=" * 70)
    
    # Check critical files
    print("\n📂 Checking Critical Files:")
    print("-" * 70)
    
    critical_files = [
        "unified_launcher.py",
        "sdlc_automation.py",
        "start.sh",
        "START_HERE.md",
        "assistant_hub/api/server.py",
        "backend_api/routers/runtime_diagnostics.py",
        "backend_api/routers/personas.py",
        "backend_api/routers/search.py",
        "backend_api/routers/templates.py",
        "backend_api/routers/audit.py",
    ]
    
    all_files_exist = True
    for file_path in critical_files:
        exists = check_file_exists(file_path)
        status = "✅" if exists else "❌"
        print(f"  {status} {file_path}")
        if not exists:
            all_files_exist = False
    
    # Check router imports
    print("\n📦 Checking Router Imports in server.py:")
    print("-" * 70)
    
    routers = [
        ("audit_router", "backend_api.routers.audit"),
        ("search_router", "backend_api.routers.search"),
        ("templates_router", "backend_api.routers.templates"),
        ("runtime_router", "backend_api.routers.runtime_diagnostics"),
        ("personas_router", "backend_api.routers.personas"),
    ]
    
    all_imports_ok = True
    for router_var, router_module in routers:
        has_import = check_import_in_file(
            "assistant_hub/api/server.py",
            router_module.split(".")[-1]
        )
        status = "✅" if has_import else "❌"
        print(f"  {status} {router_var} ({router_module})")
        if not has_import:
            all_imports_ok = False
    
    # Check router inclusions
    print("\n🔌 Checking Router Inclusions in server.py:")
    print("-" * 70)
    
    router_includes = [
        ("audit_router.router", "/audit"),
        ("search_router.router", "/search"),
        ("templates_router.router", "/templates"),
        ("runtime_router.router", "runtime"),
        ("personas_router.router", "/personas"),
    ]
    
    all_includes_ok = True
    for router_include, prefix in router_includes:
        has_include = check_import_in_file(
            "assistant_hub/api/server.py",
            f"include_router({router_include}"
        )
        status = "✅" if has_include else "❌"
        print(f"  {status} {router_include} (prefix: {prefix})")
        if not has_include:
            all_includes_ok = False
    
    # Check for operations/summary endpoint
    print("\n🔍 Checking Custom Endpoints:")
    print("-" * 70)
    
    has_operations_summary = check_import_in_file(
        "assistant_hub/api/server.py",
        "/operations/summary"
    )
    status = "✅" if has_operations_summary else "❌"
    print(f"  {status} /operations/summary endpoint")
    
    # Summary
    print("\n" + "=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)
    
    if all_files_exist:
        print("✅ All critical files exist")
    else:
        print("❌ Some critical files are missing")
    
    if all_imports_ok:
        print("✅ All routers are imported")
    else:
        print("❌ Some routers are not imported")
    
    if all_includes_ok:
        print("✅ All routers are included")
    else:
        print("❌ Some routers are not included")
    
    if has_operations_summary:
        print("✅ Custom endpoints are present")
    else:
        print("⚠️  Some custom endpoints may be missing")
    
    print("\n" + "=" * 70)
    
    if all_files_exist and all_imports_ok and all_includes_ok:
        print("✅ VERIFICATION PASSED - Setup is complete!")
        print("\nYou can now start the application with:")
        print("  python unified_launcher.py --mode browser")
        print("  or")
        print("  ./start.sh browser")
        return 0
    else:
        print("⚠️  VERIFICATION FAILED - Please review the errors above")
        return 1

if __name__ == "__main__":
    sys.exit(main())
