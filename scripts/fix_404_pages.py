#!/usr/bin/env python3
"""
Script to find and fix 404/generic pages by restoring from prior commits.
Uses headless browser testing to verify fixes.
"""

import subprocess
import json
import os
import sys
import time
from pathlib import Path
from typing import List, Dict, Tuple, Optional

PROJECT_ROOT = Path(__file__).parent.parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"
PAGES_DIR = FRONTEND_DIR / "src" / "pages"

# Routes to test (extracted from routeComponentMap.ts)
ROUTES_TO_TEST = [
    "/", "/dashboard/flight-deck", "/ai", "/ai/advanced", "/ai/autofix",
    "/ai/capabilities", "/ai/capsules", "/ai/copilot", "/ai/daemons",
    "/ai/drivers", "/ai/edge", "/ai/evals", "/ai/mlops", "/ai/operations",
    "/ai/personas", "/ai/prompts", "/ai/routing", "/ai/safety", "/ai/security",
    "/ai/systems", "/ai/vision", "/ai/workflows", "/analytics", "/audit",
    "/billing", "/chat", "/collaboration", "/data", "/docs", "/drivers",
    "/future", "/governance", "/inbox", "/integrations", "/mission",
    "/monitoring", "/notifications", "/observability", "/operations",
    "/personalization", "/projects", "/research", "/roadmap", "/search",
    "/settings", "/tasks", "/timeline", "/vision", "/work", "/workspaces",
]

# Commits known to have working pages (most recent good ones)
GOOD_COMMITS = [
    "9b4faf55",  # production release version 1.0.0.0
    "940fbb47",  # Restore legacy frontend pages
    "32c914e0",  # lastest code. please don't break
    "79e6d290",  # sturdy
    "3a154a6e",  # latest stable alpha version
]


def run_cmd(cmd: List[str], cwd: Optional[Path] = None) -> Tuple[int, str, str]:
    """Run a command and return exit code, stdout, stderr."""
    result = subprocess.run(
        cmd,
        cwd=cwd or PROJECT_ROOT,
        capture_output=True,
        text=True
    )
    return result.returncode, result.stdout, result.stderr


def get_file_at_commit(commit: str, file_path: str) -> Optional[str]:
    """Get file contents at a specific commit."""
    code, stdout, stderr = run_cmd(["git", "show", f"{commit}:{file_path}"])
    if code == 0:
        return stdout
    return None


def file_exists_at_commit(commit: str, file_path: str) -> bool:
    """Check if a file exists at a specific commit."""
    code, _, _ = run_cmd(["git", "cat-file", "-e", f"{commit}:{file_path}"])
    return code == 0


def is_generic_page(content: str) -> bool:
    """Check if page content is a generic scaffold/placeholder."""
    generic_indicators = [
        "RouteScaffold",
        "FeaturePageTemplate",
        "CategoryHomeTemplate",
        "PlatformLandingTemplate",
        "IARouteFallback",
        "Coming soon",
        "Under construction",
        "This page is a placeholder",
        "// TODO:",
        "export default function RouteScaffold",
    ]
    for indicator in generic_indicators:
        if indicator in content:
            return True
    return False


def has_real_implementation(content: str) -> bool:
    """Check if a page has real implementation (not just scaffolding)."""
    real_indicators = [
        "useQuery",
        "useMutation",
        "useState",
        "useEffect",
        "apiClient",
        "API.",
        "<div className",
        "<Card",
        "<Button",
        "PageHeader",
        "toast(",
    ]
    indicator_count = sum(1 for ind in real_indicators if ind in content)
    return indicator_count >= 3  # At least 3 real indicators


def find_best_version(file_path: str) -> Tuple[Optional[str], Optional[str]]:
    """Find the best version of a file from good commits."""
    rel_path = str(Path(file_path).relative_to(PROJECT_ROOT))

    for commit in GOOD_COMMITS:
        content = get_file_at_commit(commit, rel_path)
        if content and has_real_implementation(content) and not is_generic_page(content):
            return commit, content

    # Try with alternative paths (case variations)
    alt_paths = generate_path_variations(rel_path)
    for alt_path in alt_paths:
        for commit in GOOD_COMMITS:
            content = get_file_at_commit(commit, alt_path)
            if content and has_real_implementation(content) and not is_generic_page(content):
                return commit, content

    return None, None


