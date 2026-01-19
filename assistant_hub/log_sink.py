"""Structured log sink helpers."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict

DEFAULT_LOG_DIR = Path(os.getenv("OSDASH_LOG_DIR", "~/.osdash/logs")).expanduser()
DEFAULT_LOG_DIR.mkdir(parents=True, exist_ok=True)


def append_jsonl(filename: str, payload: Dict[str, Any]) -> None:
    """Append a JSON object to a log file safely."""
    path = DEFAULT_LOG_DIR / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False))
        f.write("\n")
