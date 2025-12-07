"""Main CLI entrypoint for osdash command."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ...config import init_db
from ...db import init_db as db_init_db
from .commands import (
    handle_onenote_command,
    handle_excel_command,
    handle_word_command,
    handle_projects_command,
    handle_history_command,
)


def create_cli_parser() -> argparse.ArgumentParser:
    """Create the main CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="osdash",
        description="OS Dashboard AI Assistant - Command Line Interface",
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
            return handle_projects_command(args, conn)
        elif args.command == "onenote":
            return handle_onenote_command(args, conn)
        elif args.command == "excel":
            return handle_excel_command(args, conn)
        elif args.command == "word":
            return handle_word_command(args, conn)
        elif args.command == "history":
            return handle_history_command(args, conn)
        else:
            print(f"Unknown command: {args.command}")
            return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())


