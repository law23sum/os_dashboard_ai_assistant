#!/bin/bash
# Complete merge process and cleanup branches

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

CURRENT=$(git branch --show-current)
echo "Current branch: $CURRENT"

# Continue merging remaining branches
MERGE_BRANCHES=(
    "integration/merge-commits-preserve-pages"
    "integration/restore-pages-ia-codex-final"
    "integration/restore-pages-ia-codex"
    "integration/ia-navigation-final"
    "gui-fully-restored"
    "restore-gui-comprehensive"
    "integration/merge-gui-commits-20251221"
)

echo "Continuing merges..."
for branch in "${MERGE_BRANCHES[@]}"; do
    if ! git show-ref --verify --quiet refs/heads/$branch; then
        continue
    fi
    
    if git merge-base --is-ancestor $branch $CURRENT 2>/dev/null; then
        echo "  ✓ $branch already merged"
        continue
    fi
    
    echo "Merging $branch..."
    if git merge -X theirs -m "Merge $branch - maximize pages" $branch 2>&1; then
        echo "  ✓ Merged $branch"
    else
        echo "  ⚠ Conflicts, resolving..."
        git checkout --theirs frontend/src/pages/ 2>/dev/null || true
        git checkout --theirs frontend/src/nav/ 2>/dev/null || true
        git checkout --theirs frontend/src/config/ 2>/dev/null || true
        git checkout --theirs frontend/src/data/ 2>/dev/null || true
        git checkout --theirs frontend/src/components/PlatformNavIA.tsx 2>/dev/null || true
        git checkout --theirs frontend/src/components/CategorySidebarIA.tsx 2>/dev/null || true
        git checkout --theirs frontend/src/components/ActorSwitch.tsx 2>/dev/null || true
        git add . 2>/dev/null || true
        git commit -m "Merge $branch - resolved conflicts" 2>/dev/null || true
    fi
done

# Count final pages
FINAL_COUNT=$(git ls-tree -r --name-only $CURRENT frontend/src/pages/ 2>/dev/null | grep -E '\.tsx$' | wc -l | tr -d ' ')
echo ""
echo "Final page count: $FINAL_COUNT"

# Now merge into incremeents if possible
if git show-ref --verify --quiet refs/heads/incremeents; then
    echo ""
    echo "Attempting to merge into incremeents..."
    # Try to merge current into incremeents via worktree or direct
    echo "Note: incremeents is in a worktree. To complete:"
    echo "  1. cd to incremeents worktree"
    echo "  2. git merge $CURRENT"
    echo "  3. Resolve any conflicts preferring $CURRENT files"
fi

echo ""
echo "Branches to delete (run manually):"
git branch | grep -v -E '(develop|main|dying|incremeents|\*)' | sed 's/^/  git branch -D /'




