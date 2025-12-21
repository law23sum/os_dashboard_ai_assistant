#!/bin/bash
# Cleanup merged branches - keep only develop, main, dying, incremeents

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

PROTECTED_BRANCHES="develop main dying incremeents"

echo "=================================================================================="
echo "Branch Cleanup: Delete all branches except protected ones"
echo "=================================================================================="
echo "Protected branches: $PROTECTED_BRANCHES"
echo ""

# Get all local branches
ALL_BRANCHES=$(git branch --list | sed 's/^[[:space:]]*\*[[:space:]]*//' | sed 's/^[[:space:]]*//')

# Filter out protected branches
BRANCHES_TO_DELETE=""
for branch in $ALL_BRANCHES; do
    # Skip if protected
    is_protected=false
    for protected in $PROTECTED_BRANCHES; do
        if [ "$branch" = "$protected" ]; then
            is_protected=true
            break
        fi
    done
    
    if [ "$is_protected" = "false" ]; then
        BRANCHES_TO_DELETE="$BRANCHES_TO_DELETE $branch"
    fi
done

if [ -z "$BRANCHES_TO_DELETE" ]; then
    echo "No branches to delete (all are protected)"
    exit 0
fi

echo "Branches to delete:"
echo "$BRANCHES_TO_DELETE" | tr ' ' '\n' | grep -v '^$' | sed 's/^/  - /'
echo ""
echo "Deleting branches..."
echo ""

# Delete each branch
for branch in $BRANCHES_TO_DELETE; do
    if [ -n "$branch" ]; then
        echo "Deleting: $branch"
        git branch -D "$branch" 2>&1 || echo "  ⚠ Could not delete $branch (may not exist or is current branch)"
    fi
done

echo ""
echo "=================================================================================="
echo "Cleanup Complete"
echo "=================================================================================="
echo ""
echo "Remaining branches:"
git branch --list | sed 's/^/  /'



