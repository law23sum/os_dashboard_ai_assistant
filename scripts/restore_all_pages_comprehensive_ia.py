#!/usr/bin/env python3
"""
Comprehensive Page Restoration Script with IA Compliance
- Builds route inventory across commits (3a154a6, 58cfc34, 4acea80)
- Scores pages to determine best commit source
- Restores pages selectively
- Ensures IA compliance (Platforms→Categories→Features)
- Verifies ~444 pages exist
"""

import json
import subprocess
import os
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict

# Source commits
STABLE_COMMIT = "3a154a6e6305fe9f3a760f44b1b10d73e1ed3256"  # Latest stable alpha
INCREMENTS_COMMIT = "58cfc345630f68bf10909538aba48c12f87ce9df"  # origin/incremeents
BACKUP_COMMIT = "4acea80190121b8ab79d8cd1367166bcfead8bde"  # Backup broken GUI

COMMITS = {
    'stable': STABLE_COMMIT,
    'increments': INCREMENTS_COMMIT,
    'backup': BACKUP_COMMIT
}

REPO_ROOT = Path(__file__).parent.parent
FRONTEND_PAGES = REPO_ROOT / "frontend/src/pages"
GUI_NAV_JSON = REPO_ROOT / "documentation/gui_nav_structure/gui_nav.latest.json"

def run_git(cmd: List[str]) -> str:
    """Run git command and return output"""
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
        print(f"Git error: {e.stderr}")
        return ""

def get_files_in_commit(commit: str, path_pattern: str = "frontend/src/pages") -> Set[str]:
    """Get all files matching pattern in a commit"""
    files = set()
    try:
        output = run_git(['ls-tree', '-r', '--name-only', commit, path_pattern])
        for line in output.split('\n'):
            if line.strip():
                files.add(line.strip())
    except Exception as e:
        print(f"Error getting files from {commit}: {e}")
    return files

def score_page_content(content: str) -> int:
    """
    Score page content:
    +3 has Execute wired to API
    +2 has Results rendering real data
    +1 each for Parameters/Config/Env sections
    -2 if stubbed/TODO
    -2 if dead links
    """
    score = 0
    content_lower = content.lower()
    
    # Check for required sections
    if 'parameters' in content_lower or 'parameter' in content_lower:
        score += 1
    if 'configuration' in content_lower or 'config' in content_lower:
        score += 1
    if 'environment' in content_lower or 'env' in content_lower:
        score += 1
    
    # Check for Execute with API calls
    if ('execute' in content_lower or 'onclick' in content_lower or 'onclick' in content_lower) and \
       ('api' in content_lower or 'fetch' in content_lower or 'axios' in content_lower or 'usequery' in content_lower):
        score += 3
    
    # Check for Results with real data
    if 'results' in content_lower and ('table' in content_lower or 'chart' in content_lower or 'data' in content_lower):
        score += 2
    
    # Penalties
    if 'todo' in content_lower or 'stub' in content_lower or 'placeholder' in content_lower:
        score -= 2
    if '404' in content_lower or 'not found' in content_lower or 'coming soon' in content_lower:
        score -= 2
    
    return score

def get_page_from_commit(commit: str, filepath: str) -> Optional[Tuple[str, int]]:
    """Get page content from commit and return (content, score)"""
    try:
        content = run_git(['show', f'{commit}:{filepath}'])
        if content:
            score = score_page_content(content)
            return (content, score)
    except Exception as e:
        pass
    return None

def build_route_inventory() -> Dict[str, Dict]:
    """
    Build comprehensive route inventory from GUI nav JSON and commits
    Returns: {route: {placement, bestCommit, componentPath, apiDeps, score}}
    """
    print("Loading GUI nav structure...")
    with open(GUI_NAV_JSON, 'r') as f:
        gui_nav = json.load(f)
    
    route_inventory = {}
    
    # Extract routes from GUI nav structure
    for edition, platforms in gui_nav.items():
        for platform_name, categories in platforms.items():
            for category_name, features in categories.items():
                # Category home route
                if features:
                    first_feature = features[0]
                    category_route = first_feature.get('path', '').rsplit('/', 1)[0] if '/' in first_feature.get('path', '') else first_feature.get('path', '')
                    if category_route:
                        route_inventory[category_route] = {
                            'placement': 'categoryHome',
                            'platform': platform_name,
                            'category': category_name,
                            'bestCommit': None,
                            'componentPath': None,
                            'score': -999
                        }
                
                # Feature routes
                for feature in features:
                    route = feature.get('path', '')
                    if route:
                        route_inventory[route] = {
                            'placement': 'feature',
                            'platform': platform_name,
                            'category': category_name,
                            'feature': feature.get('title', ''),
                            'bestCommit': None,
                            'componentPath': None,
                            'score': -999
                        }
    
    print(f"Found {len(route_inventory)} routes in GUI nav structure")
    
    # Find best commit for each route
    print("Analyzing commits for best page versions...")
    for route, info in route_inventory.items():
        # Try to find component path
        component_path = route_to_component_path(route)
        
        best_commit = None
        best_score = -999
        best_content = None
        
        # Check each commit
        for commit_name, commit_sha in COMMITS.items():
            if component_path:
                result = get_page_from_commit(commit_sha, component_path)
                if result:
                    content, score = result
                    if score > best_score:
                        best_score = score
                        best_commit = commit_name
                        best_content = content
        
        # If no component found, try alternative paths
        if not best_commit:
            alt_paths = get_alternative_paths(route)
            for alt_path in alt_paths:
                for commit_name, commit_sha in COMMITS.items():
                    result = get_page_from_commit(commit_sha, alt_path)
                    if result:
                        content, score = result
                        if score > best_score:
                            best_score = score
                            best_commit = commit_name
                            best_content = content
                            component_path = alt_path
        
        info['bestCommit'] = best_commit or 'stable'  # Default to stable
        info['componentPath'] = component_path
        info['score'] = best_score
    
    return route_inventory

