#!/usr/bin/env python3
"""
Analyze branches and merge them into incremeents branch.
Prioritizes maximum pages, categories, and platforms.
"""

import subprocess
import json
import os
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict

REPO_ROOT = Path(__file__).parent.parent

def run_git(cmd: List[str], check=True) -> str:
    """Run git command and return output."""
    try:
        result = subprocess.run(
            ['git'] + cmd,
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=check
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        if check:
            raise
        return ""

def get_all_branches() -> List[str]:
    """Get all local branches."""
    output = run_git(['branch', '--format=%(refname:short)'])
    return [b.strip() for b in output.split('\n') if b.strip()]

def count_pages_in_branch(branch: str) -> Dict[str, int]:
    """Count pages, categories, and platforms in a branch."""
    stats = {
        'pages': 0,
        'categories': 0,
        'platforms': 0,
        'tsx_files': 0
    }
    
    try:
        # Checkout branch temporarily
        run_git(['checkout', branch], check=False)
        
        # Count TSX files in pages directory
        pages_dir = REPO_ROOT / 'frontend' / 'src' / 'pages'
        if pages_dir.exists():
            tsx_files = list(pages_dir.rglob('*.tsx'))
            stats['tsx_files'] = len(tsx_files)
            stats['pages'] = len([f for f in tsx_files if f.name != 'RouteScaffold.tsx'])
        
        # Try to parse navigation structure
        nav_files = [
            REPO_ROOT / 'frontend' / 'src' / 'data' / 'iaManifest.complete.ts',
            REPO_ROOT / 'frontend' / 'src' / 'data' / 'iaManifest.ts',
            REPO_ROOT / 'documentation' / 'gui_nav_structure' / 'gui_nav.latest.json',
        ]
        
        for nav_file in nav_files:
            if nav_file.exists():
                content = nav_file.read_text()
                # Count platforms
                platform_matches = len(re.findall(r'id:\s*[\'"]', content))
                stats['platforms'] = max(stats['platforms'], platform_matches)
                # Count categories
                category_matches = len(re.findall(r'categories:\s*\[', content))
                stats['categories'] = max(stats['categories'], category_matches)
        
    except Exception as e:
        print(f"Error analyzing branch {branch}: {e}")
    
    return stats

def analyze_branches() -> Dict[str, Dict[str, int]]:
    """Analyze all branches and return stats."""
    branches = get_all_branches()
    # Exclude branches we want to keep
    keep_branches = {'develop', 'main', 'dying', 'incremeents'}
    branches = [b for b in branches if b not in keep_branches]
    
    print(f"Analyzing {len(branches)} branches...")
    
    branch_stats = {}
    current_branch = run_git(['branch', '--show-current'])
    
    for branch in branches:
        print(f"  Analyzing {branch}...")
        stats = count_pages_in_branch(branch)
        branch_stats[branch] = stats
        print(f"    Pages: {stats['pages']}, Categories: {stats['categories']}, Platforms: {stats['platforms']}")
    
    # Restore original branch
    if current_branch:
        run_git(['checkout', current_branch], check=False)
    
    return branch_stats

def find_best_branches(branch_stats: Dict[str, Dict[str, int]]) -> List[Tuple[str, int]]:
    """Find branches with most complete page sets."""
    # Score branches by total pages + categories + platforms
    scored = []
    for branch, stats in branch_stats.items():
        score = stats['pages'] * 10 + stats['categories'] * 5 + stats['platforms'] * 3
        scored.append((branch, score))
    
    # Sort by score descending
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored

def main():
    print("=== Branch Analysis and Merge Strategy ===\n")
    
    # Ensure we're on incremeents
    current = run_git(['branch', '--show-current'])
    if current != 'incremeents':
        print(f"Switching to incremeents branch (currently on {current})...")
        run_git(['checkout', 'incremeents'], check=False)
    
    # Analyze branches
    print("\n1. Analyzing branches...")
    branch_stats = analyze_branches()
    
    # Find best branches
    print("\n2. Ranking branches by completeness...")
    best_branches = find_best_branches(branch_stats)
    
    print("\nTop branches by completeness:")
    for i, (branch, score) in enumerate(best_branches[:10], 1):
        stats = branch_stats[branch]
        print(f"  {i}. {branch}: {score} points (Pages: {stats['pages']}, Categories: {stats['categories']}, Platforms: {stats['platforms']})")
    
    # Save analysis
    output_file = REPO_ROOT / 'branch_analysis_merge.json'
    with open(output_file, 'w') as f:
        json.dump({
            'branch_stats': branch_stats,
            'ranked_branches': best_branches,
            'timestamp': str(Path(__file__).stat().st_mtime)
        }, f, indent=2)
    
    print(f"\nAnalysis saved to {output_file}")
    print("\nNext steps:")
    print("  1. Review the analysis")
    print("  2. Merge top branches into incremeents")
    print("  3. Clean up merged branches")

if __name__ == '__main__':
    main()

