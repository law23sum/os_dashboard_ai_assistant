#!/usr/bin/env python3
"""
Comprehensive Route/Page Inventory Builder for Codex Restoration
Extracts ALL routes from gui_nav.latest.json, then finds best page version from 3 commits
"""

import json
import subprocess
import os
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from collections import defaultdict
import re

# Source commits
COMMITS = {
    'stable': '3a154a6e6305fe9f3a760f44b1b10d73e1ed3256',
    'increments': '58cfc345630f68bf10909538aba48c12f87ce9df',
    'backup': '4acea80190121b8ab79d8cd1367166bcfead8bde'
}

# Scoring weights
SCORE_EXECUTE_WIRED = 3
SCORE_RESULTS_REAL_DATA = 2
SCORE_PARAMETERS = 1
SCORE_CONFIG = 1
SCORE_ENV = 1
SCORE_STUB = -2
SCORE_DEAD_LINKS = -2

def run_git_command(cmd: List[str], cwd: str = None) -> str:
    """Run a git command and return output"""
    try:
        result = subprocess.run(
            ['git'] + cmd,
            cwd=cwd or os.getcwd(),
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return ""

def get_file_content(commit: str, filepath: str) -> Optional[str]:
    """Get file content from a commit"""
    try:
        output = run_git_command(['show', f'{commit}:{filepath}'])
        return output if output else None
    except:
        return None

def file_exists_in_commit(commit: str, filepath: str) -> bool:
    """Check if file exists in commit"""
    try:
        run_git_command(['cat-file', '-e', f'{commit}:{filepath}'])
        return True
    except:
        return False

def find_page_component_for_route(commit: str, route: str) -> Optional[str]:
    """Find page component file for a route in a commit"""
    # Try common patterns
    patterns = [
        f"frontend/src/pages/{route_to_filename(route)}",
        f"frontend/src/pages/{route_to_filename(route)}.tsx",
        f"frontend/src/pages/{route_to_filename(route)}.ts",
        f"frontend/src/pages/{route_to_filename(route)}.jsx",
        f"frontend/src/pages/{route_to_filename(route)}.js",
    ]
    
    # Also try nested paths
    if route.count('/') > 1:
        parts = route.strip('/').split('/')
        # Try various nested patterns
        nested_patterns = [
            f"frontend/src/pages/{'/'.join(parts)}.tsx",
            f"frontend/src/pages/{'/'.join(parts[:-1])}/{parts[-1]}.tsx",
            f"frontend/src/pages/{parts[0]}/{parts[-1]}.tsx",
        ]
        patterns.extend(nested_patterns)
    
    for pattern in patterns:
        if file_exists_in_commit(commit, pattern):
            return pattern
    
    # Search all page files
    try:
        output = run_git_command(['ls-tree', '-r', '--name-only', commit, 'frontend/src/pages'])
        files = output.split('\n')
        route_slug = route.strip('/').replace('/', '-').lower()
        
        for filepath in files:
            if filepath.endswith(('.tsx', '.ts', '.jsx', '.js')):
                filename = Path(filepath).stem.lower()
                # Fuzzy match
                if route_slug in filename or filename in route_slug:
                    return filepath
    except:
        pass
    
    return None

def route_to_filename(route: str) -> str:
    """Convert route to filename"""
    if route == '/' or route == '':
        return 'Dashboard'
    
    # Remove leading/trailing slashes
    route = route.strip('/')
    
    # Convert to PascalCase
    parts = route.split('/')
    filename = ''.join(word.capitalize() for word in parts if word)
    
    return filename

def score_page(content: str) -> int:
    """Score a page component based on completeness"""
    if not content:
        return -10  # Missing page
    
    score = 0
    
    # Check for Execute button/functionality wired to API
    if re.search(r'execute|onExecute|handleExecute|fetch.*execute', content, re.I):
        if re.search(r'api|fetch|axios|useQuery|useMutation', content, re.I):
            score += SCORE_EXECUTE_WIRED
    
    # Check for Results rendering real data
    if re.search(r'results|data.*table|chart|graph', content, re.I):
        if re.search(r'map\(|\.map\(|forEach|data\[', content):
            score += SCORE_RESULTS_REAL_DATA
    
    # Check for Parameters section
    if re.search(r'parameters|params|input.*field', content, re.I):
        score += SCORE_PARAMETERS
    
    # Check for Configuration section
    if re.search(r'config|configuration|settings', content, re.I):
        score += SCORE_CONFIG
    
    # Check for Environment section
    if re.search(r'environment|env|env\.|process\.env', content, re.I):
        score += SCORE_ENV
    
    # Penalize stubs/TODOs
    if re.search(r'stub|TODO|FIXME|placeholder|coming soon', content, re.I):
        score += SCORE_STUB
    
    # Penalize dead links
    if re.search(r'href=["\']#|onClick.*undefined|function.*\{\s*\}', content):
        score += SCORE_DEAD_LINKS
    
    return score

def extract_all_routes_from_gui_nav(gui_nav: Dict) -> List[Dict]:
    """Extract all routes from GUI nav structure with IA mapping"""
    routes = []
    
    for edition_name, platforms in gui_nav.items():
        if not isinstance(platforms, dict):
            continue
            
        for platform_name, categories in platforms.items():
            if not isinstance(categories, dict):
                continue
            
            for category_name, features in categories.items():
                if not isinstance(features, list):
                    continue
                
                # Category home route (first feature or inferred)
                category_home_route = None
                if features:
                    first_feature = features[0]
                    if isinstance(first_feature, dict) and 'path' in first_feature:
                        # Category home is typically the parent of the first feature
                        feature_path = first_feature['path']
                        parts = feature_path.rstrip('/').split('/')
                        if len(parts) >= 2:
                            category_home_route = '/'.join(parts[:-1]) or '/'
                        else:
                            category_home_route = feature_path
                
                # Add category home if we have one
                if category_home_route:
                    routes.append({
                        'route': category_home_route,
                        'platform': platform_name,
                        'category': category_name,
                        'feature': None,
                        'placement': 'categoryHome',
                        'title': category_name
                    })
                
                # Add all features
                for feature in features:
                    if isinstance(feature, dict) and 'path' in feature:
                        route = feature['path']
                        routes.append({
                            'route': route,
                            'platform': platform_name,
                            'category': category_name,
                            'feature': feature.get('title', ''),
                            'placement': 'feature',
                            'title': feature.get('title', '')
                        })
    
    return routes

def main():
    """Main execution"""
    print("=" * 80)
    print("Comprehensive Route Inventory Builder for Codex Restoration")
    print("=" * 80)
    
    # Load GUI structure
    doc_path = Path(__file__).parent.parent / 'documentation' / 'gui_nav_structure' / 'gui_nav.latest.json'
    
    if not doc_path.exists():
        print(f"ERROR: {doc_path} not found!")
        return
    
    with open(doc_path, 'r') as f:
        gui_nav = json.load(f)
    
    # Extract all routes
    print("\nExtracting routes from gui_nav.latest.json...")
    all_routes = extract_all_routes_from_gui_nav(gui_nav)
    print(f"  Found {len(all_routes)} routes")
    
    # Build inventory
    print("\nAnalyzing pages in commits...")
    inventory = {}
    
    for route_info in all_routes:
        route = route_info['route']
        candidates = {}
        
        for commit_name, commit_sha in COMMITS.items():
            filepath = find_page_component_for_route(commit_sha, route)
            
            if filepath:
                content = get_file_content(commit_sha, filepath)
                if content:
                    score = score_page(content)
                    candidates[commit_name] = {
                        'filepath': filepath,
                        'score': score,
                        'commit': commit_sha
                    }
        
        # Choose best commit
        if candidates:
            best = max(candidates.items(), key=lambda x: (x[1]['score'], 
                ['stable', 'increments', 'backup'].index(x[0])))
            best_name, best_data = best
        else:
            # No page found in any commit - will need to create
            best_name = 'stable'  # Default
            best_data = {
                'filepath': f"frontend/src/pages/{route_to_filename(route)}.tsx",
                'score': -10,
                'commit': COMMITS['stable']
            }
        
        inventory[route] = {
            'route': route,
            'title': route_info['title'],
            'platform': route_info['platform'],
            'category': route_info['category'],
            'feature': route_info['feature'],
            'placement': route_info['placement'],
            'bestCommit': best_name,
            'bestCommitSha': best_data['commit'],
            'filepath': best_data['filepath'],
            'score': best_data['score'],
            'candidates': {k: v['score'] for k, v in candidates.items()} if candidates else {}
        }
    
    # Save results
    output_dir = Path(__file__).parent.parent
    output_file = output_dir / 'route_inventory_codex.json'
    
    summary = {
        'total_routes': len(inventory),
        'by_commit': {
            name: sum(1 for r in inventory.values() if r['bestCommit'] == name)
            for name in COMMITS.keys()
        },
        'by_placement': {
            'categoryHome': sum(1 for r in inventory.values() if r.get('placement') == 'categoryHome'),
            'feature': sum(1 for r in inventory.values() if r.get('placement') == 'feature'),
        },
        'missing_pages': sum(1 for r in inventory.values() if not r.get('candidates'))
    }
    
    with open(output_file, 'w') as f:
        json.dump({
            'summary': summary,
            'routes': inventory
        }, f, indent=2)
    
    print(f"\n✓ Inventory saved to {output_file}")
    print(f"  Total routes: {summary['total_routes']}")
    print(f"  Category homes: {summary['by_placement']['categoryHome']}")
    print(f"  Features: {summary['by_placement']['feature']}")
    print(f"  Missing pages: {summary['missing_pages']}")
    print(f"\nBy commit:")
    for name, count in summary['by_commit'].items():
        print(f"  {name}: {count}")

if __name__ == '__main__':
    main()
