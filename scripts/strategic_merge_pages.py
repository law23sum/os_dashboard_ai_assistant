#!/usr/bin/env python3
"""
Strategic merge of branches into incremeents.
Favors maximum pages, categories, platforms, and features.
"""

import subprocess
import json
import os
from pathlib import Path
from collections import defaultdict

def run_git(cmd, check=True):
    """Run git command and return output."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, check=check
        )
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.CalledProcessError as e:
        return e.stdout.strip(), e.stderr.strip(), e.returncode

def get_file_list_from_branch(branch, path_prefix=""):
    """Get list of files from a branch."""
    cmd = f"git ls-tree -r --name-only {branch} {path_prefix}"
    output, _, _ = run_git(cmd, check=False)
    return [f for f in output.split('\n') if f.strip()]

def get_file_content_from_branch(branch, filepath):
    """Get file content from a branch."""
    cmd = f"git show {branch}:{filepath} 2>/dev/null"
    output, _, code = run_git(cmd, check=False)
    if code == 0:
        return output
    return None

def count_features_in_nav(nav_content):
    """Count features in navigation JSON."""
    try:
        data = json.loads(nav_content)
        count = 0
        for edition, edition_data in data.items():
            for platform, platform_data in edition_data.items():
                for category, category_features in platform_data.items():
                    if isinstance(category_features, list):
                        count += len(category_features)
        return count
    except:
        return 0

def merge_nav_files(branches):
    """Merge navigation files, keeping the one with most features."""
    best_branch = None
    best_content = None
    best_count = 0
    
    for branch in branches:
        content = get_file_content_from_branch(branch, "frontend/public/gui_nav.latest.json")
        if content:
            count = count_features_in_nav(content)
            if count > best_count:
                best_count = count
                best_branch = branch
                best_content = content
    
    return best_branch, best_content

def merge_pages_from_branches(branches, target_branch="incremeents"):
    """Merge pages from multiple branches, keeping all unique pages."""
    print(f"Merging pages from {len(branches)} branches into {target_branch}...")
    
    # Get current pages
    current_pages = set(get_file_list_from_branch(target_branch, "frontend/src/pages/"))
    
    # Collect pages from all branches
    all_pages = defaultdict(list)  # filepath -> [branches that have it]
    
    for branch in branches:
        pages = get_file_list_from_branch(branch, "frontend/src/pages/")
        for page in pages:
            if page.endswith(('.tsx', '.ts')):
                all_pages[page].append(branch)
    
    print(f"Found {len(all_pages)} unique page files across branches")
    print(f"Current branch has {len([p for p in current_pages if p.endswith(('.tsx', '.ts'))])} pages")
    
    # For each page, find the best version (prefer branches with more features)
    pages_to_add = {}
    branch_scores = {
        "ia-reorg-merge-20251221": 510803,
        "fix/restore-gui-glory": 448798,
        "integration/restore-pages-ia-ktg": 448237,  # Has most pages (487)
    }
    
    for page_path, branch_list in all_pages.items():
        # Prefer branches with higher scores
        best_branch_for_page = max(branch_list, key=lambda b: branch_scores.get(b, 0))
        content = get_file_content_from_branch(best_branch_for_page, page_path)
        if content:
            pages_to_add[page_path] = content
    
    return pages_to_add

def main():
    # Top branches to merge (prioritized by score)
    branches_to_merge = [
        "ia-reorg-merge-20251221",  # 504 features
        "integration/restore-pages-ia-ktg",  # 487 pages
        "fix/restore-gui-glory",
        "integration/codex-ia-restore-final",
        "integration/ia-navigation-final",
        "integration/merge-gui-commits-20251221",
    ]
    
    print("Strategic Merge Plan")
    print("=" * 60)
    
    # Step 1: Merge navigation file (take the one with most features)
    print("\n1. Merging navigation file...")
    best_nav_branch, best_nav_content = merge_nav_files(branches_to_merge)
    print(f"   Best navigation: {best_nav_branch} (will be used)")
    
    # Step 2: Collect all pages
    print("\n2. Collecting pages from all branches...")
    pages_to_add = merge_pages_from_branches(branches_to_merge)
    print(f"   Found {len(pages_to_add)} pages to merge")
    
    # Step 3: Create merge plan
    print("\n3. Merge Strategy:")
    print(f"   - Navigation: Use from {best_nav_branch}")
    print(f"   - Pages: Merge {len(pages_to_add)} pages from best branches")
    print(f"   - Strategy: Keep maximum content from all branches")
    
    # Save merge plan
    plan = {
        "navigation_source": best_nav_branch,
        "pages_to_merge": len(pages_to_add),
        "branches_analyzed": branches_to_merge
    }
    
    with open("merge_plan.json", "w") as f:
        json.dump(plan, f, indent=2)
    
    print("\nMerge plan saved to merge_plan.json")
    print("\nNext steps:")
    print("1. Checkout incremeents branch")
    print("2. Merge branches one by one, resolving conflicts in favor of maximum content")
    print("3. Use navigation from best branch")
    print("4. Ensure all pages are present")

if __name__ == "__main__":
    main()




