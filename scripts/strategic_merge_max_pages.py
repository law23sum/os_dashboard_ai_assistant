#!/usr/bin/env python3
"""
Strategic Merge Script - Maximize Pages, Categories, and Platforms
Merges branches into incremeents, preserving maximum content while following IA rules.
"""

import subprocess
import json
import os
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict

REPO_ROOT = Path(__file__).parent.parent

def run_git(cmd: List[str], check: bool = True) -> str:
    """Run git command and return output"""
    try:
        result = subprocess.run(
            ["git"] + cmd,
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=check
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        if check:
            raise
        return ""

def get_nav_structure_from_branch(branch: str) -> Dict:
    """Extract navigation structure from a branch"""
    nav_files = [
        "frontend/public/gui_nav.latest.json",
        "documentation/gui_nav_structure/gui_nav.latest.json",
        "frontend/src/data/iaManifest.complete.ts",
    ]
    
    for nav_file in nav_files:
        try:
            content = run_git(["show", f"{branch}:{nav_file}"], check=False)
            if content and nav_file.endswith(".json"):
                return json.loads(content)
        except:
            continue
    return {}

def count_nav_items(nav_data: Dict) -> Dict[str, int]:
    """Count platforms, categories, and features in navigation structure"""
    if not nav_data:
        return {"platforms": 0, "categories": 0, "features": 0, "total": 0}
    
    platforms = set()
    categories = set()
    features = set()
    
    for edition_name, edition_data in nav_data.items():
        if isinstance(edition_data, dict):
            for platform_name, platform_data in edition_data.items():
                platforms.add(platform_name)
                if isinstance(platform_data, dict):
                    for category_name, category_data in platform_data.items():
                        categories.add(f"{platform_name}/{category_name}")
                        if isinstance(category_data, list):
                            for feature in category_data:
                                if isinstance(feature, dict):
                                    title = feature.get("title", "")
                                    path = feature.get("path", "")
                                    if title:
                                        features.add(f"{category_name}/{title}")
    
    total = len(platforms) + len(categories) + len(features)
    return {
        "platforms": len(platforms),
        "categories": len(categories),
        "features": len(features),
        "total": total
    }

def count_pages_in_branch(branch: str) -> int:
    """Count TSX page files in a branch"""
    try:
        files = run_git(["ls-tree", "-r", "--name-only", branch, "frontend/src/pages"], check=False)
        tsx_files = [f for f in files.split("\n") if f.endswith(".tsx") and "RouteScaffold" not in f]
        return len(tsx_files)
    except:
        return 0

def analyze_branches() -> List[Tuple[str, Dict]]:
    """Analyze all relevant branches and return stats"""
    branches_to_check = [
        "incremeents",
        "gui-restore-stable-3a154a6",
        "fix/restore-gui-glory-20251220",
        "integration/restore-pages-ia-codex",
        "integration/restore-pages-ia-ktg",
        "integration/restore-pages-ia-v2",
        "integration/ia-navigation-final",
        "integration/codex-ia-restore-final",
        "restore-gui-fix",
        "restore-ui",
        "gui-fully-restored",
    ]
    
    results = []
    for branch in branches_to_check:
        # Check if branch exists
        if not run_git(["show-ref", "--verify", "--quiet", f"refs/heads/{branch}"], check=False):
            continue
        
        nav_data = get_nav_structure_from_branch(branch)
        nav_counts = count_nav_items(nav_data)
        page_count = count_pages_in_branch(branch)
        
        results.append((
            branch,
            {
                **nav_counts,
                "pages": page_count,
                "score": nav_counts["total"] + page_count
            }
        ))
    
    return sorted(results, key=lambda x: x[1]["score"], reverse=True)

def merge_branch_strategically(target_branch: str, source_branch: str) -> bool:
    """Merge source branch into target, preserving maximum content"""
    print(f"\n{'='*60}")
    print(f"Merging {source_branch} into {target_branch}")
    print(f"{'='*60}")
    
    # Checkout target branch
    run_git(["checkout", target_branch])
    
    # Try merge with strategy to favor maximum content
    try:
        # Use ours strategy for conflicts, but we'll manually resolve to keep max content
        result = run_git(["merge", "--no-commit", "--no-ff", source_branch], check=False)
        
        # Check for conflicts
        conflicts = run_git(["diff", "--name-only", "--diff-filter=U"], check=False)
        if conflicts:
            print(f"Conflicts detected in: {conflicts.split()}")
            # For now, we'll use a strategy that keeps both sides where possible
            # This is a simplified approach - in reality, we'd need more sophisticated conflict resolution
            return False
        else:
            # No conflicts, commit the merge
            run_git(["commit", "-m", f"Merge {source_branch}: Preserve maximum pages/categories/platforms"])
            return True
    except Exception as e:
        print(f"Merge failed: {e}")
        run_git(["merge", "--abort"], check=False)
        return False

def main():
    """Main execution"""
    print("Analyzing branches for maximum content...")
    results = analyze_branches()
    
    print("\nBranch Analysis Results:")
    print("-" * 80)
    for branch, stats in results:
        print(f"{branch:40} | Pages: {stats['pages']:4} | Platforms: {stats['platforms']:2} | "
              f"Categories: {stats['categories']:3} | Features: {stats['features']:4} | "
              f"Score: {stats['score']}")
    
    # Get top branches to merge
    current_branch = "incremeents"
    top_branches = [b for b, s in results if b != current_branch and s["score"] > 0][:5]
    
    print(f"\nMerging top branches into {current_branch}...")
    for branch in top_branches:
        if merge_branch_strategically(current_branch, branch):
            print(f"✓ Successfully merged {branch}")
        else:
            print(f"✗ Failed to merge {branch} (conflicts need manual resolution)")

if __name__ == "__main__":
    main()


