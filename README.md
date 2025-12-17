# OS Dashboard AI Assistant

A unified AI-powered dashboard and assistant platform with a modern React/TypeScript frontend that runs seamlessly on web browsers and native desktop applications (Linux, Windows, macOS).

This repository contains:
- **Frontend**: React/TypeScript UI (`frontend/`) - single codebase for web and desktop
- **Backend**: FastAPI REST API (`assistant_hub/api/`) serving all features
- **Core**: Python automation and AI services (`assistant_core/`, `ai_os/`)
- **Legacy**: Tkinter GUI (`assistant_hub_gui/`) - still available with `--legacy` flag

The new React interface preserves the Tkinter color palette and design language while providing a modern, cross-platform experience.

## Getting Started

    venv/bin/python -m pip install -r requirements.txt


    cd backend_api
    python main.py

    cd frontend
    npm install
    npm run build
    npm run dev:browser
   npm run dev:desktop 

### Single Entry Point (Recommended)

Use `python run.py` for an interactive launcher that lets you choose between web and desktop modes:

```bash
python -m assistant_hub_gui.main  # Interactive mode selection
python run.py             
# or sckip the prompt with environment variables
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
Tip: the Electron shell no longer auto-opens DevTools to avoid Chromium autofill console noise. Re-enable anytime by setting `OSDASH_ELECTRON_DEVTOOLS=1` before launching (`OSDASH_ELECTRON_DEVTOOLS=1 npm run dev:desktop`).

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

### AI Shell Runner (local automation)

The new `scripts/ai_shell_runner.py` script wires the OpenAI **shell** tool to your
local machine so GPT‑5.x models can inspect files or run diagnostics in a guarded loop:

```bash
export OPENAI_API_KEY=sk-...
python scripts/ai_shell_runner.py "summarize git branches and show disk usage for ./logs"
```

- Uses the Responses API with `tools=[{"type": "shell"}]`
- Executes commands inside the current working directory (configurable via `--cwd`)
- Streams raw stdout/stderr back to the model until it produces a final answer
- Limits each interaction to `--max-steps` (default 6) and enforces per-command timeouts

⚠️ **Security**: the shell tool can run arbitrary commands. Run inside a sandboxed
environment or adjust the script to enforce allowlists before trusting unreviewed output.

### Workspace Auto-Fix Shell

`scripts/workspace_autofix_shell.py` gives you a dedicated terminal for orchestrating
auto-heal loops across every git repo under your workspace:

```bash
# interactive picker
python scripts/workspace_autofix_shell.py

# batch mode — scan siblings under ~/Projects, retry tests twice, forward args to ai_auto_fix
python scripts/workspace_autofix_shell.py \
  --workspace ~/Projects \
  --max-depth 3 \
  --run-all \
  --attempts 2 \
  --autofix-arg --verify-seconds \
  --autofix-arg 15
```

The shell discovers `.git` folders, runs any available test harnesses
(`scripts/run_tests_with_autofix.py`, `npm test`, or `pytest`), and hands failures to
`ai_auto_fix.py` automatically. Repositories without tests still get an `ai_auto_fix`
daemon so every surface enjoys the same self-healing protections.

### Code Interpreter helper

`scripts/ai_code_interpreter.py` wraps the OpenAI **code interpreter / python tool**
so you can quickly offload math, analysis, or plotting tasks to a sandboxed container:

```bash
export OPENAI_API_KEY=sk-...
python scripts/ai_code_interpreter.py --file data/sample.csv \
  "Plot the rolling 7-day averages and highlight anomalies"
```

- Automatically uploads `--file` paths (repeat flag for multiple files)
- Supports container reuse via `--container-id` or auto-provisioning via `--memory`
- Prints any generated files (with container + file IDs) so they can be downloaded later
- Use `--dump-json` to inspect the full Responses payload during debugging

### Auto-fix monitor + tests

`scripts/ai_auto_fix.py` already watches backend/frontend logs. Pass `--test`
arguments so **every failing test automatically triggers the AI repair loop**:

```bash
python scripts/ai_auto_fix.py \
  --backend "python -m uvicorn backend_api.main:app --reload" \
  --frontend "npm run dev:web" \
  --test "pytest -q tests/test_office_api.py" \
  --test "pytest -q tests/test_office_router.py" \
  --test-interval 600
```

The orchestrator will:

1. Launch the backend/frontend processes (or tail existing logs with `--logs-only`)
2. Run the supplied tests on startup and every `--test-interval` seconds
3. Feed any failures/errors into the AI fixer, apply patches, and rerun until green
4. Prompt for manual intervention only if a blocker can’t be resolved automatically

### Workspace auto-fix orchestrator

`scripts/project_autofix_orchestrator.py` fans the auto-fix monitor out to every git
repo under a workspace. It detects `.git` folders, checks whether a repo ships
`scripts/ai_auto_fix.py`, and launches monitors in parallel or sequentially while
logging status to `logs/autofix_orchestrator.log`.

```bash
# List repos and their auto-fix readiness without launching monitors
python scripts/project_autofix_orchestrator.py --root ~/Projects --scan-only

# Launch monitors for every repo that ships scripts/ai_auto_fix.py
python scripts/project_autofix_orchestrator.py --root ~/Projects --ai-args "--logs-only"
```

Use `--include/--exclude` filters to target subsets of repos, `--dry-run` for safe
prechecks, and `--env KEY=VALUE` to inject API keys or sandbox toggles into child processes.

### Assistants API demo CLI

Scripts in `scripts/` mirror OpenAI’s latest built-in tools. Use `scripts/assistants_demo.py`
to exercise the Assistants API (Code Interpreter, File Search, custom functions)
without copy/pasting notebook snippets:

```bash
# Ask a single question with a freshly created assistant
OPENAI_API_KEY=sk-... \
python scripts/assistants_demo.py \
  --question "Solve 3x + 11 = 14" \
  --instructions "You are a personal math tutor."

# Reuse an existing assistant id, enable Code Interpreter and the quiz function
python scripts/assistants_demo.py \
  --assistant-id asst_abc123 \
  --enable-code --function-demo \
  --question "Generate the first 20 Fibonacci numbers" \
  --question "Give me feedback on my quiz answers"
```

Flags like `--enable-file-search --file path/to/doc.pdf` mimic the “Assistants API
Overview” notebook flow so you can upload documents, run code, and handle function
calls directly from the CLI.

### Copilot Assistants activity log

The `/ai/copilot` React page now ships an “Assistants CLI Activity” widget inside the
**Assistants API + Advanced Tools** section. Each time you run
`python scripts/assistants_demo.py`, jot the prompt, tools used, and any notes in the form—
entries persist to `localStorage` so the React/Electron UI mirrors the legacy Tkinter logbook.
Use the quick status dropdown (Completed/Running/Needs Attention) to flag follow-ups, and the
log will highlight your last six CLI runs alongside the tool stack you selected.

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