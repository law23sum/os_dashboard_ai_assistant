#!/bin/bash
# Delete all local branches except develop, main, dying, incremeents

set -e

KEEP_BRANCHES=("develop" "main" "dying" "incremeents")
CURRENT_BRANCH=$(git branch --show-current)

echo "Current branch: $CURRENT_BRANCH"
echo "Keeping branches: ${KEEP_BRANCHES[@]}"
echo ""

# Get all local branches
ALL_BRANCHES=$(git branch --format='%(refname:short)')

# Find branches to delete
BRANCHES_TO_DELETE=()
for branch in $ALL_BRANCHES; do
    branch=$(echo "$branch" | xargs)  # trim whitespace
    if [[ ! " ${KEEP_BRANCHES[@]} " =~ " ${branch} " ]]; then
        BRANCHES_TO_DELETE+=("$branch")
    fi
done

if [ ${#BRANCHES_TO_DELETE[@]} -eq 0 ]; then
    echo "No branches to delete."
    exit 0
fi

echo "Branches to delete (${#BRANCHES_TO_DELETE[@]}):"
for branch in "${BRANCHES_TO_DELETE[@]}"; do
    echo "  - $branch"
done

echo ""
read -p "Delete these branches? (y/N) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    for branch in "${BRANCHES_TO_DELETE[@]}"; do
        echo "Deleting $branch..."
        git branch -D "$branch" 2>&1 || echo "  Failed to delete $branch (may not exist or may be checked out)"
    done
    echo ""
    echo "Cleanup complete!"
    echo "Remaining branches:"
    git branch
else
    echo "Cancelled."
fi




