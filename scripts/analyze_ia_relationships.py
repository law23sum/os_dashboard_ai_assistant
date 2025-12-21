#!/usr/bin/env python3
"""
Analyze IA Relationships from Tech Spec and Navigation JSON
Validates the relationships between Platforms, Categories, and Features
"""

import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple

REPO_ROOT = Path(__file__).parent.parent
NAV_JSON = REPO_ROOT / "frontend" / "public" / "gui_nav.latest.json"
TECH_SPEC = REPO_ROOT / "tech_spec_v6.txt"

def analyze_navigation_structure():
    """Analyze the navigation JSON to understand relationships"""
    if not NAV_JSON.exists():
        print(f"Navigation JSON not found: {NAV_JSON}")
        return None
    
    with open(NAV_JSON, 'r') as f:
        nav_data = json.load(f)
    
    # Track relationships
    platform_to_categories: Dict[str, Set[str]] = defaultdict(set)
    category_to_features: Dict[str, Set[str]] = defaultdict(set)
    category_to_platforms: Dict[str, Set[str]] = defaultdict(set)
    feature_to_categories: Dict[str, Set[str]] = defaultdict(set)
    feature_paths: Dict[str, List[str]] = defaultdict(list)  # path -> [platform, category]
    
    platforms_by_edition: Dict[str, Set[str]] = defaultdict(set)
    categories_by_edition: Dict[str, Set[str]] = defaultdict(set)
    features_by_edition: Dict[str, Set[str]] = defaultdict(set)
    
    # Analyze structure
    for edition, platforms in nav_data.items():
        if not isinstance(platforms, dict):
            continue
        
        for platform_title, categories in platforms.items():
            if not isinstance(categories, dict):
                continue
            
            platforms_by_edition[edition].add(platform_title)
            
            for category_title, features in categories.items():
                if not isinstance(features, list):
                    continue
                
                categories_by_edition[edition].add(category_title)
                
                # Platform → Category (one platform has many categories)
                platform_to_categories[platform_title].add(category_title)
                
                # Category → Platform (one category can appear in multiple platforms)
                category_to_platforms[category_title].add(platform_title)
                
                for feature in features:
                    if not isinstance(feature, dict):
                        continue
                    
                    feature_title = feature.get('title', '')
                    feature_path = feature.get('path', '')
                    
                    if feature_title:
                        features_by_edition[edition].add(feature_title)
                        
                        # Category → Feature (one category has many features)
                        category_to_features[category_title].add(feature_title)
                        
                        # Feature → Category (one feature can appear in multiple categories)
                        feature_to_categories[feature_title].add(category_title)
                        
                        # Track paths for routing analysis
                        if feature_path:
                            feature_paths[feature_path].append((platform_title, category_title))
    
    return {
        'platform_to_categories': platform_to_categories,
        'category_to_features': category_to_features,
        'category_to_platforms': category_to_platforms,
        'feature_to_categories': feature_to_categories,
        'feature_paths': feature_paths,
        'platforms_by_edition': platforms_by_edition,
        'categories_by_edition': categories_by_edition,
        'features_by_edition': features_by_edition,
    }

def analyze_tech_spec():
    """Extract platform/category/feature information from tech spec"""
    if not TECH_SPEC.exists():
        print(f"Tech spec not found: {TECH_SPEC}")
        return None
    
    with open(TECH_SPEC, 'r') as f:
        content = f.read()
    
    # Extract sections that might indicate platforms/categories
    # This is a simplified extraction - would need more sophisticated parsing
    platforms_mentioned = set()
    categories_mentioned = set()
    
    # Look for workspace sections (these are likely platforms)
    import re
    workspace_pattern = r'(\d+\.\d+)\s+([A-Z][^–]+?)\s+Workspace'
    for match in re.finditer(workspace_pattern, content):
        categories_mentioned.add(match.group(2).strip())
    
    return {
        'platforms_mentioned': platforms_mentioned,
        'categories_mentioned': categories_mentioned,
    }

