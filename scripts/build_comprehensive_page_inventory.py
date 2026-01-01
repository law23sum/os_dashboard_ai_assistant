#!/usr/bin/env python3
"""
Comprehensive Page Inventory Builder
Finds ALL page files across commits - searches deeply in all subdirectories
"""

import subprocess
import json
import re
from pathlib import Path
from collections import defaultdict

# Source commits
SOURCE_COMMITS = {
    '4acea80190121b8ab79d8cd1367166bcfead8bde': 'backup-broken-gui',
    '58cfc345630f68bf10909538aba48c12f87ce9df': 'origin-incremeents',
    '3a154a6e6305fe9f3a760f44b1b10d73e1ed3256': 'stable-alpha'
}

def run_git(cmd):
    """Run git command"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True,
                          cwd='/Users/chrisdixon/Projects/os_dashboard_ai_assistant')
    return result.stdout.strip()

def get_all_tsx_files_from_commit(commit_sha):
    """Get ALL tsx/jsx files from a commit"""
    cmd = f"git ls-tree -r --name-only {commit_sha} | grep -E '\\.(tsx|jsx)$' | grep -v node_modules | grep -v test | grep -v '.d.ts' | grep -v 'vite'"
    output = run_git(cmd)
    return [line for line in output.split('\n') if line and 'pages' in line.lower()]

def count_current_pages():
    """Count pages in current working tree"""
    cmd = "find frontend/src/pages -type f -name '*.tsx' -o -name '*.jsx' 2>/dev/null"
    output = run_git(cmd)
    return len([l for l in output.split('\n') if l])

def main():
    print("=" * 80)
    print("COMPREHENSIVE PAGE INVENTORY")
    print("=" * 80)
    
    print(f"\n📂 Current working tree:")
    current_count = count_current_pages()
    print(f"   Pages in frontend/src/pages: {current_count}")
    
    all_pages = set()
    commit_pages = defaultdict(set)
    
    for commit_sha, label in SOURCE_COMMITS.items():
        print(f"\n📦 Scanning {label} ({commit_sha[:7]})")
        pages = get_all_tsx_files_from_commit(commit_sha)
        print(f"   Found {len(pages)} page files")
        
        for page in pages:
            all_pages.add(page)
            commit_pages[page].add(label)
    
    print(f"\n📊 SUMMARY")
    print("=" * 80)
    print(f"Total unique page files across all commits: {len(all_pages)}")
    print(f"Current working tree pages: {current_count}")
    print(f"Missing pages: {len(all_pages) - current_count}")
    
    # Group by directory
    by_dir = defaultdict(list)
    for page in sorted(all_pages):
        dir_name = '/'.join(page.split('/')[:-1])
        by_dir[dir_name].append(page)
    
    print(f"\n📁 PAGES BY DIRECTORY")
    print("=" * 80)
    for dir_name in sorted(by_dir.keys()):
        if 'pages' in dir_name:
            print(f"{dir_name}: {len(by_dir[dir_name])} files")
    
    # Save detailed inventory
    inventory = {}
    for page in sorted(all_pages):
        inventory[page] = {
            'path': page,
            'foundIn': list(commit_pages[page])
        }
    
    output_file = '/Users/chrisdixon/Projects/os_dashboard_ai_assistant/comprehensive_page_inventory.json'
    with open(output_file, 'w') as f:
        json.dump(inventory, f, indent=2)
    
    print(f"\n✅ Detailed inventory saved to: comprehensive_page_inventory.json")
    print(f"   Total pages catalogued: {len(inventory)}")

if __name__ == '__main__':
    main()

