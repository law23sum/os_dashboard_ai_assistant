#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import re
import sqlite3
import shutil
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

try:
    import psycopg2
    from psycopg2.extras import DictCursor
except Exception:  # pragma: no cover - optional dependency for SQLite-only use
    psycopg2 = None
    DictCursor = None

from assistant_hub.config import DB_PATH, ensure_data_directories

logger = logging.getLogger(__name__)

ensure_data_directories()
DB_FILE = str(DB_PATH)
DEFAULT_TENANT_ID = "default-tenant"
DEFAULT_TENANT_NAME = "Default Tenant"
DEFAULT_WORKSPACE_ID = "default-workspace"
DEFAULT_WORKSPACE_NAME = "Default Workspace"

PERSONAL_AI_PERSONAS = ["AIC", "Aria", "Sora", "Gabriela"]
GENERIC_AI_PERSONAS = [
    "ChatGPT",
    "Claude",
    "Gemini",
    "DeepSeek",
    "Grok",
    "Cohere",
    "Groq",
]
PERSONAS = ["Chris"] + PERSONAL_AI_PERSONAS
CHAT_PERSONAS = PERSONAS + GENERIC_AI_PERSONAS
GENERIC_AI_PROVIDERS = {
    "ChatGPT": "openai",
    "Claude": "anthropic",
    "Gemini": "google",
    "DeepSeek": "deepseek",
    "Grok": "xai",
    "Cohere": "cohere",
    "Groq": "groq",
}
PERSONA_ROLES = {
    "Chris": "Human Owner / Primary User",
    "AIC": "Sir Chief Fellow Director Principal Software Solutions Systems Engineer Architect",
    "Aria": (
        "Sir Doctor Fellow Philosopher Metaphysician Phenomenologist Axiologist "
        "Semiotician Dialectician Rhetorician Conceptual Cartographer "
        "Interdisciplinary Synthesist Canon Curator Professor"
    ),
    "Sora": (
        "Sir Doctor Fellow Ontological Epistemologist Formal Logician Scientific "
        "Methodologist Semantic Taxonomist Evidence Examiner Governance Auditor Professor"
    ),
    "Gabriela": "Fellow Commercial Strategist Product Marketer Venture-Finance Operator",
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

PMS_PROJECT_MODES = ["personal", "business", "enterprise"]
PMS_TASK_STATUSES = ["TODO", "IN_PROGRESS", "BLOCKED", "DONE", "ARCHIVED"]
PMS_TODO_STATUSES = ["TODO", "IN_PROGRESS", "DONE", "ARCHIVED"]
PMS_RUN_STATUSES = ["queued", "running", "succeeded", "failed", "needs_review"]
PMS_DOCUMENT_VISIBILITY = ["private", "team", "public"]
PMS_DOCUMENT_KINDS = ["spec", "notes", "runbook", "manuscript", "draft", "journal"]
PMS_DEFAULT_PRIORITY_TIERS = ["P0", "P1", "P2", "P3"]
PMS_JOURNAL_SECTION_TYPES = [
    "Comments",
    "KnowledgeTransfer",
    "DisputableDebate",
    "ChallengesRisks",
    "SolutionsMitigations",
    "ProposalRaised",
    "MisunderstandingClarification",
    "TechnicalDesign",
    "CommonDiscussions",
    "Questions",
    "NextSteps",
]
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
    "continuous active cortex; AIC/Sora/Aria/Gabriela become the interpretive personalities that guide "
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
    user_id: str = "demo"
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
    user_id: str = "demo"


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
class Deliverable:
    """Project deliverable entry seeded from curated roadmaps."""

    id: int
    item_number: int
    title: str
    layer: str = ""
    content: str = ""
    source: str = ""
    created_at: str = datetime.now().isoformat(timespec="seconds")
    user_id: str = "demo"


@dataclass
class PmsProject:
    project_id: str
    name: str
    mode: str = "personal"
    scope_type: str = "user"
    scope_id: str = "demo"
    status: str = "active"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    config_json: str = ""
    budget_json: str = ""
    created_by: str = "demo"
    is_sample: int = 0


@dataclass
class PmsEpic:
    epic_id: str
    project_id: str
    title: str
    description: str = ""
    acceptance_criteria: str = ""
    status: str = "active"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    scope_type: str = "user"
    scope_id: str = "demo"
    created_by: str = "demo"
    is_archived: int = 0


@dataclass
class PmsTask:
    task_id: str
    project_id: str
    title: str
    deliverable_spec: str = ""
    acceptance_criteria: str = ""
    priority: str = "P1"
    category: str = "General"
    task_type: str = "General"
    status: str = "TODO"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    enqueue_time: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    epic_id: Optional[str] = None
    scope_type: str = "user"
    scope_id: str = "demo"
    created_by: str = "demo"
    is_archived: int = 0


@dataclass
class PmsTodo:
    todo_id: str
    task_id: str
    text: str
    status: str = "TODO"
    position: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    scope_type: str = "user"
    scope_id: str = "demo"
    created_by: str = "demo"


@dataclass
class PmsExecutionRun:
    run_id: str
    project_id: str
    input_params: str = ""
    status: str = "queued"
    started_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    ended_at: Optional[str] = None
    summary: str = ""
    created_by: str = "demo"
    epic_id: Optional[str] = None
    task_id: Optional[str] = None
    todo_id: Optional[str] = None
    scope_type: str = "user"
    scope_id: str = "demo"


@dataclass
class PmsArtifact:
    artifact_id: str
    project_id: str
    kind: str
    filename: str
    display_name: str
    mime_type: str
    size: int
    sha256: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    storage_path: str = ""
    run_id: Optional[str] = None
    scope_type: str = "user"
    scope_id: str = "demo"


@dataclass
class PmsDocument:
    document_id: str
    project_id: str
    title: str
    kind: str = "spec"
    visibility: str = "private"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    published_revision_hash: Optional[str] = None
    latest_revision_hash: Optional[str] = None
    epic_id: Optional[str] = None
    task_id: Optional[str] = None
    scope_type: str = "user"
    scope_id: str = "demo"
    created_by: str = "demo"
    is_archived: int = 0


@dataclass
class PmsDocumentRevision:
    revision_id: str
    document_id: str
    revision_hash: str
    parent_hash: Optional[str] = None
    author: str = "demo"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    metadata_json: str = ""


@dataclass
class PmsDocumentBlob:
    blob_hash: str
    content: str
    size: int
    created_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))


@dataclass
class PmsExpenseEntry:
    expense_id: str
    project_id: str
    amount: float
    currency: str
    category: str
    description: str
    occurred_at: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    epic_id: Optional[str] = None
    task_id: Optional[str] = None
    vendor: Optional[str] = None
    created_by: str = "demo"
    scope_type: str = "user"
    scope_id: str = "demo"


