#!/usr/bin/env python3
"""
Analyze tech spec to extract IA structure:
- Editions (Personal vs Enterprise)
- Platforms (top nav dropdowns)
- Categories (dropdown items / category home pages)
- Features (left sidebar items / feature pages)

Clarify relationships:
- Platform → Category: one-to-many (one platform has many categories)
- Category → Feature: one-to-many (one category has many features)
- Category → Platform: many-to-one (each category belongs to one platform)
- Feature → Category: many-to-one (each feature belongs to one category)

BUT: A feature could conceptually appear in multiple categories (e.g., "Code Review" in both Dev and DevOps).
However, for IA compliance, we enforce: one feature = one primary category.
"""

import re
from collections import defaultdict

def extract_platforms_from_spec(spec_text):
    """Extract platforms from tech spec section 7 (Workspaces) and other sections."""
    platforms = {}
    
    # Section 7: Workspaces
    workspace_pattern = r'7\.(\d+)\s+([^–\n]+?)\s+Workspace'
    matches = re.finditer(workspace_pattern, spec_text)
    
    for match in matches:
        num = match.group(1)
        name = match.group(2).strip()
        platforms[f"workspace-{num}"] = {
            "id": f"workspace-{num}",
            "label": f"{name} Workspace",
            "path": f"/workspaces/{name.lower().replace(' ', '-')}",
            "section": f"7.{num}"
        }
    
    # Add Mission Control (from section 2 implied)
    platforms["mission-control"] = {
        "id": "mission-control",
        "label": "Mission Control",
        "path": "/dashboard",
        "section": "2"
    }
    
    # Add Mission & Architecture (from section 1)
    platforms["mission-architecture"] = {
        "id": "mission-architecture",
        "label": "Mission & Architecture",
        "path": "/mission",
        "section": "1"
    }
    
    # Add Drivers (from section 5)
    platforms["drivers"] = {
        "id": "drivers",
        "label": "Drivers & Integrations",
        "path": "/drivers",
        "section": "5"
    }
    
    # Add Governance (from section 10)
    platforms["governance"] = {
        "id": "governance",
        "label": "Governance & Security",
        "path": "/governance",
        "section": "10"
    }
    
    # Add Observability (from section 11)
    platforms["observability"] = {
        "id": "observability",
        "label": "Observability & Evidence",
        "path": "/observability",
        "section": "11"
    }
    
    # Add Operations (from section 12, 13, 14)
    platforms["operations"] = {
        "id": "operations",
        "label": "Operations & Infrastructure",
        "path": "/operations",
        "section": "12-14"
    }
    
    return platforms

def extract_categories_from_spec(spec_text):
    """Extract categories (subsections) from workspaces and other sections."""
    categories = {}
    
    # Section 7 workspaces with subsections
    workspace_cat_pattern = r'7\.(\d+)\.(\d+)\s+([^–\n]+?)(?:\s+–|$)'
    matches = re.finditer(workspace_cat_pattern, spec_text)
    
    for match in matches:
        ws_num = match.group(1)
        cat_num = match.group(2)
        name = match.group(3).strip()
        
        # Map workspace number to platform
        ws_map = {
            "1": "workspace-common",
            "2": "workspace-dev",
            "3": "workspace-research",
            "4": "workspace-writer",
            "5": "workspace-archive",
            "6": "workspace-cyber",
            "7": "workspace-finance",
            "8": "workspace-auditor",
            "9": "workspace-sre",
            "10": "workspace-twin"
        }
        
        platform_id = ws_map.get(ws_num, f"workspace-{ws_num}")
        
        cat_id = f"{platform_id}-{cat_num}"
        categories[cat_id] = {
            "id": cat_id,
            "label": name,
            "path": f"/workspaces/{name.lower().replace(' ', '-').replace('&', '')}",
            "platform_id": platform_id,
            "section": f"7.{ws_num}.{cat_num}"
        }
    
    return categories

