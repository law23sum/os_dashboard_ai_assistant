#!/usr/bin/env python3
import json
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
MISSING_PATH = REPO_ROOT / "agent_exports" / "recovery" / "MISSING_PAGE_SET.json"
OUT_PATH = REPO_ROOT / "agent_exports" / "recovery" / "RECOVERY_CANDIDATES.json"

PLACEHOLDER_PATTERNS = [
    "FeaturePageTemplate",
    "CategoryHomeTemplate",
    "PlatformLandingTemplate",
    "RouteScaffold",
]


def is_placeholder(text: str) -> bool:
    if any(pat in text for pat in PLACEHOLDER_PATTERNS):
        return True
    if re.search(r"return\s+null", text):
        return True
    if re.search(r"return\s*<></>", text) or re.search(r"return\s*\(\s*<></>\s*\)", text):
        return True
    return False


def git_history(path: str, limit: int = 50) -> List[str]:
    try:
        out = subprocess.check_output([
            "git", "log", "--follow", f"--max-count={limit}", "--format=%H", "--", path
        ], cwd=REPO_ROOT)
        commits = out.decode().splitlines()
        return commits
    except subprocess.CalledProcessError:
        return []


def git_show(commit: str, path: str) -> Optional[str]:
    try:
        out = subprocess.check_output(
            ["git", "show", f"{commit}:{path}"], cwd=REPO_ROOT, stderr=subprocess.DEVNULL
        )
        return out.decode(errors="ignore")
    except subprocess.CalledProcessError:
        return None


def commit_file_count(commit: str) -> int:
    try:
        out = subprocess.check_output([
            "git", "diff-tree", "--no-commit-id", "--name-only", "-r", commit
        ], cwd=REPO_ROOT)
        return len(out.decode().splitlines())
    except subprocess.CalledProcessError:
        return 0


def risk_from_count(count: int) -> str:
    if count <= 5:
        return "low"
    if count <= 20:
        return "medium"
    return "high"


def normalize_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def get_renames() -> List[Tuple[str, str, str]]:
    """Return list of (commit, old_path, new_path)."""
    try:
        out = subprocess.check_output(
            [
                "git",
                "log",
                "--all",
                "--name-status",
                "--diff-filter=R",
                "--pretty=format:%H",
            ],
            cwd=REPO_ROOT,
        ).decode()
    except subprocess.CalledProcessError:
        return []
    renames = []
    current_commit = None
    for line in out.splitlines():
        if not line:
            continue
        if re.fullmatch(r"[0-9a-f]{7,40}", line):
            current_commit = line.strip()
            continue
        if line.startswith("R") and current_commit:
            parts = line.split("\t")
            if len(parts) >= 3:
                old_path = parts[1]
                new_path = parts[2]
                renames.append((current_commit, old_path, new_path))
    return renames


def get_deletions() -> List[Tuple[str, str]]:
    """Return list of (commit, deleted_path)."""
    try:
        out = subprocess.check_output(
            [
                "git",
                "log",
                "--all",
                "--name-only",
                "--diff-filter=D",
                "--pretty=format:%H",
            ],
            cwd=REPO_ROOT,
        ).decode()
    except subprocess.CalledProcessError:
        return []
    deletions = []
    current_commit = None
    for line in out.splitlines():
        if not line:
            continue
        if re.fullmatch(r"[0-9a-f]{7,40}", line):
            current_commit = line.strip()
            continue
        if current_commit:
            deletions.append((current_commit, line.strip()))
    return deletions


def main() -> None:
    missing = json.loads(MISSING_PATH.read_text())
    component_paths = sorted({entry["current_component"] for entry in missing if entry.get("current_component")})

    missing_by_component = {entry["current_component"]: entry for entry in missing if entry.get("current_component")}
    missing_by_basename = {}
    for entry in missing:
        comp = entry.get("current_component")
        if not comp:
            continue
        base = Path(comp).name
        missing_by_basename.setdefault(normalize_name(base), []).append(entry)

    candidates: Dict[str, Dict[str, object]] = {}

    renames = get_renames()
    deletions = get_deletions()

    rename_map = {}
    for commit, old_path, new_path in renames:
        rename_map.setdefault(new_path, []).append((commit, old_path))

    deletion_map = {}
    for commit, deleted_path in deletions:
        deletion_map.setdefault(deleted_path, []).append(commit)

    for path in component_paths:
        commits = git_history(path)
        found = None
        evidence = None
        for commit in commits:
            content = git_show(commit, path)
            if content is None:
                continue
            if not is_placeholder(content):
                found = commit
                evidence = "Non-template content detected"
                break
        if not found:
            # Check renames into this path
            for commit, old_path in rename_map.get(path, []):
                content = git_show(commit, path)
                if content and not is_placeholder(content):
                    found = commit
                    evidence = f"Rename into {path} from {old_path}"
                    break
                # Check pre-rename content
                if old_path:
                    parent_content = git_show(f"{commit}^", old_path)
                    if parent_content and not is_placeholder(parent_content):
                        found = commit
                        evidence = f"Pre-rename content at {old_path}"
                        break

        if not found:
            # Check deleted files with matching base name
            base_key = normalize_name(Path(path).name)
            for entry in missing_by_basename.get(base_key, []):
                comp = entry.get("current_component")
                if not comp:
                    continue
                for deleted_path, commits_for_path in deletion_map.items():
                    if normalize_name(Path(deleted_path).name) != base_key:
                        continue
                    for commit in commits_for_path:
                        content = git_show(f"{commit}^", deleted_path)
                        if content and not is_placeholder(content):
                            found = commit
                            evidence = f"Deleted file {deleted_path} matched by name"
                            break
                    if found:
                        break
                if found:
                    break

        if found:
            count = commit_file_count(found)
            candidates[path] = {
                "candidate_commit": found,
                "evidence": evidence,
                "risk": risk_from_count(count),
                "files_changed": count,
            }
        else:
            candidates[path] = {
                "candidate_commit": None,
                "evidence": "No non-template version found in history scan",
                "risk": "high",
                "files_changed": 0,
            }

    # Expand back to missing routes
    result = []
    for entry in missing:
        comp = entry.get("current_component")
        info = candidates.get(comp, {})
        result.append({
            "route": entry.get("route"),
            "component": comp,
            "placeholder_reason": entry.get("placeholder_reason"),
            "platform": entry.get("platform"),
            "category": entry.get("category"),
            "feature": entry.get("feature"),
            "candidate_commit": info.get("candidate_commit"),
            "evidence": info.get("evidence"),
            "risk": info.get("risk"),
            "files_changed": info.get("files_changed"),
        })

    OUT_PATH.write_text(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
