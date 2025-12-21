#!/usr/bin/env python3
"""
Generate IA manifest from existing navigationStructure.ts
Reorganizes structure to follow IA rules:
- Platforms = top nav dropdown triggers
- Categories = dropdown items (category home pages)
- Features = sidebar items
"""

import re
import json
from pathlib import Path
from typing import Dict, List

def parse_navigation_structure(file_path: Path) -> Dict:
    """Parse navigationStructure.ts and extract structure."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Extract categories, platforms, and features
    structure = {
        'categories': [],
        'platforms': [],
        'features': []
    }
    
    # Parse categories (top-level)
    category_pattern = r"id:\s*['\"]([^'\"]+)['\"],\s*label:\s*['\"]([^'\"]+)['\"]"
    categories = re.findall(category_pattern, content)
    
    # Parse platforms within categories
    # Look for platform objects
    platform_pattern = r"id:\s*['\"]([^'\"]+)['\"],\s*label:\s*['\"]([^'\"]+)['\"],\s*path:\s*['\"]([^'\"]+)['\"]"
    platforms = re.findall(platform_pattern, content)
    
    # Parse features within platforms
    feature_pattern = r"id:\s*['\"]([^'\"]+)['\"],\s*label:\s*['\"]([^'\"]+)['\"],\s*path:\s*['\"]([^'\"]+)['\"]"
    features = re.findall(feature_pattern, content)
    
    # More sophisticated parsing - extract nested structure
    # Find category blocks
    category_blocks = re.finditer(
        r"id:\s*['\"]([^'\"]+)['\"],\s*label:\s*['\"]([^'\"]+)['\"].*?platforms:\s*\[(.*?)\],",
        content,
        re.DOTALL
    )
    
    ia_manifest = []
    platform_id_map = {}
    category_id_map = {}
    
    for cat_match in category_blocks:
        cat_id = cat_match.group(1)
        cat_label = cat_match.group(2)
        platforms_block = cat_match.group(3)
        
        # Extract platforms in this category
        platform_matches = re.finditer(
            r"id:\s*['\"]([^'\"]+)['\"],\s*label:\s*['\"]([^'\"]+)['\"],\s*path:\s*['\"]([^'\"]+)['\"].*?features:\s*\[(.*?)\],",
            platforms_block,
            re.DOTALL
        )
        
        platforms_list = []
        for plat_match in platform_matches:
            plat_id = plat_match.group(1)
            plat_label = plat_match.group(2)
            plat_path = plat_match.group(3)
            features_block = plat_match.group(4)
            
            # Extract features in this platform
            feature_matches = re.finditer(
                r"id:\s*['\"]([^'\"]+)['\"],\s*label:\s*['\"]([^'\"]+)['\"],\s*path:\s*['\"]([^'\"]+)['\"]",
                features_block
            )
            
            features_list = []
            for feat_match in feature_matches:
                feat_id = feat_match.group(1)
                feat_label = feat_match.group(2)
                feat_path = feat_match.group(3)
                
                features_list.append({
                    'id': feat_id,
                    'label': feat_label,
                    'route': feat_path,
                    'componentPath': f"frontend/src/pages/{feat_label.replace(' ', '')}.tsx",
                    'bestCommit': 'stable',
                    'actorScope': 'both',
                    'order': len(features_list) + 1
                })
            
            platforms_list.append({
                'id': plat_id,
                'label': plat_label,
                'path': plat_path,
                'categories': [{
                    'id': cat_id,
                    'label': cat_label,
                    'homeRoute': plat_path,  # Platform path becomes category home
                    'homeComponentPath': f"frontend/src/pages/{cat_label.replace(' ', '')}Home.tsx",
                    'homeBestCommit': 'stable',
                    'features': features_list,
                    'actorScope': 'both',
                    'order': 1
                }],
                'actorScope': 'both',
                'order': len(platforms_list) + 1
            })
        
        # Create platform entry for this category
        # In IA structure: Platform contains Categories, Categories contain Features
        # Current structure: Category contains Platforms, Platforms contain Features
        # Need to reorganize: Each Platform becomes a top-level platform
        # Each Category becomes a category within its platform
        # Features stay as features
        
        for platform in platforms_list:
            # Check if platform already exists
            existing_platform = next((p for p in ia_manifest if p['id'] == platform['id']), None)
            if existing_platform:
                # Add category to existing platform
                existing_platform['categories'].extend(platform['categories'])
            else:
                ia_manifest.append(platform)
    
    return ia_manifest

def main():
    """Generate IA manifest."""
    nav_file = Path('frontend/src/data/navigationStructure.ts')
    
    if not nav_file.exists():
        print(f"Error: {nav_file} not found")
        return
    
    print("Parsing navigation structure...")
    manifest = parse_navigation_structure(nav_file)
    
    # Count totals
    total_platforms = len(manifest)
    total_categories = sum(len(p['categories']) for p in manifest)
    total_features = sum(len(c['features']) for p in manifest for c in p['categories'])
    total_pages = total_categories + total_features
    
    print(f"\nGenerated IA Manifest:")
    print(f"  Platforms: {total_platforms}")
    print(f"  Categories: {total_categories}")
    print(f"  Features: {total_features}")
    print(f"  Total Pages: {total_pages}")
    
    # Save manifest
    output_file = Path('frontend/src/data/iaManifest.ts')
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Generate TypeScript file
    ts_content = f"""/**
 * IA Manifest - Generated from navigationStructure.ts
 * Single Source of Truth for navigation structure
 * 
 * IA Rules:
 * - Platforms = top nav dropdown triggers
 * - Categories = dropdown items (category home pages)
 * - Features = sidebar items (feature pages)
 * - NO route appears in both dropdown and sidebar
 * - NO features appear in platform dropdowns
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

export const iaManifest: IAPlatform[] = {json.dumps(manifest, indent=2)}
"""
    
    with open(output_file, 'w') as f:
        f.write(ts_content)
    
    print(f"\nSaved to: {output_file}")

if __name__ == '__main__':
    main()




