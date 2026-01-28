#!/usr/bin/env python3
"""
Restore pages using pageRegistry.ts as the route→component mapping source of truth.
Then build IA manifest from gui_nav.latest.json and ensure all pages are restored.
"""

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional

# Source commits
STABLE_COMMIT = "3a154a6e6305fe9f3a760f44b1b10d73e1ed3256"
INCREMENTS_COMMIT = "58cfc345630f68bf10909538aba48c12f87ce9df"
BACKUP_COMMIT = "4acea80190121b8ab79d8cd1367166bcfead8bde"

REPO_ROOT = Path(__file__).parent.parent
FRONTEND_SRC = REPO_ROOT / "frontend" / "src"
PAGE_REGISTRY = FRONTEND_SRC / "nav" / "pageRegistry.ts"
GUI_NAV_JSON = REPO_ROOT / "documentation" / "gui_nav_structure" / "gui_nav.latest.json"
IA_MANIFEST_OUT = FRONTEND_SRC / "data" / "iaManifest.ts"

def run_git(cmd: List[str], check: bool = False) -> str:
    """Run git command."""
    try:
        result = subprocess.run(
            ["git"] + cmd,
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=check
        )
        return result.stdout.strip()
    except:
        return ""

def parse_page_registry() -> Dict[str, str]:
    """Parse pageRegistry.ts to get route→component mappings."""
    if not PAGE_REGISTRY.exists():
        return {}
    
    content = PAGE_REGISTRY.read_text()
    mappings = {}
    
    # Pattern: '/route': () => import('../pages/Component'),
    pattern = r"'([^']+)':\s*\(\)\s*=>\s*import\(['\"]([^'\"]+)['\"]\)"
    matches = re.findall(pattern, content)
    
    for route, import_path in matches:
        # Convert import path to file path
        # '../pages/Component' -> 'pages/Component.tsx'
        component_path = import_path.replace('../', '').replace('../', '')
        if not component_path.endswith('.tsx'):
            component_path += '.tsx'
        mappings[route] = component_path
    
    return mappings

def score_page_content(content: str) -> int:
    """Score page implementation quality."""
    if not content:
        return -10
    
    score = 0
    
    # +3: Execute wired to API
    if "Execute" in content and any(k in content.lower() for k in ["fetch", "api", "usequery", "usemutation", "axios"]):
        score += 3
    
    # +2: Results rendering real data
    if "Results" in content and any(k in content.lower() for k in ["table", "chart", "data", "map"]):
        score += 2
    
    # +1: Each required section
    for section in ["Parameters", "Configuration", "Environment"]:
        if section in content:
            score += 1
    
    # Penalties
    if any(k in content.lower() for k in ["todo", "stub", "placeholder", "coming soon"]):
        score -= 2
    
    return score

def get_best_commit_for_component(component_path: str) -> Tuple[str, str]:
    """Find best commit for a component."""
    commits = [
        (STABLE_COMMIT, "stable"),
        (INCREMENTS_COMMIT, "increments"),
        (BACKUP_COMMIT, "backup")
    ]
    
    best_commit = STABLE_COMMIT
    best_name = "stable"
    best_score = -100
    
    full_path = f"frontend/src/{component_path}"
    
    for commit, name in commits:
        try:
            content = run_git(["show", f"{commit}:{full_path}"], check=False)
            score = score_page_content(content)
            if score > best_score:
                best_score = score
                best_commit = commit
                best_name = name
        except:
            continue
    
    return best_commit, best_name

def restore_component(component_path: str, commit: str, target_path: Path) -> bool:
    """Restore component from commit."""
    full_path = f"frontend/src/{component_path}"
    try:
        content = run_git(["show", f"{commit}:{full_path}"], check=False)
        if content:
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text(content, encoding='utf-8')
            return True
    except:
        pass
    return False

def build_ia_manifest() -> List[Dict]:
    """Build IA manifest from gui_nav.latest.json."""
    with open(GUI_NAV_JSON, 'r') as f:
        nav_data = json.load(f)
    
    # Parse page registry for route→component mappings
    route_to_component = parse_page_registry()
    
    platforms = []
    platform_map = {}
    platform_order = 0
    
    for edition_name, edition_data in nav_data.items():
        actor_scope = "personal" if "Personal" in edition_name else ("enterprise" if "Enterprise" in edition_name else "both")
        
        for platform_group_name, platform_group_data in edition_data.items():
            platform_id = platform_group_name.lower().replace(" ", "_").replace("&", "and").replace("-", "_")
            
            if platform_id not in platform_map:
                platform = {
                    'id': platform_id,
                    'label': platform_group_name,
                    'path': f'/{platform_id.replace("_", "-")}',
                    'actorScope': actor_scope,
                    'order': platform_order,
                    'categories': []
                }
                platforms.append(platform)
                platform_map[platform_id] = platform
                platform_order += 1
            else:
                platform = platform_map[platform_id]
                if platform['actorScope'] != actor_scope:
                    platform['actorScope'] = 'both'
            
            for category_name, features_list in platform_group_data.items():
                if not isinstance(features_list, list):
                    continue
                
                category_id = category_name.lower().replace(" ", "_").replace("&", "and").replace("-", "_")
                
                category_home = None
                category_features = []
                
                for idx, feature in enumerate(features_list):
                    if not isinstance(feature, dict):
                        continue
                    
                    route = feature.get('path', '').strip()
                    title = feature.get('title', '').strip()
                    
                    if not route or not title:
                        continue
                    
                    # Get component path from registry, or guess
                    component_path = route_to_component.get(route)
                    if not component_path:
                        # Fallback: guess from route
                        parts = route.strip("/").split("/")
                        if len(parts) > 1:
                            dir_name = "/".join(parts[:-1])
                            file_name = "".join(word.capitalize() for word in parts[-1].split("-"))
                            component_path = f"pages/{dir_name}/{file_name}.tsx"
                        else:
                            file_name = "".join(word.capitalize() for word in parts[0].split("-")) if parts else "Dashboard"
                            component_path = f"pages/{file_name}.tsx"
                    
                    # Find best commit
                    best_commit, commit_name = get_best_commit_for_component(component_path)
                    
                    if idx == 0:
                        category_home = {
                            'route': route,
                            'label': title,
                            'componentPath': component_path,
                            'bestCommit': commit_name
                        }
                    else:
                        feature_id = route.strip("/").replace("/", "_").replace("-", "_")
                        category_features.append({
                            'id': feature_id,
                            'label': title,
                            'route': route,
                            'componentPath': component_path,
                            'bestCommit': commit_name,
                            'order': idx
                        })
                
                if category_home:
                    category = {
                        'id': category_id,
                        'label': category_name,
                        'homeRoute': category_home['route'],
                        'homeComponentPath': category_home['componentPath'],
                        'homeBestCommit': category_home['bestCommit'],
                        'features': category_features,
                        'actorScope': actor_scope,
                        'order': len(platform['categories'])
                    }
                    platform['categories'].append(category)
    
    return platforms

