#!/usr/bin/env python3
"""Precompute dashboard metrics so shell startup stays fast."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable, Tuple

OPS_ROOT = Path.home() / "OS_Dashboard_AI_Assistant"
LOG_DIR = OPS_ROOT / "logs"
JSON_PATH = LOG_DIR / "dashboard_snapshot.json"
ENV_PATH = LOG_DIR / "dashboard_snapshot.env"

TARGETS = {
    "desktop": Path.home() / "Desktop",
    "downloads": Path.home() / "Downloads",
    "projects": Path.home() / "Projects",
    "ideaprojects": Path.home() / "IdeaProjects",
    "pycharmprojects": Path.home() / "PycharmProjects",
    "temporary": Path.home() / "Temporary",
}

DESKTOP_LANES = {
    "inbox": TARGETS["desktop"] / "01_Inbox",
    "active": TARGETS["desktop"] / "02_Active",
    "archive": TARGETS["desktop"] / "99_Archive",
}

DOWNLOAD_LANES = {
    "incoming": TARGETS["downloads"] / "_incoming",
    "archive": TARGETS["downloads"] / "_archive",
}


def dir_count(path: Path) -> int:
    try:
        return sum(1 for _ in os.scandir(path))
    except FileNotFoundError:
        return 0
    except NotADirectoryError:
        return 0


def dir_size(path: Path) -> str:
    if not path.exists():
        return "0B"
    try:
        result = subprocess.run(
            ["du", "-sh", str(path)],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.split()[0]
    except Exception:
        return "--"


def downloads_recent(path: Path, days: int = 7) -> int:
    if not path.exists():
        return 0
    cutoff = datetime.now() - timedelta(days=days)
    count = 0
    for root, dirs, files in os.walk(path):
        for name in files:
            try:
                full = Path(root) / name
                if datetime.fromtimestamp(full.stat().st_mtime) >= cutoff:
                    count += 1
            except FileNotFoundError:
                continue
        dirs[:] = []  # don't recurse too deep
    return count


def build_snapshot() -> dict:
    snapshot = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "targets": {},
        "desktop_lanes": {},
        "download_lanes": {},
        "downloads_recent": downloads_recent(TARGETS["downloads"]),
    }
    for key, path in TARGETS.items():
        snapshot["targets"][key] = {
            "count": dir_count(path),
            "size": dir_size(path),
        }
    for key, path in DESKTOP_LANES.items():
        snapshot["desktop_lanes"][key] = dir_count(path)
    for key, path in DOWNLOAD_LANES.items():
        snapshot["download_lanes"][key] = {
            "count": dir_count(path),
            "size": dir_size(path),
        }
    return snapshot


def write_env(snapshot: dict) -> None:
    lines = [
        f"DASH_SNAPSHOT_GENERATED='{snapshot['generated_at']}'",
    ]
    for key, data in snapshot["targets"].items():
        prefix = key.upper()
        lines.append(f"DASH_{prefix}_COUNT={data['count']}")
        lines.append(f"DASH_{prefix}_SIZE='{data['size']}'")
    for key, count in snapshot["desktop_lanes"].items():
        lines.append(f"DASH_DESKTOP_{key.upper()}={count}")
    for key, data in snapshot["download_lanes"].items():
        prefix = key.upper()
        lines.append(f"DASH_DOWNLOAD_{prefix}_COUNT={data['count']}")
        if "size" in data:
            lines.append(f"DASH_DOWNLOAD_{prefix}_SIZE='{data['size']}'")
    lines.append(f"DASH_DOWNLOADS_RECENT={snapshot['downloads_recent']}")
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    ENV_PATH.write_text("\n".join(lines) + "\n")


def write_json(snapshot: dict) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    JSON_PATH.write_text(json.dumps(snapshot, indent=2) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Precompute dashboard metrics.")
    parser.parse_args()
    snap = build_snapshot()
    write_json(snap)
    write_env(snap)
    print(
        "Dashboard snapshot updated",
        snap["generated_at"],
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
