#!/usr/bin/env python3
"""
Delete local branches except develop, main, dying, incremeents.
"""

import subprocess
from pathlib import Path

def run_git_command(cmd: list[str], check=True) -> tuple[str, int]:
    """Run a git command."""
    try:
        result = subprocess.run(
            ['git'] + cmd,
            capture_output=True,
            text=True,
            check=check,
            cwd=Path(__file__).parent.parent
        )
        return result.stdout.strip(), result.returncode
    except subprocess.CalledProcessError as e:
        return e.stderr.strip(), e.returncode

def get_all_branches() -> list[str]:
    """Get all local branches."""
    output, _ = run_git_command(['branch', '--format=%(refname:short)'], check=False)
    branches = [b.strip() for b in output.split('\n') if b.strip()]
    return branches

def delete_branch(branch: str) -> bool:
    """Delete a branch."""
    print(f"Deleting branch: {branch}")
    output, code = run_git_command(['branch', '-D', branch], check=False)
    if code == 0:
        print(f"  ✓ Deleted {branch}")
        return True
    else:
        print(f"  ✗ Failed to delete {branch}: {output}")
        return False

def main():
    """Main cleanup function."""
    print("="*80)
    print("CLEANING UP BRANCHES")
    print("="*80)
    
    # Branches to keep
    keep_branches = {'develop', 'main', 'dying', 'incremeents'}
    
    # Get all branches
    all_branches = get_all_branches()
    
    # Filter branches to delete
    branches_to_delete = [b for b in all_branches if b not in keep_branches]
    
    print(f"\nBranches to keep: {', '.join(sorted(keep_branches))}")
    print(f"Branches to delete: {len(branches_to_delete)}")
    
    if not branches_to_delete:
        print("\nNo branches to delete.")
        return
    
    print("\nBranches to be deleted:")
    for b in sorted(branches_to_delete):
        print(f"  - {b}")
    
    # Confirm
    response = input("\nProceed with deletion? (yes/no): ").strip().lower()
    if response != 'yes':
        print("Cancelled.")
        return
    
    # Delete branches
    deleted = 0
    failed = 0
    
    for branch in branches_to_delete:
        if delete_branch(branch):
            deleted += 1
        else:
            failed += 1
    
    print("\n" + "="*80)
    print(f"Cleanup complete: {deleted} deleted, {failed} failed")
    print("="*80)

if __name__ == '__main__':
    main()

