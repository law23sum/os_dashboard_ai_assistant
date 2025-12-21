#!/usr/bin/env python3
"""
Analyze branches by reading files directly from git without checking out.
Compares navigation JSON files and page counts across branches.
"""

import subprocess
import json
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict

def run_git_command(cmd: List[str]) -> str:
    """Run a git command and return output."""
    try:
        result = subprocess.run(
            ['git'] + cmd,
            capture_output=True,
            text=True,
            check=True,
            cwd=Path(__file__).parent.parent
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return ""

def get_all_branches() -> List[str]:
    """Get all local branches."""
    output = run_git_command(['branch', '--format=%(refname:short)'])
    branches = [b.strip() for b in output.split('\n') if b.strip()]
    exclude = {'develop', 'main', 'dying', 'incremeents'}
    return [b for b in branches if b not in exclude]

def read_file_from_branch(branch: str, file_path: str) -> str:
    """Read a file from a specific branch."""
    try:
        return run_git_command(['show', f'{branch}:{file_path}'])
    except:
        return ""

def analyze_nav_json(content: str) -> Dict:
    """Analyze navigation JSON content."""
    stats = {
        'platforms': 0,
        'categories': 0,
        'features': 0,
        'editions': 0,
        'platform_names': set(),
        'category_names': set(),
        'feature_paths': set(),
        'valid': False
    }
    
    if not content:
        return stats
    
    try:
        data = json.loads(content)
        stats['valid'] = True
        stats['editions'] = len(data)
        
        for edition_name, platforms in data.items():
            stats['platforms'] += len(platforms)
            for platform_name, categories in platforms.items():
                stats['platform_names'].add(platform_name)
                stats['categories'] += len(categories)
                for category_name, features in categories.items():
                    stats['category_names'].add(f"{platform_name}::{category_name}")
                    if isinstance(features, list):
                        stats['features'] += len(features)
                        for feature in features:
                            if isinstance(feature, dict) and 'path' in feature:
                                stats['feature_paths'].add(feature['path'])
    
    except Exception as e:
        print(f"Error parsing JSON: {e}")
    
    return stats

def count_pages_in_branch(branch: str) -> int:
    """Count pages in a branch by listing files."""
    try:
        output = run_git_command(['ls-tree', '-r', '--name-only', branch, 'frontend/src/pages'])
        if not output:
            return 0
        files = [f for f in output.split('\n') if f.endswith('.tsx') and not f.startswith('.')]
        return len(files)
    except:
        return 0

def get_unique_pages(branch: str) -> Set[str]:
    """Get unique page paths from a branch."""
    try:
        output = run_git_command(['ls-tree', '-r', '--name-only', branch, 'frontend/src/pages'])
        if not output:
            return set()
        files = {f for f in output.split('\n') if f.endswith('.tsx') and not f.startswith('.')}
        return files
    except:
        return set()

def analyze_branch(branch: str) -> Dict:
    """Analyze a branch."""
    print(f"Analyzing branch: {branch}")
    
    # Try multiple nav file locations
    nav_files = [
        'frontend/public/gui_nav.latest.json',
        'documentation/gui_nav_structure/gui_nav.latest.json',
    ]
    
    best_stats = None
    best_content = None
    
    for nav_file in nav_files:
        content = read_file_from_branch(branch, nav_file)
        if content:
            stats = analyze_nav_json(content)
            if stats['valid']:
                if best_stats is None or stats['features'] > best_stats['features']:
                    best_stats = stats
                    best_content = content
    
    if best_stats is None:
        return {
            'branch': branch,
            'error': 'no_nav_file',
            'platforms': 0,
            'categories': 0,
            'features': 0,
            'pages': 0
        }
    
    # Count pages
    pages = count_pages_in_branch(branch)
    unique_pages = get_unique_pages(branch)
    
    result = {
        'branch': branch,
        'platforms': best_stats['platforms'],
        'categories': best_stats['categories'],
        'features': best_stats['features'],
        'editions': best_stats['editions'],
        'pages': pages,
        'unique_pages': len(unique_pages),
        'platform_names': list(best_stats['platform_names']),
        'category_count': len(best_stats['category_names']),
        'feature_paths_count': len(best_stats['feature_paths']),
        'score': best_stats['platforms'] * 1000 + best_stats['categories'] * 100 + best_stats['features'] + pages,
        'nav_content': best_content[:500] if best_content else None  # First 500 chars for comparison
    }
    
    print(f"  Platforms: {result['platforms']}, Categories: {result['categories']}, Features: {result['features']}, Pages: {result['pages']}")
    
    return result

def main():
    """Main analysis function."""
    print("Analyzing branches by reading files directly from git...")
    
    branches = get_all_branches()
    print(f"Found {len(branches)} branches to analyze\n")
    
    results = []
    for branch in branches:
        result = analyze_branch(branch)
        results.append(result)
    
    # Sort by score
    results.sort(key=lambda x: x.get('score', 0), reverse=True)
    
    # Print summary
    print("\n" + "="*100)
    print("BRANCH ANALYSIS SUMMARY")
    print("="*100)
    print(f"{'Branch':<45} {'Plat':<6} {'Cat':<6} {'Feat':<6} {'Pages':<8} {'Unique':<8} {'Score':<10}")
    print("-"*100)
    
    for r in results:
        if 'error' not in r:
            print(f"{r['branch']:<45} {r['platforms']:<6} {r['categories']:<6} {r['features']:<6} {r['pages']:<8} {r['unique_pages']:<8} {r['score']:<10}")
        else:
            print(f"{r['branch']:<45} ERROR: {r['error']}")
    
    # Save results
    output_file = Path(__file__).parent.parent / 'branch_content_analysis.json'
    # Remove nav_content from saved results (too large)
    for r in results:
        if 'nav_content' in r:
            del r['nav_content']
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to: {output_file}")
    
    # Find branches with unique content
    print("\nBranches with most complete navigation:")
    top_branches = [r for r in results if 'error' not in r][:10]
    for i, r in enumerate(top_branches, 1):
        print(f"  {i}. {r['branch']} - {r['platforms']} platforms, {r['categories']} categories, {r['features']} features, {r['pages']} pages")
    
    return results

if __name__ == '__main__':
    main()

