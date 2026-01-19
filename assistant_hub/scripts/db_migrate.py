#!/usr/bin/env python3
"""
Lightweight migration helper to converge the Assistant Hub SQLite schema.

Usage:
    python -m assistant_hub.scripts.db_migrate
    python assistant_hub/scripts/db_migrate.py

What it does:
- Ensures data directories exist (honors ASSISTANT_HUB_DATA_DIR/ASSISTANT_HUB_DB).
- Opens the DB and runs init_db(), which applies all CREATE TABLE/ALTERs + indexes.
- Prints a short summary of the target DB path and exit status.

This is intentionally minimal: the project currently uses an auto-evolving schema
in assistant_hub_gui/assistant_hub/db.py (CREATE IF NOT EXISTS + ALTER IF MISSING).
This helper provides a single entrypoint for CI and local setup until a full
Alembic/SQLModel migration chain is introduced.
"""

from __future__ import annotations

import sys
from pathlib import Path

from assistant_hub.config import DB_PATH, ensure_data_directories
from assistant_hub.db import init_db


def migrate(db_path: Path | None = None) -> Path:
    """Run the built-in schema evolver and return the DB path."""
    ensure_data_directories()
    target = Path(db_path or DB_PATH).expanduser()
    conn = init_db(target)
    conn.close()
    return target


def main(argv: list[str] | None = None) -> int:
    try:
        path = migrate()
        print(f"✓ Migration complete. DB ready at: {path}")
        return 0
    except Exception as exc:  # pragma: no cover - defensive log for CLI use
        print(f"✗ Migration failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main(sys.argv[1:]))
