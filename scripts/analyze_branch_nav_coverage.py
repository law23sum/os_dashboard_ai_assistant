#!/usr/bin/env python3
"""
Analyze branches to find which ones have maximum navigation coverage
(platforms, categories, features)
"""
import json
import subprocess
import sys
import os

def count_nav_structure(nav_data):
    """Count platforms, categories, and features in navigation structure"""
    if not nav_data:
        return 0, 0, 0
    
    total_platforms = len(nav_data)
    total_categories = 0
    total_features = 0
    
    for edition, platforms in nav_data.items():
        for platform, categories in platforms.items():
            total_categories += len(categories)
            for category, features in categories.items():
                if isinstance(features, list):
                    total_features += len(features)
    
    return total_platforms, total_categories, total_features

def get_nav_from_branch(branch_name):
    """Try to get navigation JSON from a branch"""
    paths = [
        'frontend/public/gui_nav.latest.json',
        'documentation/gui_nav_structure/gui_nav.latest.json',
        'frontend/src/data/gui_nav.latest.json',
    ]
    
    for path in paths:
        try:
            result = subprocess.run(
                ['git', 'show', f'{branch_name}:{path}'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                try:
                    return json.loads(result.stdout)
                except json.JSONDecodeError:
                    continue
        except Exception:
            continue
    
    return None

def analyze_branches():
    """Analyze all branches for navigation coverage"""
    # Get list of branches (excluding the ones to keep)
    result = subprocess.run(
        ['git', 'branch', '--list'],
        capture_output=True,
        text=True
    )
    
    branches = []
    for line in result.stdout.split('\n'):
        branch = line.strip().lstrip('*').strip()
        if branch and branch not in ['develop', 'main', 'dying', 'incremeents']:
            branches.append(branch)
    
    print("Analyzing branches for navigation coverage...")
    print("=" * 80)
    
    results = []
    
    # Analyze current branch first
    try:
        nav_file = 'documentation/gui_nav_structure/gui_nav.latest.json'
        if os.path.exists(nav_file):
            with open(nav_file, 'r') as f:
                nav_data = json.load(f)
            platforms, categories, features = count_nav_structure(nav_data)
            results.append({
                'branch': 'incremeents (current)',
                'platforms': platforms,
                'categories': categories,
                'features': features,
                'score': platforms * 1000 + categories * 10 + features
            })
    except Exception as e:
        print(f"Error reading current branch: {e}")
    
    # Analyze other branches
    for branch in branches[:20]:  # Limit to first 20 to avoid timeout
        try:
            nav_data = get_nav_from_branch(branch)
            if nav_data:
                platforms, categories, features = count_nav_structure(nav_data)
                score = platforms * 1000 + categories * 10 + features
                results.append({
                    'branch': branch,
                    'platforms': platforms,
                    'categories': categories,
                    'features': features,
                    'score': score
                })
        except Exception as e:
            continue
    
    # Sort by score (higher is better)
    results.sort(key=lambda x: x['score'], reverse=True)
    
    # Print results
    print(f"{'Branch':<40} {'Platforms':<10} {'Categories':<12} {'Features':<10} {'Score':<10}")
    print("-" * 80)
    for r in results:
        print(f"{r['branch']:<40} {r['platforms']:<10} {r['categories']:<12} {r['features']:<10} {r['score']:<10}")
    
    # Find top 5 branches
    top_branches = [r['branch'] for r in results[:5] if r['branch'] != 'incremeents (current)']
    print("\n" + "=" * 80)
    print("Top branches to merge (excluding current):")
    for i, branch in enumerate(top_branches, 1):
        print(f"{i}. {branch}")
    
    return top_branches

if __name__ == '__main__':
    analyze_branches()

