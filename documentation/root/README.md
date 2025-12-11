# OS Dashboard AI Assistant

A unified AI-powered dashboard and assistant platform with a modern React/TypeScript frontend that runs seamlessly on web browsers and native desktop applications (Linux, Windows, macOS).

This repository contains:
- **Frontend**: React/TypeScript UI (`frontend/`) - single codebase for web and desktop
- **Backend**: FastAPI REST API (`assistant_hub/api/`) serving all features
- **Core**: Python automation and AI services (`assistant_core/`, `ai_os/`)
- **Legacy**: Tkinter GUI (`assistant_hub_gui/`) - still available with `--legacy` flag

The new React interface preserves the Tkinter color palette and design language while providing a modern, cross-platform experience.

## Getting Started

### Single Entry Point (Recommended)

Use `python run.py` for an interactive launcher that lets you choose between web and desktop modes:

```bash
python run.py              # Interactive mode selection
# or skip the prompt with environment variables
python run.py --mode web
DEV_MODE=desktop python run.py
```

The launcher will display:
```
🚀 OS Dashboard AI Assistant — Unified Launcher
==================================================================

📋 Available Launch Modes:

  🌐 1) React · Web Dev (FastAPI + Vite) ⭐ (default)
  🖥️ 2) React · Desktop Dev (FastAPI + Electron)
  📦 3) Serve built React in browser
  📦 4) Serve built React in desktop shell
```

Need the legacy Tkinter GUI? Pass `--legacy` to `run.py`:

The script:
1. Checks prerequisites (Node.js/npm as needed)
2. Boots the shared FastAPI backend that serves the React bundle
3. Prompts for one of the following modes:
   - **React · Web Dev** (Vite @ http://localhost:5173 + FastAPI proxy)
   - **React · Desktop Dev** (Electron shell talking to the same dev server)
   - **Serve Web Build** (FastAPI + `frontend/dist/`)
   - **Serve Desktop Build** (pywebview shell bundling the built React assets)

Environment overrides: set `DEV_MODE=web|desktop|web-build|desktop-build` (or `OSDASH_UI_MODE`) to bypass the prompt in CI or packaging jobs.

### Manual Launch (Alternative)

If you prefer to launch manually:

```bash
cd frontend
npm install
npm run dev
```

Then choose web or desktop when prompted.

### Backend API Server

The API server runs on port 8070 by default. Start it separately if needed:

```bash
python -m assistant_hub_gui.assistant_hub.core.api_server
```

Or use the FastAPI backend:

```bash
uvicorn ai_os.app.main:app --reload --host 127.0.0.1 --port 8000
```

Key REST endpoints used by the UI: `/writer/snapshot`, `/writer/documents`,
`/writer/narrative`, `/dashboard/summary`, `/projects/summary`, `/tasks`,
`/planes/status`, `/system`, `/projects`, and `/billing/usage`.

## Frontend (React/TypeScript)

The modern frontend is built with React, TypeScript, and Vite, powering browsers, Electron, and pywebview shells from a single codebase.

### Quick Start

```bash
cd frontend
npm install
npm run dev
```

The dev script will ask whether to launch the browser or Electron shell. See `frontend/QUICK_START.md` for more.

### Features

- ✅ Single React bundle for web + desktop (no duplicated UI logic)
- ✅ Tkinter launcher stays available for offline workflows while React gains parity
- ✅ Linux, Windows, and macOS executables via `npm run build:desktop:*`
- ✅ Preserved HTML/JS pages served from `frontend/dist/` so nothing is lost mid-migration
- ✅ FastAPI backend mounted at `/app` in production, Vite proxy in dev for hot reloads
- ✅ **Tkinter-inspired theme** with exact color matching between Tkinter and React surfaces
- ✅ **Shared code structure** (React components + FastAPI routes) eliminating redundancies
- ✅ **Single entry point** (`start_ui.py`) with interactive mode selection
- ✅ **Comprehensive deployment guide** for web and desktop platforms

See `MIGRATION_COMPLETE_SUMMARY.md` for the full migration report and `QUICK_START.md` to get started in 5 minutes.

### Build & Deployment Targets

| Target | Command | Output |
| --- | --- | --- |
| **Web** (static hosting/CDN) | `npm run build:web` | `frontend/dist/` |
| **Desktop – Linux** | `npm run build:desktop:linux` | `frontend/dist-electron/` (AppImage/DEB/RPM) |
| **Desktop – Windows** | `npm run build:desktop:windows` | `frontend/dist-electron/` (NSIS + portable) |
| **Desktop – macOS** | `npm run build:desktop:mac` | `frontend/dist-electron/` (DMG/ZIP) |
| **All platforms** | `./build-all-platforms.sh all` | Complete build with archives |

For detailed deployment instructions, see [`DEPLOYMENT.md`](./DEPLOYMENT.md).

## Legacy GUI

`assistant_hub_gui/main.py` remains fully supported for offline demos (launch manually with `python -m assistant_hub_gui.main`) and now
reads/writes the shared writer workspace store so it stays in sync with the web UI. It is not part of the default launcher anymore—React is the canonical desktop surface.

## Documentation

- Canonical spec structure: `documentation/OS_DashboardAIAssistantTOC.md`
- Queue/stack map: `documentation/QUEUE_STACK_MAP.md`
- Dead-code linkage & future hook-ups: `documentation/DEAD_CODE_LINKAGE.md`
- UI deployment guide: `docs/ui_deployment.md`
- Tk→React feature tracker: `docs/tk_to_react_mapping.md`
- Shared palette/theme: `frontend/THEME.md`
- Desktop packaging spec (PyInstaller): `packaging/start_ui.spec`

Refer to `documentation/consolidated_md/README.md` for the complete installation and
feature overview.

## Theme System

The React frontend uses a Tkinter-inspired theme system that ensures visual consistency
between the legacy Tkinter GUI and the modern React interface. Colors are defined in:

- `frontend/src/theme/colors.ts` - TypeScript theme definitions
- `frontend/src/index.css` - CSS variables
- `frontend/tailwind.config.js` - Tailwind integration

The theme supports both dark and light modes, matching the Tkinter color palette exactly.

## Shared Code

Code is shared between desktop (Electron) and web (browser) builds through:

- `frontend/src/shared/utils.ts` - Platform-agnostic utilities
- `frontend/src/lib/apiClient.ts` - Unified API client
- `frontend/src/components/` - Shared React components

This eliminates code duplication and ensures feature parity across platforms.
