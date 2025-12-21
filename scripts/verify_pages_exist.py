#!/usr/bin/env python3
"""
Verify key pages exist and are accessible.
"""

import sys
from pathlib import Path
from typing import List, Tuple

REPO_ROOT = Path(__file__).parent.parent
FRONTEND_SRC = REPO_ROOT / "frontend" / "src"
PAGES_DIR = FRONTEND_SRC / "pages"

def count_pages() -> int:
    """Count total .tsx pages."""
    if not PAGES_DIR.exists():
        return 0
    
    count = 0
    for path in PAGES_DIR.rglob("*.tsx"):
        if path.is_file():
            count += 1
    
    return count

def check_key_pages() -> Tuple[bool, List[str]]:
    """Check that key pages exist."""
    missing = []
    
    key_pages = [
        "Dashboard.tsx",
        "Ai.tsx",
        "Workspaces.tsx",
        "Drivers.tsx",
        "Data.tsx",
        "Governance.tsx",
        "Mission.tsx",
        "Observability.tsx",
        "Settings.tsx",
    ]
    
    for page in key_pages:
        page_path = PAGES_DIR / page
        if not page_path.exists():
            missing.append(page)
    
    print(f"✓ Total pages: {count_pages()}")
    print(f"✓ Key pages checked: {len(key_pages)}")
    
    if missing:
        print(f"\n✗ Missing key pages: {len(missing)}")
        for page in missing:
            print(f"  - {page}")
    else:
        print(f"\n✓ All key pages exist")
    
    return len(missing) == 0, missing

def main():
    print("=" * 80)
    print("Page Existence Verification")
    print("=" * 80)
    print()
    
    all_exist, missing = check_key_pages()
    
    print()
    print("=" * 80)
    if all_exist:
        print("✅ Pages Exist: PASSED")
    else:
        print("❌ Pages Exist: FAILED")
        print(f"   Missing {len(missing)} key pages")
    print("=" * 80)
    
    sys.exit(0 if all_exist else 1)

if __name__ == '__main__':
    main()



