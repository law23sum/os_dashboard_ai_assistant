#!/bin/bash
# Final merge into incremeents and cleanup

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

SOURCE_BRANCH="integration/restore-pages-ia"
TARGET_BRANCH="incremeents"

echo "=================================================================================="
echo "Merge $SOURCE_BRANCH into $TARGET_BRANCH"
echo "=================================================================================="

# Check if incremeents exists
if ! git show-ref --verify --quiet refs/heads/$TARGET_BRANCH; then
    echo "Creating $TARGET_BRANCH from $SOURCE_BRANCH..."
    git checkout -b $TARGET_BRANCH $SOURCE_BRANCH
    echo "✓ Created $TARGET_BRANCH with all merged pages"
else
    echo "Note: $TARGET_BRANCH exists but may be in a worktree."
    echo "To merge manually:"
    echo "  1. cd to incremeents worktree directory"
    echo "  2. git merge $SOURCE_BRANCH -X theirs"
    echo "  3. Resolve conflicts preferring $SOURCE_BRANCH files"
    echo ""
    echo "Or merge from current location:"
    echo "  git checkout $TARGET_BRANCH"
    echo "  git merge $SOURCE_BRANCH -X theirs"
fi

echo ""
echo "=================================================================================="
echo "Cleanup: Delete merged branches"
echo "=================================================================================="

PROTECTED_BRANCHES="develop main dying incremeents $SOURCE_BRANCH"

# Get list of branches to delete
BRANCHES_TO_DELETE=$(git branch | grep -v -E "($(echo $PROTECTED_BRANCHES | tr ' ' '|'))" | grep -v '\*' | sed 's/^[[:space:]]*//')

if [ -z "$BRANCHES_TO_DELETE" ]; then
    echo "No branches to delete (all protected or already deleted)"
else
    echo "Branches to delete:"
    echo "$BRANCHES_TO_DELETE" | sed 's/^/  - /'
    echo ""
    echo "To delete all (be careful!):"
    echo "$BRANCHES_TO_DELETE" | while read branch; do
        if [ -n "$branch" ]; then
            echo "  git branch -D $branch"
        fi
    done
fi

echo ""
echo "=================================================================================="
echo "Summary"
echo "=================================================================================="
PAGE_COUNT=$(git ls-tree -r --name-only $SOURCE_BRANCH frontend/src/pages/ 2>/dev/null | grep -E '\.tsx$' | wc -l | tr -d ' ')
echo "Source branch ($SOURCE_BRANCH): $PAGE_COUNT pages"
echo ""
echo "Next steps:"
echo "  1. Merge $SOURCE_BRANCH into incremeents (manually if in worktree)"
echo "  2. Verify navigation structure (Platforms→Categories→Features)"
echo "  3. Verify Personal/Enterprise actor switch works"
echo "  4. Delete merged branches"



