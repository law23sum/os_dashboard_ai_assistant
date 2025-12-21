#!/usr/bin/env python3
"""
Strategic Merge Script: Merge all branches with navigation structures into incremeents
Prioritizes maximum pages, categories, and platforms while maintaining IA compliance
"""

import subprocess
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict

REPO_ROOT = Path(__file__).parent.parent

# Key files to analyze for navigation completeness
NAV_FILES = [
    "frontend/public/gui_nav.latest.json",
    "frontend/src/data/iaManifest.complete.json",
    "frontend/src/data/iaCanonical.ts",
    "frontend/src/data/navigationStructure.ts",
    "documentation/gui_nav_structure/gui_nav.latest.json",
]

# Branches to analyze (from git branch output)
BRANCHES_TO_ANALYZE = [
    "fix/ia-navigation-merge",
    "fix/restore-gui-glory",
    "fix/restore-gui-glory-20251220",
    "gui-fully-restored",
    "gui-restore-3a154a6-work",
    "gui-restore-stable",
    "gui-restore-stable-3a154a6",
    "ia-reorg-merge-20251221",
    "integration/codex-ia-restore-final",
    "integration/ia-navigation-final",
    "integration/merge-gui-commits-20251221",
    "integration/restore-pages-ia-codex",
    "integration/restore-pages-ia-ktg",
    "integration/restore-pages-ia-v2",
    "restore-gui-fix",
    "restore-ui",
    "restore-gui-comprehensive",
]

def run_git(cmd: List[str], check=True) -> subprocess.CompletedProcess:
    """Run git command"""
    result = subprocess.run(
        ["git"] + cmd,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=check
    )
    return result

def count_nav_elements(branch: str) -> Dict[str, int]:
    """Count platforms, categories, and features in a branch"""
    counts = {
        "platforms": 0,
        "categories": 0,
        "features": 0,
        "pages": 0,
    }
    
    try:
        # Checkout branch temporarily
        run_git(["checkout", branch], check=False)
        
        # Count pages
        pages_dir = REPO_ROOT / "frontend" / "src" / "pages"
        if pages_dir.exists():
            page_files = list(pages_dir.rglob("*.tsx"))
            counts["pages"] = len(page_files)
        
        # Analyze navigation JSON files
        for nav_file in NAV_FILES:
            nav_path = REPO_ROOT / nav_file
            if nav_path.exists():
                try:
                    if nav_file.endswith(".json"):
                        with open(nav_path, "r") as f:
                            data = json.load(f)
                            counts = analyze_json_nav(data, counts)
                    elif nav_file.endswith(".ts"):
                        # Try to parse TS file for navigation structure
                        with open(nav_path, "r") as f:
                            content = f.read()
                            # Count platforms, categories, features in TS
                            counts["platforms"] += content.count("platform:")
                            counts["categories"] += content.count("category:")
                            counts["features"] += content.count("feature:")
                except Exception as e:
                    print(f"  Warning: Could not parse {nav_file}: {e}")
        
    except Exception as e:
        print(f"  Error analyzing branch {branch}: {e}")
    finally:
        # Return to incremeents
        run_git(["checkout", "incremeents"], check=False)
    
    return counts

def analyze_json_nav(data: Dict, counts: Dict) -> Dict:
    """Recursively analyze JSON navigation structure"""
    if isinstance(data, dict):
        # Check if this looks like a platform level
        if any(key in str(data.keys()) for key in ["Edition", "platform", "Platform"]):
            for key, value in data.items():
                if isinstance(value, dict):
                    # This might be a platform
                    counts["platforms"] += 1
                    counts = analyze_json_nav(value, counts)
        # Check for categories
        elif any(key in str(data.keys()) for key in ["category", "Category", "categories"]):
            counts["categories"] += 1
            for value in data.values():
                counts = analyze_json_nav(value, counts)
        # Check for features array
        elif isinstance(list(data.values())[0] if data.values() else None, list):
            # This might be a features array
            for value in data.values():
                if isinstance(value, list):
                    counts["features"] += len([v for v in value if isinstance(v, dict) and "path" in v])
        else:
            for value in data.values():
                counts = analyze_json_nav(value, counts)
    elif isinstance(data, list):
        for item in data:
            counts = analyze_json_nav(item, counts)
    
    return counts

