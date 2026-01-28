#!/usr/bin/env python3
"""
Analyze branches for maximum platforms, categories, and features.
Then merge them into incremeents branch preserving maximum pages.
"""

import json
import subprocess
import sys
from pathlib import Path
from collections import defaultdict

def run_git(cmd, check=True):
    """Run git command and return output"""
    result = subprocess.run(
        f"git {cmd}",
        shell=True,
        capture_output=True,
        text=True,
        check=check
    )
    return result.stdout.strip()

def get_branch_commits(branch):
    """Get commit hashes for a branch"""
    try:
        output = run_git(f"log {branch} --oneline -20", check=False)
        return [line.split()[0] for line in output.split('\n') if line]
    except:
        return []

def analyze_nav_json(file_path):
    """Analyze navigation JSON to count platforms, categories, features"""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        platforms = list(data.keys()) if isinstance(data, dict) else []
        categories = []
        features = []
        
        for platform_name, platform_data in data.items():
            if isinstance(platform_data, dict):
                for category_name, category_data in platform_data.items():
                    categories.append(f"{platform_name}/{category_name}")
                    if isinstance(category_data, list):
                        features.extend(category_data)
        
        return {
            'platforms': len(platforms),
            'categories': len(categories),
            'features': len(features),
            'platform_names': platforms,
            'category_names': categories
        }
    except Exception as e:
        return {'platforms': 0, 'categories': 0, 'features': 0, 'error': str(e)}

def checkout_branch(branch):
    """Checkout a branch"""
    print(f"Checking out {branch}...")
    run_git(f"checkout {branch}")
    run_git("status")

def get_nav_file_in_branch(branch, path="frontend/public/gui_nav.latest.json"):
    """Get navigation file content from a branch"""
    try:
        output = run_git(f"show {branch}:{path}", check=False)
        if output and not output.startswith("fatal:"):
            return output
        # Try alternative locations
        for alt_path in [
            "documentation/gui_nav_structure/gui_nav.latest.json",
            "frontend/src/data/gui_nav.latest.json"
        ]:
            output = run_git(f"show {branch}:{alt_path}", check=False)
            if output and not output.startswith("fatal:"):
                return output
        return None
    except:
        return None

def analyze_branches():
    """Analyze all branches for navigation completeness"""
    branches_to_check = [
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
    ]
    
    current_branch = run_git("branch --show-current")
    print(f"Current branch: {current_branch}")
    
    results = {}
    
    for branch in branches_to_check:
        print(f"\n{'='*60}")
        print(f"Analyzing branch: {branch}")
        print(f"{'='*60}")
        
        # Check if branch exists
        branch_exists = run_git(f"show-ref --verify --quiet refs/heads/{branch}", check=False)
        if branch_exists != 0:
            print(f"  Branch {branch} does not exist locally, skipping...")
            continue
        
        # Get navigation file from branch
        nav_content = get_nav_file_in_branch(branch)
        if nav_content:
            # Write to temp file for analysis
            temp_file = Path(f"/tmp/nav_{branch.replace('/', '_')}.json")
            temp_file.write_text(nav_content)
            stats = analyze_nav_json(str(temp_file))
            results[branch] = stats
            print(f"  Platforms: {stats['platforms']}")
            print(f"  Categories: {stats['categories']}")
            print(f"  Features: {stats['features']}")
            if 'error' in stats:
                print(f"  Error: {stats['error']}")
        else:
            print(f"  No navigation JSON found in {branch}")
            results[branch] = {'platforms': 0, 'categories': 0, 'features': 0, 'error': 'No nav JSON'}
    
    return results, current_branch

def merge_strategy(results):
    """Determine merge strategy based on results"""
    # Sort branches by total completeness (features + categories + platforms)
    scored = []
    for branch, stats in results.items():
        if 'error' not in stats:
            score = stats['features'] * 10 + stats['categories'] * 5 + stats['platforms']
            scored.append((score, branch, stats))
    
    scored.sort(reverse=True)
    
    print(f"\n{'='*60}")
    print("BRANCH RANKING BY COMPLETENESS")
    print(f"{'='*60}")
    for i, (score, branch, stats) in enumerate(scored[:10], 1):
        print(f"{i}. {branch}: {stats['features']} features, {stats['categories']} categories, {stats['platforms']} platforms (score: {score})")
    
    return scored

if __name__ == "__main__":
    print("Analyzing branches for maximum navigation completeness...")
    results, current_branch = analyze_branches()
    
    print(f"\n{'='*60}")
    print("ANALYSIS COMPLETE")
    print(f"{'='*60}")
    
    scored = merge_strategy(results)
    
    # Save results
    output_file = Path("branch_analysis_complete.json")
    output_data = {
        'analysis_date': run_git("log -1 --format=%ci", check=False),
        'current_branch': current_branch,
        'results': {b: {k: v for k, v in s.items() if k != 'platform_names' and k != 'category_names'} 
                   for b, s in results.items()},
        'ranking': [{'branch': b, 'score': s, 'stats': st} for s, b, st in scored]
    }
    output_file.write_text(json.dumps(output_data, indent=2))
    print(f"\nResults saved to {output_file}")


