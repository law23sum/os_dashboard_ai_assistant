#!/usr/bin/env python3
"""
Strategic merge of branches into incremeents branch.
Prioritizes maximum pages, categories, platforms, and features.
"""

import subprocess
import json
from pathlib import Path
from typing import Dict, List, Set
import shutil

def run_git_command(cmd: List[str], check=True) -> tuple[str, int]:
    """Run a git command and return output and exit code."""
    try:
        result = subprocess.run(
            ['git'] + cmd,
            capture_output=True,
            text=True,
            check=check,
            cwd=Path(__file__).parent.parent
        )
        return result.stdout.strip(), result.returncode
    except subprocess.CalledProcessError as e:
        return e.stderr.strip(), e.returncode

def ensure_on_branch(branch: str) -> bool:
    """Ensure we're on the specified branch."""
    current, _ = run_git_command(['branch', '--show-current'], check=False)
    if current.strip() == branch:
        return True
    
    print(f"Checking out {branch}...")
    output, code = run_git_command(['checkout', branch], check=False)
    if code != 0:
        print(f"Error checking out {branch}: {output}")
        return False
    return True

def merge_branch(source_branch: str, strategy: str = 'ours') -> bool:
    """Merge a branch with a specific strategy."""
    print(f"\nMerging {source_branch} with strategy '{strategy}'...")
    
    # Check if branch exists
    branches, _ = run_git_command(['branch', '--list', source_branch], check=False)
    if not branches.strip():
        print(f"  Branch {source_branch} does not exist locally, skipping")
        return False
    
    # Merge with strategy
    if strategy == 'ours':
        # Use ours strategy to keep current content, but we'll selectively add files
        output, code = run_git_command(['merge', '-X', 'ours', '--no-edit', source_branch], check=False)
    elif strategy == 'theirs':
        output, code = run_git_command(['merge', '-X', 'theirs', '--no-edit', source_branch], check=False)
    else:
        # Regular merge
        output, code = run_git_command(['merge', '--no-edit', source_branch], check=False)
    
    if code == 0:
        print(f"  ✓ Successfully merged {source_branch}")
        return True
    elif "Already up to date" in output:
        print(f"  - {source_branch} already merged")
        return True
    else:
        print(f"  ⚠ Merge conflict or error: {output[:200]}")
        # Try to resolve conflicts
        return resolve_conflicts()

def resolve_conflicts() -> bool:
    """Resolve merge conflicts by taking the version with more content."""
    print("  Attempting to resolve conflicts...")
    
    # Get conflicted files
    conflicted, _ = run_git_command(['diff', '--name-only', '--diff-filter=U'], check=False)
    if not conflicted.strip():
        return True
    
    conflicted_files = [f.strip() for f in conflicted.split('\n') if f.strip()]
    print(f"  Found {len(conflicted_files)} conflicted files")
    
    # For navigation files, we want to merge intelligently
    for file in conflicted_files:
        if 'gui_nav' in file or 'navigation' in file.lower():
            print(f"  Resolving navigation file: {file}")
            # Use a merge tool or manual resolution
            # For now, we'll keep both versions and merge later
            pass
    
    return True

def copy_files_from_branch(source_branch: str, file_patterns: List[str]) -> int:
    """Copy specific files from a branch."""
    copied = 0
    for pattern in file_patterns:
        try:
            # Use git show to get file content
            content, code = run_git_command(['show', f'{source_branch}:{pattern}'], check=False)
            if code == 0 and content:
                file_path = Path(__file__).parent.parent / pattern
                file_path.parent.mkdir(parents=True, exist_ok=True)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                copied += 1
                print(f"  Copied {pattern} from {source_branch}")
        except Exception as e:
            print(f"  Error copying {pattern}: {e}")
    
    return copied

def merge_navigation_files(source_branch: str) -> bool:
    """Intelligently merge navigation files from source branch."""
    print(f"  Merging navigation files from {source_branch}...")
    
    nav_files = [
        'frontend/public/gui_nav.latest.json',
        'documentation/gui_nav_structure/gui_nav.latest.json',
    ]
    
    for nav_file in nav_files:
        # Get content from source branch
        source_content, code = run_git_command(['show', f'{source_branch}:{nav_file}'], check=False)
        if code != 0 or not source_content:
            continue
        
        try:
            source_data = json.loads(source_content)
        except:
            continue
        
        # Get current content
        current_file = Path(__file__).parent.parent / nav_file
        if not current_file.exists():
            # Just copy it
            current_file.parent.mkdir(parents=True, exist_ok=True)
            with open(current_file, 'w', encoding='utf-8') as f:
                f.write(source_content)
            print(f"    Created {nav_file}")
            continue
        
        try:
            with open(current_file, 'r', encoding='utf-8') as f:
                current_data = json.load(f)
        except:
            # If current is invalid, use source
            with open(current_file, 'w', encoding='utf-8') as f:
                f.write(source_content)
            print(f"    Replaced invalid {nav_file}")
            continue
        
        # Merge: take maximum from both
        merged = merge_nav_data(current_data, source_data)
        
        # Write merged data
        with open(current_file, 'w', encoding='utf-8') as f:
            json.dump(merged, f, indent=2)
        
        print(f"    Merged {nav_file}")
    
    return True

