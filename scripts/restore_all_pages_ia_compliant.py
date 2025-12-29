#!/usr/bin/env python3
"""
Comprehensive Page Restoration Script - IA Compliant
Restores all pages from source commits, scores them, and selects best versions.
Follows strict IA rules: Platforms → Categories → Features
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict

# Source commits (priority order)
COMMITS = {
    'stable': '3a154a6e6305fe9f3a760f44b1b10d73e1ed3256',  # Best known good
    'incremeents': '58cfc345630f68bf10909538aba48c12f87ce9df',  # Styling/work
    'backup': '4acea80190121b8ab79d8cd1367166bcfead8bde',  # Backup (use only for missing)
}

BASE_DIR = Path(__file__).parent.parent
FRONTEND_PAGES = BASE_DIR / 'frontend/src/pages'
GUI_NAV_JSON = BASE_DIR / 'documentation/gui_nav_structure/gui_nav.latest.json'

def run_git(cmd: List[str], check=True) -> Tuple[str, str, int]:
    """Run git command and return stdout, stderr, returncode"""
    result = subprocess.run(
        ['git'] + cmd,
        cwd=BASE_DIR,
        capture_output=True,
        text=True,
        check=False
    )
    return result.stdout, result.stderr, result.returncode

def file_exists_in_commit(commit: str, path: str) -> bool:
    """Check if file exists in commit"""
    _, stderr, rc = run_git(['show', f'{commit}:{path}'])
    return rc == 0

def get_file_content(commit: str, path: str) -> Optional[str]:
    """Get file content from commit"""
    stdout, stderr, rc = run_git(['show', f'{commit}:{path}'])
    if rc == 0:
        return stdout
    return None

def list_files_in_dir(commit: str, dir_path: str) -> List[str]:
    """List all files in directory at commit"""
    stdout, stderr, rc = run_git(['ls-tree', '-r', '--name-only', commit, dir_path])
    if rc == 0:
        return [line.strip() for line in stdout.split('\n') if line.strip()]
    return []

def score_page(content: str) -> int:
    """Score a page based on completeness"""
    if not content:
        return -100  # Missing
    
    score = 0
    content_lower = content.lower()
    
    # Has Execute wired to API (+3)
    if any(marker in content for marker in [
        'apiClient.', 'fetch(', 'axios.', 'useQuery', 'useMutation',
        'execute', 'onExecute', 'handleExecute'
    ]):
        score += 3
    
    # Has Results rendering real data (+2)
    if any(marker in content_lower for marker in [
        'results', 'data.map', 'table', 'chart', 'graph',
        'renderresults', 'displayresults'
    ]):
        score += 2
    
    # Has Parameters section (+1)
    if any(marker in content_lower for marker in [
        'parameters', 'params', 'inputs', 'configuration'
    ]):
        score += 1
    
    # Has Config section (+1)
    if any(marker in content_lower for marker in [
        'config', 'settings', 'options'
    ]):
        score += 1
    
    # Has Environment section (+1)
    if any(marker in content_lower for marker in [
        'environment', 'env', 'context'
    ]):
        score += 1
    
    # Stubbed/TODO (-2)
    if any(marker in content_lower for marker in [
        '// todo', '//todo', '# todo', '#todo',
        'stub', 'placeholder', 'coming soon', 'not implemented'
    ]):
        score -= 2
    
    # Dead links (-2)
    if content.count('404') > 2 or content.count('not found') > 2:
        score -= 2
    
    return score

def find_page_component_path(route_path: str) -> str:
    """Convert route path to component file path"""
    # Remove leading slash
    path = route_path.lstrip('/')
    if not path or path == '':
        return 'frontend/src/pages/Dashboard.tsx'
    
    # Convert to PascalCase component name
    parts = path.split('/')
    filename = ''.join(part.capitalize().replace('-', '') for part in parts)
    
    # Handle special cases
    if path.startswith('workspaces/'):
        # /workspaces/dev -> WorkspacesDev.tsx
        subparts = path.split('/')
        if len(subparts) >= 2:
            category = subparts[1]
            if len(subparts) > 2:
                feature = ''.join(p.capitalize().replace('-', '') for p in subparts[2:])
                return f'frontend/src/pages/Workspaces{category.capitalize()}{feature}.tsx'
            else:
                return f'frontend/src/pages/Workspaces{category.capitalize()}.tsx'
    
    # Default pattern
    return f'frontend/src/pages/{filename}.tsx'

def load_gui_nav() -> Dict:
    """Load gui_nav.latest.json"""
    with open(GUI_NAV_JSON, 'r') as f:
        return json.load(f)

def build_route_inventory() -> Dict[str, Dict]:
    """Build inventory of all routes and their best commit versions"""
    print("Building route inventory from gui_nav.latest.json...")
    
    nav_data = load_gui_nav()
    inventory = {}
    
    # Collect all routes
    all_routes = set()
    for edition, platforms in nav_data.items():
        for platform, categories in platforms.items():
            for category, features in categories.items():
                for feature in features:
                    route_path = feature['path']
                    all_routes.add(route_path)
    
    print(f"Found {len(all_routes)} routes in gui_nav.latest.json")
    
    # Score each route across commits
    for route_path in sorted(all_routes):
        component_path = find_page_component_path(route_path)
        
        best_commit = None
        best_score = -1000
        best_content = None
        
        # Try commits in priority order
        for commit_name, commit_sha in COMMITS.items():
            if file_exists_in_commit(commit_sha, component_path):
                content = get_file_content(commit_sha, component_path)
                if content:
                    score = score_page(content)
                    if score > best_score:
                        best_score = score
                        best_commit = commit_name
                        best_content = content
        
        # Also check alternative paths
        if not best_content:
            alt_paths = [
                component_path.replace('.tsx', '.ts'),
                component_path.replace('.tsx', '.jsx'),
                component_path.replace('.tsx', '.js'),
            ]
            for alt_path in alt_paths:
                for commit_name, commit_sha in COMMITS.items():
                    if file_exists_in_commit(commit_sha, alt_path):
                        content = get_file_content(commit_sha, alt_path)
                        if content:
                            score = score_page(content)
                            if score > best_score:
                                best_score = score
                                best_commit = commit_name
                                best_content = content
                                component_path = alt_path
                                break
        
        inventory[route_path] = {
            'route': route_path,
            'component_path': component_path,
            'best_commit': best_commit,
            'best_commit_sha': COMMITS.get(best_commit) if best_commit else None,
            'score': best_score,
            'has_content': best_content is not None,
        }
    
    return inventory

def restore_page(route_path: str, inventory_entry: Dict, dry_run: bool = False) -> bool:
    """Restore a single page from best commit"""
    if not inventory_entry['best_commit_sha']:
        print(f"  ⚠️  No source found for {route_path}")
        return False
    
    component_path = inventory_entry['component_path']
    commit_sha = inventory_entry['best_commit_sha']
    
    # Ensure target directory exists
    target_file = BASE_DIR / component_path
    target_file.parent.mkdir(parents=True, exist_ok=True)
    
    if dry_run:
        print(f"  [DRY RUN] Would restore {component_path} from {commit_sha}")
        return True
    
    # Restore file
    stdout, stderr, rc = run_git(['restore', '--source', commit_sha, '--', component_path], check=False)
    
    if rc == 0:
        print(f"  ✅ Restored {component_path} from {inventory_entry['best_commit']}")
        return True
    else:
        # Try to get content and write manually
        content = get_file_content(commit_sha, component_path)
        if content:
            target_file.write_text(content, encoding='utf-8')
            print(f"  ✅ Restored {component_path} from {inventory_entry['best_commit']} (manual)")
            return True
        else:
            print(f"  ❌ Failed to restore {component_path}: {stderr}")
            return False

def main():
    """Main restoration process"""
    import argparse
    parser = argparse.ArgumentParser(description='Restore all pages from source commits')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be restored without making changes')
    parser.add_argument('--inventory-only', action='store_true', help='Only build inventory, do not restore')
    args = parser.parse_args()
    
    print("=" * 80)
    print("IA-Compliant Page Restoration")
    print("=" * 80)
    print()
    
    # Build inventory
    inventory = build_route_inventory()
    
    # Summary
    print()
    print("Inventory Summary:")
    print(f"  Total routes: {len(inventory)}")
    by_commit = defaultdict(int)
    for entry in inventory.values():
        if entry['best_commit']:
            by_commit[entry['best_commit']] += 1
        else:
            by_commit['missing'] += 1
    
    for commit, count in sorted(by_commit.items()):
        print(f"  {commit}: {count} routes")
    
    print()
    
    if args.inventory_only:
        # Save inventory to JSON
        output_file = BASE_DIR / 'route_inventory_ia.json'
        with open(output_file, 'w') as f:
            json.dump(inventory, f, indent=2)
        print(f"Inventory saved to {output_file}")
        return
    
    # Restore pages
    print("Restoring pages...")
    print()
    
    restored = 0
    failed = 0
    missing = 0
    
    for route_path in sorted(inventory.keys()):
        entry = inventory[route_path]
        print(f"Processing {route_path}...")
        
        if not entry['has_content']:
            print(f"  ⚠️  No source found, will need to create")
            missing += 1
        else:
            if restore_page(route_path, entry, dry_run=args.dry_run):
                restored += 1
            else:
                failed += 1
    
    print()
    print("=" * 80)
    print("Restoration Summary:")
    print(f"  ✅ Restored: {restored}")
    print(f"  ❌ Failed: {failed}")
    print(f"  ⚠️  Missing (need creation): {missing}")
    print("=" * 80)

if __name__ == '__main__':
    main()





