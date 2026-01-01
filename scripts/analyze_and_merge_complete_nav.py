#!/usr/bin/env python3
"""
Analyze branches to find the most complete navigation structure
(platforms, categories, features) and merge them into incremeents
"""
import json
import subprocess
import os
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict

REPO_ROOT = Path(__file__).parent.parent

def run_git_command(cmd: List[str], check=True) -> str:
    """Run a git command and return output"""
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
        print(f"Error running git {' '.join(cmd)}: {e.stderr}")
        return ""

def get_all_branches() -> List[str]:
    """Get all local branches"""
    output = run_git_command(['branch', '--list'])
    branches = [b.strip().replace('*', '').strip() for b in output.split('\n') if b.strip()]
    return [b for b in branches if b and not b.startswith('(')]

def checkout_branch(branch: str) -> bool:
    """Checkout a branch"""
    print(f"Checking out {branch}...")
    result = run_git_command(['checkout', branch], check=False)
    return result is not None or branch in run_git_command(['branch', '--show-current'])

def count_pages_in_branch(branch: str) -> int:
    """Count page files in a branch"""
    checkout_branch(branch)
    pages_dir = REPO_ROOT / 'frontend' / 'src' / 'pages'
    if not pages_dir.exists():
        return 0
    
    page_files = list(pages_dir.rglob('*.tsx')) + list(pages_dir.rglob('*.ts'))
    return len([f for f in page_files if f.is_file()])

def analyze_nav_json(branch: str) -> Dict:
    """Analyze navigation JSON in a branch"""
    checkout_branch(branch)
    
    nav_files = [
        REPO_ROOT / 'frontend' / 'public' / 'gui_nav.latest.json',
        REPO_ROOT / 'documentation' / 'gui_nav_structure' / 'gui_nav.latest.json',
    ]
    
    for nav_file in nav_files:
        if nav_file.exists():
            try:
                with open(nav_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return analyze_nav_structure(data)
            except Exception as e:
                print(f"Error reading {nav_file} in {branch}: {e}")
    
    return {
        'platforms': 0,
        'categories': 0,
        'features': 0,
        'total_items': 0
    }

def analyze_nav_structure(data: Dict) -> Dict:
    """Analyze navigation structure and count platforms, categories, features"""
    platforms = set()
    categories = set()
    features = set()
    
    if isinstance(data, dict):
        # Check if it's the new structure (Edition -> Platform -> Category -> Features)
        for edition_name, edition_data in data.items():
            if isinstance(edition_data, dict):
                for platform_name, platform_data in edition_data.items():
                    platforms.add(f"{edition_name}::{platform_name}")
                    if isinstance(platform_data, dict):
                        for category_name, category_items in platform_data.items():
                            categories.add(f"{platform_name}::{category_name}")
                            if isinstance(category_items, list):
                                for item in category_items:
                                    if isinstance(item, dict):
                                        title = item.get('title', '')
                                        path = item.get('path', '')
                                        # First item is usually the category home
                                        if title and path:
                                            features.add(f"{category_name}::{path}")
                    elif isinstance(platform_data, list):
                        # Might be features directly under platform
                        for item in platform_data:
                            if isinstance(item, dict):
                                title = item.get('title', '')
                                path = item.get('path', '')
                                if title and path:
                                    features.add(f"{platform_name}::{path}")
    
    return {
        'platforms': len(platforms),
        'categories': len(categories),
        'features': len(features),
        'total_items': len(platforms) + len(categories) + len(features),
        'platform_list': sorted(platforms),
        'category_list': sorted(categories),
        'feature_list': sorted(features)
    }

def compare_branches() -> List[Tuple[str, Dict]]:
    """Compare all branches and rank them by completeness"""
    current_branch = run_git_command(['branch', '--show-current'])
    branches = get_all_branches()
    
    # Filter to relevant branches (exclude main, develop, dying, incremeents)
    exclude = {'main', 'develop', 'dying', 'incremeents'}
    candidate_branches = [b for b in branches if b not in exclude]
    
    results = []
    
    print(f"Analyzing {len(candidate_branches)} branches...")
    
    for branch in candidate_branches:
        print(f"\nAnalyzing {branch}...")
        nav_stats = analyze_nav_json(branch)
        page_count = count_pages_in_branch(branch)
        
        nav_stats['page_count'] = page_count
        nav_stats['branch'] = branch
        results.append((branch, nav_stats))
    
    # Restore original branch
    checkout_branch(current_branch)
    
    # Sort by total completeness (prioritize nav structure completeness)
    results.sort(key=lambda x: (
        x[1]['total_items'],
        x[1]['platforms'],
        x[1]['categories'],
        x[1]['features'],
        x[1]['page_count']
    ), reverse=True)
    
    return results

def merge_branch_safely(target_branch: str, source_branch: str) -> bool:
    """Merge a branch with strategy to preserve maximum content"""
    print(f"\nMerging {source_branch} into {target_branch}...")
    
    checkout_branch(target_branch)
    
    # Merge with strategy favoring maximum content
    result = run_git_command([
        'merge', source_branch,
        '--no-edit',
        '--strategy-option=ours'  # Prefer current branch, but we'll check conflicts
    ], check=False)
    
    # Check for conflicts
    conflicts = run_git_command(['diff', '--name-only', '--diff-filter=U'], check=False)
    if conflicts:
        print(f"Conflicts detected: {conflicts}")
        # For navigation files, prefer the source branch
        conflict_files = conflicts.split('\n')
        for file in conflict_files:
            if 'gui_nav' in file or 'navigation' in file.lower():
                print(f"Resolving {file} in favor of source branch...")
                run_git_command(['checkout', '--theirs', file], check=False)
                run_git_command(['add', file], check=False)
        
        # Try to complete merge
        try:
            run_git_command(['commit', '--no-edit'], check=False)
        except:
            pass
    
    return True

def main():
    print("=== Branch Analysis for Complete Navigation Structure ===\n")
    
    # Ensure we're on incremeents
    checkout_branch('incremeents')
    
    # Analyze branches
    results = compare_branches()
    
    print("\n=== Branch Rankings (by navigation completeness) ===")
    for i, (branch, stats) in enumerate(results[:10], 1):
        print(f"{i}. {branch}")
        print(f"   Platforms: {stats['platforms']}, Categories: {stats['categories']}, "
              f"Features: {stats['features']}, Pages: {stats['page_count']}")
        print(f"   Total Items: {stats['total_items']}\n")
    
    # Select top branches to merge
    top_branches = [branch for branch, _ in results[:5]]
    print(f"\nSelected top branches to merge: {top_branches}")
    
    # Merge each branch
    for branch in top_branches:
        try:
            merge_branch_safely('incremeents', branch)
            print(f"✓ Successfully merged {branch}")
        except Exception as e:
            print(f"✗ Failed to merge {branch}: {e}")
    
    print("\n=== Merge Complete ===")
    print("Please review conflicts and commit if needed.")

if __name__ == '__main__':
    main()




