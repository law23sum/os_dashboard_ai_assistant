# Project Management System (PMS)

This document summarizes the PMS core model, deterministic scheduler, scoping rules, and integrated subsystems (runs, documents, journal, finance, audit). It reflects the `/api/pms` surface used by the desktop + web UI.

## Canonical Truth vs Derived Indices
- Canonical truth is `tasksById` (and `epicsById`) stored in `pms_tasks` / `pms_epics`.
- Scheduler indices are derived views rebuilt on demand; they are not persisted.
- Determinism is anchored on `enqueue_time` (falling back to `created_at`) and stable tie-breaks.

## Core Hierarchy
Project → Epic → Task → Todo

### Project
Fields: `project_id`, `name`, `mode` (`personal|enterprise`), `scope_type`, `scope_id`, `config`, `budget`, `created_at`, `updated_at`.

### Epic
Fields: `epic_id`, `project_id`, `title`, `description`, `acceptance_criteria`, `status`, timestamps.  
Rollups are derived from task counts and completion ratios.

### Task
Fields: `task_id`, `project_id`, `epic_id?`, `title`, `deliverable_spec`, `acceptance_criteria`, `priority`, `category`, `task_type`, `status`, `enqueue_time`, timestamps.

### Todo
Fields: `todo_id`, `task_id`, `text`, `status`, `position`, timestamps.  
Todo ordering is explicit via `position` to guarantee stable ordering after reloads.

## Scheduler (What’s Next)
1. Pick the highest priority tier with eligible tasks (excludes `DONE`/`ARCHIVED`; `BLOCKED` filtered by default).
2. Within the tier, select the lane whose head task has the oldest `enqueue_time`.
3. Tie-break by `lane_key` lexicographically, then `task_id`.
4. `next_task` mutates by updating `enqueue_time`; `peek_next` is non-mutating.

Lanes are keyed by `(category, task_type)` and are FIFO queues by default.

### Scheduler Policy Interface
- The default policy is `OldestHeadPolicy` (oldest `enqueue_time` wins).
- Policies are pluggable so future strategies can be added without changing storage.
- Indices are always rebuilt from canonical task state on load.

## Documents & Publishing
- Revisions are content-addressed (`sha256(content)`) and stored in `pms_document_blobs`.
- Document records point to `latest_revision_hash` and `published_revision_hash`.
- Default views show the published revision; history is explicit.
- Older published revisions are hidden by default (history only).

## Execution Runs & Artifacts
- Runs track execution of tasks/todos.
- Artifacts are stored as files with metadata (`sha256`, size, mime, filename).
- UI surfaces list + download; JSON/table previews can be layered later.

## Meeting Journal (Official Collaborative Discussions Journal)
- Meeting records store metadata, participants, and recording status.
- Transcript segments default to `Speaker N` labels when diarization is missing.
- Journal blocks are generated deterministically with a fixed section taxonomy:
  `Comments`, `KnowledgeTransfer`, `DisputableDebate`, `ChallengesRisks`,
  `SolutionsMitigations`, `ProposalRaised`, `MisunderstandingClarification`,
  `TechnicalDesign`, `CommonDiscussions`, `Questions`, `NextSteps`.
- Speaker mapping requires explicit consent and is logged in the audit ledger.

## UX Overview (Web)
- Global shell uses a platform dropdown, category list, and left-side feature rail.
- Project detail tabs: Overview, Epics, Tasks, Schedule, Runs, Documents, Journal, Finance, Audit, Settings.
- “Next Task” panels read from the deterministic scheduler; “peek” is non-mutating.
- Runs show artifacts with download links and lightweight previews.
- Documents expose publish pointers, revision history, and new revision inputs.
- Journal flow supports audio upload (with consent), transcript ingestion, and structured blocks.
- Finance panels show expense + labor rollups; audit pages surface ledger entries.

## Configuration & Templates
- Project config supports custom priority tiers and category/type vocabularies.
- Template packs seed default configuration (`dev`, `research`, `writing`, `finance`, `cyber`).

## Finance & Time
- Expenses and time entries are linked to project/epic/task.
- Rollups compute expense total, labor total, and combined total.
- Finance mutations emit audit events.

## Audit & Evidence
- `project_events` is append-only with a hash chain.
- Mutations across tasks, documents, runs, journal, and finance emit events.
- Evidence packs bundle audit events, documents, and run summaries.

## Scoping (Personal vs Enterprise)
- Personal scope: `scope_type=user` and `scope_id=user_id`.
- Enterprise scope: `scope_type=tenant` and `scope_id=workspace_id`.
- `/api/pms` endpoints enforce scope via the project record.
- Admin sample projects (from deliverables + `documents/projects`) are flagged `is_sample` and hidden from non-admins.

## API Quick Examples

Create task:
```json
POST /api/pms/projects/{projectId}/tasks
{
  "title": "Write spec",
  "priority": "P1",
  "category": "Engineering",
  "task_type": "Spec",
  "status": "TODO"
}
```

Peek schedule:
```http
GET /api/pms/projects/{projectId}/schedule/peek?count=5
```

Add document revision:
```json
POST /api/pms/documents/{documentId}/revisions
{
  "content": "# Draft spec\n",
  "metadata": { "author": "Aria" }
}
```

Attach meeting audio:
```json
POST /api/pms/meetings/{meetingId}/audio
{
  "filename": "sync.wav",
  "content_base64": "<base64>",
  "recording_consent": true
}
```
