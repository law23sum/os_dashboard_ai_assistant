# Front-End Deployment & Packaging Guide

This document tracks the steps required to ship the new React/Electron interface across
all supported surfaces: web browsers and desktop executables (macOS, Windows, Linux).

## Development
- Unified helper: `./start_ui.py` → prompts for web (Vite dev server) or desktop (Electron shell) and launches FastAPI automatically.
- Manual backend-only run (if needed): `uvicorn assistant_hub.api.server:create_app --factory --reload`
- Manual frontend-only run: `cd web/writer-workspace && npm run dev`

## Web Build
```bash
npm run build --prefix frontend
```
Outputs go to `frontend/dist/`. Serve the folder via any static host (Netlify, Vercel,
S3/CloudFront, etc.).

## Desktop Build (Electron)
Electron scripts already exist in `frontend/package.json`:
- `npm run build:desktop --prefix frontend` → cross-platform bundle (uses electron-builder).
- Per-OS builds: `build:desktop:mac`, `build:desktop:win`, `build:desktop:linux`.
Artifacts land in `frontend/dist-electron/`.

## Release Checklist
1. `uvicorn ai_os.app.main:app --reload` (confirm API works).
2. `npm run build --prefix frontend` (web assets).
3. `npm run build:desktop[:os] --prefix frontend` for installer packages.
4. Update `README.md`/docs with new version numbers.
5. Tag release and upload zipped builds as needed.

Future work: integrate CI to run the above steps automatically per platform.
