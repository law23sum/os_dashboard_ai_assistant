#!/usr/bin/env python3
"""
Comprehensive Page Restoration Script
Restores ALL pages from source commits (3a154a6, 58cfc34, 4acea80) and reorganizes per IA rules.

IA Rules:
- Top nav: Platforms as tab titles; Categories as dropdown items (Category HOME only)
- Left sidebar: Features only (within selected Category)
- NO route appears in both dropdown and sidebar
- NO features in platform dropdowns
- Personal/Enterprise actor switch filters nav
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict

# Source commits
STABLE_COMMIT = "3a154a6e6305fe9f3a760f44b1b10d73e1ed3256"  # latest stable alpha
INCREMENTS_COMMIT = "58cfc345630f68bf10909538aba48c12f87ce9df"  # origin/incremeents
BACKUP_COMMIT = "4acea80190121b8ab79d8cd1367166bcfead8bde"  # backup broken GUI snapshot

# Paths
REPO_ROOT = Path(__file__).parent.parent
FRONTEND_SRC = REPO_ROOT / "frontend" / "src"
PAGES_DIR = FRONTEND_SRC / "pages"
GUI_NAV_JSON = REPO_ROOT / "documentation" / "gui_nav_structure" / "gui_nav.latest.json"
IA_MANIFEST_OUT = FRONTEND_SRC / "data" / "iaManifest.generated.ts"

def run_git(cmd: List[str], check: bool = True) -> str:
    """Run git command and return output."""
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
        print(f"Git error: {e.stderr}", file=sys.stderr)
        if check:
            raise
        return ""

def get_files_in_commit(commit: str, path_pattern: str = "frontend/src/pages") -> Set[str]:
    """Get all files matching pattern in a commit."""
    try:
        output = run_git(
            ["ls-tree", "-r", "--name-only", commit, path_pattern],
            check=False
        )
        return set(output.splitlines()) if output else set()
    except Exception as e:
        print(f"Error getting files from {commit}: {e}", file=sys.stderr)
        return set()

def score_page(file_path: str, commit: str) -> int:
    """
    Score a page implementation:
    +3: Execute wired to API
    +2: Results rendering real data
    +1: Each for Parameters/Config/Env sections
    -2: Stubbed/TODO
    -2: Dead links
    """
    try:
        content = run_git(["show", f"{commit}:{file_path}"], check=False)
        if not content:
            return -10  # File doesn't exist
        
        score = 0
        
        # Check for Execute section with API calls
        if "Execute" in content and ("fetch" in content or "api" in content.lower() or "useQuery" in content or "useMutation" in content):
            score += 3
        
        # Check for Results with real rendering
        if "Results" in content and ("table" in content.lower() or "chart" in content.lower() or "data" in content.lower()):
            score += 2
        
        # Check for required sections
        sections = ["Parameters", "Configuration", "Environment"]
        for section in sections:
            if section in content:
                score += 1
        
        # Penalties
        if "TODO" in content or "stub" in content.lower() or "placeholder" in content.lower():
            score -= 2
        
        if "404" in content or "not found" in content.lower():
            score -= 2
        
        return score
    except Exception as e:
        print(f"Error scoring {file_path}@{commit}: {e}", file=sys.stderr)
        return -10

def find_best_commit_for_file(file_path: str) -> Tuple[str, int]:
    """Find the best commit for a file based on scoring."""
    commits = [
        (STABLE_COMMIT, "stable"),
        (INCREMENTS_COMMIT, "increments"),
        (BACKUP_COMMIT, "backup")
    ]
    
    best_commit = None
    best_score = -100
    best_name = None
    
    for commit, name in commits:
        score = score_page(file_path, commit)
        if score > best_score:
            best_score = score
            best_commit = commit
            best_name = name
    
    return best_commit, best_score, best_name

def load_gui_nav_structure() -> Dict:
    """Load the GUI navigation structure JSON."""
    with open(GUI_NAV_JSON, 'r') as f:
        return json.load(f)

def build_ia_manifest() -> List[Dict]:
    """Build IA manifest from gui_nav.latest.json."""
    nav_data = load_gui_nav_structure()
    platforms = []
    platform_order = 0
    
    for edition_name, edition_data in nav_data.items():
        # Determine actor scope
        if "Personal" in edition_name:
            actor_scope = "personal"
        elif "Enterprise" in edition_name:
            actor_scope = "enterprise"
        else:
            actor_scope = "both"
        
        for category_group_name, category_groups in edition_data.items():
            for category_name, features_list in category_groups.items():
                # Extract platform from category structure
                # Categories are grouped under platforms
                platform_id = category_group_name.lower().replace(" ", "_").replace("&", "and")
                platform_label = category_group_name
                
                # Find or create platform
                platform = next((p for p in platforms if p['id'] == platform_id), None)
                if not platform:
                    platform = {
                        'id': platform_id,
                        'label': platform_label,
                        'path': f'/{platform_id.replace("_", "-")}',
                        'actorScope': actor_scope,
                        'order': platform_order,
                        'categories': []
                    }
                    platforms.append(platform)
                    platform_order += 1
                
                # Create category
                category_id = category_name.lower().replace(" ", "_").replace("&", "and")
                category_label = category_name
                
                # First feature is typically the category home
                category_home = None
                category_features = []
                
                for idx, feature in enumerate(features_list):
                    feature_path = feature.get('path', '')
                    feature_title = feature.get('title', '')
                    is_new = feature.get('new', False)
                    
                    if idx == 0 or not category_home:
                        # First feature is category home
                        category_home = {
                            'route': feature_path,
                            'label': feature_title,
                            'componentPath': f"pages/{feature_path.strip('/').replace('/', '/')}.tsx"
                        }
                    else:
                        # Subsequent features go in sidebar
                        category_features.append({
                            'id': feature_path.strip('/').replace('/', '_'),
                            'label': feature_title,
                            'route': feature_path,
                            'componentPath': f"pages/{feature_path.strip('/').replace('/', '/')}.tsx",
                            'order': idx
                        })
                
                # Find best commit for category home
                if category_home:
                    best_commit, score, commit_name = find_best_commit_for_file(
                        f"frontend/src/{category_home['componentPath']}"
                    )
                    category_home['bestCommit'] = commit_name
                    category_home['score'] = score
                
                # Find best commit for each feature
                for feature in category_features:
                    best_commit, score, commit_name = find_best_commit_for_file(
                        f"frontend/src/{feature['componentPath']}"
                    )
                    feature['bestCommit'] = commit_name
                    feature['score'] = score
                
                category = {
                    'id': category_id,
                    'label': category_label,
                    'homeRoute': category_home['route'] if category_home else f'/{category_id}',
                    'homeComponentPath': category_home['componentPath'] if category_home else f'pages/{category_id}.tsx',
                    'homeBestCommit': category_home.get('bestCommit', 'stable') if category_home else 'stable',
                    'features': category_features,
                    'actorScope': actor_scope,
                    'order': len(platform['categories'])
                }
                
                platform['categories'].append(category)
    
    return platforms

def restore_file_from_commit(file_path: str, commit: str, target_path: Path):
    """Restore a file from a specific commit."""
    try:
        content = run_git(["show", f"{commit}:{file_path}"], check=False)
        if content:
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text(content, encoding='utf-8')
            print(f"✓ Restored {target_path} from {commit[:8]}")
            return True
        return False
    except Exception as e:
        print(f"✗ Failed to restore {file_path} from {commit[:8]}: {e}", file=sys.stderr)
        return False

def generate_ia_manifest_ts(platforms: List[Dict]):
    """Generate TypeScript IA manifest file."""
    ts_content = """/**
 * Generated IA Manifest - DO NOT EDIT MANUALLY
 * Generated from gui_nav.latest.json and commit analysis
 * 
 * This file is auto-generated. Edit gui_nav.latest.json and regenerate.
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
    
    # Convert to JSON and format
    ts_content += json.dumps(platforms, indent=2, ensure_ascii=False)
    
    ts_content += """

/**
 * Get all platforms filtered by actor scope
 */
