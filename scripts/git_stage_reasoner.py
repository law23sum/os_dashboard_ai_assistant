#!/usr/bin/env python3
"""Capture staged files and record why each one changed.

This helper runs after every `git add` (via the bash wrapper) so each staged
file has a short explanation before the auto-commit script runs. Reasons are
stored in .git/.ai_stage_reasons.json for later reuse/editing.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
REASONS_FILE = REPO_ROOT / ".git" / ".ai_stage_reasons.json"
ASK_UNCERTAINTY_THRESHOLD = 0.05  # Only prompt when confidence <= 5%


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
        errors="replace",
    )


def staged_files() -> list[str]:
    proc = run(["git", "diff", "--cached", "--name-only"])
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def staged_statuses() -> Dict[str, str]:
    proc = run(["git", "diff", "--cached", "--name-status"])
    mapping: Dict[str, str] = {}
    for line in proc.stdout.splitlines():
        parts = [segment.strip() for segment in line.strip().split("\t") if segment.strip()]
        if not parts:
            continue
        status = parts[0]
        if len(parts) == 2:
            path = parts[1]
            mapping[path] = status
        elif len(parts) >= 3:
            old_path, new_path = parts[1], parts[-1]
            mapping[new_path] = f"{status} {old_path} -> {new_path}"
    return mapping


def diff_for(path: str) -> str:
    proc = run(["git", "diff", "--cached", "--", path])
    return proc.stdout


def diff_hash(diff_text: str) -> str:
    return hashlib.sha1(diff_text.encode("utf-8", errors="replace")).hexdigest()


def load_stage_data() -> Dict:
    if not REASONS_FILE.exists():
        return {"files": {}}
    try:
        return json.loads(REASONS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {"files": {}}


def save_stage_data(data: Dict) -> None:
    REASONS_FILE.parent.mkdir(parents=True, exist_ok=True)
    REASONS_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def auto_reason(path: str, diff_text: str) -> Tuple[str | None, float]:
    specific = {
        "assistant_hub_gui/assistant_hub/gui.py": "Refined Assistant Hub GUI layout, theming, or event handling.",
        "assistant_core/cognitive_framework.py": "Updated cognitive framework (personas, daemons, reasoning).",
        "documentation/OS_DashboardAIAssistantTOC.md": "Reorganized canonical spec / documentation.",
        "scripts/git_auto_commit.py": "Updated auto-commit workflow.",
    }
    for needle, text in specific.items():
        if path == needle:
            return text, 1.0

    prefix_map = [
        ("documentation/", "Documentation/spec alignment updates."),
        ("docs/", "Docs or static site refresh."),
        ("assistant_core/", "Core assistant runtime adjustments."),
        ("assistant_hub_gui/", "Desktop GUI updates for Assistant Hub."),
        ("assistant_hub/", "Backend hub services updated."),
        ("ai_os/app/", "AI OS service/daemon changes."),
        ("scripts/", "Workflow/script automation updates."),
        ("tests/", "Test coverage adjustments."),
    ]
    for prefix, text in prefix_map:
        if path.startswith(prefix):
            return text, 0.8

    ext_map = {
        ".md": "Documentation changes.",
        ".py": "Python implementation update.",
        ".sh": "Shell tooling update.",
        ".json": "Configuration update.",
        ".yml": "Configuration update.",
    }
    for ext, text in ext_map.items():
        if path.endswith(ext):
            return text, 0.65

    if "TODO" in diff_text or "FIXME" in diff_text:
        return "Addressed TODO/FIXME items.", 0.4

    return None, 0.0


def prompt_for_reason(path: str, suggestion: str | None, diff_text: str) -> str:
    print(f"\nProvide a reason for {path}:")
    if suggestion:
        print(f"  AI guess: {suggestion}")
    preview = "\n".join(diff_text.splitlines()[:40])
    if preview:
        print("\n--- Diff preview (first 40 lines) ---")
        print(preview)
        print("--- End preview ---\n")
    prompt = "Reason (enter to accept AI guess)" if suggestion else "Reason"
    while True:
        user_input = input(f"{prompt}: ").strip()
        if user_input:
            return user_input
        if suggestion:
            return suggestion
        print("A reason is required.")


def main() -> int:
    files = staged_files()
    if not files:
        return 0
    data = load_stage_data()
    status_map = staged_statuses()
    entries = data.setdefault("files", {})
    now = datetime.now(timezone.utc).isoformat()
    updated = False

    for path in files:
        diff_text = diff_for(path)
        digest = diff_hash(diff_text)
        entry = entries.get(path)
        if entry and entry.get("hash") == digest:
            continue
        guess, confidence = auto_reason(path, diff_text)
        if not guess or confidence <= ASK_UNCERTAINTY_THRESHOLD:
            reason = prompt_for_reason(path, guess, diff_text)
            source = "user"
        else:
            reason = guess
            source = "auto"
        entries[path] = {
            "reason": reason,
            "source": source,
            "hash": digest,
            "updated_at": now,
        }
        updated = True

    # Remove entries for files no longer staged
    staged_set = set(files)
    removed = [p for p in list(entries.keys()) if p not in staged_set]
    for path in removed:
        del entries[path]
        updated = True

    if updated:
        data["updated_at"] = now
        save_stage_data(data)

    print("\nStage Reasoning Summary:")
    status_width = max((len(status_map.get(path, "")) for path in files), default=1)
    for path in files:
        reason = entries[path]["reason"]
        source = entries[path]["source"]
        status = status_map.get(path, "?") or "?"
        aligned_status = status.rjust(status_width)
        print(f"{aligned_status} {path} — {reason} ({source})")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        sys.exit(130)
