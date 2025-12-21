#!/usr/bin/env python3
"""
Resolve Duplicate Paths Script
- Identifies all duplicate paths in navigation
- Creates unique paths for each platform/category context
- Updates navigation JSON with resolved paths
- Generates route mapping for frontend updates
"""

import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple
import re

REPO_ROOT = Path(__file__).parent.parent
NAV_JSON = REPO_ROOT / "frontend" / "public" / "gui_nav.latest.json"
RELATIONSHIP_ANALYSIS = REPO_ROOT / "ia_relationship_analysis.json"

def slugify(text: str) -> str:
    """Convert text to URL-friendly slug"""
    # Replace special characters
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    text = text.strip('-')
    return text

def find_duplicate_paths(nav_data: Dict) -> Dict[str, List[Tuple[str, str]]]:
    """Find all duplicate paths and their contexts"""
    path_contexts = defaultdict(list)
    
    for edition, platforms in nav_data.items():
        if not isinstance(platforms, dict):
            continue
        
        for platform_title, categories in platforms.items():
            if not isinstance(categories, dict):
                continue
            
            for category_title, features in categories.items():
                if not isinstance(features, list):
                    continue
                
                for feature in features:
                    if not isinstance(feature, dict):
                        continue
                    
                    path = feature.get('path', '')
                    if path:
                        path_contexts[path].append((platform_title, category_title, feature.get('title', '')))
    
    # Filter to only duplicates
    duplicates = {
        path: contexts 
        for path, contexts in path_contexts.items() 
        if len(contexts) > 1
    }
    
    return duplicates

def create_unique_path(platform: str, category: str, feature_title: str, original_path: str) -> str:
    """Create a unique path for a feature in a specific platform/category context"""
    platform_slug = slugify(platform)
    category_slug = slugify(category)
    
    # Extract feature name from original path or use title
    if original_path:
        path_parts = original_path.strip('/').split('/')
        feature_name = path_parts[-1] if path_parts else slugify(feature_title)
    else:
        feature_name = slugify(feature_title)
    
    # Remove platform/category prefix if already present
    if feature_name.startswith(platform_slug):
        feature_name = feature_name[len(platform_slug):].lstrip('/')
    if feature_name.startswith(category_slug):
        feature_name = feature_name[len(category_slug):].lstrip('/')
    
    # Build new path
    new_path = f"/{platform_slug}/{category_slug}/{feature_name}"
    
    # Clean up double slashes
    new_path = re.sub(r'/+', '/', new_path)
    
    return new_path

def resolve_paths_in_navigation(nav_data: Dict, path_mapping: Dict[str, str] = None) -> Tuple[Dict, Dict]:
    """
    Resolve all duplicate paths in navigation data
    Returns: (resolved_nav_data, path_mapping)
    """
    if path_mapping is None:
        path_mapping = {}
    
    resolved = {}
    duplicates = find_duplicate_paths(nav_data)
    
    print(f"Found {len(duplicates)} duplicate paths to resolve")
    
    for edition, platforms in nav_data.items():
        if edition not in resolved:
            resolved[edition] = {}
        
        for platform_title, categories in platforms.items():
            if platform_title not in resolved[edition]:
                resolved[edition][platform_title] = {}
            
            for category_title, features in categories.items():
                if category_title not in resolved[edition][platform_title]:
                    resolved[edition][platform_title][category_title] = []
                
                for feature in features:
                    if not isinstance(feature, dict):
                        continue
                    
                    original_path = feature.get('path', '')
                    feature_title = feature.get('title', '')
                    
                    if not original_path:
                        # No path - create one
                        new_path = create_unique_path(platform_title, category_title, feature_title, '')
                        feature = feature.copy()
                        feature['path'] = new_path
                        if original_path != new_path:
                            path_mapping[original_path or f"NO_PATH_{feature_title}"] = new_path
                    elif original_path in duplicates:
                        # Duplicate path - create unique one
                        new_path = create_unique_path(platform_title, category_title, feature_title, original_path)
                        feature = feature.copy()
                        feature['path'] = new_path
                        feature['original_path'] = original_path  # Keep for reference
                        path_mapping[original_path] = new_path
                    else:
                        # Unique path - keep as is (but normalize)
                        normalized_path = original_path
                        # Ensure path follows pattern if it doesn't already
                        if not normalized_path.startswith(f'/{slugify(platform_title)}'):
                            # Path doesn't include platform - this is OK for root-level features
                            # But we should still normalize it
                            pass
                        feature = feature.copy()
                        feature['path'] = normalized_path
                    
                    resolved[edition][platform_title][category_title].append(feature)
    
    return resolved, path_mapping

