#!/usr/bin/env python3
"""
Verify all page components exist and have required sections.
Checks for Parameters/Config/Env/Execute/Results sections.
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Tuple

def extract_routes_from_manifest(manifest_path: Path) -> List[Dict]:
    """Extract all routes from the IA manifest."""
    routes = []
    
    with open(manifest_path, 'r') as f:
        content = f.read()
    
    # Extract all routes using regex - simpler approach
    # Pattern: "route": "/path" or "homeRoute": "/path"
    # Pattern: "componentPath": "path" or "homeComponentPath": "path"
    
    all_routes = []
    seen_routes = set()
    
    # The manifest uses TypeScript object syntax, not JSON
    # Extract using simpler patterns that work with TS format
    
    # Extract category homes
    home_routes = re.findall(r'homeRoute:\s*["\']([^"\']+)["\']', content)
    home_paths = re.findall(r'homeComponentPath:\s*["\']([^"\']+)["\']', content)
    
    # Extract features
    feature_routes = re.findall(r'route:\s*["\']([^"\']+)["\']', content)
    feature_paths = re.findall(r'componentPath:\s*["\']([^"\']+)["\']', content)
    
    # Match pairs - category homes
    for i, route in enumerate(home_routes):
        if i < len(home_paths):
            if route not in seen_routes:
                all_routes.append({
                    'route': route,
                    'componentPath': home_paths[i],
                    'type': 'categoryHome'
                })
                seen_routes.add(route)
    
    # Match pairs - features (skip if already added as category home)
    for i, route in enumerate(feature_routes):
        if i < len(feature_paths):
            if route not in seen_routes:
                all_routes.append({
                    'route': route,
                    'componentPath': feature_paths[i],
                    'type': 'feature'
                })
                seen_routes.add(route)
    
    return all_routes

def check_page_component(path: Path) -> Tuple[bool, List[str], int]:
    """Check if page component exists and has required sections."""
    if not path.exists():
        return False, ['File does not exist'], 0
    
    with open(path, 'r') as f:
        content = f.read()
    
    issues = []
    score = 0
    
    # Check for required sections
    has_params = bool(re.search(r'(Parameters|Inputs|Input|props)', content, re.I))
    has_config = bool(re.search(r'(Configuration|Config|Settings)', content, re.I))
    has_env = bool(re.search(r'(Environment|Env|env)', content, re.I))
    has_execute = bool(re.search(r'(Execute|Run|Process|Submit|onSubmit|handleSubmit)', content, re.I))
    has_results = bool(re.search(r'(Results|Output|Table|Chart|Report|render|return)', content, re.I))
    
    if not has_params:
        issues.append('Missing Parameters/Inputs section')
    else:
        score += 1
    
    if not has_config:
        issues.append('Missing Configuration section')
    else:
        score += 1
    
    if not has_env:
        issues.append('Missing Environment section')
    else:
        score += 1
    
    if not has_execute:
        issues.append('Missing Execute/Process section')
    else:
        score += 3  # Execute is critical
    
    if not has_results:
        issues.append('Missing Results/Output section')
    else:
        score += 2  # Results are critical
    
    # Check for stubs/TODOs
    has_stubs = bool(re.search(r'(TODO|FIXME|STUB|PLACEHOLDER|NotImplemented)', content, re.I))
    if has_stubs:
        issues.append('Contains stubs/TODOs')
        score -= 2
    
    # Check for API calls
    has_api = bool(re.search(r'(fetch|axios|api\.|useQuery|useMutation|useEffect)', content, re.I))
    if has_api:
        score += 1
    
    return True, issues, score

def main():
    """Verify all page components."""
    manifest_path = Path('frontend/src/data/iaManifest.complete.ts')
    
    if not manifest_path.exists():
        print(f"Error: {manifest_path} not found")
        return
    
    print("Extracting routes from manifest...")
    routes = extract_routes_from_manifest(manifest_path)
    print(f"Found {len(routes)} routes to verify\n")
    
    missing = []
    incomplete = []
    complete = []
    
    for route_info in routes:
        component_path = route_info['componentPath']
        # Convert to actual file path
        if component_path.startswith('frontend/src/'):
            file_path = Path(component_path)
        else:
            file_path = Path('frontend/src') / component_path.replace('frontend/src/', '')
        
        exists, issues, score = check_page_component(file_path)
        
        if not exists:
            missing.append({
                'route': route_info['route'],
                'path': str(file_path),
                'type': route_info['type']
            })
        elif issues:
            incomplete.append({
                'route': route_info['route'],
                'path': str(file_path),
                'type': route_info['type'],
                'issues': issues,
                'score': score
            })
        else:
            complete.append({
                'route': route_info['route'],
                'path': str(file_path),
                'score': score
            })
    
    # Print summary
    print(f"Summary:")
    print(f"  Total routes: {len(routes)}")
    print(f"  ✅ Complete: {len(complete)}")
    print(f"  ⚠️  Incomplete: {len(incomplete)}")
    print(f"  ❌ Missing: {len(missing)}")
    
    # Save reports
    if missing:
        with open('missing_pages_report.json', 'w') as f:
            json.dump(missing, f, indent=2)
        print(f"\nMissing pages report saved to: missing_pages_report.json")
    
    if incomplete:
        with open('incomplete_pages_report.json', 'w') as f:
            json.dump(incomplete, f, indent=2)
        print(f"Incomplete pages report saved to: incomplete_pages_report.json")
    
    # Show top incomplete pages (lowest scores)
    if incomplete:
        print(f"\nTop 10 pages needing attention (lowest scores):")
        sorted_incomplete = sorted(incomplete, key=lambda x: x['score'])
        for item in sorted_incomplete[:10]:
            print(f"  {item['route']}: score={item['score']}, issues={len(item['issues'])}")

if __name__ == '__main__':
    main()

