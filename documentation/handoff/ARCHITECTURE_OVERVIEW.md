# OS Dashboard AI Assistant — Architecture Overview (Discovery)

Updated: 2025-02-16

## Git Repository Map
- `/Users/sum/Project/os_dashboard_ai_assistant` — active monorepo (React/Vite UI, FastAPI backend, Python automation/CLI).
- Other git roots discovered (archival/reference only; untouched this pass): `../trader_exchange`, `../portfolio_strategist`, and multiple `../Archive/...` Django/WebStorm/Idea template repos. See TODO backlog for triage.

## Main Repo Components
- **Frontend (`frontend/`)**: React 18 + Vite; shared web/Electron bundle (routes in `src/App.tsx`, theme in `src/theme`). Observability page renders runtime diagnostics and the new harness report.
- **Backend (`assistant_hub/api/`)**: FastAPI factory `create_app` with StripPrefix middleware for optional `/api` prefix. Routers pulled from `backend_api/routers/*`; compatibility entrypoint in `backend_api/main.py`.
- **Automation/CLI (`assistant_hub/ui/terminal`)**: `osdash` commands (scan/test/run/doctor/projects/office). Workspace harness (`run_workspace_checks`, `write_workspace_report`) now emits aggregate JSON reports; override log dir via `OSDASH_HARNESS_LOG_DIR`.
- **Legacy GUI (`assistant_hub_gui/`)**: Tkinter/pywebview UI sharing sqlite DB for offline parity.
- **Core/Drivers (`assistant_core/`, `ai_os/`)**: Domain scaffolding, personas/daemons, driver abstractions referenced by the v6 spec.
- **Scripts (`scripts/`)**: Autofix orchestrators, assistants demos, workspace auto-fix shell; logs under `logs/`.

## Runtime Surfaces
- UI launcher: `python start_ui.py --mode web|desktop` (FastAPI + Vite/Electron, SPA at `/app/`).
- APIs: `/runtime/diagnostics`, `/runtime/harness-report` (new), `/system`, `/planes/status`, `/projects`, `/tasks`, `/ai/*`, `/workflows`, `/office/*`, docs at `/docs`, SPA assets `/app/assets`.
- CLI: `osdash` command; StripPrefix middleware supports `/api/*` and bare paths for browser/Electron clients.

## Persistence & Data
- SQLite DB configurable via `ASSISTANT_HUB_DB`; demo data via `assistant_hub.demo_seed.ensure_demo_data`. No migrations or ledger tables yet.
- Logs: runtime diagnostics NDJSON at `logs/runtime_diagnostics.log` (override `OSDASH_RUNTIME_LOG`); harness aggregates at `logs/osdash/workspace-report-*.json` (`OSDASH_HARNESS_LOG_DIR` override).

## Build / Test / CI
- Backend: `python -m pytest -q` (not executed here; `pytest` missing in sandbox), `pip check` for deps.
- Frontend: `npm run test -- --runInBand --prefix frontend`, `npm run build --prefix frontend`.
- Automation: `osdash test --categories lint,test,build,security` writes aggregated workspace report.
- CI: `.github/workflows/build-release.yml` and `build-electron.yml` build artifacts only; unified lint/test/security pipeline is missing.

## Pain Points / Gaps
- Spec v6 gaps: plane isolation, ledger/capsule persistence, project intelligence/TRF surfaces, research/digital twin backends, auth/tenancy, governance storage.
- Database schema unmanaged (no Alembic/versioning, no integrity chain).
- Observability limited to file-based logs; no metrics/traces or retention policy.
- Tests were not executed in this session because `pytest` is unavailable; dependency bootstrap needed.
