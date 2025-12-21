#!/usr/bin/env python3
"""
Analyze all branches to find which ones have the most complete navigation structure.
Uses git show to read files without checking out branches.
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
            branch = line.lstrip('+').strip()
            if branch:
                branches.append(branch)
    return branches

def get_file_from_branch(branch: str, file_path: str) -> str:
    """Get file contents from a branch using git show."""
    repo_root = Path(__file__).parent.parent
    try:
        result = subprocess.run(
            ['git', 'show', f'{branch}:{file_path}'],
            cwd=repo_root,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return result.stdout
        return ""
    except Exception:
        return ""

def analyze_nav_json(nav_json_str: str) -> Tuple[int, int, int]:
    """Analyze navigation JSON string and return (platforms, categories, features) counts."""
    if not nav_json_str:
        return (0, 0, 0)
    
    try:
        nav = json.loads(nav_json_str)
        
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
        return (0, 0, 0)

def analyze_branch(branch: str) -> Dict:
    """Analyze a single branch for navigation completeness."""
    # Check multiple possible locations for nav file
    nav_files = [
        'documentation/gui_nav_structure/gui_nav.latest.json',
        'frontend/public/gui_nav.latest.json',
    ]
    
    max_platforms = 0
    max_categories = 0
    max_features = 0
    found_file = None
    
    for nav_file in nav_files:
        content = get_file_from_branch(branch, nav_file)
        if content:
            platforms, categories, features = analyze_nav_json(content)
            if platforms > 0 or categories > 0 or features > 0:
                max_platforms = max(max_platforms, platforms)
                max_categories = max(max_categories, categories)
                max_features = max(max_features, features)
                found_file = nav_file
    
    total = max_platforms + max_categories + max_features
    
    return {
        'branch': branch,
        'platforms': max_platforms,
        'categories': max_categories,
        'features': max_features,
        'total': total,
        'found_file': found_file,
        'error': None if found_file else 'No nav file found'
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
    
    valid_results = [r for r in results if not r['error']]
    for result in valid_results[:20]:  # Top 20
        print(f"{result['branch']:<40} {result['platforms']:<12} {result['categories']:<12} {result['features']:<12} {result['total']:<12}")
    
    # Save results to JSON
    output_file = Path(__file__).parent.parent / 'branch_nav_analysis_final.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nFull results saved to: {output_file}")
    
    # Identify best branches
    if valid_results:
        print("\n" + "=" * 80)
        print("RECOMMENDED BRANCHES FOR MERGE:")
        print("=" * 80)
        
        # Find branches with max platforms
        max_platforms = max(r['platforms'] for r in valid_results)
        max_categories = max(r['categories'] for r in valid_results)
        max_features = max(r['features'] for r in valid_results)
        
        print(f"\nMax platforms: {max_platforms}")
        for r in valid_results:
            if r['platforms'] == max_platforms:
                print(f"  - {r['branch']}")
        
        print(f"\nMax categories: {max_categories}")
        for r in valid_results:
            if r['categories'] == max_categories:
                print(f"  - {r['branch']}")
        
        print(f"\nMax features: {max_features}")
        for r in valid_results:
            if r['features'] == max_features:
                print(f"  - {r['branch']}")
        
        # Top 5 by total
        print(f"\nTop 5 branches by total navigation items:")
        for i, r in enumerate(valid_results[:5], 1):
            print(f"  {i}. {r['branch']}: {r['total']} items ({r['platforms']} platforms, {r['categories']} categories, {r['features']} features)")

if __name__ == '__main__':
    main()

