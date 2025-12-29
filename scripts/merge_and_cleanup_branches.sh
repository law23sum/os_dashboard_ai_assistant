#!/bin/bash
# Strategic merge and cleanup script
# Merges branches with maximum content into incremeents, then cleans up

set -e

cd "$(dirname "$0")/.."

echo "=========================================="
echo "STRATEGIC BRANCH MERGE AND CLEANUP"
echo "=========================================="

# Ensure we're on incremeents
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$CURRENT_BRANCH" != "incremeents" ]; then
    echo "Switching to incremeents branch..."
    git checkout incremeents
fi

echo ""
echo "Current branch: $(git rev-parse --abbrev-ref HEAD)"
echo "Current commit: $(git rev-parse --short HEAD)"
echo ""

# List of branches to potentially merge (those with unique commits)
BRANCHES_TO_CHECK=(
    "fix/restore-gui-glory-20251220"
    "gui-restore-3a154a6-work"
)

# Merge branches that have unique commits
for branch in "${BRANCHES_TO_CHECK[@]}"; do
    if git show-ref --verify --quiet refs/heads/"$branch"; then
        UNIQUE_COMMITS=$(git log incremeents.."$branch" --oneline 2>/dev/null | wc -l | tr -d ' ')
        if [ "$UNIQUE_COMMITS" -gt 0 ]; then
            echo "Merging $branch (has $UNIQUE_COMMITS unique commits)..."
            if git merge --no-ff -m "Merge $branch: Preserve maximum pages/categories/platforms" "$branch" 2>&1; then
                echo "✓ Successfully merged $branch"
            else
                echo "⚠ Merge conflict or error with $branch, skipping..."
                git merge --abort 2>/dev/null || true
            fi
        else
            echo "⊘ $branch has no unique commits, skipping"
        fi
    else
        echo "⊘ Branch $branch not found locally, skipping"
    fi
done

echo ""
echo "=========================================="
echo "CLEANING UP BRANCHES"
echo "=========================================="

# Branches to keep
KEEP_BRANCHES=("develop" "main" "dying" "incremeents")

# Get all local branches
ALL_BRANCHES=$(git branch --format='%(refname:short)')

# Delete branches that aren't in the keep list
for branch in $ALL_BRANCHES; do
    if [[ ! " ${KEEP_BRANCHES[@]} " =~ " ${branch} " ]]; then
        echo "Deleting branch: $branch"
        git branch -D "$branch" 2>/dev/null || echo "  (could not delete, may be checked out in worktree)"
    else
        echo "Keeping branch: $branch"
    fi
done

echo ""
echo "=========================================="
echo "FINAL STATUS"
echo "=========================================="
echo "Current branch: $(git rev-parse --abbrev-ref HEAD)"
echo "Remaining branches:"
git branch

echo ""
echo "Done!"




