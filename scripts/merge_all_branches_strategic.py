#!/usr/bin/env python3
"""
Strategic Branch Merger - Merge all branches into incremeents
Prioritizes maximum pages, categories, and platforms
"""

import subprocess
import json
import os
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict

REPO_ROOT = Path(__file__).parent.parent
FRONTEND_PAGES = REPO_ROOT / "frontend" / "src" / "pages"

# Branches to keep
KEEP_BRANCHES = {"develop", "main", "dying", "incremeents"}

# Priority branches (likely to have most complete content)
PRIORITY_BRANCHES = [
    "integration/restore-pages-ia-codex-final",
    "integration/restore-pages-ia-codex",
    "integration/ia-navigation-final",
    "integration/codex-ia-restore-final",
    "gui-fully-restored",
    "restore-gui-comprehensive",
    "restore-gui-fix",
    "restore-ui",
    "gui-restore-stable",
    "gui-restore-stable-3a154a6",
    "fix/restore-gui-glory-20251220",
    "fix/restore-gui-glory",
    "integration/merge-gui-commits-20251221",
    "ia-reorg-merge-20251221",
]

def run_git(cmd: List[str], check=True) -> str:
    """Run git command"""
    result = subprocess.run(
        ["git"] + cmd,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=check
    )
    return result.stdout.strip()

def get_all_branches() -> List[str]:
    """Get all local branches"""
    branches = run_git(["branch", "--format=%(refname:short)"])
    return [b.strip() for b in branches.split("\n") if b.strip()]

def count_pages_in_branch(branch: str) -> Dict[str, int]:
    """Count pages, categories, platforms in a branch"""
    try:
        # Get list of page files
        result = run_git(
            ["ls-tree", "-r", "--name-only", branch, "frontend/src/pages"],
            check=False
        )
        pages = [p for p in result.split("\n") if p.endswith(".tsx") and p.strip()]
        
        # Try to get navigation structure
        nav_files = [
            "frontend/src/data/iaManifest.complete.ts",
            "frontend/src/data/iaManifest.complete.json",
            "documentation/gui_nav_structure/gui_nav.latest.json",
        ]
        
        platforms = set()
        categories = set()
        features = set()
        
        for nav_file in nav_files:
            try:
                content = run_git(["show", f"{branch}:{nav_file}"], check=False)
                if nav_file.endswith(".json"):
                    data = json.loads(content)
                    # Parse structure
                    if isinstance(data, dict):
                        for platform_name, platform_data in data.items():
                            platforms.add(platform_name)
                            if isinstance(platform_data, dict):
                                for category_name, category_data in platform_data.items():
                                    categories.add(category_name)
                                    if isinstance(category_data, list):
                                        for feature in category_data:
                                            if isinstance(feature, dict):
                                                features.add(feature.get("title", ""))
            except:
                pass
        
        return {
            "pages": len(pages),
            "platforms": len(platforms),
            "categories": len(categories),
            "features": len(features),
            "total": len(pages) + len(platforms) + len(categories) + len(features)
        }
    except Exception as e:
        print(f"Error counting pages in {branch}: {e}")
        return {"pages": 0, "platforms": 0, "categories": 0, "features": 0, "total": 0}

def analyze_branches() -> Dict[str, Dict[str, int]]:
    """Analyze all branches for content completeness"""
    branches = get_all_branches()
    results = {}
    
    print("Analyzing branches for content completeness...")
    for branch in branches:
        if branch in KEEP_BRANCHES:
            continue
        print(f"  Analyzing {branch}...")
        results[branch] = count_pages_in_branch(branch)
    
    return results

def merge_branch_strategic(branch: str, current_branch: str = "incremeents") -> bool:
    """Merge a branch strategically, favoring maximum content"""
    try:
        print(f"\nMerging {branch} into {current_branch}...")
        
        # Try merge with strategy favoring theirs (to get their pages)
        result = subprocess.run(
            ["git", "merge", "-X", "theirs", "--no-edit", branch],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"  ✓ Successfully merged {branch}")
            return True
        elif "Already up to date" in result.stdout or "Already up to date" in result.stderr:
            print(f"  - {branch} already merged")
            return True
        else:
            print(f"  ⚠ Merge conflict in {branch}, attempting resolution...")
            # Try to resolve conflicts by favoring files with more content
            conflicts = run_git(["diff", "--name-only", "--diff-filter=U"], check=False)
            if conflicts:
                conflict_files = conflicts.split("\n")
                print(f"  Conflicts in {len(conflict_files)} files")
                # For now, abort and try ours strategy
                run_git(["merge", "--abort"], check=False)
                # Try with ours strategy
                result2 = subprocess.run(
                    ["git", "merge", "-X", "ours", "--no-edit", branch],
                    cwd=REPO_ROOT,
                    capture_output=True,
                    text=True
                )
                if result2.returncode == 0:
                    print(f"  ✓ Merged {branch} with ours strategy")
                    return True
            
            print(f"  ✗ Failed to merge {branch}")
            return False
    except Exception as e:
        print(f"  ✗ Error merging {branch}: {e}")
        return False

def main():
    """Main merge strategy"""
    print("=" * 80)
    print("STRATEGIC BRANCH MERGER")
    print("=" * 80)
    
    # Ensure we're on incremeents
    current = run_git(["branch", "--show-current"])
    if current != "incremeents":
        print(f"Switching to incremeents branch (currently on {current})...")
        run_git(["checkout", "incremeents"])
    
    # Analyze branches
    print("\nStep 1: Analyzing branches...")
    branch_stats = analyze_branches()
    
    # Sort by total content
    sorted_branches = sorted(
        branch_stats.items(),
        key=lambda x: x[1]["total"],
        reverse=True
    )
    
    print("\nBranch Analysis Results:")
    print("-" * 80)
    for branch, stats in sorted_branches[:20]:  # Top 20
        print(f"{branch:50} Pages: {stats['pages']:4} Platforms: {stats['platforms']:2} "
              f"Categories: {stats['categories']:3} Features: {stats['features']:4} "
              f"Total: {stats['total']:4}")
    
    # Merge priority branches first
    print("\nStep 2: Merging priority branches...")
    merged = []
    failed = []
    
    # Merge priority branches
    for branch in PRIORITY_BRANCHES:
        if branch in branch_stats:
            if merge_branch_strategic(branch):
                merged.append(branch)
            else:
                failed.append(branch)
    
    # Merge remaining branches by content score
    print("\nStep 3: Merging remaining branches by content score...")
    for branch, stats in sorted_branches:
        if branch in PRIORITY_BRANCHES or branch in merged or branch in failed:
            continue
        if merge_branch_strategic(branch):
            merged.append(branch)
        else:
            failed.append(branch)
    
    # Summary
    print("\n" + "=" * 80)
    print("MERGE SUMMARY")
    print("=" * 80)
    print(f"Successfully merged: {len(merged)} branches")
    print(f"Failed to merge: {len(failed)} branches")
    
    if merged:
        print("\nMerged branches:")
        for b in merged:
            print(f"  ✓ {b}")
    
    if failed:
        print("\nFailed branches:")
        for b in failed:
            print(f"  ✗ {b}")
    
    print("\nNext steps:")
    print("1. Review merge conflicts and resolve manually if needed")
    print("2. Run tests to ensure everything works")
    print("3. Delete merged branches with: git branch -d <branch>")
    print("4. Keep only: develop, main, dying, incremeents")

if __name__ == "__main__":
    main()

