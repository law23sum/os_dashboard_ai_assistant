# OS Dashboard AI Assistant — Architecture Deep Dive

## TOC
- Sessions are appended below in chronological order.

## Session 20251211T223456Z

- Generated at: `2025-12-11T22:34:59Z`

### System boundaries
- **This repository**: OS Dashboard AI Assistant control plane + UI surfaces + automation.
- **External repositories**: referenced in place via `config/repo_manifest.json` and inspected by Sentinel (no code copying).

### High-level architecture (OS Dashboard)
- **UI plane**
  - React (Vite) web UI + Electron desktop shell: `frontend/`.
  - Legacy UI: `ui/` + Tkinter paths (fallback).
- **API/control plane**
  - FastAPI app factory: `assistant_hub/api/server.py` (serves `/app/` SPA + API endpoints).
  - Compatibility backend: `backend_api/` (router-per-domain; used by legacy flows).
- **Core domain plane**
  - `assistant_core/`: orchestration, cognitive framework, security hooks, connectors, state.
- **Automation plane (Codex Sentinel)**
  - `scripts/codex_sentinel.py`: repo registry + health + reports.
  - `scripts/ai_auto_fix.py`: log-driven self-healing loop for this repo.

### Operational guardrails
- **Non-invasive**: reports and logs only store metadata (paths, counts, statuses).
- **Reversible**: automation that applies patches uses `git apply` so changes are reviewable.
- **Safety switch**: set `SENTINEL_BYPASS=1` to skip hook enforcement temporarily.

### Blueprint alignment (v1000 → v1000+)
- `docs/v1000_blueprint.md` defines the product pillars and non-invasive integration model.
- `docs/v1000_sequential_task_queue.md` defines the execution phases (manifest → sentinel → templates → rollout).

### Next architectural unification targets
- **Backend consolidation**: converge onto a single FastAPI surface (prefer `assistant_hub/api/server.py`) and treat `backend_api/` as legacy/compat layer.
- **Contract-first APIs**: version Pydantic models and document endpoints; lock client types in `frontend/src`.
- **Sentinel adapters**: per-stack command runners (python/node/java) that can run lint/test and optionally auto-fix via policies.
## Session 20251211T223848Z

- Generated at: `2025-12-11T22:39:07Z`

### System boundaries
- **This repository**: OS Dashboard AI Assistant control plane + UI surfaces + automation.
- **External repositories**: referenced in place via `config/repo_manifest.json` and inspected by Sentinel (no code copying).

### High-level architecture (OS Dashboard)
- **UI plane**
  - React (Vite) web UI + Electron desktop shell: `frontend/`.
  - Legacy UI: `ui/` + Tkinter paths (fallback).
- **API/control plane**
  - FastAPI app factory: `assistant_hub/api/server.py` (serves `/app/` SPA + API endpoints).
  - Compatibility backend: `backend_api/` (router-per-domain; used by legacy flows).
- **Core domain plane**
  - `assistant_core/`: orchestration, cognitive framework, security hooks, connectors, state.
- **Automation plane (Codex Sentinel)**
  - `scripts/codex_sentinel.py`: repo registry + health + reports.
  - `scripts/ai_auto_fix.py`: log-driven self-healing loop for this repo.

### Operational guardrails
- **Non-invasive**: reports and logs only store metadata (paths, counts, statuses).
- **Reversible**: automation that applies patches uses `git apply` so changes are reviewable.
- **Safety switch**: set `SENTINEL_BYPASS=1` to skip hook enforcement temporarily.

### Blueprint alignment (v1000 → v1000+)
- `docs/v1000_blueprint.md` defines the product pillars and non-invasive integration model.
- `docs/v1000_sequential_task_queue.md` defines the execution phases (manifest → sentinel → templates → rollout).

### Next architectural unification targets
- **Backend consolidation**: converge onto a single FastAPI surface (prefer `assistant_hub/api/server.py`) and treat `backend_api/` as legacy/compat layer.
- **Contract-first APIs**: version Pydantic models and document endpoints; lock client types in `frontend/src`.
- **Sentinel adapters**: per-stack command runners (python/node/java) that can run lint/test and optionally auto-fix via policies.
## Session 20251211T224137Z

- Generated at: `2025-12-11T22:41:40Z`

### System boundaries
- **This repository**: OS Dashboard AI Assistant control plane + UI surfaces + automation.
- **External repositories**: referenced in place via `config/repo_manifest.json` and inspected by Sentinel (no code copying).

### High-level architecture (OS Dashboard)
- **UI plane**
  - React (Vite) web UI + Electron desktop shell: `frontend/`.
  - Legacy UI: `ui/` + Tkinter paths (fallback).
- **API/control plane**
  - FastAPI app factory: `assistant_hub/api/server.py` (serves `/app/` SPA + API endpoints).
  - Compatibility backend: `backend_api/` (router-per-domain; used by legacy flows).
- **Core domain plane**
  - `assistant_core/`: orchestration, cognitive framework, security hooks, connectors, state.
