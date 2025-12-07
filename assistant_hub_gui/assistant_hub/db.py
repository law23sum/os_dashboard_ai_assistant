#!/usr/bin/env python3
import os
import sqlite3
import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any

DB_FILE = os.path.join(os.path.dirname(__file__), "..", "assistant_hub.db")

PERSONAS = ["Chris", "AIC", "Aria", "Sora"]
PERSONA_ROLES = {
    "Chris": "Human Owner / Primary User",
    "AIC": "Auditor – reviews, checks, cross-validates",
    "Aria": "Assistant – daily flow, tasks, priorities",
    "Sora": "Archive – long-term structure, history, references",
}

STATUS_OPTIONS = ["TODO", "IN_PROGRESS", "BLOCKED", "DONE"]
PRIORITY_OPTIONS = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
DATE_FORMAT = "%Y-%m-%d"

CHAT_ROLES = ["user", "assistant", "system", "tool"]
CHAT_MESSAGE_KINDS = ["chat", "terminal", "terminal_result", "file", "tool_result"]
SECURITY_STATUS_CHOICES = ["secure", "vulnerable", "exploited", "offline"]

DEFAULT_FETCH_PREFERENCES = {
    "notes": True,
    "calendar": True,
    "mail": False,
    "files": False,
}


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
    theme: str = "plain"              # plain | light | dark
    default_view: str = "dashboard"   # dashboard | tasks | projects
    show_system_status: bool = True   # show CPU/RAM/Disk in dashboard
    font_scale: str = "medium"        # small | medium | large
    data_preferences: Dict[str, bool] = field(default_factory=lambda: DEFAULT_FETCH_PREFERENCES.copy())


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


def init_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS state_meta (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)

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


    conn.commit()
    return conn


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
    show_system_status = (show_system_status_raw == "1")
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
    return Settings(
        theme=theme,
        default_view=default_view,
        show_system_status=show_system_status,
        font_scale=font_scale,
        data_preferences=data_preferences,
    )


def save_settings(conn: sqlite3.Connection, settings: Settings):
    set_meta(conn, "setting.theme", settings.theme)
    set_meta(conn, "setting.default_view", settings.default_view)
    set_meta(conn, "setting.show_system_status", "1" if settings.show_system_status else "0")
    set_meta(conn, "setting.font_scale", settings.font_scale)
    set_meta(conn, "setting.data_preferences", json.dumps(settings.data_preferences, ensure_ascii=False))


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


def db_upsert_project(conn: sqlite3.Connection, proj: Project):
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

    c.execute(
        """
        INSERT INTO projects (name, description, status, priority, order_num)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(name) DO UPDATE SET
            description = excluded.description,
            status = excluded.status,
            priority = excluded.priority,
            order_num = excluded.order_num
        """,
        (proj.name, proj.description, proj.status, proj.priority, proj.order_num),
    )
    conn.commit()


def db_delete_project(conn: sqlite3.Connection, name: str):
    c = conn.cursor()
    c.execute("DELETE FROM projects WHERE name = ?", (name,))
    conn.commit()


def db_insert_task(conn: sqlite3.Connection, t: Task) -> int:
    c = conn.cursor()
    c.execute(
        """
        INSERT INTO tasks
        (title, project, status, priority, due_date, notes, owner, created_at,
         depends_on, recurrence_pattern, recurrence_end, time_estimated, time_logged, template_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (t.title, t.project, t.status, t.priority, t.due_date, t.notes, t.owner, t.created_at,
         t.depends_on, t.recurrence_pattern, t.recurrence_end, t.time_estimated, t.time_logged, t.template_id),
    )
    conn.commit()
    return c.lastrowid


def db_update_task(conn: sqlite3.Connection, t: Task):
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


def db_clear_chat_history(conn: sqlite3.Connection):
    c = conn.cursor()
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
