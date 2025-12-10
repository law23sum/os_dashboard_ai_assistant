# OS Dashboard AI Assistant Platform

Enterprise-grade autonomous workflows, professional content generation, and advanced system operations for multi-source data intelligence.

---

## Key Features

### Advanced Autonomous Workflows
- Multi-source intelligence with real-time web scraping and content extraction.
- Batch data processing across multiple APIs with cross-reference verification.
- Automated pipelines that clean, transform, and validate diverse datasets.
- Intelligent task management with dependency awareness and retry logic.

### Professional-Grade Content Generation
- Interactive HTML presentations with responsive layouts, charts, and animations.
- Excel dashboards featuring live data connections, conditional formatting, and native charts.
- Word documents with complex layouts, tables, and professional formatting.
- End-to-end web application deployment with custom domains.

### System-Level Operations
- Full Linux environment control, including package installation and environment setup.
- Process management with monitoring, logging, and background task control.
- Network services with public port exposure and managed services.
- Advanced file processing spanning PDF extraction, conversions, and archive handling.
- Real-time Office collaboration router bridging Office add-ins and AI feedback loops with resilient fallbacks (`assistant_core/integrations/office_realtime.py`).
- Canonical technical specification registry capturing mission, deployment modes, identity surfaces, and cognitive personas per the OS Dashboard AI Assistant TOC (`assistant_core/spec/technical_spec.py`).

### Specialized Intelligence
- Automated content validation and overflow detection.
- Accessibility compliance checks and reporting.
- Formatting validation with consistency enforcement and professional standards.
- Batch verification with cross-file error reporting.
- Local Office AI processing service that analyzes, generates, and suggests content for add-ins even when external APIs are unavailable (`assistant_core/intelligence/office_ai_service.py`).

### Concurrent Operations
- Parallel processing with intelligent batching across three to five simultaneous searches.
- Managed background tasks with progress monitoring.
- Dynamic worker pools for resource optimization and performance tuning.
- Fault-tolerant execution with automatic retries and graceful degradation.

### Advanced Integration
- Office add-in embedding for Excel dashboards with task pane support.
- Static site deployment to Vercel, Netlify, AWS, and GitHub Pages.
- API integrations with live data feeds and webhook support.
- Cross-platform compatibility spanning Windows, macOS, Linux, and mobile.

### Enterprise Security & Governance
- Policy/governance engine with compliance frameworks, audit trails, and data classification.
- Encryption service with key management, RSA/AES primitives, and usage logging.
- Authentication & RBAC manager supporting multiple auth providers and session controls.
- Security monitor with threat detection, anomaly analysis, and incident workflows.
- Billing and usage fabric for plan management, metering, and invoicing.

---

## Installation

### Prerequisites
- Python 3.8+
- `pip`
- Git (development workflow)

### Quick Install
```bash
# Clone the repository
git clone https://github.com/ai-assistant/os_dashboard_ai_assistant.git
cd os_dashboard_ai_assistant

# Install dependencies
pip install -r requirements.txt

# (Optional) register console scripts locally
pip install -e .
```

### Development Install
```bash
pip install -e .
pytest tests/
black assistant_core ai_os assistant_hub assistant_hub_gui
flake8 assistant_core ai_os assistant_hub assistant_hub_gui
```

### Guided Bootstrap
For an interactive setup (system deps, config folders, launcher script), run
`python tools/bootstrap.py`. This helper mirrors the legacy `python setup.py` flow
without interfering with modern packaging.

---

## Quick Start

### Launch the Dashboard
```bash
# Desktop GUI
./python_os -m assistant_hub_gui.main

# Lightweight FastAPI backend (optional)
python -m ai_os.app.main
```

### Run the Demo Suite
```bash
python examples/demo_usage.py
# Generates presentations, Excel dashboards, Word reports, and deployment artifacts
```

### Demo Showcase Inside the GUI
Open the GUI (`./python_os -m assistant_hub_gui.main`) and navigate to **Tools → Demo Showcase** to run the
same demo suite without leaving the dashboard. Output from `examples/demo_usage.py` streams directly into
the panel so stakeholders can review capabilities live.

### Lightweight Web Dashboard
The `ai_os/app` FastAPI service now exposes the same primitives that powered the legacy
`~/Downloads/os_dashboard_ai` Flask prototype:

- `GET /system` – CPU, memory, and disk telemetry powered by `psutil` (`ai_os/app/system_monitor.py`).
- `POST /ai/ask` – prompt → response passthrough for OpenAI-compatible chat endpoints (`ai_os/app/ai_proxy.py`).

You can point the React dashboard (`dashboard.js`) at this FastAPI app to surface a
live system health card and a “Quick AI Assistant” panel without writing additional
glue code:

```bash
uvicorn ai_os.app.main:app --reload
# serve docs/dashboard.html via any static host (or open it directly) to try the new cards
```

Both helpers degrade gracefully when `psutil` or `OPENAI_API_KEY` are missing, so you
can develop locally without secrets.

