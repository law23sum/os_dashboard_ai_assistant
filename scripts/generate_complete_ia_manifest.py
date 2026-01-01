#!/usr/bin/env python3
"""
Generate Complete IA Manifest from GUI Nav JSON
- Converts GUI nav structure to TypeScript IA manifest
- Ensures all ~444 pages are included
- Maintains IA compliance (Platforms→Categories→Features)
"""

import json
from pathlib import Path
from typing import Dict, List

REPO_ROOT = Path(__file__).parent.parent
GUI_NAV_JSON = REPO_ROOT / "documentation/gui_nav_structure/gui_nav.latest.json"
OUTPUT_FILE = REPO_ROOT / "frontend/src/data/iaManifest.complete.ts"

def route_to_component_path(route: str) -> str:
    """Convert route to component file path"""
    if not route or route == '/':
        return 'frontend/src/pages/Dashboard.tsx'
    
    path = route.lstrip('/')
    parts = path.split('/')
    
    # Convert to PascalCase
    component_name = ''.join(word.capitalize() for word in parts[-1].split('-'))
    
    if len(parts) > 1:
        dir_path = '/'.join(parts[:-1])
        return f'frontend/src/pages/{dir_path}/{component_name}.tsx'
    else:
        return f'frontend/src/pages/{component_name}.tsx'

