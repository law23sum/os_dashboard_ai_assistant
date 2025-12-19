"""Projects CLI commands."""

from __future__ import annotations

import sqlite3
import sys

from assistant_hub.db import load_state, db_upsert_project, Project


def handle_projects_command(args, conn: sqlite3.Connection) -> int:
    """Handle Projects CLI commands."""
    state = load_state(conn)

    if args.subcommand == "list":
        print(f"Found {len(state.projects)} projects:")
        for proj in state.projects:
            print(f"  - {proj.name} ({proj.status}) - {proj.description}")
        return 0

    elif args.subcommand == "view":
        project = next((p for p in state.projects if p.name == args.id or p.name == args.id), None)
        if not project:
            print(f"Project not found: {args.id}", file=sys.stderr)
            return 1

        print(f"Project: {project.name}")
        print(f"  Description: {project.description}")
        print(f"  Status: {project.status}")
        print(f"  Priority: {project.priority}")
        return 0

    elif args.subcommand == "create":
        project = Project(
            name=args.name,
            description="",
            status="active",
            priority="MEDIUM",
        )
        db_upsert_project(conn, project)
        print(f"Created project: {args.name}")
        return 0

    else:
        print(f"Unknown Projects subcommand: {args.subcommand}", file=sys.stderr)
        return 1