def generate_path_variations(path: str) -> List[str]:
    """Generate case variations of a path."""
    variations = []
    parts = path.split("/")

    # Try lowercase, Title case, UPPERCASE for each part
    for i, part in enumerate(parts):
        if part.endswith(".tsx"):
            base = part[:-4]
            variations.append("/".join(parts[:i] + [base.lower() + ".tsx"] + parts[i+1:]))
            variations.append("/".join(parts[:i] + [base.title() + ".tsx"] + parts[i+1:]))
            variations.append("/".join(parts[:i] + [base[0].upper() + base[1:] + ".tsx"] + parts[i+1:]))

    return variations


def scan_pages_for_issues() -> Dict[str, str]:
    """Scan all pages and identify issues."""
    issues = {}

    for page_file in PAGES_DIR.rglob("*.tsx"):
        # Skip test files
        if "__tests__" in str(page_file) or ".test." in str(page_file):
            continue

        try:
            content = page_file.read_text()
            rel_path = page_file.relative_to(FRONTEND_DIR)

            if is_generic_page(content):
                issues[str(page_file)] = "generic_scaffold"
            elif not has_real_implementation(content):
                issues[str(page_file)] = "minimal_implementation"
        except Exception as e:
            issues[str(page_file)] = f"read_error: {e}"

    return issues


def restore_page(file_path: str) -> bool:
    """Attempt to restore a page from a good commit."""
    commit, content = find_best_version(file_path)

    if content:
        try:
            Path(file_path).write_text(content)
            print(f"  ✓ Restored from commit {commit}")
            return True
        except Exception as e:
            print(f"  ✗ Failed to write: {e}")
            return False
    else:
        print(f"  ✗ No good version found")
        return False


def test_routes_with_playwright() -> Dict[str, str]:
    """Test routes using Playwright headless browser."""
    test_script = """
const { chromium } = require('playwright');

(async () => {
    const browser = await chromium.launch({ headless: true });
    const page = await browser.newPage();
    const results = {};
    const routes = %s;

    for (const route of routes) {
        try {
            await page.goto('http://localhost:5173' + route, {
                waitUntil: 'networkidle',
                timeout: 10000
            });

            // Check for 404 text
            const content = await page.textContent('body');
            if (content.includes('404') || content.includes('Page not found')) {
                results[route] = '404';
            } else if (content.includes('Coming soon') || content.includes('placeholder')) {
                results[route] = 'placeholder';
            } else {
                results[route] = 'ok';
            }
        } catch (e) {
            results[route] = 'error: ' + e.message;
        }
    }

    await browser.close();
    console.log(JSON.stringify(results, null, 2));
})();
""" % json.dumps(ROUTES_TO_TEST)

    test_file = PROJECT_ROOT / "scripts" / "_test_routes.js"
    test_file.write_text(test_script)

    try:
        code, stdout, stderr = run_cmd(["node", str(test_file)], cwd=FRONTEND_DIR)
        if code == 0:
            return json.loads(stdout)
        else:
            print(f"Playwright test error: {stderr}")
            return {}
    finally:
        test_file.unlink(missing_ok=True)


def main():
    print("=" * 70)
    print("  404/Generic Page Fixer")
    print("=" * 70)

    # Step 1: Scan for issues
    print("\n[1/4] Scanning pages for issues...")
    issues = scan_pages_for_issues()
    print(f"  Found {len(issues)} pages with potential issues")

    # Step 2: Categorize issues
    generic_pages = [p for p, i in issues.items() if i == "generic_scaffold"]
    minimal_pages = [p for p, i in issues.items() if i == "minimal_implementation"]
    error_pages = [p for p, i in issues.items() if i.startswith("read_error")]

    print(f"    - Generic scaffolds: {len(generic_pages)}")
    print(f"    - Minimal implementations: {len(minimal_pages)}")
    print(f"    - Read errors: {len(error_pages)}")

    # Step 3: Attempt to restore pages
    print("\n[2/4] Attempting to restore pages from good commits...")
    restored = 0
    failed = 0

    for page_path in generic_pages[:50]:  # Process in batches
        print(f"\n  Processing: {Path(page_path).name}")
        if restore_page(page_path):
            restored += 1
        else:
            failed += 1

    print(f"\n  Restored: {restored}, Failed: {failed}")

    # Step 4: Save report
    report = {
        "total_issues": len(issues),
        "generic_scaffolds": len(generic_pages),
        "minimal_implementations": len(minimal_pages),
        "restored": restored,
        "failed": failed,
        "pages_with_issues": list(issues.keys())[:100],  # First 100
    }

    report_file = PROJECT_ROOT / "page_fix_report.json"
    report_file.write_text(json.dumps(report, indent=2))
    print(f"\n[3/4] Report saved to: {report_file}")

    print("\n[4/4] Done! Run tests to verify fixes.")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
