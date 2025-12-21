#!/usr/bin/env python3
"""
Build Complete IA Manifest from Documentation
Parses gui_nav.latest.json and GUI_STRUCTURE_LATEST.md to create complete manifest
with all platforms, categories, and features (~444 pages)
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Set, Optional
from dataclasses import dataclass, asdict

@dataclass
class Feature:
    id: str
    label: str
    route: str
    component_path: Optional[str] = None
    best_commit: Optional[str] = None
    actor_scope: str = 'both'
    order: int = 0
    is_new: bool = False

@dataclass
class Category:
    id: str
    label: str
    home_route: str
    features: List[Feature]
    home_component_path: Optional[str] = None
    home_best_commit: Optional[str] = None
    actor_scope: str = 'both'
    order: int = 0

@dataclass
class Platform:
    id: str
    label: str
    path: str
    categories: List[Category]
    actor_scope: str = 'both'
    order: int = 0

def slugify(text: str) -> str:
    """Convert label to slug"""
    return re.sub(r'[^\w\s-]', '', text.lower()).strip().replace(' ', '-')

def extract_route_from_path(path_str: str) -> str:
    """Normalize route path"""
    # Remove leading/trailing slashes and normalize
    path = path_str.strip().strip('/')
    if not path:
        return '/'
    return '/' + path

def parse_gui_nav_json(json_path: Path) -> Dict:
    """Parse gui_nav.latest.json"""
    with open(json_path, 'r') as f:
        return json.load(f)

def build_platforms_from_json(nav_data: Dict) -> List[Platform]:
    """Build platform structure from JSON"""
    platforms = []
    platform_order = 1
    
    for edition_name, edition_data in nav_data.items():
        # Determine actor scope based on edition
        actor_scope = 'personal' if 'Personal' in edition_name else 'enterprise' if 'Enterprise' in edition_name else 'both'
        
        for platform_name, platform_data in edition_data.items():
            platform_id = slugify(platform_name)
            platform_path = f'/{platform_id}'
            
            categories = []
            category_order = 1
            
            for category_name, features_list in platform_data.items():
                category_id = slugify(category_name)
                
                # First feature is typically the category home
                category_home_route = None
                category_home_component = None
                category_features = []
                feature_order = 1
                
                for idx, feature_data in enumerate(features_list):
                    if isinstance(feature_data, dict):
                        feature_label = feature_data.get('title', '')
                        feature_path = feature_data.get('path', '')
                        is_new = feature_data.get('new', False)
                    else:
                        continue
                    
                    feature_id = slugify(feature_label)
                    feature_route = extract_route_from_path(feature_path)
                    
                    # First feature becomes category home (IA rule: category home = first feature)
                    if category_home_route is None:
                        category_home_route = feature_route
                        category_home_component = f'frontend/src/pages/{feature_label.replace(" ", "")}.tsx'
                        # Don't add first feature to features list - it's the category home
                        continue
                    
                    # Only add subsequent features to the features list
                    feature = Feature(
                        id=feature_id,
                        label=feature_label,
                        route=feature_route,
                        component_path=f'frontend/src/pages/{feature_label.replace(" ", "")}.tsx',
                        actor_scope=actor_scope,
                        order=feature_order,
                        is_new=is_new
                    )
                    category_features.append(feature)
                    feature_order += 1
                
                if category_home_route:
                    category = Category(
                        id=category_id,
                        label=category_name,
                        home_route=category_home_route,
                        home_component_path=category_home_component,
                        features=category_features,
                        actor_scope=actor_scope,
                        order=category_order
                    )
                    categories.append(category)
                    category_order += 1
            
            if categories:
                platform = Platform(
                    id=platform_id,
                    label=platform_name,
                    path=platform_path,
                    categories=categories,
                    actor_scope=actor_scope,
                    order=platform_order
                )
                platforms.append(platform)
                platform_order += 1
    
    return platforms

def count_total_pages(platforms: List[Platform]) -> int:
    """Count total pages (category homes + features)"""
    count = 0
    for platform in platforms:
        for category in platform.categories:
            count += 1  # Category home
            count += len(category.features)
    return count

def main():
    """Main entry point"""
    repo_root = Path(__file__).parent.parent
    json_path = repo_root / 'documentation' / 'gui_nav_structure' / 'gui_nav.latest.json'
    
    if not json_path.exists():
        print(f"Error: {json_path} not found")
        return
    
    print(f"Parsing {json_path}...")
    nav_data = parse_gui_nav_json(json_path)
    
    print("Building platform structure...")
    platforms = build_platforms_from_json(nav_data)
    
    total_pages = count_total_pages(platforms)
    print(f"\nTotal platforms: {len(platforms)}")
    print(f"Total categories: {sum(len(p.categories) for p in platforms)}")
    print(f"Total pages (category homes + features): {total_pages}")
    
    # Convert to dict for JSON serialization
    manifest_dict = {
        'platforms': [
            {
                'id': p.id,
                'label': p.label,
                'path': p.path,
                'actorScope': p.actor_scope,
                'order': p.order,
                'categories': [
                    {
                        'id': c.id,
                        'label': c.label,
                        'homeRoute': c.home_route,
                        'homeComponentPath': c.home_component_path,
                        'homeBestCommit': c.home_best_commit or 'stable',
                        'actorScope': c.actor_scope,
                        'order': c.order,
                        'features': [
                            {
                                'id': f.id,
                                'label': f.label,
                                'route': f.route,
                                'componentPath': f.component_path,
                                'bestCommit': f.best_commit or 'stable',
                                'actorScope': f.actor_scope,
                                'order': f.order,
                                'isNew': f.is_new
                            }
                            for f in c.features
                        ]
                    }
                    for c in p.categories
                ]
            }
            for p in platforms
        ]
    }
    
    # Save manifest
    output_file = repo_root / 'frontend' / 'src' / 'data' / 'iaManifest.complete.json'
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(manifest_dict, f, indent=2)
    
    print(f"\nComplete IA manifest saved to: {output_file}")
    
    # Print summary by platform
    print("\nPlatforms and page counts:")
    for platform in platforms:
        cat_count = len(platform.categories)
        feat_count = sum(len(c.features) for c in platform.categories)
        total = cat_count + feat_count
        print(f"  {platform.label}: {cat_count} categories, {feat_count} features, {total} total pages")

if __name__ == '__main__':
    main()

