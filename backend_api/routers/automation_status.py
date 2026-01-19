"""Automation status aggregation router.

Summarizes recent workspace automation activity (auto-fix + workspace shell logs)
for UI consumption. This is intentionally lightweight and file-based so it works
in dev environments without extra services.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import uuid

from fastapi import APIRouter, Request

router = APIRouter(prefix="/automation", tags=["automation"])


def _summarize_log_dir(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {"exists": False, "files": 0, "latest": None, "errors": []}
    files = sorted(path.glob("*.log"))
    latest = files[-1].name if files else None
    return {
        "exists": True,
        "files": len(files),
        "latest": latest,
    }


def _load_jsonl(path: Path, limit: int = 50) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    rows: List[Dict[str, Any]] = []
    try:
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
                if len(rows) >= limit:
                    break
    except Exception:
        return rows
    return rows


@router.get("/status")
async def get_status(request: Request) -> Dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[2]
    logs_dir = repo_root / "logs"
    workspace_shell = _summarize_log_dir(logs_dir / "workspace_shell")
    auto_fix = _summarize_log_dir(logs_dir / "auto_fix")
    # Optional structured event stream if present
    event_log = _load_jsonl(logs_dir / "automation_status.jsonl")
    correlation_id = request.headers.get("x-correlation-id") or str(uuid.uuid4())

    data = {
        "workspace_shell": workspace_shell,
        "auto_fix": auto_fix,
        "events": event_log,
    }
    return {
        "status": "ok",
        "request_id": correlation_id,
        "correlation_id": correlation_id,
        "data": data,
    }
