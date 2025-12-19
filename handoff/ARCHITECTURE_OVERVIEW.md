# OS Dashboard AI Assistant – Architecture Overview

Updated: 2025-12-17

## Repo Map (single git root)
- `frontend/` — React 18 + Vite UI with shared web/Electron shell (routes in `src/App.tsx`, data hooks in `src/api`). Entrypoints: `npm run dev:web`, `npm run dev:desktop`, `npm run build`.
- `assistant_hub/` — Primary FastAPI app (`assistant_hub.api.server:create_app`), orchestration logic, cognitive/daemon managers, SQLite-backed data helpers, and CLI surface (`assistant_hub.ui.terminal.cli:main` → `osdash`).
- `backend_api/` — Compatibility FastAPI server wiring the same routers under `/api`; still referenced by tests and legacy launch flows.
- `assistant_hub_gui/` — Legacy Tkinter + pywebview UI and the canonical SQLite schema reused by both backends.
- `scripts/` — Automation harnesses (autofix monitors, project/workspace scanners, assistants demos) plus test-matrix generator.
- `start_ui.py` — Unified launcher: preflight tests → FastAPI → Vite/Electron dev server or built assets.

## Runtime Surfaces & Entry Points
- **Web/Desktop UI**: `python start_ui.py --mode web|desktop` (boots FastAPI + Vite/Electron with API base `http://127.0.0.1:8000/api`).
- **API**: `uvicorn assistant_hub.api.server:create_app --factory --reload --host 127.0.0.1 --port 8000` (preferred) or `python backend_api/main.py` (compat).
- **CLI**: `osdash scan|test|run|doctor|projects|onenote|excel|word|history` (see `assistant_hub/ui/terminal/cli.py`).
- **Legacy GUI**: `python -m assistant_hub_gui.main` (also reachable via `python run.py`).

## Data & Persistence
- Default SQLite DB at `assistant_hub_gui/assistant_hub/assistant_hub.db` (configurable via `ASSISTANT_HUB_DB`); shared helpers in `assistant_hub.db` and `backend_api.db`.
- Attachments/cache/integration secrets live under repo-relative directories unless overridden via env vars.
- Demo data seeding via `assistant_hub.demo_seed.ensure_demo_data`; runtime diagnostics logged to `logs/runtime_diagnostics.log` (override `OSDASH_RUNTIME_LOG`).
- No migration framework yet; schema changes are implicit and risk drift.

## API & Data Flows (selected)
- **System/Observability**: `/api/runtime/diagnostics`, `/api/runtime/diagnostics/ping`, `/system`, `/planes/status`, `/billing/usage` (correlation IDs injected by middleware).
- **Work Management**: `/api/tasks`, `/api/projects`, `/dashboard/summary`, `/projects/summary`.
- **AI/Integrations**: `/api/ai/*` (systems, capsules, coach), `/api/api-connectors`, `/api/office/*`, `/api/computer-vision`, `/api/neural-architecture`, `/api/security`, `/api/edge-computing`, `/api/workflows`.
- **Writer/Research**: `/api/writer/*`, `/api/research/*`.
- **Static assets**: served from `docs/`, `frontend/dist`, and `CyberChef_v10.19.4` when present.

## Build, Test, CI
- **Python**: `requirements.txt`; pytest suite under `tests/`; preflight `scripts/run_tests_with_autofix.py`; harness tests (`tests/test_osdash_harness.py`, `tests/test_workspace_cli.py`).
- **JS**: `frontend` uses Vite + Vitest (`npm run test -- --runInBand`), Electron packaging via `electron-builder`.
- **CLI harness**: `osdash scan|test|doctor` leverages `assistant_hub.ui.terminal.harness` and workspace helpers to detect repo commands and emit JSON reports in `logs/osdash/`.
- **CI**: GitHub Actions `build-release.yml` + `build-electron.yml` package releases; missing unified lint/test/security workflow for PRs.

## Pain Points & Gaps
- No migrations or schema versioning; SQLite changes are ad hoc and can break upgrades.
- CI lacks lint/security scans and full test execution across Python + frontend.
- Observability lacks metrics/traces aggregation and SLO health; only NDJSON logs are emitted.
- Spec v6 doc index was missing; recreated at `documentation/consolidated_md/technical_spec_v6_alignment.md` but chapter summaries still need regeneration.
