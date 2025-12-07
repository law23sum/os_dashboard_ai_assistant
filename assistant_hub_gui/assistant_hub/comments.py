"""Comments and discussions system for tasks and projects."""

import sqlite3
import re
from datetime import datetime
from typing import List, Optional, Dict
from dataclasses import dataclass

from .db import PERSONAS


@dataclass
class Comment:
    """A comment on a task or project."""
    id: int
    entity_type: str  # "task" or "project"
    entity_id: str  # Task ID or project name
    author: str
    content: str
    created_at: str
    mentions: List[str] = None  # Extracted @mentions
    
    def __post_init__(self):
        if self.mentions is None:
            self.mentions = extract_mentions(self.content)


def extract_mentions(text: str) -> List[str]:
    """Extract @mentions from text.
    
    Returns list of mentioned persona names (without @ symbol).
    """
    mentions = []
    # Pattern to match @PersonaName
    pattern = r'@(\w+)'
    matches = re.findall(pattern, text)
    
    for match in matches:
        # Check if it's a valid persona
        if match in PERSONAS:
            if match not in mentions:
                mentions.append(match)
    
    return mentions


def add_comment(
    conn: sqlite3.Connection,
    entity_type: str,
    entity_id: str,
    author: str,
    content: str
) -> int:
    """Add a comment to a task or project.
    
    Args:
        conn: Database connection
        entity_type: "task" or "project"
        entity_id: Task ID (as string) or project name
        author: Author name (should be in PERSONAS)
        content: Comment content
    
    Returns:
        Comment ID
    """
    if entity_type not in ["task", "project"]:
        raise ValueError("entity_type must be 'task' or 'project'")
    
    if author not in PERSONAS:
        author = "Chris"  # Default to Chris if invalid
    
    created_at = datetime.now().isoformat(timespec="seconds")
    
    c = conn.cursor()
    c.execute("""
        INSERT INTO comments (entity_type, entity_id, author, content, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (entity_type, str(entity_id), author, content, created_at))
    
    conn.commit()
    return c.lastrowid


def get_comments(
    conn: sqlite3.Connection,
    entity_type: str,
    entity_id: str
) -> List[Comment]:
    """Get all comments for a task or project.
    
    Args:
        conn: Database connection
        entity_type: "task" or "project"
        entity_id: Task ID (as string) or project name
    
    Returns:
        List of Comment objects, ordered by creation time (oldest first)
    """
    c = conn.cursor()
    c.execute("""
        SELECT id, entity_type, entity_id, author, content, created_at
        FROM comments
        WHERE entity_type = ? AND entity_id = ?
        ORDER BY created_at ASC
    """, (entity_type, str(entity_id)))
    
    rows = c.fetchall()
    comments = []
    for row in rows:
        comment = Comment(
            id=row["id"],
            entity_type=row["entity_type"],
            entity_id=row["entity_id"],
            author=row["author"],
            content=row["content"],
            created_at=row["created_at"]
        )
        comments.append(comment)
    
    return comments


def get_comment(conn: sqlite3.Connection, comment_id: int) -> Optional[Comment]:
    """Get a specific comment by ID."""
    c = conn.cursor()
    c.execute("""
        SELECT id, entity_type, entity_id, author, content, created_at
        FROM comments
        WHERE id = ?
    """, (comment_id,))
    
    row = c.fetchone()
    if not row:
        return None
    
    return Comment(
        id=row["id"],
        entity_type=row["entity_type"],
        entity_id=row["entity_id"],
        author=row["author"],
        content=row["content"],
        created_at=row["created_at"]
    )


def delete_comment(conn: sqlite3.Connection, comment_id: int) -> bool:
    """Delete a comment."""
    c = conn.cursor()
    c.execute("DELETE FROM comments WHERE id = ?", (comment_id,))
    conn.commit()
    return c.rowcount > 0


def get_comments_by_author(
    conn: sqlite3.Connection,
    author: str,
    limit: Optional[int] = None
) -> List[Comment]:
    """Get all comments by a specific author."""
    c = conn.cursor()
    query = """
        SELECT id, entity_type, entity_id, author, content, created_at
        FROM comments
        WHERE author = ?
        ORDER BY created_at DESC
    """
    if limit:
        query += f" LIMIT {limit}"
    
    c.execute(query, (author,))
    rows = c.fetchall()
    
    comments = []
    for row in rows:
        comment = Comment(
            id=row["id"],
            entity_type=row["entity_type"],
            entity_id=row["entity_id"],
            author=row["author"],
            content=row["content"],
            created_at=row["created_at"]
        )
        comments.append(comment)
    
    return comments


def get_mentions_for_persona(
    conn: sqlite3.Connection,
    persona: str
) -> List[Comment]:
    """Get all comments that mention a specific persona."""
    c = conn.cursor()
    c.execute("""
        SELECT id, entity_type, entity_id, author, content, created_at
        FROM comments
        WHERE content LIKE ?
        ORDER BY created_at DESC
    """, (f"%@{persona}%",))
    
    rows = c.fetchall()
    comments = []
    for row in rows:
        comment = Comment(
            id=row["id"],
            entity_type=row["entity_type"],
            entity_id=row["entity_id"],
            author=row["author"],
            content=row["content"],
            created_at=row["created_at"]
        )
        # Only include if actually mentions the persona
        if persona in comment.mentions:
            comments.append(comment)
    
    return comments



