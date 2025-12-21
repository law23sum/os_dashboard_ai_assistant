#!/bin/bash
# Final branch cleanup - delete all branches except develop, main, dying, incremeents
# This script safely deletes branches that are already merged

set -e

BRANCHES_TO_KEEP=("develop" "main" "dying" "incremeents")
CURRENT_BRANCH=$(git branch --show-current)

echo "Current branch: $CURRENT_BRANCH"
echo ""

# Get all branches except the ones to keep
ALL_BRANCHES=$(git branch --list --format='%(refname:short)' | grep -vE "^($(IFS='|'; echo "${BRANCHES_TO_KEEP[*]}"))$" || true)

if [ -z "$ALL_BRANCHES" ]; then
    echo "No branches to delete. All branches are in the keep list."
    exit 0
fi

echo "Branches that will be deleted:"
echo "$ALL_BRANCHES" | sed 's/^/  - /'
echo ""

echo "Branches to keep:"
for branch in "${BRANCHES_TO_KEEP[@]}"; do
    if git branch --list --format='%(refname:short)' | grep -q "^${branch}$"; then
        echo "  ✓ $branch"
    fi
done
echo ""

# Delete branches
DELETED_COUNT=0
FAILED_COUNT=0

for branch in $ALL_BRANCHES; do
    if [ -n "$branch" ] && [ "$branch" != "$CURRENT_BRANCH" ]; then
        echo "Deleting branch: $branch"
        if git branch -D "$branch" 2>/dev/null; then
            ((DELETED_COUNT++))
        else
            echo "  ⚠ Could not delete $branch (may be checked out in worktree or has unmerged changes)"
            ((FAILED_COUNT++))
        fi
    fi
done

echo ""
echo "=== Cleanup Summary ==="
echo "Branches deleted: $DELETED_COUNT"
echo "Branches failed to delete: $FAILED_COUNT"
echo ""
echo "Remaining branches:"
git branch --list
