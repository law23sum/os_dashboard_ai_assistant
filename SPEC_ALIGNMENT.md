# Spec v6 Alignment – OS Dashboard AI Assistant

Updated: 2025-02-17

## What’s Implemented (matches Technical Spec Sheet v6)
- Unified launcher (`start_ui.py`) starts FastAPI + Vite/Electron; supports web and desktop modes.
- FastAPI surface exposes required domains: writer, projects, tasks, dashboard summaries, runtime diagnostics, search, office/vision/neural-architecture/security/threat monitoring.
- React UI mirrors Tkinter palette, ships routes for dashboard, projects/tasks, observability, docs, integrations, AI copilot panels, network monitoring, intent processor, office, capsules.
- Runtime diagnostics pipeline (`/api/runtime/diagnostics`, AppErrorBoundary beacons) and observability page wired to logs.
- Workspace automation scripts exist (autofix monitors, project orchestrator) and now surfaced via `osdash scan|test|run|doctor`.
- Env templates present (`env.*.example`), secrets pulled from env vars not code.

## Gaps / Missing vs Spec
- AuthN/AuthZ: no role model or token validation on routes; CSRF/security headers not enforced.
- Persistence: SQLite only; no migrations/indexing strategy, no ledger/event store, no CIR store abstraction.
- UI data flow: some pages still mock data (capsules, observability metrics, billing), pagination/caching absent on list endpoints.
- CI: lacks unified lint+test+security workflow; no dependency scanning (semgrep/trivy/gitleaks) or type checks gate.
- Observability: no structured metrics/traces, no correlation IDs on responses, no circuit breakers/timeouts.
- Performance/load: no pagination on `/projects`, `/tasks`, `/documents`; no caching on summary endpoints; no load-test scaffolding.
- Security baseline: missing rate limits, audit log hardening, secret scanning in CI, TLS defaults for local dev only.

## Conflicts / Ambiguities and Resolutions
- Multiple spec files and legacy docs: treated `Technical Spec Sheet (Version 6 Latest Version)` as the primary source and aligned numbering; legacy docs referenced only for lineage.
- Workspace scope: several archived repos discovered; per spec we flag them for later integration but do not block main repo work.
- CLI surface duplication (scripts vs CLI): chose to expose standardized scan/test/run/doctor through `osdash` while keeping automation scripts for batch runs.

## Prioritized Gap List
- **P0**: AuthZ/AuthN + security headers; pagination + input validation on API; unified CI (lint/test/security/typecheck); structured error schema + correlation IDs; dependency scans.
- **P1**: Metrics/tracing exporter; caching/ETag on summary endpoints; SQLite indexing + migration scripts; load-test scaffolding for dashboard/projects/tasks/runtime diagnostics.
- **P2**: Role-based UI states (admin/help/billing), integration packs (capsule marketplace wiring), multi-tenant data separation, desktop build hardening (codesigning, sandbox). 
