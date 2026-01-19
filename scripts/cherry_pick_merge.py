#!/usr/bin/env python3
"""
Cherry-pick and merge functional code from multiple commits into one integrated SaaS website.
Extracts the best version of each page with API/DB connections.
"""

import subprocess
import re
from pathlib import Path
from collections import defaultdict
import json

PROJECT_ROOT = Path(__file__).parent.parent
FRONTEND_PAGES = PROJECT_ROOT / "frontend" / "src" / "pages"

# Commits with functional code (ordered by quality - best first)
FUNCTIONAL_COMMITS = [
    ("9b4faf55", "production release version 1.0.0.0"),
    ("3a154a6e", "latest stable alpha version"),
    ("020c499e", "stable and working"),
    ("e9e7071a", "stable"),
    ("b3dfb4bc", "stable"),
]

# API/DB implementation indicators with weights
QUALITY_INDICATORS = {
    "useQuery": 5, "useMutation": 5, "apiClient": 4, "apiPath": 4,
    "@tanstack/react-query": 3, "queryClient": 3,
    ".get(": 3, ".post(": 3, ".put(": 3, ".delete(": 3, ".patch(": 2,
    "useState": 2, "useEffect": 2, "useMemo": 2,
    "toast": 2, "refetch": 2, "isLoading": 2,
    "onSubmit": 2, "handleSubmit": 2,
}

# Template indicators (pages to replace)
TEMPLATE_PATTERNS = [
    r"FeaturePageTemplate", r"CategoryHomeTemplate", r"PlatformLandingTemplate",
    r"RouteScaffold", r"This workspace provides comprehensive tools",
    r"Welcome to .* This workspace", r"EnvironmentSection",
]

def run_git(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=PROJECT_ROOT)
    return result.stdout.strip() if result.returncode == 0 else None

def get_file_at_commit(commit, path):
    return run_git(["git", "show", f"{commit}:{path}"])

