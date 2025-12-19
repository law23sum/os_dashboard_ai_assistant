# TODO Backlog (Spec v6 aligned)

Updated: 2025-12-17  
Priority: P0 (urgent), P1 (important), P2 (later). Repo: `os_dashboard_ai_assistant`.

## P0
- **CI quality gate** — Add GitHub Actions workflow running lint (`ruff`/`flake8`, `npm run lint`), tests (`pytest -q`, `npm test -- --runInBand`), and scans (`pip audit`, `gitleaks`/`semgrep`). Files: `.github/workflows/ci.yml`, `requirements-dev.txt`, `frontend/package.json` scripts. Tests: workflow green on PRs; local `pytest`/`npm test` succeed.
- **Deterministic persistence** — Standardize DB path to `~/.osdash/data/assistant_hub.db`, add Alembic/SQLModel migrations with `schema_migrations`, indexes on project/task lookups, and pagination on list endpoints. Files: `assistant_hub/db.py`, new `assistant_hub/migrations/`, relevant routers. Tests: migration runs on clean env; list endpoints enforce `page_size` caps and return paged results.
- **API contracts + observability** — Standardize response envelope (`request_id`, `status`, `data`, `error`), add `/healthz` + `/readyz`, structured JSON logging, and ensure correlation IDs propagate to UI. Files: `assistant_hub/api/server.py`, `assistant_hub/logging_config.py`, `frontend/src/api/*.ts`. Tests: pytest for health endpoints and request ID header; vitest for client parsing.
- **Spec canon completion** — With `documentation/consolidated_md/technical_spec_v6_alignment.md` restored, backfill lower_snake_case chapter summaries (`00_*` … `10_*`) mapped to legacy sources. Tests: markdown lint; internal links resolve.
- **Test tooling baseline** — Install/declare pytest + plugins in dev requirements; ensure `python -m pytest tests/test_osdash_harness.py` passes locally. Files: `requirements-dev.txt` (or update `requirements.txt`), `README.md` test instructions. Tests: pytest available in env; harness tests green.

## P1
- **AuthN/AuthZ baseline** — Token/session middleware with roles (admin/operator/viewer) applied to mutating routes; `.env.template` enumerates secrets. Files: `assistant_hub/security/auth.py`, FastAPI deps, `.env.template`. Tests: pytest covering allowed/denied routes.
- **Design system & UI states** — Create shared UI primitives (Card/Stat/Table/EmptyState/Skeleton/Alert) in `frontend/src/components/ui/` and apply to Dashboard, Observability, Projects, Tasks pages with empty/error/loading states. Tests: vitest render snapshots; manual smoke via `npm run dev:web`.
- **Runtime log hygiene** — Rotate NDJSON runtime diagnostics with retention (size/time based), expose metadata endpoint for UI. Files: `backend_api/routers/runtime_diagnostics.py`, logging config. Tests: pytest simulating log rollover and metadata endpoint.
- **Workspace harness polish** — Document new run-level UUID + timeout behavior, add CLI flag for per-command timeout/autofix, and surface report paths in `README.md`. Files: `assistant_hub/ui/terminal/cli.py`, `assistant_hub/ui/terminal/harness.py`, `README.md`. Tests: expand `tests/test_osdash_harness.py` to cover workspace report run_id and timeout flag.

## P2
- **Async job queue scaffold** — Add lightweight queue (RQ/Celery/Arq) for long-running AI/driver tasks with status polling; wire to `/ai/*` routers. Files: `assistant_hub/core/jobs.py`, FastAPI startup/shutdown hooks. Tests: unit test enqueues/completes a job and surfaces status.
- **Load-test harness** — Add k6/locust scripts targeting `/dashboard/summary`, `/tasks`, `/runtime/diagnostics`; document run instructions. Files: `tools/loadtest/`, `docs/loadtest.md`. Tests: scripts execute locally and report latencies.
- **Secrets hygiene** — Add `.env.template` with required vars, document secrets handling, and include gitleaks/semgrep allowlists as needed. Files: `.env.template`, `.github/workflows/ci.yml`, `documentation/DEPLOYMENT.md`. Tests: CI secret scan passes or allowlist documented.
- **Billing & policy stubs** — Implement minimal usage/billing models with rate-limit/policy hooks and admin toggle. Files: `assistant_hub/api/server.py`, `assistant_hub/services/billing.py`. Tests: pytest ensuring quotas enforced and errors carry request IDs.
