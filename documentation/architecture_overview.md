## repository map and surfaces
- `frontend/` — React + TypeScript (Vite) with optional Electron wrapper; routes served via `start_ui.py` or `npm run dev:web`; tests via `vitest`, packaging via `electron-builder`.
- `assistant_hub/` — FastAPI app (`assistant_hub/api/server.py`) exposing assistant, dashboard, projects, writer, integrations, monitoring, analytics, runtime diagnostics; pulls routers from `backend_api/routers` and domain logic from `assistant_core`.
- `backend_api/` — Legacy/compat FastAPI app wiring the same router set; used by older clients and CLI entrypoints.
- `assistant_core/` — Domain/engine layer: drivers, orchestration, reasoning, analytics, search, capsule registry, spec registry, failure registry, tasks, CI/test fixtures.
- `assistant_hub_gui/` — Legacy Tkinter UI (kept for compatibility).
- `scripts/` — Automation harnesses (ai_shell_runner, ai_auto_fix, workspace/project autofix orchestrators, test matrix generator).
- `start_ui.py` — Unified launcher that runs preflight tests, boots FastAPI, and starts the React web/desktop shells.
- `.github/workflows/` — Electron build pipelines (Windows/macOS/Linux); no unified CI for lint/test across Python/TS yet.

## runtime entrypoints and commands
- Primary local run: `python start_ui.py --mode web|desktop` (boots FastAPI + Vite/Electron).
- Backend only: `uvicorn assistant_hub.api.server:create_app --factory --reload --host 0.0.0.0 --port 8000`.
- Legacy backend: `python backend_api/main.py`.
- Frontend only: `cd frontend && npm run dev:web` (or `dev:desktop`), `npm run build`.
- Tests: `pytest` (root), `npm test` (frontend vitest), `node --test electron/__tests__/*.test.cjs`.

## architecture as-built (current state)
- Presentation: React SPA (Vite) + optional Electron shell; legacy Tkinter UI still present.
- API boundary: FastAPI app exposes many feature families (dashboard/projects/tasks/writer/analytics/integrations/monitoring/network/security/capsules/edge/etc.). Middleware includes CORS + optional prefix stripping. No auth/roles enforced.
- Service/domain: Logic split between `assistant_hub` and `assistant_core` (drivers, orchestrators, registries, analytics, search, reasoning, workspace engines). Heavy use of in-memory flows with limited separation of concerns.
- Persistence: SQLite via `assistant_hub/db.py` and `assistant_hub/config.py` (paths set via env); attachments/integrations cached under data dir; no migrations or schema versioning.
- Observability: Runtime diagnostics endpoint (`/api/runtime/diagnostics`), NDJSON logging to `logs/runtime_diagnostics.log`; basic health (`/api/health`); limited structured logging/correlation IDs.
- Security: Env-based secrets loading; no authN/authZ, no request validation beyond Pydantic models; CORS open to localhost origins.
- CI/CD: Electron build workflows only; missing unified lint/test/security pipeline across Python/TS.

## detected pain points and gaps
- Fragmented API surfaces (`assistant_hub.api.server` and `backend_api.main`) duplicating router wiring.
- Lack of auth, tenancy, and role-aware controls despite multi-surface spec.
- No migration/versioning for the SQLite schema; limited data integrity guarantees.
- Observability is minimal (no metrics/traces, sparse structured logs).
- Automation harness exists but not integrated into a single CLI (`osdash`) for repo scanning/testing.
- Frontend relies on cached/demo data when backend missing; end-to-end contract tests absent.
- CI does not run lint/pytest/vitest/security scans; drift risk is high.
