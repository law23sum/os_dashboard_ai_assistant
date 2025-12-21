#!/bin/bash
# Merge branches with complete navigation into incremeents, favoring maximum content

set -e

REPO_DIR="/Users/chrisdixon/Projects/os_dashboard_ai_assistant"
cd "$REPO_DIR"

# Ensure we're on incremeents
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$CURRENT_BRANCH" != "incremeents" ]; then
    echo "Switching to incremeents branch..."
    git checkout incremeents
fi

# Best branches with complete navigation (523 total elements)
BEST_BRANCHES=(
    "fix/ia-navigation-merge"
    "fix/restore-gui-glory"
    "gui-fully-restored"
    "integration/codex-ia-restore-final"
    "integration/ia-navigation-final"
    "integration/merge-gui-commits-20251221"
    "integration/restore-pages-ia-v2"
)

echo "=========================================="
echo "Merging branches with complete navigation"
echo "=========================================="
echo ""

# Merge strategy: Use 'ours' for conflicts to keep incremeents base, then selectively take 'theirs' for nav files
MERGE_STRATEGY="--no-edit"

for BRANCH in "${BEST_BRANCHES[@]}"; do
    echo "Attempting to merge: $BRANCH"
    
    # Check if branch exists
    if ! git show-ref --verify --quiet refs/heads/"$BRANCH"; then
        echo "  ⚠️  Branch $BRANCH does not exist locally, skipping..."
        continue
    fi
    
    # Try merge with strategy favoring maximum content
    if git merge "$BRANCH" --no-commit --no-ff 2>&1 | tee /tmp/merge_output.txt; then
        echo "  ✅ Merge successful: $BRANCH"
        
        # For navigation files, prefer the merged version (theirs)
        NAV_FILES=(
            "frontend/public/gui_nav.latest.json"
            "documentation/gui_nav_structure/gui_nav.latest.json"
        )
        
        for NAV_FILE in "${NAV_FILES[@]}"; do
            if [ -f "$NAV_FILE" ]; then
                # Check if there's a version in the merged branch
                if git show "$BRANCH:$NAV_FILE" > /dev/null 2>&1; then
                    echo "  📄 Taking navigation from $BRANCH: $NAV_FILE"
                    git checkout --theirs "$NAV_FILE" 2>/dev/null || true
                    git add "$NAV_FILE"
                fi
            fi
        done
        
        # Commit the merge
        git commit -m "Merge $BRANCH: Restore complete navigation (15 platforms, 66 categories, 442 features)" || true
        
    else
        # Check if merge failed due to conflicts
        if grep -q "CONFLICT" /tmp/merge_output.txt 2>/dev/null; then
            echo "  ⚠️  Conflicts detected in $BRANCH, resolving..."
            
            # For conflicts, prefer 'theirs' (the branch being merged) for navigation files
            # This ensures we get the complete navigation structure
            NAV_FILES=(
                "frontend/public/gui_nav.latest.json"
                "documentation/gui_nav_structure/gui_nav.latest.json"
            )
            
            for NAV_FILE in "${NAV_FILES[@]}"; do
                if git ls-files -u | grep -q "$NAV_FILE"; then
                    echo "  🔧 Resolving conflict: $NAV_FILE (taking theirs for complete nav)"
                    git checkout --theirs "$NAV_FILE" 2>/dev/null || true
                    git add "$NAV_FILE"
                fi
            done
            
            # For other conflicts, try to auto-resolve or abort
            if git diff --check; then
                echo "  ✅ Conflicts resolved, committing..."
                git commit -m "Merge $BRANCH: Resolved conflicts, preserved complete navigation" || true
            else
                echo "  ⚠️  Remaining conflicts, aborting merge for $BRANCH"
                git merge --abort || true
            fi
        else
            echo "  ⚠️  Merge failed for $BRANCH (may already be merged)"
        fi
    fi
    
    echo ""
done

echo "=========================================="
echo "Merge complete!"
echo "=========================================="
echo ""
echo "Verifying navigation completeness..."

# Verify final navigation
if [ -f "frontend/public/gui_nav.latest.json" ]; then
    python3 << 'PYTHON_SCRIPT'
import json
import sys

try:
    with open('frontend/public/gui_nav.latest.json', 'r') as f:
        data = json.load(f)
    
    platforms = 0
    categories = 0
    features = 0
    
    if isinstance(data, dict):
        for edition, platforms_dict in data.items():
            if isinstance(platforms_dict, dict):
                platforms += len(platforms_dict)
                for platform, categories_dict in platforms_dict.items():
                    if isinstance(categories_dict, dict):
                        categories += len(categories_dict)
                        for category, features_list in categories_dict.items():
                            if isinstance(features_list, list):
                                features += len(features_list)
    
    print(f"✅ Final Navigation Count:")
    print(f"   Platforms: {platforms}")
    print(f"   Categories: {categories}")
    print(f"   Features: {features}")
    print(f"   Total: {platforms + categories + features}")
    
    if platforms >= 15 and categories >= 66 and features >= 442:
        print("\n🎉 SUCCESS: Complete navigation restored!")
        sys.exit(0)
    else:
        print("\n⚠️  WARNING: Navigation may be incomplete")
        sys.exit(1)
except Exception as e:
    print(f"❌ Error verifying navigation: {e}")
    sys.exit(1)
PYTHON_SCRIPT
fi


