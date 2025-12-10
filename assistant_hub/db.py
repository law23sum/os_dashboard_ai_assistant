#!/usr/bin/env python3
import os
import sqlite3
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

DB_FILE = str((Path(__file__).resolve().parent.parent / "assistant_hub.db"))

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


def init_db(db_path: Optional[os.PathLike | str] = None) -> sqlite3.Connection:
    """
    Initialize the SQLite database (creating tables if needed) and return a connection.

    Args:
        db_path: Optional override path for the DB file. Defaults to the canonical assistant_hub.db.
    """

    target = Path(db_path) if db_path else Path(DB_FILE)
    target.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(target), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS state_meta (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """
    )

    c.execute(
        """
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
    """
    )

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
    c.execute(
        """
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
    """
    )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS projects (
            name TEXT PRIMARY KEY,
            description TEXT,
            status TEXT,
            priority TEXT
        )
    """
    )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS external_sources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            kind TEXT,
            connected INTEGER DEFAULT 1,
            last_sync TEXT
        )
    """
    )

    c.execute(
        """
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
    """
    )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            persona TEXT,
            role TEXT,
            kind TEXT,
            content TEXT,
            created_at TEXT
        )
    """
    )

    c.execute(
        """
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
    """
    )

    # Add description column if it doesn't exist (for existing databases)
    c.execute("PRAGMA table_info(note_links)")
    columns = [row[1] for row in c.fetchall()]
    if "description" not in columns:
        c.execute("ALTER TABLE note_links ADD COLUMN description TEXT DEFAULT ''")

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS document_versions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            note_link_id INTEGER NOT NULL,
            version_number INTEGER NOT NULL,
            file_path TEXT NOT NULL,
            file_size INTEGER NOT NULL,
            checksum TEXT NOT NULL,
            created_at TEXT NOT NULL,
            created_by TEXT,
            description TEXT,
            FOREIGN KEY(note_link_id) REFERENCES note_links(id)
        )
    """
    )

    c.execute(
        """
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
    """
    )

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
    except Exception:
        pass

    conn.commit()
    return conn


def get_meta(
    conn: sqlite3.Connection, key: str, default: Optional[str] = None
) -> Optional[str]:
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
            time_estimated = (
                r["time_estimated"] if r["time_estimated"] is not None else None
            )
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
                created_at=r["created_at"]
                or datetime.now().isoformat(timespec="seconds"),
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
        projects.append(
            Project(
                name=r["name"],
                description=r["description"] or "",
                status=r["status"] or "active",
                priority=priority,
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
                created_at=r["created_at"]
                or datetime.now().isoformat(timespec="seconds"),
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
    approval_mode = (
        get_meta(conn, "setting.change_permission_mode", "ask_when_unsure")
        or "ask_when_unsure"
    )
    continuity_mode = get_meta(conn, "setting.continuity_mode", "full") or "full"
    risk_appetite = get_meta(conn, "setting.risk_appetite", "balanced") or "balanced"
    auto_overwrite_raw = get_meta(conn, "setting.auto_overwrite", "1") or "1"
    auto_overwrite = auto_overwrite_raw == "1"
    if approval_mode not in CHANGE_PERMISSION_MODES:
        approval_mode = "auto" if auto_overwrite else "ask"
    auto_overwrite = approval_mode == "auto"
    if continuity_mode not in CONTINUITY_MODES:
        continuity_mode = "full"
    if risk_appetite not in RISK_APPETITE_MODES:
        risk_appetite = "balanced"
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
        change_permission_mode=approval_mode,
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
    set_meta(conn, "setting.change_permission_mode", settings.change_permission_mode)
    set_meta(conn, "setting.continuity_mode", settings.continuity_mode)
    set_meta(conn, "setting.risk_appetite", settings.risk_appetite)
    set_meta(
        conn,
        "setting.auto_overwrite",
        "1" if settings.change_permission_mode == "auto" else "0",
    )


def save_active_persona(conn: sqlite3.Connection, state: AssistantState):
    set_meta(conn, "active_persona", state.active_persona)


def load_security_status(conn: sqlite3.Connection) -> SecurityStatus:
    status = (get_meta(conn, "security.status", "offline") or "offline").lower()
    if status not in SECURITY_STATUS_CHOICES:
        status = "offline"
    message = (
        get_meta(conn, "security.message", "Telemetry not available yet.")
        or "Telemetry not available yet."
    )
    updated_at = get_meta(conn, "security.updated_at", "") or ""
    source = get_meta(conn, "security.source", "mac_guard") or "mac_guard"
    return SecurityStatus(
        status=status, message=message, updated_at=updated_at, source=source
    )


def save_security_status(conn: sqlite3.Connection, status: SecurityStatus):
    set_meta(conn, "security.status", status.status)
    set_meta(conn, "security.message", status.message)
    set_meta(conn, "security.updated_at", status.updated_at)
    set_meta(conn, "security.source", status.source)


def db_upsert_project(conn: sqlite3.Connection, proj: Project):
    c = conn.cursor()
    # Check if priority column exists, if not add it
    c.execute("PRAGMA table_info(projects)")
    columns = [row[1] for row in c.fetchall()]
    if "priority" not in columns:
        c.execute("ALTER TABLE projects ADD COLUMN priority TEXT DEFAULT 'MEDIUM'")
        conn.commit()

    c.execute(
        """
        INSERT INTO projects (name, description, status, priority)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(name) DO UPDATE SET
            description = excluded.description,
            status = excluded.status,
            priority = excluded.priority
        """,
        (proj.name, proj.description, proj.status, proj.priority),
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
        ),
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
        (
            t.title,
            t.project,
            t.status,
            t.priority,
            t.due_date,
            t.notes,
            t.owner,
            t.depends_on,
            t.recurrence_pattern,
            t.recurrence_end,
            t.time_estimated,
            t.time_logged,
            t.template_id,
            t.id,
        ),
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


def load_external_connections(
    conn: sqlite3.Connection,
) -> Dict[str, ExternalConnection]:
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
            '  "title": "Risk Assessment",\n'
            '  "versioning": "{governance}",\n'
            '  "operating_model": "{roles}",\n'
            '  "behaviors": "{behaviors}",\n'
            '  "sections": ["briefs", "proposals", "compliance reports", "patient summaries", "risk assessments", "regulatory filings", "engineering specs", "technical documents", "product updates", "operational manuals"]\n'
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
    conn: sqlite3.Connection,
    file_type: Optional[str] = None,
    category: Optional[str] = None,
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
                created_at=row["created_at"]
                or datetime.now().isoformat(timespec="seconds"),
            )
        )
    return samples


def db_document_samples_asdict(conn: sqlite3.Connection) -> List[Dict[str, Any]]:
    """Convenience helper for API responses."""

    return [asdict(sample) for sample in db_get_document_samples(conn)]
