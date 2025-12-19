## p0
- backend_api/ assistant_hub.api.server: consolidate router bootstrap so `assistant_hub.api.server` is canonical and `backend_api.main` mounts it for compatibility; add `/api/v1` prefix and uniform error/correlation middleware; acceptance: app serves legacy and v1 routes, responses include `correlation_id`, regression pytest green.
- assistant_hub/db.py + new migrations folder: introduce Alembic migrations, schema version table, and deterministic data dir under `~/.osdash` or env override; acceptance: `alembic upgrade head` succeeds on clean env, database created automatically via launcher, pytest passes DB init tests.
- assistant_hub/api/auth (new): add token-based auth with roles (admin/operator/user/viewer) and dependency guards on sensitive routes; acceptance: protected routes return 401/403 without token, sample token works, contract tests cover dashboard/projects/tasks.
- frontend/src (design system): add shared shell (nav/header), loading/error/skeleton states, and typed API client generated from OpenAPI; acceptance: Vite dev runs, vitest covering client hooks, key pages fetch live data with graceful error/empty states.
- .github/workflows (new): CI workflow running ruff+pytest, eslint+prettier, vitest, semgrep (baseline); acceptance: workflow passes locally via `npm test` + `pytest`, CI file present.

## p1
- assistant_hub/api/runtime_diagnostics: add structured metrics (Prometheus) and WebSocket feed for diagnostics; acceptance: `/api/metrics` exposes counters/histograms, websocket streaming works with sample events, tests simulate event push.
- frontend/pages/logs: new Logs & Observability page consuming diagnostics feed with filters; acceptance: renders list/stream, handles reconnect, vitest coverage for UI states.
- scripts/osdash (new CLI): unify repo scan/test/run doctor commands leveraging existing scripts; acceptance: `osdash scan|test|run|doctor` available via entrypoint, unit tests validate command dispatch.
- documentation: keep ARCHITECTURE_OVERVIEW, SPEC_ALIGNMENT, BLUEPRINT_V_1000 updated after each increment; acceptance: docs reference latest commands and schema.

## p2
- Performance: add pagination/default limits to list endpoints, indexes on project_id/updated_at; acceptance: responses paginated, DB indexes created via migration, tests validate limits.
- Reliability: add retry/backoff wrappers for external integrations and command runner; acceptance: transient failures retried with cap, unit tests cover backoff.
- Security: tighten CORS and secure headers, CSRF token for browser POST; acceptance: headers present in responses, tests confirm CSRF enforcement on state-changing routes.
