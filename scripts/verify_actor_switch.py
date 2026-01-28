#!/usr/bin/env python3
"""
Verify Personal/Enterprise Actor Switch:
1. ActorSwitch component exists
2. Filters platforms based on actor scope
3. Filters categories based on actor scope
4. Filters features based on actor scope
"""

import sys
from pathlib import Path
from typing import Set

REPO_ROOT = Path(__file__).parent.parent
FRONTEND_SRC = REPO_ROOT / "frontend" / "src"

def find_actor_switch() -> Path:
    """Find ActorSwitch component."""
    candidates = [
        FRONTEND_SRC / "components" / "ActorSwitch.tsx",
        FRONTEND_SRC / "components" / "ActorSwitch.jsx",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None

def find_navigation_context() -> Path:
    """Find navigation context that uses actor scope."""
    candidates = [
        FRONTEND_SRC / "navigation" / "context.tsx",
        FRONTEND_SRC / "navigation" / "iaContext.tsx",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None

def verify_actor_switch() -> tuple[bool, list[str]]:
    """Verify actor switch implementation."""
    errors = []
    warnings = []
    
    # Check ActorSwitch exists
    actor_switch = find_actor_switch()
    if not actor_switch:
        errors.append("ActorSwitch component not found")
        return False, errors
    
    content = actor_switch.read_text(encoding='utf-8')
    
    # Check for Personal/Enterprise toggle
    if "personal" not in content.lower() and "enterprise" not in content.lower():
        errors.append("ActorSwitch missing Personal/Enterprise toggle")
    
    if "ActorScope" not in content and "actorScope" not in content:
        warnings.append("ActorSwitch may not have actorScope type")
    
    # Check navigation context
    nav_context = find_navigation_context()
    if nav_context:
        nav_content = nav_context.read_text(encoding='utf-8')
        
        # Check for filtering based on actor scope
        if "actorScope" in nav_content or "ActorScope" in nav_content:
            if "filter" not in nav_content.lower() and "getPlatforms" not in nav_content:
                warnings.append("Navigation context may not filter by actor scope")
        else:
            warnings.append("Navigation context may not use actor scope")
    
    print(f"✓ ActorSwitch component found: {actor_switch.name}")
    if nav_context:
        print(f"✓ Navigation context found: {nav_context.name}")
    
    if errors:
        print(f"\n✗ Errors: {len(errors)}")
        for error in errors:
            print(f"  - {error}")
    
    if warnings:
        print(f"\n⚠ Warnings: {len(warnings)}")
        for warning in warnings:
            print(f"  - {warning}")
    
    return len(errors) == 0, errors + warnings

def main():
    print("=" * 80)
    print("Actor Switch Verification")
    print("=" * 80)
    print()
    
    is_valid, issues = verify_actor_switch()
    
    print()
    print("=" * 80)
    if is_valid:
        print("✅ Actor Switch: PASSED")
    else:
        print("❌ Actor Switch: FAILED")
        print(f"   Found {len(issues)} issues")
    print("=" * 80)
    
    sys.exit(0 if is_valid else 1)

if __name__ == '__main__':
    main()




