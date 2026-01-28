#!/usr/bin/env python3
"""
Codex Route Inventory Builder
Builds a comprehensive route/page inventory across specified commits
"""

import subprocess
import json
import re
from pathlib import Path
from collections import defaultdict

# Source commits to harvest
SOURCE_COMMITS = {
    '4acea80': 'backup-broken-gui',
    '58cfc34': 'origin/incremeents',
    '3a154a6': 'stable-alpha'
}

def run_git_command(cmd):
    """Run a git command and return output"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd='/Users/chrisdixon/Projects/os_dashboard_ai_assistant')
    return result.stdout.strip()

def get_page_files_from_commit(commit_sha):
    """Get all page files from a specific commit"""
    cmd = f"git ls-tree -r --name-only {commit_sha} | grep -E '(frontend|ui)/.*/(pages|routes)/.*\\.(tsx?|jsx?)$' | grep -v test | grep -v '.d.ts'"
    output = run_git_command(cmd)
    return [line for line in output.split('\n') if line]

def get_route_files_from_commit(commit_sha):
    """Get route configuration files from a specific commit"""
    cmd = f"git ls-tree -r --name-only {commit_sha} | grep -E '(routes?|nav|gui_nav)\\.(tsx?|jsx?|json)$' | grep -v test"
    output = run_git_command(cmd)
    return [line for line in output.split('\n') if line]

def extract_route_from_path(file_path):
    """Extract likely route from file path"""
    # frontend/src/pages/Workspaces/Dev/Repos.tsx -> /workspaces/dev/repos
    match = re.search(r'pages/(.+)\.(tsx?|jsx?)$', file_path)
    if match:
        route_part = match.group(1)
        # Convert to lowercase and handle special cases
        parts = route_part.split('/')
        route = '/' + '/'.join(p.lower() for p in parts if p not in ['index', 'Index'])
        return route
    return None

def score_page_implementation(commit_sha, file_path):
    """Score a page implementation based on completeness"""
    try:
        cmd = f"git show {commit_sha}:{file_path}"
        content = run_git_command(cmd)
        
        score = 0
        
        # Positive scoring
        if 'fetch(' in content or 'axios' in content or 'useQuery' in content:
            score += 3  # Has API wiring
        if 'Results' in content or 'Chart' in content or 'Table' in content:
            score += 2  # Has results rendering
        if 'Parameters' in content or 'Config' in content:
            score += 1
        if 'Environment' in content or 'Execute' in content:
            score += 1
        
        # Negative scoring
        if 'TODO' in content or 'FIXME' in content:
            score -= 2
        if 'export default function' not in content and 'export function' not in content:
            score -= 2
        
        return score
    except:
        return -10  # File doesn't exist or error

def build_route_inventory():
    """Build comprehensive route inventory across all source commits"""
    inventory = defaultdict(lambda: {
        'route': None,
        'placement': None,  # 'categoryHome' or 'feature'
        'candidates': [],
        'bestCommit': None,
        'bestScore': -999,
        'componentPath': None
    })
    
    print("=" * 80)
    print("BUILDING ROUTE INVENTORY FROM SOURCE COMMITS")
    print("=" * 80)
    
    for commit_sha, commit_label in SOURCE_COMMITS.items():
        print(f"\n📦 Scanning commit: {commit_sha} ({commit_label})")
        
        page_files = get_page_files_from_commit(commit_sha)
        print(f"   Found {len(page_files)} page files")
        
        for file_path in page_files:
            route = extract_route_from_path(file_path)
            if not route:
                continue
            
            score = score_page_implementation(commit_sha, file_path)
            
            inventory[route]['route'] = route
            inventory[route]['candidates'].append({
                'commit': commit_sha,
                'label': commit_label,
                'path': file_path,
                'score': score
            })
            
            # Track best implementation
            if score > inventory[route]['bestScore']:
                inventory[route]['bestScore'] = score
                inventory[route]['bestCommit'] = commit_sha
                inventory[route]['componentPath'] = file_path
    
    print(f"\n📊 INVENTORY SUMMARY")
    print("=" * 80)
    print(f"Total unique routes found: {len(inventory)}")
    
    return dict(inventory)

def categorize_routes(inventory):
    """Categorize routes as category homes or features"""
    for route, data in inventory.items():
        # Simple heuristic: routes with 2 segments are likely category homes
        # routes with 3+ segments are features
        segments = [s for s in route.split('/') if s]
        if len(segments) <= 2:
            data['placement'] = 'categoryHome'
        else:
            data['placement'] = 'feature'
    
    return inventory

def save_inventory(inventory, output_path):
    """Save inventory to JSON file"""
    with open(output_path, 'w') as f:
        json.dump(inventory, f, indent=2)
    print(f"\n✅ Inventory saved to: {output_path}")

def print_summary(inventory):
    """Print summary of inventory"""
    category_homes = sum(1 for r in inventory.values() if r['placement'] == 'categoryHome')
    features = sum(1 for r in inventory.values() if r['placement'] == 'feature')
    
    print(f"\n📋 ROUTE BREAKDOWN")
    print("=" * 80)
    print(f"Category Homes: {category_homes}")
    print(f"Features: {features}")
    print(f"Total Routes: {len(inventory)}")
    
    # Show best commits distribution
    commit_counts = defaultdict(int)
    for route_data in inventory.values():
        if route_data['bestCommit']:
            commit_counts[route_data['bestCommit']] += 1
    
    print(f"\n📦 BEST IMPLEMENTATION BY COMMIT")
    print("=" * 80)
    for commit, count in sorted(commit_counts.items(), key=lambda x: -x[1]):
        label = SOURCE_COMMITS.get(commit, commit)
        print(f"{label}: {count} routes")

def main():
    inventory = build_route_inventory()
    inventory = categorize_routes(inventory)
    
    output_path = Path(__file__).parent.parent / 'route_inventory_codex.json'
    save_inventory(inventory, output_path)
    
    print_summary(inventory)
    
    print(f"\n✅ Route inventory complete!")
    print(f"   Use this data to selectively restore pages with:")
    print(f"   git restore --source <bestCommit> -- <componentPath>")

if __name__ == '__main__':
    main()