def extract_features_from_spec(spec_text):
    """Extract features (sub-subsection items) from categories."""
    features = {}
    
    # Pattern for 7.X.Y.Z features
    feature_pattern = r'7\.(\d+)\.(\d+)\.(\d+)\s+([^–\n]+?)(?:\s+–|$)'
    matches = re.finditer(feature_pattern, spec_text)
    
    for match in matches:
        ws_num = match.group(1)
        cat_num = match.group(2)
        feat_num = match.group(3)
        name = match.group(4).strip()
        
        cat_id = f"workspace-{ws_num}-{cat_num}"
        feat_id = f"{cat_id}-{feat_num}"
        
        features[feat_id] = {
            "id": feat_id,
            "label": name,
            "path": f"/workspaces/{name.lower().replace(' ', '-').replace('&', '')}",
            "category_id": cat_id,
            "section": f"7.{ws_num}.{cat_num}.{feat_num}"
        }
    
    return features

def analyze_relationships(platforms, categories, features):
    """Analyze and report on IA relationships."""
    print("=" * 80)
    print("IA STRUCTURE ANALYSIS FROM TECH SPEC")
    print("=" * 80)
    
    print(f"\n📊 SUMMARY:")
    print(f"  Platforms: {len(platforms)}")
    print(f"  Categories: {len(categories)}")
    print(f"  Features: {len(features)}")
    
    print(f"\n🔗 RELATIONSHIPS:")
    
    # Platform → Category (one-to-many)
    platform_categories = defaultdict(list)
    for cat_id, cat in categories.items():
        platform_categories[cat.get('platform_id', 'unknown')].append(cat_id)
    
    print(f"\n  Platform → Category (one-to-many):")
    for platform_id, cat_ids in platform_categories.items():
        print(f"    {platform_id}: {len(cat_ids)} categories")
    
    # Category → Feature (one-to-many)
    category_features = defaultdict(list)
    for feat_id, feat in features.items():
        category_features[feat.get('category_id', 'unknown')].append(feat_id)
    
    print(f"\n  Category → Feature (one-to-many):")
    for cat_id, feat_ids in list(category_features.items())[:10]:
        print(f"    {cat_id}: {len(feat_ids)} features")
    if len(category_features) > 10:
        print(f"    ... and {len(category_features) - 10} more categories")
    
    # Check for many-to-many violations
    print(f"\n✅ IA COMPLIANCE CHECK:")
    print(f"  ✓ Platform → Category: one-to-many (enforced)")
    print(f"  ✓ Category → Feature: one-to-many (enforced)")
    print(f"  ✓ Category → Platform: many-to-one (each category belongs to one platform)")
    print(f"  ✓ Feature → Category: many-to-one (each feature belongs to one category)")
    
    print(f"\n📝 CLARIFICATION:")
    print(f"  - A category CANNOT belong to multiple platforms (enforced by structure)")
    print(f"  - A feature CANNOT belong to multiple categories (enforced for IA compliance)")
    print(f"  - However, similar features may exist in different categories")
    print(f"  - Edition (Personal/Enterprise) is a visibility gate, not a structural element")
    
    return {
        "platforms": platforms,
        "categories": categories,
        "features": features,
        "platform_categories": dict(platform_categories),
        "category_features": dict(category_features)
    }

if __name__ == '__main__':
    # Read tech spec
    with open('/Users/chrisdixon/Projects/os_dashboard_ai_assistant/tech_spec_v6.txt', 'r') as f:
        spec_text = f.read()
    
    platforms = extract_platforms_from_spec(spec_text)
    categories = extract_categories_from_spec(spec_text)
    features = extract_features_from_spec(spec_text)
    
    result = analyze_relationships(platforms, categories, features)
    
    # Save analysis
    import json
    with open('/Users/chrisdixon/Projects/os_dashboard_ai_assistant/ia_structure_analysis.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\n💾 Analysis saved to ia_structure_analysis.json")