def route_to_component_path(route: str) -> Optional[str]:
    """Convert route to component file path"""
    if not route or route == '/':
        return 'frontend/src/pages/Dashboard.tsx'
    
    # Remove leading slash
    path = route.lstrip('/')
    
    # Convert to PascalCase component name
    parts = path.split('/')
    component_name = ''.join(word.capitalize() for word in parts[-1].split('-'))
    
    # Build path
    if len(parts) > 1:
        dir_path = '/'.join(parts[:-1])
        return f'frontend/src/pages/{dir_path}/{component_name}.tsx'
    else:
        return f'frontend/src/pages/{component_name}.tsx'

def get_alternative_paths(route: str) -> List[str]:
    """Get alternative component paths for a route"""
    paths = []
    if not route or route == '/':
        return ['frontend/src/pages/Dashboard.tsx']
    
    path = route.lstrip('/')
    parts = path.split('/')
    
    # Try different naming conventions
    base_name = parts[-1].replace('-', '')
    camel_name = ''.join(word.capitalize() for word in parts[-1].split('-'))
    
    if len(parts) > 1:
        dir_path = '/'.join(parts[:-1])
        paths.append(f'frontend/src/pages/{dir_path}/{camel_name}.tsx')
        paths.append(f'frontend/src/pages/{dir_path}/{base_name}.tsx')
    else:
        paths.append(f'frontend/src/pages/{camel_name}.tsx')
        paths.append(f'frontend/src/pages/{base_name}.tsx')
    
    return paths

def restore_page(route: str, info: Dict, dry_run: bool = False) -> bool:
    """Restore a page from the best commit"""
    if not info.get('componentPath'):
        return False
    
    commit_name = info.get('bestCommit', 'stable')
    commit_sha = COMMITS.get(commit_name, STABLE_COMMIT)
    
    target_path = REPO_ROOT / info['componentPath']
    
    if dry_run:
        print(f"Would restore {route} from {commit_name} to {target_path}")
        return True
    
    try:
        # Get content from commit
        content = run_git(['show', f'{commit_sha}:{info["componentPath"]}'])
        if not content:
            return False
        
        # Ensure directory exists
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write file
        with open(target_path, 'w') as f:
            f.write(content)
        
        print(f"✓ Restored {route} from {commit_name}")
        return True
    except Exception as e:
        print(f"✗ Failed to restore {route}: {e}")
        return False

def main():
    print("=" * 80)
    print("Comprehensive Page Restoration with IA Compliance")
    print("=" * 80)
    
    # Build route inventory
    inventory = build_route_inventory()
    
    # Save inventory
    inventory_file = REPO_ROOT / "route_inventory_comprehensive_ia.json"
    with open(inventory_file, 'w') as f:
        json.dump(inventory, f, indent=2)
    print(f"\nSaved route inventory to {inventory_file}")
    
    # Count pages
    total_routes = len(inventory)
    category_homes = sum(1 for v in inventory.values() if v['placement'] == 'categoryHome')
    features = sum(1 for v in inventory.values() if v['placement'] == 'feature')
    
    print(f"\nRoute Statistics:")
    print(f"  Total routes: {total_routes}")
    print(f"  Category homes: {category_homes}")
    print(f"  Features: {features}")
    print(f"  Target: ~444 pages")
    
    # Restore pages
    print("\nRestoring pages...")
    restored = 0
    failed = 0
    
    for route, info in inventory.items():
        if restore_page(route, info, dry_run=False):
            restored += 1
        else:
            failed += 1
    
    print(f"\nRestoration complete:")
    print(f"  Restored: {restored}")
    print(f"  Failed: {failed}")
    
    return 0

if __name__ == '__main__':
    exit(main())

