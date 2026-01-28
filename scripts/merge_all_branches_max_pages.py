#!/usr/bin/env python3
"""
Strategic merge of all branches into incremeents, preserving maximum pages, categories, and platforms.
Follows IA structure: Platforms (top nav) -> Categories (dropdown) -> Features (left sidebar)
"""

import json
import subprocess
import sys
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple, Optional

def run_git(cmd: str, check: bool = True) -> str:
    """Run git command and return output"""
    result = subprocess.run(
        f"git {cmd}",
        shell=True,
        capture_output=True,
        text=True,
        check=check
    )
    return result.stdout.strip()

def count_nav_structure(nav_data: Dict) -> Dict[str, int]:
    """Count platforms, categories, and features from navigation JSON structure"""
    counts = {
        'platforms': 0,
        'categories': 0,
        'features': 0,
        'editions': 0
    }
    
    if not nav_data or not isinstance(nav_data, dict):
        return counts
    
    # Structure: Edition -> Platform -> Category -> [Features]
    for edition_name, platforms_dict in nav_data.items():
        if isinstance(platforms_dict, dict):
            counts['editions'] += 1
            for platform_name, categories_dict in platforms_dict.items():
                if isinstance(categories_dict, dict):
                    counts['platforms'] += 1
                    for category_name, features_list in categories_dict.items():
                        if isinstance(features_list, list):
                            counts['categories'] += 1
                            counts['features'] += len([f for f in features_list if isinstance(f, dict) and 'path' in f])
    
    return counts

def get_nav_from_branch(branch: str) -> Optional[Dict]:
    """Get navigation JSON from a branch"""
    nav_paths = [
        "frontend/public/gui_nav.latest.json",
        "documentation/gui_nav_structure/gui_nav.latest.json",
        "frontend/src/data/gui_nav.latest.json"
    ]
    
    for path in nav_paths:
        try:
            output = run_git(f"show {branch}:{path}", check=False)
            if output and not output.startswith("fatal:") and not output.startswith("error:"):
                try:
                    return json.loads(output)
                except json.JSONDecodeError:
                    continue
        except:
            continue
    
    return None

def analyze_branches() -> List[Tuple[str, Dict[str, int], Dict]]:
    """Analyze all branches and return sorted by completeness"""
    # Use git show-ref to get actual branch refs
    refs_output = run_git("show-ref", check=False)
    branch_refs = {}
    for line in refs_output.split('\n'):
        if 'refs/heads/' in line:
            commit_hash, ref = line.split()
            branch_name = ref.replace('refs/heads/', '')
            if any(keyword in branch_name.lower() for keyword in ['gui', 'restore', 'integration', 'ia', 'fix']):
                branch_refs[branch_name] = commit_hash
    
    branches_to_check = [
        "fix/ia-navigation-merge",
        "fix/restore-gui-glory",
        "fix/restore-gui-glory-20251220",
        "gui-fully-restored",
        "gui-restore-3a154a6-work",
        "gui-restore-stable",
        "gui-restore-stable-3a154a6",
        "ia-reorg-merge-20251221",
        "integration/codex-ia-restore-final",
        "integration/ia-navigation-final",
        "integration/merge-gui-commits-20251221",
        "integration/restore-pages-ia-codex",
        "integration/restore-pages-ia-ktg",
        "integration/restore-pages-ia-v2",
        "restore-gui-fix",
        "restore-ui",
    ]
    
    # Also check specific commits mentioned by user
    commits_to_check = {
        "4acea80": "4acea80190121b8ab79d8cd1367166bcfead8bde",
        "58cfc34": "58cfc345630f68bf10909538aba48c12f87ce9df",
        "3a154a6": "3a154a6e6305fe9f3a760f44b1b10d73e1ed3256",
    }
    
    results = []
    current_branch = run_git("branch --show-current")
    checked_commits = set()
    
    print(f"Current branch: {current_branch}")
    print(f"Analyzing branches and commits...\n")
    
    # Check branches
    for branch in branches_to_check:
        if branch not in branch_refs:
            print(f"  ⚠ {branch}: Does not exist locally")
            continue
        
        commit_hash = branch_refs[branch]
        if commit_hash in checked_commits:
            print(f"  ⊙ {branch}: Already checked (same commit as another branch)")
            continue
        
        checked_commits.add(commit_hash)
        nav_data = get_nav_from_branch(commit_hash)
        if nav_data:
            counts = count_nav_structure(nav_data)
            score = counts['features'] * 10 + counts['categories'] * 5 + counts['platforms'] * 2
            results.append((branch, counts, nav_data, score, commit_hash))
            print(f"  ✓ {branch} ({commit_hash[:8]}): {counts['platforms']} platforms, {counts['categories']} categories, {counts['features']} features (score: {score})")
        else:
            print(f"  ✗ {branch}: No navigation JSON found")
    
    # Check specific commits
    for name, commit_hash in commits_to_check.items():
        if commit_hash in checked_commits:
            continue
        checked_commits.add(commit_hash)
        nav_data = get_nav_from_branch(commit_hash)
        if nav_data:
            counts = count_nav_structure(nav_data)
            score = counts['features'] * 10 + counts['categories'] * 5 + counts['platforms'] * 2
            results.append((f"commit-{name}", counts, nav_data, score, commit_hash))
            print(f"  ✓ commit-{name} ({commit_hash[:8]}): {counts['platforms']} platforms, {counts['categories']} categories, {counts['features']} features (score: {score})")
    
    # Sort by score (features are most important)
    results.sort(key=lambda x: x[3], reverse=True)
    
    return results

