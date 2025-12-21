# Spec Alignment (Technical Spec Sheet v6)

Updated: 2025-12-17  
Sources: `Technical Spec Sheet (Version 6 Latest Version).txt`, `documentation/README.md`, `documentation/consolidated_md/technical_spec_v6_alignment.md`.

## Implemented
- **Layered surfaces**: React web/desktop UI (`frontend/`) with rich routing (dashboard/projects/tasks/logs/settings/integrations/docs); FastAPI backend (`assistant_hub.api.server:create_app`) plus compatibility server in `backend_api`; legacy Tkinter UI retained.
- **Control/data planes**: `/system`, `/planes/status`, `/runtime/diagnostics` endpoints with correlation IDs; Observability page reads NDJSON runtime diagnostics and system stats.
- **Workspace automation**: `osdash` CLI (scan/test/run/doctor + project/office/history helpers) and workspace harness in `assistant_hub.ui.terminal` writing JSON reports under `logs/osdash/`; scripts for autofix and test matrix generation.
- **Config/deployment**: Env-driven config (`assistant_hub.config`), optional TLS from `certs/`, Dockerfile + docker-compose + Procfile, GitHub Actions release builders, unified launcher `start_ui.py`.
- **Documentation spine**: Spec index restored at `documentation/consolidated_md/technical_spec_v6_alignment.md` to map spec chapters to sources.

## Missing / Partial vs Spec
- **Quality gates**: No PR workflow for lint/tests/security (Python + JS); dependency/secret scans absent.
- **Persistence rigor**: No migrations or schema versioning; SQLite path differs by launcher; list APIs lack pagination/indexing/caching.
- **AuthN/AuthZ & governance**: No user/tenant/role enforcement or token middleware; policy plane, budget guardrails, and billing hooks are stubs.
- **Observability depth**: Metrics/traces missing; NDJSON logging lacks rotation/retention; health/readiness SLOs undefined.
- **Reliability patterns**: Timeouts/retries/backoff are inconsistent; idempotency/rate limits not standardized; error schema varies across routers.
- **Docs completeness**: Consolidated chapter summaries referenced in `documentation/README.md` are missing; only the index exists.
- **Security hygiene**: Example envs not validated; secure headers/CSRF not enforced; automated gitleaks/semgrep/trivy/pip-audit missing.

## Conflicts / Ambiguities
- Dual API entrypoints (`assistant_hub.api.server` vs `backend_api.main`) both mount routers; keep `assistant_hub.api.server` as canonical, retain legacy for compatibility only.
- SQLite location varies between `assistant_hub_gui` defaults and env overrides; converge on a single data dir (e.g., `~/.osdash/data/assistant_hub.db`) with migrations.
- UI expects live data but several routers return static/demo payloads; contracts lack typed schemas or versioning.
- Observability endpoints emit mixed shapes; need a unified diagnostic envelope that surfaces correlation IDs to UI.

## Prioritized Gap List
- **P0 CI + security** — Add GitHub Actions workflow for lint (ruff/flake8, eslint/prettier), tests (pytest, vitest), and scans (gitleaks/semgrep/pip audit). Publish harness JSON reports as artifacts.
- **P0 Persistence baseline** — Introduce migration/version table, deterministic data dir, seed script, and pagination for tasks/projects APIs.
- **P0 API contracts** — Typed request/response models, correlation IDs, and consistent error envelopes across dashboard/projects/logs; align UI fetches to these schemas.
- **P0 Doc summaries** — Regenerate the missing consolidated chapters (`00_mission_identity_agents.md` ... `10_meta_stack_layers.md`) linked from the restored index.
- **P1 AuthZ/AuthN** — Token/session layer with roles (admin/user/observer), middleware for protected routes, and tests.
- **P1 Observability** — Structured logging with rotation, readiness/liveness endpoints, and optional metrics exporter; surface correlation IDs to UI.
- **P2 Performance & reliability** — Timeouts/retries/backoff for outbound calls, caching/memoization for dashboards, and rate limits for expensive operations.
- **P2 Security hygiene** — Secure headers/CSRF where applicable, env validation, secret/dependency scans, and `.env.template` parity with examples.
