#!/usr/bin/env python3
"""
Merge navigation structure from documentation into current navigation JSON
Ensures maximum platforms, categories, and features are preserved
"""

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
DOC_NAV = REPO_ROOT / "documentation" / "gui_nav_structure" / "gui_nav.latest.json"
CURRENT_NAV = REPO_ROOT / "frontend" / "public" / "gui_nav.latest.json"
GUI_STRUCTURE = REPO_ROOT / "documentation" / "gui_nav_structure" / "GUI_STRUCTURE_LATEST_1.md"

def parse_markdown_structure(md_file: Path) -> dict:
    """Parse the markdown GUI structure to extract platforms, categories, and features"""
    structure = {}
    
    with open(md_file, "r") as f:
        content = f.read()
    
    # Extract platform sections (e.g., "# 1) Mission & Architecture  `/mission`")
    platform_pattern = r'#\s+\d+\)\s+([^`]+)\s+`([^`]+)`'
    category_pattern = r'##\s+\d+\.\d+\s+([^`]+)\s+`([^`]+)`'
    feature_pattern = r'- `([^`]+)`\s+—\s+([^\n]+)'
    
    current_platform = None
    current_category = None
    
    for line in content.split("\n"):
        # Check for platform
        platform_match = re.match(platform_pattern, line)
        if platform_match:
            platform_name = platform_match.group(1).strip()
            platform_path = platform_match.group(2).strip()
            current_platform = platform_name
            if current_platform not in structure:
                structure[current_platform] = {}
            continue
        
        # Check for category
        category_match = re.match(category_pattern, line)
        if category_match:
            category_name = category_match.group(1).strip()
            category_path = category_match.group(2).strip()
            if current_platform:
                current_category = category_name
                if current_category not in structure[current_platform]:
                    structure[current_platform][current_category] = []
            continue
        
        # Check for feature
        feature_match = re.match(feature_pattern, line)
        if feature_match and current_platform and current_category:
            feature_path = feature_match.group(1).strip()
            feature_desc = feature_match.group(2).strip()
            # Extract feature name from path
            feature_name = feature_path.split("/")[-1].replace("-", " ").title()
            structure[current_platform][current_category].append({
                "title": feature_name,
                "path": feature_path,
                "new": "[NEW]" in feature_desc or "[Enterprise]" in feature_desc,
                "description": feature_desc
            })
    
    return structure

def merge_navigation_structures(doc_json: dict, current_json: dict, md_structure: dict) -> dict:
    """Merge navigation structures, prioritizing maximum content"""
    merged = {"Personal Workstation Edition": {}, "Enterprise Control Plane Add‑Ons": {}}
    
    # Start with documentation JSON structure
    for edition, platforms in doc_json.items():
        if edition not in merged:
            merged[edition] = {}
        
        for platform, categories in platforms.items():
            if platform not in merged[edition]:
                merged[edition][platform] = {}
            
            for category, features in categories.items():
                if category not in merged[edition][platform]:
                    merged[edition][platform][category] = []
                
                # Add features from documentation
                feature_set = set()
                for feature in features:
                    feature_key = (feature.get("path", ""), feature.get("title", ""))
                    if feature_key not in feature_set:
                        merged[edition][platform][category].append(feature)
                        feature_set.add(feature_key)
    
    # Merge in current JSON, adding any missing items
    for edition, platforms in current_json.items():
        if edition not in merged:
            merged[edition] = {}
        
        for platform, categories in platforms.items():
            if platform not in merged[edition]:
                merged[edition][platform] = {}
            
            for category, features in categories.items():
                if category not in merged[edition][platform]:
                    merged[edition][platform][category] = []
                
                # Add features from current, avoiding duplicates
                existing_paths = {f.get("path", "") for f in merged[edition][platform][category]}
                for feature in features:
                    if feature.get("path", "") not in existing_paths:
                        merged[edition][platform][category].append(feature)
    
    # Add from markdown structure (most authoritative)
    for platform, categories in md_structure.items():
        # Find matching platform in merged structure
        for edition in merged.values():
            for existing_platform in edition.keys():
                if platform.lower() in existing_platform.lower() or existing_platform.lower() in platform.lower():
                    for category, features in categories.items():
                        if category not in edition[existing_platform]:
                            edition[existing_platform][category] = []
                        
                        # Add features, avoiding duplicates
                        existing_paths = {f.get("path", "") for f in edition[existing_platform][category]}
                        for feature in features:
                            if feature.get("path", "") not in existing_paths:
                                edition[existing_platform][category].append(feature)
                    break
    
    return merged

def main():
    """Main merge function"""
    print("="*60)
    print("MERGING NAVIGATION FROM DOCUMENTATION")
    print("="*60)
    
    # Load documentation JSON
    print("\n1. Loading documentation navigation JSON...")
    with open(DOC_NAV, "r") as f:
        doc_json = json.load(f)
    
    # Load current navigation JSON
    print("2. Loading current navigation JSON...")
    if CURRENT_NAV.exists():
        with open(CURRENT_NAV, "r") as f:
            current_json = json.load(f)
    else:
        current_json = {}
        print("   Warning: Current navigation JSON not found, starting fresh")
    
    # Parse markdown structure
    print("3. Parsing markdown GUI structure...")
    md_structure = parse_markdown_structure(GUI_STRUCTURE)
    
    # Count elements
    doc_platforms = sum(len(platforms) for platforms in doc_json.values())
    doc_categories = sum(
        len(categories) 
        for platforms in doc_json.values() 
        for categories in platforms.values()
    )
    doc_features = sum(
        len(features) 
        for platforms in doc_json.values() 
        for categories in platforms.values() 
        for features in categories.values()
    )
    
    current_platforms = sum(len(platforms) for platforms in current_json.values()) if current_json else 0
    current_categories = sum(
        len(categories) 
        for platforms in current_json.values() 
        for categories in platforms.values()
    ) if current_json else 0
    current_features = sum(
        len(features) 
        for platforms in current_json.values() 
        for categories in platforms.values() 
        for features in categories.values()
    ) if current_json else 0
    
    print(f"\nDocumentation: {doc_platforms} platforms, {doc_categories} categories, {doc_features} features")
    print(f"Current: {current_platforms} platforms, {current_categories} categories, {current_features} features")
    
    # Merge structures
    print("\n4. Merging navigation structures...")
    merged = merge_navigation_structures(doc_json, current_json, md_structure)
    
    # Count merged elements
    merged_platforms = sum(len(platforms) for platforms in merged.values())
    merged_categories = sum(
        len(categories) 
        for platforms in merged.values() 
        for categories in platforms.values()
    )
    merged_features = sum(
        len(features) 
        for platforms in merged.values() 
        for categories in platforms.values() 
        for features in categories.values()
    )
    
    print(f"Merged: {merged_platforms} platforms, {merged_categories} categories, {merged_features} features")
    
    # Save merged structure
    print("\n5. Saving merged navigation JSON...")
    CURRENT_NAV.parent.mkdir(parents=True, exist_ok=True)
    with open(CURRENT_NAV, "w") as f:
        json.dump(merged, f, indent=2)
    
    print(f"\n✅ Navigation merged successfully!")
    print(f"   Saved to: {CURRENT_NAV}")
    print(f"\nSummary:")
    print(f"   Platforms: {merged_platforms} (target: max)")
    print(f"   Categories: {merged_categories} (target: max)")
    print(f"   Features: {merged_features} (target: max)")

if __name__ == "__main__":
    main()



