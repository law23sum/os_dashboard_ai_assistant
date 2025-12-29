#!/usr/bin/env python3
"""
Analyze branches to find those with the most complete navigation structure.
Counts platforms, categories, and features from navigation JSON files.
"""

import subprocess
import json
import os
from pathlib import Path
from collections import defaultdict

def get_local_branches():
    """Get list of local branches."""
    result = subprocess.run(
        ['git', 'branch', '--format=%(refname:short)'],
        capture_output=True,
        text=True,
        cwd='/Users/chrisdixon/Projects/os_dashboard_ai_assistant'
    )
    branches = [b.strip() for b in result.stdout.strip().split('\n') if b.strip()]
    # Filter to relevant branches (exclude develop, main, dying, incremeents for now)
    relevant = [
        'gui-fully-restored', 'integration/ia-navigation-final',
        'integration/restore-pages-ia-codex', 'fix/restore-gui-glory',
        'gui-restore-stable-3a154a6', 'integration/merge-gui-commits-20251221',
        'integration/restore-pages-ia-v2', 'restore-ui', 'restore-gui-fix',
        'integration/codex-ia-restore-final', 'integration/restore-pages-ia-ktg',
        'fix/ia-navigation-merge', 'gui-restore-stable', 'gui-restore-3a154a6-work'
    ]
    return [b for b in branches if b in relevant]

def count_nav_elements_from_json(data, path=""):
    """Recursively count platforms, categories, and features from navigation JSON."""
    platforms = set()
    categories = set()
    features = 0
    
    if isinstance(data, dict):
        # Check if this is the edition level (Personal/Enterprise)
        if any(k in data for k in ['Personal Workstation Edition', 'Enterprise Workstation Edition']):
            # This is edition level, next level is platforms
            for edition, platforms_dict in data.items():
                if isinstance(platforms_dict, dict):
                    for platform_name, categories_dict in platforms_dict.items():
                        platforms.add(platform_name)
                        if isinstance(categories_dict, dict):
                            for category_name, features_list in categories_dict.items():
                                categories.add(f"{platform_name}::{category_name}")
                                if isinstance(features_list, list):
                                    features += len(features_list)
        else:
            # Might be platform level or category level
            for key, value in data.items():
                if isinstance(value, dict):
                    # Could be categories
                    if any(isinstance(v, list) for v in value.values()):
                        # This looks like categories -> features
                        categories.add(key)
                        for cat_name, features_list in value.items():
                            if isinstance(features_list, list):
                                features += len(features_list)
                    else:
                        # Recurse
                        sub_platforms, sub_categories, sub_features = count_nav_elements_from_json(value, f"{path}.{key}")
                        platforms.update(sub_platforms)
                        categories.update(sub_categories)
                        features += sub_features
                elif isinstance(value, list):
                    # This is a features list
                    features += len(value)
    
    return platforms, categories, features

def analyze_branch_nav(branch_name):
    """Analyze navigation completeness for a branch."""
    current_branch = subprocess.run(
        ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
        capture_output=True,
        text=True,
        cwd='/Users/chrisdixon/Projects/os_dashboard_ai_assistant'
    ).stdout.strip()
    
    nav_files = [
        'frontend/public/gui_nav.latest.json',
        'documentation/gui_nav_structure/gui_nav.latest.json'
    ]
    
    max_platforms = 0
    max_categories = 0
    max_features = 0
    found_files = []
    
    for nav_file in nav_files:
        try:
            # Try to read file from branch
            result = subprocess.run(
                ['git', 'show', f'{branch_name}:{nav_file}'],
                capture_output=True,
                text=True,
                cwd='/Users/chrisdixon/Projects/os_dashboard_ai_assistant',
                timeout=10
            )
            
            if result.returncode == 0 and result.stdout:
                data = json.loads(result.stdout)
                platforms, categories, features = count_nav_elements_from_json(data)
                
                max_platforms = max(max_platforms, len(platforms))
                max_categories = max(max_categories, len(categories))
                max_features = max(max_features, features)
                found_files.append(nav_file)
        except Exception as e:
            pass  # File doesn't exist in this branch
    
    return {
        'platforms': max_platforms,
        'categories': max_categories,
        'features': max_features,
        'total': max_platforms + max_categories + max_features,
        'files_found': found_files
    }

def analyze_all_branches():
    """Analyze all relevant branches."""
    branches = get_local_branches()
    current_branch = subprocess.run(
        ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
        capture_output=True,
        text=True,
        cwd='/Users/chrisdixon/Projects/os_dashboard_ai_assistant'
    ).stdout.strip()
    
    results = {}
    
    print("Analyzing branches for navigation completeness...")
    print("=" * 80)
    
    for branch in branches:
        print(f"Analyzing: {branch}...")
        results[branch] = analyze_branch_nav(branch)
    
    # Restore current branch (no-op if already there)
    subprocess.run(
        ['git', 'checkout', current_branch],
        capture_output=True,
        cwd='/Users/chrisdixon/Projects/os_dashboard_ai_assistant'
    )
    
    return results

if __name__ == '__main__':
    results = analyze_all_branches()
    
    # Sort by total elements
    sorted_results = sorted(results.items(), key=lambda x: x[1]['total'], reverse=True)
    
    print("\n" + "=" * 80)
    print("BRANCH NAVIGATION COMPLETENESS ANALYSIS")
    print("=" * 80)
    print(f"{'Branch':<45} {'Platforms':<12} {'Categories':<12} {'Features':<12} {'Total':<12}")
    print("-" * 80)
    
    for branch, counts in sorted_results:
        print(f"{branch:<45} {counts['platforms']:<12} {counts['categories']:<12} {counts['features']:<12} {counts['total']:<12}")
    
    # Save results
    with open('/Users/chrisdixon/Projects/os_dashboard_ai_assistant/branch_nav_completeness.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to branch_nav_completeness.json")
    print(f"\n🏆 Top 5 branches by total elements:")
    for i, (branch, counts) in enumerate(sorted_results[:5], 1):
        print(f"  {i}. {branch}: {counts['total']} total ({counts['platforms']} platforms, {counts['categories']} categories, {counts['features']} features)")



