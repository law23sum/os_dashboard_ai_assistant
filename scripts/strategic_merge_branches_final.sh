#!/bin/bash
# Strategic merge of branches with most complete navigation structure into incremeents
# Preserves maximum platforms, categories, features, and pages

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# Branches to merge (prioritized by completeness)
# These branches have: 15 platforms, 66 categories, 504 features, 2112+ pages
BRANCHES_TO_MERGE=(
    "fix/ia-navigation-merge"
    "integration/ia-navigation-final"
    "integration/restore-pages-ia-codex"
    "integration/merge-gui-commits-20251221"
    "gui-restore-stable-3a154a6"
)

TARGET_BRANCH="incremeents"

echo "=================================================================================="
echo "Strategic Merge: Preserve Maximum Navigation Structure"
echo "=================================================================================="
echo "Target: $TARGET_BRANCH"
echo "Branches to merge: ${BRANCHES_TO_MERGE[@]}"
echo ""

# Ensure we're on incremeents
git checkout "$TARGET_BRANCH" || exit 1

# Merge each branch with strategy to preserve maximum content
for branch in "${BRANCHES_TO_MERGE[@]}"; do
    echo "----------------------------------------------------------------------------"
    echo "Merging: $branch"
    echo "----------------------------------------------------------------------------"
    
    # Check if branch exists
    if ! git show-ref --verify --quiet refs/heads/"$branch"; then
        echo "⚠ Branch $branch does not exist, skipping..."
        continue
    fi
    
    # Merge with ours strategy (keep current) but check for new content
    if git merge --no-edit --no-ff "$branch" -X ours 2>&1 | tee /tmp/merge_output.txt; then
        echo "✓ Successfully merged $branch"
    else
        # If merge failed, check for conflicts
        if grep -q "Automatic merge failed" /tmp/merge_output.txt; then
            echo "⚠ Merge conflict in $branch, resolving in favor of keeping all files..."
            
            # For navigation/config files, prefer the branch being merged
            for file in $(git diff --name-only --diff-filter=U | grep -E "(gui_nav|navigation|pages)"); do
                echo "  Resolving $file in favor of $branch..."
                git checkout --theirs "$file" 2>/dev/null || true
                git add "$file" 2>/dev/null || true
            done
            
            # Try to complete merge
            if git commit --no-edit 2>&1; then
                echo "✓ Resolved conflicts and merged $branch"
            else
                echo "✗ Failed to resolve conflicts for $branch, aborting merge..."
                git merge --abort 2>/dev/null || true
            fi
        else
            echo "✗ Merge failed for $branch"
        fi
    fi
    
    echo ""
done

echo "=================================================================================="
echo "Merge Complete"
echo "=================================================================================="

# Verify navigation structure
if [ -f "frontend/public/gui_nav.latest.json" ]; then
    echo ""
    echo "Verifying navigation structure..."
    python3 -c "
import json
from pathlib import Path

nav_file = Path('frontend/public/gui_nav.latest.json')
if nav_file.exists():
    with open(nav_file) as f:
        data = json.load(f)
        platforms = set()
        categories = set()
        features = set()
        
        for edition, edition_data in data.items():
            for platform, platform_data in edition_data.items():
                platforms.add(f'{edition}::{platform}')
                if isinstance(platform_data, dict):
                    for category, items in platform_data.items():
                        categories.add(f'{platform}::{category}')
                        if isinstance(items, list):
                            for item in items:
                                if isinstance(item, dict):
                                    path = item.get('path', '')
                                    if path:
                                        features.add(path)
        
        print(f'Final Navigation Structure:')
        print(f'  Platforms: {len(platforms)}')
        print(f'  Categories: {len(categories)}')
        print(f'  Features: {len(features)}')
        print(f'  Total: {len(platforms) + len(categories) + len(features)}')
" || echo "Could not verify navigation structure"
fi

echo ""
echo "Next steps:"
echo "  1. Review merged changes"
echo "  2. Test navigation structure"
echo "  3. Delete merged branches (except develop, main, dying, incremeents)"




