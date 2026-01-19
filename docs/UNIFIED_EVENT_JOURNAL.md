# Unified Event Journal and Logging SDK

Updated: 2025-01-05

## Purpose
Establish a single, append-only event journal that records every meaningful action, decision, and transition across AI OS, all agents, and OS adapters. The journal is the authoritative audit trail and the primary source for the "Journal" UI.

## Architecture Layers
1. Agent Runtime Layer (per agent, per host/VM/container)
   - Each agent runs inside its own isolation boundary.
   - Each agent has a dedicated local partition (read/write) for private artifacts and sensitive knowledge.
   - Host mounts (Desktop/Documents/Downloads) are read-only per policy.
2. Orchestration + Policy Layer (AI OS core)
   - Dispatches tasks, enforces read/write constraints, applies resource controls.
   - Emits policy decisions, denials, throttles, and recovery events.
3. Unified Observability + Journal Layer (central event hub)
   - A single, centralized event stream for the team timeline and aggregated views.
   - Per-agent journals are subordinate replicas optimized for local forensics.

## Non-Negotiable Constraints (Phase 1)
A) Isolation and storage
- Dedicated per-agent local partition for sensitive knowledge and working artifacts.
- Host Desktop/Documents/Downloads mounted read-only in every agent environment.
- Default scope (system root or user root) is recorded at session start.

B) Privileges
- Read-only host visibility via system APIs and read-only mounts.
- No kernel memory access or privileged writes outside the agent partition.
- Any privilege escalation requires explicit policy approval and logging.

C) Autonomy with accountability
- Agents may explore, question, and propose within allowed scope.
- All meaningful steps must emit structured events to prevent black-box behavior.
- Idle agents may read the Project Deliverables queue and propose epics/tasks/todos (read-only), with full logging.

## Event-First Pattern
- Every meaningful step emits at least two events: INTENT and OUTCOME.
- Micro-steps can be aggregated within a bounded operation that logs OPERATION_START and OPERATION_END.
- INTENT and OUTCOME are recorded via EventEmitter.emit_intent and EventEmitter.emit_outcome.

## Canonical Event Schema
Required fields (unless noted):
- event_id (ULID/UUID, sortable preferred)
- ts_utc (ISO-8601 UTC timestamp)
- host_id (stable machine identifier)
- os_family (linux | windows | macos)
- runtime_scope (host | vm | container)
- agent_id (agent identifier or "os_dashboard")
- session_id (created at session start)
- correlation_id (traces a multi-step workflow)
- operation_id (optional; groups micro-steps into a bounded operation)
- causation_id (optional parent event_id)
- event_type (controlled vocabulary below)
- severity (debug | info | notice | warning | error | critical)
- visibility (private | team | admin)
- project_ref (optional: project_id, epic_id, task_id)
- resource_snapshot (optional: cpu_pct, ram_mb, io_read_mb, io_write_mb, net_in_kb, net_out_kb)
- artifact_refs (optional list: kind, path_or_uri, hash, size_bytes)
- message (concise human-readable statement)
- payload (structured JSON per event_type)
- prev_event_hash (hash of previous event)
- event_hash (hash of current event)

## Controlled Event Taxonomy (v1)
Session and policy
- SESSION_START, SESSION_END
- CAPABILITY_REQUEST, CAPABILITY_GRANTED, CAPABILITY_DENIED
- POLICY_LOAD, POLICY_DECISION, POLICY_DENY_ACTION

Thinking / dialogue / governance
- THOUGHT, PLAN, QUESTION, ASSUMPTION
- DEBATE_OPEN, DEBATE_TURN, SUPPORT, REBUTTAL, DISPUTE, RESOLUTION
- DECISION, RATIONALE, RISK_NOTE, SAFETY_NOTE

Actions and system effects
- OPERATION_START, OPERATION_END
- TASK_CLAIM, TASK_HANDOFF, TASK_COMPLETE, TASK_BLOCKED
- READ_OPERATION, WRITE_OPERATION
- FILE_DIFF_CREATED, ARTIFACT_CREATED, ARTIFACT_UPDATED, ARTIFACT_DELETED
- BUG_DETECTED, CRASH_DETECTED, RECOVERY_ATTEMPT, RECOVERY_SUCCESS, RECOVERY_FAIL

Resource and stability
- RESOURCE_POLICY_APPLIED, THROTTLE_APPLIED, THROTTLE_RELEASED
- FREEZE_DETECTED, WATCHDOG_TRIGGERED
- IO_PRESSURE, MEMORY_PRESSURE, CPU_PRESSURE

Cross-agent collaboration
- MESSAGE_SENT, MESSAGE_RECEIVED
- HELP_REQUESTED, HELP_PROVIDED
- CONSENSUS_REACHED, ESCALATION_TO_MASTER_CHRIS

## Logging Behavior Rules
1. No silent work
   - Any state change, file operation, command execution, or metadata read MUST emit INTENT and OUTCOME.
2. Correlation is mandatory
   - Multi-step workflows share a correlation_id.
   - OUTCOME should reference causation_id (the INTENT or inbound message).
3. Timestamps are consistent
   - Use UTC for ordering; local time may be recorded as an extra field.
4. Append-only, tamper-evident logs
   - No in-place edits.
   - Hash chaining required; log rotation emits ROTATION events.
5. Visibility and sensitive knowledge
   - private events may contain sensitive knowledge.
   - team events are shareable across agents.
   - admin events are for AI OS policy and Master Chris oversight.
   - Redactions emit REDACTION_APPLIED referencing the original event_id.

## Event Hub Requirements
- Local-first service using IPC (Unix socket / named pipe).
- Persists to SQLite (WAL mode) with periodic JSONL segment exports.
- Provides query endpoints for timeline rendering and aggregation:
  - filters: agent_id, session_id, time range, event_type, project_ref, visibility.
  - reports: per-agent totals, cross-agent collaboration counts, anomaly detection.
- Journal views are rendered from the immutable audit ledger (authoritative) and may
  merge per-agent private journals for local forensics.

## SDK Components
- EventEmitter: emit(), emit_intent(), emit_outcome(), emit_error(), emit_question(), emit_debate_turn().
- EventSink: LocalAppendOnlySink, HubSink, ConsoleSink (dev only).
- EventHub: ingest(), validate schema, append, index, query().
- JournalRenderer: builds per-agent journal, team journal, and collaboration views.

## Journal View Behavior (AI OS UI)
A) Team Journal Summary
- Selected time window (default last 24h)
- Totals by event_type, warnings/errors
- Cross-agent collaboration counts
- Active sessions and status

B) Per-Agent Contribution Table
- Total events, thoughts, plans, questions, actions, debates, disputes, resolutions, recoveries
- Resource anomalies (throttles, freezes, watchdog triggers)
- Links to drill-down timeline

C) Collaboration Journal
- Ordered timeline filtered to cross-agent events plus DECISION and RESOLUTION
- Each entry shows timestamp, agent, event_type, message, correlation_id, artifacts

## Acceptance Criteria
- 100% of meaningful operations emit events using the shared SDK.
- Correlation_id threads are visible end-to-end across agents.
- Logs are append-only and hash-chained.
- Policy constraints are enforced and violations emit POLICY_DENY_ACTION.
- Journal UI displays per-agent totals and team collaboration timeline with drill-down.
