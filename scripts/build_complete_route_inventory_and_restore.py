#!/usr/bin/env python3
"""
Complete Route Inventory and Restoration Script
Builds route inventory from gui_nav.latest.json and restores pages from best commits.
"""

import json
import subprocess
import os
import re
from typing import Dict, List, Tuple, Set, Optional
from pathlib import Path
from collections import defaultdict

SOURCE_COMMITS = {
    'stable': '3a154a6e6305fe9f3a760f44b1b10d73e1ed3256',
    'increments': '58cfc345630f68bf10909538aba48c12f87ce9df',
    'backup': '4acea80190121b8ab79d8cd1367166bcfead8bde'
}

def run_git_command(cmd: List[str], cwd: str = '.') -> str:
    """Run git command and return output."""
    try:
        result = subprocess.run(['git'] + cmd, cwd=cwd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            return ""
        return result.stdout.strip()
    except Exception as e:
        print(f"Git command failed: {' '.join(cmd)} - {e}")
        return ""

def get_file_content(commit: str, filepath: str) -> Optional[str]:
    """Get file content from specific commit."""
    content = run_git_command(['show', f'{commit}:{filepath}'])
    return content if content else None

def score_page_implementation(content: str) -> int:
    """Score a page implementation based on completeness."""
    if not content:
        return -10
    
    score = 0
    
    # Check for required sections
    if re.search(r'(Parameters|Inputs|Input)', content, re.I):
        score += 1
    if re.search(r'(Configuration|Config|Settings)', content, re.I):
        score += 1
    if re.search(r'(Environment|Env)', content, re.I):
        score += 1
    if re.search(r'(Execute|Run|Process|Submit)', content, re.I):
        score += 3  # Execute is critical
    if re.search(r'(Results|Output|Table|Chart|Report)', content, re.I):
        score += 2  # Results are critical
    
    # Penalties
    if re.search(r'(TODO|FIXME|STUB|PLACEHOLDER)', content, re.I):
        score -= 2
    if re.search(r'(//.*disabled|/\*.*disabled)', content, re.I):
        score -= 1
    
    # Check for API calls
    if re.search(r'(fetch|axios|api\.|useQuery|useMutation)', content, re.I):
        score += 1
    
    # Check for real data rendering
    if re.search(r'(map\(|\.map\(|forEach)', content):
        score += 1
    
    return score

def find_best_commit_for_route(route: str, route_type: str) -> Tuple[str, int]:
    """Find the best commit for a route by scoring implementations."""
    best_commit = 'stable'
    best_score = -100
    
    # Convert route to component path
    component_path = route_to_component_path(route)
    
    for commit_name, commit_sha in SOURCE_COMMITS.items():
        content = get_file_content(commit_sha, component_path)
        if content:
            score = score_page_implementation(content)
            if score > best_score:
                best_score = score
                best_commit = commit_name
        else:
            # Try alternative paths
            alt_paths = get_alternative_paths(route)
            for alt_path in alt_paths:
                content = get_file_content(commit_sha, alt_path)
                if content:
                    score = score_page_implementation(content)
                    if score > best_score:
                        best_score = score
                        best_commit = commit_name
                        break
    
    return best_commit, best_score

def route_to_component_path(route: str) -> str:
    """Convert route to component file path."""
    # Remove leading/trailing slashes
    route = route.strip('/')
    if not route:
        return 'frontend/src/pages/Dashboard.tsx'
    
    # Convert to PascalCase component name
    parts = route.split('/')
    component_name = ''.join(word.capitalize() for word in parts[-1].split('-'))
    
    # Handle special cases
    if route == '/':
        return 'frontend/src/pages/Dashboard.tsx'
    
    # Build path
    if len(parts) > 1:
        dir_path = '/'.join(parts[:-1])
        dir_path = dir_path.replace('/', '/').replace('-', '')
        return f'frontend/src/pages/{dir_path}/{component_name}.tsx'
    else:
        return f'frontend/src/pages/{component_name}.tsx'

def get_alternative_paths(route: str) -> List[str]:
    """Get alternative file paths for a route."""
    paths = []
    route = route.strip('/')
    parts = route.split('/')
    
    # Try different naming conventions
    component_name = ''.join(word.capitalize() for word in parts[-1].split('-'))
    paths.append(f'frontend/src/pages/{component_name}.tsx')
    
    if len(parts) > 1:
        # Try nested structure
        dir_name = parts[-2].replace('-', '').capitalize()
        paths.append(f'frontend/src/pages/{dir_name}/{component_name}.tsx')
    
    return paths

def parse_gui_nav_json(json_path: str) -> Dict:
    """Parse gui_nav.latest.json and extract all routes."""
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    routes = {}
    platform_order = 0
    
    for edition_name, edition_data in data.items():
        platform_order += 1
        
        for platform_name, categories in edition_data.items():
            if not isinstance(categories, dict):
                continue
            
            platform_id = platform_name.lower().replace(' ', '-').replace('&', '')
            platform_path = f'/{platform_id}'
            
            category_order = 0
            for category_name, features in categories.items():
                if not isinstance(features, list):
                    continue
                
                category_order += 1
                category_id = category_name.lower().replace(' ', '-').replace('&', '')
                category_home_route = None
                
                # First feature is typically the category home
                feature_order = 0
                for feature in features:
                    if not isinstance(feature, dict):
                        continue
                    
                    feature_order += 1
                    route = feature.get('path', '')
                    title = feature.get('title', '')
                    
                    if not route:
                        continue
                    
                    # Determine if this is category home or feature
                    is_category_home = (feature_order == 1 and 
                                       route.count('/') <= 2 and
                                       not any(f['path'] == route for f in features[1:] if isinstance(f, dict)))
                    
                    route_type = 'categoryHome' if is_category_home else 'feature'
                    
                    if is_category_home:
                        category_home_route = route
                    
                    routes[route] = {
                        'title': title,
                        'route': route,
                        'route_type': route_type,
                        'platform': platform_name,
                        'platform_id': platform_id,
                        'category': category_name,
                        'category_id': category_id,
                        'category_home_route': category_home_route,
                        'edition': 'enterprise' if 'Enterprise' in edition_name else 'personal',
                        'order': feature_order,
                        'platform_order': platform_order,
                        'category_order': category_order,
                        'is_new': feature.get('new', False)
                    }
    
    return routes

def build_route_matrix(routes: Dict) -> Dict:
    """Build route→bestCommit matrix."""
    matrix = {}
    total = len(routes)
    
    for i, (route, route_info) in enumerate(routes.items(), 1):
        if i % 50 == 0:
            print(f"Processing route {i}/{total}: {route}")
        
        best_commit, score = find_best_commit_for_route(route, route_info['route_type'])
        
        matrix[route] = {
            **route_info,
            'best_commit': best_commit,
            'best_commit_sha': SOURCE_COMMITS[best_commit],
            'score': score,
            'component_path': route_to_component_path(route)
        }
    
    return matrix

def generate_restoration_commands(matrix: Dict) -> List[str]:
    """Generate git restore commands for missing pages."""
    commands = []
    restored = set()
    
    for route, info in matrix.items():
        component_path = info['component_path']
        
        # Check if file exists
        if os.path.exists(component_path):
            continue
        
        commit_sha = info['best_commit_sha']
        
        # Generate restore command
        cmd = f"git restore --source {commit_sha} -- {component_path}"
        commands.append({
            'route': route,
            'command': cmd,
            'commit': info['best_commit'],
            'component_path': component_path
        })
    
    return commands

def main():
    print("Building complete route inventory...")
    
    # Parse GUI nav JSON
    json_path = 'documentation/gui_nav_structure/gui_nav.latest.json'
    if not os.path.exists(json_path):
        print(f"Error: {json_path} not found")
        return
    
    routes = parse_gui_nav_json(json_path)
    print(f"Found {len(routes)} routes in GUI nav JSON")
    
    # Build route matrix
    print("\nBuilding route→bestCommit matrix...")
    matrix = build_route_matrix(routes)
    
    # Save matrix
    output_path = 'route_matrix_complete.json'
    with open(output_path, 'w') as f:
        json.dump(matrix, f, indent=2)
    print(f"\nSaved route matrix to {output_path}")
    
    # Generate restoration commands
    print("\nGenerating restoration commands...")
    restore_commands = generate_restoration_commands(matrix)
    print(f"Found {len(restore_commands)} pages to restore")
    
    # Save restoration plan
    restore_plan_path = 'restore_plan.json'
    with open(restore_plan_path, 'w') as f:
        json.dump(restore_commands, f, indent=2)
    print(f"Saved restoration plan to {restore_plan_path}")
    
    # Count pages by type
    category_homes = sum(1 for r in matrix.values() if r['route_type'] == 'categoryHome')
    features = sum(1 for r in matrix.values() if r['route_type'] == 'feature')
    
    print(f"\nSummary:")
    print(f"  Total routes: {len(matrix)}")
    print(f"  Category homes: {category_homes}")
    print(f"  Features: {features}")
    print(f"  Pages to restore: {len(restore_commands)}")
    
    # Count by commit
    by_commit = defaultdict(int)
    for info in matrix.values():
        by_commit[info['best_commit']] += 1
    
    print(f"\nBest commit distribution:")
    for commit, count in by_commit.items():
        print(f"  {commit}: {count}")

if __name__ == '__main__':
    main()





