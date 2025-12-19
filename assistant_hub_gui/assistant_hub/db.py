#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import sqlite3
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from assistant_hub.config import DB_PATH, ensure_data_directories

ensure_data_directories()
DB_FILE = str(DB_PATH)

PERSONAS = ["Chris", "AIC", "Aria", "Sora"]
PERSONA_ROLES = {
    "Chris": "Human Owner / Primary User",
    "AIC": "Auditor – reviews, checks, cross-validates",
    "Aria": "Assistant – daily flow, tasks, priorities",
    "Sora": "Archive – long-term structure, history, references",
}

STATUS_OPTIONS = ["TODO", "IN_PROGRESS", "BLOCKED", "DONE"]
PRIORITY_OPTIONS = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
OPERATION_STATUS_OPTIONS = ["queued", "running", "succeeded", "failed", "needs_review"]
DATE_FORMAT = "%Y-%m-%d"

CHAT_ROLES = ["user", "assistant", "system", "tool"]
CHAT_MESSAGE_KINDS = ["chat", "terminal", "terminal_result", "file", "tool_result"]
SECURITY_STATUS_CHOICES = ["secure", "vulnerable", "exploited", "offline"]
CHANGE_PERMISSION_MODES = ["auto", "ask", "ask_when_unsure"]
CONTINUITY_MODES = ["full", "automation-off", "read-only"]
RISK_APPETITE_MODES = ["conservative", "balanced", "progressive"]

DEFAULT_FETCH_PREFERENCES = {
    "notes": True,
    "calendar": True,
    "mail": False,
    "files": False,
}


GOVERNANCE_BANNER = (
    "every AI edit is tracked | every change is diffed | every document has a version "
    "history | every operation has a timestamp | every action is reversible | every "
    "output is accountable"
)

OPERATING_ROLES = (
    "OneNote becomes the living structured memory; Word becomes the formatted deliverable "
    "engine; Excel becomes the analytical substrate; Git becomes the brain stem holding the "
    "lineage of every thought; ChatGPT becomes the reasoning center; Daemons become the "
    "continuous active cortex; AIC/Sora/Aria become the interpretive personalities that guide "
    "knowledge formation"
)

OPERATING_BEHAVIORS = (
    "notices missing documents | drafts proposals | updates reports | summarizes notebooks | "
    "analyzes spreadsheets | reorganizes folders | updates tasks | alerts the user when "
    "something's outdated | tracks version history | suggests improvements | predicts next "
    "steps | executes workflows"
)


@dataclass
class Task:
    id: int
    title: str
    project: str = "General"
    status: str = "TODO"
    priority: str = "MEDIUM"
    due_date: Optional[str] = ""
    notes: str = ""
    owner: str = "Chris"
    created_at: str = datetime.now().isoformat(timespec="seconds")
    # New fields for task automation
    depends_on: Optional[int] = None  # ID of task this depends on
    recurrence_pattern: Optional[str] = None  # e.g., "daily", "weekly", "monthly"
    recurrence_end: Optional[str] = None  # End date for recurrence
    time_estimated: Optional[int] = None  # Estimated time in minutes
    time_logged: Optional[int] = None  # Logged time in minutes
    template_id: Optional[str] = None  # Reference to task template


@dataclass
class Project:
    name: str
    description: str = ""
    status: str = "active"
    priority: str = "MEDIUM"
    order_num: int = 0


@dataclass
class ChatMessage:
    id: int
    persona: str
    role: str = "user"
    kind: str = "chat"
    content: str = ""
    created_at: str = datetime.now().isoformat(timespec="seconds")


@dataclass
class AssistantState:
    tasks: List[Task]
    projects: List[Project]
    chat_messages: List[ChatMessage] = field(default_factory=list)
    active_persona: str = "AIC"


@dataclass
class Settings:
    theme: str = "plain"  # plain | light | dark
    default_view: str = "dashboard"  # dashboard | tasks | projects
    show_system_status: bool = True  # show CPU/RAM/Disk in dashboard
    font_scale: str = "medium"  # small | medium | large
    data_preferences: Dict[str, bool] = field(
        default_factory=lambda: DEFAULT_FETCH_PREFERENCES.copy()
    )
    change_permission_mode: str = "ask_when_unsure"  # auto | ask | ask_when_unsure
    continuity_mode: str = "full"  # full | automation-off | read-only
    risk_appetite: str = "balanced"  # conservative | balanced | progressive
    auto_overwrite: bool = True  # legacy flag retained for backward compatibility


@dataclass
class SecurityStatus:
    status: str = "offline"
    message: str = "Telemetry not available yet."
    updated_at: str = ""
    source: str = "mac_guard"


@dataclass
class ExternalConnection:
    service: str
    username: str = ""
    connected: bool = False
    last_login: Optional[str] = None
    notes: str = ""


@dataclass
class NoteLink:
    """Link between a project and an external integration resource."""
    id: int
    project_id: str  # References Project.name
    integration_type: str  # "onenote" | "excel" | "word" | "filesystem" | ...
    external_id: str  # Page ID, workbook ID, file path, etc.
    title: str = ""
    description: str = ""  # Additional description
    created_at: str = datetime.now().isoformat(timespec="seconds")
    last_synced: Optional[str] = None


@dataclass
class AgentRun:
    """Record of an AI agent action/operation."""
    id: int
    agent: str  # "AIC" | "Sora" | "Aria" | "User"
    action_type: str  # "ONENOTE_CLEANUP" | "EXCEL_SUMMARY" | "WORD_DRAFT" | ...
    input_context: str = ""  # Serialized snippet or description
    output_summary: str = ""
    related_files: str = ""  # JSON array of file paths
    git_commit_hash: Optional[str] = None
    created_at: str = datetime.now().isoformat(timespec="seconds")


@dataclass
class DocumentSample:
    """A materialized sample document definition for every supported file type."""

    id: int
    file_type: str
    title: str
    category: str
    description: str
    sample_content: str
    governance: str
    created_at: str = datetime.now().isoformat(timespec="seconds")


@dataclass
class DocumentOperation:
    """Track AI-driven document operations with governance metadata."""

    id: int
    title: str
    project_id: str
    integration_type: str
    external_id: str
    operation: str
    status: str = "queued"  # queued | running | succeeded | failed | needs_review
    persona: str = "AIC"
    version_tag: Optional[str] = None
    diff_path: Optional[str] = None
    external_company: Optional[str] = None
    started_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    completed_at: Optional[str] = None
    notes: str = ""


@dataclass
class UserAccount:
    """Authenticated user account for multi-tenant web/desktop surfaces."""

    id: str
    email: str
    display_name: str = ""
    password_hash: str = ""
    is_admin: bool = False
    environment: str = "demo"  # demo | prod
    disabled: bool = False
    created_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    last_login: Optional[str] = None


