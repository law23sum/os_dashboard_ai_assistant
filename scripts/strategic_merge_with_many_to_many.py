#!/usr/bin/env python3
"""
Strategic Merge Script with Many-to-Many Relationship Handling
- Merges branches to maximize platforms, categories, and features
- Handles many-to-many relationships correctly
- Resolves duplicate paths intelligently
- Preserves edition-specific visibility
"""

import json
import subprocess
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple, Optional
import shutil

REPO_ROOT = Path(__file__).parent.parent
NAV_JSON = REPO_ROOT / "frontend" / "public" / "gui_nav.latest.json"
FRONTEND_PAGES = REPO_ROOT / "frontend" / "src" / "pages"
RELATIONSHIP_ANALYSIS = REPO_ROOT / "ia_relationship_analysis.json"

def run_git(cmd: List[str], check=True) -> str:
    """Run git command and return output"""
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
        print(f"Git command failed: {' '.join(cmd)}")
        print(f"Error: {e.stderr}")
        return ""

def get_all_branches() -> List[str]:
    """Get all local branches"""
    output = run_git(["branch", "--list"])
    branches = [b.strip().replace("*", "").strip() for b in output.split("\n") if b.strip()]
    return [b for b in branches if b and not b.startswith("(")]

def load_navigation_from_branch(branch: str) -> Optional[Dict]:
    """Load navigation JSON from a specific branch"""
    current_branch = run_git(["rev-parse", "--abbrev-ref", "HEAD"])
    
    try:
        run_git(["checkout", branch], check=False)
        
        nav_file = REPO_ROOT / "frontend" / "public" / "gui_nav.latest.json"
        if nav_file.exists():
            with open(nav_file, 'r') as f:
                return json.load(f)
        return None
    except Exception as e:
        print(f"Error loading navigation from {branch}: {e}")
        return None
    finally:
        run_git(["checkout", current_branch], check=False)

def count_content(nav_data: Dict) -> Dict[str, int]:
    """Count platforms, categories, and features in navigation data"""
    stats = {
        "platforms": 0,
        "categories": 0,
        "features": 0,
        "platform_category_pairs": 0,
        "category_feature_pairs": 0
    }
    
    for edition, platforms in nav_data.items():
        if not isinstance(platforms, dict):
            continue
        
        platform_set = set()
        category_set = set()
        feature_set = set()
        
        for platform_title, categories in platforms.items():
            if not isinstance(categories, dict):
                continue
            
            platform_set.add(platform_title)
            
            for category_title, features in categories.items():
                if not isinstance(features, list):
                    continue
                
                category_set.add(category_title)
                stats["platform_category_pairs"] += 1
                
                for feature in features:
                    if not isinstance(feature, dict):
                        continue
                    
                    feature_title = feature.get('title', '')
                    if feature_title:
                        feature_set.add(feature_title)
                        stats["category_feature_pairs"] += 1
        
        stats["platforms"] = max(stats["platforms"], len(platform_set))
        stats["categories"] = max(stats["categories"], len(category_set))
        stats["features"] = max(stats["features"], len(feature_set))
    
    return stats

def merge_navigation_data(base: Dict, incoming: Dict) -> Dict:
    """
    Merge navigation data preserving many-to-many relationships
    Strategy: Union merge - keep all platforms, categories, and features
    """
    merged = {}
    
    # Process each edition
    for edition in set(list(base.keys()) + list(incoming.keys())):
        if edition not in merged:
            merged[edition] = {}
        
        base_platforms = base.get(edition, {})
        incoming_platforms = incoming.get(edition, {})
        
        # Union of all platforms
        all_platforms = set(list(base_platforms.keys()) + list(incoming_platforms.keys()))
        
        for platform_title in all_platforms:
            if platform_title not in merged[edition]:
                merged[edition][platform_title] = {}
            
            base_categories = base_platforms.get(platform_title, {})
            incoming_categories = incoming_platforms.get(platform_title, {})
            
            # Union of all categories for this platform
            all_categories = set(list(base_categories.keys()) + list(incoming_categories.keys()))
            
            for category_title in all_categories:
                if category_title not in merged[edition][platform_title]:
                    merged[edition][platform_title][category_title] = []
                
                base_features = base_categories.get(category_title, [])
                incoming_features = incoming_categories.get(category_title, [])
                
                # Merge features, deduplicating by path
                feature_paths = {}
                
                # Add base features
                for feature in base_features:
                    if isinstance(feature, dict):
                        path = feature.get('path', '')
                        if path and path not in feature_paths:
                            feature_paths[path] = feature
                        elif not path:
                            # No path, use title as key
                            title = feature.get('title', '')
                            if title and title not in feature_paths:
                                feature_paths[title] = feature
                
                # Add incoming features (incoming takes precedence for conflicts)
                for feature in incoming_features:
                    if isinstance(feature, dict):
                        path = feature.get('path', '')
                        if path:
                            feature_paths[path] = feature  # Overwrite if exists
                        else:
                            title = feature.get('title', '')
                            if title:
                                feature_paths[title] = feature
                
                # Convert back to list
                merged[edition][platform_title][category_title] = list(feature_paths.values())
    
    return merged

