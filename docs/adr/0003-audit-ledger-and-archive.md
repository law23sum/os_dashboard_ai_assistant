# ADR 0003: Immutable Audit Ledger and Secure Archive Engine

Status: Accepted
Date: 2026-01-05

## Context
The platform needs a governed, tamper-evident record of agent and orchestrator behavior.
Existing logs and the Event Hub are not append-only and do not provide a canonical hash
chain with sealed, encrypted archives.

## Decision
- Introduce a dedicated audit package under `assistant_hub/audit` that defines the
  canonical AuditEvent schema (schema_version = 1) and hashing rules.
- Use UUIDv4 for event_id (ULID preferred, but no ULID dependency is available).
- Compute event_hash with SHA-256 over canonical JSON: UTF-8, sorted keys, no whitespace,
  and excluding `event_hash` itself.
- Store the ledger in a dedicated SQLite database (`audit_ledger.db`) using WAL mode,
  FULL synchronous, and append-only triggers to block UPDATE/DELETE.
- Centralize ingestion through the EventHub service (FastAPI POST `/audit/events`) and
  the Audit SDK (EventEmitter + helpers). No direct writes to the ledger from agents.
- Archive format: JSONL segments + manifest. Optional gzip compression supported.
- Integrity: per-event hash chaining plus per-archive HMAC-SHA256 seal of the manifest.
- Encryption at rest: AES-GCM using the `cryptography` package with key files stored
  outside the repo (env-configurable paths).
- Key management: file-based keys loaded from env-configurable paths; keys are generated
  on first use if missing and never committed.

## Integration Map (Initial)
- `assistant_hub/terminal.py`: COMMAND_INTENT/COMMAND_OUTCOME for shell execution.
- `backend_api/routers/chat.py`: MESSAGE_SENT/MESSAGE_RECEIVED for chat flow.
- `backend_api/routers/tasks.py`: TASK_CLAIM/TASK_COMPLETE/TASK_BLOCKED on status changes.
- `backend_api/main.py`: SESSION_START/SESSION_END with policy snapshot.
- `assistant_hub/integrations/filesystem_integration.py`: READ_OPERATION for file previews.

## Options Considered
1. Reuse existing Event Hub schema without a new ledger
   - Rejected: not append-only, hash chain is per-agent and mutable, no archive sealing.
2. Store audit events inside the primary application database
   - Rejected: higher blast radius and migration risk; weaker append-only enforcement.
3. Dedicated audit ledger database with EventHub ingestion
   - Accepted: clear separation, deterministic append-only chain, minimal impact on
     existing app schema.

## Threat Model
- The ledger is tamper-evident, not physically immutable. An attacker with filesystem
  access can delete or replace files; detection is provided via hash chain and archive seals.
- Archives provide stronger integrity (sealed + encrypted) but remain vulnerable to
  full-disk compromise unless keys are protected.

## Consequences
- Core workflows must emit structured events through the Audit SDK or EventHub.
- Operational configuration must provide key paths for sealing/encryption.
- Archive rotation and verification become standard operational tasks.
