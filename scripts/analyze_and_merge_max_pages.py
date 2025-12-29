#!/usr/bin/env python3
"""
Strategic Branch Analysis and Merge Script
Finds branches with maximum platforms, categories, and feature pages
Merges them into incremeents branch preserving maximum content
"""

import subprocess
import json
import os
import re
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple

REPO_ROOT = Path(__file__).parent.parent
FRONTEND_PAGES = REPO_ROOT / "frontend" / "src" / "pages"
NAV_JSON = REPO_ROOT / "frontend" / "public" / "gui_nav.latest.json"

def run_git(cmd: List[str], check=True) -> str:
    """Run git command and return output"""
    try:
        result = subprocess.run(
            ["git"] + cmd,
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=check
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Git command failed: {' '.join(cmd)}")
        print(f"Error: {e.stderr}")
        return ""

def get_all_branches() -> List[str]:
    """Get all local branches"""
    output = run_git(["branch", "--list"])
    branches = [b.strip().replace("*", "").strip() for b in output.split("\n") if b.strip()]
    return [b for b in branches if b and not b.startswith("(")]

def count_pages_in_branch(branch: str) -> Dict[str, int]:
    """Count pages, platforms, categories in a branch"""
    stats = {
        "total_pages": 0,
        "platforms": 0,
        "categories": 0,
        "features": 0,
        "tsx_files": 0
    }
    
    # Checkout branch temporarily (stash first)
    current_branch = run_git(["rev-parse", "--abbrev-ref", "HEAD"])
    
    try:
        # Count TSX files in pages directory
        if (REPO_ROOT / "frontend" / "src" / "pages").exists():
            tsx_files = list((REPO_ROOT / "frontend" / "src" / "pages").rglob("*.tsx"))
            stats["tsx_files"] = len(tsx_files)
            stats["total_pages"] = len(tsx_files)
        
        # Try to read navigation JSON if it exists
        if NAV_JSON.exists():
            try:
                with open(NAV_JSON, 'r') as f:
                    nav_data = json.load(f)
                    # Count platforms (top level keys after edition)
                    for edition, platforms in nav_data.items():
                        if isinstance(platforms, dict):
                            stats["platforms"] = len(platforms)
                            # Count categories
                            for platform, categories in platforms.items():
                                if isinstance(categories, dict):
                                    stats["categories"] += len(categories)
                                    # Count features
                                    for category, features in categories.items():
                                        if isinstance(features, list):
                                            stats["features"] += len(features)
            except:
                pass
    except Exception as e:
        print(f"Error analyzing branch {branch}: {e}")
    
    return stats

def analyze_branches() -> Dict[str, Dict[str, int]]:
    """Analyze all branches and return statistics"""
    branches = get_all_branches()
    branch_stats = {}
    
    current_branch = run_git(["rev-parse", "--abbrev-ref", "HEAD"])
    print(f"Current branch: {current_branch}")
    
    for branch in branches:
        if branch in ["main", "develop", "dying", "incremeents"]:
            continue  # Skip protected branches for now
        
        print(f"Analyzing branch: {branch}")
        try:
            # Checkout branch
            run_git(["checkout", branch], check=False)
            stats = count_pages_in_branch(branch)
            branch_stats[branch] = stats
            print(f"  Pages: {stats['total_pages']}, Platforms: {stats['platforms']}, "
                  f"Categories: {stats['categories']}, Features: {stats['features']}")
        except Exception as e:
            print(f"  Error analyzing {branch}: {e}")
    
    # Return to original branch
    run_git(["checkout", current_branch], check=False)
    
    return branch_stats

def find_best_branches(branch_stats: Dict[str, Dict[str, int]]) -> List[Tuple[str, int]]:
    """Find branches with maximum content, scored by total pages + features"""
    scored = []
    for branch, stats in branch_stats.items():
        # Score: prioritize pages, then features, then categories, then platforms
        score = (
            stats.get("total_pages", 0) * 10 +
            stats.get("features", 0) * 5 +
            stats.get("categories", 0) * 3 +
            stats.get("platforms", 0) * 2
        )
        scored.append((branch, score))
    
    # Sort by score descending
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored

def main():
    print("=" * 80)
    print("Strategic Branch Analysis for Maximum Web Pages")
    print("=" * 80)
    
    # Ensure we're on incremeents
    current = run_git(["rev-parse", "--abbrev-ref", "HEAD"])
    if current != "incremeents":
        print(f"Switching to incremeents branch (currently on {current})")
        run_git(["checkout", "incremeents"], check=False)
    
    # Analyze branches
    print("\nAnalyzing branches...")
    branch_stats = analyze_branches()
    
    # Find best branches
    print("\n" + "=" * 80)
    print("Branch Rankings (by content score):")
    print("=" * 80)
    best_branches = find_best_branches(branch_stats)
    
    for i, (branch, score) in enumerate(best_branches[:20], 1):
        stats = branch_stats.get(branch, {})
        print(f"{i:2d}. {branch:40s} Score: {score:6d} | "
              f"Pages: {stats.get('total_pages', 0):4d} | "
              f"Platforms: {stats.get('platforms', 0):2d} | "
              f"Categories: {stats.get('categories', 0):3d} | "
              f"Features: {stats.get('features', 0):4d}")
    
    # Save analysis
    output_file = REPO_ROOT / "branch_analysis_max_pages.json"
    with open(output_file, 'w') as f:
        json.dump({
            "branch_stats": branch_stats,
            "rankings": [{"branch": b, "score": s} for b, s in best_branches]
        }, f, indent=2)
    
    print(f"\nAnalysis saved to: {output_file}")
    
    # Recommend merge order
    print("\n" + "=" * 80)
    print("Recommended Merge Order (top 10 branches):")
    print("=" * 80)
    for i, (branch, score) in enumerate(best_branches[:10], 1):
        print(f"{i}. {branch} (score: {score})")
    
    return best_branches

if __name__ == "__main__":
    main()



