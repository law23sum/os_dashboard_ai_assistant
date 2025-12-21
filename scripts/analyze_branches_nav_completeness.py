#!/usr/bin/env python3
"""
Analyze branches for navigation completeness.
Finds branches with maximum platforms, categories, and features.
"""

import subprocess
import json
import os
from pathlib import Path
from typing import Dict, List, Tuple
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
    except subprocess.CalledProcessError as e:
        print(f"Error running git command: {' '.join(cmd)}")
        print(f"Error: {e.stderr}")
        return ""

def get_all_branches() -> List[str]:
    """Get all local branches."""
    output = run_git_command(['branch', '--format=%(refname:short)'])
    branches = [b.strip() for b in output.split('\n') if b.strip()]
    # Filter out develop, main, dying, incremeents (keep these)
    exclude = {'develop', 'main', 'dying', 'incremeents'}
    return [b for b in branches if b not in exclude]

def checkout_branch(branch: str) -> bool:
    """Checkout a branch."""
    try:
        run_git_command(['checkout', branch])
        return True
    except:
        return False

def analyze_nav_json(file_path: Path) -> Dict[str, int]:
    """Analyze navigation JSON file for completeness."""
    stats = {
        'platforms': 0,
        'categories': 0,
        'features': 0,
        'editions': 0,
        'file_exists': False
    }
    
    if not file_path.exists():
        return stats
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        stats['file_exists'] = True
        stats['editions'] = len(data)
        
        for edition_name, platforms in data.items():
            stats['platforms'] += len(platforms)
            for platform_name, categories in platforms.items():
                stats['categories'] += len(categories)
                for category_name, features in categories.items():
                    if isinstance(features, list):
                        stats['features'] += len(features)
    
    except Exception as e:
        print(f"Error analyzing {file_path}: {e}")
    
    return stats

def count_pages_in_branch(branch: str) -> int:
    """Count React/TSX pages in frontend/src/pages."""
    try:
        pages_dir = Path(__file__).parent.parent / 'frontend' / 'src' / 'pages'
        if not pages_dir.exists():
            return 0
        
        count = 0
        for file in pages_dir.rglob('*.tsx'):
            if file.is_file() and not file.name.startswith('.'):
                count += 1
        return count
    except:
        return 0

def analyze_branch(branch: str) -> Dict:
    """Analyze a branch for navigation completeness."""
    print(f"Analyzing branch: {branch}")
    
    # Save current branch
    current_branch = run_git_command(['branch', '--show-current'])
    
    # Checkout branch
    if not checkout_branch(branch):
        print(f"  Failed to checkout {branch}")
        return {
            'branch': branch,
            'error': 'checkout_failed',
            'platforms': 0,
            'categories': 0,
            'features': 0,
            'pages': 0
        }
    
    # Analyze navigation files
    nav_files = [
        Path('frontend/public/gui_nav.latest.json'),
        Path('documentation/gui_nav_structure/gui_nav.latest.json'),
    ]
    
    best_stats = {
        'platforms': 0,
        'categories': 0,
        'features': 0,
        'editions': 0
    }
    
    for nav_file in nav_files:
        stats = analyze_nav_json(nav_file)
        if stats['file_exists']:
            # Take the best stats
            if stats['platforms'] > best_stats['platforms']:
                best_stats = stats
    
    # Count pages
    pages = count_pages_in_branch(branch)
    
    # Restore original branch
    if current_branch:
        checkout_branch(current_branch)
    
    result = {
        'branch': branch,
        'platforms': best_stats['platforms'],
        'categories': best_stats['categories'],
        'features': best_stats['features'],
        'editions': best_stats['editions'],
        'pages': pages,
        'score': best_stats['platforms'] * 1000 + best_stats['categories'] * 100 + best_stats['features'] + pages
    }
    
    print(f"  Platforms: {result['platforms']}, Categories: {result['categories']}, Features: {result['features']}, Pages: {result['pages']}")
    
    return result

def main():
    """Main analysis function."""
    print("Analyzing branches for navigation completeness...")
    
    branches = get_all_branches()
    print(f"Found {len(branches)} branches to analyze")
    
    results = []
    for branch in branches:
        result = analyze_branch(branch)
        results.append(result)
    
    # Sort by score (descending)
    results.sort(key=lambda x: x.get('score', 0), reverse=True)
    
    # Print summary
    print("\n" + "="*80)
    print("BRANCH ANALYSIS SUMMARY")
    print("="*80)
    print(f"{'Branch':<40} {'Platforms':<12} {'Categories':<12} {'Features':<12} {'Pages':<10} {'Score':<10}")
    print("-"*80)
    
    for r in results:
        if 'error' not in r:
            print(f"{r['branch']:<40} {r['platforms']:<12} {r['categories']:<12} {r['features']:<12} {r['pages']:<10} {r['score']:<10}")
    
    # Save results
    output_file = Path(__file__).parent.parent / 'branch_nav_analysis.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to: {output_file}")
    
    # Recommend top branches
    top_branches = [r for r in results if 'error' not in r][:10]
    print("\nTop branches by completeness:")
    for i, r in enumerate(top_branches, 1):
        print(f"  {i}. {r['branch']} (score: {r['score']})")
    
    return results

if __name__ == '__main__':
    main()