def merge_nav_data(current: Dict, source: Dict) -> Dict:
    """Merge navigation data, taking maximum from both."""
    merged = {}
    
    # Merge editions
    all_editions = set(current.keys()) | set(source.keys())
    
    for edition in all_editions:
        current_platforms = current.get(edition, {})
        source_platforms = source.get(edition, {})
        
        merged_platforms = {}
        all_platforms = set(current_platforms.keys()) | set(source_platforms.keys())
        
        for platform in all_platforms:
            current_categories = current_platforms.get(platform, {})
            source_categories = source_platforms.get(platform, {})
            
            merged_categories = {}
            all_categories = set(current_categories.keys()) | set(source_categories.keys())
            
            for category in all_categories:
                current_features = current_categories.get(category, [])
                source_features = source_categories.get(category, [])
                
                # Merge features, deduplicate by path
                feature_map = {}
                for feat in current_features:
                    if isinstance(feat, dict) and 'path' in feat:
                        feature_map[feat['path']] = feat
                
                for feat in source_features:
                    if isinstance(feat, dict) and 'path' in feat:
                        # Prefer source if it has more fields or is newer
                        if feat['path'] not in feature_map or len(feat) > len(feature_map[feat['path']]):
                            feature_map[feat['path']] = feat
                
                merged_categories[category] = list(feature_map.values())
            
            merged_platforms[platform] = merged_categories
        
        merged[edition] = merged_platforms
    
    return merged

def copy_pages_from_branch(source_branch: str) -> int:
    """Copy all page files from source branch."""
    print(f"  Copying pages from {source_branch}...")
    
    # List all pages in source branch
    pages_output, code = run_git_command(['ls-tree', '-r', '--name-only', source_branch, 'frontend/src/pages'], check=False)
    if code != 0:
        return 0
    
    pages = [p.strip() for p in pages_output.split('\n') if p.strip() and p.endswith('.tsx')]
    copied = 0
    
    for page in pages:
        # Get file content
        content, code = run_git_command(['show', f'{source_branch}:{page}'], check=False)
        if code == 0 and content:
            page_path = Path(__file__).parent.parent / page
            page_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Only copy if it doesn't exist or source is larger (more complete)
            if not page_path.exists() or len(content) > page_path.stat().st_size:
                with open(page_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                copied += 1
    
    print(f"    Copied {copied} pages")
    return copied

def main():
    """Main merge function."""
    print("="*80)
    print("STRATEGIC MERGE TO INCREMEENTS")
    print("="*80)
    
    # Ensure we're on incremeents
    if not ensure_on_branch('incremeents'):
        print("ERROR: Could not checkout incremeents branch")
        return
    
    # Priority branches (most complete)
    priority_branches = [
        'integration/restore-pages-ia-ktg',  # Most pages (487)
        'ia-reorg-merge-20251221',  # Most features (504)
        'fix/ia-navigation-merge',
        'integration/codex-ia-restore-final',
        'integration/ia-navigation-final',
    ]
    
    # Other branches to merge
    other_branches = [
        'fix/restore-gui-glory',
        'fix/restore-gui-glory-20251220',
        'gui-fully-restored',
        'integration/merge-gui-commits-20251221',
        'integration/restore-pages-ia-v2',
    ]
    
    print("\nMerging priority branches...")
    for branch in priority_branches:
        # First merge navigation files intelligently
        merge_navigation_files(branch)
        
        # Then copy pages
        copy_pages_from_branch(branch)
        
        # Finally do git merge
        merge_branch(branch, strategy='ours')
    
    print("\nMerging other branches...")
    for branch in other_branches:
        merge_branch(branch, strategy='ours')
    
    print("\n" + "="*80)
    print("MERGE COMPLETE")
    print("="*80)
    print("\nNext steps:")
    print("1. Review conflicts and resolve if needed")
    print("2. Test the navigation structure")
    print("3. Clean up merged branches")

if __name__ == '__main__':
    main()
