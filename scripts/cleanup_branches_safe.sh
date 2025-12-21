#!/bin/bash
# Safely delete local branches except develop, main, dying, incremeents

set -e

REPO_DIR="/Users/chrisdixon/Projects/os_dashboard_ai_assistant"
cd "$REPO_DIR"

# Ensure we're on incremeents branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$CURRENT_BRANCH" != "incremeents" ]; then
    echo "⚠️  Currently on $CURRENT_BRANCH, switching to incremeents..."
    git checkout incremeents
fi

# Branches to keep
KEEP_BRANCHES=("develop" "main" "dying" "incremeents")

echo "=========================================="
echo "Branch Cleanup - Safe Deletion"
echo "=========================================="
echo ""
echo "Branches to KEEP:"
for branch in "${KEEP_BRANCHES[@]}"; do
    echo "  ✓ $branch"
done
echo ""

# Get all local branches
ALL_BRANCHES=$(git branch --format='%(refname:short)' | grep -vE '^(develop|main|dying|incremeents)$' | sort)

if [ -z "$ALL_BRANCHES" ]; then
    echo "✅ No branches to delete. All branches are protected."
    exit 0
fi

echo "Branches to DELETE:"
BRANCH_COUNT=0
while IFS= read -r branch; do
    if [ -n "$branch" ]; then
        echo "  ✗ $branch"
        ((BRANCH_COUNT++))
    fi
done <<< "$ALL_BRANCHES"

echo ""
echo "Total branches to delete: $BRANCH_COUNT"
echo ""

# Confirm deletion
read -p "Proceed with deletion? (yes/no): " -r
echo
if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo "❌ Cleanup cancelled."
    exit 1
fi

echo ""
echo "Deleting branches..."
echo ""

DELETED=0
FAILED=0

while IFS= read -r branch; do
    if [ -n "$branch" ]; then
        if git branch -D "$branch" 2>/dev/null; then
            echo "  ✅ Deleted: $branch"
            ((DELETED++))
        else
            echo "  ⚠️  Failed to delete: $branch"
            ((FAILED++))
        fi
    fi
done <<< "$ALL_BRANCHES"

echo ""
echo "=========================================="
echo "Cleanup Complete"
echo "=========================================="
echo "✅ Deleted: $DELETED branches"
if [ $FAILED -gt 0 ]; then
    echo "⚠️  Failed: $FAILED branches"
fi
echo ""
echo "Remaining branches:"
git branch --format='%(refname:short)' | sort


