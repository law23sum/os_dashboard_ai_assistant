#!/bin/bash
# Final merge and cleanup script
# Merges remaining branches into incremeents and cleans up

set -e

BRANCHES_TO_KEEP=("develop" "main" "dying" "incremeents")
CURRENT_BRANCH=$(git branch --show-current)

if [ "$CURRENT_BRANCH" != "incremeents" ]; then
    echo "Switching to incremeents branch..."
    git checkout incremeents
fi

echo "=== Analyzing Navigation Coverage ==="
python3 << 'PYTHON'
import json
import os

nav_file = 'documentation/gui_nav_structure/gui_nav.latest.json'
if os.path.exists(nav_file):
    with open(nav_file, 'r') as f:
        nav = json.load(f)
    
    platforms_count = len(nav)
    total_categories = 0
    total_features = 0
    
    for edition, platforms in nav.items():
        for platform, categories in platforms.items():
            total_categories += len(categories)
            for category, features in categories.items():
                total_features += len(features)
    
    print(f"Current incremeents branch coverage:")
    print(f"  Editions: {platforms_count}")
    print(f"  Total Categories: {total_categories}")
    print(f"  Total Features: {total_features}")
    print(f"  Coverage Score: {platforms_count * 1000 + total_categories * 10 + total_features}")
PYTHON

echo ""
echo "=== Checking for unmerged branches ==="
UNMERGED=$(git branch --list --no-merged incremeents | grep -v "develop\|main\|dying\|incremeents" || true)

if [ -n "$UNMERGED" ]; then
    echo "Found unmerged branches:"
    echo "$UNMERGED"
    echo ""
    echo "Merging unmerged branches..."
    
    for branch in $UNMERGED; do
        branch=$(echo "$branch" | tr -d ' *')
        if [ -n "$branch" ]; then
            echo "Merging $branch..."
            git merge --no-edit "$branch" -m "Merge $branch: maximize navigation coverage" || {
                echo "Merge conflict in $branch, skipping..."
                git merge --abort 2>/dev/null || true
            }
        fi
    done
else
    echo "No unmerged branches found."
fi

echo ""
echo "=== Cleanup: Deleting merged branches ==="
ALL_BRANCHES=$(git branch --list | sed 's/^[ *]*//' | grep -v "^$(echo ${BRANCHES_TO_KEEP[@]} | tr ' ' '|')$" || true)

if [ -n "$ALL_BRANCHES" ]; then
    echo "Branches to delete:"
    echo "$ALL_BRANCHES"
    echo ""
    read -p "Delete these branches? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        for branch in $ALL_BRANCHES; do
            echo "Deleting branch: $branch"
            git branch -D "$branch" 2>/dev/null || echo "Could not delete $branch (may be checked out in worktree)"
        done
        echo "Cleanup complete!"
    else
        echo "Cleanup cancelled."
    fi
else
    echo "No branches to delete."
fi

echo ""
echo "=== Final Status ==="
echo "Current branch: $(git branch --show-current)"
echo "Branches remaining:"
git branch --list