export function getPlatforms(actorScope: ActorScope): IAPlatform[] {
  return iaManifest.filter(p => 
    p.actorScope === 'both' || p.actorScope === actorScope
  )
}

/**
 * Get categories for a platform, filtered by actor scope
 */
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

/**
 * Get features for a category, filtered by actor scope
 */
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

/**
 * Find route context (platform/category/feature)
 */
export function findRouteContext(route: string): {
  platform?: IAPlatform
  category?: IACategory
  feature?: IAFeature
  isCategoryHome: boolean
} {
  for (const platform of iaManifest) {
    for (const category of platform.categories) {
      // Check category home
      if (route === category.homeRoute) {
        return {
          platform,
          category,
          isCategoryHome: true,
        }
      }
      
      // Check features
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
    print(f"✓ Generated IA manifest: {IA_MANIFEST_OUT}")

def main():
    print("=" * 80)
    print("Comprehensive Page Restoration Script")
    print("=" * 80)
    print()
    
    print("Step 1: Building IA manifest from gui_nav.latest.json...")
    platforms = build_ia_manifest()
    print(f"✓ Found {len(platforms)} platforms")
    
    total_categories = sum(len(p['categories']) for p in platforms)
    total_features = sum(
        len(c['features']) for p in platforms for c in p['categories']
    )
    print(f"✓ Found {total_categories} categories, {total_features} features")
    
    print()
    print("Step 2: Restoring pages from best commits...")
    
    commit_map = {
        'stable': STABLE_COMMIT,
        'increments': INCREMENTS_COMMIT,
        'backup': BACKUP_COMMIT
    }
    
    restored_count = 0
    failed_count = 0
    
    for platform in platforms:
        for category in platform['categories']:
            # Restore category home
            home_path = FRONTEND_SRC / category['homeComponentPath']
            commit = commit_map.get(category['homeBestCommit'], STABLE_COMMIT)
            source_path = f"frontend/src/{category['homeComponentPath']}"
            
            if restore_file_from_commit(source_path, commit, home_path):
                restored_count += 1
            else:
                failed_count += 1
                print(f"  ⚠ Category home not found: {category['homeRoute']}")
            
            # Restore features
            for feature in category['features']:
                feature_path = FRONTEND_SRC / feature['componentPath']
                commit = commit_map.get(feature['bestCommit'], STABLE_COMMIT)
                source_path = f"frontend/src/{feature['componentPath']}"
                
                if restore_file_from_commit(source_path, commit, feature_path):
                    restored_count += 1
                else:
                    failed_count += 1
                    print(f"  ⚠ Feature not found: {feature['route']}")
    
    print()
    print(f"✓ Restored {restored_count} pages")
    if failed_count > 0:
        print(f"⚠ {failed_count} pages not found in source commits (will use templates)")
    
    print()
    print("Step 3: Generating IA manifest TypeScript file...")
    generate_ia_manifest_ts(platforms)
    
    print()
    print("=" * 80)
    print("Restoration complete!")
    print("=" * 80)
    print(f"Total pages: {restored_count + failed_count}")
    print(f"Platforms: {len(platforms)}")
    print(f"Categories: {total_categories}")
    print(f"Features: {total_features}")

if __name__ == '__main__':
    main()