@dataclass
class PmsTimeEntry:
    time_entry_id: str
    project_id: str
    actor_id: str
    role: str
    duration_minutes: int
    hourly_rate: float
    occurred_at: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    epic_id: Optional[str] = None
    task_id: Optional[str] = None
    scope_type: str = "user"
    scope_id: str = "demo"


@dataclass
class PmsMeetingSession:
    meeting_id: str
    project_id: str
    title: str
    started_at: str
    ended_at: Optional[str] = None
    participants_json: str = ""
    language: str = "en"
    created_by: str = "demo"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    epic_id: Optional[str] = None
    task_id: Optional[str] = None
    scope_type: str = "user"
    scope_id: str = "demo"
    recording_status: str = "none"
    recording_path: str = ""
    recording_mime_type: Optional[str] = None
    recording_size: Optional[int] = None
    recording_sha256: Optional[str] = None
    transcript_status: Optional[str] = None
    journal_status: Optional[str] = None


@dataclass
class PmsTranscriptSegment:
    segment_id: str
    meeting_id: str
    ts_start: float
    ts_end: float
    speaker_label: str
    text_original: str
    text_translated: Optional[str] = None
    confidence: Optional[float] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))


@dataclass
class PmsJournalBlock:
    block_id: str
    meeting_id: str
    ts_start: float
    ts_end: float
    section_type: str
    content: str
    speaker_label: Optional[str] = None
    references_json: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))


@dataclass
class PmsSpeakerMapping:
    mapping_id: str
    meeting_id: str
    speaker_label: str
    participant_name: str
    consented_by: str
    consented_at: str
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))


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


_DB_URL_ENV_KEYS = ("DATABASE_URL", "ASSISTANT_HUB_DATABASE_URL", "OSDASH_DATABASE_URL")
_POSTGRES_FAILURE = False
_POSTGRES_FAILURE_LOGGED = False


def _disable_postgres(exc: Exception) -> None:
    global _POSTGRES_FAILURE, _POSTGRES_FAILURE_LOGGED
    _POSTGRES_FAILURE = True
    if _POSTGRES_FAILURE_LOGGED:
        return
    logger.warning(
        "PostgreSQL connection failed (%s), falling back to SQLite. "
        "To use PostgreSQL, ensure the server is running and DATABASE_URL is correct.",
        exc,
    )
    _POSTGRES_FAILURE_LOGGED = True


def _database_url() -> Optional[str]:
    for key in _DB_URL_ENV_KEYS:
        value = os.getenv(key)
        if value:
            return value.strip()
    return None


def _is_postgres_url(url: str) -> bool:
    lowered = url.strip().lower()
    return lowered.startswith(("postgres://", "postgresql://", "postgresql+psycopg2://"))


def database_url() -> Optional[str]:
    if _POSTGRES_FAILURE:
        return None
    url = _database_url()
    if not url:
        return None
    if _is_postgres_url(url):
        return url
    return None


def is_postgres_enabled() -> bool:
    return database_url() is not None


def _require_psycopg2() -> None:
    if psycopg2 is None or DictCursor is None:
        raise RuntimeError("psycopg2 is required when DATABASE_URL targets Postgres")


_INSERT_OR_IGNORE_RE = re.compile(r"^\s*INSERT\s+OR\s+IGNORE\s+", re.IGNORECASE)
_AUTOINCREMENT_RE = re.compile(
    r"\bINTEGER\s+PRIMARY\s+KEY\s+AUTOINCREMENT\b",
    re.IGNORECASE,
)
_DATETIME_FUNC_RE = re.compile(r"\bdatetime\(([^)]+)\)", re.IGNORECASE)
_PRAGMA_TABLE_INFO_RE = re.compile(
    r"^PRAGMA\s+table_info\s*\(\s*(['\"]?)(?P<table>[^'\")]+)\1\s*\)",
    re.IGNORECASE,
)


def _strip_semicolon(sql: str) -> str:
    return sql.rstrip().rstrip(";")


def _replace_qmark(sql: str) -> str:
    out: List[str] = []
    in_single = False
    in_double = False
    i = 0
    while i < len(sql):
        ch = sql[i]
        if ch == "'" and not in_double:
            out.append(ch)
            if in_single:
                if i + 1 < len(sql) and sql[i + 1] == "'":
                    out.append(sql[i + 1])
                    i += 2
                    continue
                in_single = False
            else:
                in_single = True
            i += 1
            continue
        if ch == '"' and not in_single:
            out.append(ch)
            if in_double:
                if i + 1 < len(sql) and sql[i + 1] == '"':
                    out.append(sql[i + 1])
                    i += 2
                    continue
                in_double = False
            else:
                in_double = True
            i += 1
            continue
        if ch == "?" and not in_single and not in_double:
            out.append("%s")
        else:
            out.append(ch)
        i += 1
    return "".join(out)


def _rewrite_insert_or_ignore(sql: str) -> str:
    if not _INSERT_OR_IGNORE_RE.search(sql):
        return sql
    rewritten = _INSERT_OR_IGNORE_RE.sub("INSERT ", sql)
    if re.search(r"\bON\s+CONFLICT\b", rewritten, re.IGNORECASE):
        return rewritten
    return f"{_strip_semicolon(rewritten)} ON CONFLICT DO NOTHING"


def _rewrite_autoincrement(sql: str) -> str:
    return _AUTOINCREMENT_RE.sub("SERIAL PRIMARY KEY", sql)


def _rewrite_datetime(sql: str) -> str:
    return _DATETIME_FUNC_RE.sub(r"\1", sql)


def _extract_sqlite_master_name(sql: str) -> Optional[str]:
    match = re.search(r"name\s*=\s*'([^']+)'", sql, re.IGNORECASE)
    if match:
        return match.group(1)
    match = re.search(r'name\s*=\s*"([^"]+)"', sql, re.IGNORECASE)
    if match:
        return match.group(1)
    return None


def _translate_sqlite_master(sql: str, params: Optional[Sequence[Any]]) -> tuple[str, Optional[Sequence[Any]]]:
    if "sqlite_master" not in sql.lower():
        return sql, params
    base = (
        "SELECT table_name AS name FROM information_schema.tables "
        "WHERE table_schema = 'public' AND table_type = 'BASE TABLE'"
    )
    name = _extract_sqlite_master_name(sql)
    if name:
        base += " AND table_name = %s"
        params = (name,)
    elif re.search(r"name\s*=\s*\?", sql, re.IGNORECASE):
        base += " AND table_name = %s"
    if "order by" in sql.lower():
        base += " ORDER BY name"
    return base, params


