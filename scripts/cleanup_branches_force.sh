#!/bin/bash
# Force delete all branches except develop, main, dying, incremeents

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# Ensure we're on incremeents
current_branch=$(git branch --show-current)
if [ "$current_branch" != "incremeents" ]; then
    echo "Switching to incremeents branch..."
    git checkout incremeents
fi

# Branches to keep
KEEP_BRANCHES=("develop" "main" "dying" "incremeents")

# Get all local branches
ALL_BRANCHES=($(git branch --format='%(refname:short)'))

# Find branches to delete
TO_DELETE=()
for branch in "${ALL_BRANCHES[@]}"; do
    keep=false
    for keep_branch in "${KEEP_BRANCHES[@]}"; do
        if [ "$branch" == "$keep_branch" ]; then
            keep=true
            break
        fi
    done
    if [ "$keep" == "false" ]; then
        TO_DELETE+=("$branch")
    fi
done

echo "Branches to keep: ${KEEP_BRANCHES[*]}"
echo "Branches to delete: ${#TO_DELETE[@]}"
echo ""

if [ ${#TO_DELETE[@]} -eq 0 ]; then
    echo "No branches to delete."
    exit 0
fi

# Force delete all branches
DELETED=0
FAILED=0

for branch in "${TO_DELETE[@]}"; do
    if git branch -D "$branch" 2>/dev/null; then
        echo "✓ Deleted: $branch"
        ((DELETED++))
    else
        echo "✗ Failed to delete: $branch"
        ((FAILED++))
    fi
done

echo ""
echo "Cleanup complete!"
echo "Deleted: $DELETED branches"
echo "Failed: $FAILED branches"
echo ""
echo "Remaining branches:"
git branch

