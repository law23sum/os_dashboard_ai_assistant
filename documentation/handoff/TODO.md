# TODO Backlog

Updated: 2025-02-17

## P0 – Blockers
- `assistant_hub/api/server.py`, `backend_api/routers/*`: add auth middleware (API key/bearer), role checks, and secure headers (HSTS toggle for dev). Acceptance: protected routes reject unauthenticated requests; integration test covering 200/401/403; docs updated.
- `assistant_hub/db.py` + new `migrations/`: introduce Alembic baseline for existing SQLite schema with indices on `projects.updated_at`, `tasks.status`, `diagnostics_log.created_at`. Acceptance: `alembic upgrade head` succeeds on fresh DB; pytest passes with migrated schema.
- `assistant_hub/api/routes`: enforce pagination + input validation on list endpoints (`projects`, `tasks`, `documents`, `diagnostics`). Acceptance: default limit=50, max=200; responses include `total`; tests for bounds and invalid params.
- CI config (GitHub Actions): add unified workflow running `pytest`, `npm test -- --runInBand`, lint (ruff/flake8 or eslint), and dependency scan (pip check + npm audit or trivy). Acceptance: workflow green locally via `osdash test --dry-run` plus CI definition present.

## P1 – Important
- `assistant_hub/api/server.py`, `assistant_hub/utils/logging.py` (new): structured JSON logging with `request_id`/`trace_id`; propagate header to frontend. Acceptance: logs emit correlation id; pytest asserts presence on sample request.
- `assistant_hub/observability` (new): expose `/metrics` using `prometheus-fastapi-instrumentator`; add gauges for request latency/error rate. Acceptance: curl `/metrics` returns prometheus text; unit test asserts key metrics present.
- `frontend/src/lib/apiClient.ts`, `frontend/src/pages/*`: wire real data for observability (runtime diagnostics stream) and capsules/integrations where mocked. Acceptance: components render data from API with loading/error states; MSW or integration test covering fetch.
- `assistant_hub/ui/terminal/workspace.py`: add load-test scaffolding hook (e.g., `osdash test --category load` invoking `scripts/load_tests.py`). Acceptance: dry-run lists load commands; failing load test marks suite red.
- `assistant_hub/scripts` (new): `db_migrate.py` helper to run Alembic and verify schema; used in CI. Acceptance: script exits 0 and prints applied revisions; included in README/doctor output.

## P2 – Nice-to-have
- `frontend/src/components/design-system/*` (new): codify buttons, cards, nav, stat blocks, table, skeletons with theme tokens. Acceptance: Storybook or unit snapshot; reused in dashboard/projects pages.
- `assistant_hub/api/eventing` (new): simple outbox table + background worker for audit/diagnostics events. Acceptance: inserting event queues row; worker drains to log; test covers idempotent retry.
- `docker-compose.yml`: add health checks for backend/frontend, env templating, and volume mounts for logs. Acceptance: `docker compose up` healthy; `osdash doctor` reports compose status.
- `docs/`: refresh README with osdash workspace examples and add architecture diagram from Blueprint V+1000. Acceptance: commands copy/paste runnable; linked from SPEC_ALIGNMENT.
