#!/bin/bash
# Cleanup merged branches - Keep only develop, main, dying, incremeents

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# Branches to keep
KEEP_BRANCHES=("develop" "main" "dying" "incremeents")

echo "==================================================================="
echo "CLEANUP MERGED BRANCHES"
echo "==================================================================="
echo ""
echo "This script will delete all local branches except:"
for branch in "${KEEP_BRANCHES[@]}"; do
  echo "  - $branch"
done
echo ""

# Get current branch
CURRENT_BRANCH=$(git branch --show-current)
echo "Current branch: $CURRENT_BRANCH"
echo ""

# Ensure we're not on a branch we want to delete
if [[ ! " ${KEEP_BRANCHES[@]} " =~ " ${CURRENT_BRANCH} " ]]; then
  echo "⚠️  WARNING: You are on branch '$CURRENT_BRANCH' which will be deleted!"
  echo "Switching to 'incremeents' branch..."
  git checkout incremeents
fi

# Get all local branches
ALL_BRANCHES=($(git branch --format='%(refname:short)'))

# Find branches to delete
TO_DELETE=()
for branch in "${ALL_BRANCHES[@]}"; do
  if [[ ! " ${KEEP_BRANCHES[@]} " =~ " ${branch} " ]]; then
    TO_DELETE+=("$branch")
  fi
done

if [ ${#TO_DELETE[@]} -eq 0 ]; then
  echo "✅ No branches to delete. All branches are in the keep list."
  exit 0
fi

echo "Branches to be deleted (${#TO_DELETE[@]} total):"
for branch in "${TO_DELETE[@]}"; do
  # Check if branch is merged
  if git branch --merged incremeents | grep -q "^[ *]*${branch}$"; then
    echo "  ✓ $branch (merged)"
  else
    echo "  ⚠ $branch (not merged - will force delete)"
  fi
done
echo ""

read -p "Do you want to proceed? (yes/no): " -r
echo
if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
  echo "Aborted."
  exit 1
fi

# Delete branches
DELETED=0
FAILED=0

for branch in "${TO_DELETE[@]}"; do
  if git branch --merged incremeents | grep -q "^[ *]*${branch}$"; then
    # Branch is merged, safe to delete
    if git branch -d "$branch" 2>/dev/null; then
      echo "✅ Deleted merged branch: $branch"
      ((DELETED++))
    else
      echo "⚠️  Failed to delete (may have unmerged changes): $branch"
      read -p "Force delete? (yes/no): " -r
      if [[ $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        if git branch -D "$branch" 2>/dev/null; then
          echo "✅ Force deleted: $branch"
          ((DELETED++))
        else
          echo "❌ Failed to force delete: $branch"
          ((FAILED++))
        fi
      else
        ((FAILED++))
      fi
    fi
  else
    # Branch not merged, ask for confirmation
    echo "⚠️  Branch '$branch' is not merged into incremeents"
    read -p "Delete anyway? (yes/no): " -r
    if [[ $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
      if git branch -D "$branch" 2>/dev/null; then
        echo "✅ Force deleted: $branch"
        ((DELETED++))
      else
        echo "❌ Failed to delete: $branch"
        ((FAILED++))
      fi
    else
      echo "⏭️  Skipped: $branch"
      ((FAILED++))
    fi
  fi
done

echo ""
echo "==================================================================="
echo "CLEANUP SUMMARY"
echo "==================================================================="
echo "Deleted: $DELETED branches"
echo "Failed/Skipped: $FAILED branches"
echo ""
echo "Remaining branches:"
git branch --format='%(refname:short)' | while read branch; do
  echo "  - $branch"
done