class PostgresConnection:
    def __init__(self, conn) -> None:
        self._conn = conn
        self.row_factory = None
        self._db_kind = "postgres"

    def cursor(self) -> "PostgresCursor":
        cursor = self._conn.cursor(cursor_factory=DictCursor)
        return PostgresCursor(cursor, self)

    def execute(self, sql: str, params: Optional[Sequence[Any]] = None) -> "PostgresCursor":
        cursor = self.cursor()
        return cursor.execute(sql, params)

    def executemany(self, sql: str, params_seq: Sequence[Sequence[Any]]) -> "PostgresCursor":
        cursor = self.cursor()
        return cursor.executemany(sql, params_seq)

    def commit(self) -> None:
        self._conn.commit()

    def rollback(self) -> None:
        self._conn.rollback()

    def close(self) -> None:
        self._conn.close()

    def __enter__(self) -> "PostgresConnection":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if exc:
            self.rollback()
        else:
            self.commit()
        self.close()

    def _translate_statement(
        self, sql: str, params: Optional[Sequence[Any]]
    ) -> tuple[Optional[str], Optional[Sequence[Any]], Optional[List[Any]], Optional[List[tuple]]]:
        stripped = _strip_semicolon(sql.strip())
        if not stripped:
            return stripped, params, None, None

        if stripped.upper().startswith("PRAGMA"):
            pragma_match = _PRAGMA_TABLE_INFO_RE.match(stripped)
            if pragma_match:
                table = pragma_match.group("table")
                pragma_sql = """
                    SELECT
                        c.ordinal_position - 1 AS cid,
                        c.column_name AS name,
                        c.data_type AS type,
                        CASE WHEN c.is_nullable = 'NO' THEN 1 ELSE 0 END AS notnull,
                        c.column_default AS dflt_value,
                        CASE WHEN tc.constraint_type = 'PRIMARY KEY' THEN 1 ELSE 0 END AS pk
                    FROM information_schema.columns c
                    LEFT JOIN information_schema.key_column_usage kcu
                        ON c.table_schema = kcu.table_schema
                       AND c.table_name = kcu.table_name
                       AND c.column_name = kcu.column_name
                    LEFT JOIN information_schema.table_constraints tc
                        ON tc.table_schema = kcu.table_schema
                       AND tc.table_name = kcu.table_name
                       AND tc.constraint_name = kcu.constraint_name
                       AND tc.constraint_type = 'PRIMARY KEY'
                    WHERE c.table_schema = 'public' AND c.table_name = %s
                    ORDER BY c.ordinal_position
                """
                return pragma_sql, (table,), None, None
            if stripped.upper().startswith("PRAGMA INTEGRITY_CHECK"):
                return None, None, [("ok",)], None
            return None, None, [], None

        rewritten, params = _translate_sqlite_master(stripped, params)
        rewritten = _rewrite_insert_or_ignore(rewritten)
        rewritten = _rewrite_autoincrement(rewritten)
        rewritten = _rewrite_datetime(rewritten)
        rewritten = _replace_qmark(rewritten)
        return rewritten, params, None, None


class PostgresCursor:
    def __init__(self, cursor, connection: PostgresConnection) -> None:
        self._cursor = cursor
        self._connection = connection
        self._fake_rows: Optional[List[Any]] = None
        self._fake_index = 0
        self._fake_description: Optional[List[tuple]] = None
        self._lastrowid: Optional[Any] = None

    @property
    def description(self):
        if self._fake_description is not None:
            return self._fake_description
        return self._cursor.description

    @property
    def rowcount(self):
        if self._fake_rows is not None:
            return len(self._fake_rows)
        return self._cursor.rowcount

    @property
    def lastrowid(self):
        return self._lastrowid

    def execute(self, sql: str, params: Optional[Sequence[Any]] = None) -> "PostgresCursor":
        self._fake_rows = None
        self._fake_index = 0
        self._fake_description = None
        self._lastrowid = None

        rewritten, params, fake_rows, fake_description = self._connection._translate_statement(
            sql, params
        )
        if fake_rows is not None:
            self._fake_rows = fake_rows
            self._fake_description = fake_description
            return self

        try:
            if params is None:
                self._cursor.execute(rewritten)
            else:
                self._cursor.execute(rewritten, params)
        except Exception as exc:
            raise sqlite3.OperationalError(str(exc)) from exc
        self._lastrowid = getattr(self._cursor, "lastrowid", None)
        return self

    def executemany(self, sql: str, params_seq: Sequence[Sequence[Any]]) -> "PostgresCursor":
        self._fake_rows = None
        self._fake_index = 0
        self._fake_description = None
        self._lastrowid = None

        rewritten, params, fake_rows, fake_description = self._connection._translate_statement(
            sql, None
        )
        if fake_rows is not None:
            self._fake_rows = fake_rows
            self._fake_description = fake_description
            return self

        try:
            self._cursor.executemany(rewritten, params_seq)
        except Exception as exc:
            raise sqlite3.OperationalError(str(exc)) from exc
        self._lastrowid = getattr(self._cursor, "lastrowid", None)
        return self

    def fetchone(self):
        if self._fake_rows is not None:
            if self._fake_index >= len(self._fake_rows):
                return None
            row = self._fake_rows[self._fake_index]
            self._fake_index += 1
            return row
        return self._cursor.fetchone()

    def fetchall(self):
        if self._fake_rows is not None:
            if self._fake_index == 0:
                self._fake_index = len(self._fake_rows)
                return list(self._fake_rows)
            remaining = self._fake_rows[self._fake_index :]
            self._fake_index = len(self._fake_rows)
            return list(remaining)
        return self._cursor.fetchall()

    def fetchmany(self, size: Optional[int] = None):
        if self._fake_rows is not None:
            if self._fake_index >= len(self._fake_rows):
                return []
            if size is None:
                size = 1
            end = min(self._fake_index + size, len(self._fake_rows))
            batch = self._fake_rows[self._fake_index : end]
            self._fake_index = end
            return list(batch)
        if size is None:
            return self._cursor.fetchmany()
        return self._cursor.fetchmany(size)

    def close(self) -> None:
        self._cursor.close()


def is_postgres_connection(conn: Any) -> bool:
    return isinstance(conn, PostgresConnection)


def _connect_sqlite(db_path: Optional[os.PathLike | str] = None) -> sqlite3.Connection:
    target = Path(db_path) if db_path else Path(DB_FILE)
    target.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(target), check_same_thread=False, timeout=10.0)
    conn.row_factory = sqlite3.Row
    return conn


def connect_db(db_path: Optional[os.PathLike | str] = None):
    url = database_url()
    if url:
        try:
            _require_psycopg2()
        except Exception as exc:
            _disable_postgres(exc)
            return _connect_sqlite(db_path)
    if url:
        try:
            return PostgresConnection(psycopg2.connect(url))
        except Exception as exc:
            _disable_postgres(exc)
            return _connect_sqlite(db_path)
    return _connect_sqlite(db_path)


def _execute_insert_returning_id(
    conn,
    cursor,
    sql: str,
    params: Sequence[Any],
) -> Any:
    if is_postgres_connection(conn):
        sql = f"{_strip_semicolon(sql.strip())} RETURNING id"
        cursor.execute(sql, params)
        row = cursor.fetchone()
        return row[0] if row else 0
    cursor.execute(sql, params)
    return cursor.lastrowid