def resolve_duplicate_paths(nav_data: Dict, relationship_analysis: Dict) -> Tuple[Dict, Dict]:
    """
    Resolve duplicate paths by ensuring each path is unique within its context
    Returns: (resolved_nav_data, path_mapping)
    """
    resolved = {}
    path_mapping = {}  # old_path -> new_path
    
    # Load relationship analysis to understand duplicates
    duplicate_paths = relationship_analysis.get('feature_paths', {})
    
    for edition, platforms in nav_data.items():
        if edition not in resolved:
            resolved[edition] = {}
        
        for platform_title, categories in platforms.items():
            if platform_title not in resolved[edition]:
                resolved[edition][platform_title] = {}
            
            for category_title, features in categories.items():
                if category_title not in resolved[edition][platform_title]:
                    resolved[edition][platform_title][category_title] = []
                
                for feature in features:
                    if not isinstance(feature, dict):
                        continue
                    
                    original_path = feature.get('path', '')
                    
                    # Check if this path is duplicated
                    if original_path in duplicate_paths:
                        contexts = duplicate_paths[original_path]
                        if len(contexts) > 1:
                            # Path is duplicated - make it unique by adding platform/category context
                            # Find the context that matches current platform/category
                            matching_context = None
                            for ctx_platform, ctx_category in contexts:
                                if ctx_platform == platform_title and ctx_category == category_title:
                                    matching_context = (ctx_platform, ctx_category)
                                    break
                            
                            if matching_context:
                                # Create unique path: /{platform}/{category}/{feature}
                                platform_slug = platform_title.lower().replace(' ', '-').replace('&', 'and')
                                category_slug = category_title.lower().replace(' ', '-').replace('&', 'and')
                                
                                # Extract feature name from path
                                path_parts = original_path.strip('/').split('/')
                                feature_name = path_parts[-1] if path_parts else 'feature'
                                
                                # Create new unique path
                                new_path = f"/{platform_slug}/{category_slug}/{feature_name}"
                                
                                # Only remap if it's actually different
                                if new_path != original_path:
                                    path_mapping[original_path] = new_path
                                    feature = feature.copy()
                                    feature['path'] = new_path
                                    feature['original_path'] = original_path  # Keep original for reference
                    else:
                        # Path is not duplicated, but ensure it follows the pattern
                        # Normalize path to include platform/category if missing
                        if original_path and not original_path.startswith(f'/{platform_title.lower()}'):
                            # Path doesn't include platform context - add it
                            platform_slug = platform_title.lower().replace(' ', '-').replace('&', 'and')
                            category_slug = category_title.lower().replace(' ', '-').replace('&', 'and')
                            
                            path_parts = original_path.strip('/').split('/')
                            feature_name = path_parts[-1] if path_parts else 'feature'
                            
                            new_path = f"/{platform_slug}/{category_slug}/{feature_name}"
                            if new_path != original_path:
                                path_mapping[original_path] = new_path
                                feature = feature.copy()
                                feature['path'] = new_path
                    
                    resolved[edition][platform_title][category_title].append(feature)
    
    return resolved, path_mapping

