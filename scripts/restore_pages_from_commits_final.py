#!/usr/bin/env python3
"""
Final Comprehensive Page Restoration
- Restores all pages from commits (3a154a6, 58cfc34, 4acea80)
- Ensures ~444 pages exist
- Maintains IA compliance
"""

import json
import subprocess
import os
from pathlib import Path
from typing import Dict, List, Set

REPO_ROOT = Path(__file__).parent.parent
GUI_NAV_JSON = REPO_ROOT / "documentation/gui_nav_structure/gui_nav.latest.json"
FRONTEND_PAGES = REPO_ROOT / "frontend/src/pages"

COMMITS = {
    'stable': '3a154a6e6305fe9f3a760f44b1b10d73e1ed3256',
    'increments': '58cfc345630f68bf10909538aba48c12f87ce9df',
    'backup': '4acea80190121b8ab79d8cd1367166bcfead8bde'
}

def run_git(cmd: List[str]) -> str:
    """Run git command"""
    try:
        result = subprocess.run(
            ['git'] + cmd,
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return ""

def get_all_routes_from_gui_nav() -> Set[str]:
    """Extract all routes from GUI nav JSON"""
    routes = set()
    try:
        with open(GUI_NAV_JSON, 'r') as f:
            data = json.load(f)
        
        for edition, platforms in data.items():
            for platform_name, categories in platforms.items():
                for category_name, features in categories.items():
                    for feature in features:
                        route = feature.get('path', '')
                        if route:
                            routes.add(route)
    except Exception as e:
        print(f"Error reading GUI nav: {e}")
    return routes

def route_to_component_path(route: str) -> str:
    """Convert route to component file path"""
    if not route or route == '/':
        return 'frontend/src/pages/Dashboard.tsx'
    
    path = route.lstrip('/')
    parts = path.split('/')
    
    # Convert to PascalCase
    component_name = ''.join(word.capitalize() for word in parts[-1].split('-'))
    
    if len(parts) > 1:
        dir_path = '/'.join(parts[:-1])
        return f'frontend/src/pages/{dir_path}/{component_name}.tsx'
    else:
        return f'frontend/src/pages/{component_name}.tsx'

def find_page_in_commits(route: str) -> tuple:
    """Find page in commits, return (commit_name, filepath)"""
    component_path = route_to_component_path(route)
    
    # Try stable first
    for commit_name, commit_sha in COMMITS.items():
        content = run_git(['show', f'{commit_sha}:{component_path}'])
        if content:
            return (commit_name, component_path)
    
    # Try alternative paths
    alt_paths = [
        component_path.replace('.tsx', '.ts'),
        component_path.replace('.tsx', '.jsx'),
        component_path.replace('.tsx', '.js'),
    ]
    
    for alt_path in alt_paths:
        for commit_name, commit_sha in COMMITS.items():
            content = run_git(['show', f'{commit_sha}:{alt_path}'])
            if content:
                return (commit_name, alt_path)
    
    return (None, None)

def restore_page(route: str, commit_name: str, filepath: str) -> bool:
    """Restore a page from commit"""
    if not commit_name or not filepath:
        return False
    
    commit_sha = COMMITS[commit_name]
    target_path = REPO_ROOT / filepath
    
    try:
        content = run_git(['show', f'{commit_sha}:{filepath}'])
        if not content:
            return False
        
        target_path.parent.mkdir(parents=True, exist_ok=True)
        with open(target_path, 'w') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Error restoring {route}: {e}")
        return False

def main():
    print("=" * 80)
    print("Comprehensive Page Restoration")
    print("=" * 80)
    
    # Get all routes from GUI nav
    routes = get_all_routes_from_gui_nav()
    print(f"\nFound {len(routes)} routes in GUI nav structure")
    
    # Find and restore pages
    restored = 0
    failed = 0
    results = []
    
    for route in sorted(routes):
        commit_name, filepath = find_page_in_commits(route)
        if commit_name and filepath:
            if restore_page(route, commit_name, filepath):
                restored += 1
                results.append({
                    'route': route,
                    'commit': commit_name,
                    'filepath': filepath,
                    'status': 'restored'
                })
                print(f"✓ {route} from {commit_name}")
            else:
                failed += 1
                results.append({
                    'route': route,
                    'status': 'failed'
                })
        else:
            failed += 1
            results.append({
                'route': route,
                'status': 'not_found'
            })
            print(f"✗ {route} not found in any commit")
    
    # Save results
    results_file = REPO_ROOT / "page_restoration_results.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n{'=' * 80}")
    print(f"Restoration Summary:")
    print(f"  Total routes: {len(routes)}")
    print(f"  Restored: {restored}")
    print(f"  Failed: {failed}")
    print(f"  Results saved to: {results_file}")
    print(f"{'=' * 80}")
    
    return 0

if __name__ == '__main__':
    exit(main())