def merge_navigation_data(base: Dict, incoming: Dict) -> Dict:
    """Merge navigation data, preserving maximum content"""
    merged = json.loads(json.dumps(base))  # Deep copy
    
    # Merge editions
    for edition_name, platforms_dict in incoming.items():
        if edition_name not in merged:
            merged[edition_name] = {}
        
        # Merge platforms
        for platform_name, categories_dict in platforms_dict.items():
            if platform_name not in merged[edition_name]:
                merged[edition_name][platform_name] = {}
            
            # Merge categories
            for category_name, features_list in categories_dict.items():
                if category_name not in merged[edition_name][platform_name]:
                    merged[edition_name][platform_name][category_name] = []
                
                # Merge features - use a set to track by path
                existing_paths = {f.get('path') for f in merged[edition_name][platform_name][category_name] if isinstance(f, dict)}
                
                for feature in features_list:
                    if isinstance(feature, dict) and feature.get('path'):
                        if feature['path'] not in existing_paths:
                            merged[edition_name][platform_name][category_name].append(feature)
                            existing_paths.add(feature['path'])
    
    return merged

def main():
    print("="*70)
    print("STRATEGIC BRANCH MERGE - MAXIMUM PAGES PRESERVATION")
    print("="*70)
    
    # Ensure we're on incremeents
    current_branch = run_git("branch --show-current")
    if current_branch != "incremeents":
        print(f"⚠️  Warning: Not on incremeents branch (currently on {current_branch})")
        print("Switching to incremeents...")
        run_git("checkout incremeents")
    
    # Analyze branches
    branch_results = analyze_branches()
    
    if not branch_results:
        print("\n❌ No branches with navigation data found!")
        return
    
    print(f"\n{'='*70}")
    print(f"FOUND {len(branch_results)} BRANCHES WITH NAVIGATION DATA")
    print(f"{'='*70}\n")
    
    # Get current navigation
    current_nav_path = Path("frontend/public/gui_nav.latest.json")
    if not current_nav_path.exists():
        current_nav_path = Path("documentation/gui_nav_structure/gui_nav.latest.json")
    
    if current_nav_path.exists():
        current_nav = json.loads(current_nav_path.read_text())
        current_counts = count_nav_structure(current_nav)
        print(f"Current state: {current_counts['platforms']} platforms, {current_counts['categories']} categories, {current_counts['features']} features")
    else:
        print("⚠️  No current navigation file found, starting from scratch")
        current_nav = {}
        current_counts = {'platforms': 0, 'categories': 0, 'features': 0}
    
    # Merge strategy: take the best from each branch
    print(f"\n{'='*70}")
    print("MERGING NAVIGATION DATA")
    print(f"{'='*70}\n")
    
    merged_nav = current_nav
    best_counts = current_counts
    
    for branch_item in branch_results:
        branch = branch_item[0]
        counts = branch_item[1]
        nav_data = branch_item[2]
        score = branch_item[3]
        print(f"Merging {branch}...")
        merged_nav = merge_navigation_data(merged_nav, nav_data)
        new_counts = count_nav_structure(merged_nav)
        
        if (new_counts['features'] > best_counts['features'] or 
            (new_counts['features'] == best_counts['features'] and new_counts['categories'] > best_counts['categories'])):
            best_counts = new_counts
            print(f"  ✓ Improved: {new_counts['platforms']} platforms, {new_counts['categories']} categories, {new_counts['features']} features")
        else:
            print(f"  - No improvement (already have better)")
    
    print(f"\n{'='*70}")
    print("FINAL RESULTS")
    print(f"{'='*70}")
    print(f"Final counts: {best_counts['platforms']} platforms, {best_counts['categories']} categories, {best_counts['features']} features")
    
    # Save merged navigation
    output_path = Path("frontend/public/gui_nav.latest.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(merged_nav, indent=2))
    
    # Also save to documentation
    doc_path = Path("documentation/gui_nav_structure/gui_nav.latest.json")
    doc_path.write_text(json.dumps(merged_nav, indent=2))
    
    print(f"\n✓ Saved merged navigation to:")
    print(f"  - {output_path}")
    print(f"  - {doc_path}")
    
    # Create summary
    summary = {
        'analysis_date': run_git("log -1 --format=%ci", check=False),
        'current_branch': run_git("branch --show-current"),
        'final_counts': best_counts,
        'branches_analyzed': len(branch_results),
        'branches_merged': [
            {
                'branch': item[0],
                'counts': item[1],
                'score': item[3],
                'commit': item[4] if len(item) > 4 else None
            }
            for item in branch_results
        ]
    }
    
    summary_path = Path("merge_max_pages_summary.json")
    summary_path.write_text(json.dumps(summary, indent=2))
    print(f"  - {summary_path}")
    
    print(f"\n{'='*70}")
    print("NEXT STEPS")
    print(f"{'='*70}")
    print("1. Review the merged navigation JSON files")
    print("2. Stage the changes: git add frontend/public/gui_nav.latest.json documentation/gui_nav_structure/gui_nav.latest.json")
    print("3. Commit the changes")
    print("4. Test the navigation structure")
    print("\n⚠️  Note: This script only merges navigation JSON. You may still need to:")
    print("   - Merge actual page files from branches")
    print("   - Resolve conflicts in other files")
    print("   - Run tests to verify everything works")

if __name__ == "__main__":
    main()