### Canon Spec Compliance
- Canon requirements live in `OS DashboardAIAssistantTOC.txt`.
- The implementation-to-spec mapping for these services is tracked in
  `documentation/OS_DashboardAIAssistantTOC_MAPPING.md` – reference it when extending
  telemetry, orchestration, or AI proxy layers to keep the build auditable.
- Legacy / idle modules that are not currently wired into the GUI/API stack are
  cataloged in `documentation/DEAD_CODE_LINKAGE.md` with clear guidance on how to
  connect them end-to-end.
- Queue/stack interactions between the React dashboard, FastAPI orchestration, and
  daemon layer are illustrated in `documentation/QUEUE_STACK_MAP.md` so front → middle
  → back flows stay transparent.


## CLI Helpers

### python_os alias
The repository ships a portable `python_os` helper:
- Run it directly via `./python_os ...` or add the repo root to your `PATH` to call
  `python_os` without a prefix.
- In offline environments you can also create a shell alias (`alias
  python_os=python3`).
- If you already run `pip install -e . --no-build-isolation --no-deps`, the console
  entry point registers the same command globally.

Either way it simply proxies to your active Python interpreter, so `python`/`python3`
remain equivalent for every example command. To launch the desktop dashboard without
installing anything globally, run:

```bash
./python_os -m assistant_hub_gui.main
```

### Auto-commit helper
To stage everything and create a detailed commit message automatically, run:

```bash
python scripts/git_auto_commit.py
```

The helper performs `git add .`, inspects the staged diff, and triggers `git commit`
with a message that includes the file list, diffstat, branch, timestamp, and a stub
for your rationale. If an OpenAI key is set (`OPENAI_API_KEY`), it also asks the AI
layer to summarize the diff. You get to review the proposed commit message, tweak the
AI summary, edit manually (via `$EDITOR`), or abort before the commit is finalized.

#### One-step `git add` + commit
If you want this to happen automatically whenever you stage the whole tree, use the
wrapper script (and alias) that mimics `git add`:

```bash
# Add to ~/.bashrc or ~/.zshrc
alias gitadd='./scripts/git_add_auto_commit.sh'

# Use this instead of `git add .`
gitadd .
```

When you pass `.`, the wrapper immediately invokes `scripts/git_auto_commit.py` so the
commit is created right away. Passing specific paths behaves like the normal `git add`
with no auto-commit.

## Repository Structure Snapshot
The file `project_directory_structure` contains the full `ls -R` output captured on
2025-12-10. Regenerate it anytime with `ls -R > project_directory_structure` to keep
the directory map in sync with the repo.

### Monitor Real-Time Sessions
1. Launch the GUI via `./python_os -m assistant_hub_gui.main` (or start the FastAPI backend with `python -m ai_os.app.main`).
2. Navigate to **Tools → Real-Time Sessions** to inspect connected Office add-ins, their active documents, and the router's AI event log.
3. Set `AI_SERVICE_URL` to your processing endpoint or rely on the built-in offline service (`assistant_core/intelligence/office_ai_service.py`) that automatically powers the router when no remote endpoint is available.

### Run the Office Realtime Service
Spin up the shared router as a standalone backend for Office add-ins:

```bash
uvicorn assistant_core.integrations.office_server:app --host 0.0.0.0 --port 8080
# WebSocket endpoint: ws://localhost:8080/ws
```

Clients should first send a `register` message (with `application`, `documentId`, etc.), then stream `live_edit` or `ai_request` payloads following the protocol outlined in `assistant_core/integrations/office_realtime.py`.

### Inspect the Canonical Technical Specification
Query the mission, architecture, and plane definitions derived from the OS Dashboard TOC:

```bash
python -m assistant_core.spec.cli mission --format json
python -m assistant_core.spec.cli architecture
python -m assistant_core.spec.cli failure
python -m assistant_core.spec.cli all --format json
```

The GUI exposes the same data under **Help → Technical Spec**.

---

## Architecture Overview

```
ai_os/             # FastAPI service and connectors powering the lightweight web dashboard
assistant_core/    # Intelligence, orchestration, integrations, and system services
assistant_hub/     # Backend logic shared by the terminal + GUI clients
assistant_hub_gui/ # Tk/ttkbootstrap desktop dashboard
examples/          # Demo scripts (see examples/demo_usage.py)
```

Each layer is modular, so you can import specific helpers (e.g. `assistant_core.system.operations.SystemOperationsController`) in your own scripts or use the GUI to drive them interactively.
---

## Configuration

Copy `config/default_config.yaml` to `config/config.yaml` (or set `CONFIG_PATH`) to override defaults. Most GUI actions also expose their settings directly; update API keys and tenant IDs from **Settings → Integrations** inside the dashboard.
---

## Testing

```bash
pytest tests/
```

---

## Contributing
- Fork the repo, create a virtualenv, and install dependencies via `pip install -r requirements.txt && pip install -e .`.
- Run `pytest tests/` plus `black`/`flake8` before opening a pull request.
- Document new GUI flows or CLI helpers in this README.

## License
MIT License (see `LICENSE`).

## Acknowledgments
- Beautiful Soup, Pandas, and Jinja2 for content generation
- OpenPyXL and python-docx for Office automation
- psutil and aiohttp for system telemetry and async networking
