#!/bin/bash
# Strategic merge of branches into incremeents, favoring maximum pages/categories/platforms

set -e

BRANCHES_TO_MERGE=(
    "ia-reorg-merge-20251221"
    "fix/restore-gui-glory"
    "fix/restore-gui-glory-20251220"
    "gui-fully-restored"
    "integration/codex-ia-restore-final"
    "integration/ia-navigation-final"
    "integration/merge-gui-commits-20251221"
    "integration/restore-pages-ia-v2"
    "integration/restore-pages-ia-ktg"
    "fix/ia-navigation-merge"
)

CURRENT_BRANCH=$(git branch --show-current)
echo "Current branch: $CURRENT_BRANCH"

if [ "$CURRENT_BRANCH" != "incremeents" ]; then
    echo "Switching to incremeents branch..."
    git checkout incremeents
fi

echo "Stashing any uncommitted changes..."
git stash push -m "Stash before strategic merge" || true

for BRANCH in "${BRANCHES_TO_MERGE[@]}"; do
    echo ""
    echo "=========================================="
    echo "Merging $BRANCH into incremeents..."
    echo "=========================================="
    
    # Check if branch exists
    if ! git show-ref --verify --quiet refs/heads/$BRANCH; then
        echo "Branch $BRANCH does not exist, skipping..."
        continue
    fi
    
    # Merge with strategy favoring maximum content
    # Use -X theirs for files that might conflict, but we'll review
    git merge --no-commit --no-ff $BRANCH -m "Merge $BRANCH: preserve maximum pages/categories/platforms" || {
        echo "Merge conflict detected for $BRANCH"
        echo "Resolving conflicts in favor of maximum content..."
        
        # For navigation files, prefer the version with more features
        if [ -f "frontend/public/gui_nav.latest.json" ]; then
            # Count features in both versions
            OUR_FEATURES=$(git show HEAD:frontend/public/gui_nav.latest.json 2>/dev/null | grep -o '"title"' | wc -l || echo "0")
            THEIR_FEATURES=$(git show $BRANCH:frontend/public/gui_nav.latest.json 2>/dev/null | grep -o '"title"' | wc -l || echo "0")
            
            if [ "$THEIR_FEATURES" -gt "$OUR_FEATURES" ]; then
                echo "  Using their version (more features: $THEIR_FEATURES vs $OUR_FEATURES)"
                git checkout --theirs frontend/public/gui_nav.latest.json
            else
                echo "  Using our version (more features: $OUR_FEATURES vs $THEIR_FEATURES)"
                git checkout --ours frontend/public/gui_nav.latest.json
            fi
        fi
        
        # For page files, prefer keeping both (add theirs)
        git add frontend/src/pages/*.tsx frontend/src/pages/**/*.tsx 2>/dev/null || true
        
        # Continue merge
        git commit -m "Merge $BRANCH: resolved conflicts favoring maximum content" || {
            echo "Failed to complete merge of $BRANCH"
            git merge --abort || true
            continue
        }
    }
    
    # If merge succeeded without conflicts, commit
    if git diff --cached --quiet && git diff --quiet; then
        echo "No changes from $BRANCH, skipping commit"
        git merge --abort 2>/dev/null || true
    else
        git commit -m "Merge $BRANCH: preserve maximum pages/categories/platforms" || true
    fi
    
    echo "Completed merge of $BRANCH"
done

echo ""
echo "=========================================="
echo "Strategic merge complete!"
echo "=========================================="
git log --oneline -10



