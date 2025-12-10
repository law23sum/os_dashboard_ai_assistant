"""Load and save dashboard state from database."""

from __future__ import annotations

import sqlite3
from typing import Optional

from ..db import (
    AssistantState,
    Project,
    Task,
    ChatMessage,
    NoteLink,
    AgentRun,
    load_state as db_load_state,
    init_db,
)


def load_state(conn: Optional[sqlite3.Connection] = None) -> AssistantState:
    """Load the complete dashboard state from the database."""
    if conn is None:
        conn = init_db()
    return db_load_state(conn)


def save_state(
    state: AssistantState, conn: Optional[sqlite3.Connection] = None
) -> None:
    """Save the dashboard state to the database."""
    if conn is None:
        conn = init_db()
    # State is saved incrementally through individual operations
    # This is a placeholder for future bulk save operations
    pass
