#!/usr/bin/env python3
import json
import os
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional

ROOT = Path(__file__).resolve().parents[1]

ROUTE_COMPONENT_MAP_PATH = ROOT / 'frontend/src/navigation/routeComponentMap.ts'
APP_PATH = ROOT / 'frontend/src/App.tsx'
IA_MANIFEST_JSON = ROOT / 'frontend/src/data/iaManifest.from_json.json'
IA_MANIFEST_COMPLETE_JSON = ROOT / 'frontend/src/data/iaManifest.complete.json'
IA_CANONICAL_PATH = ROOT / 'frontend/src/data/iaCanonical.ts'

OUTPUT_UI = ROOT / 'agent_exports/ui'
OUTPUT_RECOVERY = ROOT / 'agent_exports/recovery'

TEMPLATE_PATHS = {
    'FeaturePageTemplate': 'frontend/src/components/templates/FeaturePageTemplate.tsx',
    'CategoryHomeTemplate': 'frontend/src/components/templates/CategoryHomeTemplate.tsx',
    'PlatformLandingTemplate': 'frontend/src/components/templates/PlatformLandingTemplate.tsx',
    'RouteScaffold': 'frontend/src/pages/RouteScaffold.tsx',
}

PARAMETERS_MARKERS = [
    'data-page-section="inputs"',
    'data-page-section="execute"',
    'data-page-section="results"',
    'Parameters',
    'Execute',
    'Results',
]


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding='utf-8')
    except FileNotFoundError:
        return ''


def parse_route_component_map(path: Path) -> Dict[str, str]:
    text = read_text(path)
    pairs = re.findall(r'^\s*"([^"]+)"\s*:\s*"([^"]+)"', text, re.M)
    return {route: component for route, component in pairs}


def build_import_map(app_text: str) -> Dict[str, str]:
    import_map: Dict[str, str] = {}
    for line in app_text.splitlines():
        line = line.strip()
        m = re.match(r"import\s+([A-Za-z0-9_]+)\s+from\s+['\"]([^'\"]+)['\"]", line)
        if m:
            name, rel_path = m.groups()
            import_map[name] = rel_path
    return import_map


def resolve_import_path(rel_path: str) -> Optional[str]:
    # Only resolve relative paths under frontend/src
    if not rel_path.startswith('.'):
        return None
    base = APP_PATH.parent
    candidate = (base / rel_path).resolve()
    if candidate.suffix:
        if candidate.exists():
            return str(candidate.relative_to(ROOT))
        return str(candidate.relative_to(ROOT))
    for ext in ('.tsx', '.ts', '.jsx', '.js'):
        path = candidate.with_suffix(ext)
        if path.exists():
            return str(path.relative_to(ROOT))
    # fallback to .tsx
    return str(candidate.with_suffix('.tsx').relative_to(ROOT))


def parse_app_routes(path: Path) -> Dict[str, str]:
    text = read_text(path)
    import_map = build_import_map(text)
    routes: Dict[str, str] = {}

    route_pattern = re.compile(r'<Route\s+[^>]*path="([^"]+)"[^>]*element=\{([\s\S]*?)\}\s*/?>')
    for match in route_pattern.finditer(text):
        route = match.group(1)
        element = match.group(2)
        component_candidates = re.findall(r'<([A-Z][A-Za-z0-9_]*)', element)
        component_path = None
        # prefer page imports
        for name in reversed(component_candidates):
            rel_path = import_map.get(name)
            if rel_path and '/pages/' in rel_path:
                component_path = resolve_import_path(rel_path)
                break
        if not component_path:
            for name in reversed(component_candidates):
                rel_path = import_map.get(name)
                if rel_path:
                    component_path = resolve_import_path(rel_path)
                    break
        if not component_path and component_candidates:
            component_path = component_candidates[-1]
        if component_path:
            routes[route] = component_path

    return routes


def load_ia_manifest(path: Path) -> dict:
    if not path.exists():
        return {"platforms": []}
    return json.loads(path.read_text(encoding='utf-8'))


def normalize_label(value: str) -> str:
    return re.sub(r'[^a-z0-9]+', '-', value.strip().lower()).strip('-')


