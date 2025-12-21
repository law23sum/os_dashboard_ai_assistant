#!/usr/bin/env python3
"""Final resolution of all conflicts"""
import subprocess
import os
from pathlib import Path

os.chdir(Path(__file__).parent.parent)

def run(cmd, check=False):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=check)
    return result.stdout.strip(), result.stderr.strip(), result.returncode

# Get all deleted files
print("Getting deleted files...")
stdout, _, _ = run("git status --porcelain | grep '^DU' | awk '{print $2}'")
deleted = [f.strip() for f in stdout.split('\n') if f.strip()]

print(f"Found {len(deleted)} deleted files to restore")
for i, f in enumerate(deleted, 1):
    Path(f).parent.mkdir(parents=True, exist_ok=True)
    stdout, stderr, code = run(f'git show incremeents:"{f}" > "{f}" 2>&1', check=False)
    if code == 0:
        run(f'git add "{f}"', check=False)
        if i % 10 == 0:
            print(f"  Restored {i}/{len(deleted)}...")
    else:
        print(f"  Failed to restore {f}: {stderr}")

print(f"\nRestored {len(deleted)} deleted files")

# Get all conflicted files
print("\nGetting conflicted files...")
stdout, _, _ = run("git status --porcelain | grep '^UU' | awk '{print $2}'")
conflicted = [f.strip() for f in stdout.split('\n') if f.strip()]

print(f"Found {len(conflicted)} conflicted files to resolve")
for i, f in enumerate(conflicted, 1):
    run(f'git checkout --ours "{f}" 2>&1', check=False)
    run(f'git add "{f}"', check=False)
    if i % 10 == 0:
        print(f"  Resolved {i}/{len(conflicted)}...")

print(f"\nResolved {len(conflicted)} conflicts")

# Final check
stdout, _, _ = run("git status --porcelain | grep -E '^UU|^DU' | wc -l")
remaining = int(stdout.strip() or 0)
print(f"\nRemaining conflicts: {remaining}")

if remaining == 0:
    print("\n✅ All conflicts resolved!")
else:
    print(f"\n⚠️  {remaining} files still need attention")

