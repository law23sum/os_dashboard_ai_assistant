"""Comments and discussions system for tasks and projects."""

from datetime import datetime
from typing import List, Optional, Dict
from dataclasses import dataclass

import sqlite3
from .db import init_db, DB_FILE


@dataclass
class Comment:
    """A comment on a task or project."""
    id: int
    entity_type: str  # "task" or "project"
    entity_id: str  # Task ID or project name
    author: str  # Persona name
    content: str
    created_at: str
    mentions: Optional[str] = None  # JSON array of mentioned personas


def init_comments_table(conn: sqlite3.Connection):
    """Initialize the comments table if it doesn't exist."""
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_type TEXT NOT NULL,
            entity_id TEXT NOT NULL,
            author TEXT NOT NULL,
            content TEXT NOT NULL,
            mentions TEXT,
            created_at TEXT NOT NULL
        )
    """)
    c.execute("""
        CREATE INDEX IF NOT EXISTS idx_comments_entity 
        ON comments(entity_type, entity_id)
    """)
    conn.commit()


def add_comment(
    conn: sqlite3.Connection,
    entity_type: str,
    entity_id: str,
    author: str,
    content: str,
    mentions: Optional[List[str]] = None
) -> int:
    """Add a comment to a task or project."""
    init_comments_table(conn)
    
    c = conn.cursor()
    mentions_json = None
    if mentions:
        import json
        mentions_json = json.dumps(mentions)
    
    created_at = datetime.now().isoformat(timespec="seconds")
    
    c.execute("""
        INSERT INTO comments (entity_type, entity_id, author, content, mentions, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (entity_type, entity_id, author, content, mentions_json, created_at))
    
    conn.commit()
    return c.lastrowid


def get_comments(
    conn: sqlite3.Connection,
    entity_type: str,
    entity_id: str
) -> List[Comment]:
    """Get all comments for a task or project."""
    init_comments_table(conn)
    
    c = conn.cursor()
    c.execute("""
        SELECT id, entity_type, entity_id, author, content, mentions, created_at
        FROM comments
        WHERE entity_type = ? AND entity_id = ?
        ORDER BY created_at ASC
    """, (entity_type, entity_id))
    
    comments = []
    for row in c.fetchall():
        mentions = None
        if row["mentions"]:
            import json
            try:
                mentions = json.loads(row["mentions"])
            except Exception:
                pass
        
        comments.append(Comment(
            id=row["id"],
            entity_type=row["entity_type"],
            entity_id=row["entity_id"],
            author=row["author"],
            content=row["content"],
            mentions=mentions,
            created_at=row["created_at"]
        ))
    
    return comments


def delete_comment(conn: sqlite3.Connection, comment_id: int) -> bool:
    """Delete a comment."""
    init_comments_table(conn)
    
    c = conn.cursor()
    c.execute("DELETE FROM comments WHERE id = ?", (comment_id,))
    conn.commit()
    return c.rowcount > 0


def get_comment_count(conn: sqlite3.Connection, entity_type: str, entity_id: str) -> int:
    """Get the number of comments for an entity."""
    init_comments_table(conn)
    
    c = conn.cursor()
    c.execute("""
        SELECT COUNT(*) as count
        FROM comments
        WHERE entity_type = ? AND entity_id = ?
    """, (entity_type, entity_id))
    
    row = c.fetchone()
    return row["count"] if row else 0


def extract_mentions(content: str) -> List[str]:
    """Extract @mentions from comment content."""
    import re
    mentions = re.findall(r'@(\w+)', content)
    # Filter to valid personas
    valid_personas = ["Chris", "AIC", "Aria", "Sora"]
    return [m for m in mentions if m in valid_personas]

