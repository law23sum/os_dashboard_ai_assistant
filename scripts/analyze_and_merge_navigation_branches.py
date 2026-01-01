#!/usr/bin/env python3
"""
Analyze branches to find the most complete navigation structure
and merge them into incremeents branch.
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict

def run_git(cmd: List[str]) -> str:
    """Run git command and return output."""
    try:
        result = subprocess.run(
            ['git'] + cmd,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running git {' '.join(cmd)}: {e.stderr}")
        return ""

def get_branch_list() -> List[str]:
    """Get list of all local branches."""
    output = run_git(['branch', '--format=%(refname:short)'])
    return [b.strip() for b in output.split('\n') if b.strip()]

def get_nav_file_from_branch(branch: str) -> Dict:
    """Get navigation JSON from a branch."""
    nav_files = [
        'frontend/src/data/gui_nav.latest.json',
        'frontend/public/gui_nav.latest.json',
        'documentation/gui_nav_structure/gui_nav.latest.json'
    ]
    
    for nav_file in nav_files:
        try:
            content = run_git(['show', f'{branch}:{nav_file}'])
            if content:
                return json.loads(content)
        except:
            continue
    
    return {}

def count_navigation_structure(nav_data: Dict) -> Dict[str, int]:
    """Count platforms, categories, and features in navigation structure."""
    counts = {
        'platforms': 0,
        'categories': 0,
        'features': 0,
        'editions': 0
    }
    
    if not nav_data:
        return counts
    
    for edition, platforms in nav_data.items():
        if isinstance(platforms, dict):
            counts['editions'] += 1
            for platform, categories in platforms.items():
                if isinstance(categories, dict):
                    counts['platforms'] += 1
                    for category, features in categories.items():
                        if isinstance(features, list):
                            counts['categories'] += 1
                            counts['features'] += len(features)
    
    return counts

def analyze_branches() -> List[Tuple[str, Dict[str, int], Dict]]:
    """Analyze all branches and return sorted by completeness."""
    branches = get_branch_list()
    results = []
    
    print(f"Analyzing {len(branches)} branches...")
    
    for branch in branches:
        if branch in ['main', 'develop', 'dying', 'incremeents']:
            continue
        
        nav_data = get_nav_file_from_branch(branch)
        counts = count_navigation_structure(nav_data)
        
        if counts['features'] > 0:  # Only consider branches with navigation
            total_score = (
                counts['editions'] * 1000 +
                counts['platforms'] * 100 +
                counts['categories'] * 10 +
                counts['features']
            )
            results.append((branch, counts, nav_data, total_score))
            print(f"  {branch}: {counts['platforms']} platforms, {counts['categories']} categories, {counts['features']} features (score: {total_score})")
    
    # Sort by score (descending)
    results.sort(key=lambda x: x[3], reverse=True)
    return results

def merge_navigation_structures(*nav_structures: Dict) -> Dict:
    """Merge multiple navigation structures, keeping the most complete version."""
    merged = {}
    
    for nav_data in nav_structures:
        if not nav_data:
            continue
        
        for edition, platforms in nav_data.items():
            if edition not in merged:
                merged[edition] = {}
            
            for platform, categories in platforms.items():
                if platform not in merged[edition]:
                    merged[edition][platform] = {}
                
                for category, features in categories.items():
                    if category not in merged[edition][platform]:
                        merged[edition][platform][category] = []
                    
                    # Merge features, avoiding duplicates
                    existing_paths = {f.get('path', '') for f in merged[edition][platform][category]}
                    for feature in features:
                        if feature.get('path', '') not in existing_paths:
                            merged[edition][platform][category].append(feature)
    
    return merged

def main():
    print("=== Navigation Branch Analysis ===\n")
    
    # Analyze branches
    results = analyze_branches()
    
    if not results:
        print("No branches with navigation structure found!")
        return
    
    print(f"\n=== Top 5 Branches by Completeness ===")
    for i, (branch, counts, nav_data, score) in enumerate(results[:5], 1):
        print(f"{i}. {branch}")
        print(f"   Editions: {counts['editions']}, Platforms: {counts['platforms']}, "
              f"Categories: {counts['categories']}, Features: {counts['features']}")
    
    # Get top branches for merging
    top_branches = [r[0] for r in results[:5]]
    top_nav_data = [r[2] for r in results[:5]]
    
    # Merge navigation structures
    print(f"\n=== Merging Navigation Structures ===")
    merged_nav = merge_navigation_structures(*top_nav_data)
    merged_counts = count_navigation_structure(merged_nav)
    
    print(f"Merged result:")
    print(f"  Editions: {merged_counts['editions']}")
    print(f"  Platforms: {merged_counts['platforms']}")
    print(f"  Categories: {merged_counts['categories']}")
    print(f"  Features: {merged_counts['features']}")
    
    # Save merged navigation
    output_file = Path('merged_navigation.json')
    with open(output_file, 'w') as f:
        json.dump(merged_nav, f, indent=2)
    
    print(f"\nMerged navigation saved to {output_file}")
    print(f"\nTop branches to merge: {', '.join(top_branches)}")
    
    return top_branches, merged_nav

if __name__ == '__main__':
    main()