def calculate_quality_score(content):
    if not content:
        return 0
    score = sum(content.count(ind) * weight for ind, weight in QUALITY_INDICATORS.items())
    score += min(len(content) // 1000, 20)
    return score

def is_template_page(content):
    if not content:
        return True
    return any(re.search(pattern, content, re.IGNORECASE) for pattern in TEMPLATE_PATTERNS)

def has_real_implementation(content):
    if not content or is_template_page(content):
        return False
    return calculate_quality_score(content) >= 10

def normalize_name(filepath):
    """Extract just the filename without path, lowercased."""
    name = Path(filepath).stem.lower()
    # Remove common suffixes/prefixes
    name = re.sub(r'(page|view|index|home|screen|workspace)$', '', name)
    name = re.sub(r'^(page|view)', '', name)
    # Remove non-alphanumeric
    name = re.sub(r'[^a-z0-9]', '', name)
    return name

def get_all_pages_from_commit(commit):
    """Get all page files from a commit with their content."""
    output = run_git(["git", "ls-tree", "-r", "--name-only", f"{commit}"])
    if not output:
        return {}

    pages = {}
    for filepath in output.split('\n'):
        if not filepath.startswith("frontend/src/pages/"):
            continue
        if not filepath.endswith(".tsx"):
            continue
        if ".test." in filepath or "__tests__" in filepath:
            continue

        content = get_file_at_commit(commit, filepath)
        if content and has_real_implementation(content):
            norm_name = normalize_name(filepath)
            score = calculate_quality_score(content)

            # Store best version for each normalized name
            if norm_name not in pages or score > pages[norm_name]["score"]:
                pages[norm_name] = {
                    "path": filepath,
                    "filename": Path(filepath).name,
                    "content": content,
                    "score": score,
                    "commit": commit,
                }
    return pages

def main():
    print("=" * 80)
    print("  CHERRY-PICK & MERGE: Building Integrated SaaS Website")
    print("=" * 80)

    # Step 1: Collect all functional pages from all commits
    print("\n[1/6] Extracting functional pages from all commits...")
    best_pages = {}

    for commit, msg in FUNCTIONAL_COMMITS:
        print(f"  Scanning {commit[:8]}: {msg}")
        pages = get_all_pages_from_commit(commit)
        for name, info in pages.items():
            if name not in best_pages or info["score"] > best_pages[name]["score"]:
                best_pages[name] = info
        print(f"    Found {len(pages)} API-connected pages")

    print(f"\n  Total best implementations: {len(best_pages)}")

    # Step 2: Find ALL template pages in current codebase
    print("\n[2/6] Finding ALL template pages to replace...")
    template_pages = []
    for tsx_file in FRONTEND_PAGES.rglob("*.tsx"):
        if "__tests__" in str(tsx_file) or ".test." in str(tsx_file):
            continue
        try:
            content = tsx_file.read_text()
            if is_template_page(content):
                norm_name = normalize_name(str(tsx_file))
                template_pages.append({
                    "path": tsx_file,
                    "norm_name": norm_name,
                    "score": calculate_quality_score(content),
                })
        except Exception:
            pass

    print(f"  Found {len(template_pages)} template pages")

    # Step 3: Match and replace template pages
    print("\n[3/6] Replacing template pages with functional code...")
    replaced = 0
    for template in template_pages:
        norm_name = template["norm_name"]
        if norm_name in best_pages:
            best = best_pages[norm_name]
            try:
                template["path"].write_text(best["content"])
                replaced += 1
                print(f"  ✓ {template['path'].relative_to(FRONTEND_PAGES)} <- {best['filename']} (score: {template['score']} -> {best['score']})")
            except Exception as e:
                print(f"  ✗ {template['path'].name}: {e}")

    # Step 4: Also restore core pages that might have been overwritten
    print("\n[4/6] Restoring core functional pages...")
    core_pages_restored = 0
    for name, info in best_pages.items():
        # Find matching file in current codebase
        matching_files = list(FRONTEND_PAGES.rglob(f"*{info['filename']}"))
        if not matching_files:
            matching_files = list(FRONTEND_PAGES.rglob(f"*{name}*.tsx"))

        for target in matching_files:
            try:
                current_content = target.read_text()
                current_score = calculate_quality_score(current_content)
                if current_score < info["score"] and is_template_page(current_content):
                    target.write_text(info["content"])
                    core_pages_restored += 1
                    print(f"  ✓ {target.relative_to(FRONTEND_PAGES)} (score: {current_score} -> {info['score']})")
            except Exception:
                pass

    # Step 5: Copy missing high-value pages to root
    print("\n[5/6] Adding missing functional pages...")
    added = 0
    for name, info in best_pages.items():
        target = FRONTEND_PAGES / info["filename"]
        if not target.exists():
            try:
                target.write_text(info["content"])
                added += 1
                print(f"  + {info['filename']} (score: {info['score']})")
            except Exception as e:
                print(f"  ✗ {info['filename']}: {e}")

    # Step 6: Summary
    print("\n[6/6] Integration Complete")
    print("=" * 80)
    print(f"  Templates replaced: {replaced}")
    print(f"  Core pages restored: {core_pages_restored}")
    print(f"  New pages added: {added}")
    print(f"  Total API/DB pages available: {len(best_pages)}")
    print("=" * 80)

    # List all available functional pages
    print("\n  Available functional pages (by quality score):")
    for name, info in sorted(best_pages.items(), key=lambda x: x[1]["score"], reverse=True)[:25]:
        print(f"    {info['filename']:40} score: {info['score']:3} (from {info['commit'][:8]})")

    # Save report
    report = {
        "templates_replaced": replaced,
        "core_restored": core_pages_restored,
        "new_added": added,
        "pages": {name: {"filename": info["filename"], "score": info["score"], "commit": info["commit"]}
                  for name, info in best_pages.items()}
    }
    (PROJECT_ROOT / "cherry_pick_report.json").write_text(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
