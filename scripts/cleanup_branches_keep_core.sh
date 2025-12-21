#!/bin/bash
# Clean up branches, keeping only: develop, main, dying, incremeents

set -e

BRANCHES_TO_KEEP=("develop" "main" "dying" "incremeents")
CURRENT_BRANCH=$(git branch --show-current)

echo "======================================================================"
echo "BRANCH CLEANUP - KEEPING ONLY: ${BRANCHES_TO_KEEP[*]}"
echo "======================================================================"
echo "Current branch: $CURRENT_BRANCH"
echo ""

# Get all local branches
ALL_BRANCHES=$(git branch --format='%(refname:short)')

BRANCHES_TO_DELETE=()
for branch in $ALL_BRANCHES; do
    # Skip current branch and branches to keep
    if [ "$branch" != "$CURRENT_BRANCH" ]; then
        keep_it=0
        for keep in "${BRANCHES_TO_KEEP[@]}"; do
            if [ "$branch" == "$keep" ]; then
                keep_it=1
                break
            fi
        done
        
        if [ $keep_it -eq 0 ]; then
            BRANCHES_TO_DELETE+=("$branch")
        fi
    fi
done

if [ ${#BRANCHES_TO_DELETE[@]} -eq 0 ]; then
    echo "✓ No branches to delete. All branches are already in the keep list."
    exit 0
fi

echo "Branches to delete (${#BRANCHES_TO_DELETE[@]}):"
for branch in "${BRANCHES_TO_DELETE[@]}"; do
    echo "  - $branch"
done

echo ""
read -p "Are you sure you want to delete these branches? (yes/no): " -r
echo ""

if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo "Cancelled."
    exit 0
fi

echo "Deleting branches..."
for branch in "${BRANCHES_TO_DELETE[@]}"; do
    if git branch -D "$branch" 2>/dev/null; then
        echo "  ✓ Deleted $branch"
    else
        echo "  ✗ Failed to delete $branch (may not exist or has unmerged changes)"
    fi
done

echo ""
echo "======================================================================"
echo "CLEANUP COMPLETE"
echo "======================================================================"
echo "Remaining branches:"
git branch --format='  %(refname:short)'

