#!/usr/bin/env python3
"""
Verify all routes are registered and navigation follows IA rules.
"""

import json
import re
from pathlib import Path
from typing import Set, Dict, List

def extract_routes_from_manifest(manifest_file: Path) -> Dict[str, Set[str]]:
    """Extract all routes from IA manifest."""
    with open(manifest_file, 'r') as f:
        content = f.read()
    
    routes = {
        'category_homes': set(),
        'features': set(),
        'all': set()
    }
    
    # Extract routes from TypeScript manifest
    # Look for homeRoute and route patterns
    home_routes = re.findall(r'homeRoute:\s*["\']([^"\']+)["\']', content)
    feature_routes = re.findall(r'route:\s*["\']([^"\']+)["\']', content)
    
    routes['category_homes'] = set(home_routes)
    routes['features'] = set(feature_routes)
    routes['all'] = routes['category_homes'] | routes['features']
    
    return routes

def check_routes_in_code(routes_file: Path, routes: Set[str]) -> Dict:
    """Check if routes are registered in routing code."""
    if not routes_file.exists():
        return {'error': f'Routes file not found: {routes_file}'}
    
    with open(routes_file, 'r') as f:
        content = f.read()
    
    found = set()
    missing = set()
    
    for route in routes:
        # Check if route appears in routes file
        if route in content or f'path="{route}"' in content or f"path='{route}'" in content:
            found.add(route)
        else:
            missing.add(route)
    
    return {
        'total': len(routes),
        'found': len(found),
        'missing': len(missing),
        'missing_routes': sorted(missing)
    }

def verify_ia_rules(manifest_file: Path) -> Dict:
    """Verify IA rules are followed in navigation components."""
    issues = []
    
    # Check PlatformNavIA
    platform_nav = Path(__file__).parent.parent / 'frontend' / 'src' / 'components' / 'PlatformNavIA.tsx'
    if platform_nav.exists():
        with open(platform_nav, 'r') as f:
            content = f.read()
        
        # Check that it only shows categories, not features
        if 'category.features' in content and 'dropdown' in content.lower():
            # Should only show categories in dropdown
            if 'features.map' in content or 'feature.map' in content:
                issues.append('PlatformNavIA: Features should NOT appear in dropdown')
        
        # Check that categories route to homeRoute
        if 'category.homeRoute' not in content:
            issues.append('PlatformNavIA: Categories should route to homeRoute')
    
    # Check CategorySidebarIA
    sidebar = Path(__file__).parent.parent / 'frontend' / 'src' / 'components' / 'CategorySidebarIA.tsx'
    if sidebar.exists():
        with open(sidebar, 'r') as f:
            content = f.read()
        
        # Should only show features
        if 'category' in content and 'dropdown' in content.lower():
            issues.append('CategorySidebarIA: Should only show features, not categories')
    
    return {
        'issues': issues,
        'passed': len(issues) == 0
    }

def main():
    """Main verification."""
    print("=" * 80)
    print("Route and Navigation Verification")
    print("=" * 80)
    
    manifest_file = Path(__file__).parent.parent / 'frontend' / 'src' / 'data' / 'iaManifest.ts'
    routes_file = Path(__file__).parent.parent / 'frontend' / 'src' / 'routesIA.tsx'
    
    if not manifest_file.exists():
        print(f"Error: Manifest file not found: {manifest_file}")
        return
    
    print(f"\n1. Extracting routes from manifest...")
    routes = extract_routes_from_manifest(manifest_file)
    
    print(f"   Category homes: {len(routes['category_homes'])}")
    print(f"   Features: {len(routes['features'])}")
    print(f"   Total routes: {len(routes['all'])}")
    
    print(f"\n2. Checking route registration...")
    route_check = check_routes_in_code(routes_file, routes['all'])
    
    if 'error' in route_check:
        print(f"   {route_check['error']}")
    else:
        print(f"   Found: {route_check['found']}/{route_check['total']}")
        print(f"   Missing: {route_check['missing']}")
        if route_check['missing_routes']:
            print(f"   Missing routes (first 10):")
            for route in route_check['missing_routes'][:10]:
                print(f"     - {route}")
    
    print(f"\n3. Verifying IA rules...")
    ia_check = verify_ia_rules(manifest_file)
    
    if ia_check['passed']:
        print("   ✓ All IA rules passed")
    else:
        print(f"   ✗ Found {len(ia_check['issues'])} issues:")
        for issue in ia_check['issues']:
            print(f"     - {issue}")
    
    print(f"\n{'='*80}")
    print("Verification complete!")
    
    # Summary
    all_passed = (
        route_check.get('missing', 0) == 0 and
        ia_check['passed']
    )
    
    if all_passed:
        print("✓ All checks passed!")
    else:
        print("⚠ Some issues found. See above for details.")

if __name__ == '__main__':
    main()

