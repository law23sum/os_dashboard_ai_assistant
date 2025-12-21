#!/usr/bin/env python3
"""Resolve all unmerged files by checking out appropriate versions"""
import subprocess
import os
from pathlib import Path

os.chdir(Path(__file__).parent.parent)

def run(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip(), result.stderr.strip(), result.returncode

# Get all unmerged files with their stages
print("Getting unmerged files...")
stdout, _, _ = run("git ls-files -u")
unmerged = {}
for line in stdout.split('\n'):
    if not line.strip():
        continue
    parts = line.split()
    if len(parts) >= 4:
        stage = parts[0]
        filepath = parts[3]
        if filepath not in unmerged:
            unmerged[filepath] = []
        unmerged[filepath].append(stage)

print(f"Found {len(unmerged)} unmerged files")

# Resolve each file
restored = 0
kept_ours = 0
for filepath, stages in unmerged.items():
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    
    # If stage 3 exists (theirs/incoming), restore it
    if '3' in stages:
        stdout, stderr, code = run(f'git checkout --theirs "{filepath}" 2>&1')
        if code == 0:
            run(f'git add "{filepath}"')
            restored += 1
            if restored % 20 == 0:
                print(f"  Restored {restored} files...")
    # If stage 1 or 2 exists (ours/current), keep it
    elif '1' in stages or '2' in stages:
        run(f'git checkout --ours "{filepath}" 2>&1')
        run(f'git add "{filepath}"')
        kept_ours += 1
        if kept_ours % 20 == 0:
            print(f"  Kept ours for {kept_ours} files...")

print(f"\nRestored (theirs): {restored}")
print(f"Kept ours: {kept_ours}")

# Check remaining
stdout, _, _ = run("git ls-files -u | wc -l")
remaining = int(stdout.strip() or 0)
print(f"\nRemaining unmerged: {remaining}")

if remaining == 0:
    print("\n✅ All files resolved!")
else:
    print(f"\n⚠️  {remaining} files still unmerged")

