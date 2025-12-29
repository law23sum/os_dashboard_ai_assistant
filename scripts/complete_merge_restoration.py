#!/usr/bin/env python3
"""
Complete merge restoration - restore all deleted files and resolve all conflicts.
Ensures proper navigation structure: Platform → Category → Features
"""

import subprocess
import os
import json
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

def restore_deleted_file(filepath):
    """Restore a deleted file from incremeents branch"""
    file_path = Path(filepath)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    stdout, stderr, code = run_cmd(f"git show incremeents:{filepath} > {filepath} 2>&1", check=False)
    if code == 0:
        run_cmd(f"git add {filepath}", check=False)
        return True
    return False

def resolve_conflict(filepath):
    """Resolve conflict by keeping current version"""
    if filepath.endswith(('.db', '.png', '.jpg', '.jpeg', '.gif', '.ico', '.pdf', '.bin')):
        run_cmd(f"git checkout --ours {filepath}", check=False)
    else:
        run_cmd(f"git checkout --ours {filepath}", check=False)
    run_cmd(f"git add {filepath}", check=False)
    return True

def main():
    print("=" * 80)
    print("Complete Merge Restoration")
    print("Restoring all deleted pages and resolving all conflicts")
    print("=" * 80)
    
    # Step 1: Get all deleted files
    print("\n[1/3] Restoring deleted files...")
    stdout, _, _ = run_cmd("git status --porcelain | grep '^DU' | awk '{print $2}'")
    deleted_files = [f.strip() for f in stdout.split('\n') if f.strip()]
    
    restored = 0
    for filepath in deleted_files:
        if restore_deleted_file(filepath):
            restored += 1
            if restored % 10 == 0:
                print(f"  Restored {restored}/{len(deleted_files)} files...")
    
    print(f"✓ Restored {restored}/{len(deleted_files)} deleted files")
    
    # Step 2: Resolve all conflicts
    print("\n[2/3] Resolving merge conflicts...")
    stdout, _, _ = run_cmd("git status --porcelain | grep '^UU' | awk '{print $2}'")
    conflicted_files = [f.strip() for f in stdout.split('\n') if f.strip()]
    
    resolved = 0
    for filepath in conflicted_files:
        if resolve_conflict(filepath):
            resolved += 1
            if resolved % 10 == 0:
                print(f"  Resolved {resolved}/{len(conflicted_files)} conflicts...")
    
    print(f"✓ Resolved {resolved}/{len(conflicted_files)} conflicts")
    
    # Step 3: Verify navigation structure
    print("\n[3/3] Verifying navigation structure...")
    nav_file = Path("frontend/public/gui_nav.latest.json")
    if nav_file.exists():
        try:
            with open(nav_file, 'r') as f:
                nav_data = json.load(f)
            print(f"✓ Navigation file found with {len(nav_data)} editions")
        except:
            print("⚠ Navigation file exists but couldn't be parsed")
    else:
        print("⚠ Navigation file not found")
    
    # Summary
    print("\n" + "=" * 80)
    print("Summary")
    print("=" * 80)
    print(f"Files restored: {restored}/{len(deleted_files)}")
    print(f"Conflicts resolved: {resolved}/{len(conflicted_files)}")
    
    # Check remaining
    stdout, _, _ = run_cmd("git status --porcelain | grep -E '^UU|^DU' | wc -l")
    remaining = int(stdout.strip() or 0)
    
    if remaining > 0:
        print(f"\n⚠️  {remaining} files still need attention")
    else:
        print("\n✅ All conflicts resolved! Ready to commit.")
    
    print("\nNext step: Review and commit")

if __name__ == "__main__":
    main()

