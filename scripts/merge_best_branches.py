#!/usr/bin/env python3
"""
Merge branches with maximum pages, categories, and platforms into incremeents.
Strategy: Merge in order of page count, preferring branches with more complete navigation.
"""

import subprocess
import sys
from pathlib import Path
from typing import List, Set

REPO_ROOT = Path(__file__).parent.parent

def run_git(cmd: List[str], check: bool = False) -> str:
    """Run git command."""
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
        print(f"Git error: {e.stderr}", file=sys.stderr)
        return ""

def count_pages(branch: str) -> int:
    """Count .tsx files in pages directory."""
    try:
        output = run_git(["ls-tree", "-r", "--name-only", branch, "frontend/src/pages/"])
        if output:
            return len([f for f in output.splitlines() if f.endswith('.tsx')])
    except:
        pass
    return 0

def has_navigation_files(branch: str) -> bool:
    """Check if branch has navigation configuration files."""
    nav_files = [
        "frontend/src/nav/pageRegistry.ts",
        "frontend/src/config/navigation.ts",
        "frontend/src/data/navigationStructure.ts",
        "frontend/src/components/PlatformNavIA.tsx",
        "frontend/src/components/CategorySidebarIA.tsx"
    ]
    
    for nav_file in nav_files:
        try:
            content = run_git(["show", f"{branch}:{nav_file}"])
            if content:
                return True
        except:
            continue
    return False

def merge_branch(target_branch: str, source_branch: str) -> bool:
    """Merge source branch into target with strategy to keep most files."""
    print(f"\nMerging {source_branch} into {target_branch}...")
    
    # Checkout target
    run_git(["checkout", target_branch])
    
    # Merge with strategy to prefer more files
    try:
        # Try merge with ours strategy (keep target's files by default)
        result = run_git(["merge", "-X", "ours", source_branch], check=False)
        if "Already up to date" in result:
            print(f"  ✓ {source_branch} already merged")
            return True
        elif "CONFLICT" in result or "conflict" in result:
            print(f"  ⚠ Conflicts detected, resolving...")
            # For conflicts, prefer files from source (more pages)
            run_git(["checkout", "--theirs", "frontend/src/pages/"], check=False)
            run_git(["checkout", "--theirs", "frontend/src/nav/"], check=False)
            run_git(["checkout", "--theirs", "frontend/src/config/"], check=False)
            run_git(["checkout", "--theirs", "frontend/src/data/"], check=False)
            run_git(["checkout", "--theirs", "frontend/src/components/PlatformNavIA.tsx"], check=False)
            run_git(["checkout", "--theirs", "frontend/src/components/CategorySidebarIA.tsx"], check=False)
            run_git(["checkout", "--theirs", "frontend/src/components/ActorSwitch.tsx"], check=False)
            run_git(["add", "."], check=False)
            run_git(["commit", "-m", f"Merge {source_branch} - prefer source files for maximum pages"], check=False)
            print(f"  ✓ Resolved conflicts, committed")
            return True
        else:
            print(f"  ✓ Merged successfully")
            return True
    except Exception as e:
        print(f"  ✗ Merge failed: {e}", file=sys.stderr)
        return False

def main():
    print("=" * 80)
    print("Merge Best Branches into incremeents")
    print("=" * 80)
    
    # Target branch
    target = "incremeents"
    
    # Branches to analyze (excluding protected ones)
    protected = {"develop", "main", "dying", "incremeents"}
    
    # Get all local branches
    branches_output = run_git(["branch"])
    all_branches = [b.strip().replace("*", "").strip() for b in branches_output.splitlines()]
    candidate_branches = [b for b in all_branches if b not in protected]
    
    print(f"\nAnalyzing {len(candidate_branches)} candidate branches...")
    
    # Score branches
    branch_scores = []
    for branch in candidate_branches:
        page_count = count_pages(branch)
        has_nav = has_navigation_files(branch)
        score = page_count + (1000 if has_nav else 0)  # Prefer branches with nav files
        branch_scores.append((branch, page_count, has_nav, score))
    
    # Sort by score (descending)
    branch_scores.sort(key=lambda x: x[3], reverse=True)
    
    print("\nTop branches to merge:")
    print("-" * 80)
    for branch, pages, nav, score in branch_scores[:15]:
        nav_str = "✓" if nav else "✗"
        print(f"  {branch:<50} {pages:>4} pages  nav:{nav_str}  score:{score}")
    
    # Select top branches to merge
    top_branches = [b[0] for b in branch_scores[:10] if b[1] > 100]  # At least 100 pages
    
    print(f"\nMerging {len(top_branches)} top branches into {target}...")
    
    # Ensure we're on target branch
    current = run_git(["branch", "--show-current"])
    if current != target:
        print(f"Checking out {target}...")
        run_git(["checkout", target])
    
    # Merge branches
    merged = []
    failed = []
    
    for branch in top_branches:
        if merge_branch(target, branch):
            merged.append(branch)
        else:
            failed.append(branch)
    
    print("\n" + "=" * 80)
    print("Merge Summary")
    print("=" * 80)
    print(f"✓ Successfully merged: {len(merged)}")
    for b in merged:
        print(f"  - {b}")
    
    if failed:
        print(f"\n✗ Failed to merge: {len(failed)}")
        for b in failed:
            print(f"  - {b}")
    
    # Count final pages
    final_count = count_pages(target)
    print(f"\nFinal page count in {target}: {final_count}")

if __name__ == '__main__':
    main()




