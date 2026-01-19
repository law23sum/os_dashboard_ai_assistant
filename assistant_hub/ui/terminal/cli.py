"""Main CLI entrypoint for osdash command."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List

from ...db import CHAT_PERSONAS, init_db as db_init_db
from .commands import (
    handle_onenote_command,
    handle_excel_command,
    handle_word_command,
    handle_projects_command,
    handle_history_command,
)
from .harness import (
    detect_project_profile,
    doctor as doctor_profile,
    run_workspace_checks,
    run_target,
    scan_summary,
)
from .workspace import doctor_workspace, print_profiles, scan_workspace


DEFAULT_WORKSPACE_ROOT = Path(__file__).resolve().parents[3]


def create_cli_parser() -> argparse.ArgumentParser:
    """Create the main CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="osdash",
        description="AI OS Console - Command Line Interface",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Projects command
    projects_parser = subparsers.add_parser("projects", help="Manage projects")
    projects_sub = projects_parser.add_subparsers(dest="subcommand")
    projects_sub.add_parser("list", help="List all projects")
    projects_sub.add_parser("view", help="View a project").add_argument(
        "id", help="Project name or ID"
    )
    projects_sub.add_parser("create", help="Create a new project").add_argument(
        "name", help="Project name"
    )

    # Workspace scan command
    scan_parser = subparsers.add_parser("scan", help="Discover git repos and available checks")
    scan_parser.add_argument(
        "--root",
        default=DEFAULT_WORKSPACE_ROOT,
        type=Path,
        help=f"Workspace root to scan (default: {DEFAULT_WORKSPACE_ROOT})",
    )
    scan_parser.add_argument(
        "--max-depth", type=int, default=2, help="Directory depth to scan"
    )
    scan_parser.add_argument(
        "--json", action="store_true", help="Print JSON output"
    )

    # Workspace test command
    test_parser = subparsers.add_parser("test", help="Run lint/test/build/security checks")
    test_parser.add_argument(
        "--root",
        default=DEFAULT_WORKSPACE_ROOT,
        type=Path,
        help=f"Workspace root to scan (default: {DEFAULT_WORKSPACE_ROOT})",
    )
    test_parser.add_argument(
        "--max-depth", type=int, default=2, help="Directory depth to scan"
    )
    test_parser.add_argument(
        "--categories",
        type=str,
        default="lint,test",
        help="Comma-separated categories to run (lint,test,build,security)",
    )
    test_parser.add_argument(
        "--autofix",
        action="store_true",
        help="Trigger scripts/ai_auto_fix.py after failures when present",
    )
    test_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Plan checks without executing commands",
    )
    test_parser.add_argument(
        "--report",
        type=Path,
        help="Optional path for a single aggregated workspace report (JSON)",
    )

    # Workspace run command
    run_parser = subparsers.add_parser("run", help="Launch a dev target")
    run_parser.add_argument("target", choices=["backend", "frontend", "desktop"])
    run_parser.add_argument(
        "--root",
        default=DEFAULT_WORKSPACE_ROOT,
        type=Path,
        help=f"Workspace root to scan (default: {DEFAULT_WORKSPACE_ROOT})",
    )

    # Workspace doctor command
    doctor_parser = subparsers.add_parser("doctor", help="Diagnose workspace health")
    doctor_parser.add_argument(
        "--root",
        default=DEFAULT_WORKSPACE_ROOT,
        type=Path,
        help=f"Workspace root to scan (default: {DEFAULT_WORKSPACE_ROOT})",
    )

    # OneNote command
    onenote_parser = subparsers.add_parser("onenote", help="OneNote operations")
    onenote_sub = onenote_parser.add_subparsers(dest="subcommand")
    onenote_sub.add_parser("list-notebooks", help="List all notebooks")
    onenote_sub.add_parser("list-sections", help="List sections").add_argument(
        "notebook_id", help="Notebook ID"
    )
    onenote_sub.add_parser("list-pages", help="List pages").add_argument(
        "section_id", help="Section ID"
    )
    clean_parser = onenote_sub.add_parser("clean-section", help="Clean a section")
    clean_parser.add_argument("section_id", help="Section ID")
    clean_parser.add_argument(
        "--agent", default="AIC", choices=["AIC", "Aria", "Sora"], help="Agent to use"
    )
    summarize_parser = onenote_sub.add_parser("summarize-page", help="Summarize a page")
    summarize_parser.add_argument("page_id", help="Page ID")
    summarize_parser.add_argument(
        "--agent", default="AIC", choices=["AIC", "Aria", "Sora"], help="Agent to use"
    )

    # Excel command
    excel_parser = subparsers.add_parser("excel", help="Excel operations")
    excel_sub = excel_parser.add_subparsers(dest="subcommand")
    summarize_excel = excel_sub.add_parser("summarize", help="Summarize a workbook")
    summarize_excel.add_argument("path", help="Path to Excel file")
    summarize_excel.add_argument("--sheet", help="Sheet name (optional)")
    summarize_excel.add_argument(
        "--agent", default="AIC", choices=["AIC", "Aria", "Sora"], help="Agent to use"
    )

    # Word command
    word_parser = subparsers.add_parser("word", help="Word document operations")
    word_sub = word_parser.add_subparsers(dest="subcommand")
    draft_parser = word_sub.add_parser("draft", help="Draft a document")
    draft_parser.add_argument("--project", help="Project ID")
    draft_parser.add_argument("--template", help="Template name")
    draft_parser.add_argument(
        "--agent", default="Aria", choices=["AIC", "Aria", "Sora"], help="Agent to use"
    )
    rewrite_parser = word_sub.add_parser("rewrite", help="Rewrite a document")
    rewrite_parser.add_argument("path", help="Path to Word document")
    rewrite_parser.add_argument(
        "--agent", default="Aria", choices=["AIC", "Aria", "Sora"], help="Agent to use"
    )

    # History command
    history_parser = subparsers.add_parser("history", help="View action history")
    history_parser.add_argument(
        "--limit", type=int, default=20, help="Number of entries to show"
    )
    history_parser.add_argument("--agent", help="Filter by agent")
    history_parser.add_argument(
        "--tag", help="Filter by tag (onenote, excel, word, etc.)"
    )

    # Audit command
    audit_parser = subparsers.add_parser("audit", help="Audit ledger utilities")
    audit_sub = audit_parser.add_subparsers(dest="subcommand")
    emit_parser = audit_sub.add_parser("emit", help="Emit a dev audit event")
    emit_parser.add_argument("--event-type", required=True, help="Event type to emit")
    emit_parser.add_argument("--message", required=True, help="Event message")
    emit_parser.add_argument("--payload", help="JSON payload string")

    verify_parser = audit_sub.add_parser("verify-ledger", help="Verify ledger hash chain")
    verify_parser.add_argument("--from-seq", type=int, help="Start sequence")
    verify_parser.add_argument("--to-seq", type=int, help="End sequence")

    audit_sub.add_parser("rotate", help="Rotate archives now")
    audit_sub.add_parser("list-archives", help="List archive records")

    verify_archive = audit_sub.add_parser("verify-archive", help="Verify an archive bundle")
    verify_archive.add_argument("path", help="Path to encrypted archive")

    restore_archive = audit_sub.add_parser("restore-archive", help="Restore an archive bundle")
    restore_archive.add_argument("path", help="Path to encrypted archive")
    restore_archive.add_argument("output_dir", help="Directory for extracted files")

    # Chat command - interactive AI chat
    chat_parser = subparsers.add_parser("chat", help="Interactive chat with AI agents")
    chat_parser.add_argument(
        "--agent",
        choices=CHAT_PERSONAS,
        help="AI agent to use (default: interactive selection)",
    )
    chat_parser.add_argument(
        "--clear-history",
        action="store_true",
        help="Start with empty conversation history",
    )
    chat_parser.add_argument(
        "--clear-on-switch",
        action="store_true",
        help="Clear history when switching agents",
    )
    chat_parser.add_argument(
        "--enable-shell",
        action="store_true",
        default=True,
        help="Allow AI to execute shell commands (default: True)",
    )
    chat_parser.add_argument(
        "--no-shell",
        dest="enable_shell",
        action="store_false",
        help="Disable shell command execution",
    )
    chat_parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show verbose error messages",
    )

    return parser


