#!/usr/bin/env python3
"""
Analyze missing page components from git history and classify them into:
- covered: route already exists in current route map
- redirect: old route should redirect to existing route
- restore: route missing, should be added under Legacy Recovery

Writes plan artifacts into docs/integration/.
"""
from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
PAGES_ROOT = REPO_ROOT / "frontend" / "src" / "pages"
ROUTE_MAP_PATH = REPO_ROOT / "frontend" / "src" / "navigation" / "routeComponentMap.ts"
RENAME_MAP_PATH = REPO_ROOT / "history_missing_pages_renamed.json"
OUTPUT_DIR = REPO_ROOT / "docs" / "integration"
PLAN_PATH = OUTPUT_DIR / "legacy_recovery_plan.json"
SUMMARY_PATH = OUTPUT_DIR / "legacy_recovery_summary.md"

ROUTE_RE = re.compile(r"Route:\s*([^\s*]+)")


@dataclass
class CommitInfo:
    sha: str
    date: str
    subject: str


def run_git(args: List[str]) -> str:
    return subprocess.check_output(["git", *args], cwd=REPO_ROOT, text=True).strip()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def slugify(value: str) -> str:
    value = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", value)
    value = value.replace("_", "-")
    value = re.sub(r"[^A-Za-z0-9-]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value.lower() or "item"


def titleize(value: str) -> str:
    value = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", value)
    value = value.replace("_", " ").replace("-", " ")
    return " ".join(part.capitalize() for part in value.split()) or "Untitled"


def list_history_page_paths() -> List[str]:
    output = run_git([
        "log",
        "--all",
        "--name-only",
        "--pretty=format:",
        "--",
        "frontend/src/pages",
    ])
    paths = set()
    for line in output.splitlines():
        line = line.strip()
        if not line:
            continue
        if not line.endswith(".tsx"):
            continue
        if "**[new]**" in line:
            continue
        if "/__tests__/" in line:
            continue
        paths.add(line)
    return sorted(paths)


def list_current_page_paths() -> List[str]:
    return sorted(
        str(path.relative_to(REPO_ROOT))
        for path in PAGES_ROOT.rglob("*.tsx")
        if "__tests__" not in path.parts
    )


def load_route_component_map() -> Tuple[Dict[str, str], Dict[str, List[str]]]:
    route_map: Dict[str, str] = {}
    component_to_routes: Dict[str, List[str]] = {}
    if not ROUTE_MAP_PATH.exists():
        return route_map, component_to_routes
    for line in read_text(ROUTE_MAP_PATH).splitlines():
        match = re.match(r"\s*\"([^\"]+)\"\s*:\s*\"([^\"]+)\"", line)
        if not match:
            continue
        route, component = match.groups()
        route_map[route] = component
        component_to_routes.setdefault(component, []).append(route)
    return route_map, component_to_routes


def load_rename_map() -> Dict[str, List[str]]:
    if not RENAME_MAP_PATH.exists():
        return {}
    return json.loads(read_text(RENAME_MAP_PATH))


def build_last_commit_map() -> Dict[str, CommitInfo]:
    output = run_git([
        "log",
        "--all",
        "--diff-filter=AM",
        "--name-only",
        "--pretty=format:%H|%cs|%s",
        "--",
        "frontend/src/pages",
    ])
    commit_map: Dict[str, CommitInfo] = {}
    current_commit: Optional[CommitInfo] = None

    for line in output.splitlines():
        line = line.strip()
        if not line:
            continue
        if "|" in line and re.match(r"^[0-9a-f]{7,}\\|", line):
            parts = line.split("|", 2)
            if len(parts) == 3:
                current_commit = CommitInfo(*parts)
            else:
                current_commit = None
            continue
        if not current_commit:
            continue
        if not line.endswith(".tsx"):
            continue
        if "/__tests__/" in line:
            continue
        if line not in commit_map:
            commit_map[line] = current_commit
    return commit_map


def batch_show_files(commit_map: Dict[str, CommitInfo], paths: List[str]) -> Dict[str, Optional[str]]:
    requests = [(commit_map[path].sha, path) for path in paths if path in commit_map]
    if not requests:
        return {}

    proc = subprocess.Popen(
        ["git", "cat-file", "--batch"],
        cwd=REPO_ROOT,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )
    assert proc.stdin is not None
    assert proc.stdout is not None

    for sha, path in requests:
        proc.stdin.write(f"{sha}:{path}\n".encode("utf-8"))
    proc.stdin.close()

    contents: Dict[str, Optional[str]] = {}
    for _, path in requests:
        header = proc.stdout.readline()
        if not header:
            contents[path] = None
            continue
        header_text = header.decode("utf-8", errors="replace").strip()
        if header_text.endswith("missing"):
            contents[path] = None
            continue
        parts = header_text.split()
        if len(parts) < 3:
            contents[path] = None
            continue
        try:
            size = int(parts[2])
        except ValueError:
            contents[path] = None
            continue
        body = proc.stdout.read(size)
        proc.stdout.read(1)
        contents[path] = body.decode("utf-8", errors="replace")

    proc.stdout.close()
    proc.wait()
    return contents


def extract_route(content: str) -> Optional[str]:
    match = ROUTE_RE.search(content)
    if match:
        return match.group(1).strip()
    return None


def choose_route(routes: List[str]) -> Optional[str]:
    if not routes:
        return None
    return sorted(routes, key=lambda value: (len(value), value))[0]


def derive_category(route: Optional[str], filename: str) -> str:
    if route:
        parts = route.strip("/").split("/")
        if parts:
            if parts[0] == "legacy" and len(parts) > 1:
                return titleize(parts[1])
            return titleize(parts[0])
    return titleize(filename)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    history_paths = set(list_history_page_paths())
    current_paths = set(list_current_page_paths())
    current_paths_lower = {path.lower(): path for path in current_paths}
    missing_paths = sorted(history_paths - current_paths)

    route_map, component_to_routes = load_route_component_map()
    rename_map = load_rename_map()
    commit_map = build_last_commit_map()
    file_contents = batch_show_files(commit_map, missing_paths)

    plan_records = []
    redirects: Dict[str, str] = {}
    restore_records = []
    covered_records = []

    for path in missing_paths:
        covered_by = current_paths_lower.get(path.lower())
        commit_used = commit_map.get(path)
        content = file_contents.get(path)
        route = extract_route(content) if content else None
        filename = Path(path).stem
        title = titleize(filename)

        action = "unknown"
        route_final = None
        redirect_to = None

        if covered_by:
            action = "covered"
        elif route and route in route_map:
            action = "covered"
        else:
            candidates = rename_map.get(path, [])
            mapped_route = None
            for candidate in candidates:
                candidate_path = REPO_ROOT / candidate
                if candidate_path.exists():
                    mapped_route = choose_route(component_to_routes.get(candidate, []))
                    if mapped_route:
                        break
            if mapped_route and route:
                action = "redirect"
                redirect_to = mapped_route
                redirects[route] = mapped_route
            else:
                action = "restore"
                if route and route not in route_map:
                    route_final = route
                else:
                    route_final = f"/legacy/{slugify(filename)}"

        category = derive_category(route_final or route, filename)

        record = {
            "path": path,
            "route": route,
            "route_final": route_final,
            "title": title,
            "category": category,
            "action": action,
            "redirect_to": redirect_to,
            "covered_by": covered_by or "",
            "commit": commit_used.sha if commit_used else "",
            "commit_date": commit_used.date if commit_used else "",
            "commit_subject": commit_used.subject if commit_used else "",
        }
        plan_records.append(record)

        if action == "covered":
            covered_records.append(record)
        elif action == "redirect":
            pass
        elif action == "restore":
            restore_records.append(record)

    plan = {
        "missing_total": len(missing_paths),
        "covered": len(covered_records),
        "redirect": len(redirects),
        "restore": len(restore_records),
        "redirects": redirects,
        "restore_records": restore_records,
        "records": plan_records,
    }

    PLAN_PATH.write_text(json.dumps(plan, indent=2), encoding="utf-8")

    summary_lines = [
        "# Legacy Recovery Summary",
        "",
        f"Missing pages: {len(missing_paths)}",
        f"Covered by existing routes: {len(covered_records)}",
        f"Redirects added: {len(redirects)}",
        f"Routes to restore: {len(restore_records)}",
        "",
        "## Next Steps",
        "- Apply redirects to path_mapping.json",
        "- Add Legacy Recovery platform to gui_nav.latest.json",
        "- Restore missing page components for restore routes",
    ]
    SUMMARY_PATH.write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    print(f"Wrote {PLAN_PATH}")
    print(f"Wrote {SUMMARY_PATH}")


if __name__ == "__main__":
    main()
