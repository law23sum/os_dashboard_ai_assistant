"""OneNote CLI commands."""

from __future__ import annotations

import sqlite3
import sys

from ....integrations.onenote.client import OneNoteClient
from ....integrations.onenote.service import OneNoteService
from ....config import DATA_DIR


def handle_onenote_command(args, conn: sqlite3.Connection) -> int:
    """Handle OneNote CLI commands."""
    from ....versioning import start_worker
    
    # Start git worker if not already running
    start_worker()
    
    client = OneNoteClient()
    mirror_root = DATA_DIR / "onenote_mirror"
    service = OneNoteService(str(mirror_root), client)

    if args.subcommand == "list-notebooks":
        notebooks = client.list_notebooks()
        print(f"Found {len(notebooks)} notebooks:")
        for nb in notebooks:
            print(f"  - {nb.get('displayName', 'Unknown')} (ID: {nb.get('id', 'N/A')})")
        return 0

    elif args.subcommand == "list-sections":
        sections = client.list_sections(args.notebook_id)
        print(f"Found {len(sections)} sections:")
        for sec in sections:
            print(f"  - {sec.get('displayName', 'Unknown')} (ID: {sec.get('id', 'N/A')})")
        return 0

    elif args.subcommand == "list-pages":
        pages = client.list_pages(args.section_id)
        print(f"Found {len(pages)} pages:")
        for page in pages:
            print(f"  - {page.get('title', 'Unknown')} (ID: {page.get('id', 'N/A')})")
        return 0

    elif args.subcommand == "clean-section":
        print(f"Cleaning section {args.section_id} with agent {args.agent}...")
        paths = service.clean_section(args.section_id, actor=args.agent)
        print(f"Cleaned {len(paths)} pages. Files saved to:")
        for path in paths:
            print(f"  - {path}")
        return 0

    elif args.subcommand == "summarize-page":
        print(f"Summarizing page {args.page_id} with agent {args.agent}...")
        path = service.summarize_page(args.page_id)
        print(f"Summary saved to: {path}")
        return 0

    else:
        print(f"Unknown OneNote subcommand: {args.subcommand}", file=sys.stderr)
        return 1

