#!/usr/bin/env python3
"""Script to import existing documents from the filesystem into the database."""

import sys
import os
from pathlib import Path

# Add the assistant_hub_gui directory to the path
assistant_hub_gui_dir = Path(__file__).parent
if str(assistant_hub_gui_dir) not in sys.path:
    sys.path.insert(0, str(assistant_hub_gui_dir))

from assistant_hub.document_manager import scan_and_import_existing_documents
from assistant_hub.db import init_db
from assistant_hub.logging_config import configure_logging


def main():
    """Import existing documents."""
    configure_logging()

    print("🔍 Scanning for existing documents to import...")

    # Get database connection
    conn = init_db()

    try:
        # Scan and import documents
        imported_count, errors = scan_and_import_existing_documents(conn)

        print(f"✅ Successfully imported {imported_count} documents")

        if errors:
            print("❌ Errors encountered:")
            for error in errors:
                print(f"  - {error}")
        else:
            print("🎉 No errors encountered!")

    except Exception as e:
        print(f"❌ Error during import: {e}")
        return 1

    finally:
        conn.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
