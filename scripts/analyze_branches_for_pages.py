#!/usr/bin/env python3
"""
Analyze branches to find those with the most complete page sets.
Counts platforms, categories, and features from frontend/src/pages.
"""

import subprocess
import json
import os
from pathlib import Path
from collections import defaultdict

def get_branches():
    """Get list of local branches to analyze."""
    result = subprocess.run(
        ['git', 'branch', '--format=%(refname:short)'],
        capture_output=True,
        text=True,
        cwd=os.getcwd()
    )
    branches = [b.strip() for b in result.stdout.strip().split('\n') if b.strip()]
    # Filter to branches we care about
    relevant = [b for b in branches if any(x in b.lower() for x in [
        'fix', 'integration', 'gui', 'restore', 'ia', 'merge', 'stable'
    ]) and b not in ['develop', 'main', 'dying', 'incremeents']]
    return relevant

def count_pages_in_branch(branch):
    """Count pages in a branch by checking out and counting files."""
    try:
        # Get list of page files from branch without checking out
        result = subprocess.run(
            ['git', 'ls-tree', '-r', '--name-only', branch, 'frontend/src/pages'],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        if result.returncode != 0:
            return None
        
        files = [f for f in result.stdout.strip().split('\n') if f and f.endswith('.tsx')]
        return len(files)
    except Exception as e:
        print(f"Error counting pages in {branch}: {e}")
        return None

def analyze_navigation_structure(branch):
    """Try to extract navigation structure from branch."""
    try:
        # Try to get navigation config
        result = subprocess.run(
            ['git', 'show', f'{branch}:frontend/src/navigation/context.tsx'],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        if result.returncode == 0:
            # Check if it has navigation structure
            has_nav = 'NavigationStructure' in result.stdout or 'NavPlatformItem' in result.stdout
            return has_nav
    except:
        pass
    return False

def main():
    print("Analyzing branches for page completeness...")
    
    branches = get_branches()
    print(f"Found {len(branches)} relevant branches to analyze")
    
    results = []
    
    for branch in branches:
        print(f"Analyzing {branch}...")
        page_count = count_pages_in_branch(branch)
        has_nav = analyze_navigation_structure(branch)
        
        if page_count is not None:
            results.append({
                'branch': branch,
                'page_count': page_count,
                'has_navigation': has_nav
            })
            print(f"  {branch}: {page_count} pages, nav={has_nav}")
    
    # Sort by page count descending
    results.sort(key=lambda x: x['page_count'], reverse=True)
    
    print("\n=== Top branches by page count ===")
    for r in results[:20]:
        print(f"{r['branch']}: {r['page_count']} pages")
    
    # Save results
    with open('branch_analysis.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to branch_analysis.json")
    return results

if __name__ == '__main__':
    main()
