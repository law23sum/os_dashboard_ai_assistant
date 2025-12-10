# OS Dashboard – React Desktop Migration Plan

## 1. Objectives
- Preserve the existing **desktop** form factor while replacing the Tkinter GUI with a modern React + TypeScript interface inspired by the “Research & Simulation Workspace” mockup.
- Introduce a clean API boundary so the UI no longer imports Python modules directly, enabling packaging via **pywebview** (Python host + embedded WebView) or Electron/Tauri later.

## 2. Architecture Overview
1. **Python host (existing codebase)**
   - Continues to manage personas, tasks/projects, automations, document workflows, and shell execution.
   - Runs a FastAPI application (`assistant_hub.api.server`) exposing REST + WebSocket endpoints.
   - Optionally launches the React desktop shell via pywebview.
2. **React + TypeScript UI** (`frontend/`)
   - Built with Vite, React Router, Chakra UI (or Material UI), TanStack Query, and Chart.js/Recharts.
   - Implements feature modules (Dashboard, Tasks, Projects, AI Console, Integrations, Settings).
   - Communicates exclusively with the Python API.
3. **Desktop packaging**
   - PyInstaller bundles: start FastAPI + pywebview, load compiled React assets from `frontend/dist`.

## 3. API Surface (Phase 1)
| Endpoint | Method | Description |
| --- | --- | --- |
| `/api/health` | GET | Health check |
| `/api/personas` | GET/POST | List personas / set active persona |
| `/api/tasks` | GET/POST/PUT/DELETE | CRUD for tasks, filters for project/owner |
| `/api/projects` | GET/POST/PUT/DELETE | CRUD for projects + documents |
| `/api/chat` | POST | Send AI console message, returns streaming token via WebSocket `/api/chat/stream` |
| `/api/terminal` | POST | Execute shell command (sandboxed) and stream output |
| `/api/docs/upload` | POST | Upload document for project |
| `/api/research/simulations` | GET/POST | Start/list research simulations (new dashboard) |
| `/api/integrations` | GET/POST | Proxy to `IntegrationAPIGateway` |
| `/api/system/status` | GET | CPU/RAM/security telemetry |

## 4. React Application Structure
```
frontend/
  package.json
  tsconfig.json
  vite.config.ts
  src/
    main.tsx
    App.tsx
    components/
      Layout/
      Dashboard/
    hooks/useApi.ts
    api/client.ts
    pages/
      Dashboard.tsx
      Tasks.tsx
      Projects.tsx
      AIConsole.tsx
```
- Routing via React Router.
- UI kit: Chakra UI (responsive grid, cards, buttons).
- Data fetching: TanStack Query (automatic caching/refetch).
- Charts: react-chartjs-2 (for simulation results) and Recharts for knowledge graph placeholders.

## 5. Desktop Wrapper (Phase 2)
1. Add `assistant_hub_gui/webview_app.py`:
   - Starts FastAPI server (thread) if not already running.
   - Launches pywebview window pointing at `http://127.0.0.1:<port>` or the local `dist/index.html`.
2. Packaging:
   - Build React app (`npm run build`) → copy `dist` into `assistant_hub_gui/static`.
   - Use PyInstaller spec to include FastAPI + static assets.

## 6. Migration Steps
1. **API foundation** – implement FastAPI server bridging to existing services; unit tests for endpoints.
2. **React scaffold** – commit Vite/React skeleton + design system, implement “Research Dashboard” page calling mock API.
3. **Feature parity** – Tasks, Projects, AI Console, Integrations, Settings.
4. **Desktop host** – pywebview wrapper, packaging scripts.
5. **Decommission Tk GUI** – remove `assistant_hub/gui.py` once React client is default.

## 7. Risks & Mitigations
- **API coverage**: ensure each GUI action has an endpoint; start with read-only to unblock frontend dev.
- **Authentication**: for local desktop, reuse persona selection; future multi-user support may add OAuth.
- **Performance**: keep long-running operations asynchronous (WebSockets for command/chat streaming).

This plan provides the blueprint; the following commits scaffold the API and React project so implementation can begin immediately.

## 8. Implementation Snapshot (Current)
- `frontend/` now contains a Vite + React + TypeScript SPA that renders the Research & Simulation workspace aesthetic with Chakra UI, React Query, and Chart.js. The router uses the `/app` base path so the same bundle drives browser and desktop modes.
- `assistant_hub/api/server.py` can optionally mount the pre-built SPA (`create_app(..., frontend_dist=...)`) while still exposing `/api` endpoints, letting FastAPI serve both data and static assets.
- `assistant_hub_gui/webview_app.py` encapsulates the cross-platform desktop shell. It launches FastAPI via uvicorn and then either opens a browser or embeds the bundle through **pywebview**, which keeps Windows/macOS/Linux parity for future PyInstaller packaging.
- `start_ui.py` is the single launcher; it prompts for React desktop vs React browser (legacy Tk retired) whenever `python start_ui.py` runs locally, so migration testing is one keystroke away.
- `pywebview` is part of `requirements.txt`, `.gitignore` ignores `frontend/node_modules` and `dist`, and the Vite config emits assets rooted at `/app`, matching the FastAPI mount path.
