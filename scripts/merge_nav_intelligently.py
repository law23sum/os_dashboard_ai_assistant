#!/usr/bin/env python3
"""
Intelligently merge navigation files from multiple branches to maximize content.
Combines platforms, categories, and features from all branches.
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Set

def get_file_from_branch(branch: str, file_path: str) -> str:
    """Get file contents from a branch."""
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

def merge_nav_structures(all_navs: List[Dict]) -> Dict:
    """
    Merge multiple navigation structures, preserving maximum content.
    Combines platforms, categories, and features from all sources.
    """
    merged = {}
    
    # Collect all editions
    all_editions = set()
    for nav in all_navs:
        all_editions.update(nav.keys())
    
    for edition in all_editions:
        merged[edition] = {}
        
        # Collect all platforms for this edition
        all_platforms = set()
        for nav in all_navs:
            if edition in nav:
                all_platforms.update(nav[edition].keys())
        
        for platform in all_platforms:
            merged[edition][platform] = {}
            
            # Collect all categories for this platform
            all_categories = set()
            for nav in all_navs:
                if edition in nav and platform in nav[edition]:
                    all_categories.update(nav[edition][platform].keys())
            
            for category in all_categories:
                # Collect all features from all branches for this category
                feature_map = {}  # path -> feature
                
                for nav in all_navs:
                    if edition in nav and platform in nav[edition] and category in nav[edition][platform]:
                        features = nav[edition][platform][category]
                        for feature in features:
                            path = feature.get('path', '')
                            # Prefer features from branches with more total features (later in list)
                            if path not in feature_map:
                                feature_map[path] = feature
                
                # Convert back to list, maintaining order (first feature is category home)
                merged[edition][platform][category] = list(feature_map.values())
    
    return merged

def main():
    """Main merge function."""
    repo_root = Path(__file__).parent.parent
    
    # Branches to merge (in order of preference - most features first)
    branches = [
        'ia-reorg-merge-20251221',  # 504 features
        'main',  # 444 features
        'fix/ia-navigation-merge',  # 442 features
        'fix/restore-gui-glory',  # 442 features
        'integration/ia-navigation-final',  # 442 features
    ]
    
    nav_files = [
        'frontend/public/gui_nav.latest.json',
        'documentation/gui_nav_structure/gui_nav.latest.json',
    ]
    
    for nav_file in nav_files:
        print(f"\nMerging {nav_file}...")
        
        # Load navigation from all branches
        all_navs = []
        for branch in branches:
            content = get_file_from_branch(branch, nav_file)
            if content:
                try:
                    nav = json.loads(content)
                    all_navs.append(nav)
                    features = sum(len(features) for platform in nav.values() for categories in platform.values() for features in categories.values())
                    print(f"  Loaded from {branch}: {features} features")
                except Exception as e:
                    print(f"  Error loading from {branch}: {e}")
        
        if not all_navs:
            print(f"  No navigation files found in branches")
            continue
        
        # Merge all navigation structures
        merged_nav = merge_nav_structures(all_navs)
        
        # Count merged result
        merged_features = sum(len(features) for platform in merged_nav.values() for categories in platform.values() for features in categories.values())
        merged_platforms = sum(len(platforms) for platforms in merged_nav.values())
        merged_categories = sum(len(categories) for platform in merged_nav.values() for categories in platform.values())
        
        print(f"  Merged result: {merged_platforms} platforms, {merged_categories} categories, {merged_features} features")
        
        # Write merged navigation
        nav_path = repo_root / nav_file
        nav_path.parent.mkdir(parents=True, exist_ok=True)
        with open(nav_path, 'w') as f:
            json.dump(merged_nav, f, indent=2)
        
        print(f"  Saved to {nav_path}")

if __name__ == '__main__':
    main()


