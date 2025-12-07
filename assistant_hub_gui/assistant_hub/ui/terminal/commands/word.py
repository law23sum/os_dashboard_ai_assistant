"""Word CLI commands."""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

from ....integrations.word.service import WordService


def handle_word_command(args, conn: sqlite3.Connection) -> int:
    """Handle Word CLI commands."""
    service = WordService()

    if args.subcommand == "draft":
        print(f"Drafting document with agent {args.agent}...")
        # This is a placeholder - would need project context
        print("Draft functionality requires project context. Use GUI for full features.")
        return 0

    elif args.subcommand == "rewrite":
        path = Path(args.path)
        if not path.exists():
            print(f"Error: File not found: {path}", file=sys.stderr)
            return 1

        print(f"Rewriting {path} with agent {args.agent}...")
        try:
            changed_files = service.rewrite_document(str(path), style="concise", actor=args.agent)
            print(f"Document rewritten. Modified files:")
            for f in changed_files:
                print(f"  - {f}")
            return 0
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

    else:
        print(f"Unknown Word subcommand: {args.subcommand}", file=sys.stderr)
        return 1



