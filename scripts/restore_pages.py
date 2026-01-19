#!/usr/bin/env python3
"""
Restore working pages from prior commits.
Finds pages that have API implementations and replaces template pages.
"""

import subprocess
from pathlib import Path
import re

PROJECT_ROOT = Path(__file__).parent.parent
FRONTEND_PAGES = PROJECT_ROOT / "frontend" / "src" / "pages"

# Commits with working implementations (ordered by preference)
COMMITS = [
    "020c499e",  # stable and working (cursor branch)
    "9b4faf55",  # production release version 1.0.0.0
    "b3dfb4bc",  # stable
    "3a154a6e",  # latest stable alpha
    "1fcbc8a4",  # Restore all deleted pages
    "e9e7071a",  # stable
]

# API implementation indicators
API_INDICATORS = [
    "useQuery",
    "useMutation",
    "apiClient",
    "apiPath",
    "fetch(",
    "@tanstack/react-query",
    ".get(",
    ".post(",
    ".put(",
    ".delete(",
]

# Template indicators (pages to replace)
TEMPLATE_INDICATORS = [
    "FeaturePageTemplate",
    "CategoryHomeTemplate",
    "PlatformLandingTemplate",
    "RouteScaffold",
    "This workspace provides comprehensive tools",
    "Welcome to .* This workspace",
    "EnvironmentSection",
]

def run_git(cmd):
    """Run a git command and return output."""
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=PROJECT_ROOT)
    return result.stdout.strip() if result.returncode == 0 else None

def get_file_at_commit(commit, path):
    """Get file content at a specific commit."""
    return run_git(["git", "show", f"{commit}:{path}"])

def count_api_indicators(content):
    """Count API implementation indicators."""
    if not content:
        return 0
    return sum(content.count(ind) for ind in API_INDICATORS)

def has_api_implementation(content):
    """Check if content has real API implementation."""
    return count_api_indicators(content) >= 3

def is_template_page(content):
    """Check if content is a template/scaffold page."""
    if not content:
        return True
    for template in TEMPLATE_INDICATORS:
        if re.search(template, content):
            return True
    return False

def get_working_pages_from_commit(commit):
    """Get all working pages from a commit."""
    output = run_git(["git", "ls-tree", "-r", "--name-only", f"{commit}:frontend/src/pages/"])
    if not output:
        return {}

    working_pages = {}
    for filename in output.split('\n'):
        if not filename.endswith('.tsx'):
            continue
        path = f"frontend/src/pages/{filename}"
        content = get_file_at_commit(commit, path)
        if content and has_api_implementation(content) and not is_template_page(content):
            # Store by normalized name for matching
            name = Path(filename).stem.lower()
            working_pages[name] = {
                "commit": commit,
                "path": path,
                "content": content,
                "score": count_api_indicators(content),
                "original_name": filename,
            }
    return working_pages

def get_current_template_pages():
    """Find all current pages that use templates."""
    template_pages = []
    for tsx_file in FRONTEND_PAGES.rglob("*.tsx"):
        if "__tests__" in str(tsx_file):
            continue
        try:
            content = tsx_file.read_text()
            if is_template_page(content):
                rel_path = tsx_file.relative_to(PROJECT_ROOT)
                name = tsx_file.stem.lower()
                template_pages.append({
                    "path": str(rel_path),
                    "name": name,
                    "full_path": tsx_file,
                })
        except Exception:
            pass
    return template_pages

def normalize_name(name):
    """Normalize page name for matching."""
    # Remove common suffixes/prefixes
    name = name.lower()
    name = re.sub(r'(home|index|page|view|panel|screen)$', '', name)
    name = re.sub(r'^(page|view|)', '', name)
    # Remove special characters
    name = re.sub(r'[^a-z0-9]', '', name)
    return name

def main():
    print("=" * 70)
    print("  Page Restoration Tool - Multi-Commit Search")
    print("=" * 70)

    # Step 1: Get working pages from all commits
    print("\n[1/4] Gathering working pages from git history...")
    all_working_pages = {}

    for commit in COMMITS:
        print(f"  Scanning {commit}...")
        pages = get_working_pages_from_commit(commit)
        for name, info in pages.items():
            # Keep the best version (highest API score)
            if name not in all_working_pages or info["score"] > all_working_pages[name]["score"]:
                all_working_pages[name] = info

    print(f"  Found {len(all_working_pages)} working pages with API implementations")

    # Also add normalized names for better matching
    normalized_working = {}
    for name, info in all_working_pages.items():
        norm = normalize_name(name)
        if norm not in normalized_working or info["score"] > normalized_working[norm]["score"]:
            normalized_working[norm] = info

    # Step 2: Find current template pages
    print("\n[2/4] Finding template pages in current codebase...")
    template_pages = get_current_template_pages()
    print(f"  Found {len(template_pages)} template-based pages")

    # Step 3: Match and prepare restoration
    print("\n[3/4] Matching template pages with working implementations...")
    to_restore = []

    for template in template_pages:
        name = template["name"]
        norm_name = normalize_name(name)

        # Try exact match first
        if name in all_working_pages:
            working = all_working_pages[name]
            to_restore.append({
                "target": template["full_path"],
                "source_commit": working["commit"],
                "source_path": working["path"],
                "content": working["content"],
                "score": working["score"],
                "match_type": "exact",
            })
        # Try normalized match
        elif norm_name in normalized_working:
            working = normalized_working[norm_name]
            to_restore.append({
                "target": template["full_path"],
                "source_commit": working["commit"],
                "source_path": working["path"],
                "content": working["content"],
                "score": working["score"],
                "match_type": "normalized",
            })

    print(f"  Found {len(to_restore)} matching implementations to restore")

    if not to_restore:
        print("\nNo matching implementations found.")
        # List available working pages for reference
        print("\nAvailable working pages from git history:")
        for name in sorted(all_working_pages.keys())[:30]:
            info = all_working_pages[name]
            print(f"  - {name} (score: {info['score']}, commit: {info['commit'][:8]})")
        return

    # Show matches
    print(f"\n=== Pages to Restore ===")
    for item in to_restore[:40]:
        print(f"  {item['target'].name} <- {item['source_commit'][:8]}:{Path(item['source_path']).name} ({item['match_type']}, score: {item['score']})")
    if len(to_restore) > 40:
        print(f"  ... and {len(to_restore) - 40} more")

    # Step 4: Restore pages
    print(f"\n[4/4] Restoring {len(to_restore)} pages...")
    restored = 0
    errors = []

    for item in to_restore:
        try:
            target = item["target"]
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(item["content"])
            restored += 1
            print(f"  ✓ {target.relative_to(PROJECT_ROOT)}")
        except Exception as e:
            errors.append((str(item["target"]), str(e)))
            print(f"  ✗ {item['target']} - {e}")

    print(f"\n=== Restoration Complete ===")
    print(f"Restored: {restored}")
    print(f"Errors: {len(errors)}")

    # List unmatched template pages
    unmatched = len(template_pages) - len(to_restore)
    if unmatched > 0:
        print(f"\nNote: {unmatched} template pages had no matching implementations in git history.")
        print("These may be new pages that were never fully implemented.")

if __name__ == "__main__":
    main()
