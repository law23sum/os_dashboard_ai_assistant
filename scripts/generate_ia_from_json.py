#!/usr/bin/env python3
"""
Generate complete IA manifest from gui_nav.latest.json
This is more accurate than parsing markdown
"""

import json
from pathlib import Path
from typing import Dict, List

def generate_manifest_from_json(json_file: Path) -> List[Dict]:
    """Generate IA manifest from JSON structure."""
    
    with open(json_file, 'r') as f:
        nav_data = json.load(f)
    
    platforms = []
    platform_order = 1
    
    # Process Personal Workstation Edition
    for edition_name, edition_data in nav_data.items():
        for category_name, category_data in edition_data.items():
            if not isinstance(category_data, dict):
                continue
            
            # Determine platform based on category
            platform_id = None
            platform_label = None
            platform_path = None
            
            if 'Mission Control' in category_name:
                platform_id = 'mission-control'
                platform_label = 'Mission Control'
                platform_path = '/'
            elif 'Workspaces' in category_name:
                platform_id = 'workspaces'
                platform_label = 'Workspaces'
                platform_path = '/workspaces'
            elif 'AI Fabric' in category_name:
                platform_id = 'ai-fabric'
                platform_label = 'AI Fabric'
                platform_path = '/ai'
            elif 'Drivers & Integrations' in category_name:
                platform_id = 'drivers-integrations'
                platform_label = 'Drivers & Integrations'
                platform_path = '/drivers'
            elif 'Data & Knowledge' in category_name:
                platform_id = 'data-knowledge'
                platform_label = 'Data & Knowledge'
                platform_path = '/data'
            elif 'Docs & Spec' in category_name:
                platform_id = 'docs-spec'
                platform_label = 'Docs & Spec'
                platform_path = '/docs'
            elif 'Settings & Admin' in category_name:
                platform_id = 'settings-admin'
                platform_label = 'Settings & Admin'
                platform_path = '/settings'
            elif 'Mission & Architecture' in category_name:
                platform_id = 'mission-architecture'
                platform_label = 'Mission & Architecture'
                platform_path = '/mission'
            elif 'Governance & Security' in category_name:
                platform_id = 'governance-security'
                platform_label = 'Governance & Security'
                platform_path = '/governance'
            elif 'Observability & Evidence' in category_name:
                platform_id = 'observability-evidence'
                platform_label = 'Observability & Evidence'
                platform_path = '/observability'
            elif 'Operations & Infrastructure' in category_name:
                platform_id = 'operations-infrastructure'
                platform_label = 'Operations & Infrastructure'
                platform_path = '/operations'
            elif 'Roadmap & Risks' in category_name:
                platform_id = 'roadmap-risks'
                platform_label = 'Roadmap & Risks'
                platform_path = '/roadmap'
            elif 'Vision & Meta-Stack' in category_name:
                platform_id = 'vision-meta-stack'
                platform_label = 'Vision & Meta-Stack'
                platform_path = '/vision'
            
            if not platform_id:
                continue
            
            # Find or create platform
            platform = next((p for p in platforms if p['id'] == platform_id), None)
            if not platform:
                actor_scope = 'enterprise' if 'Enterprise' in edition_name else 'both'
                platform = {
                    'id': platform_id,
                    'label': platform_label,
                    'path': platform_path,
                    'actorScope': actor_scope,
                    'order': platform_order,
                    'categories': []
                }
                platforms.append(platform)
                platform_order += 1
            
            # Process subcategories (workspace types, etc.)
            for subcat_name, features in category_data.items():
                if not isinstance(features, list):
                    continue
                
                # Create category
                category_id = subcat_name.lower().replace(' ', '-').replace('&', '').replace('/', '-')
                
                # Determine category home route from first feature or infer
                category_home_route = None
                if features and isinstance(features[0], dict) and 'path' in features[0]:
                    first_path = features[0]['path']
                    # Extract category home (e.g., /workspaces/dev from /workspaces/dev/overview)
                    if '/' in first_path:
                        parts = first_path.split('/')
                        if len(parts) >= 2:
                            category_home_route = '/'.join(parts[:2])
                
                if not category_home_route:
                    category_home_route = f"{platform_path}/{category_id}".replace('//', '/')
                
                category = {
                    'id': category_id,
                    'label': subcat_name,
                    'homeRoute': category_home_route,
                    'homeComponentPath': f"frontend/src/pages/{subcat_name.replace(' ', '').replace('&', '')}Home.tsx",
                    'homeBestCommit': 'stable',
                    'actorScope': platform['actorScope'],
                    'order': len(platform['categories']) + 1,
                    'features': []
                }
                
                # Process features
                for feature in features:
                    if not isinstance(feature, dict):
                        continue
                    
                    feature_title = feature.get('title', '')
                    feature_path = feature.get('path', '')
                    is_new = feature.get('new', False)
                    
                    if not feature_path:
                        continue
                    
                    feature_id = feature_title.lower().replace(' ', '-').replace('&', '').replace('/', '-')
                    component_name = feature_title.replace(' ', '').replace('&', '').replace('/', '')
                    
                    feature_obj = {
                        'id': feature_id,
                        'label': feature_title,
                        'route': feature_path,
                        'componentPath': f"frontend/src/pages/{component_name}.tsx",
                        'bestCommit': 'stable',
                        'actorScope': platform['actorScope'],
                        'order': len(category['features']) + 1
                    }
                    
                    category['features'].append(feature_obj)
                
                platform['categories'].append(category)
    
    return platforms