def generate_route_mapping(path_mapping: Dict[str, str]) -> Dict[str, Dict]:
    """Generate route mapping for frontend updates"""
    route_mapping = {
        "old_to_new": path_mapping,
        "new_to_old": {v: k for k, v in path_mapping.items()},
        "redirects": {}
    }
    
    # Generate redirect rules (if old paths should redirect to new)
    for old_path, new_path in path_mapping.items():
        if old_path and new_path and old_path != new_path:
            route_mapping["redirects"][old_path] = new_path
    
    return route_mapping

def update_route_files(path_mapping: Dict[str, str], route_mapping: Dict):
    """Update route files with new paths (if route files exist)"""
    # This would update actual route files in the frontend
    # For now, just generate a migration script
    
    migration_script = REPO_ROOT / "scripts" / "migrate_routes.py"
    
    script_content = f'''#!/usr/bin/env python3
"""
Auto-generated route migration script
Updates route references from old paths to new paths
"""

PATH_MAPPING = {json.dumps(path_mapping, indent=2)}

def migrate_routes():
    """Migrate route references in frontend code"""
    import re
    from pathlib import Path
    
    frontend_dir = Path(__file__).parent.parent / "frontend"
    
    # Files to update
    route_files = [
        frontend_dir / "src" / "routes.tsx",
        frontend_dir / "src" / "routes-generated.tsx",
        frontend_dir / "src" / "routesIA.tsx",
    ]
    
    for route_file in route_files:
        if not route_file.exists():
            continue
        
        content = route_file.read_text()
        updated = False
        
        for old_path, new_path in PATH_MAPPING.items():
            if old_path in content:
                content = content.replace(old_path, new_path)
                updated = True
        
        if updated:
            route_file.write_text(content)
            print(f"Updated: {{route_file}}")

if __name__ == "__main__":
    migrate_routes()
'''
    
    migration_script.write_text(script_content)
    print(f"Migration script generated: {migration_script}")

def main():
    print("=" * 80)
    print("DUPLICATE PATH RESOLUTION")
    print("=" * 80)
    
    # Load navigation data
    if not NAV_JSON.exists():
        print(f"Navigation JSON not found: {NAV_JSON}")
        return
    
    print(f"\nLoading navigation from: {NAV_JSON}")
    with open(NAV_JSON, 'r') as f:
        nav_data = json.load(f)
    
    # Find duplicates
    print("\nAnalyzing paths...")
    duplicates = find_duplicate_paths(nav_data)
    
    print(f"\nFound {len(duplicates)} duplicate paths:")
    for path, contexts in list(duplicates.items())[:10]:
        print(f"\n  {path}:")
        for platform, category, title in contexts:
            print(f"    - {platform} / {category} / {title}")
    
    if len(duplicates) > 10:
        print(f"\n  ... and {len(duplicates) - 10} more")
    
    # Resolve paths
    print("\nResolving duplicate paths...")
    resolved_nav, path_mapping = resolve_paths_in_navigation(nav_data)
    
    # Verify no duplicates remain
    remaining_duplicates = find_duplicate_paths(resolved_nav)
    if remaining_duplicates:
        print(f"\nWARNING: {len(remaining_duplicates)} duplicates still remain!")
        for path, contexts in list(remaining_duplicates.items())[:5]:
            print(f"  {path}: {len(contexts)} contexts")
    else:
        print("\n✓ All duplicate paths resolved!")
    
    # Save resolved navigation
    output_file = REPO_ROOT / "frontend" / "public" / "gui_nav.resolved.json"
    with open(output_file, 'w') as f:
        json.dump(resolved_nav, f, indent=2)
    
    print(f"\nResolved navigation saved to: {output_file}")
    
    # Generate route mapping
    route_mapping = generate_route_mapping(path_mapping)
    
    mapping_file = REPO_ROOT / "path_resolution_mapping.json"
    with open(mapping_file, 'w') as f:
        json.dump({
            "path_mapping": path_mapping,
            "route_mapping": route_mapping,
            "duplicates_resolved": len(duplicates),
            "paths_remapped": len(path_mapping)
        }, f, indent=2)
    
    print(f"Path resolution mapping saved to: {mapping_file}")
    
    # Generate migration script
    update_route_files(path_mapping, route_mapping)
    
    # Statistics
    print("\n" + "=" * 80)
    print("RESOLUTION STATISTICS")
    print("=" * 80)
    print(f"Duplicate paths found: {len(duplicates)}")
    print(f"Paths remapped: {len(path_mapping)}")
    print(f"Remaining duplicates: {len(remaining_duplicates)}")
    
    print("\nNext steps:")
    print("1. Review gui_nav.resolved.json")
    print("2. Review path_resolution_mapping.json")
    print("3. If approved, copy gui_nav.resolved.json to gui_nav.latest.json")
    print("4. Run scripts/migrate_routes.py to update route files")

if __name__ == "__main__":
    main()


