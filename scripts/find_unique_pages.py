#!/usr/bin/env python3
"""Find unique pages in branches that aren't in incremeents."""

import subprocess
import json

def run_git(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip()

def get_pages_in_branch(branch):
    """Get set of page files in a branch."""
    cmd = f"git ls-tree -r --name-only {branch} frontend/src/pages/ 2>/dev/null | grep -E '\\.tsx?$'"
    output = run_git(cmd)
    return set(f for f in output.split('\n') if f.strip())

def main():
    current_pages = get_pages_in_branch("incremeents")
    print(f"Current branch (incremeents) has {len(current_pages)} pages")
    
    branches_to_check = [
        "integration/restore-pages-ia-ktg",
        "fix/restore-gui-glory",
        "integration/codex-ia-restore-final",
        "integration/ia-navigation-final",
        "integration/merge-gui-commits-20251221",
    ]
    
    all_unique = set()
    for branch in branches_to_check:
        branch_pages = get_pages_in_branch(branch)
        unique = branch_pages - current_pages
        if unique:
            print(f"\n{branch}: {len(unique)} unique pages")
            for page in sorted(unique)[:10]:
                print(f"  - {page}")
            if len(unique) > 10:
                print(f"  ... and {len(unique) - 10} more")
            all_unique.update(unique)
    
    print(f"\nTotal unique pages across all branches: {len(all_unique)}")
    
    if all_unique:
        with open("unique_pages_to_merge.json", "w") as f:
            json.dump(sorted(all_unique), f, indent=2)
        print("Saved to unique_pages_to_merge.json")

if __name__ == "__main__":
    main()



