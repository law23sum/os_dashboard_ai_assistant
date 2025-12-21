#!/usr/bin/env python3
"""
Analyze branches to find those with maximum pages, categories, and platforms.
Merge strategy: favor branches with most complete navigation structure.
"""

import subprocess
import json
import os
from pathlib import Path
from collections import defaultdict

def run_git(cmd):
    """Run git command and return output."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running {cmd}: {e.stderr}")
        return ""

def get_branch_list():
    """Get list of local branches."""
    branches = run_git("git branch --format='%(refname:short)'")
    return [b.strip() for b in branches.split('\n') if b.strip()]

def count_pages_in_branch(branch):
    """Count pages in a branch by checking frontend/src/pages directory."""
    try:
        # Checkout branch temporarily (using git show)
        pages_dir = "frontend/src/pages"
        result = run_git(f"git ls-tree -r --name-only {branch} {pages_dir} 2>/dev/null | grep -E '\\.tsx?$' | wc -l")
        return int(result) if result.isdigit() else 0
    except:
        return 0

def count_nav_items_in_branch(branch):
    """Count navigation items (platforms, categories, features) in a branch."""
    try:
        nav_file = "frontend/public/gui_nav.latest.json"
        content = run_git(f"git show {branch}:{nav_file} 2>/dev/null")
        if not content:
            return {"platforms": 0, "categories": 0, "features": 0}
        
        data = json.loads(content)
        platforms = 0
        categories = 0
        features = 0
        
        for edition, edition_data in data.items():
            platforms += len(edition_data)
            for platform, platform_data in edition_data.items():
                categories += len(platform_data)
                for category, category_features in platform_data.items():
                    if isinstance(category_features, list):
                        features += len(category_features)
        
        return {"platforms": platforms, "categories": categories, "features": features}
    except Exception as e:
        print(f"Error analyzing {branch}: {e}")
        return {"platforms": 0, "categories": 0, "features": 0}

def analyze_branches():
    """Analyze all branches and rank them by completeness."""
    branches = get_branch_list()
    
    # Exclude branches we want to keep
    exclude = {"incremeents", "develop", "main", "dying"}
    branches = [b for b in branches if b not in exclude]
    
    results = []
    
    print("Analyzing branches...")
    for branch in branches:
        print(f"  Analyzing {branch}...")
        page_count = count_pages_in_branch(branch)
        nav_counts = count_nav_items_in_branch(branch)
        
        # Calculate score: prioritize features > categories > platforms > pages
        score = (
            nav_counts["features"] * 1000 +
            nav_counts["categories"] * 100 +
            nav_counts["platforms"] * 10 +
            page_count
        )
        
        results.append({
            "branch": branch,
            "pages": page_count,
            "platforms": nav_counts["platforms"],
            "categories": nav_counts["categories"],
            "features": nav_counts["features"],
            "score": score
        })
    
    # Sort by score descending
    results.sort(key=lambda x: x["score"], reverse=True)
    
    return results

def main():
    print("Branch Analysis for Merge Strategy")
    print("=" * 60)
    
    results = analyze_branches()
    
    print("\nTop branches by completeness:")
    print("-" * 60)
    print(f"{'Branch':<40} {'Pages':<8} {'Platforms':<10} {'Categories':<12} {'Features':<10} {'Score':<10}")
    print("-" * 60)
    
    for r in results[:20]:  # Top 20
        print(f"{r['branch']:<40} {r['pages']:<8} {r['platforms']:<10} {r['categories']:<12} {r['features']:<10} {r['score']:<10}")
    
    # Save results
    with open("branch_analysis_merge.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to branch_analysis_merge.json")
    print(f"\nRecommended branches to merge (top 5):")
    for i, r in enumerate(results[:5], 1):
        print(f"  {i}. {r['branch']} (score: {r['score']})")

if __name__ == "__main__":
    main()



