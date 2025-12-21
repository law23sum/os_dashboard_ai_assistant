#!/usr/bin/env python3
"""
Build Route Inventory and Restore Pages
1. Analyzes routes across commits (3a154a6, 58cfc34, 4acea80)
2. Scores each page implementation
3. Builds IA manifest from gui_nav.latest.json
4. Restores pages from best commits
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict

# Source commits
STABLE_COMMIT = "3a154a6e6305fe9f3a760f44b1b10d73e1ed3256"
INCREMENTS_COMMIT = "58cfc345630f68bf10909538aba48c12f87ce9df"
BACKUP_COMMIT = "4acea80190121b8ab79d8cd1367166bcfead8bde"

REPO_ROOT = Path(__file__).parent.parent
FRONTEND_SRC = REPO_ROOT / "frontend" / "src"
PAGES_DIR = FRONTEND_SRC / "pages"
GUI_NAV_JSON = REPO_ROOT / "documentation" / "gui_nav_structure" / "gui_nav.latest.json"
IA_MANIFEST_OUT = FRONTEND_SRC / "data" / "iaManifest.generated.ts"

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
    except subprocess.CalledProcessError as e:
        return ""

def path_to_component_path(route_path: str) -> str:
    """Convert route path to component file path."""
    if route_path == "/":
        return "pages/Dashboard.tsx"
    
    # Remove leading slash and convert to path
    parts = route_path.strip("/").split("/")
    # Convert to PascalCase for component name
    component_name = "".join(word.capitalize() for word in parts[-1].split("-"))
    # Build directory path
    if len(parts) > 1:
        dir_path = "/".join(parts[:-1])
        return f"pages/{dir_path}/{component_name}.tsx"
    else:
        return f"pages/{component_name}.tsx"

def score_page_content(content: str) -> int:
    """Score page implementation quality."""
    if not content:
        return -10
    
    score = 0
    
    # +3: Execute wired to API
    if "Execute" in content and any(keyword in content.lower() for keyword in ["fetch", "api", "usequery", "usemutation", "axios", "http"]):
        score += 3
    
    # +2: Results rendering real data
    if "Results" in content and any(keyword in content.lower() for keyword in ["table", "chart", "data", "map", "list"]):
        score += 2
    
    # +1: Each required section
    for section in ["Parameters", "Configuration", "Environment"]:
        if section in content:
            score += 1
    
    # Penalties
    if any(keyword in content.lower() for keyword in ["todo", "stub", "placeholder", "coming soon", "not implemented"]):
        score -= 2
    
    if any(keyword in content.lower() for keyword in ["404", "not found", "error"]):
        score -= 2
    
    return score

def get_best_commit_for_file(relative_path: str) -> Tuple[str, int, str]:
    """Find best commit for a file."""
    commits = [
        (STABLE_COMMIT, "stable"),
        (INCREMENTS_COMMIT, "increments"),
        (BACKUP_COMMIT, "backup")
    ]
    
    best_commit = STABLE_COMMIT
    best_score = -100
    best_name = "stable"
    
    for commit, name in commits:
        try:
            content = run_git(["show", f"{commit}:{relative_path}"], check=False)
            score = score_page_content(content)
            if score > best_score:
                best_score = score
                best_commit = commit
                best_name = name
        except:
            continue
    
    return best_commit, best_score, best_name

def build_ia_manifest_from_json() -> List[Dict]:
    """Build IA manifest from gui_nav.latest.json."""
    with open(GUI_NAV_JSON, 'r') as f:
        nav_data = json.load(f)
    
    platforms = []
    platform_id_map = {}  # Track platform IDs to avoid duplicates
    platform_order = 0
    
    for edition_name, edition_data in nav_data.items():
        # Determine actor scope
        if "Personal" in edition_name:
            actor_scope = "personal"
        elif "Enterprise" in edition_name:
            actor_scope = "enterprise"
        else:
            actor_scope = "both"
        
        # Iterate through category groups (these are PLATFORMS)
        for platform_group_name, platform_group_data in edition_data.items():
            # Create platform ID
            platform_id = platform_group_name.lower().replace(" ", "_").replace("&", "and").replace("-", "_")
            
            # Get or create platform
            if platform_id not in platform_id_map:
                platform = {
                    'id': platform_id,
                    'label': platform_group_name,
                    'path': f'/{platform_id.replace("_", "-")}',
                    'actorScope': actor_scope,
                    'order': platform_order,
                    'categories': []
                }
                platforms.append(platform)
                platform_id_map[platform_id] = platform
                platform_order += 1
            else:
                platform = platform_id_map[platform_id]
                # Update actor scope if needed (merge personal + enterprise)
                if platform['actorScope'] != actor_scope:
                    platform['actorScope'] = 'both'
            
            # Iterate through categories (these are CATEGORIES within the platform)
            for category_name, features_list in platform_group_data.items():
                if not isinstance(features_list, list):
                    continue
                
                category_id = category_name.lower().replace(" ", "_").replace("&", "and").replace("-", "_")
                
                # First feature is category home, rest are sidebar features
                category_home = None
                category_features = []
                
                for idx, feature in enumerate(features_list):
                    if not isinstance(feature, dict):
                        continue
                    
                    feature_path = feature.get('path', '').strip()
                    feature_title = feature.get('title', '').strip()
                    
                    if not feature_path or not feature_title:
                        continue
                    
                    component_path = path_to_component_path(feature_path)
                    relative_path = f"frontend/src/{component_path}"
                    
                    # Find best commit
                    best_commit, score, commit_name = get_best_commit_for_file(relative_path)
                    
                    if idx == 0:
                        # First feature = category home
                        category_home = {
                            'route': feature_path,
                            'label': feature_title,
                            'componentPath': component_path,
                            'bestCommit': commit_name,
                            'score': score
                        }
                    else:
                        # Rest = sidebar features
                        feature_id = feature_path.strip("/").replace("/", "_").replace("-", "_")
                        category_features.append({
                            'id': feature_id,
                            'label': feature_title,
                            'route': feature_path,
                            'componentPath': component_path,
                            'bestCommit': commit_name,
                            'score': score,
                            'order': idx
                        })
                
                # Create category
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

def restore_file_from_commit(source_path: str, commit: str, target_path: Path) -> bool:
    """Restore file from commit."""
    try:
        content = run_git(["show", f"{commit}:{source_path}"], check=False)
        if content:
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text(content, encoding='utf-8')
            return True
        return False
    except Exception as e:
        return False

def generate_ts_manifest(platforms: List[Dict]):
    """Generate TypeScript IA manifest."""
    ts_content = """/**
 * Generated IA Manifest - DO NOT EDIT MANUALLY
 * Generated from gui_nav.latest.json and commit analysis
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
    
    # Convert to JSON
    ts_content += json.dumps(platforms, indent=2, ensure_ascii=False)
    
    ts_content += """

export function getPlatforms(actorScope: ActorScope): IAPlatform[] {
  return iaManifest.filter(p => 
    p.actorScope === 'both' || p.actorScope === actorScope
  )
}

export function getCategories(platformId: string, actorScope: ActorScope): IACategory[] {
  const platform = iaManifest.find(p => p.id === platformId)
  if (!platform) return []
  
  if (platform.actorScope !== 'both' && platform.actorScope !== actorScope) {
    return []
  }
  
  return platform.categories.filter(c => 
    c.actorScope === 'both' || c.actorScope === actorScope
  )
}

export function getFeatures(platformId: string, categoryId: string, actorScope: ActorScope): IAFeature[] {
  const platform = iaManifest.find(p => p.id === platformId)
  if (!platform) return []
  
  const category = platform.categories.find(c => c.id === categoryId)
  if (!category) return []
  
  if (category.actorScope !== 'both' && category.actorScope !== actorScope) {
    return []
  }
  
  return category.features.filter(f => 
    f.actorScope === 'both' || f.actorScope === actorScope
  )
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
        return {
          platform,
          category,
          isCategoryHome: true,
        }
      }
      
      for (const feature of category.features) {
        if (route === feature.route || route.startsWith(feature.route + '/')) {
          return {
            platform,
            category,
            feature,
            isCategoryHome: false,
          }
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
    print("Route Inventory & Page Restoration")
    print("=" * 80)
    print()
    
    print("Step 1: Building IA manifest from gui_nav.latest.json...")
    platforms = build_ia_manifest_from_json()
    print(f"✓ Found {len(platforms)} platforms")
    
    total_categories = sum(len(p['categories']) for p in platforms)
    total_features = sum(len(c['features']) for p in platforms for c in p['categories'])
    total_pages = total_categories + total_features  # Category homes + features
    print(f"✓ Found {total_categories} categories, {total_features} features")
    print(f"✓ Total pages: {total_pages}")
    print()
    
    print("Step 2: Restoring pages from best commits...")
    commit_map = {
        'stable': STABLE_COMMIT,
        'increments': INCREMENTS_COMMIT,
        'backup': BACKUP_COMMIT
    }
    
    restored = 0
    failed = 0
    
    for platform in platforms:
        for category in platform['categories']:
            # Restore category home
            home_path = FRONTEND_SRC / category['homeComponentPath']
            commit = commit_map.get(category['homeBestCommit'], STABLE_COMMIT)
            source_path = f"frontend/src/{category['homeComponentPath']}"
            
            if restore_file_from_commit(source_path, commit, home_path):
                restored += 1
                print(f"  ✓ {category['homeRoute']}")
            else:
                failed += 1
                print(f"  ⚠ {category['homeRoute']} (not found)")
            
            # Restore features
            for feature in category['features']:
                feature_path = FRONTEND_SRC / feature['componentPath']
                commit = commit_map.get(feature['bestCommit'], STABLE_COMMIT)
                source_path = f"frontend/src/{feature['componentPath']}"
                
                if restore_file_from_commit(source_path, commit, feature_path):
                    restored += 1
                else:
                    failed += 1
    
    print()
    print(f"✓ Restored {restored} pages")
    if failed > 0:
        print(f"⚠ {failed} pages not found (will need templates)")
    
    print()
    print("Step 3: Generating IA manifest TypeScript...")
    generate_ts_manifest(platforms)
    print(f"✓ Generated {IA_MANIFEST_OUT}")
    
    print()
    print("=" * 80)
    print("Complete!")
    print("=" * 80)
    print(f"Platforms: {len(platforms)}")
    print(f"Categories: {total_categories}")
    print(f"Features: {total_features}")
    print(f"Total pages: {total_pages}")
    print(f"Restored: {restored}")
    print(f"Missing: {failed}")

if __name__ == '__main__':
    main()




