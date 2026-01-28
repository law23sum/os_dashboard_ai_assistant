#!/usr/bin/env python3
"""
Finalize merge by restoring all deleted files and resolving all conflicts.
"""

import subprocess
import os
from pathlib import Path

project_root = Path(__file__).parent.parent
os.chdir(project_root)

def run_cmd(cmd, check=False):
    """Run a git command"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            check=check
        )
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.CalledProcessError as e:
        return e.stdout.strip(), e.stderr.strip(), e.returncode

def main():
    print("=" * 80)
    print("Finalizing Merge - Restoring All Files and Resolving Conflicts")
    print("=" * 80)
    
    # Step 1: Restore all deleted files (DU status)
    print("\n[1/2] Restoring deleted files...")
    stdout, _, _ = run_cmd("git status --porcelain | grep '^DU' | awk '{print $2}'")
    deleted_files = [f.strip() for f in stdout.split('\n') if f.strip()]
    
    restored = 0
    for filepath in deleted_files:
        file_path = Path(filepath)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Try to restore from incremeents branch
        stdout, stderr, code = run_cmd(f"git show incremeents:{filepath} > {filepath} 2>&1", check=False)
        if code == 0:
            run_cmd(f"git add {filepath}", check=False)
            restored += 1
            if restored % 10 == 0:
                print(f"  Restored {restored}/{len(deleted_files)} files...")
    
    print(f"✓ Restored {restored}/{len(deleted_files)} deleted files")
    
    # Step 2: Resolve all conflicts (UU status)
    print("\n[2/2] Resolving merge conflicts...")
    stdout, _, _ = run_cmd("git status --porcelain | grep '^UU' | awk '{print $2}'")
    conflicted_files = [f.strip() for f in stdout.split('\n') if f.strip()]
    
    resolved = 0
    for filepath in conflicted_files:
        # Skip binary files
        if filepath.endswith(('.db', '.png', '.jpg', '.jpeg', '.gif', '.ico', '.pdf', '.bin')):
            run_cmd(f"git checkout --ours {filepath}", check=False)
        else:
            # For text files, keep current version (ours)
            run_cmd(f"git checkout --ours {filepath}", check=False)
        
        run_cmd(f"git add {filepath}", check=False)
        resolved += 1
        if resolved % 10 == 0:
            print(f"  Resolved {resolved}/{len(conflicted_files)} conflicts...")
    
    print(f"✓ Resolved {resolved}/{len(conflicted_files)} conflicts")
    
    # Summary
    print("\n" + "=" * 80)
    print("Summary")
    print("=" * 80)
    print(f"Files restored: {restored}/{len(deleted_files)}")
    print(f"Conflicts resolved: {resolved}/{len(conflicted_files)}")
    
    # Check remaining issues
    stdout, _, _ = run_cmd("git status --porcelain | grep -E '^UU|^DU' | wc -l")
    remaining = int(stdout.strip() or 0)
    
    if remaining > 0:
        print(f"\n⚠️  {remaining} files still need attention")
        print("Run 'git status' to see details")
    else:
        print("\n✅ All conflicts resolved! Ready to commit.")
        print("\nNext step: git commit")

if __name__ == "__main__":
    main()

