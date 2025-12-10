#!/usr/bin/env python3
"""Remove duplicate tasks from the database."""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from assistant_hub.db import init_db, load_state, db_delete_task


def main():
    """Remove duplicate tasks."""
    conn = init_db()
    state = load_state(conn)

    print(f"Total tasks before cleanup: {len(state.tasks)}\n")

    # Find duplicates by (title, project) pair
    seen = {}
    duplicates = []

    for task in state.tasks:
        key = (task.title.lower().strip(), task.project)
        if key in seen:
            duplicates.append(task)
        else:
            seen[key] = task

    print(f"Found {len(duplicates)} duplicate tasks\n")

    if duplicates:
        print("Removing duplicates...")
        for task in duplicates:
            print(f"  Removing: {task.title[:60]}... (Project: {task.project})")
            db_delete_task(conn, task.id)

        print(f"\nRemoved {len(duplicates)} duplicate tasks")
    else:
        print("No duplicates found!")

    # Reload and show final count
    state = load_state(conn)
    print(f"\nTotal tasks after cleanup: {len(state.tasks)}")

    conn.close()


if __name__ == "__main__":
    main()