def analyze_branches_for_merge() -> List[Tuple[str, Dict, Dict]]:
    """Analyze all branches and return ranked list with navigation data"""
    branches = get_all_branches()
    branch_data = []
    
    # Skip protected branches
    skip_branches = {"main", "develop", "dying", "incremeents"}
    
    for branch in branches:
        if branch in skip_branches:
            continue
        
        print(f"Analyzing branch: {branch}")
        nav_data = load_navigation_from_branch(branch)
        
        if nav_data:
            stats = count_content(nav_data)
            score = (
                stats["platforms"] * 10 +
                stats["categories"] * 5 +
                stats["features"] * 2 +
                stats["platform_category_pairs"] * 3 +
                stats["category_feature_pairs"] * 1
            )
            
            branch_data.append((branch, nav_data, stats))
            print(f"  Score: {score}, Platforms: {stats['platforms']}, Categories: {stats['categories']}, Features: {stats['features']}")
    
    # Sort by score descending
    branch_data.sort(key=lambda x: (
        x[2]["platforms"] * 10 +
        x[2]["categories"] * 5 +
        x[2]["features"] * 2
    ), reverse=True)
    
    return branch_data

def main():
    print("=" * 80)
    print("STRATEGIC MERGE WITH MANY-TO-MANY RELATIONSHIP HANDLING")
    print("=" * 80)
    
    # Ensure we're on incremeents
    current = run_git(["rev-parse", "--abbrev-ref", "HEAD"])
    if current != "incremeents":
        print(f"Switching to incremeents branch (currently on {current})")
        run_git(["checkout", "incremeents"], check=False)
    
    # Load relationship analysis
    relationship_analysis = {}
    if RELATIONSHIP_ANALYSIS.exists():
        with open(RELATIONSHIP_ANALYSIS, 'r') as f:
            relationship_analysis = json.load(f)
    
    # Analyze branches
    print("\nAnalyzing branches for merge...")
    branch_data = analyze_branches_for_merge()
    
    if not branch_data:
        print("No branches with navigation data found!")
        return
    
    # Start with current branch's navigation
    print("\nLoading base navigation from incremeents...")
    base_nav = load_navigation_from_branch("incremeents")
    if not base_nav:
        print("No navigation data in incremeents branch, starting fresh...")
        base_nav = {}
    
    # Merge top branches
    print("\nMerging branches (top 10)...")
    merged_nav = base_nav
    
    for i, (branch, nav_data, stats) in enumerate(branch_data[:10], 1):
        print(f"\n{i}. Merging {branch}...")
        print(f"   Platforms: {stats['platforms']}, Categories: {stats['categories']}, Features: {stats['features']}")
        merged_nav = merge_navigation_data(merged_nav, nav_data)
    
    # Resolve duplicate paths
    print("\nResolving duplicate paths...")
    resolved_nav, path_mapping = resolve_duplicate_paths(merged_nav, relationship_analysis)
    
    # Save merged navigation
    output_file = REPO_ROOT / "frontend" / "public" / "gui_nav.merged.json"
    with open(output_file, 'w') as f:
        json.dump(resolved_nav, f, indent=2)
    
    print(f"\nMerged navigation saved to: {output_file}")
    
    # Save path mapping
    mapping_file = REPO_ROOT / "path_mapping.json"
    with open(mapping_file, 'w') as f:
        json.dump(path_mapping, f, indent=2)
    
    print(f"Path mapping saved to: {mapping_file}")
    
    # Statistics
    final_stats = count_content(resolved_nav)
    print("\n" + "=" * 80)
    print("MERGE STATISTICS")
    print("=" * 80)
    print(f"Final Platforms: {final_stats['platforms']}")
    print(f"Final Categories: {final_stats['categories']}")
    print(f"Final Features: {final_stats['features']}")
    print(f"Platform-Category Pairs: {final_stats['platform_category_pairs']}")
    print(f"Category-Feature Pairs: {final_stats['category_feature_pairs']}")
    print(f"Paths Remapped: {len(path_mapping)}")
    
    # Create summary
    summary = {
        "merged_branches": [branch for branch, _, _ in branch_data[:10]],
        "final_stats": final_stats,
        "paths_remapped": len(path_mapping),
        "path_mapping_file": str(mapping_file),
        "merged_nav_file": str(output_file)
    }
    
    summary_file = REPO_ROOT / "merge_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\nSummary saved to: {summary_file}")
    print("\nNext steps:")
    print("1. Review gui_nav.merged.json")
    print("2. Review path_mapping.json for path changes")
    print("3. If approved, copy gui_nav.merged.json to gui_nav.latest.json")
    print("4. Update route files to use new paths")

if __name__ == "__main__":
    main()



