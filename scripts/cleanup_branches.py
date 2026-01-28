#!/usr/bin/env python3
"""Clean up branches, keeping only develop, main, dying, incremeents"""

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
KEEP_BRANCHES = {"develop", "main", "dying", "incremeents"}

def run_git(cmd):
    """Run git command"""
    result = subprocess.run(["git"] + cmd, cwd=REPO_ROOT, capture_output=True, text=True)
    return result.returncode == 0, result.stdout.strip(), result.stderr.strip()

def main():
    # Get all local branches
    success, stdout, _ = run_git(["branch", "--format=%(refname:short)"])
    if not success:
        print("Failed to get branch list")
        return
    
    branches = [b.strip() for b in stdout.split("\n") if b.strip()]
    
    # Find branches to delete
    to_delete = [b for b in branches if b not in KEEP_BRANCHES]
    
    if not to_delete:
        print("No branches to delete")
        return
    
    print(f"Branches to delete ({len(to_delete)}):")
    for branch in to_delete:
        print(f"  - {branch}")
    
    print(f"\nDeleting branches...")
    deleted = []
    failed = []
    
    for branch in to_delete:
        success, _, stderr = run_git(["branch", "-D", branch])
        if success:
            deleted.append(branch)
            print(f"✓ Deleted {branch}")
        else:
            failed.append(branch)
            print(f"✗ Failed to delete {branch}: {stderr}")
    
    print(f"\n{'='*80}")
    print(f"Deleted {len(deleted)} branches")
    if failed:
        print(f"Failed to delete {len(failed)} branches: {', '.join(failed)}")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()




