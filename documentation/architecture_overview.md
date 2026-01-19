# OS Dashboard AI Assistant – Architecture Overview

Updated: 2025-02-17

## Repo Map (single git repo)
- `frontend/` — React 18 + Vite web/desktop UI (Electron shell). Entry: `npm run dev:web`, `npm run dev:desktop`, `npm run build`.
- `assistant_hub/` — Core Python services, FastAPI app factory (`assistant_hub.api.server:create_app`), workspace/domain logic, automation harnesses, CLI entrypoints.
- `backend_api/` — Legacy/compat FastAPI server; routers reused by `assistant_hub.api.server`.
- `assistant_hub/ui/terminal/harness.py` — workspace discovery + standardized lint/test/build/security runner; writes consolidated reports.
- `backend_api/routers/workspace.py` — shared workspace scan/doctor/checks API.
- `scripts/` — automation shells (autofix monitors, test matrix generator, assistants demos).
- `start_ui.py` — unified launcher wiring preflight tests → FastAPI → Vite/Electron shell.

## Runtime Surfaces
- **Web/Desktop UI**: `start_ui.py --mode web|desktop` (runs FastAPI + Vite/Electron). API base defaults to `http://127.0.0.1:8000/api`.
- **FastAPI (shared)**: `python -m uvicorn assistant_hub.api.server:create_app --factory --reload --host 127.0.0.1 --port 8000`.
- **Workspace Health**: `/api/workspace/scan`, `/api/workspace/doctor`, `/api/workspace/checks` (dry-run or execute harness). UI route `/workspace/health` renders results.
- **CLI**: `osdash scan|test|run|doctor` plus legacy project/office/history helpers.
- **Legacy FastAPI**: `python backend_api/main.py` (compat shim for `/api/*`).
- **Tkinter GUI**: `python -m assistant_hub_gui.main` (via `run.py` shim).

## Persistence & Data
- SQLite DB at `assistant_hub_gui/assistant_hub/assistant_hub.db` (configurable via `ASSISTANT_HUB_DB`). Shared schema via `assistant_hub.db`.
- Attachments/cache/integrations under `ASSISTANT_HUB_*` dirs (default under repo root).
- Demo data seeded via `assistant_hub.demo_seed.ensure_demo_data`.

## Observability & Journal
- Unified Event Hub with a shared logging SDK and append-only journals (planned). Spec: `docs/UNIFIED_EVENT_JOURNAL.md`.
- Per-agent local journals plus a team timeline rendered in the OS Dashboard "Journal" view.

## API Surface (selected)
- Observability/runtime: `/runtime/diagnostics`, `/runtime/diagnostics/ping`, `/system`, `/system/memory-thread-plan`, `/planes/status`.
- Workspace automation: `/workspace/scan`, `/workspace/checks`, `/workspace/doctor` (aggregated harness report + env checks).
- Work management: `/tasks`, `/projects`, `/dashboard/summary`, `/projects/summary`.
- AI & integrations: `/ai/*` (systems, capsules, coach), `/api-connectors`, `/office/*`, `/computer-vision`, `/neural-architecture`, `/security`, `/edge-computing`, `/workflows`.
- Writer/research: `/writer/*`, `/research/*`.
- Static docs served from `docs/` (and CyberChef bundle when present).

## Build/Test Tooling
- Python: `requirements.txt`, pytest suite under `tests/`, preflight runner `scripts/run_tests_with_autofix.py`, `scripts/generate_test_matrix.py`; new tests cover workspace harness + API.
- JS: `frontend` uses `npm install`, `npm run build`, `npm test` (vitest). Electron packaging via `electron-builder`.
- CI: GitHub Actions release builders exist; unified lint/test/security workflow still missing.

## Known Gaps / Pain Points
- No consolidated CI for lint/test/security across Python + frontend.
- AuthN/AuthZ still open; APIs unauthenticated beyond CORS.
- Persistence lacks migrations/indexes; list endpoints missing pagination.
- Observability currently file-based; unified event journal planned (see `docs/UNIFIED_EVENT_JOURNAL.md`).
