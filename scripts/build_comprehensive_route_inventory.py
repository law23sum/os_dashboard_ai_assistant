#!/usr/bin/env python3
"""
Comprehensive Route/Page Inventory Builder
Scans specified commits to build a complete inventory of all pages/routes
"""

import subprocess
import json
import re
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict

# Source commits
COMMITS = {
    'stable': '3a154a6e6305fe9f3a760f44b1b10d73e1ed3256',
    'incremeents': '58cfc345630f68bf10909538aba48c12f87ce9df',
    'backup': '4acea80190121b8ab79d8cd1367166bcfead8bde'
}

@dataclass
class PageInfo:
    """Information about a page/route"""
    route: str
    component_path: Optional[str] = None
    commit: Optional[str] = None
    score: int = 0
    has_execute: bool = False
    has_results: bool = False
    has_parameters: bool = False
    has_config: bool = False
    has_env: bool = False
    has_stubs: bool = False
    has_todos: bool = False
    has_dead_links: bool = False
    file_size: int = 0
    line_count: int = 0

def run_git_command(cmd: List[str]) -> str:
    """Run a git command and return output"""
    try:
        result = subprocess.run(
            ['git'] + cmd,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running git command: {' '.join(cmd)}")
        print(f"Error: {e.stderr}")
        return ""

def get_files_in_commit(commit: str, pattern: str = "*.tsx") -> List[str]:
    """Get all files matching pattern in a commit"""
    cmd = ['ls-tree', '-r', '--name-only', commit]
    output = run_git_command(cmd)
    files = [f for f in output.split('\n') if f.endswith(pattern)]
    return files

def get_file_content(commit: str, filepath: str) -> Optional[str]:
    """Get file content from a specific commit"""
    try:
        cmd = ['show', f'{commit}:{filepath}']
        return run_git_command(cmd)
    except:
        return None

def score_page(content: str) -> Tuple[int, Dict[str, bool]]:
    """Score a page based on completeness"""
    score = 0
    flags = {
        'has_execute': False,
        'has_results': False,
        'has_parameters': False,
        'has_config': False,
        'has_env': False,
        'has_stubs': False,
        'has_todos': False,
        'has_dead_links': False
    }
    
    content_lower = content.lower()
    
    # Check for Execute section (wired to API)
    if re.search(r'(execute|onExecute|handleExecute|run|onRun)', content, re.IGNORECASE):
        if re.search(r'(api|fetch|axios|useQuery|useMutation)', content, re.IGNORECASE):
            score += 3
            flags['has_execute'] = True
    
    # Check for Results section (rendering real data)
    if re.search(r'(results|output|data|table|chart|graph)', content, re.IGNORECASE):
        if re.search(r'(map|\.map\(|useQuery|data\s*=|results\s*=)', content, re.IGNORECASE):
            score += 2
            flags['has_results'] = True
    
    # Check for Parameters section
    if re.search(r'(parameters|params|inputs|form|formData)', content, re.IGNORECASE):
        score += 1
        flags['has_parameters'] = True
    
    # Check for Configuration section
    if re.search(r'(config|configuration|settings|options)', content, re.IGNORECASE):
        score += 1
        flags['has_config'] = True
    
    # Check for Environment section
    if re.search(r'(environment|env|env\.|process\.env)', content, re.IGNORECASE):
        score += 1
        flags['has_env'] = True
    
    # Penalties
    if re.search(r'(stub|placeholder|todo|fixme|xxx)', content_lower):
        score -= 2
        flags['has_stubs'] = True
        if 'todo' in content_lower or 'fixme' in content_lower:
            flags['has_todos'] = True
    
    if re.search(r'(404|not found|dead link|broken)', content_lower):
        score -= 2
        flags['has_dead_links'] = True
    
    return score, flags

def extract_route_from_path(filepath: str) -> Optional[str]:
    """Extract route from file path"""
    # frontend/src/pages/Workspaces/Dev/Committasks.tsx -> /workspaces/dev/commit-tasks
    # frontend/src/pages/Ai/Capsules/Templates.tsx -> /ai/capsules/templates
    
    if not filepath.startswith('frontend/src/pages/'):
        return None
    
    # Remove prefix
    rel_path = filepath.replace('frontend/src/pages/', '')
    
    # Remove extension
    rel_path = rel_path.replace('.tsx', '').replace('.ts', '')
    
    # Convert to route
    parts = rel_path.split('/')
    
    # Handle special cases
    if parts[0] == 'Dashboard.tsx' or parts[0] == 'Dashboard':
        return '/'
    
    # Convert PascalCase to kebab-case
    route_parts = []
    for part in parts:
        if part.endswith('.tsx'):
            part = part[:-4]
        # Convert PascalCase to kebab-case
        kebab = re.sub(r'(?<!^)(?=[A-Z])', '-', part).lower()
        route_parts.append(kebab)
    
    route = '/' + '/'.join(route_parts)
    return route

def find_pages_in_commit(commit: str, commit_name: str) -> Dict[str, PageInfo]:
    """Find all page components in a commit"""
    pages = {}
    
    # Get all .tsx files in frontend/src/pages
    all_files = get_files_in_commit(commit, '.tsx')
    page_files = [f for f in all_files if 'frontend/src/pages' in f and f.endswith('.tsx')]
    
    print(f"\nScanning {commit_name} ({commit[:8]})...")
    print(f"Found {len(page_files)} page files")
    
    for filepath in page_files:
        content = get_file_content(commit, filepath)
        if not content:
            continue
        
        route = extract_route_from_path(filepath)
        if not route:
            continue
        
        score, flags = score_page(content)
        
        page_info = PageInfo(
            route=route,
            component_path=filepath,
            commit=commit_name,
            score=score,
            **flags,
            file_size=len(content),
            line_count=len(content.split('\n'))
        )
        
        # If we already have this route, keep the one with higher score
        if route in pages:
            if score > pages[route].score:
                pages[route] = page_info
        else:
            pages[route] = page_info
    
    return pages

def build_inventory() -> Dict:
    """Build comprehensive inventory across all commits"""
    all_pages = {}
    
    # Scan each commit
    for commit_name, commit_hash in COMMITS.items():
        pages = find_pages_in_commit(commit_hash, commit_name)
        
        # Merge pages, keeping best version
        for route, page_info in pages.items():
            if route not in all_pages:
                all_pages[route] = page_info
            else:
                # Keep the one with higher score, or prefer stable > incremeents > backup
                current = all_pages[route]
                priority = {'stable': 3, 'incremeents': 2, 'backup': 1}
                
                if (page_info.score > current.score or 
                    (page_info.score == current.score and 
                     priority.get(page_info.commit, 0) > priority.get(current.commit, 0))):
                    all_pages[route] = page_info
    
    return all_pages

def main():
    """Main entry point"""
    print("Building comprehensive route/page inventory...")
    print(f"Scanning commits: {COMMITS}")
    
    inventory = build_inventory()
    
    # Convert to dict for JSON serialization
    inventory_dict = {
        route: {
            'route': info.route,
            'component_path': info.component_path,
            'commit': info.commit,
            'score': info.score,
            'has_execute': info.has_execute,
            'has_results': info.has_results,
            'has_parameters': info.has_parameters,
            'has_config': info.has_config,
            'has_env': info.has_env,
            'has_stubs': info.has_stubs,
            'has_todos': info.has_todos,
            'has_dead_links': info.has_dead_links,
            'file_size': info.file_size,
            'line_count': info.line_count
        }
        for route, info in inventory.items()
    }
    
    # Save inventory
    output_file = Path(__file__).parent.parent / 'route_inventory_comprehensive.json'
    with open(output_file, 'w') as f:
        json.dump(inventory_dict, f, indent=2)
    
    print(f"\nInventory complete!")
    print(f"Total unique routes: {len(inventory)}")
    print(f"Saved to: {output_file}")
    
    # Print summary
    by_commit = defaultdict(int)
    for info in inventory.values():
        by_commit[info.commit] += 1
    
    print("\nPages by source commit:")
    for commit, count in sorted(by_commit.items(), key=lambda x: -x[1]):
        print(f"  {commit}: {count} pages")
    
    print("\nScore distribution:")
    scores = [info.score for info in inventory.values()]
    print(f"  Min: {min(scores)}")
    print(f"  Max: {max(scores)}")
    print(f"  Avg: {sum(scores) / len(scores):.1f}")

if __name__ == '__main__':
    main()





