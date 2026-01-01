#!/usr/bin/env python3
"""
Generate TypeScript IA Manifest from JSON
Converts iaManifest.complete.json to TypeScript format
"""

import json
from pathlib import Path

def generate_ts_from_json(json_path: Path, output_path: Path):
    """Generate TypeScript file from JSON manifest"""
    
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    ts_content = '''/**
 * Canonical IA Manifest - Single Source of Truth
 * Auto-generated from gui_nav.latest.json
 * 
 * Complete manifest with all 507 pages (15 platforms, 66 categories, 441 features)
 * Generated: {timestamp}
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
  isNew?: boolean
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

export const iaManifest: IAPlatform[] = {data}

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
'''
    
    # Convert JSON to TypeScript format
    import datetime
    timestamp = datetime.datetime.now().isoformat()
    ts_content = ts_content.replace('{timestamp}', timestamp)
    
    # Format the data as TypeScript - need to convert properly
    def format_value(val):
        if isinstance(val, str):
            # Check if it's a commit type
            if val in ['stable', 'increments', 'incremeents', 'backup']:
                if val == 'incremeents':
                    return "'increments'"
                return f"'{val}'"
            # Check if it's an actor scope
            if val in ['personal', 'enterprise', 'both']:
                return f"'{val}'"
            # Regular string
            return json.dumps(val)
        elif isinstance(val, bool):
            return 'true' if val else 'false'
        elif isinstance(val, (int, float)):
            return str(val)
        elif isinstance(val, list):
            return '[' + ', '.join(format_value(v) for v in val) + ']'
        elif isinstance(val, dict):
            return '{' + ', '.join(f'{k}: {format_value(v)}' for k, v in val.items()) + '}'
        else:
            return json.dumps(val)
    
    # Build TypeScript array manually for better formatting
    platforms_ts = []
    for platform in data['platforms']:
        platform_str = f'''  {{
    id: {json.dumps(platform['id'])},
    label: {json.dumps(platform['label'])},
    path: {json.dumps(platform['path'])},
    actorScope: '{platform['actorScope']}',
    order: {platform['order']},
    categories: ['''
        
        categories_ts = []
        for category in platform['categories']:
            features_ts = []
            for feature in category['features']:
                best_commit = feature.get('bestCommit', 'stable')
                if best_commit == 'incremeents':
                    best_commit = 'increments'
                is_new = feature.get('isNew', False)
                feature_str = f'''        {{
          id: {json.dumps(feature['id'])},
          label: {json.dumps(feature['label'])},
          route: {json.dumps(feature['route'])},
          componentPath: {json.dumps(feature['componentPath'])},
          bestCommit: '{best_commit}',
          actorScope: '{feature['actorScope']}',
          order: {feature['order']}{', isNew: true' if is_new else ''}
        }}'''
                features_ts.append(feature_str)
            
            home_best_commit = category.get('homeBestCommit', 'stable')
            if home_best_commit == 'incremeents':
                home_best_commit = 'increments'
            
            category_str = f'''      {{
        id: {json.dumps(category['id'])},
        label: {json.dumps(category['label'])},
        homeRoute: {json.dumps(category['homeRoute'])},
        homeComponentPath: {json.dumps(category['homeComponentPath'])},
        homeBestCommit: '{home_best_commit}',
        actorScope: '{category['actorScope']}',
        order: {category['order']},
        features: [
{chr(10).join(features_ts)}
        ]
      }}'''
            categories_ts.append(category_str)
        
        platform_str += '\n' + '\n'.join(categories_ts) + '\n    ]\n  }'
        platforms_ts.append(platform_str)
    
    data_str = '[\n' + ',\n'.join(platforms_ts) + '\n]'
    ts_content = ts_content.replace('{data}', data_str)
    
    # Write output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(ts_content)
    
    print(f"Generated TypeScript manifest: {output_path}")
    print(f"  Platforms: {len(data['platforms'])}")
    print(f"  Total categories: {sum(len(p['categories']) for p in data['platforms'])}")
    print(f"  Total features: {sum(len(c['features']) for p in data['platforms'] for c in p['categories'])}")

if __name__ == '__main__':
    repo_root = Path(__file__).parent.parent
    json_path = repo_root / 'frontend' / 'src' / 'data' / 'iaManifest.complete.json'
    output_path = repo_root / 'frontend' / 'src' / 'data' / 'iaManifest.complete.ts'
    
    generate_ts_from_json(json_path, output_path)

