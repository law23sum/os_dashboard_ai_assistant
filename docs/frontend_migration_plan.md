# Frontend Migration Plan

This document captures the scope and approach for migrating the AI OS UI from the Tkinter/ttk Python application to the existing React/TypeScript codebase in `frontend/`.

## 1. Current State

### 1.1 Python Desktop UI
- The primary GUI lives in `assistant_hub_gui/assistant_hub/gui.py` and builds a ttk `Notebook` with both classic and consolidated tabs for every workflow (`_build_dashboard_tab`, `_build_tasks_tab`, `_build_ai_os_tab`, etc.). The tab construction happens in `gui.py:1245-1320`, making it clear how many distinct surfaces we need to reproduce.
- Each tab delegates to helper modules for data access and automation:
  - `assistant_hub_gui/assistant_hub/db.py:1-190` defines the persisted entities (`Task`, `Project`, `ChatMessage`, `DocumentOperation`, `Settings`, etc.) and exports CRUD helpers that currently back the GUI.
  - `assistant_hub_gui/assistant_hub/ai.py` and `assistant_hub_gui/assistant_hub/ai_layer/*` provide AI orchestration (agent replies, tool calling).
  - `assistant_hub_gui/assistant_hub/task_automation.py`, `sync_scheduler.py`, `document_manager.py`, and `integrations/` back the automation widgets shown on the Tools and AI Ops tabs.
- Secondary Tkinter applets exist under `ui/`, but the flagship GUI above has the superset of features we need to replace.

#### Tab / Feature Inventory
| Category | Tkinter entry point | Notes |
| --- | --- | --- |
| Core work management | `_build_dashboard_tab`, `_build_tasks_tab`, `_build_projects_tab`, `_build_chat_tab` | Task board, Kanban-esque project grid, persona-aware chat console. |
| Integrations & Tools | `_build_integrations_tab`, `_build_tools_tab`, `_build_writer_workspace_tab` | OneNote/Excel/Git connectors, document governance utilities, content authoring workspace. |
| Analytics & Settings | `_build_analytics_tab`, `_build_settings_tab`, `_build_ai_operations_tab`, `_build_dashboard_analytics_tab` | Productivity metrics, AI Ops feed, system preferences. |
| Advanced AI systems | `_build_ai_systems_tab` plus individual tabs built between `gui.py:1294-1319` (`_build_ai_os_tab`, `_build_advanced_ai_tab`, `_build_security_threat_detection_tab`, etc.) | Tiles and tables that report daemon health, workflows, NAS progress, security posture, etc. |

### 1.2 Backend/API Layer
- A FastAPI service in `backend_api/main.py` already exposes `/api/tasks`, `/api/projects`, `/api/chat`, `/api/dashboard`, `/api/integrations`, and `/api/settings`, all backed by the same SQLite helpers as the Tkinter app. This service will become the canonical backend for the React UI.
- Additional routers are still required for features such as document operations, AI Ops feeds, analytics data, daemon controls, and integration handshakes.

### 1.3 Current React Prototype
- `frontend/` is a Vite + React + TypeScript project. `App.tsx` wires up routes for Dashboard, Tasks, Projects, Chat, Integrations, and Settings (`frontend/src/App.tsx:1-27`), and each page already uses Tailwind utility classes plus React Query for data fetching.
- Dependencies declared in `package.json` need to be aligned with what the code imports (React Query, React Router, Axios, lucide-react, Tailwind stack, etc.).

## 2. Target Web Architecture

### 2.1 Project Structure
```
frontend/
  src/
    app/               # routing, providers, error boundaries
    components/        # shared layout/nav primitives
    features/
      dashboard/
      tasks/
      projects/
      chat/
      tools/
      ai-ops/
      analytics/
    lib/
      apiClient.ts     # Axios instance w/ auth + interceptors
      websocket.ts     # shared WS helper for chat + live ops
    types/             # entities mirrored from assistant_hub_gui.assistant_hub.db
```

- Each feature slice should expose `routes`, `components`, and `api` helpers.
- TanStack Query stays the data/cache orchestrator; React Context is reserved for lightweight UI state (theme, persona, layout density).
- Tailwind CSS + custom tokens provide the design system consistent with the "Glass" aesthetic defined in the Tkinter theme code (`gui.py:1940-2005`).

### 2.2 API Contracts
For every Tkinter tab we need a REST (or WebSocket) surface:

