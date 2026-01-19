# ADR 0002: Unified Event Journal and Logging SDK

Status: Accepted
Date: 2025-01-05

## Context
The platform requires auditability across autonomous agents and orchestration decisions. Current logging is fragmented and does not provide a single, queryable timeline for cross-agent workflows.

## Decision
- Adopt a unified, append-only Event Hub as a first-class platform subsystem.
- Require all components (agents, orchestrator, OS adapters, UI services) to emit through a shared logging SDK.
- Enforce an event-first pattern with INTENT and OUTCOME events for meaningful actions.
- Use SQLite (WAL mode) as the primary Event Hub store with periodic JSONL exports for portability.
- Maintain per-agent local journals as subordinate replicas optimized for privacy and local forensics.

## Options Considered
1. Per-module logs without a shared schema
   - Rejected: no unified timeline, poor auditability, hard to query.
2. Centralized logging without agent-local journals
   - Rejected: weak local forensics and privacy constraints.
3. Unified Event Hub with shared SDK and per-agent journals
   - Accepted: consistent audit trail, local-first resilience, cross-agent correlation.

## Consequences
- All meaningful operations must emit structured events with correlation_id and causation_id.
- Logging becomes a required dependency for core workflows.
- New policy decisions (redaction, visibility) must be implemented at the Event Hub level.

## Follow-ups
- Implement Event Hub service and SDK scaffolding.
- Wire emitters into task dispatch, file operations, and resource control paths.
- Add Journal UI views for per-agent summaries and team timelines.
