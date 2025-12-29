#!/usr/bin/env python3
"""
Strategic Branch Analysis and Merge Script
Finds branches with maximum platforms, categories, and features, then merges into incremeents
"""

import subprocess
import json
import os
import re
from pathlib import Path
from collections import defaultdict

def run_git(cmd, cwd=None):
    """Run git command and return output"""
    try:
        result = subprocess.run(
            cmd, shell=True, cwd=cwd, capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Git command failed: {cmd}")
        print(f"Error: {e.stderr}")
        return ""

def count_pages_in_branch(branch_name):
    """Count pages, platforms, categories, and features in a branch"""
    print(f"Analyzing branch: {branch_name}")
    
    # Checkout branch temporarily
    run_git(f"git checkout {branch_name}")
    
    counts = {
        'pages': 0,
        'platforms': 0,
        'categories': 0,
        'features': 0,
        'nav_json_exists': False,
        'nav_json_size': 0
    }
    
    # Count React pages
    pages_dir = Path("frontend/src/pages")
    if pages_dir.exists():
        for ext in ['tsx', 'ts', 'jsx', 'js']:
            pages = list(pages_dir.rglob(f"*.{ext}"))
            # Filter out test files, utils, etc.
            pages = [p for p in pages if 'test' not in str(p).lower() and 
                    'utils' not in str(p).lower() and
                    'types' not in str(p).lower()]
            counts['pages'] += len(pages)
    
    # Check navigation JSON
    nav_json_paths = [
        "frontend/public/gui_nav.latest.json",
        "documentation/gui_nav_structure/gui_nav.latest.json"
    ]
    
    for nav_path in nav_json_paths:
        nav_file = Path(nav_path)
        if nav_file.exists():
            try:
                with open(nav_file, 'r') as f:
                    nav_data = json.load(f)
                    counts['nav_json_exists'] = True
                    counts['nav_json_size'] = os.path.getsize(nav_path)
                    
                    # Count platforms, categories, features
                    for edition, platforms in nav_data.items():
                        counts['platforms'] += len(platforms)
                        for platform, categories in platforms.items():
                            counts['categories'] += len(categories)
                            for category, features in categories.items():
                                if isinstance(features, list):
                                    counts['features'] += len(features)
            except Exception as e:
                print(f"Error reading nav JSON: {e}")
    
    return counts

def get_branch_commits(branch_name, limit=10):
    """Get recent commits from a branch"""
    commits = run_git(f"git log {branch_name} --oneline -{limit}")
    return commits.split('\n') if commits else []

def analyze_all_branches():
    """Analyze all relevant branches"""
    # Get all local branches
    branches_output = run_git("git branch --format='%(refname:short)'")
    all_branches = [b.strip() for b in branches_output.split('\n') if b.strip()]
    
    # Filter relevant branches
    relevant_branches = [
        b for b in all_branches 
        if any(keyword in b.lower() for keyword in [
            'gui', 'restore', 'ia', 'integration', 'fix', 'incremeents'
        ]) and b not in ['main', 'develop', 'dying']
    ]
    
    print(f"Found {len(relevant_branches)} relevant branches to analyze")
    
    # Store current branch
    current_branch = run_git("git rev-parse --abbrev-ref HEAD")
    
    branch_analysis = {}
    
    try:
        for branch in relevant_branches:
            print(f"\n{'='*60}")
            print(f"Analyzing: {branch}")
            print(f"{'='*60}")
            
            counts = count_pages_in_branch(branch)
            commits = get_branch_commits(branch, limit=5)
            
            branch_analysis[branch] = {
                'counts': counts,
                'commits': commits,
                'score': counts['pages'] + counts['features'] * 2 + counts['categories'] * 3 + counts['platforms'] * 5
            }
            
            print(f"Pages: {counts['pages']}, Features: {counts['features']}, "
                  f"Categories: {counts['categories']}, Platforms: {counts['platforms']}")
            print(f"Score: {branch_analysis[branch]['score']}")
    
    finally:
        # Return to original branch
        run_git(f"git checkout {current_branch}")
    
    return branch_analysis, current_branch

def find_best_branches(branch_analysis):
    """Find branches with maximum content"""
    # Sort by score
    sorted_branches = sorted(
        branch_analysis.items(),
        key=lambda x: x[1]['score'],
        reverse=True
    )
    
    print("\n" + "="*60)
    print("BRANCH RANKINGS (by content score)")
    print("="*60)
    
    for i, (branch, data) in enumerate(sorted_branches[:20], 1):
        counts = data['counts']
        print(f"{i:2d}. {branch:40s} | "
              f"Pages: {counts['pages']:4d} | "
              f"Features: {counts['features']:4d} | "
              f"Categories: {counts['categories']:3d} | "
              f"Platforms: {counts['platforms']:2d} | "
              f"Score: {data['score']:6d}")
    
    # Return top branches
    return [b[0] for b in sorted_branches[:10]]

if __name__ == "__main__":
    print("="*60)
    print("STRATEGIC BRANCH ANALYSIS")
    print("="*60)
    
    # Analyze branches
    branch_analysis, current_branch = analyze_all_branches()
    
    # Find best branches
    best_branches = find_best_branches(branch_analysis)
    
    # Save analysis
    with open("branch_analysis_merge.json", "w") as f:
        json.dump({
            'analysis': branch_analysis,
            'best_branches': best_branches,
            'current_branch': current_branch
        }, f, indent=2)
    
    print(f"\nAnalysis saved to branch_analysis_merge.json")
    print(f"\nTop branches to merge: {', '.join(best_branches[:5])}")




