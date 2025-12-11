# UI Deployment Guide

This document explains how to run the modern React UI (browser + desktop), ship
the production build, and package executables for Linux, Windows, and macOS.

## Prerequisites

- Python 3.11+ with project dependencies installed (`pip install -r requirements.txt`)
- Node.js 18+ with npm for the React front end
- `uvicorn` for the FastAPI layer (`pip install uvicorn`)
- Optional: PyInstaller (desktop packaging), `create-dmg` or `codesign` tooling
  for macOS signing/notarization.

## Development Workflow

Use the launcher to pick between runtime modes (single entry point):

```bash
./start_ui.py
```

- **React (browser dev)** — starts FastAPI + Vite dev server with hot reload (http://localhost:5173).
- **React (desktop dev)** — same backend plus the Electron dev shell.
- **React (browser build)** — serves `frontend/dist` via FastAPI/pywebview so you can preview the production bundle in a browser.
- **React (desktop build)** — wraps `frontend/dist` inside a pywebview shell for Windows/macOS/Linux desktop testing prior to packaging.

Each option automatically starts the FastAPI backend so both desktop and browser clients use the exact same code path.

## Web Build (browser deployment)

```bash
cd frontend
npm install               # first run only
npm run build             # produces frontend/dist
```

Serve the generated `frontend/dist/` directory via any CDN/web server
(Nginx, S3 + CloudFront, Vercel, static Azure bucket, etc.) and configure the
client to point at the deployed FastAPI host via `VITE_API_BASE_URL`.
`assistant_hub_gui/webview_app.py` can also mount `frontend/dist` behind
FastAPI’s `/app` route if you prefer to bundle everything in Python.

## Desktop Packaging (cross-platform)

- **Pywebview/Python bundle** — ship the FastAPI host and pywebview shell via
  PyInstaller. This is ideal when you want a pure-Python distribution that still
  renders the React UI inside a native window.
- **Electron bundle** — alternatively, use the existing Electron scripts for a
  JavaScript-only desktop app (useful when distributing via auto-updaters).

### Windows

```bash
pip install pyinstaller
pyinstaller --noconfirm --name os-dashboard --windowed start_ui.py
# or build the Electron variant
cd frontend
npm install
npm run build:desktop:windows
```

Ship `dist/os-dashboard/os-dashboard.exe` (PyInstaller) or the Electron output
under `frontend/dist/` + `frontend/dist_electron/`. Wrap with MSIX/InnoSetup if
you need installers.

### macOS

```bash
pyinstaller --noconfirm --name OS-Dashboard --windowed start_ui.py
# or Electron
cd frontend && npm run build:desktop:mac
```

Codesign/notarize the `.app` bundle that PyInstaller/Electron produces before
distribution.

### Linux

```bash
pyinstaller --noconfirm --name os-dashboard start_ui.py
# or Electron
cd frontend && npm run build:desktop:linux
```

Distribute the binary directly or wrap it as an AppImage/Snap/Flatpak.

## CI/CD Pointers

- Add two jobs: `npm ci && npm run build` (web assets) and `pyinstaller start_ui.py`
  (pywebview desktop). If you need Electron artifacts, add the corresponding
  `npm run build:desktop:*` jobs.
- Publish `frontend/dist/` to your static host and upload PyInstaller/Electron
  artifacts to your package feed or release bucket.