def generate_ts_manifest(platforms: List[Dict]):
    """Generate TypeScript IA manifest."""
    ts_content = """/**
 * Generated IA Manifest - DO NOT EDIT MANUALLY
 * Generated from gui_nav.latest.json
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

export const iaManifest: IAPlatform[] = """
    
    ts_content += json.dumps(platforms, indent=2, ensure_ascii=False)
    
    ts_content += """

export function getPlatforms(actorScope: ActorScope): IAPlatform[] {
  return iaManifest.filter(p => p.actorScope === 'both' || p.actorScope === actorScope)
}

export function getCategories(platformId: string, actorScope: ActorScope): IACategory[] {
  const platform = iaManifest.find(p => p.id === platformId)
  if (!platform) return []
  if (platform.actorScope !== 'both' && platform.actorScope !== actorScope) return []
  return platform.categories.filter(c => c.actorScope === 'both' || c.actorScope === actorScope)
}

export function getFeatures(platformId: string, categoryId: string, actorScope: ActorScope): IAFeature[] {
  const platform = iaManifest.find(p => p.id === platformId)
  if (!platform) return []
  const category = platform.categories.find(c => c.id === categoryId)
  if (!category) return []
  if (category.actorScope !== 'both' && category.actorScope !== actorScope) return []
  return category.features.filter(f => f.actorScope === 'both' || f.actorScope === actorScope)
}

export function findRouteContext(route: string): {
  platform?: IAPlatform
  category?: IACategory
  feature?: IAFeature
  isCategoryHome: boolean
} {
  for (const platform of iaManifest) {
    for (const category of platform.categories) {
      if (route === category.homeRoute) {
        return { platform, category, isCategoryHome: true }
      }
      for (const feature of category.features) {
        if (route === feature.route || route.startsWith(feature.route + '/')) {
          return { platform, category, feature, isCategoryHome: false }
        }
      }
    }
  }
  return { isCategoryHome: false }
}
"""
    
    IA_MANIFEST_OUT.write_text(ts_content, encoding='utf-8')

def main():
    print("=" * 80)
    print("Page Restoration Using Registry")
    print("=" * 80)
    print()
    
    print("Step 1: Parsing pageRegistry.ts...")
    route_to_component = parse_page_registry()
    print(f"✓ Found {len(route_to_component)} route→component mappings")
    
    print()
    print("Step 2: Building IA manifest...")
    platforms = build_ia_manifest()
    print(f"✓ Found {len(platforms)} platforms")
    
    total_categories = sum(len(p['categories']) for p in platforms)
    total_features = sum(len(c['features']) for p in platforms for c in p['categories'])
    total_pages = total_categories + total_features
    print(f"✓ Found {total_categories} categories, {total_features} features")
    print(f"✓ Total pages: {total_pages}")
    
    print()
    print("Step 3: Restoring pages...")
    commit_map = {'stable': STABLE_COMMIT, 'increments': INCREMENTS_COMMIT, 'backup': BACKUP_COMMIT}
    
    restored = 0
    failed = 0
    
    for platform in platforms:
        for category in platform['categories']:
            # Restore category home
            home_path = FRONTEND_SRC / category['homeComponentPath']
            commit = commit_map.get(category['homeBestCommit'], STABLE_COMMIT)
            if restore_component(category['homeComponentPath'], commit, home_path):
                restored += 1
            else:
                failed += 1
            
            # Restore features
            for feature in category['features']:
                feature_path = FRONTEND_SRC / feature['componentPath']
                commit = commit_map.get(feature['bestCommit'], STABLE_COMMIT)
                if restore_component(feature['componentPath'], commit, feature_path):
                    restored += 1
                else:
                    failed += 1
    
    print(f"✓ Restored {restored} pages")
    if failed > 0:
        print(f"⚠ {failed} pages not found")
    
    print()
    print("Step 4: Generating IA manifest...")
    generate_ts_manifest(platforms)
    print(f"✓ Generated {IA_MANIFEST_OUT}")
    
    print()
    print("=" * 80)
    print("Complete!")
    print(f"Total pages: {total_pages}, Restored: {restored}, Missing: {failed}")
    print("=" * 80)

if __name__ == '__main__':
    main()