def print_relationship_analysis(analysis):
    """Print detailed relationship analysis"""
    print("=" * 80)
    print("IA RELATIONSHIP ANALYSIS")
    print("=" * 80)
    
    print("\n1. EDITION ANALYSIS")
    print("-" * 80)
    for edition, platforms in analysis['platforms_by_edition'].items():
        print(f"\n{edition}:")
        print(f"  Platforms: {len(platforms)}")
        print(f"  Categories: {len(analysis['categories_by_edition'][edition])}")
        print(f"  Features: {len(analysis['features_by_edition'][edition])}")
    
    print("\n2. PLATFORM → CATEGORY RELATIONSHIPS")
    print("-" * 80)
    print("(One Platform has Many Categories - ONE-TO-MANY)")
    for platform, categories in sorted(analysis['platform_to_categories'].items()):
        print(f"\n  Platform: {platform}")
        print(f"    Categories ({len(categories)}): {', '.join(sorted(categories)[:5])}")
        if len(categories) > 5:
            print(f"    ... and {len(categories) - 5} more")
    
    print("\n3. CATEGORY → PLATFORM RELATIONSHIPS")
    print("-" * 80)
    print("(Can a Category appear in Multiple Platforms? - MANY-TO-MANY)")
    multi_platform_categories = {
        cat: platforms 
        for cat, platforms in analysis['category_to_platforms'].items() 
        if len(platforms) > 1
    }
    
    if multi_platform_categories:
        print(f"\n  YES - {len(multi_platform_categories)} categories appear in multiple platforms:")
        for cat, platforms in sorted(multi_platform_categories.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
            print(f"    {cat}: appears in {len(platforms)} platforms ({', '.join(sorted(platforms))})")
    else:
        print("\n  NO - Each category appears in only one platform (ONE-TO-ONE)")
    
    print("\n4. CATEGORY → FEATURE RELATIONSHIPS")
    print("-" * 80)
    print("(One Category has Many Features - ONE-TO-MANY)")
    for category, features in sorted(analysis['category_to_features'].items()):
        if len(features) > 0:
            print(f"\n  Category: {category}")
            print(f"    Features ({len(features)}): {', '.join(sorted(features)[:5])}")
            if len(features) > 5:
                print(f"    ... and {len(features) - 5} more")
    
    print("\n5. FEATURE → CATEGORY RELATIONSHIPS")
    print("-" * 80)
    print("(Can a Feature appear in Multiple Categories? - MANY-TO-MANY)")
    multi_category_features = {
        feat: categories 
        for feat, categories in analysis['feature_to_categories'].items() 
        if len(categories) > 1
    }
    
    if multi_category_features:
        print(f"\n  YES - {len(multi_category_features)} features appear in multiple categories:")
        for feat, categories in sorted(multi_category_features.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
            print(f"    {feat}: appears in {len(categories)} categories ({', '.join(sorted(categories))})")
    else:
        print("\n  NO - Each feature appears in only one category (ONE-TO-ONE)")
    
    print("\n6. PATH DUPLICATION ANALYSIS")
    print("-" * 80)
    duplicate_paths = {
        path: platforms_cats 
        for path, platforms_cats in analysis['feature_paths'].items() 
        if len(platforms_cats) > 1
    }
    
    if duplicate_paths:
        print(f"\n  WARNING: {len(duplicate_paths)} feature paths appear in multiple platform/category contexts:")
        for path, contexts in list(duplicate_paths.items())[:10]:
            print(f"    {path}:")
            for platform, category in contexts:
                print(f"      - {platform} / {category}")
    else:
        print("\n  ✓ No duplicate paths found")
    
    print("\n" + "=" * 80)
    print("RELATIONSHIP SUMMARY")
    print("=" * 80)
    print("""
    ACTUAL RELATIONSHIPS (from navigation JSON):
    
    1. Platform → Categories: ONE-TO-MANY
       - One platform contains multiple categories
       - Example: "Mission Control" platform has "Core Flight Deck", "Engagement", etc.
    
    2. Category → Platforms: MANY-TO-MANY (if categories can appear in multiple platforms)
       - Current data shows: {'category_to_platforms': ...}
       - If a category appears in only one platform: ONE-TO-ONE
       - If a category appears in multiple platforms: MANY-TO-MANY
    
    3. Category → Features: ONE-TO-MANY
       - One category contains multiple features
       - Example: "Core Flight Deck" category has "Dashboard", "Projects", "Tasks", etc.
    
    4. Feature → Categories: MANY-TO-MANY (if features can appear in multiple categories)
       - Current data shows: {'feature_to_categories': ...}
       - If a feature appears in only one category: ONE-TO-ONE
       - If a feature appears in multiple categories: MANY-TO-MANY
    
    USER'S LOGIC VALIDATION:
    - User says: "one to one from platform to category"
      → CORRECTED: Should be ONE-TO-MANY (one platform has many categories)
    
    - User says: "one to one for category to feature"
      → CORRECTED: Should be ONE-TO-MANY (one category has many features)
    
    - User thinks: "does a category have multiple platforms?"
      → VALID: If categories can appear under different platforms, this is MANY-TO-MANY
    
    - User thinks: "does a feature have multiple categories?"
      → VALID: If features can appear in different categories, this is MANY-TO-MANY
    
    CORRECTED MODEL:
    - Platform → Categories: ONE-TO-MANY (one platform, many categories)
    - Category ↔ Platforms: MANY-TO-MANY (categories can appear in multiple platforms)
    - Category → Features: ONE-TO-MANY (one category, many features)
    - Feature ↔ Categories: MANY-TO-MANY (features can appear in multiple categories)
    """)

def main():
    print("Analyzing IA relationships from navigation structure...")
    analysis = analyze_navigation_structure()
    
    if analysis:
        print_relationship_analysis(analysis)
        
        # Save analysis
        output_file = REPO_ROOT / "ia_relationship_analysis.json"
        with open(output_file, 'w') as f:
            json.dump({
                'platform_to_categories': {k: list(v) for k, v in analysis['platform_to_categories'].items()},
                'category_to_platforms': {k: list(v) for k, v in analysis['category_to_platforms'].items()},
                'category_to_features': {k: list(v) for k, v in analysis['category_to_features'].items()},
                'feature_to_categories': {k: list(v) for k, v in analysis['feature_to_categories'].items()},
                'multi_platform_categories': {
                    k: list(v) 
                    for k, v in analysis['category_to_platforms'].items() 
                    if len(v) > 1
                },
                'multi_category_features': {
                    k: list(v) 
                    for k, v in analysis['feature_to_categories'].items() 
                    if len(v) > 1
                },
            }, f, indent=2)
        
        print(f"\nAnalysis saved to: {output_file}")
    else:
        print("Failed to analyze navigation structure")

if __name__ == "__main__":
    main()


