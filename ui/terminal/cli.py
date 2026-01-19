"""Main CLI entrypoint for osdash command."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from assistant_hub.db import CHAT_PERSONAS, init_db as db_init_db

# Import commands lazily to avoid hard dependency requirements for unused commands
# from .commands import ... (removed top-level import)


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
    projects_sub.add_parser("view", help="View a project").add_argument("id", help="Project name or ID")
    projects_sub.add_parser("create", help="Create a new project").add_argument("name", help="Project name")

    # OneNote command
    onenote_parser = subparsers.add_parser("onenote", help="OneNote operations")
    onenote_sub = onenote_parser.add_subparsers(dest="subcommand")
    onenote_sub.add_parser("list-notebooks", help="List all notebooks")
    onenote_sub.add_parser("list-sections", help="List sections").add_argument("notebook_id", help="Notebook ID")
    onenote_sub.add_parser("list-pages", help="List pages").add_argument("section_id", help="Section ID")
    clean_parser = onenote_sub.add_parser("clean-section", help="Clean a section")
    clean_parser.add_argument("section_id", help="Section ID")
    clean_parser.add_argument("--agent", default="AIC", choices=["AIC", "Aria", "Sora"], help="Agent to use")
    summarize_parser = onenote_sub.add_parser("summarize-page", help="Summarize a page")
    summarize_parser.add_argument("page_id", help="Page ID")
    summarize_parser.add_argument("--agent", default="AIC", choices=["AIC", "Aria", "Sora"], help="Agent to use")

    # Excel command
    excel_parser = subparsers.add_parser("excel", help="Excel operations")
    excel_sub = excel_parser.add_subparsers(dest="subcommand")
    summarize_excel = excel_sub.add_parser("summarize", help="Summarize a workbook")
    summarize_excel.add_argument("path", help="Path to Excel file")
    summarize_excel.add_argument("--sheet", help="Sheet name (optional)")
    summarize_excel.add_argument("--agent", default="AIC", choices=["AIC", "Aria", "Sora"], help="Agent to use")

    # Word command
    word_parser = subparsers.add_parser("word", help="Word document operations")
    word_sub = word_parser.add_subparsers(dest="subcommand")
    draft_parser = word_sub.add_parser("draft", help="Draft a document")
    draft_parser.add_argument("--project", help="Project ID")
    draft_parser.add_argument("--template", help="Template name")
    draft_parser.add_argument("--agent", default="Aria", choices=["AIC", "Aria", "Sora"], help="Agent to use")
    rewrite_parser = word_sub.add_parser("rewrite", help="Rewrite a document")
    rewrite_parser.add_argument("path", help="Path to Word document")
    rewrite_parser.add_argument("--agent", default="Aria", choices=["AIC", "Aria", "Sora"], help="Agent to use")

    # History command
    history_parser = subparsers.add_parser("history", help="View action history")
    history_parser.add_argument("--limit", type=int, default=20, help="Number of entries to show")
    history_parser.add_argument("--agent", help="Filter by agent")
    history_parser.add_argument("--tag", help="Filter by tag (onenote, excel, word, etc.)")

    # API session costs
    api_costs_parser = subparsers.add_parser(
        "api-session-costs",
        help="Show API session costs by provider and version",
    )
    api_costs_parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw JSON instead of a table",
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
        "--verbose", "-v",
        action="store_true",
        help="Show verbose error messages",
    )
    chat_parser.add_argument(
        "--style",
        help="Interaction style (discussion, debate, informative, persuasive)",
    )

    # Workspace orchestration commands
    scan_parser = subparsers.add_parser("scan", help="Discover git repos and inferred commands")
    scan_parser.add_argument("--root", help="Workspace root to scan (defaults to parent of repo)")
    scan_parser.add_argument("--max-depth", type=int, default=3, help="Maximum directory depth to search")
    scan_parser.add_argument("--exclude", action="append", default=[], help="Paths to exclude")
    scan_parser.add_argument("--json", action="store_true", help="Output as JSON")

    test_parser = subparsers.add_parser("test", help="Run lint/test/security suites across repos")
    test_parser.add_argument("--root", help="Workspace root (defaults to parent of repo)")
    test_parser.add_argument("--max-depth", type=int, default=2, help="Maximum directory depth to search")
    test_parser.add_argument("--project", help="Restrict to a single repo name")
    test_parser.add_argument(
        "--categories",
        nargs="+",
        default=["lint", "test", "security"],
        help="Categories to run (lint, test, security, build)",
    )
    test_parser.add_argument("--autofix", action="store_true", help="Invoke autofix script on failures when available")
    test_parser.add_argument("--dry-run", action="store_true", help="List commands without executing them")

    run_parser = subparsers.add_parser("run", help="Start a repo using inferred run commands")
    run_parser.add_argument("project", nargs="?", help="Repo name to run (defaults to current repo)")
    run_parser.add_argument("--root", help="Workspace root (defaults to parent of repo)")
    run_parser.add_argument("--max-depth", type=int, default=3, help="Maximum directory depth to search")
    run_parser.add_argument("--command", help="Override run command")

    doctor_parser = subparsers.add_parser("doctor", help="Diagnose common workspace issues")
    doctor_parser.add_argument("--root", help="Workspace root (defaults to parent of repo)")
    doctor_parser.add_argument("--max-depth", type=int, default=3, help="Maximum directory depth to search")
    doctor_parser.add_argument("--json", action="store_true", help="Output as JSON")

    return parser


def main() -> int:
    """Main CLI entrypoint."""
    parser = create_cli_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Initialize database
    conn = db_init_db()

    try:
        if args.command == "projects":
            from .commands.projects import handle_projects_command
            return handle_projects_command(args, conn)
        elif args.command == "onenote":
            from .commands.onenote import handle_onenote_command
            return handle_onenote_command(args, conn)
        elif args.command == "excel":
            from .commands.excel import handle_excel_command
            return handle_excel_command(args, conn)
        elif args.command == "word":
            from .commands.word import handle_word_command
            return handle_word_command(args, conn)
        elif args.command == "history":
            from .commands.history import handle_history_command
            return handle_history_command(args, conn)
        elif args.command == "api-session-costs":
            from .commands.api_session_costs import handle_api_session_costs_command
            return handle_api_session_costs_command(args, conn)
        elif args.command == "audit":
            from .commands.audit import handle_audit_command
            return handle_audit_command(args)
        elif args.command == "chat":
            from .commands.chat import handle_chat_command
            return handle_chat_command(args)
        elif args.command == "scan":
            from .commands.workspace import handle_scan_command
            return handle_scan_command(args)
        elif args.command == "test":
            from .commands.workspace import handle_test_command
            return handle_test_command(args)
        elif args.command == "run":
            from .commands.workspace import handle_run_command
            return handle_run_command(args)
        elif args.command == "doctor":
            from .commands.workspace import handle_doctor_command
            return handle_doctor_command(args)
        else:
            print(f"Unknown command: {args.command}")
            return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
