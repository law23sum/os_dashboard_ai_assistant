#!/usr/bin/env python3
"""Resolve all remaining conflicts"""
import subprocess
import os
from pathlib import Path

os.chdir(Path(__file__).parent.parent)

def run(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip(), result.stderr.strip(), result.returncode

# Restore deleted files
print("Restoring deleted files...")
stdout, _, _ = run("git status --porcelain | grep '^DU' | awk '{print $2}'")
deleted = [f for f in stdout.split('\n') if f]
for f in deleted:
    Path(f).parent.mkdir(parents=True, exist_ok=True)
    run(f'git show incremeents:"{f}" > "{f}" 2>/dev/null')
    run(f'git add "{f}"')
print(f"Restored {len(deleted)} files")

# Resolve conflicts
print("Resolving conflicts...")
stdout, _, _ = run("git status --porcelain | grep '^UU' | awk '{print $2}'")
conflicted = [f for f in stdout.split('\n') if f]
for f in conflicted:
    run(f'git checkout --ours "{f}" 2>/dev/null')
    run(f'git add "{f}"')
print(f"Resolved {len(conflicted)} conflicts")

# Check remaining
stdout, _, _ = run("git status --porcelain | grep -E '^UU|^DU' | wc -l")
remaining = int(stdout.strip() or 0)
print(f"\nRemaining: {remaining}")

