"""Core dataclasses and enums for the Project Management System (PMS)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

PMS_PROJECT_MODES = ("personal", "enterprise")
PMS_TASK_STATUSES = ("TODO", "IN_PROGRESS", "BLOCKED", "DONE", "ARCHIVED")
PMS_TODO_STATUSES = ("TODO", "DONE")
PMS_RUN_STATUSES = ("queued", "running", "succeeded", "failed", "needs_review")
PMS_DOCUMENT_KINDS = ("spec", "notes", "runbook", "manuscript", "draft", "journal")
PMS_DOCUMENT_VISIBILITY = ("private", "team", "enterprise", "public")
PMS_DEFAULT_PRIORITY_TIERS = ("P0", "P1", "P2", "P3")
PMS_JOURNAL_SECTION_TYPES = (
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
)


@dataclass
class PmsProject:
    project_id: str
    name: str
    mode: str
    scope_type: str
    scope_id: str
    status: str
    created_at: str
    updated_at: str
    config: Dict[str, Any] = field(default_factory=dict)
    budget_amount: Optional[float] = None
    budget_currency: Optional[str] = None
    created_by: Optional[str] = None


@dataclass
class PmsEpic:
    epic_id: str
    project_id: str
    title: str
    description: str
    acceptance_criteria: str
    status: str
    created_at: str
    updated_at: str


@dataclass
class PmsTask:
    task_id: str
    project_id: str
    epic_id: Optional[str]
    title: str
    deliverable_spec: str
    acceptance_criteria: str
    priority: str
    category: str
    task_type: str
    status: str
    created_at: str
    updated_at: str
    enqueue_time: str


@dataclass
class PmsTodo:
    todo_id: str
    task_id: str
    text: str
    status: str
    position: int
    created_at: str
    updated_at: str


@dataclass
class PmsExecutionRun:
    run_id: str
    project_id: str
    epic_id: Optional[str]
    task_id: Optional[str]
    todo_id: Optional[str]
    input_params: Dict[str, Any]
    status: str
    started_at: str
    ended_at: Optional[str]
    summary: Optional[str]
    created_by: Optional[str]


@dataclass
class PmsArtifact:
    artifact_id: str
    run_id: str
    project_id: str
    kind: str
    filename: Optional[str]
    display_name: Optional[str]
    mime_type: Optional[str]
    size_bytes: Optional[int]
    sha256: Optional[str]
    created_at: str
    storage_path: Optional[str]


@dataclass
class PmsDocument:
    document_id: str
    project_id: str
    epic_id: Optional[str]
    task_id: Optional[str]
    title: str
    kind: str
    visibility: str
    created_at: str
    updated_at: str
    published_revision_hash: Optional[str]
    latest_revision_hash: Optional[str]


@dataclass
class PmsDocumentRevision:
    revision_hash: str
    document_id: str
    parent_hash: Optional[str]
    author: Optional[str]
    created_at: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PmsDocumentBlob:
    revision_hash: str
    blob_path: str
    size_bytes: Optional[int]
    created_at: str
    content_type: Optional[str]


@dataclass
class PmsExpenseEntry:
    expense_id: str
    project_id: str
    epic_id: Optional[str]
    task_id: Optional[str]
    amount: float
    currency: str
    category: Optional[str]
    vendor: Optional[str]
    description: Optional[str]
    occurred_at: str
    created_at: str
    updated_at: str
    created_by: Optional[str]


@dataclass
class PmsTimeEntry:
    time_entry_id: str
    project_id: str
    epic_id: Optional[str]
    task_id: Optional[str]
    actor_id: Optional[str]
    role: Optional[str]
    duration_minutes: int
    hourly_rate: float
    occurred_at: str
    created_at: str
    updated_at: str
    created_by: Optional[str]


@dataclass
class PmsMeetingSession:
    meeting_id: str
    project_id: str
    epic_id: Optional[str]
    task_id: Optional[str]
    title: str
    started_at: str
    ended_at: Optional[str]
    participants: List[str]
    language: Optional[str]
    created_by: Optional[str]
    created_at: str
    recording_status: Optional[str]
    audio_path: Optional[str]
    transcript_status: Optional[str]
    journal_status: Optional[str]


@dataclass
class PmsTranscriptSegment:
    segment_id: Optional[int]
    meeting_id: str
    ts_start: float
    ts_end: float
    speaker_label: str
    text_original: str
    text_translated: Optional[str]
    confidence: Optional[float]


@dataclass
class PmsJournalBlock:
    block_id: str
    meeting_id: str
    ts_start: float
    ts_end: float
    section_type: str
    speaker_label: Optional[str]
    content: str
    references: Dict[str, Any] = field(default_factory=dict)
    created_at: str = ""


@dataclass
class PmsSpeakerMapping:
    meeting_id: str
    speaker_label: str
    display_name: str
    consent: bool
    created_at: str
    updated_at: str
