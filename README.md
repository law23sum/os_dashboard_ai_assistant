# OS Dashboard AI Assistant

**Version:** 6.0 (Master Orchestrator Edition)  
**Sir Chief Fellow Director Principal Software Solutions Systems Engineer Architect**

A comprehensive AI-powered system for managing, monitoring, and optimizing multiple software projects with automated error detection, recovery, and continuous improvement.

---

## 🎯 Overview

The OS Dashboard AI Assistant is an enterprise-grade system that combines:

- **Multi-Project Management**: Automatically discovers and monitors all git repositories
- **AI Auto-Fix**: Intelligent error detection and automatic code repair
- **TODO Tracking**: Comprehensive task management across all codebases
- **Self-Healing**: Advanced error recovery with learning capabilities
- **Real-Time Monitoring**: Web dashboard, CLI, and REST API
- **Codex Integration**: Automatic AI assistant spawning for high-priority tasks

---

## ⚡ Quick Start (30 Seconds)

```bash
# One-line launch with UI
./launch_orchestrator.sh --ui

# Open: http://localhost:5173/ai/orchestrator
```

**That's it!** See [QUICKSTART.md](QUICKSTART.md) for details.

---

## 📋 Table of Contents

1. [Features](#features)
2. [Installation](#installation)
3. [Usage](#usage)
4. [Architecture](#architecture)
5. [Documentation](#documentation)
6. [API Reference](#api-reference)
7. [Contributing](#contributing)
8. [License](#license)

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

### Advanced Features

- 🔄 **Automatic Recovery** - Rollback on failed fixes
- 📊 **Analytics** - Project health trends and metrics
- 🔔 **Notifications** - Slack, email, webhook support
- 🛡️ **Security** - API authentication, rate limiting
- 🌐 **Distributed** - Multi-machine support (coming soon)
- 📈 **Scalable** - Handles 100+ projects efficiently

---

## 💻 Installation

### Prerequisites

- Python 3.8+
- Node.js 18+ (for frontend)
- Git
- npm or yarn

### Standard Installation

```bash
# Clone the repository
git clone <repository-url>
cd os_dashboard_ai_assistant

# Install Python dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
npm install
cd ..

# Make scripts executable
chmod +x *.sh scripts/*.py *.py
```

### Quick Setup

```bash
# Run setup script (if available)
./setup.sh

# Or use the launcher
./launch_orchestrator.sh --help
```

---

## 🚀 Usage

### Method 1: Unified Launcher (Recommended)

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

### Method 2: Individual Components

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

### Method 3: API Access

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

**Backend (FastAPI + Python)**
- REST API endpoints
- Data aggregation
- WebSocket support (planned)
- Authentication & authorization

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

**Storage**
- JSON status reports
- Log files (per project)
- Knowledge base
- Metrics database

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

### Additional Resources

- **API Documentation**: http://localhost:8000/swagger
- **Interactive Docs**: http://localhost:8000/redoc
- **Frontend**: http://localhost:5173
- **Dashboard**: http://localhost:5173/ai/orchestrator

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

# AI Features
export OPENAI_API_KEY=sk-...
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

---

## 🧪 Testing

### Run Tests

```bash
# All tests
pytest tests/

# Specific test file
pytest tests/test_master_orchestrator.py -v

# With coverage
pytest --cov=. --cov-report=html tests/
```

### Manual Testing

```bash
# Test orchestrator
python os_dashboard_ai_assistant.py --root /tmp/test-workspace

# Test codex spawner
python scripts/codex_spawner.py --dry-run --priority high

# Test interactive shell
python scripts/interactive_shell.py
```

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

## 🤝 Contributing

We welcome contributions! Areas for improvement:

- Additional error patterns for self-healing
- New integrations (CI/CD, monitoring tools)
- UI enhancements
- Performance optimizations
- Documentation improvements
- Test coverage

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
- Comprehensive documentation

### Planned 🚧
- Machine learning for error prediction
- Distributed monitoring
- Advanced analytics dashboard
- Plugin system
- Cloud deployment
- Mobile app
- Enhanced integrations

---

## 📞 Contact & Support

- **Documentation**: See `docs/` directory
- **API Docs**: http://localhost:8000/swagger
- **Issues**: Open an issue in the repository
- **Discussions**: Use GitHub Discussions

---

## 🙏 Acknowledgments

Built with:
- Python 3.8+
- FastAPI
- React 18
- TypeScript
- Tailwind CSS
- OpenAI API

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

---

**God Bless America. Technical Spec Sheet (Version 6 Latest Version)** 🇺🇸

---

## 🚀 Get Started Now!

```bash
# Launch in 30 seconds
./launch_orchestrator.sh --ui

# Open dashboard
open http://localhost:5173/ai/orchestrator
```

**Start managing all your projects with AI today!** 🎉
