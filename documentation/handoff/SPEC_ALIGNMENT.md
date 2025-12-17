# Spec v6 Alignment — Current State

Updated: 2025-02-16

## Implemented vs Spec
- React/Electron UI with routes spanning dashboard, AI ops, observability, integrations; Tk palette preserved.
- Runtime diagnostics pipeline (`/runtime/diagnostics` POST/GET) feeding Observability page.
- Workspace harness exposed via `osdash scan|test|run|doctor` and aggregated report (`write_workspace_report`) now surfaced at `/runtime/harness-report`.
- Unified launcher (`start_ui.py`) starts FastAPI + Vite/Electron; StripPrefix middleware allows `/api/*` compatibility.
- Canon specs stored in `Technical Spec Sheet (Version 6 Latest Version).txt`; documentation index in `documentation/README.md`.

## Missing / Out-of-Spec
- **Planes separation (Spec §2)**: Data/Control/Governance planes are conceptual stubs; single process handles all planes and storage.
- **Ledger & capsule graph (Spec §3.7, §8)**: No persisted ledger, hash chaining, or capsule orchestration; UI “Project Ledger” is a placeholder.
- **Project Intelligence & TRF UI (Spec §4.5–§4.8)**: No reasoning traces, risk scores, or TRF queries exposed via API/UI.
- **Driver governance (Spec §5.12)**: No admission control/backpressure; execution planner remains a document only.
- **Collaboration/tenancy (Spec §3.1, §7.12)**: Single-user defaults; no authN/authZ hooks or tenant roles.
- **Research/Digital Twin workspaces (Spec §7.4, §7.11)**: Routes exist but lack backend connectors and data models.
- **Data governance (Spec §6)**: No migrations, integrity protections, or residency/audit stores.
- **Security & CI (Spec §6, §8)**: No auth, CSRF, or dependency scans in CI; only artifact builds run.
- **Observability breadth (Spec §7)**: File-based logs only; no metrics/traces or rotation/retention policy.

## Conflicts / Ambiguities
- Spec references `technical_spec_v6_alignment.md` which is missing; will recreate under `documentation/consolidated_md/`.
- Multiple archived git roots detected in `../Archive/...`; treated as out of scope for now (documented in TODO/DECISIONS).
- `apiPath` defaults to `/api/*` while backend exposes both prefixed/unprefixed routes via StripPrefix; dual behavior retained for compatibility.

## Prioritized Gap List
- **P0**: Introduce DB migrations + ledger table with hash-chain; expose `/api/projects/ledger` and render in React Projects view. Tests: alembic upgrade on clean env; pytest coverage for ledger writes; UI shows live events.
- **P0**: Auth/authz skeleton (users/roles/tenants) gating mutating routes; env-based secrets template. Tests: FastAPI dependency enforces role; unauthorized calls rejected.
- **P0**: CI pipeline for lint/test/security (pytest + frontend tests + `pip check`/`npm audit`) and harness dry-run gating PRs.
- **P1**: Plane adapters (Data/Control/Governance) with health endpoints; plane cards consume real readiness metrics.
- **P1**: Project Intelligence + TRF UI/API (risk scores, reasoning traces) with persisted summaries.
- **P1**: Research/Digital Twin workspace backends with minimal mock providers and telemetry surfaced in React.
- **P2**: Observability upgrades (metrics/traces via OpenTelemetry exporters, log rotation/retention for diagnostics and harness reports).
