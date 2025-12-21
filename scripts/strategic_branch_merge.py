#!/usr/bin/env python3
"""
Strategic Branch Merge Script
Merges branches into incremeents branch, preserving maximum content.
Prioritizes branches with most platforms, categories, and features.
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

REPO_ROOT = Path(__file__).parent.parent
NAV_JSON_PATHS = [
    "frontend/src/data/gui_nav.latest.json",
    "frontend/public/gui_nav.latest.json",
    "documentation/gui_nav_structure/gui_nav.latest.json"
]

def run_git(cmd: List[str]) -> Tuple[int, str, str]:
    """Run git command and return exit code, stdout, stderr"""
    result = subprocess.run(
        ["git"] + cmd,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True
    )
    return result.returncode, result.stdout, result.stderr

def get_branch_list() -> List[str]:
    """Get list of all local branches"""
    exit_code, stdout, _ = run_git(["branch", "--format=%(refname:short)"])
    if exit_code != 0:
        return []
    return [b.strip() for b in stdout.strip().split("\n") if b.strip()]

def count_nav_content(nav_data: Dict) -> Dict[str, int]:
    """Count platforms, categories, and features in navigation structure"""
    counts = {
        "platforms": 0,
        "categories": 0,
        "features": 0
    }
    
    for edition, platforms in nav_data.items():
        if not isinstance(platforms, dict):
            continue
        counts["platforms"] += len(platforms)
        for platform_name, categories in platforms.items():
            if not isinstance(categories, dict):
                continue
            counts["categories"] += len(categories)
            for category_name, features in categories.items():
                if isinstance(features, list):
                    counts["features"] += len(features)
    
    return counts

def get_nav_from_branch(branch: str) -> Tuple[Dict, Dict[str, int]]:
    """Get navigation JSON from a branch and count its content"""
    nav_data = {}
    counts = {"platforms": 0, "categories": 0, "features": 0}
    
    for nav_path in NAV_JSON_PATHS:
        exit_code, stdout, _ = run_git([
            "show", f"{branch}:{nav_path}"
        ])
        if exit_code == 0 and stdout:
            try:
                nav_data = json.loads(stdout)
                counts = count_nav_content(nav_data)
                return nav_data, counts
            except json.JSONDecodeError:
                continue
    
    return {}, counts

def analyze_branches() -> List[Dict]:
    """Analyze all branches and return sorted by content richness"""
    branches = get_branch_list()
    branch_data = []
    
    # Exclude branches we want to keep
    keep_branches = {"develop", "main", "dying", "incremeents"}
    
    for branch in branches:
        if branch in keep_branches:
            continue
        
        print(f"Analyzing branch: {branch}")
        nav_data, counts = get_nav_from_branch(branch)
        
        # Score: platforms * 1000 + categories * 100 + features
        score = counts["platforms"] * 1000 + counts["categories"] * 100 + counts["features"]
        
        branch_data.append({
            "branch": branch,
            "platforms": counts["platforms"],
            "categories": counts["categories"],
            "features": counts["features"],
            "score": score,
            "nav_data": nav_data
        })
    
    # Sort by score (descending)
    branch_data.sort(key=lambda x: x["score"], reverse=True)
    return branch_data

def merge_branch_into_current(branch: str, strategy: str = "ours") -> bool:
    """Merge a branch into current branch with strategy"""
    print(f"\nMerging {branch} into incremeents (strategy: {strategy})...")
    
    # Merge with strategy to favor current branch content
    exit_code, stdout, stderr = run_git([
        "merge", f"-X{strategy}", branch, "--no-edit"
    ])
    
    if exit_code == 0:
        print(f"✓ Successfully merged {branch}")
        return True
    else:
        print(f"✗ Merge conflict or error with {branch}: {stderr}")
        # Check if there are conflicts
        exit_code_conflicts, _, _ = run_git(["diff", "--check"])
        if exit_code_conflicts != 0:
            # Try to resolve by favoring current branch for conflicts
            print(f"  Attempting to resolve conflicts by favoring incremeents...")
            run_git(["checkout", "--ours", "."])
            run_git(["add", "."])
            exit_code_commit, _, _ = run_git(["commit", "--no-edit"])
            if exit_code_commit == 0:
                print(f"✓ Resolved conflicts and committed")
                return True
        return False

def main():
    print("=" * 80)
    print("Strategic Branch Merge - Finding branches with maximum content")
    print("=" * 80)
    
    # Ensure we're on incremeents branch
    exit_code, stdout, _ = run_git(["rev-parse", "--abbrev-ref", "HEAD"])
    current_branch = stdout.strip()
    
    if current_branch != "incremeents":
        print(f"Current branch is {current_branch}, checking out incremeents...")
        run_git(["checkout", "incremeents"])
    
    # Analyze branches
    print("\nAnalyzing branches...")
    branch_data = analyze_branches()
    
    if not branch_data:
        print("No branches to analyze")
        return
    
    print("\n" + "=" * 80)
    print("Branch Analysis Results (sorted by content richness):")
    print("=" * 80)
    print(f"{'Branch':<40} {'Platforms':<12} {'Categories':<12} {'Features':<12} {'Score':<10}")
    print("-" * 80)
    
    for data in branch_data[:20]:  # Show top 20
        print(f"{data['branch']:<40} {data['platforms']:<12} {data['categories']:<12} {data['features']:<12} {data['score']:<10}")
    
    # Identify top branches to merge (top 5-10 by score)
    top_branches = [b["branch"] for b in branch_data[:10] if b["score"] > 0]
    
    print(f"\n\nIdentified {len(top_branches)} branches with content to merge:")
    for branch in top_branches:
        print(f"  - {branch}")
    
    # Get current branch content counts
    _, current_nav, _ = run_git(["show", f"HEAD:{NAV_JSON_PATHS[0]}"])
    current_counts = count_nav_content(json.loads(current_nav)) if current_nav else {"platforms": 0, "categories": 0, "features": 0}
    current_score = current_counts["platforms"] * 1000 + current_counts["categories"] * 100 + current_counts["features"]
    
    print(f"\nCurrent incremeents branch score: {current_score} (P:{current_counts['platforms']}, C:{current_counts['categories']}, F:{current_counts['features']})")
    
    # Merge branches that have more content than current
    branches_to_merge = []
    for branch_info in branch_data:
        if branch_info["score"] > current_score:
            branches_to_merge.append(branch_info["branch"])
    
    if not branches_to_merge:
        print("\nNo branches have more content than current incremeents branch.")
        print("Merging top branches anyway to consolidate content...")
        branches_to_merge = top_branches[:5]
    
    print(f"\n\nMerging {len(branches_to_merge)} branches into incremeents...")
    print("Strategy: Using 'theirs' to favor more content, then resolving conflicts manually")
    
    merged_count = 0
    for branch in branches_to_merge:
        # Use 'theirs' strategy to favor the branch being merged (more content)
        if merge_branch_into_current(branch, strategy="theirs"):
            merged_count += 1
        else:
            print(f"Warning: Could not merge {branch}, skipping...")
    
    print(f"\n{'='*80}")
    print(f"Merged {merged_count} out of {len(branches_to_merge)} branches")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()



