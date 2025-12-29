#!/usr/bin/env python3
"""
Verify no duplicate routes between dropdown and sidebar.
"""

import re
import sys
from pathlib import Path
from typing import Dict, Set

REPO_ROOT = Path(__file__).parent.parent
FRONTEND_SRC = REPO_ROOT / "frontend" / "src"

def extract_all_routes() -> Dict[str, Set[str]]:
    """Extract routes from navigation files."""
    routes = {
        'dropdown': set(),
        'sidebar': set(),
        'all': set()
    }
    
    # Check pageRegistry
    page_registry = FRONTEND_SRC / "nav" / "pageRegistry.ts"
    if page_registry.exists():
        content = page_registry.read_text(encoding='utf-8')
        # Extract route keys: '/route': () => import(...)
        pattern = r"'([^']+)':\s*\(\)\s*=>"
        matches = re.findall(pattern, content)
        routes['all'].update(matches)
    
    # Check navigation structure
    nav_structure = FRONTEND_SRC / "data" / "navigationStructure.ts"
    if nav_structure.exists():
        content = nav_structure.read_text(encoding='utf-8')
        # Extract paths
        pattern = r'path:\s*["\']([^"\']+)["\']'
        matches = re.findall(pattern, content)
        routes['all'].update(matches)
    
    # Categorize routes
    for route in routes['all']:
        parts = route.strip('/').split('/')
        if len(parts) == 2:
            # Category home (dropdown)
            routes['dropdown'].add(route)
        elif len(parts) >= 3:
            # Feature (sidebar)
            routes['sidebar'].add(route)
    
    return routes

def verify_no_duplicates() -> tuple[bool, list[str]]:
    """Verify no duplicate routes."""
    errors = []
    
    routes = extract_all_routes()
    
    # Check for duplicates
    duplicates = routes['dropdown'] & routes['sidebar']
    
    if duplicates:
        errors.append(f"Found {len(duplicates)} duplicate routes:")
        for dup in sorted(duplicates)[:20]:
            errors.append(f"  - {dup}")
        if len(duplicates) > 20:
            errors.append(f"  ... and {len(duplicates) - 20} more")
    
    print(f"✓ Total routes: {len(routes['all'])}")
    print(f"✓ Dropdown routes (categories): {len(routes['dropdown'])}")
    print(f"✓ Sidebar routes (features): {len(routes['sidebar'])}")
    
    if duplicates:
        print(f"\n✗ Duplicates found: {len(duplicates)}")
    else:
        print(f"\n✓ No duplicates found")
    
    return len(duplicates) == 0, errors

def main():
    print("=" * 80)
    print("Duplicate Routes Verification")
    print("=" * 80)
    print()
    
    no_duplicates, issues = verify_no_duplicates()
    
    print()
    print("=" * 80)
    if no_duplicates:
        print("✅ No Duplicates: PASSED")
    else:
        print("❌ No Duplicates: FAILED")
        for issue in issues[:10]:
            print(f"   {issue}")
    print("=" * 80)
    
    sys.exit(0 if no_duplicates else 1)

if __name__ == '__main__':
    main()




