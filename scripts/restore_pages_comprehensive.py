#!/usr/bin/env python3
"""
Comprehensive Page Restoration - IA Compliant
Checks current codebase AND commits, selects best version per route
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict
import re

COMMITS = {
    'stable': '3a154a6e6305fe9f3a760f44b1b10d73e1ed3256',
    'incremeents': '58cfc345630f68bf10909538aba48c12f87ce9df',
    'backup': '4acea80190121b8ab79d8cd1367166bcfead8bde',
}

BASE_DIR = Path(__file__).parent.parent
FRONTEND_PAGES = BASE_DIR / 'frontend/src/pages'
GUI_NAV_JSON = BASE_DIR / 'documentation/gui_nav_structure/gui_nav.latest.json'

def run_git(cmd: List[str]) -> Tuple[str, str, int]:
    result = subprocess.run(['git'] + cmd, cwd=BASE_DIR, capture_output=True, text=True, check=False)
    return result.stdout, result.stderr, result.returncode

def file_exists_in_commit(commit: str, path: str) -> bool:
    _, stderr, rc = run_git(['show', f'{commit}:{path}'])
    return rc == 0

def get_file_content(commit: str, path: str) -> Optional[str]:
    stdout, stderr, rc = run_git(['show', f'{commit}:{path}'])
    return stdout if rc == 0 else None

def score_page(content: str) -> int:
    """Score page completeness"""
    if not content:
        return -100
    score = 0
    cl = content.lower()
    
    # Execute wired (+3)
    if re.search(r'(apiClient\.|fetch\(|axios\.|useQuery|useMutation|execute|onExecute|handleExecute)', content):
        score += 3
    # Results rendering (+2)
    if re.search(r'(results|data\.map|table|chart|graph|renderresults)', cl):
        score += 2
    # Parameters (+1)
    if re.search(r'(parameters|params|inputs)', cl):
        score += 1
    # Config (+1)
    if re.search(r'\b(config|settings|options)\b', cl):
        score += 1
    # Environment (+1)
    if re.search(r'\b(environment|env|context)\b', cl):
        score += 1
    # Stubs (-2)
    if re.search(r'(todo|stub|placeholder|coming soon|not implemented)', cl, re.I):
        score -= 2
    return score

def route_to_component_path(route: str) -> List[str]:
    """Convert route to possible component paths"""
    path = route.strip('/')
    if not path:
        return ['frontend/src/pages/Dashboard.tsx']
    
    paths = []
    parts = path.split('/')
    
    # Direct mapping: /ai/advanced -> AiAdvanced.tsx
    filename = ''.join(p.capitalize().replace('-', '') for p in parts)
    paths.append(f'frontend/src/pages/{filename}.tsx')
    
    # Workspaces: /workspaces/dev/cicd -> WorkspacesDevCicd.tsx
    if path.startswith('workspaces/'):
        subparts = parts[1:]  # Skip 'workspaces'
        if len(subparts) >= 2:
            category = subparts[0].capitalize()
            feature = ''.join(p.capitalize().replace('-', '') for p in subparts[1:])
            paths.append(f'frontend/src/pages/Workspaces{category}{feature}.tsx')
        elif len(subparts) == 1:
            paths.append(f'frontend/src/pages/Workspaces{subparts[0].capitalize()}.tsx')
    
    # With subdirectories: /ai/capsules/builder -> Ai/Capsules/Builder.tsx or AiCapsulesBuilder.tsx
    if len(parts) > 2:
        # Flat: AiCapsulesBuilder
        paths.append(f'frontend/src/pages/{filename}.tsx')
        # Nested: Ai/Capsules/Builder
        nested = '/'.join(p.capitalize() for p in parts[:-1])
        file = parts[-1].capitalize().replace('-', '')
        paths.append(f'frontend/src/pages/{nested}/{file}.tsx')
    
    # Also try .ts, .jsx, .js variants
    variants = []
    for p in paths:
        variants.extend([
            p.replace('.tsx', '.ts'),
            p.replace('.tsx', '.jsx'),
            p.replace('.tsx', '.js'),
        ])
    paths.extend(variants)
    
    return list(set(paths))  # Dedupe

def find_page_in_location(location: str, paths: List[str], is_commit: bool = False) -> Optional[Tuple[str, str, int]]:
    """Find page in location (commit or filesystem) and return (path, content, score)"""
    for candidate_path in paths:
        if is_commit:
            if file_exists_in_commit(location, candidate_path):
                content = get_file_content(location, candidate_path)
                if content:
                    return (candidate_path, content, score_page(content))
        else:
            file_path = BASE_DIR / candidate_path
            if file_path.exists():
                try:
                    content = file_path.read_text(encoding='utf-8')
                    return (candidate_path, content, score_page(content))
                except:
                    pass
    return None

def build_comprehensive_inventory() -> Dict:
    """Build inventory checking both current codebase and commits"""
    print("Loading gui_nav.latest.json...")
    with open(GUI_NAV_JSON, 'r') as f:
        nav_data = json.load(f)
    
    all_routes = set()
    for edition, platforms in nav_data.items():
        for platform, categories in platforms.items():
            for category, features in categories.items():
                for feature in features:
                    all_routes.add(feature['path'])
    
    print(f"Found {len(all_routes)} routes to check")
    print("\nChecking pages in current codebase and commits...")
    
    inventory = {}
    stats = {'current': 0, 'commits': 0, 'missing': 0}
    
    for i, route in enumerate(sorted(all_routes), 1):
        if i % 50 == 0:
            print(f"  Processed {i}/{len(all_routes)} routes...")
        
        candidate_paths = route_to_component_path(route)
        best_path = None
        best_content = None
        best_score = -1000
        best_source = None
        
        # Check current codebase first
        result = find_page_in_location('', candidate_paths, is_commit=False)
        if result:
            path, content, score = result
            if score > best_score:
                best_path, best_content, best_score = path, content, score
                best_source = 'current'
                stats['current'] += 1
        
        # Check commits (priority order)
        for commit_name, commit_sha in COMMITS.items():
            result = find_page_in_location(commit_sha, candidate_paths, is_commit=True)
            if result:
                path, content, score = result
                if score > best_score:
                    best_path, best_content, best_score = path, content, score
                    best_source = commit_name
                    if best_source != 'current':
                        stats['commits'] += 1
        
        if not best_content:
            stats['missing'] += 1
        
        inventory[route] = {
            'route': route,
            'component_path': best_path,
            'source': best_source,
            'source_sha': COMMITS.get(best_source) if best_source in COMMITS else None,
            'score': best_score,
            'has_content': best_content is not None,
            'candidate_paths': candidate_paths[:3],  # Store first few for debugging
        }
    
    print(f"\nInventory Summary:")
    print(f"  Found in current codebase: {stats['current']}")
    print(f"  Found in commits: {stats['commits']}")
    print(f"  Missing: {stats['missing']}")
    print(f"  Total: {len(inventory)}")
    
    return inventory

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--save-inventory', action='store_true', help='Save inventory to JSON')
    args = parser.parse_args()
    
    print("=" * 80)
    print("Comprehensive Page Inventory - IA Compliant")
    print("=" * 80)
    print()
    
    inventory = build_comprehensive_inventory()
    
    if args.save_inventory:
        output_file = BASE_DIR / 'route_inventory_comprehensive.json'
        with open(output_file, 'w') as f:
            json.dump(inventory, f, indent=2)
        print(f"\nInventory saved to {output_file}")
    
    # Show summary by source
    by_source = defaultdict(int)
    for entry in inventory.values():
        source = entry.get('source', 'missing')
        by_source[source] += 1
    
    print("\nRoutes by source:")
    for source, count in sorted(by_source.items(), key=lambda x: (x[0] or '', x[1])):
        print(f"  {source or 'missing'}: {count}")

if __name__ == '__main__':
    main()