def insert_and_fetch_id(conn, sql: str, params: Sequence[Any]) -> Any:
    cursor = conn.cursor()
    return _execute_insert_returning_id(conn, cursor, sql, params)


def _check_database_integrity(conn: sqlite3.Connection) -> bool:
    """Check if database is valid by running integrity check."""
    try:
        cursor = conn.cursor()
        cursor.execute("PRAGMA integrity_check")
        result = cursor.fetchone()
        return result[0] == "ok"
    except Exception as e:
        logger.error(f"Database integrity check failed: {e}")
        return False


def _recover_database(db_path: Path) -> bool:
    """Attempt to recover corrupted database by backing it up and removing it."""
    try:
        if db_path.exists():
            # Add timestamp to backup filename to avoid overwriting
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = db_path.parent / f"{db_path.stem}_{timestamp}.db.backup"
            shutil.copy2(db_path, backup_path)
            logger.warning(f"Backed up corrupted database to {backup_path}")
            
            # Remove corrupted file so it can be recreated
            db_path.unlink()
            logger.info("Removed corrupted database file, will be recreated on next init")
        return True
    except Exception as e:
        logger.error(f"Database recovery failed: {e}")
        return False


def init_db(db_path: Optional[os.PathLike | str] = None) -> sqlite3.Connection:
    """Initialize the database schema (SQLite by default, Postgres when DATABASE_URL is set)."""
    # Try to connect - this may fall back to SQLite if PostgreSQL is unavailable
    target = Path(db_path) if db_path else Path(DB_FILE)
    try:
        conn = connect_db(db_path)
    except Exception as exc:
        logger.warning("PostgreSQL connection failed (%s), falling back to SQLite.", exc)
        conn = None
    if conn is None:
        target.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(target), check_same_thread=False)
        conn.row_factory = sqlite3.Row
    
    # If we got a SQLite connection (either by design or fallback), run SQLite initialization
    if not is_postgres_connection(conn):
        target.parent.mkdir(parents=True, exist_ok=True)

        # Check for database corruption before attempting to use it
        if target.exists():
            try:
                # Use a test connection for integrity check
                test_conn = sqlite3.connect(str(target), check_same_thread=False)
                if not _check_database_integrity(test_conn):
                    test_conn.close()
                    logger.warning("Database integrity check failed, attempting recovery...")
                    if not _recover_database(target):
                        logger.error("Database recovery failed, creating new database")
                        if target.exists():
                            backup_path = target.with_suffix(".db.backup")
                            try:
                                shutil.move(target, backup_path)
                                logger.info(f"Moved corrupted database to {backup_path}")
                            except Exception as e:
                                logger.error(f"Failed to move corrupted database: {e}")
                                target.unlink()  # Force remove if move fails
                            # Reconnect after recovery
                            conn.close()
                            conn = sqlite3.connect(str(target), check_same_thread=False)
                            conn.row_factory = sqlite3.Row
                else:
                    test_conn.close()
            except sqlite3.DatabaseError as e:
                logger.warning(f"Database error detected: {e}, attempting recovery...")
                if not _recover_database(target):
                    logger.error("Database recovery failed, creating new database")
                    if target.exists():
                        backup_path = target.with_suffix(".db.backup")
                        try:
                            shutil.move(target, backup_path)
                            logger.info(f"Moved corrupted database to {backup_path}")
                        except Exception as e:
                            logger.error(f"Failed to move corrupted database: {e}")
                            target.unlink()  # Force remove if move fails
                    # Reconnect after recovery
                    conn.close()
                    conn = sqlite3.connect(str(target), check_same_thread=False)
                    conn.row_factory = sqlite3.Row

        # Apply SQLite performance optimizations to the existing connection
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

    def _column_exists(table: str, column: str) -> bool:
        try:
            rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
            return any(row[1] == column for row in rows)
        except Exception:
            return False

    def _add_column(table: str, column: str, definition: str) -> None:
        if _column_exists(table, column):
            return
        try:
            conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
        except Exception:
            # Ignore if the table does not exist yet or if column cannot be added.
            pass

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
    c.execute("PRAGMA table_info(users)")
    columns = [row[1] for row in c.fetchall()]
    if "tenant_id" not in columns:
        c.execute("ALTER TABLE users ADD COLUMN tenant_id TEXT")
    if "workspace_id" not in columns:
        c.execute("ALTER TABLE users ADD COLUMN workspace_id TEXT")
    if "username" not in columns:
        c.execute("ALTER TABLE users ADD COLUMN username TEXT")

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS user_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            refresh_token TEXT UNIQUE NOT NULL,
            expires_at TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS user_activity (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            action TEXT NOT NULL,
            resource TEXT,
            details TEXT,
            ip_address TEXT,
            user_agent TEXT,
            timestamp TEXT,
            created_at TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """
    )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS tenants (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS workspaces (
            id TEXT PRIMARY KEY,
            tenant_id TEXT NOT NULL,
            name TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(tenant_id) REFERENCES tenants(id) ON DELETE CASCADE
        )
        """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS ledger_events (
            id TEXT PRIMARY KEY,
            entity_type TEXT NOT NULL,
            entity_id TEXT NOT NULL,
            action TEXT NOT NULL,
            created_at TEXT NOT NULL,
            metadata_json TEXT
        )
        """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS cir_documents (
            id TEXT PRIMARY KEY,
            workspace_id TEXT NOT NULL,
            title TEXT NOT NULL,
            status TEXT,
            created_at TEXT NOT NULL,
            metadata_json TEXT,
            FOREIGN KEY(workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE
        )
        """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS capsules (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            policy_tier TEXT,
            created_at TEXT NOT NULL
        )
        """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS drivers (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT,
            created_at TEXT NOT NULL
        )
        """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS policies (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            version TEXT,
            created_at TEXT NOT NULL
        )
        """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS policy_packs (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            version TEXT,
            created_at TEXT NOT NULL,
            tenant_id TEXT,
            workspace_id TEXT
        )
        """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS policy_decisions (
            id TEXT PRIMARY KEY,
            simulation_id TEXT NOT NULL,
            decision TEXT NOT NULL,
            rationale TEXT,
            severity TEXT,
            created_at TEXT NOT NULL,
            tenant_id TEXT,
            workspace_id TEXT,
            FOREIGN KEY(simulation_id) REFERENCES policy_simulations(id) ON DELETE CASCADE
        )
        """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS usage_records (
            id TEXT PRIMARY KEY,
            tenant_id TEXT NOT NULL,
            metric TEXT NOT NULL,
            value REAL NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(tenant_id) REFERENCES tenants(id) ON DELETE CASCADE
        )
        """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS evidence_packs (
            id TEXT PRIMARY KEY,
            workspace_id TEXT NOT NULL,
            label TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE
        )
        """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS configs (
            id TEXT PRIMARY KEY,
            scope TEXT NOT NULL,
            data_json TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS metrics (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            value REAL NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS secrets (
            id TEXT PRIMARY KEY,
            handle TEXT NOT NULL,
            kind TEXT,
            created_at TEXT NOT NULL
        )
        """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS artifacts (
            id TEXT PRIMARY KEY,
            handle TEXT NOT NULL,
            storage_uri TEXT,
            created_at TEXT NOT NULL
        )
        """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS policy_simulations (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            policy_pack_id TEXT NOT NULL,
            scenario TEXT NOT NULL,
            environment_profile TEXT NOT NULL,
            status TEXT NOT NULL,
            risk_score REAL NOT NULL,
            cost_estimate REAL NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE SET NULL
        )
        """
    )

    # ---------------------------------------------------------------------
    # Governance / classification scaffolding columns
    # ---------------------------------------------------------------------

    _add_column("tasks", "tenant_id", "TEXT")
    _add_column("tasks", "workspace_id", "TEXT")
    _add_column("tasks", "updated_at", "TEXT")

    _add_column("projects", "tenant_id", "TEXT")
    _add_column("projects", "workspace_id", "TEXT")
    _add_column("projects", "created_at", "TEXT")
    _add_column("projects", "updated_at", "TEXT")

    _add_column("usage_records", "workspace_id", "TEXT")
    _add_column("usage_records", "user_id", "TEXT")

    _add_column("evidence_packs", "tenant_id", "TEXT")
    _add_column("evidence_packs", "user_id", "TEXT")
    _add_column("evidence_packs", "retention_policy", "TEXT")
    _add_column("evidence_packs", "legal_hold", "INTEGER DEFAULT 0")
    _add_column("evidence_packs", "residency", "TEXT")

    _add_column("configs", "tenant_id", "TEXT")
    _add_column("configs", "workspace_id", "TEXT")
    _add_column("configs", "user_id", "TEXT")
    _add_column("configs", "updated_at", "TEXT")

    _add_column("metrics", "tenant_id", "TEXT")
    _add_column("metrics", "workspace_id", "TEXT")
    _add_column("metrics", "user_id", "TEXT")
    _add_column("metrics", "dimension_json", "TEXT")
    _add_column("metrics", "source", "TEXT")

    _add_column("secrets", "handle", "TEXT NOT NULL DEFAULT ''")
    _add_column("secrets", "tenant_id", "TEXT")
    _add_column("secrets", "workspace_id", "TEXT")
    _add_column("secrets", "user_id", "TEXT")
    _add_column("secrets", "last_rotated_at", "TEXT")
    _add_column("secrets", "expires_at", "TEXT")
    _add_column("secrets", "retention_policy", "TEXT")

    _add_column("artifacts", "handle", "TEXT NOT NULL DEFAULT ''")
    _add_column("artifacts", "tenant_id", "TEXT")
    _add_column("artifacts", "workspace_id", "TEXT")
    _add_column("artifacts", "user_id", "TEXT")
    _add_column("artifacts", "size_bytes", "INTEGER")
    _add_column("artifacts", "content_type", "TEXT")
    _add_column("artifacts", "checksum", "TEXT")
    _add_column("artifacts", "retention_policy", "TEXT")
    _add_column("artifacts", "legal_hold", "INTEGER DEFAULT 0")
    _add_column("artifacts", "residency", "TEXT")

    _add_column("policy_simulations", "tenant_id", "TEXT")
    _add_column("policy_simulations", "workspace_id", "TEXT")
    _add_column("policy_simulations", "decisions_json", "TEXT")
    _add_column("policy_simulations", "distribution_json", "TEXT")
    _add_column("policy_simulations", "report", "TEXT")
    _add_column("policy_simulations", "updated_at", "TEXT")

    _add_column("ledger_events", "tenant_id", "TEXT")
    _add_column("ledger_events", "workspace_id", "TEXT")
    _add_column("ledger_events", "user_id", "TEXT")

    _add_column("cir_documents", "tenant_id", "TEXT")
    _add_column("cir_documents", "user_id", "TEXT")

    _add_column("capsules", "tenant_id", "TEXT")
    _add_column("drivers", "tenant_id", "TEXT")
    _add_column("policies", "tenant_id", "TEXT")
    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_policy_simulations_user
        ON policy_simulations(user_id, datetime(created_at) DESC)
        """
    )
    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_policy_simulations_pack
        ON policy_simulations(policy_pack_id, datetime(created_at) DESC)
        """
    )
    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_policy_simulations_status
        ON policy_simulations(status, datetime(created_at) DESC)
        """
    )
    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_policy_simulations_tenant
        ON policy_simulations(tenant_id, datetime(created_at) DESC)
        """
    )
    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_policy_simulations_workspace
        ON policy_simulations(workspace_id, datetime(created_at) DESC)
        """
    )
    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_policy_packs_tenant
        ON policy_packs(tenant_id, datetime(created_at) DESC)
        """
    )
    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_policy_packs_workspace
        ON policy_packs(workspace_id, datetime(created_at) DESC)
        """
    )
    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_policy_decisions_simulation
        ON policy_decisions(simulation_id, datetime(created_at) DESC)
        """
    )
    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_policy_decisions_tenant
        ON policy_decisions(tenant_id, datetime(created_at) DESC)
        """
    )
    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_policy_decisions_workspace
        ON policy_decisions(workspace_id, datetime(created_at) DESC)
        """
    )

    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_tenants_name
        ON tenants(name)
        """
    )
    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_workspaces_tenant
        ON workspaces(tenant_id)
        """
    )
    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_ledger_events_entity
        ON ledger_events(entity_id, datetime(created_at) DESC)
        """
    )
    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_ledger_events_tenant
        ON ledger_events(tenant_id, datetime(created_at) DESC)
        """
    )
    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_ledger_events_workspace
        ON ledger_events(workspace_id, datetime(created_at) DESC)
        """
    )
    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_ledger_events_user
        ON ledger_events(user_id, datetime(created_at) DESC)
        """
    )
    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_cir_documents_workspace
        ON cir_documents(workspace_id, datetime(created_at) DESC)
        """
    )
    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_cir_documents_tenant
        ON cir_documents(tenant_id, datetime(created_at) DESC)
        """
    )
    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_cir_documents_user
        ON cir_documents(user_id, datetime(created_at) DESC)
        """
    )
    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_usage_records_tenant
        ON usage_records(tenant_id, metric, datetime(created_at) DESC)
        """
    )
    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_usage_records_workspace
        ON usage_records(workspace_id, metric, datetime(created_at) DESC)
        """
    )
    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_usage_records_user
        ON usage_records(user_id, metric, datetime(created_at) DESC)
        """
    )
    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_evidence_packs_workspace
        ON evidence_packs(workspace_id, datetime(created_at) DESC)
        """
    )
    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_evidence_packs_tenant
        ON evidence_packs(tenant_id, datetime(created_at) DESC)
        """
    )
    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_evidence_packs_user
        ON evidence_packs(user_id, datetime(created_at) DESC)
        """
    )
    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_configs_scope
        ON configs(scope)
        """
    )
    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_configs_tenant
        ON configs(tenant_id, datetime(created_at) DESC)
        """
    )
    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_configs_workspace
        ON configs(workspace_id, datetime(created_at) DESC)
        """
    )
    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_configs_user
        ON configs(user_id, datetime(created_at) DESC)
        """
    )
    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_metrics_name
        ON metrics(name, datetime(created_at) DESC)
        """
    )
    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_metrics_tenant
        ON metrics(tenant_id, datetime(created_at) DESC)
        """
    )
    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_metrics_workspace
        ON metrics(workspace_id, datetime(created_at) DESC)
        """
    )
    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_metrics_user
        ON metrics(user_id, datetime(created_at) DESC)
        """
    )
    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_secrets_handle
        ON secrets(handle)
        """
    )
    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_secrets_tenant
        ON secrets(tenant_id, datetime(created_at) DESC)
        """
    )
    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_secrets_workspace
        ON secrets(workspace_id, datetime(created_at) DESC)
        """
    )
    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_secrets_user
        ON secrets(user_id, datetime(created_at) DESC)
        """
    )
    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_artifacts_handle
        ON artifacts(handle)
        """
    )
    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_artifacts_tenant
        ON artifacts(tenant_id, datetime(created_at) DESC)
        """
    )
    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_artifacts_workspace
        ON artifacts(workspace_id, datetime(created_at) DESC)
        """
    )
    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_artifacts_user
        ON artifacts(user_id, datetime(created_at) DESC)
        """
    )
    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_capsules_tenant
        ON capsules(tenant_id, datetime(created_at) DESC)
        """
    )
    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_drivers_tenant
        ON drivers(tenant_id, datetime(created_at) DESC)
        """
    )
    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_policies_tenant
        ON policies(tenant_id, datetime(created_at) DESC)
        """
    )
    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_policy_simulations_user
        ON policy_simulations(user_id, policy_pack_id, datetime(created_at) DESC)
        """
    )
    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_users_tenant
        ON users(tenant_id)
        """
    )
    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_users_workspace
        ON users(workspace_id)
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

    _add_column("tasks", "created_at", "TEXT")
    _add_column("tasks", "tenant_id", "TEXT")
    _add_column("tasks", "workspace_id", "TEXT")

    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_tasks_user
        ON tasks(user_id, datetime(created_at) DESC)
        """
    )
    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_tasks_tenant
        ON tasks(tenant_id, datetime(created_at) DESC)
        """
    )
    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_tasks_workspace
        ON tasks(workspace_id, datetime(created_at) DESC)
        """
    )
    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_tasks_status
        ON tasks(status, datetime(created_at) DESC)
        """
    )
    
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

    _add_column("projects", "created_at", "TEXT")
    _add_column("projects", "tenant_id", "TEXT")
    _add_column("projects", "workspace_id", "TEXT")

    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_projects_user
        ON projects(user_id, datetime(created_at) DESC)
        """
    )
    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_projects_tenant
        ON projects(tenant_id, datetime(created_at) DESC)
        """
    )
    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_projects_workspace
        ON projects(workspace_id, datetime(created_at) DESC)
        """
    )
    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_projects_status
        ON projects(status)
        """
    )

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

    # ---------------------------------------------------------------------
    # Deliverables catalog (admin-seeded)
    # ---------------------------------------------------------------------
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS deliverables (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_number INTEGER NOT NULL,
            title TEXT NOT NULL,
            layer TEXT,
            content TEXT,
            source TEXT,
            created_at TEXT NOT NULL,
            user_id TEXT DEFAULT 'demo'
        )
        """
    )
    c.execute("PRAGMA table_info(deliverables)")
    columns = [row[1] for row in c.fetchall()]
    if "user_id" not in columns:
        c.execute("ALTER TABLE deliverables ADD COLUMN user_id TEXT DEFAULT 'demo'")
    if "layer" not in columns:
        c.execute("ALTER TABLE deliverables ADD COLUMN layer TEXT DEFAULT ''")
    if "source" not in columns:
        c.execute("ALTER TABLE deliverables ADD COLUMN source TEXT DEFAULT ''")

    # ---------------------------------------------------------------------
    # Intelligence Project Management (IPM) tables (legacy pms_* storage)
    # ---------------------------------------------------------------------
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS pms_projects (
            project_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            mode TEXT NOT NULL,
            scope_type TEXT NOT NULL,
            scope_id TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT,
            updated_at TEXT,
            config_json TEXT,
            budget_json TEXT,
            created_by TEXT,
            is_sample INTEGER DEFAULT 0
        )
        """
    )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS pms_epics (
            epic_id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            acceptance_criteria TEXT,
            status TEXT,
            created_at TEXT,
            updated_at TEXT,
            scope_type TEXT,
            scope_id TEXT,
            created_by TEXT,
            is_archived INTEGER DEFAULT 0
        )
        """
    )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS pms_tasks (
            task_id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            epic_id TEXT,
            title TEXT NOT NULL,
            deliverable_spec TEXT,
            acceptance_criteria TEXT,
            priority TEXT,
            category TEXT,
            task_type TEXT,
            status TEXT,
            created_at TEXT,
            updated_at TEXT,
            enqueue_time TEXT,
            scope_type TEXT,
            scope_id TEXT,
            created_by TEXT,
            is_archived INTEGER DEFAULT 0
        )
        """
    )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS pms_todos (
            todo_id TEXT PRIMARY KEY,
            task_id TEXT NOT NULL,
            text TEXT NOT NULL,
            status TEXT,
            position INTEGER,
            created_at TEXT,
            updated_at TEXT,
            scope_type TEXT,
            scope_id TEXT,
            created_by TEXT
        )
        """
    )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS pms_runs (
            run_id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            epic_id TEXT,
            task_id TEXT,
            todo_id TEXT,
            input_params TEXT,
            status TEXT,
            started_at TEXT,
            ended_at TEXT,
            summary TEXT,
            created_by TEXT,
            scope_type TEXT,
            scope_id TEXT
        )
        """
    )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS pms_artifacts (
            artifact_id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            run_id TEXT,
            kind TEXT,
            filename TEXT,
            display_name TEXT,
            mime_type TEXT,
            size INTEGER,
            sha256 TEXT,
            created_at TEXT,
            storage_path TEXT,
            scope_type TEXT,
            scope_id TEXT
        )
        """
    )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS pms_documents (
            document_id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            epic_id TEXT,
            task_id TEXT,
            title TEXT,
            kind TEXT,
            visibility TEXT,
            created_at TEXT,
            updated_at TEXT,
            published_revision_hash TEXT,
            latest_revision_hash TEXT,
            scope_type TEXT,
            scope_id TEXT,
            created_by TEXT,
            is_archived INTEGER DEFAULT 0
        )
        """
    )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS pms_document_blobs (
            blob_hash TEXT PRIMARY KEY,
            content TEXT,
            size INTEGER,
            created_at TEXT
        )
        """
    )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS pms_document_revisions (
            revision_id TEXT PRIMARY KEY,
            document_id TEXT NOT NULL,
            revision_hash TEXT NOT NULL,
            parent_hash TEXT,
            author TEXT,
            created_at TEXT,
            metadata_json TEXT
        )
        """
    )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS pms_expenses (
            expense_id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            epic_id TEXT,
            task_id TEXT,
            amount REAL,
            currency TEXT,
            category TEXT,
            vendor TEXT,
            description TEXT,
            occurred_at TEXT,
            created_at TEXT,
            updated_at TEXT,
            created_by TEXT,
            scope_type TEXT,
            scope_id TEXT
        )
        """
    )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS pms_time_entries (
            time_entry_id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            epic_id TEXT,
            task_id TEXT,
            actor_id TEXT,
            role TEXT,
            duration_minutes INTEGER,
            hourly_rate REAL,
            occurred_at TEXT,
            created_at TEXT,
            updated_at TEXT,
            scope_type TEXT,
            scope_id TEXT
        )
        """
    )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS pms_meetings (
            meeting_id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            epic_id TEXT,
            task_id TEXT,
            title TEXT,
            started_at TEXT,
            ended_at TEXT,
            participants_json TEXT,
            language TEXT,
            created_by TEXT,
            created_at TEXT,
            scope_type TEXT,
            scope_id TEXT,
            recording_status TEXT,
            recording_path TEXT,
            recording_mime_type TEXT,
            recording_size INTEGER,
            recording_sha256 TEXT,
            transcript_status TEXT,
            journal_status TEXT
        )
        """
    )

    c.execute("PRAGMA table_info(pms_meetings)")
    meeting_columns = {row[1] for row in c.fetchall()}
    for column_name, column_type in {
        "recording_path": "TEXT",
        "recording_mime_type": "TEXT",
        "recording_size": "INTEGER",
        "recording_sha256": "TEXT",
        "transcript_status": "TEXT",
        "journal_status": "TEXT",
    }.items():
        if column_name not in meeting_columns:
            c.execute(f"ALTER TABLE pms_meetings ADD COLUMN {column_name} {column_type}")

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS pms_transcript_segments (
            segment_id TEXT PRIMARY KEY,
            meeting_id TEXT NOT NULL,
            ts_start REAL,
            ts_end REAL,
            speaker_label TEXT,
            text_original TEXT,
            text_translated TEXT,
            confidence REAL,
            created_at TEXT
        )
        """
    )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS pms_journal_blocks (
            block_id TEXT PRIMARY KEY,
            meeting_id TEXT NOT NULL,
            ts_start REAL,
            ts_end REAL,
            section_type TEXT,
            speaker_label TEXT,
            content TEXT,
            references_json TEXT,
            created_at TEXT
        )
        """
    )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS pms_speaker_mappings (
            mapping_id TEXT PRIMARY KEY,
            meeting_id TEXT NOT NULL,
            speaker_label TEXT,
            participant_name TEXT,
            consented_by TEXT,
            consented_at TEXT,
            updated_at TEXT
        )
        """
    )

    c.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS idx_pms_projects_scope_name
        ON pms_projects(scope_type, scope_id, name)
        """
    )
    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_pms_projects_scope
        ON pms_projects(scope_type, scope_id, status)
        """
    )
    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_pms_projects_sample
        ON pms_projects(is_sample, created_at DESC)
        """
    )
    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_pms_epics_project
        ON pms_epics(project_id, updated_at DESC)
        """
    )
    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_pms_tasks_project
        ON pms_tasks(project_id, status, priority)
        """
    )
    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_pms_tasks_epic
        ON pms_tasks(epic_id, updated_at DESC)
        """
    )
    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_pms_tasks_enqueue
        ON pms_tasks(enqueue_time, task_id)
        """
    )
    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_pms_todos_task
        ON pms_todos(task_id, position)
        """
    )
    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_pms_runs_project
        ON pms_runs(project_id, started_at DESC)
        """
    )
    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_pms_runs_task
        ON pms_runs(task_id, started_at DESC)
        """
    )
    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_pms_artifacts_run
        ON pms_artifacts(run_id, created_at DESC)
        """
    )
    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_pms_documents_project
        ON pms_documents(project_id, updated_at DESC)
        """
    )
    c.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS idx_pms_doc_revision_unique
        ON pms_document_revisions(document_id, revision_hash)
        """
    )
    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_pms_doc_revisions_doc
        ON pms_document_revisions(document_id, created_at DESC)
        """
    )
    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_pms_expenses_project
        ON pms_expenses(project_id, occurred_at DESC)
        """
    )
    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_pms_time_entries_project
        ON pms_time_entries(project_id, occurred_at DESC)
        """
    )
    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_pms_meetings_project
        ON pms_meetings(project_id, started_at DESC)
        """
    )
    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_pms_transcript_meeting
        ON pms_transcript_segments(meeting_id, ts_start)
        """
    )
    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_pms_journal_meeting
        ON pms_journal_blocks(meeting_id, section_type, ts_start)
        """
    )
    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_pms_speaker_meeting
        ON pms_speaker_mappings(meeting_id, speaker_label)
        """
    )

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
    _ensure_default_tenant_workspace(conn)
    _ensure_bootstrap_accounts(conn)
    return conn


