#!/usr/bin/env python3
"""
Technical Spec Coverage Checker
Analyzes implemented features against Technical Spec v6 requirements.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Set

# Major spec sections that should have implementations
SPEC_SECTIONS = {
    "§3.3": "Projects & Workspaces",
    "§3.4": "Task Model",
    "§3.7": "Project Ledger",
    "§4.5": "Project Intelligence",
    "§4.6": "TRF - Theoretical Reasoning Framework",
    "§6.3": "Data Storage",
    "§7.2": "Master Stack Engine",
    "§7.3": "Dev Workspace",
    "§7.4": "Research Workspace",
    "§7.5": "Writer Workspace",
    "§7.7": "Cybersecurity Workspace",
    "§8": "Capsule System",
    "§11": "Observability",
    "§13": "Deployment Models",
    "§17.2": "Core Capabilities",
}

REQUIRED_BACKEND_ENDPOINTS = [
    "/api/projects",
    "/api/tasks",
    "/api/data/backup",
    "/api/data/restore",
    "/api/data/stats",
    "/api/projects/{id}/intelligence",
    "/api/projects/{id}/trf",
    "/api/projects/{id}/insights",
    "/api/projects/{id}/ledger",
]

REQUIRED_FRONTEND_PAGES = [
    "/projects",
    "/tasks",
    "/dashboard",
    "/settings",
    "/ai-copilot",
    "/research",
    "/writer",
    "/security",
]


def scan_backend_routes(backend_dir: Path) -> Dict[str, List[str]]:
    """Scan backend routers for implemented endpoints."""
    routers = {}
    routers_dir = backend_dir / "routers"
    
    if not routers_dir.exists():
        return routers
    
    for router_file in routers_dir.glob("*.py"):
        if router_file.name == "__init__.py":
            continue
            
        content = router_file.read_text()
        endpoints = []
        
        # Find all @router decorators
        for match in re.finditer(r'@router\.(get|post|put|delete|patch)\(["\']([^"\']+)', content):
            method, path = match.groups()
            endpoints.append(f"{method.upper()} {path}")
        
        if endpoints:
            routers[router_file.stem] = endpoints
    
    return routers


def scan_frontend_pages(frontend_dir: Path) -> List[str]:
    """Scan frontend for implemented pages."""
    pages = []
    pages_dir = frontend_dir / "src" / "pages"
    
    if not pages_dir.exists():
        return pages
    
    for page_file in pages_dir.glob("*.tsx"):
        page_name = page_file.stem
        # Convert PascalCase to kebab-case
        route = re.sub(r'(?<!^)(?=[A-Z])', '-', page_name).lower()
        pages.append(f"/{route}")
    
    return pages


def scan_spec_references(project_root: Path) -> Dict[str, List[str]]:
    """Scan codebase for spec section references."""
    references = {}
    
    # Scan backend
    for py_file in project_root.glob("backend_api/**/*.py"):
        content = py_file.read_text()
        for section in SPEC_SECTIONS.keys():
            if section in content:
                references.setdefault(section, []).append(str(py_file.relative_to(project_root)))
    
    # Scan frontend
    for ts_file in project_root.glob("frontend/src/**/*.{ts,tsx}"):
        try:
            content = ts_file.read_text()
            for section in SPEC_SECTIONS.keys():
                if section in content:
                    references.setdefault(section, []).append(str(ts_file.relative_to(project_root)))
        except Exception:
            pass
    
    return references


def generate_report(project_root: Path):
    """Generate coverage report."""
    print("=" * 80)
    print("OS Dashboard - Technical Spec v6 Coverage Report")
    print("=" * 80)
    print()
    
    # Backend analysis
    print("📡 Backend API Endpoints")
    print("-" * 80)
    backend_routes = scan_backend_routes(project_root / "backend_api")
    
    total_endpoints = 0
    for router_name, endpoints in sorted(backend_routes.items()):
        print(f"\n{router_name}.py ({len(endpoints)} endpoints):")
        for endpoint in sorted(endpoints)[:5]:  # Show first 5
            print(f"  ✅ {endpoint}")
            total_endpoints += 1
        if len(endpoints) > 5:
            print(f"  ... and {len(endpoints) - 5} more")
    
    print(f"\n📊 Total Endpoints: {total_endpoints}")
    print()
    
    # Frontend analysis
    print("🎨 Frontend Pages")
    print("-" * 80)
    frontend_pages = scan_frontend_pages(project_root / "frontend")
    for page in sorted(frontend_pages)[:20]:  # Show first 20
        print(f"  ✅ {page}")
    
    if len(frontend_pages) > 20:
        print(f"  ... and {len(frontend_pages) - 20} more")
    
    print(f"\n📊 Total Pages: {len(frontend_pages)}")
    print()
    
    # Spec coverage
    print("📖 Technical Spec Section Coverage")
    print("-" * 80)
    spec_refs = scan_spec_references(project_root)
    
    implemented = set(spec_refs.keys())
    not_implemented = set(SPEC_SECTIONS.keys()) - implemented
    
    for section in sorted(implemented):
        print(f"  ✅ {section}: {SPEC_SECTIONS[section]} ({len(spec_refs[section])} references)")
    
    if not_implemented:
        print("\n  ⚠️  Sections with no explicit references:")
        for section in sorted(not_implemented):
            print(f"     ❌ {section}: {SPEC_SECTIONS[section]}")
    
    print()
    coverage_pct = (len(implemented) / len(SPEC_SECTIONS)) * 100
    print(f"📊 Spec Coverage: {coverage_pct:.1f}% ({len(implemented)}/{len(SPEC_SECTIONS)} sections)")
    print()
    
    # Required endpoints check
    print("🔍 Required Endpoints Check")
    print("-" * 80)
    all_endpoints_str = str(backend_routes)
    
    for required in REQUIRED_BACKEND_ENDPOINTS:
        # Simplify check
        endpoint_path = required.split("{")[0].rstrip("/")
        if endpoint_path in all_endpoints_str or required in all_endpoints_str:
            print(f"  ✅ {required}")
        else:
            print(f"  ❌ {required} (MISSING)")
    
    print()
    
    # Summary
    print("=" * 80)
    print("Summary")
    print("=" * 80)
    print(f"✅ Backend Routers: {len(backend_routes)}")
    print(f"✅ API Endpoints: {total_endpoints}")
    print(f"✅ Frontend Pages: {len(frontend_pages)}")
    print(f"✅ Spec Coverage: {coverage_pct:.1f}%")
    print()
    print("Status: " + ("🎉 EXCELLENT" if coverage_pct >= 80 else "✅ GOOD" if coverage_pct >= 60 else "⚠️  NEEDS WORK"))
    print("=" * 80)


if __name__ == "__main__":
    project_root = Path(__file__).parent.parent
    generate_report(project_root)