def get_branch_scores() -> List[Tuple[str, Dict[str, int]]]:
    """Get scores for all branches"""
    print("Analyzing branches for navigation completeness...")
    scores = []
    
    for branch in BRANCHES_TO_ANALYZE:
        print(f"\nAnalyzing branch: {branch}")
        try:
            # Check if branch exists
            result = run_git(["show-ref", "--verify", "--quiet", f"refs/heads/{branch}"], check=False)
            if result.returncode != 0:
                print(f"  Branch {branch} does not exist, skipping")
                continue
            
            counts = count_nav_elements(branch)
            score = counts["platforms"] * 100 + counts["categories"] * 10 + counts["features"] + counts["pages"]
            counts["score"] = score
            scores.append((branch, counts))
            print(f"  Platforms: {counts['platforms']}, Categories: {counts['categories']}, "
                  f"Features: {counts['features']}, Pages: {counts['pages']}, Score: {score}")
        except Exception as e:
            print(f"  Error: {e}")
            continue
    
    return sorted(scores, key=lambda x: x[1]["score"], reverse=True)

def merge_branch_strategically(branch: str) -> bool:
    """Merge a branch into incremeents, prioritizing maximum content"""
    print(f"\n{'='*60}")
    print(f"Merging branch: {branch}")
    print(f"{'='*60}")
    
    try:
        # Ensure we're on incremeents
        run_git(["checkout", "incremeents"], check=True)
        
        # Merge with strategy to keep both sides when possible
        result = run_git([
            "merge", 
            "--no-ff",
            "--strategy-option=ours",  # Prefer our version for conflicts
            branch
        ], check=False)
        
        if result.returncode == 0:
            print(f"✅ Successfully merged {branch}")
            return True
        else:
            # Handle conflicts
            print(f"⚠️  Merge conflicts detected for {branch}")
            conflicts = run_git(["diff", "--name-only", "--diff-filter=U"], check=False)
            if conflicts.stdout:
                print(f"Conflicts in files:")
                print(conflicts.stdout)
            
            # Try to resolve by taking both sides where possible
            # For navigation files, we want to merge content, not replace
            nav_conflicts = [f for f in conflicts.stdout.split("\n") if "nav" in f.lower() or "ia" in f.lower()]
            
            if nav_conflicts:
                print(f"Navigation conflicts detected. Will merge content...")
                # For now, abort and handle manually
                run_git(["merge", "--abort"], check=False)
                return False
            else:
                # Accept ours for non-nav conflicts, then manually merge nav
                run_git(["checkout", "--ours", "."], check=False)
                run_git(["add", "."], check=False)
                run_git(["commit", "-m", f"Merge {branch} - resolved conflicts"], check=False)
                return True
                
    except Exception as e:
        print(f"❌ Error merging {branch}: {e}")
        run_git(["merge", "--abort"], check=False)
        return False

def main():
    """Main merge strategy"""
    print("="*60)
    print("STRATEGIC NAVIGATION MERGE")
    print("="*60)
    
    # Ensure we're on incremeents
    run_git(["checkout", "incremeents"], check=True)
    
    # Get branch scores
    scores = get_branch_scores()
    
    if not scores:
        print("\n❌ No branches found to analyze")
        return
    
    print("\n" + "="*60)
    print("BRANCH RANKINGS (by navigation completeness)")
    print("="*60)
    for i, (branch, counts) in enumerate(scores, 1):
        print(f"{i}. {branch}: Score={counts['score']} "
              f"(P:{counts['platforms']}, C:{counts['categories']}, "
              f"F:{counts['features']}, Pages:{counts['pages']})")
    
    # Merge top branches
    print("\n" + "="*60)
    print("MERGING BRANCHES (top to bottom)")
    print("="*60)
    
    merged = []
    failed = []
    
    for branch, counts in scores[:10]:  # Merge top 10
        if merge_branch_strategically(branch):
            merged.append(branch)
        else:
            failed.append(branch)
    
    print("\n" + "="*60)
    print("MERGE SUMMARY")
    print("="*60)
    print(f"✅ Successfully merged: {len(merged)} branches")
    for branch in merged:
        print(f"  - {branch}")
    
    if failed:
        print(f"\n⚠️  Failed to merge: {len(failed)} branches")
        for branch in failed:
            print(f"  - {branch}")
    
    print("\n✅ Merge process complete!")
    print("Next steps:")
    print("1. Review conflicts and manually merge navigation files")
    print("2. Verify all pages are present")
    print("3. Run tests to ensure IA compliance")

if __name__ == "__main__":
    main()


