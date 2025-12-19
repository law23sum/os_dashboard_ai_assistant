"""Workspace-level osdash commands."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Iterable, List, Optional, Sequence

from assistant_hub.ui.terminal import harness, workspace

DEFAULT_WORKSPACE_ROOT = workspace.REPO_ROOT.parent


def _resolve_root(root: Optional[str]) -> Path:
    """Resolve workspace root from CLI flag, env, or default."""

    if root:
        return Path(root).expanduser().resolve()
    env_root = os.environ.get("OSDASH_WORKSPACE_ROOT")
    if env_root:
        return Path(env_root).expanduser().resolve()
    return DEFAULT_WORKSPACE_ROOT


def _print_report(results: Iterable[harness.CheckResult]) -> None:
    for result in results:
        status = result.status
        command = " ".join(result.command)
        print(f"[{status}] {command} ({result.duration_seconds:.1f}s)")
        if result.output.strip():
            print(result.output.strip())


def handle_scan_command(args) -> int:
    root = _resolve_root(getattr(args, "root", None))
    profiles = workspace.scan_workspace(
        root,
        max_depth=getattr(args, "max_depth", 3),
        excludes=getattr(args, "exclude", None),
    )
    if getattr(args, "json", False):
        json.dump([p.to_dict() for p in profiles], sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0
    workspace.print_profiles(profiles, as_json=False)
    return 0


def handle_test_command(args) -> int:
    root = _resolve_root(getattr(args, "root", None))
    profiles = harness.discover_profiles(root, max_depth=getattr(args, "max_depth", 2))
    if getattr(args, "project", None):
        profiles = [p for p in profiles if p.name == args.project]
    if not profiles:
        print(f"[osdash] no repositories with commands found under {root}")
        return 1

    categories: Sequence[str] = getattr(args, "categories", ["lint", "test", "security"])
    dry_run = getattr(args, "dry_run", False)
    overall_ok = True

    for profile in profiles:
        if dry_run:
            print(f"- {profile.name} ({profile.root})")
            for category in categories:
                cmds = profile.commands.get(category, [])
                if not cmds:
                    continue
                print(f"  {category}: {[ ' '.join(cmd) for cmd in cmds ]}")
            continue

        results = harness.run_checks(profile, categories, autofix=getattr(args, "autofix", False))
        harness.write_report(profile, results)
        _print_report(results)
        if any(r.status == "failed" for r in results):
            overall_ok = False

    return 0 if (overall_ok or dry_run) else 1


def handle_run_command(args) -> int:
    root = _resolve_root(getattr(args, "root", None))
    profiles = workspace.scan_workspace(root, max_depth=getattr(args, "max_depth", 3))
    target = getattr(args, "project", None)
    if not target and profiles:
        target = workspace.REPO_ROOT.name
    profile = next((p for p in profiles if p.name == target or p.path.name == target), None)
    if not profile:
        print(f"[osdash] unable to find repo named {target!r} under {root}")
        return 1
    result = workspace.execute_run(profile, override_command=getattr(args, "command", None))
    return getattr(result, "returncode", 0)


def handle_doctor_command(args) -> int:
    root = _resolve_root(getattr(args, "root", None))
    profiles = workspace.scan_workspace(root, max_depth=getattr(args, "max_depth", 3))
    doctor_notes: List[str] = workspace.doctor_workspace(profiles)
    env_report = harness.doctor(root)

    if getattr(args, "json", False):
        json.dump({"notes": doctor_notes, "env": env_report}, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0

    print("Doctor report:")
    for note in doctor_notes:
        print(f"- {note}")
    print("\nEnvironment:")
    for check in env_report["checks"]:
        label = check["label"]
        status = check["status"]
        lines = ", ".join(check.get("output", []))
        print(f"- {label}: {status} ({lines})")
    return 0