def main() -> int:
    """Main CLI entrypoint."""
    parser = create_cli_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Harness commands do not require DB access
    if args.command == "scan":
        summary = scan_summary(args.root, max_depth=args.max_depth)
        workspace_profiles = scan_workspace(args.root, max_depth=args.max_depth)
        workspace_notes = doctor_workspace(workspace_profiles)
        payload = {
            "root": summary["root"],
            "projects": summary.get("projects", []),
            "workspace_profiles": [profile.to_dict() for profile in workspace_profiles],
            "notes": workspace_notes,
        }
        if args.json:
            print(json.dumps(payload, indent=2))
        else:
            print(f"[osdash] scanned {summary['root']}")
            for project in summary.get("projects", []):
                commands = ", ".join(project.get("commands", {}).keys()) or "no checks"
                print(f" - {project.get('name')}: {commands}")
            if workspace_profiles:
                print("[osdash] workspace profiles:")
                print_profiles(workspace_profiles, as_json=False)
            for note in workspace_notes:
                print(f"[osdash] note: {note}")
        return 0

    if args.command == "test":
        categories: List[str] = [
            part.strip() for part in args.categories.split(",") if part.strip()
        ]
        report = run_workspace_checks(
            args.root,
            categories,
            max_depth=args.max_depth,
            autofix=args.autofix,
            dry_run=args.dry_run,
            report_path=args.report,
        )
        summary = report.get("summary", {})
        projects = summary.get("projects", 0)
        root = summary.get("root", args.root)
        print(f"[osdash] scanned {projects} project(s) under {root}")
        print(
            "[osdash] checks: {total} | passed: {passed} | failed: {failed} | skipped: {skipped}".format(
                total=summary.get("checks", 0),
                passed=summary.get("passed", 0),
                failed=summary.get("failed", 0),
                skipped=summary.get("skipped", 0),
            )
        )
        if summary.get("report_path"):
            print(f"[osdash] report saved to {summary.get('report_path')}")
        return 1 if summary.get("failed", 0) else 0

    if args.command == "run":
        profile = detect_project_profile(args.root.resolve())
        if not profile.commands:
            print("[osdash] no commands detected in this project; ensure dependencies are installed")
        return run_target(profile, args.target)

    if args.command == "doctor":
        summary = doctor_profile(args.root)
        workspace_profiles = scan_workspace(args.root, max_depth=1)
        workspace_notes = doctor_workspace(workspace_profiles)
        for check in summary["checks"]:
            label = check["label"]
            status = check["status"]
            detail = "; ".join(check.get("output", []))
            print(f"[osdash] {label}: {status} ({detail})")
        for note in workspace_notes:
            print(f"[osdash] note: {note}")
        return 0

    # Initialize database
    conn = db_init_db()

    try:
        if args.command == "projects":
            return handle_projects_command(args, conn)
        elif args.command == "onenote":
            return handle_onenote_command(args, conn)
        elif args.command == "excel":
            return handle_excel_command(args, conn)
        elif args.command == "word":
            return handle_word_command(args, conn)
        elif args.command == "history":
            return handle_history_command(args, conn)
        elif args.command == "audit":
            from .commands.audit import handle_audit_command

            return handle_audit_command(args)
        elif args.command == "chat":
            from ui.terminal.commands.chat import handle_chat_command

            return handle_chat_command(args)
        else:
            print(f"Unknown command: {args.command}")
            return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