| Feature | API needs | Notes |
| --- | --- | --- |
| Tasks/Projects | Already covered (`/api/tasks`, `/api/projects`). Extend with bulk edits, templates, dependencies, recurring rules, and attachments. |
| Chat / AI Console | `/api/chat` + `/api/chat/ws` exist; needs tool-call streaming, persona metadata, and file upload endpoints. |
| Integrations | `/api/integrations` currently returns an empty list; expand with connectors that reflect `assistant_hub_gui/assistant_hub/integrations/*`. |
| Tools & Document Ops | New `/api/document-operations` (CRUD + diff downloads), `/api/documents/samples`, `/api/automation/run` endpoints to surface what `_build_tools_tab` and `_build_ai_operations_tab` expose. |
| Writer Workspace | `/api/writer/documents`, `/api/writer/suggestions`, `/api/writer/pipeline` leveraging `document_manager.py` and `writer` state variables. |
| AI Ops / Daemons | `/api/ai-ops/events`, `/api/ai-ops/daemons`, `/api/ai-ops/actions` to replicate `_render_ai_os_daemon_view` interactions. WebSocket streaming recommended. |
| Analytics | `/api/analytics/productivity`, `/api/analytics/projects`, `/api/analytics/reports` mirroring the helpers in `analytics.py`. |
| Settings | `/api/settings` now drives automation controls, governance banners, theme overrides, and persona defaults (parity with Tkinter). |

### 2.3 Shared Concerns
- **Auth**: API is currently local-only. React should support API tokens or OS-native auth when introduced.
- **Offline storage**: Continue relying on SQLite through FastAPI; React should treat the API as source of truth and cache via React Query.
- **Real-time events**: Chat and AI Ops both require bidirectional updates; prefer WebSocket hooks with exponential backoff.
- **Theming**: Serve CSS variables (colors, typography) from a design token JSON so both Tkinter and React can stay in sync during migration.

## 3. Migration Roadmap

1. **Foundation & Tooling (Week 1)**
   - Finalize dependencies, Tailwind config, linting, shared types, and axios client.
   - Stand up CI scripts that build both FastAPI and React bundles.

2. **Core Feature Parity (Weeks 2-3)**
   - Port Dashboard, Tasks, Projects, Chat, Integrations, and Settings views to React using live data.
   - Implement task editing (status/priority pills), project CRUD, persona switching, and settings persistence.

3. **Tools, Writer Workspace, Analytics (Weeks 3-4)**
   - Expose document operation history, governance banners, and analytics cards through new REST endpoints.
   - Build Writer Workspace UI (document list + editor + AI suggestions) using the same state shape as `gui.py` writer fields.

4. **AI Ops & Advanced Systems (Weeks 4-6)**
   - Model daemon/automation data, NAS status, security posture, and workflow orchestration pages as dedicated feature slices with streaming updates.
   - Map each Tkinter tab listed in `gui.py:1294-1319` to either a new React route or a consolidated dashboard section.

5. **Decommission Tkinter UI**
   - Once feature parity is validated, package the FastAPI + React stack as the default distribution.
   - Keep Tkinter available in maintenance mode until governance + offline stories are satisfied.

## 4. Risks & Mitigations
- **Scope Creep**: There are ~20 advanced tabs; prioritize the ones that reflect live data. Document placeholders for speculative future tabs.
- **API Coverage**: Several GUI actions call helpers directly (e.g., `_run_ai_os_daemon`). Capture every helper that mutates state and expose it via FastAPI endpoints to avoid business logic duplication.
- **Concurrency**: Tkinter currently performs some operations synchronously; when moving to HTTP we must guard long-running actions with jobs/queues to keep the UI responsive.
- **Testing**: Introduce component tests (Vitest/React Testing Library) and backend integration tests (Pytest) before cutting over.

## 5. Immediate Next Steps
1. Normalize the React project's dependencies/assets so it builds successfully (done in this change set).
2. Continue fleshing out feature slices (tasks, projects, chat, etc.) by extracting shared types and API clients.
3. Expand FastAPI routers for document operations, analytics, automations, and integrations as outlined above.

## 6. Multi-Platform Delivery Strategy
- **Single UI bundle**: The React app under `frontend/src` remains the canonical UI for both browsers and desktop shells. Tkinter stays available for legacy flows, but all new features land in React so we never fork UX logic again.
- **Runtime Targets**:
  - **Web** – Static bundle from `npm run build` is now mounted automatically by the FastAPI app at `/app` (see `ai_os/app/main.py`). Any deployment (Docker, ECS, serverless) can serve the API and UI together without extra nginx glue.
- **Desktop** – `start_ui.py` lets developers pick “React Desktop (Electron)” or “React Web” in dev mode. The “Web” option spins up `uvicorn ai_os.app.main:app` (with optional `npm run dev`) so Electron/Tauri shells can later point at the same localhost server.
  - **Executables** – FastAPI + React bundle can be wrapped by PyInstaller (backend) and Electron/Tauri (frontend) for macOS DMG, Windows MSI, and Linux AppImage packages. Because the backend already serves the React bundle, the desktop shell only needs to embed a browser view.
- **Local Dev Switcher**: Run `./start_ui.py` to pick the target. This keeps both desktop and web React experiences exercised each time engineers work locally and prevents one surface from regressing unnoticed.
- **Deployment Prep**:
  - Artifact layout keeps `frontend/dist/` shared between web hosting and the FastAPI static mount.
  - Future CI/CD can run `npm run build && python -m build` once, then publish both the static web bundle and FastAPI container image / desktop installers without duplicating build steps.