def init_db(db_path: Optional[os.PathLike | str] = None) -> sqlite3.Connection:
    """Initialize the SQLite database (creating tables if needed) and return a connection."""
    target = Path(db_path) if db_path else Path(DB_FILE)
    target.parent.mkdir(parents=True, exist_ok=True)
    
    # Allow use across background worker threads (integrations, daemons, API).
    conn = sqlite3.connect(str(target), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    # ========================================================================
    # PERFORMANCE OPTIMIZATION: Configure SQLite for better performance
    # ========================================================================
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 5000")

    # Enable WAL mode for better concurrency (multiple readers, one writer)
    conn.execute("PRAGMA journal_mode = WAL")

    # Increase cache size for better performance (default is -2000 KB, we set to -10000 KB = 10 MB)
    conn.execute("PRAGMA cache_size = -10000")

    # Use memory for temporary tables
    conn.execute("PRAGMA temp_store = MEMORY")

    # Optimize for write operations
    conn.execute("PRAGMA synchronous = NORMAL")

    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS state_meta (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)

    # ---------------------------------------------------------------------
    # Auth & tenancy tables (web + desktop)
    # ---------------------------------------------------------------------
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            display_name TEXT,
            password_hash TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0,
            environment TEXT DEFAULT 'demo',
            disabled INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            last_login TEXT
        )
        """
    )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS audit_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            event_type TEXT NOT NULL,
            object_type TEXT,
            object_id TEXT,
            ip TEXT,
            user_agent TEXT,
            created_at TEXT NOT NULL,
            metadata_json TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE SET NULL
        )
        """
    )
    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_audit_events_user_time
        ON audit_events(user_id, datetime(created_at) DESC)
        """
    )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS event_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            source TEXT NOT NULL,
            level TEXT NOT NULL,
            message TEXT NOT NULL,
            user_id TEXT,
            thread TEXT,
            process TEXT,
            metadata_json TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE SET NULL
        )
        """
    )
    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_event_log_time
        ON event_log(datetime(timestamp) DESC, id DESC)
        """
    )

    c.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            project TEXT,
            status TEXT,
            priority TEXT,
            due_date TEXT,
            notes TEXT,
            owner TEXT,
            created_at TEXT,
            depends_on INTEGER,
            recurrence_pattern TEXT,
            recurrence_end TEXT,
            time_estimated INTEGER,
            time_logged INTEGER,
            template_id TEXT
        )
    """)
    
    # Add new columns if they don't exist (for existing databases)
    c.execute("PRAGMA table_info(tasks)")
    columns = [row[1] for row in c.fetchall()]
    new_columns = [
        ("depends_on", "INTEGER"),
        ("recurrence_pattern", "TEXT"),
        ("recurrence_end", "TEXT"),
        ("time_estimated", "INTEGER"),
        ("time_logged", "INTEGER"),
        ("template_id", "TEXT"),
    ]
    for col_name, col_type in new_columns:
        if col_name not in columns:
            c.execute(f"ALTER TABLE tasks ADD COLUMN {col_name} {col_type}")

    # Add tenant/user binding
    c.execute("PRAGMA table_info(tasks)")
    columns = [row[1] for row in c.fetchall()]
    if "user_id" not in columns:
        c.execute("ALTER TABLE tasks ADD COLUMN user_id TEXT DEFAULT 'demo'")
    
    # Create task_templates table
    c.execute("""
        CREATE TABLE IF NOT EXISTS task_templates (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            title TEXT NOT NULL,
            project TEXT,
            priority TEXT,
            notes TEXT,
            time_estimated INTEGER,
            created_at TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            name TEXT PRIMARY KEY,
            description TEXT,
            status TEXT,
            priority TEXT,
            order_num INTEGER DEFAULT 0
        )
    """)

    # Add new columns if they don't exist (for existing databases)
    c.execute("PRAGMA table_info(projects)")
    columns = [row[1] for row in c.fetchall()]
    new_columns = [
        ("priority", "TEXT DEFAULT 'MEDIUM'"),
        ("order_num", "INTEGER DEFAULT 0"),
    ]
    for col_name, col_type in new_columns:
        if col_name not in columns:
            c.execute(f"ALTER TABLE projects ADD COLUMN {col_name} {col_type}")

    c.execute("PRAGMA table_info(projects)")
    columns = [row[1] for row in c.fetchall()]
    if "user_id" not in columns:
        c.execute("ALTER TABLE projects ADD COLUMN user_id TEXT DEFAULT 'demo'")

    c.execute("""
        CREATE TABLE IF NOT EXISTS external_sources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            kind TEXT,
            connected INTEGER DEFAULT 1,
            last_sync TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS external_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_id INTEGER,
            external_id TEXT,
            kind TEXT,
            title TEXT,
            data_json TEXT,
            created_at TEXT,
            last_seen_at TEXT,
            FOREIGN KEY(source_id) REFERENCES external_sources(id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            persona TEXT,
            role TEXT,
            kind TEXT,
            content TEXT,
            created_at TEXT
        )
    """)

    c.execute("PRAGMA table_info(chat_messages)")
    columns = [row[1] for row in c.fetchall()]
    if "user_id" not in columns:
        c.execute("ALTER TABLE chat_messages ADD COLUMN user_id TEXT DEFAULT 'demo'")

    c.execute("""
        CREATE TABLE IF NOT EXISTS note_links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id TEXT NOT NULL,
            integration_type TEXT NOT NULL,
            external_id TEXT NOT NULL,
            title TEXT,
            description TEXT,
            created_at TEXT,
            last_synced TEXT,
            FOREIGN KEY(project_id) REFERENCES projects(name)
        )
    """)
    
    # Add description column if it doesn't exist (for existing databases)
    c.execute("PRAGMA table_info(note_links)")
    columns = [row[1] for row in c.fetchall()]
    if "description" not in columns:
        c.execute("ALTER TABLE note_links ADD COLUMN description TEXT DEFAULT ''")
    c.execute("PRAGMA table_info(note_links)")
    columns = [row[1] for row in c.fetchall()]
    if "user_id" not in columns:
        c.execute("ALTER TABLE note_links ADD COLUMN user_id TEXT DEFAULT 'demo'")

    c.execute("""
        CREATE TABLE IF NOT EXISTS agent_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent TEXT NOT NULL,
            action_type TEXT NOT NULL,
            input_context TEXT,
            output_summary TEXT,
            related_files TEXT,
            git_commit_hash TEXT,
            created_at TEXT
        )
    """)

    c.execute("PRAGMA table_info(agent_runs)")
    columns = [row[1] for row in c.fetchall()]
    if "user_id" not in columns:
        c.execute("ALTER TABLE agent_runs ADD COLUMN user_id TEXT DEFAULT 'demo'")

    # Document operations table for AI-driven updates and external sync
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS document_operations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            project_id TEXT NOT NULL,
            integration_type TEXT NOT NULL,
            external_id TEXT NOT NULL,
            operation TEXT NOT NULL,
            status TEXT NOT NULL,
            persona TEXT NOT NULL,
            version_tag TEXT,
            diff_path TEXT,
            external_company TEXT,
            started_at TEXT NOT NULL,
            completed_at TEXT,
            notes TEXT
        )
        """
    )

    c.execute("PRAGMA table_info(document_operations)")
    columns = [row[1] for row in c.fetchall()]
    if "user_id" not in columns:
        c.execute("ALTER TABLE document_operations ADD COLUMN user_id TEXT DEFAULT 'demo'")

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS project_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id TEXT NOT NULL,
            event_type TEXT NOT NULL,
            payload TEXT,
            created_at TEXT NOT NULL,
            hash_prev TEXT,
            hash_curr TEXT
        )
        """
    )

    c.execute("PRAGMA table_info(project_events)")
    columns = [row[1] for row in c.fetchall()]
    if "user_id" not in columns:
        c.execute("ALTER TABLE project_events ADD COLUMN user_id TEXT DEFAULT 'demo'")

    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_document_operations_status
        ON document_operations(status, started_at DESC)
        """
    )
    
    # Create indexes for frequently queried columns to improve performance
    c.execute("""
        CREATE INDEX IF NOT EXISTS idx_tasks_project 
        ON tasks(project)
    """)

    c.execute("""
        CREATE INDEX IF NOT EXISTS idx_tasks_status 
        ON tasks(status)
    """)

    c.execute("""
        CREATE INDEX IF NOT EXISTS idx_tasks_priority 
        ON tasks(priority)
    """)

    c.execute("""
        CREATE INDEX IF NOT EXISTS idx_tasks_created_at 
        ON tasks(created_at DESC)
    """)

    c.execute("""
        CREATE INDEX IF NOT EXISTS idx_tasks_project_status 
        ON tasks(project, status)
    """)

    c.execute("""
        CREATE INDEX IF NOT EXISTS idx_projects_status 
        ON projects(status)
    """)

    c.execute("""
        CREATE INDEX IF NOT EXISTS idx_projects_order 
        ON projects(order_num, name)
    """)

    c.execute("""
        CREATE INDEX IF NOT EXISTS idx_chat_messages_persona 
        ON chat_messages(persona, created_at ASC, id ASC)
    """)

    c.execute("""
        CREATE INDEX IF NOT EXISTS idx_note_links_project 
        ON note_links(project_id)
    """)

    c.execute("""
        CREATE INDEX IF NOT EXISTS idx_note_links_integration 
        ON note_links(integration_type)
    """)

    c.execute("""
        CREATE INDEX IF NOT EXISTS idx_project_events_project 
        ON project_events(project_id, created_at DESC)
    """)

    c.execute("""
        CREATE INDEX IF NOT EXISTS idx_agent_runs_created 
        ON agent_runs(created_at DESC)
    """)

    # Document versions table for tracking document history
    c.execute("""
        CREATE TABLE IF NOT EXISTS document_versions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            note_link_id INTEGER NOT NULL,
            version_number INTEGER NOT NULL,
            file_path TEXT NOT NULL,
            file_size INTEGER,
            checksum TEXT,
            created_at TEXT NOT NULL,
            created_by TEXT,
            description TEXT,
            FOREIGN KEY(note_link_id) REFERENCES note_links(id) ON DELETE CASCADE,
            UNIQUE(note_link_id, version_number)
        )
    """)
    
    # Create index for faster lookups
    c.execute("""
        CREATE INDEX IF NOT EXISTS idx_document_versions_link 
        ON document_versions(note_link_id, version_number DESC)
    """)
    
    # Comments table for tasks and projects
    # Note: No FOREIGN KEY constraint since entity_id can reference either tasks(id) or projects(name)
    # with different types (INTEGER vs TEXT). Application-level integrity is maintained.
    c.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_type TEXT NOT NULL,
            entity_id TEXT NOT NULL,
            author TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    
    # Create index for faster comment lookups
    c.execute("""
        CREATE INDEX IF NOT EXISTS idx_comments_entity 
        ON comments(entity_type, entity_id, created_at DESC)
    """)
    
    # Document templates table
    c.execute("""
        CREATE TABLE IF NOT EXISTS document_templates (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT
        )
    """)
    
    # Create index for document templates
    c.execute("""
        CREATE INDEX IF NOT EXISTS idx_document_templates_category 
        ON document_templates(category)
    """)
    
    # Initialize default document templates
    try:
        from .document_templates import initialize_default_templates
        initialize_default_templates(conn)
    except Exception:
        pass  # Don't fail if templates can't be initialized

    # Document sample definitions for each file type
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS document_samples (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_type TEXT NOT NULL,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            sample_content TEXT,
            governance TEXT,
            created_at TEXT NOT NULL
        )
        """
    )
    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_document_samples_file_type
        ON document_samples(file_type, category)
        """
    )

    try:
        initialize_document_samples(conn)
    # Seed sample document operations so the AI Ops board is never empty
    except Exception:
        pass
    try:
        c.execute("SELECT COUNT(*) as count FROM document_operations")
        row = c.fetchone()
        op_count = row["count"] if row else 0
        if op_count == 0:
            now = datetime.now().isoformat(timespec="seconds")
            seed_operations = [
                (
                    "Proposal drafting daemon",
                    "General",
                    "word",
                    "governance/proposals/proposal_v1.docx",
                    "drafts proposals",
                    "running",
                    "Aria",
                    None,
                    None,
                    "Acme Corp",
                    now,
                    None,
                    "every AI edit is tracked, every change is diffed, every output is accountable",
                ),
                (
                    "Compliance watchdog",
                    "Compliance",
                    "pdf",
                    "regulations/latest_regulation.pdf",
                    "notices missing documents",
                    "queued",
                    "AIC",
                    None,
                    None,
                    "Regulatory Affairs",
                    now,
                    None,
                    "every document has a version history and every action is reversible",
                ),
                (
                    "Notebook curator",
                    "Research",
                    "onenote",
                    "ideas/notebook",
                    "summarizes notebooks",
                    "running",
                    "Sora",
                    None,
                    None,
                    "Internal",
                    now,
                    None,
                    "OneNote becomes the living structured memory; Git holds the lineage",
                ),
                (
                    "Spreadsheet analyst",
                    "Finance",
                    "excel",
                    "models/q4_forecast.xlsx",
                    "analyzes spreadsheets",
                    "needs_review",
                    "AIC",
                    None,
                    None,
                    "Finance Partner",
                    now,
                    None,
                    "Excel becomes the analytical substrate; alerts the user when something's outdated",
                ),
            ]
            c.executemany(
                """
                INSERT INTO document_operations (
                    title, project_id, integration_type, external_id, operation, status, persona,
                    version_tag, diff_path, external_company, started_at, completed_at, notes
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                seed_operations,
            )
    except Exception:
        pass

    # ========================================================================
    # PERFORMANCE OPTIMIZATION: Add indexes for commonly queried columns
    # ========================================================================
    # Index for tasks by status (used in dashboard, task lists)
    c.execute("""
        CREATE INDEX IF NOT EXISTS idx_tasks_status 
        ON tasks(status)
    """)

    # Index for tasks by project (used in project views)
    c.execute("""
        CREATE INDEX IF NOT EXISTS idx_tasks_project 
        ON tasks(project)
    """)

    # Index for tasks by owner (used in persona views)
    c.execute("""
        CREATE INDEX IF NOT EXISTS idx_tasks_owner 
        ON tasks(owner)
    """)

    # Index for tasks by priority (used in filtering)
    c.execute("""
        CREATE INDEX IF NOT EXISTS idx_tasks_priority 
        ON tasks(priority)
    """)

    # Composite index for common queries (status + project)
    c.execute("""
        CREATE INDEX IF NOT EXISTS idx_tasks_status_project 
        ON tasks(status, project)
    """)

    # Index for chat messages by persona (used in chat history)
    c.execute("""
        CREATE INDEX IF NOT EXISTS idx_chat_messages_persona 
        ON chat_messages(persona)
    """)

    # Index for chat messages by created_at for chronological sorting
    c.execute("""
        CREATE INDEX IF NOT EXISTS idx_chat_messages_created_at 
        ON chat_messages(created_at)
    """)

    # Index for note_links by project_id (used in project views)
    c.execute("""
        CREATE INDEX IF NOT EXISTS idx_note_links_project 
        ON note_links(project_id)
    """)

    # Index for document_operations by status (used in operation tracking)
    c.execute("""
        CREATE INDEX IF NOT EXISTS idx_document_operations_status 
        ON document_operations(status)
    """)

    # Check if project_ledger table exists before creating index
    cursor = c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='project_ledger'")
    if cursor.fetchone() is not None:
        # Index for project_ledger by project_id and created_at
        c.execute("""
            CREATE INDEX IF NOT EXISTS idx_project_ledger_project_created 
            ON project_ledger(project_id, created_at DESC)
        """)

    # ========================================================================
    # PERFORMANCE OPTIMIZATION: Add indexes for commonly queried columns
    # ========================================================================
    # Index for tasks by status (used in dashboard, task lists)
    c.execute("""
        CREATE INDEX IF NOT EXISTS idx_tasks_status 
        ON tasks(status)
    """)

    # Index for tasks by project (used in project views)
    c.execute("""
        CREATE INDEX IF NOT EXISTS idx_tasks_project 
        ON tasks(project)
    """)

    # Index for tasks by owner (used in persona views)
    c.execute("""
        CREATE INDEX IF NOT EXISTS idx_tasks_owner 
        ON tasks(owner)
    """)

    # Index for tasks by priority (used in filtering)
    c.execute("""
        CREATE INDEX IF NOT EXISTS idx_tasks_priority 
        ON tasks(priority)
    """)

    # Composite index for common queries (status + project)
    c.execute("""
        CREATE INDEX IF NOT EXISTS idx_tasks_status_project 
        ON tasks(status, project)
    """)

    # Index for chat messages by persona (used in chat history)
    c.execute("""
        CREATE INDEX IF NOT EXISTS idx_chat_messages_persona 
        ON chat_messages(persona)
    """)

    # Index for chat messages by created_at for chronological sorting
    c.execute("""
        CREATE INDEX IF NOT EXISTS idx_chat_messages_created_at 
        ON chat_messages(created_at)
    """)

    # Index for note_links by project_id (used in project views)
    c.execute("""
        CREATE INDEX IF NOT EXISTS idx_note_links_project 
        ON note_links(project_id)
    """)

    # Index for document_operations by status (used in operation tracking)
    c.execute("""
        CREATE INDEX IF NOT EXISTS idx_document_operations_status 
        ON document_operations(status)
    """)

    # Check if project_ledger table exists before creating index
    cursor = c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='project_ledger'")
    if cursor.fetchone() is not None:
        # Index for project_ledger by project_id and created_at
        c.execute("""
            CREATE INDEX IF NOT EXISTS idx_project_ledger_project_created 
            ON project_ledger(project_id, created_at DESC)
        """)
    conn.commit()
    _ensure_bootstrap_accounts(conn)
    return conn