def detect_placeholder_reason(component_path: str, component_text: str) -> Optional[str]:
    if component_path in TEMPLATE_PATHS.values():
        for name, path in TEMPLATE_PATHS.items():
            if path == component_path:
                return name
    if not component_text:
        return 'other'

    if 'FeaturePageTemplate' in component_text:
        return 'FeaturePageTemplate'
    if 'CategoryHomeTemplate' in component_text:
        return 'CategoryHomeTemplate'
    if 'PlatformLandingTemplate' in component_text:
        return 'PlatformLandingTemplate'
    if 'RouteScaffold' in component_text or 'RouteScaffold' in component_path:
        return 'RouteScaffold'

    lines = component_text.splitlines()
    small_file = len(lines) <= 150
    has_layout_markers = any(
        marker in component_text
        for marker in (
            '<section',
            '<div',
            '<PageHeader',
            'data-page-section=',
            '<FeaturePageTemplate',
            '<CategoryHomeTemplate',
            '<PlatformLandingTemplate',
        )
    )
    if small_file and not has_layout_markers:
        if re.search(r'return\s+null', component_text):
            return 'empty return'
        if re.search(r'return\s+<></>', component_text):
            return 'empty return'
        if re.search(r'return\s+<div\s*/>', component_text):
            return 'empty return'

    if re.search(r'export\s+\{\s*default\s*\}\s*from\s*[\\"\'][^\\\"\\\']*RouteScaffold', component_text):
        return 'RouteScaffold'
    return None


def detect_has_parameters_frame(component_text: str) -> bool:
    if not component_text:
        return False
    if 'FeaturePageTemplate' in component_text:
        return True
    if 'FeaturePageFrame' in component_text:
        return True
    if 'LegacyHomePage' in component_text:
        return True
    hits = [marker for marker in PARAMETERS_MARKERS if marker in component_text]
    return len(hits) >= 3


def read_component_text(component_path: str, cache: Dict[str, str]) -> str:
    if component_path in cache:
        return cache[component_path]
    path = ROOT / component_path
    text = read_text(path) if path.exists() else ''
    cache[component_path] = text
    return text


def build_redirects_from_manifest(manifest: dict) -> List[dict]:
    redirects: List[dict] = []
    platforms = manifest.get('platforms', [])
    if platforms:
        first_platform = platforms[0]
        first_category = (first_platform.get('categories') or [None])[0]
        if first_platform and first_category:
            redirects.append({"from": "/", "to": f"/{first_platform['id']}/{first_category['id']}", "source": "iaCanonical"})
            redirects.append({"from": "/dashboard", "to": f"/{first_platform['id']}/{first_category['id']}", "source": "iaCanonical"})

    for platform in platforms:
        platform_id = platform.get('id')
        for category in platform.get('categories', []):
            category_id = category.get('id')
            legacy_home = category.get('homeRoute')
            canonical_home = f"/{platform_id}/{category_id}"
            if legacy_home:
                redirects.append({"from": legacy_home, "to": canonical_home, "source": "iaCanonical"})
            for feature in category.get('features', []):
                legacy_route = feature.get('route')
                canonical_route = f"/{platform_id}/{category_id}/{feature.get('id')}"
                if legacy_route:
                    redirects.append({"from": legacy_route, "to": canonical_route, "source": "iaCanonical"})
    return redirects


def guess_context(route: str, manifest: dict) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    platform_guess = None
    category_guess = None
    feature_guess = None
    for platform in manifest.get('platforms', []):
        if platform.get('path') == route:
            platform_guess = platform.get('label')
        for category in platform.get('categories', []):
            if category.get('homeRoute') == route:
                platform_guess = platform.get('label')
                category_guess = category.get('label')
            for feature in category.get('features', []):
                if feature.get('route') == route:
                    platform_guess = platform.get('label')
                    category_guess = category.get('label')
                    feature_guess = feature.get('label')
    return platform_guess, category_guess, feature_guess


def collect_page_sections(component_text: str) -> List[str]:
    if not component_text:
        return []
    matches = re.findall(r'data-page-section=\"([^\"]+)\"', component_text)
    return sorted(set(matches))


