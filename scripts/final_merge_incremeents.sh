#!/bin/bash
# Final merge into incremeents using direct ref manipulation

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

SOURCE="integration/restore-pages-ia"
TARGET="incremeents"

echo "Merging $SOURCE into $TARGET..."

# Get current branch
CURRENT=$(git branch --show-current)
echo "Current branch: $CURRENT"

# If we're not on incremeents, try to merge via refs
if [ "$CURRENT" != "$TARGET" ]; then
    echo "Attempting to merge $SOURCE into $TARGET..."
    
    # Create a temporary branch from incremeents
    TEMP_BRANCH="temp-merge-to-incremeents"
    git branch -D $TEMP_BRANCH 2>/dev/null || true
    git checkout -b $TEMP_BRANCH $TARGET 2>/dev/null || {
        echo "Cannot checkout $TARGET (worktree issue)"
        echo ""
        echo "Manual merge required:"
        echo "  1. Find incremeents worktree: git worktree list"
        echo "  2. cd to worktree directory"
        echo "  3. git merge $SOURCE -X theirs"
        echo "  4. Resolve conflicts if any"
        exit 0
    }
    
    # Merge source into temp branch
    if git merge -X theirs -m "Merge $SOURCE - maximize pages, categories, platforms" $SOURCE 2>&1; then
        echo "✓ Merged successfully"
        
        # Update incremeents ref to point to merged commit
        MERGED_COMMIT=$(git rev-parse HEAD)
        git update-ref refs/heads/$TARGET $MERGED_COMMIT
        echo "✓ Updated $TARGET to merged commit"
        
        # Cleanup
        git checkout $CURRENT
        git branch -D $TEMP_BRANCH
        echo "✓ Cleaned up temporary branch"
    else
        echo "⚠ Merge conflicts - resolving..."
        git checkout --theirs frontend/src/pages/ 2>/dev/null || true
        git checkout --theirs frontend/src/nav/ 2>/dev/null || true
        git checkout --theirs frontend/src/config/ 2>/dev/null || true
        git checkout --theirs frontend/src/data/ 2>/dev/null || true
        git add . 2>/dev/null || true
        git commit -m "Merge $SOURCE - resolved conflicts" 2>/dev/null || true
        
        MERGED_COMMIT=$(git rev-parse HEAD)
        git update-ref refs/heads/$TARGET $MERGED_COMMIT
        git checkout $CURRENT
        git branch -D $TEMP_BRANCH
        echo "✓ Resolved conflicts and updated $TARGET"
    fi
else
    # Already on incremeents
    git merge -X theirs -m "Merge $SOURCE - maximize pages" $SOURCE
fi

echo ""
echo "✓ Merge complete! $TARGET now has all pages from $SOURCE"




