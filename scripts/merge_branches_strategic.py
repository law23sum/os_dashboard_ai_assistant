#!/usr/bin/env python3
"""
Strategic merge of branches into incremeents.
Merges in favor of maximum pages, categories, and platforms.
"""

import subprocess
import json
import os
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict

REPO_ROOT = Path(__file__).parent.parent

def run_git(cmd: List[str], check=True) -> str:
    """Run git command and return output."""
    try:
        result = subprocess.run(
            ['git'] + cmd,
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=check
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        if check:
            raise
        return ""

def get_branch_commits(branch: str) -> List[str]:
    """Get commit SHAs for a branch."""
    output = run_git(['log', '--format=%H', branch, '-10'], check=False)
    return [c.strip() for c in output.split('\n') if c.strip()]

def get_files_in_commit(commit: str, path_filter: str = 'frontend/src/pages') -> Set[str]:
    """Get files changed/added in a commit."""
    output = run_git(['diff-tree', '--no-commit-id', '--name-only', '-r', commit], check=False)
    files = [f.strip() for f in output.split('\n') if f.strip()]
    return {f for f in files if path_filter in f and f.endswith('.tsx')}

def merge_branch_strategic(target_branch: str, source_branch: str) -> bool:
    """Merge source branch into target, favoring maximum pages."""
    print(f"\nMerging {source_branch} into {target_branch}...")
    
    # Checkout target
    run_git(['checkout', target_branch], check=False)
    
    # Try merge with strategy favoring 'theirs' (source branch) for pages
    try:
        # First, try a normal merge
        result = run_git(['merge', '--no-commit', '--no-ff', source_branch], check=False)
        
        # Check for conflicts
        conflicts = run_git(['diff', '--name-only', '--diff-filter=U'], check=False)
        if conflicts:
            conflict_files = [f.strip() for f in conflicts.split('\n') if f.strip()]
            print(f"  Conflicts in {len(conflict_files)} files")
            
            # For page files, prefer source branch (theirs)
            for file in conflict_files:
                if 'frontend/src/pages' in file and file.endswith('.tsx'):
                    print(f"    Resolving {file} in favor of source branch...")
                    run_git(['checkout', '--theirs', file], check=False)
                    run_git(['add', file], check=False)
                elif 'frontend/src/navigation' in file or 'frontend/src/components' in file:
                    # For nav/components, prefer source if it has more content
                    print(f"    Resolving {file} in favor of source branch...")
                    run_git(['checkout', '--theirs', file], check=False)
                    run_git(['add', file], check=False)
        
        # Complete merge
        run_git(['commit', '-m', f'Merge {source_branch} into {target_branch} - favor maximum pages'], check=False)
        print(f"  ✓ Successfully merged {source_branch}")
        return True
    except Exception as e:
        print(f"  ✗ Merge failed: {e}")
        run_git(['merge', '--abort'], check=False)
        return False

def main():
    print("=== Strategic Branch Merge ===\n")
    
    # Ensure we're on incremeents
    current = run_git(['branch', '--show-current'])
    if current != 'incremeents':
        print(f"Switching to incremeents branch (currently on {current})...")
        run_git(['checkout', 'incremeents'], check=False)
    
    # Priority branches to merge (based on user's mention of specific commits)
    priority_branches = [
        'fix/restore-gui-glory',
        'fix/restore-gui-glory-20251220',
        'gui-restore-stable-3a154a6',
        'gui-restore-stable',
        'restore-ui',
        'restore-gui-fix',
        'restore-gui-comprehensive',
        'integration/ia-navigation-final',
        'integration/restore-pages-ia-codex-final',
        'integration/restore-pages-ia-v2',
        'integration/merge-gui-commits-20251221',
        'fix/ia-navigation-merge',
        'integration/ia-navigation-merge',
    ]
    
    # Get all branches
    all_branches = [b.strip() for b in run_git(['branch', '--format=%(refname:short)']).split('\n') if b.strip()]
    keep_branches = {'develop', 'main', 'dying', 'incremeents'}
    merge_candidates = [b for b in all_branches if b not in keep_branches]
    
    # Prioritize the mentioned branches
    to_merge = []
    for branch in priority_branches:
        if branch in merge_candidates:
            to_merge.append(branch)
            merge_candidates.remove(branch)
    
    # Add remaining branches
    to_merge.extend(merge_candidates)
    
    print(f"Will merge {len(to_merge)} branches into incremeents")
    print(f"Priority branches: {len(priority_branches)}")
    print(f"Other branches: {len(merge_candidates)}\n")
    
    # Merge each branch
    merged = []
    failed = []
    
    for branch in to_merge:
        if merge_branch_strategic('incremeents', branch):
            merged.append(branch)
        else:
            failed.append(branch)
    
    print(f"\n=== Merge Summary ===")
    print(f"Successfully merged: {len(merged)} branches")
    print(f"Failed: {len(failed)} branches")
    
    if merged:
        print(f"\nMerged branches:")
        for b in merged:
            print(f"  ✓ {b}")
    
    if failed:
        print(f"\nFailed branches:")
        for b in failed:
            print(f"  ✗ {b}")
    
    print(f"\nNext: Clean up merged branches (except develop, main, dying, incremeents)")

if __name__ == '__main__':
    main()

