"""Helpers for managing provider API keys."""

from __future__ import annotations

import os
import re
from typing import Dict, List, Optional

_rotation_index: Dict[str, int] = {}


def _split_list(value: str) -> List[str]:
    parts = re.split(r"[;,]", value)
    return [p.strip() for p in parts if p.strip()]


def collect_keys(base_name: str) -> List[str]:
    keys: List[str] = []

    def _add(value: Optional[str]) -> None:
        if not value:
            return
        if value in keys:
            return
        keys.append(value)

    _add(os.getenv(base_name))

    list_value = os.getenv(f"{base_name}S") or os.getenv(f"{base_name}_LIST")
    if list_value:
        for item in _split_list(list_value):
            _add(item)

    numbered: List[tuple[int, str]] = []
    pattern = re.compile(rf"^{re.escape(base_name)}(\d+)$")
    for name, value in os.environ.items():
        match = pattern.match(name)
        if not match:
            continue
        if not value:
            continue
        numbered.append((int(match.group(1)), value))
    for _, value in sorted(numbered, key=lambda pair: pair[0]):
        _add(value)

    return keys


def select_key(base_name: str, *, pool: Optional[str] = None) -> Optional[str]:
    keys = collect_keys(base_name)
    if not keys:
        return None
    pool_name = pool or base_name
    index = _rotation_index.get(pool_name, 0)
    key = keys[index % len(keys)]
    _rotation_index[pool_name] = (index + 1) % len(keys)
    return key
