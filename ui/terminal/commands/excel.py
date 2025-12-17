"""Excel CLI commands."""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

from assistant_hub.integrations.excel.service import ExcelService


def handle_excel_command(args, conn: sqlite3.Connection) -> int:
    """Handle Excel CLI commands."""
    service = ExcelService()

    if args.subcommand == "summarize":
        path = Path(args.path)
        if not path.exists():
            print(f"Error: File not found: {path}", file=sys.stderr)
            return 1

        sheet_name = args.sheet or "Sheet1"
        instruction = f"Create a summary of the data in {sheet_name}"

        print(f"Summarizing {path} (sheet: {sheet_name}) with agent {args.agent}...")
        try:
            changed_files = service.summarize_sheet(str(path), sheet_name, instruction, actor=args.agent)
            print(f"Summary created. Modified files:")
            for f in changed_files:
                print(f"  - {f}")
            return 0
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

    else:
        print(f"Unknown Excel subcommand: {args.subcommand}", file=sys.stderr)
        return 1
