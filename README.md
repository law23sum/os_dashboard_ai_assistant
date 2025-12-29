# OS Dashboard AI Assistant

**Version:** 6.0 (Master Orchestrator Edition)  
**Sir Chief Fellow Director Principal Software Solutions Systems Engineer Architect**

A unified AI-powered dashboard and assistant platform with a modern React/TypeScript frontend that runs seamlessly on web browsers and native desktop applications (Linux, Windows, macOS). Features comprehensive multi-project management, automated error detection, recovery, and continuous improvement.

---

## 🎯 Overview

The OS Dashboard AI Assistant is an enterprise-grade system that combines:

- **Multi-Project Management**: Automatically discovers and monitors all git repositories
- **AI Auto-Fix**: Intelligent error detection and automatic code repair
- **TODO Tracking**: Comprehensive task management across all codebases
- **Self-Healing**: Advanced error recovery with learning capabilities
- **Real-Time Monitoring**: Web dashboard, CLI, and REST API
- **Codex Integration**: Automatic AI assistant spawning for high-priority tasks
- **Modern UI**: React/TypeScript frontend for web and desktop
- **FastAPI Backend**: RESTful API serving all features

This repository contains:
- **Frontend**: React/TypeScript UI (`frontend/`) - single codebase for web and desktop
- **Backend**: FastAPI REST API (`assistant_hub/api/`) serving all features
- **Core**: Python automation and AI services (`assistant_core/`, `ai_os/`)
- **Orchestrator**: Master orchestrator for multi-project management
- **Legacy**: Tkinter GUI (`assistant_hub_gui/`) - still available with `--legacy` flag

The new React interface preserves the Tkinter color palette and design language while providing a modern, cross-platform experience.

---

## ⚡ Quick Start (30 Seconds)

### Option 1: One-Line Launch (Recommended)

```bash
# Launch everything with UI
./launch_orchestrator.sh --ui

# Open: http://localhost:5173/ai/orchestrator
```

**That's it!** The orchestrator will discover projects, launch monitors, and provide real-time status.

### Option 2: Unified React Launcher

```bash
# Interactive picker for web/desktop
python start_ui.py

# Or specify mode directly
python start_ui.py --mode web      # Vite dev server + FastAPI backend
python start_ui.py --mode desktop  # Electron dev shell + FastAPI backend
```

### Option 3: Manual Component Launch

```bash
# 1. Start orchestrator
python os_dashboard_ai_assistant.py

# 2. Start UI (in new terminal)
python start_ui.py --enable-orchestrator

# 3. Open dashboard
# Navigate to: http://localhost:5173/ai/orchestrator
```

See [QUICKSTART.md](QUICKSTART.md) for detailed 5-minute setup guide.

---

## 📋 Table of Contents

