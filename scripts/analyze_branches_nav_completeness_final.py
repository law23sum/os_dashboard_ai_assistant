#!/usr/bin/env python3
"""
Analyze all branches to find which ones have the most complete navigation structure.
Counts platforms, categories, and features from gui_nav.latest.json files.
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple

def get_all_branches() -> List[str]:
    """Get all local branches."""
    result = subprocess.run(
        ['git', 'branch', '--list'],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent
    )
    branches = []
    for line in result.stdout.split('\n'):
        line = line.strip()
        if line and not line.startswith('*'):
            # Remove leading/trailing whitespace and + markers
            branch = line.lstrip('+').strip()
            if branch:
                branches.append(branch)
    return branches

def checkout_branch(branch: str) -> bool:
    """Checkout a branch (stash changes first)."""
    repo_root = Path(__file__).parent.parent
    try:
        # Stash any changes
        subprocess.run(['git', 'stash'], cwd=repo_root, capture_output=True)
        # Checkout branch
        result = subprocess.run(
            ['git', 'checkout', branch],
            cwd=repo_root,
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except Exception as e:
        print(f"Error checking out {branch}: {e}", file=sys.stderr)
        return False

def analyze_nav_file(file_path: Path) -> Tuple[int, int, int]:
    """Analyze a navigation JSON file and return (platforms, categories, features) counts."""
    if not file_path.exists():
        return (0, 0, 0)
    
    try:
        with open(file_path, 'r') as f:
            nav = json.load(f)
        
        platform_count = 0
        category_count = 0
        feature_count = 0
        
        for edition, platforms in nav.items():
            platform_count += len(platforms)
            for platform, categories in platforms.items():
                category_count += len(categories)
                for category, features in categories.items():
                    feature_count += len(features)
        
        return (platform_count, category_count, feature_count)
    except Exception as e:
        print(f"Error analyzing {file_path}: {e}", file=sys.stderr)
        return (0, 0, 0)

def analyze_branch(branch: str) -> Dict:
    """Analyze a single branch for navigation completeness."""
    repo_root = Path(__file__).parent.parent
    current_branch = subprocess.run(
        ['git', 'branch', '--show-current'],
        cwd=repo_root,
        capture_output=True,
        text=True
    ).stdout.strip()
    
    # Try to checkout the branch
    if not checkout_branch(branch):
        return {
            'branch': branch,
            'platforms': 0,
            'categories': 0,
            'features': 0,
            'total': 0,
            'error': 'Could not checkout'
        }
    
    # Check multiple possible locations for nav file
    nav_files = [
        repo_root / 'documentation' / 'gui_nav_structure' / 'gui_nav.latest.json',
        repo_root / 'frontend' / 'public' / 'gui_nav.latest.json',
    ]
    
    max_platforms = 0
    max_categories = 0
    max_features = 0
    
    for nav_file in nav_files:
        platforms, categories, features = analyze_nav_file(nav_file)
        max_platforms = max(max_platforms, platforms)
        max_categories = max(max_categories, categories)
        max_features = max(max_features, features)
    
    # Restore original branch
    if current_branch:
        checkout_branch(current_branch)
    
    total = max_platforms + max_categories + max_features
    
    return {
        'branch': branch,
        'platforms': max_platforms,
        'categories': max_categories,
        'features': max_features,
        'total': total,
        'error': None
    }

def main():
    """Main analysis function."""
    print("Analyzing branches for navigation completeness...")
    print("=" * 80)
    
    branches = get_all_branches()
    print(f"Found {len(branches)} branches to analyze\n")
    
    results = []
    for i, branch in enumerate(branches, 1):
        print(f"[{i}/{len(branches)}] Analyzing {branch}...", end=' ', flush=True)
        result = analyze_branch(branch)
        results.append(result)
        if result['error']:
            print(f"ERROR: {result['error']}")
        else:
            print(f"✓ {result['platforms']} platforms, {result['categories']} categories, {result['features']} features")
    
    # Sort by total (descending)
    results.sort(key=lambda x: x['total'], reverse=True)
    
    print("\n" + "=" * 80)
    print("RESULTS (sorted by total navigation items):")
    print("=" * 80)
    print(f"{'Branch':<40} {'Platforms':<12} {'Categories':<12} {'Features':<12} {'Total':<12}")
    print("-" * 80)
    
    for result in results[:20]:  # Top 20
        if not result['error']:
            print(f"{result['branch']:<40} {result['platforms']:<12} {result['categories']:<12} {result['features']:<12} {result['total']:<12}")
    
    # Save results to JSON
    output_file = Path(__file__).parent.parent / 'branch_nav_analysis_final.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nFull results saved to: {output_file}")
    
    # Identify best branches
    print("\n" + "=" * 80)
    print("RECOMMENDED BRANCHES FOR MERGE:")
    print("=" * 80)
    
    # Find branches with max platforms
    max_platforms = max(r['platforms'] for r in results if not r['error'])
    max_categories = max(r['categories'] for r in results if not r['error'])
    max_features = max(r['features'] for r in results if not r['error'])
    
    print(f"\nMax platforms: {max_platforms}")
    for r in results:
        if r['platforms'] == max_platforms and not r['error']:
            print(f"  - {r['branch']}")
    
    print(f"\nMax categories: {max_categories}")
    for r in results:
        if r['categories'] == max_categories and not r['error']:
            print(f"  - {r['branch']}")
    
    print(f"\nMax features: {max_features}")
    for r in results:
        if r['features'] == max_features and not r['error']:
            print(f"  - {r['branch']}")

if __name__ == '__main__':
    main()


