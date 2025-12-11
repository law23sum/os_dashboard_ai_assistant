# Frontend Migration: Tkinter to React + TypeScript

This document outlines the migration from the Python Tkinter GUI to a modern web-based React + TypeScript frontend with a FastAPI backend.

## Architecture Overview

- **Frontend**: React + TypeScript + Vite + Tailwind CSS (single codebase for web + desktop shells)
- **Backend**: FastAPI REST + WebSocket APIs (`ai_os/app` for shared services, `assistant_hub/api` for legacy routes)
- **Communication**: REST for CRUD/data sync, WebSockets for chat + daemon events
- **Desktop Compatibility**: Tkinter UI remains for legacy flows while the React bundle is embedded in desktop shells (Electron/Tauri) and served via FastAPI for browsers. Both surfaces now pull from the same backend to eliminate duplication.

## Project Structure

```
os_dashboard_ai_assistant/
├── frontend/                  # React + TypeScript frontend (shared between web + desktop)
│   ├── src/                   # components, features, routes
│   ├── public/
│   └── package.json
│
├── ai_os/app/                 # FastAPI app that now mounts the built React UI at /app
│   └── main.py
│
├── assistant_hub/api/         # Legacy FastAPI surface (incrementally merged with ai_os/app)
│
├── assistant_hub_gui/         # Tkinter GUI (still available, uses same backend + DB)
│   └── main.py
│
└── start_ui.py                # Single launcher prompting for React web/desktop modes
```

The React build output (`frontend/dist/`) is served by FastAPI (`ai_os/app/main.py`) at `/app`, ensuring the same assets power both desktop shells and browsers.

## Setup Instructions

### Unified Dev Launcher

```bash
./start_ui.py
```

- Pick FastAPI + React (web) to spin up `uvicorn ai_os.app.main:app --reload` and start the Vite dev server (`npm run dev`). The backend exposes REST/WebSocket endpoints at `http://127.0.0.1:8000` and serves the production React build at `http://127.0.0.1:8000/app` when `frontend/dist` exists.
- Pick the React desktop mode to launch the Electron shell pointing at the same dev stack. Legacy Tkinter can still be run manually (`python -m assistant_hub_gui.main`) but is no longer part of the unified launcher.

### Manual Backend Setup

```bash
pip install -r requirements.txt  # ensure fastapi, uvicorn, etc.
uvicorn ai_os.app.main:app --reload
```

### Manual Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Vite serves `http://localhost:5173` for browser development and proxies API calls to the FastAPI backend.

## Migration Status

### ✅ Completed
- [x] React + TypeScript + Vite project structure and build tooling
- [x] FastAPI backend that mounts `frontend/dist/` for browser delivery
- [x] Dashboard/tasks/projects basic pages with REST data
- [x] Multi-mode dev launcher (`start_ui.py`)
- [x] PyInstaller spec scaffold for the unified launcher (`packaging/start_ui.spec`)
- [x] Plan for shared React bundle across web + desktop without losing Tkinter support
- [x] Tkinter-inspired design system shared between the browser SPA and desktop shells
- [x] Advanced Tkinter tabs mapped to React routes with `/ai/systems` parity dashboard

### 🚧 In Progress
- [ ] Chat page with persona switching + WebSockets
- [ ] Integrations tab parity (OneNote/Excel/Git/etc.)
- [ ] AI Ops/Automation surfacing (remaining Tkinter widgets)
- [ ] Analytics + Writer workspace parity

### 📋 Pending
- [ ] Authentication/session management for hosted deployments
- [ ] File uploads/document diff governance APIs
- [ ] Advanced AI tabs (20+) mapped to React routes
- [ ] Electron/Tauri packaging + PyInstaller bundles for Windows/macOS/Linux
- [ ] CI/CD pipeline to publish static web build + desktop installers simultaneously

## API Endpoints

### Tasks
- `GET /api/tasks/` - List all tasks (with filters)
- `GET /api/tasks/{task_id}` - Get a single task
- `POST /api/tasks/` - Create a new task
- `PUT /api/tasks/{task_id}` - Update a task
- `DELETE /api/tasks/{task_id}` - Delete a task

### Projects
- `GET /api/projects/` - List all projects
- `GET /api/projects/{project_name}` - Get a single project
- `POST /api/projects/` - Create a new project
- `PUT /api/projects/{project_name}` - Update a project
- `DELETE /api/projects/{project_name}` - Delete a project

### Chat
- `GET /api/chat/` - Get chat history
- `POST /api/chat/` - Send a message
- `DELETE /api/chat/` - Clear chat history
- `WS /api/chat/ws` - WebSocket for real-time chat

### Dashboard
- `GET /api/dashboard/stats` - Get dashboard statistics

### Settings
- `GET /api/settings/` - Get current settings
- `PUT /api/settings/` - Update settings

### Integrations
- `GET /api/integrations/` - List all integrations
- `POST /api/integrations/{service}/connect` - Connect to a service
- `POST /api/integrations/{service}/disconnect` - Disconnect from a service

### Terminal / Tools
- `GET /api/terminal/commands` - Shared command catalog sourced from `assistant_hub/command_catalog.py`
- `POST /api/terminal` - Execute a command on the FastAPI host and stream stdout/stderr back to the React client

## Development Workflow

1. Start the backend API server first
2. Start the frontend development server
3. The frontend proxies API requests to `http://localhost:8000` (configured in `vite.config.ts`)

## Multi-Platform Deployment Plan

- **Web Browser**: `npm run build` produces `frontend/dist/`; FastAPI serves it at `/app`. Static hosting (S3, Vercel, CloudFront) can also consume the same bundle.
- **Desktop (macOS/Windows/Linux)**:
  - Embed the React bundle inside an Electron or Tauri shell that points to the local FastAPI server (started by the packaged backend or connecting to a remote API).
  - Package the backend with PyInstaller (or Briefcase) so it runs as a background service on each OS. Installers will include both the Python service and the desktop shell to ensure offline capability.
  - Keep Tkinter available for air-gapped workflows until React parity is confirmed.
- **Dev Ergonomics**: `start_ui.py` ensures engineers regularly exercise both targets, reducing drift.

## Next Steps

1. **Feature Parity**: Continue porting Tkinter-only tabs (AI Ops, analytics, advanced AI systems) into React feature slices.
2. **Shared Types/SDK**: Generate TypeScript types from the Python dataclasses (with `pydantic`/`datamodel-code-generator`) so backend + frontend share schemas without manual duplication.
3. **WebSocket + Streaming**: Wire chat, daemon telemetry, and automation events through FastAPI WebSockets so both desktop and web clients receive live updates.
4. **Packaging**: Add Electron/Tauri config plus PyInstaller specs to CI so web bundles and desktop installers are produced together.
5. **Testing**: Expand pytest suites (backend) and Vitest/RTL suites (frontend) to guard the unified UI.

## Notes

- The backend reuses the existing database and business logic from `assistant_hub_gui/assistant_hub/db.py`
- The frontend is built with modern React patterns (hooks, context, query management)
- Tailwind CSS is used for styling (similar to the professional themes in the Tkinter version)
- React Query is used for server state management
- The migration is incremental - you can run both the Tkinter GUI and the web app side-by-side during transition