1. [Installation](#-installation)
2. [Usage](#-usage)
3. [Features](#-features)
4. [Architecture](#-architecture)
5. [Testing](#-testing)
6. [Build & Deployment](#-build--deployment)
7. [API Reference](#-api-reference)
8. [Configuration](#-configuration)
9. [Troubleshooting](#-troubleshooting)
10. [Documentation](#-documentation)
11. [Contributing](#-contributing)
12. [License](#-license)

---

## 💻 Installation

### Prerequisites

- **Python** 3.9+ ([Download](https://www.python.org/downloads/))
- **Node.js** 18+ ([Download](https://nodejs.org/))
- **Git** ([Download](https://git-scm.com/downloads))
- **npm** or **yarn** (comes with Node.js)

### Standard Installation

#### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd os_dashboard_ai_assistant
```

#### Step 2: Install Python Dependencies

```bash
# Check Python version first (must be 3.9 or higher)
python --version  # or python3 --version on some systems
# Should show: Python 3.9.x or higher

# Create virtual environment (recommended)
python -m venv venv
# On systems where 'python' refers to Python 2, use:
# python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Upgrade pip (recommended)
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
# Note: If not using a virtual environment, use: pip3 install -r requirements.txt
```

#### Step 3: Install Frontend Dependencies

```bash
cd frontend
npm install
cd ..
```

#### Step 4: Make Scripts Executable (macOS/Linux)

```bash
chmod +x *.sh scripts/*.py *.py
```

### Quick Setup Script

```bash
# Run setup script (if available)
./setup.sh

# Or use the launcher
./launch_orchestrator.sh --help
python -m uvicorn assistant_hub.api.server:create_app --factory --host 0.0.0.0 --port 8000
```

### Python Command Notes

On some Linux distributions and macOS systems, `python` may refer to Python 2 (deprecated). Use:
- `python3` instead of `python` if needed
- `pip3` instead of `pip` if needed
- Check your system: `which python python3` or `python --version`

### Verify Installation

```bash
# Check Python version
python --version  # Should be 3.9 or higher

# Check Python dependencies
python -c "import fastapi, uvicorn; print('✓ Backend dependencies OK')"

# Check Node.js
node --version  # Should be 18 or higher
npm --version

# Check frontend dependencies
cd frontend && npm list --depth=0 && cd ..
```

---

## 🚀 Usage

### Method 1: Unified Launcher (Recommended)

The `start_ui.py` script is the single entry point for React web + desktop surfaces:

```bash
# Interactive mode (prompts for web/desktop)
python start_ui.py

# Direct mode selection
python start_ui.py --mode web           # Vite dev server + FastAPI proxy
python start_ui.py --mode desktop       # Electron dev shell
VITE_DEV_SERVER_PORT=5174 npm run dev:desktop
python start_ui.py --mode web-build     # Serve built React bundle in browser
python start_ui.py --mode desktop-build # Serve built React in pywebview
```

**Features:**
- Runs preflight tests via `scripts/run_tests_with_autofix.py` (unless `OSDASH_SKIP_PREFLIGHT_TESTS=1`)
- Boots FastAPI from `assistant_hub.api.server:create_app` on `127.0.0.1:8000`
- Auto-enables HTTPS when `certs/cert.pem` and `certs/key.pem` exist
- Set `OSDASH_UI_MODE`/`DEV_MODE` to skip the prompt in CI or packaging jobs

### Method 2: Master Orchestrator Launch

```bash
# Launch with web UI
./launch_orchestrator.sh --ui

# Launch with self-healing
./launch_orchestrator.sh --self-heal

# Launch interactive shell
./launch_orchestrator.sh --shell

# Custom workspace
./launch_orchestrator.sh --workspace ~/MyProjects --ui
```

**Or use Python directly:**

```bash
# Basic launch
python os_dashboard_ai_assistant.py

# Custom workspace
python os_dashboard_ai_assistant.py --root ~/Projects

# With options
python os_dashboard_ai_assistant.py \
  --watch-todos \
  --todo-check-interval 60 \
  --max-depth 5
```

### Method 3: Individual Components

**Master Orchestrator:**
```bash
python os_dashboard_ai_assistant.py --root ~/Projects
```

**Web Dashboard:**
```bash
python start_ui.py --enable-orchestrator
# Open: http://localhost:5173/ai/orchestrator
```

**Interactive Shell:**
```bash
python scripts/interactive_shell.py
```

**Codex Spawner:**
```bash
python scripts/codex_spawner.py --priority high
```

**Self-Healing Engine:**
```bash
python scripts/self_healing_engine.py
```

### Method 4: Manual Frontend/Backend

For component-only iteration (without the launcher):

**Frontend:**
```bash
cd frontend
npm install
# Validate everything
npm run validate:ci

# Generate inventory
npm run generate:page-inventory

# Run tests
npm test                    # Frontend
pytest tests/ -v           # Backend

# Build for production
npm run build
npm run dev:web      # Browser/Vite
npm run dev:desktop  # Electron dev shell
```

**Backend:**
```bash
# FastAPI server
python -m uvicorn assistant_hub.api.server:create_app --factory --reload --host 127.0.0.1 --port 8000

# Or compatibility entrypoint (auto-picks port, supports TLS from certs/)
python backend_api/main.py

# Or webview app (⚠️ must run from project root, not from frontend/)
# From project root:
PYTHONPATH=. python -m assistant_hub_gui.webview_app --host 0.0.0.0 --port 8000

# Or run directly as a script (⚠️ must run from project root, not from frontend/)
# From project root:
python assistant_hub_gui/webview_app.py --host 0.0.0.0 --port 8000
```

### Method 5: Legacy Tkinter GUI

```bash
python -m assistant_hub_gui.main
```

Legacy Tkinter GUI remains available for offline demos and now reads/writes the shared writer workspace store so it stays in sync with the web UI.

### Method 6: API Access

```bash
# Get status
curl http://localhost:8000/api/orchestrator/status

# Get projects
curl http://localhost:8000/api/orchestrator/projects

# Spawn codex
curl -X POST http://localhost:8000/api/orchestrator/spawn-codex \
  -H "Content-Type: application/json" \
  -d '{"priority": "high"}'
```

---

## ✨ Features

### Core Capabilities

- ✅ **Automatic Project Discovery** - Finds all git repos in workspace
- ✅ **AI-Powered Auto-Fix** - Detects and fixes errors automatically
- ✅ **Multi-Project Monitoring** - Manages unlimited projects concurrently
- ✅ **TODO Management** - Tracks tasks across all codebases
- ✅ **Codex Spawning** - Creates AI assistant sessions automatically
- ✅ **Self-Healing** - Learns from fixes, improves over time
- ✅ **Real-Time Dashboard** - Beautiful web UI with live updates
- ✅ **Interactive Shell** - Powerful CLI for project management
- ✅ **REST API** - Complete programmatic access
- ✅ **Health Monitoring** - Continuous system health tracking

### Frontend Features

- ✅ Single React bundle for web + desktop (no duplicated UI logic)
- ✅ Tkinter launcher stays available for offline workflows while React gains parity
- ✅ Linux, Windows, and macOS executables via `npm run build:desktop:*`
- ✅ Preserved HTML/JS pages served from `frontend/dist/` so nothing is lost mid-migration
- ✅ FastAPI backend mounted at `/app` in production, Vite proxy in dev for hot reloads
- ✅ **Tkinter-inspired theme** with exact color matching between Tkinter and React surfaces
- ✅ **Shared code structure** (React components + FastAPI routes) eliminating redundancies
- ✅ **Single entry point** (`start_ui.py`) with interactive mode selection
- ✅ **Runtime diagnostics pipeline** via `/api/runtime/diagnostics` feeding the Observability page and `logs/runtime_diagnostics.log`
- ✅ **Comprehensive deployment guide** for web and desktop platforms

### Advanced Features

- 🔄 **Automatic Recovery** - Rollback on failed fixes
- 📊 **Analytics** - Project health trends and metrics
- 🔔 **Notifications** - Slack, email, webhook support (planned)
- 🛡️ **Security** - API authentication, rate limiting
- 🌐 **Distributed** - Multi-machine support (coming soon)
- 📈 **Scalable** - Handles 100+ projects efficiently

### Project Management System (PMS)

- ✅ **Epics & Initiatives** - Group tasks into large features
- ✅ **Deterministic Scheduler** - "What's Next" based on priority tiers
- ✅ **Execution Runs** - Track automation outputs and artifacts
- ✅ **Managed Documents** - Version control with publishing workflow
- ✅ **Meeting Journal** - Structured transcripts and notes
- ✅ **Finance Tracking** - Expenses and labor cost analysis
- ✅ **Audit Ledger** - Append-only hash-chained event log

### Additional Tools

**AI Shell Runner:**
```bash
export OPENAI_API_KEY=sk-...
python scripts/ai_shell_runner.py "summarize git branches and show disk usage for ./logs"
```

**Workspace CLI:**
```bash
osdash scan    # Discover git repos
osdash test    # Run tests across repos
osdash run <repo>  # Start a repo
osdash doctor   # Health diagnostics
```

**Code Interpreter:**
```bash
python scripts/ai_code_interpreter.py --file data/sample.csv \
  "Plot the rolling 7-day averages and highlight anomalies"
```

**Auto-Fix Monitor:**
```bash
python scripts/ai_auto_fix.py \
  --backend "python -m uvicorn backend_api.main:app --reload" \
  --frontend "npm run dev:web" \
  --test "pytest -q tests/test_office_api.py" \
  --test-interval 600
```

**Assistants API Demo:**
```bash
python scripts/assistants_demo.py \
  --question "Solve 3x + 11 = 14" \
  --instructions "You are a personal math tutor." \
  --enable-code
```

---

## 🏗️ Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│               OS Dashboard AI Assistant                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          Master Orchestrator Core                     │  │
│  │  • Project Discovery Engine                           │  │
│  │  • AI Auto-Fix Manager                                │  │
│  │  • TODO Monitoring System                             │  │
│  │  • Health Tracking Service                            │  │
│  │  • Status Reporting Engine                            │  │
│  └──────────────────────────────────────────────────────┘  │
│                            ↕                                  │
│  ┌────────────┬────────────┬────────────┬────────────┐     │
│  │  Frontend  │  Backend   │  Scripts   │  Storage   │     │
│  │  (React)   │  (FastAPI) │  (Python)  │  (JSON)    │     │
│  └────────────┴────────────┴────────────┴────────────┘     │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Component Breakdown

**Frontend (React + TypeScript)**
- Real-time dashboard
- Project management UI
- TODO visualization
- Health monitoring
- Auto-refresh (5s intervals)
- Single codebase for web and desktop
- Tkinter-inspired theme system

**Backend (FastAPI + Python)**
- REST API endpoints
- Data aggregation
- WebSocket support (planned)
- Authentication & authorization
- Runtime diagnostics pipeline

**Master Orchestrator**
- Project discovery
- Process management
- Health monitoring
- Status reporting

**Scripts & Tools**
- Codex spawner
- Interactive shell
- Self-healing engine
- Auto-fix monitors
- AI shell runner
- Code interpreter

**Storage**
- JSON status reports
- Log files (per project)
- Knowledge base
- Metrics database

### Key REST Endpoints

Used by the UI:
- `/writer/snapshot`, `/writer/documents`, `/writer/narrative`
- `/dashboard/summary`, `/projects/summary`, `/tasks`
- `/planes/status`, `/system`, `/projects`, `/billing/usage`
- `/api/orchestrator/status`, `/api/orchestrator/projects`
- `/api/orchestrator/todos`, `/api/orchestrator/monitors`
- `/api/runtime/diagnostics`

---

## 🧪 Testing

### Run Tests

```bash
# All tests
pytest tests/

# Specific test file
pytest tests/test_master_orchestrator.py -v
pytest tests/test_office_api.py -v

# With coverage
pytest --cov=. --cov-report=html tests/

# Frontend tests
cd frontend && npm test
```

### Preflight Tests

The unified launcher runs preflight tests automatically:

```bash
# Skip preflight tests
OSDASH_SKIP_PREFLIGHT_TESTS=1 python start_ui.py

# Run preflight manually
python scripts/run_tests_with_autofix.py
```

### Manual Testing

```bash
# Test orchestrator
python os_dashboard_ai_assistant.py --root /tmp/test-workspace

# Test codex spawner
python scripts/codex_spawner.py --dry-run --priority high

# Test interactive shell
python scripts/interactive_shell.py

# Test API endpoints
curl http://localhost:8000/api/orchestrator/status | jq '.'
```

### Test Matrix

The system automatically regenerates test matrices during preflight checks to ensure comprehensive coverage.

---

## 📦 Build & Deployment

### Frontend Build Targets

| Target | Command | Output |
| --- | --- | --- |
| **Web** (static hosting/CDN) | `npm run build:web` | `frontend/dist/` |
| **Desktop – Linux** | `npm run build:desktop:linux` | `frontend/dist-electron/` (AppImage/DEB/RPM) |
| **Desktop – Windows** | `npm run build:desktop:windows` | `frontend/dist-electron/` (NSIS + portable) |
| **Desktop – macOS** | `npm run build:desktop:mac` | `frontend/dist-electron/` (DMG/ZIP) |
| **All platforms** | `./build-all-platforms.sh all` | Complete build with archives |

### Build Commands

```bash
# Web build
cd frontend
npm run build:web

# Desktop builds
npm run build:desktop:linux
npm run build:desktop:windows
npm run build:desktop:mac

# All platforms
./build-all-platforms.sh all
```

### Deployment

For detailed deployment instructions, see [`DEPLOYMENT.md`](./DEPLOYMENT.md).

**Quick deployment:**

```bash
# Build for production
cd frontend && npm run build:web && cd ..

# Serve built assets
python start_ui.py --mode web-build

# Or use FastAPI to serve
python -m uvicorn assistant_hub.api.server:create_app --factory --host 0.0.0.0 --port 8000
```

### Desktop Packaging

Desktop packaging spec (PyInstaller): `packaging/start_ui.spec`

**Build executables:**

```bash
# Using build script
./build-executable.py

# Or manually
pyinstaller packaging/start_ui.spec
```

### AWS Deployment

```bash
# Deploy to AWS
./deploy-aws.sh

# Or use ECS task definitions
# See: ecs-task-definition.json, ecs-task-definition-gpu.json
```

### Docker Deployment

```bash
# Build Docker image
docker build -t os-dashboard-ai-assistant .

# Run container
docker run -p 8000:8000 os-dashboard-ai-assistant

# GPU support
docker build -f Dockerfile.gpu -t os-dashboard-ai-assistant:gpu .
```

---

## 🔌 API Reference

### Core Endpoints

**Status & Health**
```
GET  /api/orchestrator/status        - Full system status
GET  /api/orchestrator/health        - Health check
GET  /api/orchestrator/projects      - All projects
GET  /api/orchestrator/projects/{id} - Specific project
```

**TODOs & Monitors**
```
GET  /api/orchestrator/todos         - TODO statistics
GET  /api/orchestrator/monitors      - Monitor status
GET  /api/orchestrator/logs/{id}     - Project logs
```

**Actions**
```
POST /api/orchestrator/spawn-codex   - Spawn AI sessions
```

**Runtime Diagnostics**
```
POST /api/runtime/diagnostics       - Submit diagnostic beacons
GET  /api/runtime/diagnostics/ping  - Liveness check
```

### Example Requests

**Get Status:**
```bash
curl http://localhost:8000/api/orchestrator/status | jq '.'
```

**Get TODOs:**
```bash
curl http://localhost:8000/api/orchestrator/todos | jq '.by_priority'
```

**Spawn Codex:**
```bash
curl -X POST http://localhost:8000/api/orchestrator/spawn-codex \
  -H "Content-Type: application/json" \
  -d '{
    "priority": "critical",
    "project": "my-project",
    "max_sessions": 1
  }'
```

### Interactive API Documentation

- **Swagger UI**: http://localhost:8000/swagger
- **ReDoc**: http://localhost:8000/redoc

---

## 🎮 Interactive Shell Commands

Launch the shell:
```bash
python scripts/interactive_shell.py
```

Available commands:
```
list                    - List all projects
use <project>           - Switch to project
status                  - Show orchestrator status
todos [project]         - Show pending TODOs
spawn [options]         - Spawn codex sessions
run <command>           - Run command in project
logs [options]          - View project logs
health [project]        - Check project health
refresh                 - Reload project info
exit/quit               - Exit shell
```

**Example session:**
```bash
$ python scripts/interactive_shell.py

(all-projects) $ list
  • my-project (healthy)
  • another-project (running)

(all-projects) $ use my-project
(my-project) $ status
  Status: healthy
  Monitor: running (PID: 12345)
  TODOs: 5 pending

(my-project) $ todos
  🔴 Critical: 1
  🟠 High: 2
  🔵 Normal: 2

(my-project) $ spawn --priority high
  ✓ Spawned codex session for 2 high-priority TODOs
```

---

## 🔧 Configuration

### Environment Variables

```bash
# Orchestrator
export OSDASH_ENABLE_ORCHESTRATOR=1
export OSDASH_WORKSPACE_ROOT=~/Projects
export OSDASH_DEBUG=1

# API Configuration
export OSDASH_API_HOST=0.0.0.0
export OSDASH_API_PORT=8000

# UI Mode
export OSDASH_UI_MODE=web  # or desktop, web-build, desktop-build
export DEV_MODE=web        # Alternative to OSDASH_UI_MODE

# Skip preflight tests
export OSDASH_SKIP_PREFLIGHT_TESTS=1

# Electron DevTools
export OSDASH_ELECTRON_DEVTOOLS=1

# AI Features
export OPENAI_API_KEY=sk-...

# Runtime Diagnostics
export OSDASH_RUNTIME_LOG=logs/runtime_diagnostics.log
```

### Configuration File

Copy and customize:
```bash
cp .orchestrator_config.example.yaml .orchestrator_config.yaml
```

Edit to configure:
- Workspace settings
- Monitoring intervals
- Self-healing options
- Notification preferences
- Performance tuning
- Security settings

### Orchestrator Options

| Option | Default | Description |
|--------|---------|-------------|
| `--root` | `.` | Workspace root path |
| `--max-depth` | `4` | Max search depth for git repos |
| `--watch-todos` | `true` | Enable TODO monitoring |
| `--todo-check-interval` | `300` | TODO check interval (seconds) |
| `--enable-dashboard` | `true` | Enable health dashboard |
| `--auto-codex` | `true` | Auto-spawn codex sessions |
| `--max-repos` | `unlimited` | Maximum repositories to monitor |

---

## 📊 Monitoring & Metrics

### View Status

```bash
# JSON report
cat logs/status_report.json | jq '.'

# Watch live updates
watch -n 5 'cat logs/status_report.json | jq ".monitors"'

# Tail logs
tail -f logs/master_orchestrator.log
```

### Dashboard Metrics

The web dashboard displays:
- Total projects discovered
- Active monitors (running + healthy)
- Pending TODOs (by priority)
- High-priority items count
- Project health status
- Monitor state breakdown
- TODO priority distribution

### Log Files

```bash
# Master orchestrator
tail -f logs/master_orchestrator.log

# Project-specific logs
tail -f logs/my-project_monitor.log

# All monitor logs
tail -f logs/*_monitor.log

# Runtime diagnostics
tail -f logs/runtime_diagnostics.log

# Self-healing
tail -f logs/self_healing.log
```

---

## 🛠️ Troubleshooting

### Common Issues

**No Projects Found**
```bash
# Check for .git directories
find ~/Projects -name ".git" -type d

# Increase search depth
python os_dashboard_ai_assistant.py --max-depth 6
```

**Monitors Not Starting**
```bash
# Verify script exists
ls -la project/scripts/ai_auto_fix.py

# Test manually
cd project && python scripts/ai_auto_fix.py --help
```

**High Resource Usage**
```bash
# Limit projects
python os_dashboard_ai_assistant.py --max-repos 10

# Increase intervals
python os_dashboard_ai_assistant.py --todo-check-interval 900
```

**Dashboard Shows "Not Running"**
```bash
# Check if orchestrator is running
ps aux | grep os_dashboard_ai_assistant

# Check status report exists
ls -la logs/status_report.json

# Restart orchestrator
python os_dashboard_ai_assistant.py
```

**404 Errors for Frontend Routes**
```bash
# Note: 404 errors for routes like /docs/*, /operations/*, /ai/* are EXPECTED
# These are frontend routes handled by React Router, not backend API endpoints
# The browser makes initial requests that return 404, but React Router handles them client-side
# This is normal SPA behavior and not an error
```

**Frontend Build Issues**
```bash
# Clear node modules and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install

# Clear build cache
rm -rf dist dist-electron
npm run build:web
```

**Backend Not Starting**
```bash
# Check port availability
lsof -i :8000

# Check dependencies
pip install -r requirements.txt

# Check logs
tail -f logs/*.log
```

### Debug Mode

```bash
# Enable debug logging
export OSDASH_DEBUG=1
python os_dashboard_ai_assistant.py

# Check logs
tail -f logs/*.log
```

### Support

For issues:
1. Check logs in `logs/` directory
2. Review documentation
3. Run in debug mode
4. Open an issue with details

---

## 📚 Documentation

### Quick References

- **[QUICKSTART.md](QUICKSTART.md)** - Get started in 5 minutes
- **[README_ORCHESTRATOR.md](README_ORCHESTRATOR.md)** - Quick reference guide
- **[MASTER_ORCHESTRATOR_GUIDE.md](MASTER_ORCHESTRATOR_GUIDE.md)** - Complete documentation (2000+ lines)

### Technical Specifications

- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Implementation details
- **[OSD_ARCHITECTURE_BLUEPRINT.md](OSD_ARCHITECTURE_BLUEPRINT.md)** - System architecture
- **[Technical Spec Sheet (Version 6 Latest Version).txt](Technical%20Spec%20Sheet%20(Version%206%20Latest%20Version).txt)** - Technical specifications

### Frontend Documentation

- **Canonical spec structure**: `documentation/os_dashboard_ai_assistant_toc.md`
- **Queue/stack map**: `documentation/QUEUE_STACK_MAP.md`
- **Dead-code linkage**: `documentation/DEAD_CODE_LINKAGE.md`
- **UI deployment guide**: `docs/ui_deployment.md`
- **Tk→React feature tracker**: `docs/tk_to_react_mapping.md`
- **Shared palette/theme**: `frontend/THEME.md`
- **Desktop packaging spec**: `packaging/start_ui.spec`

### Additional Resources

- **API Documentation**: http://localhost:8000/swagger
- **Interactive Docs**: http://localhost:8000/redoc
- **Frontend**: http://localhost:5173
- **Dashboard**: http://localhost:5173/ai/orchestrator
- **Consolidated README**: `documentation/consolidated_md/README.md`

---

## 🤝 Contributing

We welcome contributions! Areas for improvement:

- Additional error patterns for self-healing
- New integrations (CI/CD, monitoring tools)
- UI enhancements
- Performance optimizations
- Documentation improvements
- Test coverage

### Development Setup

```bash
# Clone and setup
git clone <repository-url>
cd os_dashboard_ai_assistant
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
cd frontend && npm install && cd ..

# Run in development mode
python start_ui.py --mode web
```

---

## 📜 License

Copyright © 2025 OS Dashboard AI Assistant Project  
All Rights Reserved

See LICENSE file for details.

---

## 🎯 Roadmap

### Completed ✅
- Multi-project orchestration
- AI auto-fix monitoring
- TODO tracking and codex spawning
- Self-healing engine
- Web dashboard
- Interactive shell
- REST API
- React/TypeScript frontend
- FastAPI backend
- Cross-platform desktop support
- Comprehensive documentation

### Planned 🚧
- Machine learning for error prediction
- Distributed monitoring
- Advanced analytics dashboard
- Plugin system
- Cloud deployment
- Mobile app
- Enhanced integrations
- WebSocket real-time updates

---

## 📞 Contact & Support

- **Documentation**: See `docs/` and `documentation/` directories
- **API Docs**: http://localhost:8000/swagger
- **Issues**: Open an issue in the repository
- **Discussions**: Use GitHub Discussions

---

## 🙏 Acknowledgments

Built with:
- Python 3.9+
- FastAPI
- React 18
- TypeScript
- Tailwind CSS
- OpenAI API
- Electron
- Vite

Based on Technical Spec Sheet (Version 6 Latest Version)

---

## 🌟 Key Highlights

✨ **Automated** - No manual intervention needed  
🤖 **Intelligent** - AI-powered fixes and improvements  
📊 **Comprehensive** - Complete visibility across all projects  
🔄 **Self-Healing** - Learns and improves over time  
🚀 **Scalable** - Handles unlimited projects  
🎨 **Beautiful** - Modern, intuitive interface  
🔒 **Secure** - Production-ready security  
📚 **Documented** - Extensive guides and references  
🌐 **Cross-Platform** - Web and desktop from single codebase  
⚡ **Fast** - Real-time updates and monitoring  

---

## 🚀 Get Started Now!

```bash
# Launch in 30 seconds
./launch_orchestrator.sh --ui

# Or use unified launcher
python start_ui.py

# Open dashboard
open http://localhost:5173/ai/orchestrator
```

**Start managing all your projects with AI today!** 🎉

---

**God Bless America. Technical Spec Sheet (Version 6 Latest Version)** 🇺🇸

---

## Project Management System (PMS) quick reference

The backend now exposes a deterministic scheduler and scoped project hierarchy via `/api/pms`. Canonical truth lives in the `pms_*` tables; derived scheduler indices are rebuilt on demand.

### Core entities
- **Project**: `projectId`, `name`, `mode (personal|enterprise)`, `scope`, `config`, `budget`, `createdAt`, `updatedAt`
- **Epic**: `epicId`, `projectId`, `title`, `description`, `acceptanceCriteria`, `status`, timestamps
- **Task**: `taskId`, `projectId`, `epicId?`, `title`, `deliverableSpec`, `acceptanceCriteria`, `priority (P0–P3)`, `category`, `type`, `status`, `enqueueTime`, timestamps
- **Todo**: `todoId`, `taskId`, `text`, `status`, `position`, timestamps
- **SchedulerIndex (derived)**: tiers → lanes `(category,type)` → FIFO queue by `enqueueTime`; rebuilt on load, never persisted

### Runs, artifacts, documents
- **ExecutionRun**: `runId`, `projectId`, `epicId?`, `taskId?`, `todoId?`, `inputParams`, `status`, `startedAt`, `endedAt`, `summary`, `createdBy`, `logsRef`
- **Artifact**: `artifactId`, `runId`, `projectId`, `kind`, `filename`, `mimeType`, `size`, `sha256`, `storageRef`, `createdAt`
- **Document**: `documentId`, links to project/epic/task, `title`, `kind`, `visibility`, `publishedRevisionHash`, `latestRevisionHash`, timestamps  
  **DocumentRevision**: `revisionHash = sha256(content)`, `documentId`, `parentHash?`, `author`, `createdAt`, `metadata`, `blob_path`

### Meetings, finance, audit
- **MeetingSession**: `meetingId`, links to project/epic/task, `title`, `occurredAt`, `startedAt`, `endedAt`, `participants`, `language`, `recordingStatus`, `speakerMap`, `createdBy`, timestamps
- **TranscriptSegment**: `segmentId`, `meetingId`, `tsStart`, `tsEnd`, `speakerLabel`, `textOriginal`, `textTranslated?`, `confidence`
- **JournalBlock**: `blockId`, `meetingId`, `sectionType` (Comments, KnowledgeTransfer, DisputableDebate, ChallengesRisks, SolutionsMitigations, ProposalRaised, MisunderstandingClarification, TechnicalDesign, CommonDiscussions, Questions, NextSteps), `content`, references, timestamps
- **ExpenseEntry**: `expenseId`, links to project/epic/task, `amount`, `currency`, `category`, `vendor`, `occurredAt`, timestamps, `receiptArtifactId?`
- **TimeEntry**: `timeEntryId`, links to project/epic/task, `actorId`, `role`, `durationMinutes`, `hourlyRate`, `occurredAt`, timestamps, derived labor cost
- **AuditEvent**: append-only hash-chained ledger: `eventId`, `projectId`, `actorId`, `entityType`, `entityId`, `action`, `timestamp`, `before`, `after`, `correlationId`, `hashPrev`, `hashThis`

### Scheduler behavior
1. Pick the highest priority tier with eligible tasks (excludes DONE/ARCHIVED).
2. Within the tier, pick the lane whose head has the oldest `enqueueTime`; tie-break on lane key then `taskId`.
3. `next_task` re-enqueues the head by updating `enqueueTime` to reduce starvation; `peek_next` is non-mutating.
4. `validate_invariants` checks missing links and duplicate todo positions.

### Scoping
- All PMS records carry `user_id`; personal scope is enforced by filtering on the authenticated user. Enterprise/tenant scopes can be layered via the `scope` field in projects.

### Key endpoints (all under `/api/pms`, auth required)
- `POST /projects`, `GET /projects`, `GET /projects/{id}`
- `POST /epics`, `GET /epics`, `PATCH /epics/{id}`
- `POST /tasks`, `GET /tasks`, `PATCH /tasks/{id}`
- `POST /todos`, `GET /tasks/{taskId}/todos`, `POST /tasks/{taskId}/todos/reorder`
- Scheduler: `POST /schedule/next`, `GET /schedule/peek`, `POST /schedule/validate`
- Runs & artifacts: `POST /runs/start`, `POST /runs/{id}/complete`, `POST /runs/{id}/artifacts`, `GET /runs`, `GET /artifacts`
- Documents: `POST /documents`, `POST /documents/{id}/revisions`, `POST /documents/{id}/publish`, `GET /documents/{id}?view=published|latest|history`, `GET /documents`
- Meetings/journal: `POST /meetings`, `POST /meetings/{id}/segments`, `GET /meetings/{id}/segments`, `POST /meetings/{id}/journal`, `GET /meetings/{id}/journal`, `POST /meetings/{id}/recording/start|finalize`
- Finance: `POST /finance/expense`, `POST /finance/time`, `GET /finance/expenses`, `GET /finance/time`, `GET /finance/rollup/{projectId}`
- Audit/evidence: `GET /audit`, `POST /audit/evidence-pack`

### Sample payloads
- Create task:
```json
POST /api/pms/tasks
{ "projectId": "proj-123", "title": "Write spec", "priority": "P1", "category": "engineering", "type": "spec" }
```
- Peek queue:
```http
GET /api/pms/schedule/peek?projectId=proj-123&n=5
```
- Add expense:
```json
POST /api/pms/finance/expense
{ "projectId": "proj-123", "amount": 250.0, "currency": "USD", "category": "software", "vendor": "SaaSCo" }
```