- **Automation plane (Codex Sentinel)**
  - `scripts/codex_sentinel.py`: repo registry + health + reports.
  - `scripts/ai_auto_fix.py`: log-driven self-healing loop for this repo.

### Operational guardrails
- **Non-invasive**: reports and logs only store metadata (paths, counts, statuses).
- **Reversible**: automation that applies patches uses `git apply` so changes are reviewable.
- **Safety switch**: set `SENTINEL_BYPASS=1` to skip hook enforcement temporarily.

### Blueprint alignment (v1000 → v1000+)
- `docs/v1000_blueprint.md` defines the product pillars and non-invasive integration model.
- `docs/v1000_sequential_task_queue.md` defines the execution phases (manifest → sentinel → templates → rollout).

### Next architectural unification targets
- **Backend consolidation**: converge onto a single FastAPI surface (prefer `assistant_hub/api/server.py`) and treat `backend_api/` as legacy/compat layer.
- **Contract-first APIs**: version Pydantic models and document endpoints; lock client types in `frontend/src`.
- **Sentinel adapters**: per-stack command runners (python/node/java) that can run lint/test and optionally auto-fix via policies.
## Session 20251211T232211Z

- Generated at: `2025-12-11T23:22:42Z`

### System boundaries
- **This repository**: OS Dashboard AI Assistant control plane + UI surfaces + automation.
- **External repositories**: referenced in place via `config/repo_manifest.json` and inspected by Sentinel (no code copying).

### High-level architecture (OS Dashboard)
- **UI plane**
  - React (Vite) web UI + Electron desktop shell: `frontend/`.
  - Legacy UI: `ui/` + Tkinter paths (fallback).
- **API/control plane**
  - FastAPI app factory: `assistant_hub/api/server.py` (serves `/app/` SPA + API endpoints).
  - Compatibility backend: `backend_api/` (router-per-domain; used by legacy flows).
- **Core domain plane**
  - `assistant_core/`: orchestration, cognitive framework, security hooks, connectors, state.
- **Automation plane (Codex Sentinel)**
  - `scripts/codex_sentinel.py`: repo registry + health + reports.
  - `scripts/ai_auto_fix.py`: log-driven self-healing loop for this repo.

### Operational guardrails
- **Non-invasive**: reports and logs only store metadata (paths, counts, statuses).
- **Reversible**: automation that applies patches uses `git apply` so changes are reviewable.
- **Safety switch**: set `SENTINEL_BYPASS=1` to skip hook enforcement temporarily.

### Blueprint alignment (v1000 → v1000+)
- `docs/v1000_blueprint.md` defines the product pillars and non-invasive integration model.
- `docs/v1000_sequential_task_queue.md` defines the execution phases (manifest → sentinel → templates → rollout).

### Next architectural unification targets
- **Backend consolidation**: converge onto a single FastAPI surface (prefer `assistant_hub/api/server.py`) and treat `backend_api/` as legacy/compat layer.
- **Contract-first APIs**: version Pydantic models and document endpoints; lock client types in `frontend/src`.
- **Sentinel adapters**: per-stack command runners (python/node/java) that can run lint/test and optionally auto-fix via policies.
## Session 20251211T233147Z

- Generated at: `2025-12-11T23:32:19Z`

### System boundaries
- **This repository**: OS Dashboard AI Assistant control plane + UI surfaces + automation.
- **External repositories**: referenced in place via `config/repo_manifest.json` and inspected by Sentinel (no code copying).

### High-level architecture (OS Dashboard)
- **UI plane**
  - React (Vite) web UI + Electron desktop shell: `frontend/`.
  - Legacy UI: `ui/` + Tkinter paths (fallback).
- **API/control plane**
  - FastAPI app factory: `assistant_hub/api/server.py` (serves `/app/` SPA + API endpoints).
  - Compatibility backend: `backend_api/` (router-per-domain; used by legacy flows).
- **Core domain plane**
  - `assistant_core/`: orchestration, cognitive framework, security hooks, connectors, state.
- **Automation plane (Codex Sentinel)**
  - `scripts/codex_sentinel.py`: repo registry + health + reports.
  - `scripts/ai_auto_fix.py`: log-driven self-healing loop for this repo.

### Operational guardrails
- **Non-invasive**: reports and logs only store metadata (paths, counts, statuses).
- **Reversible**: automation that applies patches uses `git apply` so changes are reviewable.
- **Safety switch**: set `SENTINEL_BYPASS=1` to skip hook enforcement temporarily.

### Blueprint alignment (v1000 → v1000+)
- `docs/v1000_blueprint.md` defines the product pillars and non-invasive integration model.
- `docs/v1000_sequential_task_queue.md` defines the execution phases (manifest → sentinel → templates → rollout).

### Next architectural unification targets
- **Backend consolidation**: converge onto a single FastAPI surface (prefer `assistant_hub/api/server.py`) and treat `backend_api/` as legacy/compat layer.
- **Contract-first APIs**: version Pydantic models and document endpoints; lock client types in `frontend/src`.
- **Sentinel adapters**: per-stack command runners (python/node/java) that can run lint/test and optionally auto-fix via policies.
