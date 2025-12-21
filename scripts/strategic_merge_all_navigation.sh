#!/bin/bash
# Strategic merge of all navigation branches into incremeents
# Preserves maximum pages, categories, and platforms

set -e

BRANCHES_TO_MERGE=(
    "ia-reorg-merge-20251221"
    "fix/restore-gui-glory"
    "fix/restore-gui-glory-20251220"
    "gui-fully-restored"
    "integration/codex-ia-restore-final"
    "integration/ia-navigation-final"
    "integration/merge-gui-commits-20251221"
    "fix/ia-navigation-merge"
    "integration/restore-pages-ia-v2"
    "integration/restore-pages-ia-ktg"
)

KEEP_BRANCHES=("main" "develop" "dying" "incremeents")

echo "=== Strategic Navigation Merge ==="
echo "Current branch: $(git branch --show-current)"
echo ""

# Ensure we're on incremeents
if [ "$(git branch --show-current)" != "incremeents" ]; then
    echo "Switching to incremeents branch..."
    git checkout incremeents
fi

# Stash any uncommitted changes
if ! git diff-index --quiet HEAD --; then
    echo "Stashing uncommitted changes..."
    git stash push -m "Pre-merge stash: saving state before strategic navigation merge"
fi

# Merge each branch strategically
for branch in "${BRANCHES_TO_MERGE[@]}"; do
    if git show-ref --verify --quiet refs/heads/"$branch"; then
        echo ""
        echo "=== Merging $branch ==="
        
        # Try to merge
        if git merge --no-edit --no-ff "$branch" -m "Merge $branch: Preserve maximum pages/categories/platforms" 2>&1 | tee /tmp/merge_output.log; then
            echo "✓ Successfully merged $branch"
        else
            # Handle conflicts
            echo "⚠ Conflicts detected in $branch"
            
            # List conflicts
            echo "Conflicting files:"
            git diff --name-only --diff-filter=U
            
            # Strategy: prefer files with more content (more pages/features)
            echo "Resolving conflicts in favor of maximum content..."
            
            # For navigation files, prefer the version with more features
            for file in $(git diff --name-only --diff-filter=U | grep -E "(gui_nav|navigation|nav)"); do
                echo "  Resolving $file..."
                # Count features in both versions
                ours_count=$(git show :2:"$file" 2>/dev/null | grep -c '"title"' || echo 0)
                theirs_count=$(git show :3:"$file" 2>/dev/null | grep -c '"title"' || echo 0)
                
                if [ "$theirs_count" -gt "$ours_count" ]; then
                    echo "    Using theirs ($theirs_count features vs $ours_count)"
                    git checkout --theirs "$file"
                else
                    echo "    Using ours ($ours_count features vs $theirs_count)"
                    git checkout --ours "$file"
                fi
            done
            
            # For page files, prefer the version that exists
            for file in $(git diff --name-only --diff-filter=U | grep -E "pages/.*\.tsx$"); do
                if [ -f "$file" ]; then
                    echo "  Keeping existing $file"
                    git add "$file"
                else
                    echo "  Adding new $file"
                    git checkout --theirs "$file" 2>/dev/null || git checkout --ours "$file" 2>/dev/null || true
                    git add "$file" 2>/dev/null || true
                fi
            done
            
            # For other files, prefer the version with more content
            for file in $(git diff --name-only --diff-filter=U | grep -v -E "(gui_nav|navigation|nav|pages/)"); do
                ours_size=$(git show :2:"$file" 2>/dev/null | wc -l || echo 0)
                theirs_size=$(git show :3:"$file" 2>/dev/null | wc -l || echo 0)
                
                if [ "$theirs_size" -gt "$ours_size" ]; then
                    git checkout --theirs "$file"
                else
                    git checkout --ours "$file"
                fi
                git add "$file"
            done
            
            # Complete the merge
            git commit --no-edit -m "Merge $branch: Resolved conflicts, preserved maximum content"
            echo "✓ Resolved conflicts and merged $branch"
        fi
    else
        echo "⚠ Branch $branch does not exist locally, skipping..."
    fi
done

# Update navigation JSON with merged version
if [ -f "merged_navigation.json" ]; then
    echo ""
    echo "=== Updating navigation JSON ==="
    
    # Find the best location for navigation JSON
    if [ -f "frontend/public/gui_nav.latest.json" ]; then
        cp merged_navigation.json frontend/public/gui_nav.latest.json
        echo "Updated frontend/public/gui_nav.latest.json"
    fi
    
    if [ -f "frontend/src/data/gui_nav.latest.json" ]; then
        cp merged_navigation.json frontend/src/data/gui_nav.latest.json
        echo "Updated frontend/src/data/gui_nav.latest.json"
    fi
    
    if [ -f "documentation/gui_nav_structure/gui_nav.latest.json" ]; then
        cp merged_navigation.json documentation/gui_nav_structure/gui_nav.latest.json
        echo "Updated documentation/gui_nav_structure/gui_nav.latest.json"
    fi
    
    git add frontend/public/gui_nav.latest.json frontend/src/data/gui_nav.latest.json documentation/gui_nav_structure/gui_nav.latest.json 2>/dev/null || true
    git commit -m "Update navigation JSON with merged structure (569 features)" || true
fi

echo ""
echo "=== Merge Complete ==="
echo "All navigation branches merged into incremeents"
echo ""
echo "Next: Clean up branches (run cleanup script)"