def _bcrypt_hash_password(raw_password: str) -> str:
    """Hash a password for storage (bcrypt)."""
    import bcrypt  # local import to avoid hard dep at module import time

    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(raw_password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def _ensure_default_tenant_workspace(conn: sqlite3.Connection) -> None:
    """Ensure a default tenant/workspace exist for scope enforcement."""
    now = datetime.now().isoformat(timespec="seconds")
    cur = conn.cursor()
    cur.execute(
        """
        INSERT OR IGNORE INTO tenants (id, name, created_at)
        VALUES (?, ?, ?)
        """,
        (DEFAULT_TENANT_ID, DEFAULT_TENANT_NAME, now),
    )
    cur.execute(
        """
        INSERT OR IGNORE INTO workspaces (id, tenant_id, name, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (DEFAULT_WORKSPACE_ID, DEFAULT_TENANT_ID, DEFAULT_WORKSPACE_NAME, now),
    )
    cur.execute(
        "UPDATE users SET tenant_id = ? WHERE tenant_id IS NULL OR tenant_id = ''",
        (DEFAULT_TENANT_ID,),
    )
    cur.execute(
        "UPDATE users SET workspace_id = ? WHERE workspace_id IS NULL OR workspace_id = ''",
        (DEFAULT_WORKSPACE_ID,),
    )
    conn.commit()


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
        username = (email.split("@", 1)[0] if email else user_id).strip().lower()
        cur.execute("SELECT id FROM users WHERE email = ?", (email,))
        row = cur.fetchone()
        if row:
            return
        cur.execute(
            """
            INSERT INTO users (
                id,
                email,
                username,
                display_name,
                password_hash,
                is_admin,
                environment,
                disabled,
                created_at,
                last_login,
                tenant_id,
                workspace_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?, NULL, ?, ?)
            """,
            (
                user_id,
                email,
                username,
                "Admin" if is_admin else "Demo User",
                _bcrypt_hash_password(password),
                1 if is_admin else 0,
                environment,
                now,
                DEFAULT_TENANT_ID,
                DEFAULT_WORKSPACE_ID,
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


def save_api_key(conn: sqlite3.Connection, provider: str, api_key: str) -> None:
    """Persist an API key in the shared metadata table."""
    if not api_key:
        # Don't save empty keys, maybe delete if it exists?
        return
    key = f"{provider.lower()}.api_key"
    set_meta(conn, key, api_key)


def load_api_key(conn: sqlite3.Connection, provider: str, default: Optional[str] = None) -> Optional[str]:
    """Fetch an API key from the database."""
    key = f"{provider.lower()}.api_key"
    return get_meta(conn, key, default)


def save_openai_api_key(conn: sqlite3.Connection, api_key: str) -> None:
    """Persist the OpenAI API key in the shared metadata table."""
    save_api_key(conn, "openai", api_key)


def load_openai_api_key(conn: sqlite3.Connection, default: Optional[str] = None) -> Optional[str]:
    """Fetch the OpenAI API key from the database, if present."""
    return load_api_key(conn, "openai", default)


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
                user_id=r["user_id"] if "user_id" in r.keys() else "demo",
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
        try:
            user_id = r["user_id"] if r["user_id"] is not None else "demo"
        except (KeyError, IndexError):
            user_id = "demo"

        projects.append(
            Project(
                name=r["name"],
                description=r["description"] or "",
                status=r["status"] or "active",
                priority=priority,
                order_num=order_num,
                user_id=user_id,
            )
        )

    c.execute("SELECT * FROM chat_messages ORDER BY id ASC")
    chat_rows = c.fetchall()
    chat_messages: List[ChatMessage] = []
    for r in chat_rows:
        persona = r["persona"] or PERSONAS[0]
        if persona not in CHAT_PERSONAS:
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
    if "user_id" not in columns:
        c.execute("ALTER TABLE projects ADD COLUMN user_id TEXT DEFAULT 'demo'")
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
            user_id=kwargs.get("user_id", "demo"),
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
    insert_sql = """
        INSERT INTO tasks
        (title, project, status, priority, due_date, notes, owner, created_at,
         depends_on, recurrence_pattern, recurrence_end, time_estimated, time_logged, template_id, user_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
    new_id = _execute_insert_returning_id(
        conn,
        c,
        insert_sql,
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
    return new_id


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
            user_id=row["user_id"] if "user_id" in row.keys() else "demo",
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
    insert_sql = """
        INSERT INTO chat_messages (persona, role, kind, content, created_at)
        VALUES (?, ?, ?, ?, ?)
        """
    new_id = _execute_insert_returning_id(
        conn,
        c,
        insert_sql,
        (msg.persona, msg.role, msg.kind, msg.content, created_at),
    )
    conn.commit()
    return new_id


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

    insert_sql = """
        INSERT INTO external_sources (name, kind, connected, last_sync)
        VALUES (?, ?, 1, ?)
        """
    new_id = _execute_insert_returning_id(conn, c, insert_sql, (name, kind, now))
    conn.commit()
    return new_id


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
    insert_sql = """
        INSERT INTO document_operations (
            title, project_id, integration_type, external_id, operation, status, persona,
            version_tag, diff_path, external_company, started_at, completed_at, notes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
    new_id = _execute_insert_returning_id(
        conn,
        c,
        insert_sql,
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
    return new_id


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
    insert_sql = """
        INSERT INTO note_links (project_id, integration_type, external_id, title, description, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """
    new_id = _execute_insert_returning_id(
        conn,
        c,
        insert_sql,
        (project_id, integration_type, external_id, title, description, created_at),
    )
    conn.commit()
    return new_id


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
        SELECT id, project_id, event_type, payload, created_at, hash_prev, hash_curr, user_id
        FROM project_events
        {where}
        ORDER BY datetime(created_at) DESC, id DESC
        LIMIT ?
    """
    try:
        rows = cursor.execute(query, params).fetchall()
    except sqlite3.OperationalError:
        # Table/column might not exist yet on very old databases.
        fallback_query = f"""
            SELECT id, project_id, event_type, payload, created_at, hash_prev, hash_curr
            FROM project_events
            {where}
            ORDER BY datetime(created_at) DESC, id DESC
            LIMIT ?
        """
        try:
            rows = cursor.execute(fallback_query, params).fetchall()
        except sqlite3.OperationalError:
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
                "user_id": row["user_id"] if "user_id" in row.keys() else None,
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
    payload_json = json.dumps(payload_dict, sort_keys=True, default=str)

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
    tenant_id = None
    workspace_id = None
    try:
        cursor.execute(
            "SELECT tenant_id, workspace_id FROM projects WHERE name = ?",
            (project_id,),
        )
        row = cursor.fetchone()
        if row:
            tenant_id = row["tenant_id"] if "tenant_id" in row.keys() else None
            workspace_id = row["workspace_id"] if "workspace_id" in row.keys() else None
    except sqlite3.OperationalError:
        tenant_id = None
        workspace_id = None

    _log_immutable_audit_ledger_event(
        project_id=project_id,
        event_type=event_type,
        entity_type=entity_type,
        entity_id=entity_id,
        payload=payload or {},
        user_id=user_id,
        tenant_id=tenant_id,
        workspace_id=workspace_id,
    )
    return hash_curr


def _log_immutable_audit_ledger_event(
    *,
    project_id: str,
    event_type: str,
    entity_type: Optional[str],
    entity_id: Optional[str],
    payload: Dict[str, Any],
    user_id: str,
    tenant_id: Optional[str],
    workspace_id: Optional[str],
) -> None:
    try:
        from assistant_core.immutable_audit_ledger import (
            get_immutable_audit_ledger_module,
        )
    except Exception:
        logger.debug("Immutable audit ledger module unavailable", exc_info=True)
        return

    try:
        ledger_module = get_immutable_audit_ledger_module()
        ledger_module.record_project_event_sync(
            project_id=project_id,
            event_type=event_type,
            entity_type=entity_type,
            entity_id=entity_id,
            payload=payload,
            user_id=user_id,
            tenant_id=tenant_id,
            workspace_id=workspace_id,
        )
    except Exception:
        logger.exception("Immutable audit ledger logging failed for project event")
