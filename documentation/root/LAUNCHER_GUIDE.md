# Unified Launcher Guide

## Overview

The `start_ui.py` script is the **single entry point** for launching the OS Dashboard AI Assistant in React modes (web + desktop). It bootstraps the shared FastAPI backend, installs prerequisites, and keeps both display surfaces in sync.

## Usage

### Interactive Mode (Recommended)

Simply run:
```bash
python start_ui.py
```

You'll be prompted to choose:
1. **React · Web Dev** – Vite dev server + FastAPI proxy (http://localhost:5173)
2. **React · Desktop Dev** – Electron shell connected to the same dev server
3. **Serve Web Build** – FastAPI + built React assets (`frontend/dist`)
4. **Serve Desktop Build** – pywebview desktop shell serving the same build

### Direct Mode Selection

Skip the prompt by specifying a mode:
```bash
python start_ui.py --mode web           # Launch Vite + browser
python start_ui.py --mode desktop       # Launch Electron shell
python start_ui.py --mode web-build     # Serve built React bundle in browser
python start_ui.py --mode desktop-build # Serve built React in pywebview
```

## Features

### Automatic Backend Coordination
- Spawns `uvicorn assistant_hub.api.server:create_app --reload` automatically for dev modes
- Ensures backend shuts down cleanly when you exit
- Serves the built React bundle directly (no extra steps) for build-preview modes

### Dependency Management
- Verifies Node.js/npm are available
- Prints friendly instructions if the React build output is missing
- Works across Linux, Windows, and macOS shells

### Clean Shutdown
- Handles Ctrl+C gracefully in every mode
- Stops backend server if it was started by the launcher
- Cleans up subprocesses on exit

## Modes Explained

### 1. React · Web Dev
- **Type:** Web application
- **Backend Required:** Yes (for full functionality)
- **Use Case:** Web-based access, development, testing
- **Platform:** Any modern web browser
- **URL:** http://localhost:5173

### 2. React · Desktop Dev
- **Type:** Electron desktop application
- **Backend Required:** Yes (for full functionality)
- **Use Case:** Native desktop experience
- **Platform:** Linux, Windows, macOS
- **URL:** http://localhost:5173 (internal)

### 3. Serve Web Build
- **Type:** Production React build hosted by FastAPI
- **Backend Required:** Bundled FastAPI server handles routing
- **Use Case:** Preview built assets exactly as they'll be hosted
- **Platform:** Any browser
- **URL:** http://127.0.0.1:8800/app/

### 4. Serve Desktop Build
- **Type:** Pywebview shell pointing at the built React bundle
- **Backend Required:** Bundled FastAPI server handles routing
- **Use Case:** Preview cross-platform desktop experience without building installers
- **Platform:** Linux, Windows, macOS
- **URL:** http://127.0.0.1:8800/app/ (embedded webview)

## Environment Variables

You can set these to customize behavior:

- `DEV_MODE=web|desktop|web-build|desktop-build` - Skip the prompt
- `OSDASH_UI_MODE` - Legacy variable (mirrors `DEV_MODE`)
- `VITE_API_BASE_URL` - Override API base URL (default: http://localhost:8000)

## Troubleshooting

### Backend Not Starting
- Check if port 8000 is already in use
- Verify Python dependencies are installed
- Check backend logs for errors

### Frontend Dependencies Missing
- The launcher will automatically run `npm install`
- If it fails, manually run: `cd frontend && npm install`

### Port Already in Use
- Backend: Change port in backend config or stop existing server
- Frontend: Vite will automatically use next available port

### Need the Legacy Tkinter UI?
- Run it directly with `python -m assistant_hub_gui.main`
- It is not part of the default launcher to keep the desktop story React-only

## Examples

### Development Workflow
```bash
# Start in web mode for development
python start_ui.py --mode web
```

### Production Testing
```bash
# Test desktop app
python start_ui.py --mode desktop-build
```

## Integration with CI/CD

You can use the launcher in scripts:
```bash
#!/bin/bash
# Start backend
uvicorn ai_os.app.main:app --reload &
BACKEND_PID=$!

# Wait for backend
sleep 5

# Launch frontend
python start_ui.py --mode web

# Cleanup
kill $BACKEND_PID
```

## Next Steps

- See `README.md` for project overview
- See `frontend/DEPLOYMENT_GUIDE.md` for production deployment
- See `MIGRATION_COMPLETE.md` for migration status
