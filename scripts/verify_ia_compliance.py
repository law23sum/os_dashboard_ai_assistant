#!/usr/bin/env python3
"""
Verify navigation structure follows IA rules:
- Platforms = top nav dropdown titles only
- Categories = dropdown list items (category home pages)
- Features = left sidebar only (never in dropdowns)
- No route duplication (dropdown OR sidebar, never both)
"""

import json
from pathlib import Path
from typing import Dict, Set, List

def load_nav_json(file_path: Path) -> Dict:
    """Load navigation JSON."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def verify_ia_structure(nav_data: Dict) -> Dict:
    """Verify IA structure compliance."""
    issues = []
    warnings = []
    
    platforms = set()
    categories = set()
    features = set()
    category_home_paths = set()
    feature_paths = set()
    
    # Analyze structure
    for edition_name, platforms_dict in nav_data.items():
        for platform_name, categories_dict in platforms_dict.items():
            platforms.add(platform_name)
            
            for category_name, features_list in categories_dict.items():
                category_key = f"{platform_name}::{category_name}"
                categories.add(category_key)
                
                if not isinstance(features_list, list):
                    issues.append(f"Category {category_key} has non-list features")
                    continue
                
                if len(features_list) == 0:
                    warnings.append(f"Category {category_key} has no features")
                    continue
                
                # First item should be category home
                first_feature = features_list[0]
                if isinstance(first_feature, dict) and 'path' in first_feature:
                    category_home_paths.add(first_feature['path'])
                
                # All other items are features
                for i, feature in enumerate(features_list[1:], 1):
                    if isinstance(feature, dict) and 'path' in feature:
                        path = feature['path']
                        feature_paths.add(path)
                        features.add(path)
    
    # Check for duplicates
    duplicates = category_home_paths & feature_paths
    if duplicates:
        issues.append(f"Paths appear in both category home and features: {duplicates}")
    
    # Summary
    summary = {
        'platforms': len(platforms),
        'categories': len(categories),
        'features': len(features),
        'category_homes': len(category_home_paths),
        'issues': issues,
        'warnings': warnings,
        'compliant': len(issues) == 0
    }
    
    return summary

def main():
    """Main verification function."""
    print("="*80)
    print("IA COMPLIANCE VERIFICATION")
    print("="*80)
    
    nav_files = [
        Path('frontend/public/gui_nav.latest.json'),
        Path('documentation/gui_nav_structure/gui_nav.latest.json'),
    ]
    
    for nav_file in nav_files:
        if not nav_file.exists():
            continue
        
        print(f"\nVerifying: {nav_file}")
        nav_data = load_nav_json(nav_file)
        
        if not nav_data:
            print("  ✗ Could not load navigation data")
            continue
        
        summary = verify_ia_structure(nav_data)
        
        print(f"  Platforms: {summary['platforms']}")
        print(f"  Categories: {summary['categories']}")
        print(f"  Features: {summary['features']}")
        print(f"  Category Homes: {summary['category_homes']}")
        
        if summary['compliant']:
            print("  ✓ IA Structure is compliant")
        else:
            print("  ✗ IA Structure has issues:")
            for issue in summary['issues']:
                print(f"    - {issue}")
        
        if summary['warnings']:
            print("  ⚠ Warnings:")
            for warning in summary['warnings'][:10]:  # Limit warnings
                print(f"    - {warning}")
            if len(summary['warnings']) > 10:
                print(f"    ... and {len(summary['warnings']) - 10} more warnings")

if __name__ == '__main__':
    main()