def generate_ia_manifest() -> str:
    """Generate TypeScript IA manifest from GUI nav JSON"""
    
    with open(GUI_NAV_JSON, 'r') as f:
        gui_nav = json.load(f)
    
    platforms = []
    platform_order = 1
    
    for edition_name, edition_platforms in gui_nav.items():
        # Determine actor scope
        if 'Personal' in edition_name:
            actor_scope = 'personal'
        elif 'Enterprise' in edition_name:
            actor_scope = 'enterprise'
        else:
            actor_scope = 'both'
        
        for platform_name, categories in edition_platforms.items():
            # Convert platform name to ID and path
            platform_id = platform_name.lower().replace(' ', '-').replace('&', '').replace(' ', '')
            platform_path = f'/{platform_id.replace(" ", "-")}'
            
            # Special cases
            if 'Mission Control' in platform_name:
                platform_id = 'mission-control'
                platform_path = '/'
            elif 'Workspaces' in platform_name:
                platform_id = 'workspaces'
                platform_path = '/workspaces'
            elif 'AI Fabric' in platform_name:
                platform_id = 'ai-fabric'
                platform_path = '/ai'
            elif 'Drivers' in platform_name:
                platform_id = 'drivers'
                platform_path = '/drivers'
            elif 'Data' in platform_name:
                platform_id = 'data'
                platform_path = '/data'
            elif 'Docs' in platform_name:
                platform_id = 'docs'
                platform_path = '/docs'
            elif 'Settings' in platform_name:
                platform_id = 'settings'
                platform_path = '/settings'
            elif 'Governance' in platform_name:
                platform_id = 'governance'
                platform_path = '/governance'
            elif 'Observability' in platform_name:
                platform_id = 'observability'
                platform_path = '/observability'
            elif 'Operations' in platform_name:
                platform_id = 'operations'
                platform_path = '/operations'
            elif 'Roadmap' in platform_name:
                platform_id = 'roadmap'
                platform_path = '/roadmap'
            elif 'Vision' in platform_name:
                platform_id = 'vision'
                platform_path = '/vision'
            
            categories_list = []
            category_order = 1
            
            for category_name, features in categories.items():
                if not features:
                    continue
                
                category_id = category_name.lower().replace(' ', '-').replace('&', '').replace('/', '-')
                
                # Get category home route (first feature's route parent)
                first_feature = features[0]
                first_route = first_feature.get('path', '')
                if '/' in first_route:
                    category_home_route = '/'.join(first_route.split('/')[:-1]) or first_route
                else:
                    category_home_route = first_route
                
                category_home_component = route_to_component_path(category_home_route)
                
                features_list = []
                feature_order = 1
                
                for feature in features:
                    feature_route = feature.get('path', '')
                    if not feature_route:
                        continue
                    
                    feature_id = feature_route.lstrip('/').replace('/', '-').replace('-', '-')
                    feature_label = feature.get('title', feature_id)
                    feature_component = route_to_component_path(feature_route)
                    
                    features_list.append({
                        'id': feature_id,
                        'label': f'"{feature_label}"',
                        'route': f'"{feature_route}"',
                        'componentPath': f'"{feature_component}"',
                        'bestCommit': "'stable'",
                        'actorScope': f"'{actor_scope}'",
                        'order': feature_order
                    })
                    feature_order += 1
                
                categories_list.append({
                    'id': category_id,
                    'label': f'"{category_name}"',
                    'homeRoute': f'"{category_home_route}"',
                    'homeComponentPath': f'"{category_home_component}"',
                    'homeBestCommit': "'stable'",
                    'features': features_list,
                    'actorScope': f"'{actor_scope}'",
                    'order': category_order
                })
                category_order += 1
            
            platforms.append({
                'id': platform_id,
                'label': f'"{platform_name}"',
                'path': f'"{platform_path}"',
                'categories': categories_list,
                'actorScope': f"'{actor_scope}'",
                'order': platform_order
            })
            platform_order += 1
    
    # Generate TypeScript
    ts_code = '''/**
 * Complete IA Manifest - Generated from gui_nav.latest.json
 * Single Source of Truth for Navigation Structure
 * 
 * IA Rules:
 * - Platforms = top nav dropdown tabs
 * - Categories = dropdown items (route to category home)
 * - Features = left sidebar items (never in dropdown)
 */

export type ActorScope = 'personal' | 'enterprise' | 'both'

export interface IAFeature {
  id: string
  label: string
  route: string
  componentPath: string
  bestCommit: 'stable' | 'increments' | 'backup'
  actorScope: ActorScope
  order: number
}

export interface IACategory {
  id: string
  label: string
  homeRoute: string
  homeComponentPath: string
  homeBestCommit: 'stable' | 'increments' | 'backup'
  features: IAFeature[]
  actorScope: ActorScope
  order: number
}

export interface IAPlatform {
  id: string
  label: string
  path: string
  categories: IACategory[]
  actorScope: ActorScope
  order: number
}

export const iaManifest: IAPlatform[] = [
'''
    
    for platform in platforms:
        ts_code += f'''  {{
    id: '{platform["id"]}',
    label: {platform["label"]},
    path: {platform["path"]},
    actorScope: {platform["actorScope"]},
    order: {platform["order"]},
    categories: [
'''
        for category in platform['categories']:
            ts_code += f'''      {{
        id: '{category["id"]}',
        label: {category["label"]},
        homeRoute: {category["homeRoute"]},
        homeComponentPath: {category["homeComponentPath"]},
        homeBestCommit: {category["homeBestCommit"]},
        actorScope: {category["actorScope"]},
        order: {category["order"]},
        features: [
'''
            for feature in category['features']:
                ts_code += f'''          {{
            id: '{feature["id"]}',
            label: {feature["label"]},
            route: {feature["route"]},
            componentPath: {feature["componentPath"]},
            bestCommit: {feature["bestCommit"]},
            actorScope: {feature["actorScope"]},
            order: {feature["order"]},
          }},
'''
            ts_code += '''        ],
      },
'''
        ts_code += '''    ],
  },
'''
    
    ts_code += ''']
'''
    
    return ts_code

def main():
    print("Generating complete IA manifest...")
    
    ts_code = generate_ia_manifest()
    
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, 'w') as f:
        f.write(ts_code)
    
    print(f"Generated IA manifest: {OUTPUT_FILE}")
    
    # Count pages
    with open(GUI_NAV_JSON, 'r') as f:
        gui_nav = json.load(f)
    
    total_pages = 0
    for edition, platforms in gui_nav.items():
        for platform_name, categories in platforms.items():
            for category_name, features in categories.items():
                total_pages += len(features)
    
    print(f"Total pages in manifest: {total_pages}")
    print(f"Target: ~444 pages")
    
    return 0

if __name__ == '__main__':
    exit(main())