def _bcrypt_hash_password(raw_password: str) -> str:
    """Hash a password for storage (bcrypt)."""
    import bcrypt  # local import to avoid hard dep at module import time

    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(raw_password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def _ensure_bootstrap_accounts(conn: sqlite3.Connection) -> None:
    """Ensure an initial admin + demo user exist (dev-friendly defaults).

    Credentials are controlled via env vars:
    - OSDASH_ADMIN_EMAIL
    - OSDASH_ADMIN_PASSWORD
    - OSDASH_DEMO_EMAIL
    - OSDASH_DEMO_PASSWORD
    """

    admin_id = os.getenv("OSDASH_ADMIN_ID", "admin").strip() or "admin"
    demo_id = os.getenv("OSDASH_DEMO_ID", "demo").strip() or "demo"
    admin_email = os.getenv("OSDASH_ADMIN_EMAIL", "admin@osdash.local").strip().lower()
    admin_password = os.getenv("OSDASH_ADMIN_PASSWORD", "ChangeMeNow!").strip()
    demo_email = os.getenv("OSDASH_DEMO_EMAIL", "demo@osdash.local").strip().lower()
    demo_password = os.getenv("OSDASH_DEMO_PASSWORD", "demo").strip()

    now = datetime.now().isoformat(timespec="seconds")
    cur = conn.cursor()

    def _upsert_user(*, user_id: str, email: str, password: str, is_admin: bool, environment: str) -> None:
        cur.execute("SELECT id FROM users WHERE email = ?", (email,))
        row = cur.fetchone()
        if row:
            return
        cur.execute(
            """
            INSERT INTO users (id, email, display_name, password_hash, is_admin, environment, disabled, created_at, last_login)
            VALUES (?, ?, ?, ?, ?, ?, 0, ?, NULL)
            """,
            (
                user_id,
                email,
                "Admin" if is_admin else "Demo User",
                _bcrypt_hash_password(password),
                1 if is_admin else 0,
                environment,
                now,
            ),
        )

    _upsert_user(user_id=admin_id, email=admin_email, password=admin_password, is_admin=True, environment="prod")
    _upsert_user(user_id=demo_id, email=demo_email, password=demo_password, is_admin=False, environment="demo")
    conn.commit()


def get_meta(conn: sqlite3.Connection, key: str, default: Optional[str] = None) -> Optional[str]:
    c = conn.cursor()
    c.execute("SELECT value FROM state_meta WHERE key = ?", (key,))
    row = c.fetchone()
    if row is None:
        return default
    return row["value"]


def set_meta(conn: sqlite3.Connection, key: str, value: str):
    c = conn.cursor()
    c.execute(
        "INSERT INTO state_meta (key, value) VALUES (?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (key, value),
    )
    conn.commit()


OPENAI_API_KEY_META = "openai.api_key"


def save_openai_api_key(conn: sqlite3.Connection, api_key: str) -> None:
    """Persist the OpenAI API key in the shared metadata table."""
    if not api_key:
        raise ValueError("api_key must be provided")
    set_meta(conn, OPENAI_API_KEY_META, api_key)


def load_openai_api_key(conn: sqlite3.Connection, default: Optional[str] = None) -> Optional[str]:
    """Fetch the OpenAI API key from the database, if present."""
    return get_meta(conn, OPENAI_API_KEY_META, default)


def clear_openai_api_key(conn: sqlite3.Connection) -> None:
    """Remove the stored OpenAI API key."""
    c = conn.cursor()
    c.execute("DELETE FROM state_meta WHERE key = ?", (OPENAI_API_KEY_META,))
    conn.commit()


def load_state(conn: sqlite3.Connection) -> AssistantState:
    c = conn.cursor()

    c.execute("SELECT * FROM tasks")
    tasks_rows = c.fetchall()
    tasks: List[Task] = []
    for r in tasks_rows:
        status = (r["status"] or "TODO").upper()
        if status not in STATUS_OPTIONS:
            status = "TODO"
        priority = (r["priority"] or "MEDIUM").upper()
        if priority not in PRIORITY_OPTIONS:
            priority = "MEDIUM"
        owner = r["owner"] or "Chris"
        if owner not in PERSONAS:
            owner = "Chris"

        # Handle new fields with defaults (sqlite3.Row doesn't have .get(), use try/except)
        try:
            depends_on = r["depends_on"] if r["depends_on"] else None
        except (KeyError, IndexError):
            depends_on = None
        
        try:
            recurrence_pattern = r["recurrence_pattern"] or None
        except (KeyError, IndexError):
            recurrence_pattern = None
        
        try:
            recurrence_end = r["recurrence_end"] or None
        except (KeyError, IndexError):
            recurrence_end = None
        
        try:
            time_estimated = r["time_estimated"] if r["time_estimated"] is not None else None
        except (KeyError, IndexError):
            time_estimated = None
        
        try:
            time_logged = r["time_logged"] if r["time_logged"] is not None else None
        except (KeyError, IndexError):
            time_logged = None
        
        try:
            template_id = r["template_id"] or None
        except (KeyError, IndexError):
            template_id = None
        
        tasks.append(
            Task(
                id=r["id"],
                title=r["title"],
                project=r["project"] or "General",
                status=status,
                priority=priority,
                due_date=r["due_date"] or "",
                notes=r["notes"] or "",
                owner=owner,
                created_at=r["created_at"] or datetime.now().isoformat(timespec="seconds"),
                depends_on=depends_on,
                recurrence_pattern=recurrence_pattern,
                recurrence_end=recurrence_end,
                time_estimated=time_estimated,
                time_logged=time_logged,
                template_id=template_id,
            )
        )

    c.execute("SELECT * FROM projects")
    proj_rows = c.fetchall()
    projects: List[Project] = []
    for r in proj_rows:
        # Check if priority column exists by trying to access it
        try:
            priority = (r["priority"] or "MEDIUM").upper()
        except (KeyError, IndexError):
            priority = "MEDIUM"
        if priority not in PRIORITY_OPTIONS:
            priority = "MEDIUM"

        # Check if order_num column exists by trying to access it
        try:
            order_num = r["order_num"] if r["order_num"] is not None else 0
        except (KeyError, IndexError):
            order_num = 0

        projects.append(
            Project(
                name=r["name"],
                description=r["description"] or "",
                status=r["status"] or "active",
                priority=priority,
                order_num=order_num,
            )
        )

    c.execute("SELECT * FROM chat_messages ORDER BY id ASC")
    chat_rows = c.fetchall()
    chat_messages: List[ChatMessage] = []
    for r in chat_rows:
        persona = r["persona"] or PERSONAS[0]
        if persona not in PERSONAS:
            persona = PERSONAS[0]
        role = (r["role"] or "user").lower()
        if role not in CHAT_ROLES:
            role = "user"
        kind = (r["kind"] or "chat").lower()
        if kind not in CHAT_MESSAGE_KINDS:
            kind = "chat"
        chat_messages.append(
            ChatMessage(
                id=r["id"],
                persona=persona,
                role=role,
                kind=kind,
                content=r["content"] or "",
                created_at=r["created_at"] or datetime.now().isoformat(timespec="seconds"),
            )
        )

    active_persona = get_meta(conn, "active_persona", "AIC") or "AIC"
    if active_persona not in PERSONAS:
        active_persona = "AIC"

    return AssistantState(
        tasks=tasks,
        projects=projects,
        chat_messages=chat_messages,
        active_persona=active_persona,
    )


def load_settings(conn: sqlite3.Connection) -> Settings:
    theme = get_meta(conn, "setting.theme", "plain") or "plain"
    default_view = get_meta(conn, "setting.default_view", "dashboard") or "dashboard"
    show_system_status_raw = get_meta(conn, "setting.show_system_status", "1") or "1"
    show_system_status = show_system_status_raw == "1"
    font_scale = get_meta(conn, "setting.font_scale", "medium") or "medium"
    data_pref_raw = get_meta(conn, "setting.data_preferences", None)
    data_preferences = DEFAULT_FETCH_PREFERENCES.copy()
    if data_pref_raw:
        try:
            parsed = json.loads(data_pref_raw)
            if isinstance(parsed, dict):
                for key, val in parsed.items():
                    data_preferences[key] = bool(val)
        except json.JSONDecodeError:
            pass

    change_permission_mode = (
        get_meta(conn, "setting.change_permission_mode", "ask_when_unsure")
        or "ask_when_unsure"
    )
    if change_permission_mode not in CHANGE_PERMISSION_MODES:
        change_permission_mode = "ask_when_unsure"

    continuity_mode = get_meta(conn, "setting.continuity_mode", "full") or "full"
    if continuity_mode not in CONTINUITY_MODES:
        continuity_mode = "full"

    risk_appetite = get_meta(conn, "setting.risk_appetite", "balanced") or "balanced"
    if risk_appetite not in RISK_APPETITE_MODES:
        risk_appetite = "balanced"

    auto_overwrite_raw = get_meta(conn, "setting.auto_overwrite", None)
    auto_overwrite = (
        auto_overwrite_raw == "1"
        if auto_overwrite_raw is not None
        else change_permission_mode == "auto"
    )

    return Settings(
        theme=theme,
        default_view=default_view,
        show_system_status=show_system_status,
        font_scale=font_scale,
        data_preferences=data_preferences,
        change_permission_mode=change_permission_mode,
        continuity_mode=continuity_mode,
        risk_appetite=risk_appetite,
        auto_overwrite=auto_overwrite,
    )


def save_settings(conn: sqlite3.Connection, settings: Settings):
    set_meta(conn, "setting.theme", settings.theme)
    set_meta(conn, "setting.default_view", settings.default_view)
    set_meta(
        conn, "setting.show_system_status", "1" if settings.show_system_status else "0"
    )
    set_meta(conn, "setting.font_scale", settings.font_scale)
    set_meta(
        conn,
        "setting.data_preferences",
        json.dumps(settings.data_preferences, ensure_ascii=False),
    )
    set_meta(
        conn,
        "setting.change_permission_mode",
        settings.change_permission_mode,
    )
    set_meta(conn, "setting.continuity_mode", settings.continuity_mode)
    set_meta(conn, "setting.risk_appetite", settings.risk_appetite)
    set_meta(
        conn,
        "setting.auto_overwrite",
        "1" if settings.auto_overwrite else "0",
    )


def save_active_persona(conn: sqlite3.Connection, state: AssistantState):
    set_meta(conn, "active_persona", state.active_persona)


def load_security_status(conn: sqlite3.Connection) -> SecurityStatus:
    status = (get_meta(conn, "security.status", "offline") or "offline").lower()
    if status not in SECURITY_STATUS_CHOICES:
        status = "offline"
    message = get_meta(conn, "security.message", "Telemetry not available yet.") or "Telemetry not available yet."
    updated_at = get_meta(conn, "security.updated_at", "") or ""
    source = get_meta(conn, "security.source", "mac_guard") or "mac_guard"
    return SecurityStatus(status=status, message=message, updated_at=updated_at, source=source)


def save_security_status(conn: sqlite3.Connection, status: SecurityStatus):
    set_meta(conn, "security.status", status.status)
    set_meta(conn, "security.message", status.message)
    set_meta(conn, "security.updated_at", status.updated_at)
    set_meta(conn, "security.source", status.source)


def db_upsert_project(conn: sqlite3.Connection, proj: Optional[Project] = None, **kwargs):
    c = conn.cursor()
    # Check if new columns exist, if not add them
    c.execute("PRAGMA table_info(projects)")
    columns = [row[1] for row in c.fetchall()]
    if "priority" not in columns:
        c.execute("ALTER TABLE projects ADD COLUMN priority TEXT DEFAULT 'MEDIUM'")
        conn.commit()
    if "order_num" not in columns:
        c.execute("ALTER TABLE projects ADD COLUMN order_num INTEGER DEFAULT 0")
        conn.commit()

    if proj is None:
        proj = Project(**kwargs)

    # Default user_id fallback for older callers
    user_id = getattr(proj, "user_id", None) or kwargs.get("user_id") or "demo"

    c.execute(
        """
        INSERT INTO projects (name, description, status, priority, order_num, user_id)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(name) DO UPDATE SET
            description = excluded.description,
            status = excluded.status,
            priority = excluded.priority,
            order_num = excluded.order_num,
            user_id = excluded.user_id
        """,
        (proj.name, proj.description, proj.status, proj.priority, proj.order_num, user_id),
    )
    conn.commit()


def db_delete_project(conn: sqlite3.Connection, name: str):
    c = conn.cursor()
    c.execute("DELETE FROM projects WHERE name = ?", (name,))
    conn.commit()


def db_insert_task(conn: sqlite3.Connection, t: Optional[Task] = None, **kwargs) -> int:
    if t is None:
        # id is auto-increment; placeholder 0
        t = Task(
            id=0,
            title=kwargs.get("title", ""),
            project=kwargs.get("project", "General"),
            status=kwargs.get("status", "TODO"),
            priority=kwargs.get("priority", "MEDIUM"),
            due_date=kwargs.get("due_date", "") or "",
            notes=kwargs.get("notes", "") or "",
            owner=kwargs.get("owner", "Chris"),
            created_at=kwargs.get("created_at", datetime.now().isoformat(timespec="seconds")),
            depends_on=kwargs.get("depends_on"),
            recurrence_pattern=kwargs.get("recurrence_pattern"),
            recurrence_end=kwargs.get("recurrence_end"),
            time_estimated=kwargs.get("time_estimated"),
            time_logged=kwargs.get("time_logged"),
            template_id=kwargs.get("template_id"),
        )
    user_id = getattr(t, "user_id", None) or kwargs.get("user_id") or "demo"
    c = conn.cursor()
    c.execute(
        """
        INSERT INTO tasks
        (title, project, status, priority, due_date, notes, owner, created_at,
         depends_on, recurrence_pattern, recurrence_end, time_estimated, time_logged, template_id, user_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            t.title,
            t.project,
            t.status,
            t.priority,
            t.due_date,
            t.notes,
            t.owner,
            t.created_at,
            t.depends_on,
            t.recurrence_pattern,
            t.recurrence_end,
            t.time_estimated,
            t.time_logged,
            t.template_id,
            user_id,
        ),
    )
    conn.commit()
    return c.lastrowid


def db_update_task(conn: sqlite3.Connection, t: Optional[Task] = None, task_id: Optional[int] = None, **kwargs):
    if t is None:
        if task_id is None:
            raise ValueError("task_id is required when not providing a Task")
        # Load existing then apply updates
        cur = conn.cursor()
        row = cur.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        if not row:
            raise ValueError("Task not found")
        t = Task(
            id=row["id"],
            title=row["title"],
            project=row["project"] or "General",
            status=row["status"] or "TODO",
            priority=row["priority"] or "MEDIUM",
            due_date=row["due_date"] or "",
            notes=row["notes"] or "",
            owner=row["owner"] or "Chris",
            created_at=row["created_at"] or datetime.now().isoformat(timespec="seconds"),
            depends_on=row["depends_on"] if "depends_on" in row.keys() else None,
            recurrence_pattern=row["recurrence_pattern"] if "recurrence_pattern" in row.keys() else None,
            recurrence_end=row["recurrence_end"] if "recurrence_end" in row.keys() else None,
            time_estimated=row["time_estimated"] if "time_estimated" in row.keys() else None,
            time_logged=row["time_logged"] if "time_logged" in row.keys() else None,
            template_id=row["template_id"] if "template_id" in row.keys() else None,
        )
        for key, value in kwargs.items():
            if hasattr(t, key):
                setattr(t, key, value)
    c = conn.cursor()
    c.execute(
        """
        UPDATE tasks
        SET title = ?, project = ?, status = ?, priority = ?,
            due_date = ?, notes = ?, owner = ?,
            depends_on = ?, recurrence_pattern = ?, recurrence_end = ?,
            time_estimated = ?, time_logged = ?, template_id = ?
        WHERE id = ?
        """,
        (t.title, t.project, t.status, t.priority, t.due_date, t.notes, t.owner,
         t.depends_on, t.recurrence_pattern, t.recurrence_end,
         t.time_estimated, t.time_logged, t.template_id, t.id),
    )
    conn.commit()


def db_delete_task(conn: sqlite3.Connection, task_id: int):
    c = conn.cursor()
    c.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()


def db_insert_chat_message(conn: sqlite3.Connection, msg: ChatMessage) -> int:
    c = conn.cursor()
    created_at = msg.created_at or datetime.now().isoformat(timespec="seconds")
    c.execute(
        """
        INSERT INTO chat_messages (persona, role, kind, content, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (msg.persona, msg.role, msg.kind, msg.content, created_at),
    )
    conn.commit()
    return c.lastrowid


def db_clear_chat_history(conn: sqlite3.Connection, persona: Optional[str] = None):
    c = conn.cursor()
    if persona:
        c.execute("DELETE FROM chat_messages WHERE persona = ?", (persona,))
    else:
        c.execute("DELETE FROM chat_messages")
    conn.commit()


# Azure/Microsoft Graph credentials storage
def save_azure_credentials(conn: sqlite3.Connection, tenant_id: str, client_id: str, client_secret: str):
    """Save Azure credentials to the database."""
    set_meta(conn, "azure.tenant_id", tenant_id)
    set_meta(conn, "azure.client_id", client_id)
    set_meta(conn, "azure.client_secret", client_secret)


def load_azure_credentials(conn: sqlite3.Connection) -> Optional[Dict[str, str]]:
    """Load Azure credentials from the database. Returns dict with tenant_id, client_id, client_secret or None."""
    tenant_id = get_meta(conn, "azure.tenant_id")
    client_id = get_meta(conn, "azure.client_id")
    client_secret = get_meta(conn, "azure.client_secret")
    
    if tenant_id and client_id and client_secret:
        return {
            "tenant_id": tenant_id,
            "client_id": client_id,
            "client_secret": client_secret,
        }
    return None


def delete_azure_credentials(conn: sqlite3.Connection):
    """Delete Azure credentials from the database."""
    c = conn.cursor()
    c.execute("DELETE FROM state_meta WHERE key IN ('azure.tenant_id', 'azure.client_id', 'azure.client_secret')")
    conn.commit()


def ensure_external_source(conn: sqlite3.Connection, name: str, kind: str) -> int:
    c = conn.cursor()
    c.execute("SELECT id FROM external_sources WHERE name = ?", (name,))
    row = c.fetchone()
    now = datetime.now().isoformat(timespec="seconds")
    if row:
        return row["id"]

    c.execute(
        """
        INSERT INTO external_sources (name, kind, connected, last_sync)
        VALUES (?, ?, 1, ?)
        """,
        (name, kind, now),
    )
    conn.commit()
    return c.lastrowid


def record_external_item(
    conn: sqlite3.Connection,
    source_name: str,
    source_kind: str,
    external_id: str,
    item_kind: str,
    title: str,
    data: Dict[str, Any],
):
    source_id = ensure_external_source(conn, source_name, source_kind)
    now = datetime.now().isoformat(timespec="seconds")
    data_json = json.dumps(data, ensure_ascii=False)

    c = conn.cursor()
    c.execute(
        """
        SELECT id FROM external_items
        WHERE source_id = ? AND external_id = ?
        """,
        (source_id, external_id),
    )
    row = c.fetchone()
    if row:
        c.execute(
            """
            UPDATE external_items
            SET kind = ?, title = ?, data_json = ?, last_seen_at = ?
            WHERE id = ?
            """,
            (item_kind, title, data_json, now, row["id"]),
        )
    else:
        c.execute(
            """
            INSERT INTO external_items
            (source_id, external_id, kind, title, data_json, created_at, last_seen_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (source_id, external_id, item_kind, title, data_json, now, now),
        )
    conn.commit()


def load_external_connections(conn: sqlite3.Connection) -> Dict[str, ExternalConnection]:
    raw = get_meta(conn, "external.connections", "{}") or "{}"
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        payload = {}

    connections: Dict[str, ExternalConnection] = {}
    for service, data in payload.items():
        if isinstance(data, dict):
            connections[service] = ExternalConnection(
                service=service,
                username=data.get("username", ""),
                connected=bool(data.get("connected", False)),
                last_login=data.get("last_login"),
                notes=data.get("notes") or data.get("scope_description", ""),
            )
    return connections


def save_external_connections(
    conn: sqlite3.Connection, connections: Dict[str, ExternalConnection]
):
    payload: Dict[str, Any] = {}
    for service, conn_obj in connections.items():
        payload[service] = {
            "username": conn_obj.username,
            "connected": conn_obj.connected,
            "last_login": conn_obj.last_login,
            "notes": conn_obj.notes,
        }
    set_meta(conn, "external.connections", json.dumps(payload, ensure_ascii=False))


# Document Operation helpers -------------------------------------------------


def db_record_document_operation(
    conn: sqlite3.Connection,
    title: str,
    project_id: str,
    integration_type: str,
    external_id: str,
    operation: str,
    status: str = "queued",
    persona: str = "AIC",
    version_tag: Optional[str] = None,
    diff_path: Optional[str] = None,
    external_company: Optional[str] = None,
    notes: str = "",
) -> int:
    """Record a document operation so it can be surfaced in the GUI/API."""

    if status not in OPERATION_STATUS_OPTIONS:
        status = "queued"

    now = datetime.now().isoformat(timespec="seconds")
    c = conn.cursor()
    c.execute(
        """
        INSERT INTO document_operations (
            title, project_id, integration_type, external_id, operation, status, persona,
            version_tag, diff_path, external_company, started_at, completed_at, notes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            title,
            project_id,
            integration_type,
            external_id,
            operation,
            status,
            persona,
            version_tag,
            diff_path,
            external_company,
            now,
            None,
            notes,
        ),
    )
    conn.commit()
    return c.lastrowid


def db_update_document_operation_status(
    conn: sqlite3.Connection,
    operation_id: int,
    status: Optional[str] = None,
    diff_path: Optional[str] = None,
    version_tag: Optional[str] = None,
    external_company: Optional[str] = None,
    notes: Optional[str] = None,
    mark_complete: bool = False,
):
    """Update status/metadata for a document operation."""

    updates = []
    params: List[Any] = []

    if status:
        if status not in OPERATION_STATUS_OPTIONS:
            status = "needs_review"
        updates.append("status = ?")
        params.append(status)

    if diff_path is not None:
        updates.append("diff_path = ?")
        params.append(diff_path)

    if version_tag is not None:
        updates.append("version_tag = ?")
        params.append(version_tag)

    if external_company is not None:
        updates.append("external_company = ?")
        params.append(external_company)

    if notes is not None:
        updates.append("notes = ?")
        params.append(notes)

    if mark_complete:
        updates.append("completed_at = ?")
        params.append(datetime.now().isoformat(timespec="seconds"))

    if not updates:
        return

    params.append(operation_id)
    query = f"UPDATE document_operations SET {', '.join(updates)} WHERE id = ?"
    c = conn.cursor()
    c.execute(query, params)
    conn.commit()


def db_list_document_operations(
    conn: sqlite3.Connection,
    limit: int = 50,
    status: Optional[str] = None,
    integration_type: Optional[str] = None,
) -> List[DocumentOperation]:
    """Return recent document operations for dashboards and APIs."""

    c = conn.cursor()
    query = "SELECT * FROM document_operations WHERE 1=1"
    params: List[Any] = []

    if status and status in OPERATION_STATUS_OPTIONS:
        query += " AND status = ?"
        params.append(status)

    if integration_type:
        query += " AND integration_type = ?"
        params.append(integration_type)

    query += " ORDER BY started_at DESC"
    query += " LIMIT ?"
    params.append(limit)

    c.execute(query, params)
    rows = c.fetchall()
    operations: List[DocumentOperation] = []
    for row in rows:
        operations.append(
            DocumentOperation(
                id=row["id"],
                title=row["title"],
                project_id=row["project_id"],
                integration_type=row["integration_type"],
                external_id=row["external_id"],
                operation=row["operation"],
                status=row["status"],
                persona=row["persona"],
                version_tag=row["version_tag"],
                diff_path=row["diff_path"],
                external_company=row["external_company"],
                started_at=row["started_at"],
                completed_at=row["completed_at"],
                notes=row["notes"] or "",
            )
        )

    return operations


# Note Links (Document Management) Functions
def db_create_note_link(
    conn: sqlite3.Connection,
    project_id: str,
    integration_type: str,
    external_id: str,
    title: str = "",
    description: str = ""
) -> int:
    """Create a note link (document reference) in the database."""
    c = conn.cursor()
    created_at = datetime.now().isoformat(timespec="seconds")
    c.execute(
        """
        INSERT INTO note_links (project_id, integration_type, external_id, title, description, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (project_id, integration_type, external_id, title, description, created_at),
    )
    conn.commit()
    return c.lastrowid


def db_get_note_links(
    conn: sqlite3.Connection,
    project_id: Optional[str] = None,
    integration_type: Optional[str] = None
) -> List[NoteLink]:
    """Get note links, optionally filtered by project and/or integration type."""
    c = conn.cursor()
    query = "SELECT * FROM note_links WHERE 1=1"
    params = []
    
    if project_id:
        query += " AND project_id = ?"
        params.append(project_id)
    
    if integration_type:
        query += " AND integration_type = ?"
        params.append(integration_type)
    
    query += " ORDER BY created_at DESC"
    
    c.execute(query, params)
    rows = c.fetchall()
    
    links = []
    for r in rows:
        links.append(
            NoteLink(
                id=r["id"],
                project_id=r["project_id"],
                integration_type=r["integration_type"],
                external_id=r["external_id"],
                title=r["title"] or "",
                description=r["description"] or "",
                created_at=r["created_at"] or datetime.now().isoformat(timespec="seconds"),
                last_synced=r["last_synced"],
            )
        )
    return links


def db_get_note_link(conn: sqlite3.Connection, link_id: int) -> Optional[NoteLink]:
    """Get a single note link by ID."""
    c = conn.cursor()
    c.execute("SELECT * FROM note_links WHERE id = ?", (link_id,))
    row = c.fetchone()
    if not row:
        return None
    
    return NoteLink(
        id=row["id"],
        project_id=row["project_id"],
        integration_type=row["integration_type"],
        external_id=row["external_id"],
        title=row["title"] or "",
        description=row["description"] or "",
        created_at=row["created_at"] or datetime.now().isoformat(timespec="seconds"),
        last_synced=row["last_synced"],
    )


def db_update_note_link(
    conn: sqlite3.Connection,
    link_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None
):
    """Update a note link's metadata."""
    c = conn.cursor()
    updates = []
    params = []
    
    if title is not None:
        updates.append("title = ?")
        params.append(title)
    
    if description is not None:
        updates.append("description = ?")
        params.append(description)
    
    if not updates:
        return
    
    params.append(link_id)
    query = f"UPDATE note_links SET {', '.join(updates)} WHERE id = ?"
    c.execute(query, params)
    conn.commit()


def db_delete_note_link(conn: sqlite3.Connection, link_id: int):
    """Delete a note link from the database."""
    c = conn.cursor()
    c.execute("DELETE FROM note_links WHERE id = ?", (link_id,))
    conn.commit()


# ---------------- Document sample helpers -----------------

DEFAULT_DOCUMENT_SAMPLES = [
    {
        "file_type": "csv",
        "title": "Compliance Report Snapshot",
        "category": "compliance reports",
        "description": "CSV seed capturing auditable compliance metrics and lineage cues.",
        "sample_content": (
            "section,metric,value,owner,version,governance\n"
            "Controls,Passed,24,Chris,v1,Every AI edit is tracked\n"
            "Exceptions,Open,3,AIC,v1,Every change is diffed\n"
            "Notes,Ledger,{governance},Sora,v1,{roles}"
        ),
    },
    {
        "file_type": "json",
        "title": "Risk Assessment Outline",
        "category": "risk assessments",
        "description": "JSON blueprint for AI-led risk reviews with provenance and personas.",
        "sample_content": (
            "{{\n"
            "  \"title\": \"Risk Assessment\",\n"
            "  \"versioning\": \"{governance}\",\n"
            "  \"operating_model\": \"{roles}\",\n"
            "  \"behaviors\": \"{behaviors}\",\n"
            "  \"sections\": [\"briefs\", \"proposals\", \"compliance reports\", \"patient summaries\", \"risk assessments\", \"regulatory filings\", \"engineering specs\", \"technical documents\", \"product updates\", \"operational manuals\"]\n"
            "}}"
        ),
    },
    {
        "file_type": "pdf",
        "title": "Regulatory Filing Shell",
        "category": "regulatory filings",
        "description": "Text payload ready to be exported as PDF with governance header.",
        "sample_content": (
            "Regulatory Filing (Sample)\n"
            "Governance: {governance}\n"
            "Roles: {roles}\n"
            "Behaviors: {behaviors}\n"
            "Sections covered: compliance reports, patient summaries, risk assessments, regulatory filings,\n"
            "engineering specs, technical documents, product updates, operational manuals."
        ),
    },
    {
        "file_type": "xlsx",
        "title": "Operational Metrics Workbook",
        "category": "operational manuals",
        "description": "Workbook-style text scaffold the AI can expand into XLSX.",
        "sample_content": (
            "Sheet: Executive Dashboard\n"
            "Metric,Owner,Value,Last Updated\n"
            "AI Drafted Proposals,Aria,7,Today\n"
            "Notebook Summaries,Sora,12,Today\n"
            "Workflow Executions,AIC,5,Today\n"
            "Governance,{governance},{roles},Now\n"
        ),
    },
    {
        "file_type": "docx",
        "title": "Governed Brief Template",
        "category": "briefs",
        "description": "Docx-style outline for briefs, proposals, and updates with AI accountability.",
        "sample_content": (
            "# Brief / Proposal / Update\n"
            "Governance: {governance}\n"
            "Operating Model: {roles}\n"
            "Behaviors: {behaviors}\n\n"
            "Use for: briefs, proposals, compliance reports, patient summaries, risk assessments, regulatory filings,\n"
            "engineering specs, technical documents, product updates, operational manuals."
        ),
    },
    {
        "file_type": "txt",
        "title": "Notes Inbox Seed",
        "category": "notes",
        "description": "Lightweight TXT starter for raw ideas that daemons will promote into formal docs.",
        "sample_content": (
            "Raw ideas captured here.\n"
            "Governance: {governance}\n"
            "Roles: {roles}\n"
            "Behaviors: {behaviors}\n"
            "The assistant notices missing documents, drafts proposals, updates reports, summarizes notebooks,"
            " analyzes spreadsheets, reorganizes folders, updates tasks, alerts the user when something's outdated,"
            " tracks version history, suggests improvements, predicts next steps, and executes workflows."
        ),
    },
]


def initialize_document_samples(conn: sqlite3.Connection):
    """Seed the database with a sample definition for each supported file type."""

    c = conn.cursor()
    for sample in DEFAULT_DOCUMENT_SAMPLES:
        c.execute(
            "SELECT id FROM document_samples WHERE file_type = ? AND title = ?",
            (sample["file_type"], sample["title"]),
        )
        if c.fetchone():
            continue

        payload = sample["sample_content"].format(
            governance=GOVERNANCE_BANNER,
            roles=OPERATING_ROLES,
            behaviors=OPERATING_BEHAVIORS,
        )

        c.execute(
            """
            INSERT INTO document_samples (
                file_type, title, category, description, sample_content, governance, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                sample["file_type"],
                sample["title"],
                sample["category"],
                sample["description"],
                payload,
                GOVERNANCE_BANNER,
                datetime.now().isoformat(timespec="seconds"),
            ),
        )

    conn.commit()


def db_get_document_samples(
    conn: sqlite3.Connection, file_type: Optional[str] = None, category: Optional[str] = None
) -> List[DocumentSample]:
    """Return document sample definitions with optional filtering."""

    c = conn.cursor()
    query = "SELECT * FROM document_samples WHERE 1=1"
    params: List[Any] = []
    if file_type:
        query += " AND file_type = ?"
        params.append(file_type)
    if category:
        query += " AND category = ?"
        params.append(category)
    query += " ORDER BY file_type, title"
    c.execute(query, params)
    rows = c.fetchall()
    samples: List[DocumentSample] = []
    for row in rows:
        samples.append(
            DocumentSample(
                id=row["id"],
                file_type=row["file_type"],
                title=row["title"],
                category=row["category"],
                description=row["description"] or "",
                sample_content=row["sample_content"] or "",
                governance=row["governance"] or GOVERNANCE_BANNER,
                created_at=row["created_at"] or datetime.now().isoformat(timespec="seconds"),
            )
        )
    return samples


def db_document_samples_asdict(conn: sqlite3.Connection) -> List[Dict[str, Any]]:
    """Convenience helper for API responses."""

    return [asdict(sample) for sample in db_get_document_samples(conn)]


def db_list_project_events(
    conn: sqlite3.Connection,
    *,
    project_id: Optional[str] = None,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    """Return recent project ledger events."""

    cursor = conn.cursor()
    where = ""
    params: List[Any] = []
    if project_id:
        where = "WHERE project_id = ?"
        params.append(project_id)
    params.append(max(1, min(limit, 500)))

    query = f"""
        SELECT id, project_id, event_type, payload, created_at, hash_prev, hash_curr
        FROM project_events
        {where}
        ORDER BY datetime(created_at) DESC, id DESC
        LIMIT ?
    """
    try:
        rows = cursor.execute(query, params).fetchall()
    except sqlite3.OperationalError:
        # Table might not exist yet on very old databases.
        return []

    events: List[Dict[str, Any]] = []
    for row in rows:
        payload_raw = row["payload"]
        try:
            payload = json.loads(payload_raw) if payload_raw else {}
        except Exception:
            payload = {"raw": payload_raw}

        events.append(
            {
                "id": row["id"],
                "project_id": row["project_id"],
                "event_type": row["event_type"],
                "payload": payload,
                "created_at": row["created_at"],
                "hash_prev": row["hash_prev"],
                "hash_curr": row["hash_curr"],
            }
        )
    return events


def db_record_project_event(
    conn: sqlite3.Connection,
    *,
    project_id: str,
    event_type: str,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    payload: Optional[Dict[str, Any]] = None,
    user_id: str = "demo",
) -> str:
    """Append an event to the project ledger with a hash chain."""

    cursor = conn.cursor()
    timestamp = datetime.utcnow().isoformat() + "Z"
    payload_dict = {
        "entity_type": entity_type,
        "entity_id": entity_id,
        "data": payload or {},
    }
    payload_json = json.dumps(payload_dict, sort_keys=True)

    cursor.execute(
        """
        SELECT hash_curr FROM project_events
        WHERE project_id = ?
        ORDER BY datetime(created_at) DESC, id DESC
        LIMIT 1
        """,
        (project_id,),
    )
    prev_row = cursor.fetchone()
    hash_prev = prev_row["hash_curr"] if prev_row else None

    ledger_seed = f"{project_id}|{event_type}|{timestamp}|{payload_json}|{hash_prev or ''}"
    hash_curr = hashlib.sha256(ledger_seed.encode("utf-8")).hexdigest()

    cursor.execute(
        """
        INSERT INTO project_events (
            project_id, event_type, payload, created_at, hash_prev, hash_curr, user_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            project_id,
            event_type,
            payload_json,
            timestamp,
            hash_prev,
            hash_curr,
            user_id,
        ),
    )
    conn.commit()
    return hash_curr