def main() -> int:
    OUTPUT_UI.mkdir(parents=True, exist_ok=True)
    OUTPUT_RECOVERY.mkdir(parents=True, exist_ok=True)

    route_component_map = parse_route_component_map(ROUTE_COMPONENT_MAP_PATH)
    app_routes = parse_app_routes(APP_PATH)

    manifest = load_ia_manifest(IA_MANIFEST_JSON)
    complete_manifest = load_ia_manifest(IA_MANIFEST_COMPLETE_JSON)

    # Build route entries
    routes: Dict[str, str] = dict(route_component_map)
    for route, component in app_routes.items():
        routes.setdefault(route, component)

    component_cache: Dict[str, str] = {}

    redirect_entries = build_redirects_from_manifest(manifest)

    route_entries = []
    for route, component_path in sorted(routes.items(), key=lambda item: item[0]):
        component_text = read_component_text(component_path, component_cache)
        placeholder_reason = detect_placeholder_reason(component_path, component_text)
        is_placeholder = bool(placeholder_reason)
        has_frame = detect_has_parameters_frame(component_text)
        platform_guess, category_guess, feature_guess = guess_context(route, manifest)
        route_entries.append({
            "route": route,
            "kind": "ui",
            "page_component_path": component_path,
            "is_redirect": False,
            "redirect_target": None,
            "is_placeholder_page": is_placeholder,
            "placeholder_reason": placeholder_reason,
            "has_parameters_execute_results_frame": has_frame,
            "platform_guess": platform_guess,
            "category_guess": category_guess,
            "feature_guess": feature_guess,
        })

    # Platform catalog
    platform_catalog = []
    for platform in manifest.get('platforms', []):
        platform_catalog.append({
            "platform_id": platform.get('id'),
            "platform_label": platform.get('label'),
            "platform_path": platform.get('path'),
            "where_defined": str(IA_MANIFEST_JSON.relative_to(ROOT)),
            "tab_order": platform.get('order'),
        })

    # Category catalog
    category_catalog = []
    for platform in manifest.get('platforms', []):
        for category in platform.get('categories', []):
            category_catalog.append({
                "platform_id": platform.get('id'),
                "platform_label": platform.get('label'),
                "category_id": category.get('id'),
                "category_label": category.get('label'),
                "homeRoute": category.get('homeRoute'),
                "component": category.get('homeComponentPath'),
                "where_defined": str(IA_MANIFEST_JSON.relative_to(ROOT)),
                "dropdown_order": category.get('order'),
            })

    # Feature catalog
    feature_catalog = []
    for platform in manifest.get('platforms', []):
        for category in platform.get('categories', []):
            for feature in category.get('features', []):
                component_path = feature.get('componentPath')
                component_text = read_component_text(component_path, component_cache)
                placeholder_reason = detect_placeholder_reason(component_path, component_text)
                shared_key = normalize_label(feature.get('label', ''))
                feature_catalog.append({
                    "platform_id": platform.get('id'),
                    "platform_label": platform.get('label'),
                    "category_id": category.get('id'),
                    "category_label": category.get('label'),
                    "feature_id": feature.get('id'),
                    "feature_label": feature.get('label'),
                    "route": feature.get('route'),
                    "component_path": component_path,
                    "shared_feature_key": shared_key,
                    "placeholder_reason": placeholder_reason,
                    "widgets_displays": collect_page_sections(component_text),
                })

    # Page catalog
    feature_routes = {f['route'] for f in feature_catalog}
    category_routes = {c['homeRoute'] for c in category_catalog}
    platform_routes = {p.get('platform_path') for p in platform_catalog if p.get('platform_path')}

    page_catalog = {
        "feature_pages": [],
        "category_home_pages": [],
        "platform_landing_pages": [],
        "other_pages": [],
    }

    route_index = {entry['route']: entry for entry in route_entries}

    for feature in feature_catalog:
        entry = route_index.get(feature['route'])
        if not entry:
            continue
        page_catalog['feature_pages'].append({
            "route": feature['route'],
            "component_path": feature['component_path'],
            "renderer": feature['component_path'],
            "is_placeholder_page": entry['is_placeholder_page'],
            "placeholder_reason": entry['placeholder_reason'],
            "has_parameters_execute_results_frame": entry['has_parameters_execute_results_frame'],
        })

    for category in category_catalog:
        entry = route_index.get(category['homeRoute'])
        if not entry:
            continue
        page_catalog['category_home_pages'].append({
            "route": category['homeRoute'],
            "component_path": category['component'],
            "renderer": category['component'],
            "is_placeholder_page": entry['is_placeholder_page'],
            "placeholder_reason": entry['placeholder_reason'],
            "has_parameters_execute_results_frame": entry['has_parameters_execute_results_frame'],
        })

    for platform in platform_catalog:
        route = platform.get('platform_path')
        if not route:
            continue
        entry = route_index.get(route)
        if not entry:
            continue
        page_catalog['platform_landing_pages'].append({
            "route": route,
            "component_path": entry['page_component_path'],
            "renderer": entry['page_component_path'],
            "is_placeholder_page": entry['is_placeholder_page'],
            "placeholder_reason": entry['placeholder_reason'],
            "has_parameters_execute_results_frame": entry['has_parameters_execute_results_frame'],
        })

    for route, entry in route_index.items():
        if route in feature_routes or route in category_routes or route in platform_routes:
            continue
        page_catalog['other_pages'].append({
            "route": route,
            "component_path": entry['page_component_path'],
            "renderer": entry['page_component_path'],
            "is_placeholder_page": entry['is_placeholder_page'],
            "placeholder_reason": entry['placeholder_reason'],
            "has_parameters_execute_results_frame": entry['has_parameters_execute_results_frame'],
        })

    # Duplicate detection
    duplicates = {
        "by_component_path": [],
        "by_label": [],
    }
    component_groups: Dict[str, List[dict]] = {}
    for feature in feature_catalog:
        component_groups.setdefault(feature['component_path'], []).append(feature)
    for component_path, features in component_groups.items():
        if len(features) < 2:
            continue
        routes = [f['route'] for f in features]
        labels = [f['feature_label'] for f in features]
        duplicates['by_component_path'].append({
            "component_path": component_path,
            "occurrences": len(features),
            "routes": routes,
            "labels": labels,
            "recommended_shared_feature_key": normalize_label(labels[0] if labels else component_path),
            "recommended_canonical_route": sorted(routes)[0] if routes else None,
        })

    label_groups: Dict[str, List[dict]] = {}
    for feature in feature_catalog:
        norm = normalize_label(feature['feature_label'] or '')
        if not norm:
            continue
        label_groups.setdefault(norm, []).append(feature)
    for norm, features in label_groups.items():
        if len(features) < 2:
            continue
        routes = [f['route'] for f in features]
        component_paths = [f['component_path'] for f in features]
        duplicates['by_label'].append({
            "label_key": norm,
            "occurrences": len(features),
            "routes": routes,
            "component_paths": component_paths,
            "recommended_shared_feature_key": norm,
            "recommended_canonical_route": sorted(routes)[0] if routes else None,
        })

    # Empty pages list
    empty_pages = [
        entry for entry in route_entries
        if entry['is_placeholder_page']
    ]

    # Recovery missing page set
    missing_page_set = []
    for entry in empty_pages:
        missing_page_set.append({
            "route": entry['route'],
            "current_component": entry['page_component_path'],
            "placeholder_reason": entry['placeholder_reason'],
            "platform_context": entry['platform_guess'],
            "category_context": entry['category_guess'],
            "feature_context": entry['feature_guess'],
        })

    # Write outputs
    repo_info = {
        "branch": os.environ.get('GIT_BRANCH', 'unknown'),
        "commit": os.environ.get('GIT_COMMIT', 'unknown'),
    }

    (OUTPUT_UI / 'ROUTE_MAP.json').write_text(
        json.dumps({"repo": repo_info, "routes": route_entries}, indent=2),
        encoding='utf-8'
    )
    (OUTPUT_UI / 'PAGE_CATALOG.json').write_text(
        json.dumps(page_catalog, indent=2),
        encoding='utf-8'
    )
    (OUTPUT_UI / 'PLATFORM_CATALOG.json').write_text(
        json.dumps(platform_catalog, indent=2),
        encoding='utf-8'
    )
    (OUTPUT_UI / 'CATEGORY_CATALOG.json').write_text(
        json.dumps(category_catalog, indent=2),
        encoding='utf-8'
    )
    (OUTPUT_UI / 'FEATURE_CATALOG.json').write_text(
        json.dumps(feature_catalog, indent=2),
        encoding='utf-8'
    )
    (OUTPUT_UI / 'DUPLICATES.json').write_text(
        json.dumps(duplicates, indent=2),
        encoding='utf-8'
    )
    (OUTPUT_UI / 'REDIRECTS.json').write_text(
        json.dumps(redirect_entries, indent=2),
        encoding='utf-8'
    )

    empty_md_lines = [
        '# Empty/Template Pages',
        '',
    ]
    for entry in empty_pages:
        empty_md_lines.append(
            f"- {entry['route']} | {entry['placeholder_reason']} | {entry['page_component_path']}"
        )
    (OUTPUT_UI / 'EMPTY_PAGES.md').write_text('\n'.join(empty_md_lines) + '\n', encoding='utf-8')

    (OUTPUT_RECOVERY / 'MISSING_PAGE_SET.json').write_text(
        json.dumps(missing_page_set, indent=2),
        encoding='utf-8'
    )

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
