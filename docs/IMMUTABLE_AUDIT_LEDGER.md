# Immutable Audit Ledger and Secure Archive Engine

Updated: 2026-01-05

## What it is (and is not)
- The ledger is tamper-evident, append-only, and hash-chained.
- It is not physically immutable: an attacker with filesystem access can delete files.
- Archives add sealed and encrypted bundles for stronger integrity at rest.

## How it works
1. Agents and services emit structured AuditEvent payloads via the Audit SDK.
2. EventHub validates, redacts secrets, enforces size limits, and appends to the ledger.
3. Each event includes `prev_hash` and `event_hash` computed from canonical JSON.
4. Archives rotate into encrypted bundles (JSONL + manifest) with HMAC seals.

Guardrail: ad-hoc print logs are not the authoritative record. Use the Audit SDK
or EventHub ingestion for any event that must be audited.

## Ledger storage
- SQLite (WAL + FULL synchronous) with append-only triggers on `audit_events`.
- Ledger DB path is configured via `AUDIT_LEDGER_DB_PATH` (default: `AUDIT_BASE_DIR/audit_ledger.db`).

## Archive format
- Segment file: JSONL (optional gzip) with canonical JSON per line.
- Manifest: metadata + seal (HMAC-SHA256).
- Bundle: ZIP containing segment + manifest, encrypted with AES-GCM.

## CLI commands
Examples (from repo root):
```bash
python cli.py audit emit --event-type SESSION_START --message "dev start" --payload '{"example":true}'
python cli.py audit verify-ledger
python cli.py audit rotate
python cli.py audit list-archives
python cli.py audit verify-archive /path/to/archive.zip.enc
python cli.py audit restore-archive /path/to/archive.zip.enc /tmp/audit_restore
```

## Verification
- Ledger: `verify-ledger` replays the hash chain and reports the first mismatch.
- Archive: `verify-archive` checks seal, segment sha256, and hash continuity.

## Querying events
- API: `GET /api/audit/events` with filters `agent_id`, `event_type`, `session_id`.
- SDK: use `EventHub.query_events(...)` from `assistant_hub.telemetry`.

## Key management
- HMAC key: `AUDIT_HMAC_KEY_PATH` (default: `AUDIT_KEY_DIR/audit_hmac.key`)
- AES-GCM key: `AUDIT_ENCRYPTION_KEY_PATH` (default: `AUDIT_KEY_DIR/audit_encryption.key`)
- Keys are generated on first use and never committed.

## Environment variables
- `AUDIT_BASE_DIR`, `AUDIT_KEY_DIR`
- `AUDIT_LEDGER_DB_PATH`, `AUDIT_ARCHIVE_DIR`, `AUDIT_ARTIFACT_DIR`
- `AUDIT_ARCHIVE_ROTATION_MODE` (daily|size)
- `AUDIT_ARCHIVE_ROTATION_MAX_EVENTS`
- `AUDIT_ARCHIVE_RETENTION_DAYS`
- `AUDIT_HMAC_KEY_PATH`, `AUDIT_ENCRYPTION_KEY_PATH`
- `AUDIT_MAX_EVENT_BYTES`
- `AUDIT_ARCHIVE_COMPRESSION` (none|gzip)