def main():
    """Generate complete IA manifest from JSON."""
    json_file = Path(__file__).parent.parent / 'documentation' / 'gui_nav_structure' / 'gui_nav.latest.json'
    
    if not json_file.exists():
        print(f"Error: {json_file} not found")
        return
    
    print("Generating IA manifest from gui_nav.latest.json...")
    platforms = generate_manifest_from_json(json_file)
    
    print(f"\nFound {len(platforms)} platforms")
    
    total_categories = sum(len(p['categories']) for p in platforms)
    total_features = sum(
        len(cat['features']) 
        for p in platforms 
        for cat in p['categories']
    )
    total_pages = total_categories + total_features
    
    print(f"  {total_categories} categories")
    print(f"  {total_features} features")
    print(f"  {total_pages} total pages")
    
    # Generate TypeScript manifest
    output_file = Path(__file__).parent.parent / 'frontend' / 'src' / 'data' / 'iaManifest.from_json.ts'
    
    ts_content = f"""/**
 * Complete IA Manifest - Generated from gui_nav.latest.json
 * Single Source of Truth for all {total_pages} pages
 */

export type ActorScope = 'personal' | 'enterprise' | 'both'

export interface IAFeature {{
  id: string
  label: string
  route: string
  componentPath: string
  bestCommit: 'stable' | 'increments' | 'backup'
  actorScope: ActorScope
  order: number
}}

export interface IACategory {{
  id: string
  label: string
  homeRoute: string
  homeComponentPath: string
  homeBestCommit: 'stable' | 'increments' | 'backup'
  features: IAFeature[]
  actorScope: ActorScope
  order: number
}}

export interface IAPlatform {{
  id: string
  label: string
  path: string
  categories: IACategory[]
  actorScope: ActorScope
  order: number
}}

export const iaManifest: IAPlatform[] = {json.dumps(platforms, indent=2)}

export function getPlatforms(actorScope: ActorScope): IAPlatform[] {{
  return iaManifest.filter(p => 
    p.actorScope === 'both' || p.actorScope === actorScope
  )
}}

export function getCategories(platformId: string, actorScope: ActorScope): IACategory[] {{
  const platform = iaManifest.find(p => p.id === platformId)
  if (!platform) return []
  
  if (platform.actorScope !== 'both' && platform.actorScope !== actorScope) {{
    return []
  }}
  
  return platform.categories.filter(c => 
    c.actorScope === 'both' || c.actorScope === actorScope
  )
}}

export function getFeatures(platformId: string, categoryId: string, actorScope: ActorScope): IAFeature[] {{
  const platform = iaManifest.find(p => p.id === platformId)
  if (!platform) return []
  
  const category = platform.categories.find(c => c.id === categoryId)
  if (!category) return []
  
  if (category.actorScope !== 'both' && category.actorScope !== actorScope) {{
    return []
  }}
  
  return category.features.filter(f => 
    f.actorScope === 'both' || f.actorScope === actorScope
  )
}}

export function findRouteContext(route: string): {{
  platform?: IAPlatform
  category?: IACategory
  feature?: IAFeature
  isCategoryHome: boolean
}} {{
  for (const platform of iaManifest) {{
    for (const category of platform.categories) {{
      if (route === category.homeRoute) {{
        return {{
          platform,
          category,
          isCategoryHome: true,
        }}
      }}
      
      for (const feature of category.features) {{
        if (route === feature.route || route.startsWith(feature.route + '/')) {{
          return {{
            platform,
            category,
            feature,
            isCategoryHome: false,
          }}
        }}
      }}
    }}
  }}
  
  return {{ isCategoryHome: false }}
}}
"""
    
    with open(output_file, 'w') as f:
        f.write(ts_content)
    
    print(f"\nGenerated manifest: {output_file}")
    print(f"Total pages: {total_pages}")

if __name__ == '__main__':
    main()

