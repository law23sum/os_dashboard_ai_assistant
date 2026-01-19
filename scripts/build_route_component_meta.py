#!/usr/bin/env python3
"""Generate route component metadata (template usage) for UI wrappers."""
from __future__ import annotations

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ROUTE_MAP_PATH = REPO_ROOT / "frontend" / "src" / "navigation" / "routeComponentMap.ts"
OUTPUT_PATH = REPO_ROOT / "frontend" / "src" / "navigation" / "routeComponentMeta.ts"


def extract_json_block(text: str, start_token: str) -> str | None:
    start_index = text.find(start_token)
    if start_index == -1:
        return None
    assign_index = text.find("=", start_index)
    if assign_index == -1:
        return None
    open_index = text.find("{", assign_index)
    if open_index == -1:
        return None
    depth = 0
    for i in range(open_index, len(text)):
        ch = text[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[open_index : i + 1]
    return None


def load_route_map() -> dict:
    text = ROUTE_MAP_PATH.read_text()
    block = extract_json_block(text, "export const routeComponentMap")
    if not block:
        return {}
    block = re.sub(r",\s*([}\]])", r"\1", block)
    return json.loads(block)


def main() -> None:
    route_map = load_route_map()
    uses_template = {}
    for route, component_path in route_map.items():
        if not isinstance(component_path, str):
            continue
        component_file = REPO_ROOT / component_path
        if not component_file.exists():
            uses_template[route] = False
            continue
        content = component_file.read_text(errors="ignore")
        uses_template[route] = "FeaturePageTemplate" in content
    output_lines = [
        "export const routeUsesFeatureTemplate: Record<string, boolean> = {",
    ]
    for route in sorted(uses_template):
        output_lines.append(
            f"  {json.dumps(route)}: {str(uses_template[route]).lower()},"
        )
    output_lines.append("}")
    OUTPUT_PATH.write_text("\n".join(output_lines) + "\n")
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
