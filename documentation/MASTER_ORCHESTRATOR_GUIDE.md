# Master Orchestrator - Complete Guide

**Version:** 1.0  
**Date:** December 19, 2025  
**Author:** Sir Chief Fellow Director Principal Software Solutions Systems Engineer Architect

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Architecture](#architecture)
4. [Features](#features)
5. [Usage Guide](#usage-guide)
6. [API Reference](#api-reference)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)
9. [Advanced Configuration](#advanced-configuration)

---

## 🎯 Overview

The Master Orchestrator is a comprehensive AI-powered system that manages multiple projects across your workspace. It provides:

- **Automatic Project Discovery**: Finds all git repositories in your workspace
- **AI Auto-Fix Monitoring**: Launches intelligent monitors for each project
- **TODO Management**: Tracks and prioritizes TODO items across all codebases
- **Codex Spawning**: Automatically creates AI assistant sessions for high-priority tasks
- **Health Monitoring**: Continuously monitors project health and status
- **Self-Healing**: Automatically detects and fixes common errors
- **Unified Interface**: Provides web UI, CLI, and API access

---

## 🚀 Quick Start

### Method 1: Standalone Launch

```bash
# Basic launch
python os_dashboard_ai_assistant.py

# With custom workspace
python os_dashboard_ai_assistant.py --root ~/Projects

# With TODO monitoring
python os_dashboard_ai_assistant.py --watch-todos --todo-check-interval 60
```

### Method 2: Integrated with UI

```bash
# Launch UI with orchestrator
python start_ui.py --enable-orchestrator

# Or set environment variable
OSDASH_ENABLE_ORCHESTRATOR=1 python start_ui.py
```

### Method 3: Interactive Shell

```bash
# Launch interactive shell
python scripts/interactive_shell.py

# Available commands in shell:
#   list - List all projects
#   use <project> - Switch to project
#   status - Show orchestrator status
#   todos - Show pending TODOs
#   spawn - Spawn codex sessions
#   run <cmd> - Run command in project
#   logs - View project logs
```

---

## 🏗️ Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────────┐
│                  Master Orchestrator                         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │         Project Discovery Engine                     │   │
│  │  • .git detection                                    │   │
│  │  • Project analysis                                  │   │
│  │  • Metadata extraction                               │   │
│  └─────────────────────────────────────────────────────┘   │
│                            ↓                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │         AI Auto-Fix Monitor Manager                  │   │
│  │  • Process spawning                                  │   │
│  │  • Output monitoring                                 │   │
│  │  • Health tracking                                   │   │
│  └─────────────────────────────────────────────────────┘   │
│                            ↓                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │         TODO Monitoring System                       │   │
│  │  • TODO extraction                                   │   │
│  │  • Priority analysis                                 │   │
│  │  • Codex spawning                                    │   │
│  └─────────────────────────────────────────────────────┘   │
│                            ↓                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │         Health & Status Reporting                    │   │
│  │  • Real-time metrics                                 │   │
│  │  • JSON reports                                      │   │
│  │  • API endpoints                                     │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
              ↓               ↓               ↓
   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
   │  Web UI      │  │  CLI Tools   │  │  REST API    │
   │  Dashboard   │  │  Shell       │  │  Endpoints   │
   └──────────────┘  └──────────────┘  └──────────────┘
```

### Data Flow

1. **Discovery Phase**
   - Recursively scans workspace for `.git` directories
   - Analyzes each project (tests, auto-fix scripts, TODOs)
   - Builds project registry

2. **Monitoring Phase**
   - Launches AI auto-fix monitors for capable projects
   - Monitors process output in real-time
   - Logs to project-specific files

3. **TODO Analysis Phase**
   - Extracts TODO items from markdown files
   - Categorizes by priority (critical, high, normal, low)
   - Generates codex input files

4. **Health Tracking Phase**
   - Checks monitor process health
   - Updates status report every 5 minutes
   - Triggers alerts on failures

---

## ✨ Features

### 1. Project Discovery

The orchestrator automatically discovers all projects in your workspace:

```python
# Projects are identified by .git directories
projects/
├── project-a/.git  ← Discovered
├── project-b/.git  ← Discovered
└── project-c/      ← Skipped (no .git)
```

**Discovery includes:**
- Project path and name
- Current git branch
- Presence of `scripts/ai_auto_fix.py`
- Presence of tests
- TODO files

### 2. AI Auto-Fix Monitoring

For each project with `scripts/ai_auto_fix.py`, the orchestrator:

- Launches a dedicated monitor process
- Streams output to `logs/{project}_monitor.log`
- Automatically fixes errors using AI
- Tracks health and status

**Monitor Lifecycle:**
```
[Discovered] → [Running] → [Healthy] ← Self-healing loop
                    ↓
              [Unhealthy] → Auto-recovery
                    ↓
              [Stopped/Error] → Restart
```

### 3. TODO Management

Tracks TODO items across all projects:

**Supported TODO Formats:**
```markdown
- [ ] Regular TODO
- [ ] CRITICAL: High priority item
- [ ] TODO: Normal priority
- [ ] FIXME: Code fix needed
- [ ] HACK: Technical debt
```

**Priority Detection:**
- `critical`, `urgent`, `asap` → Critical
- `important`, `high` → High
- `low`, `someday`, `maybe` → Low
- Default → Normal

### 4. Codex Spawning

Automatically spawns AI assistant sessions for high-priority TODOs:

```bash
# Manual spawning
python scripts/codex_spawner.py --priority high

# Automatic spawning (when enabled)
# Triggers when critical/high priority TODOs detected
```

**Spawning Process:**
1. Reads status report for TODO counts
2. Filters by priority and project
3. Generates context file with TODO details
4. Opens new terminal with context
5. AI assistant ready to work

### 5. Health Monitoring

Continuous health monitoring includes:

- **Process Health**: Monitor process status
- **Log Analysis**: Error pattern detection
- **Performance Metrics**: Response times, throughput
- **Resource Usage**: Memory, CPU tracking

**Health States:**
- 🟢 **Healthy**: All systems operational
- 🟡 **Warning**: Minor issues detected
- 🔴 **Critical**: Major issues, intervention needed

### 6. Self-Healing

Advanced error recovery system:

**Detection:**
- Pattern matching on log output
- Frequency tracking
- Severity classification

**Recovery:**
- Automatic backup creation
- Strategy execution
- Success rate tracking
- Rollback on failure

**Learning:**
- Records successful fixes
- Updates knowledge base
- Improves over time

---

## 📖 Usage Guide

### Basic Operations

#### 1. Launch the Orchestrator

```bash
# Default workspace (current directory)
python os_dashboard_ai_assistant.py

# Custom workspace
python os_dashboard_ai_assistant.py --root ~/MyProjects

# With options
python os_dashboard_ai_assistant.py \
  --root ~/Projects \
  --max-depth 5 \
  --todo-check-interval 300 \
  --enable-dashboard
```

#### 2. View Status

**Via CLI:**
```bash
# Read status report
cat logs/status_report.json | jq '.'

# Using interactive shell
python scripts/interactive_shell.py
(all-projects) $ status
```

**Via Web UI:**
```bash
# Launch UI with orchestrator
python start_ui.py --enable-orchestrator

# Navigate to: http://localhost:5173/ai/orchestrator
```

**Via API:**
```bash
curl http://localhost:8000/api/orchestrator/status | jq '.'
```

#### 3. Manage TODOs

**List TODOs:**
```bash
# Via interactive shell
python scripts/interactive_shell.py
(all-projects) $ todos

# Or specific project
(all-projects) $ todos my-project
```

**Spawn Codex:**
```bash
# Spawn for high-priority TODOs
python scripts/codex_spawner.py --priority high

# Spawn for specific project
python scripts/codex_spawner.py --project my-project

# Limit number of sessions
python scripts/codex_spawner.py --max-sessions 1
```

#### 4. Monitor Logs

**View Recent Logs:**
```bash
# Via interactive shell
python scripts/interactive_shell.py
(all-projects) $ use my-project
(my-project) $ logs

# Or directly
tail -f logs/my-project_monitor.log
```

**Search Logs:**
```bash
# Find errors
grep -i error logs/*_monitor.log

# Find specific patterns
grep "HTTP 500" logs/*_monitor.log
```

### Advanced Operations

#### 1. Custom Project Filtering

```python
# In your code
from os_dashboard_ai_assistant import MasterOrchestrator

orchestrator = MasterOrchestrator(
    root=Path("~/Projects"),
    max_depth=4,
)

# Filter projects
projects = orchestrator.discover_projects()
python_projects = [p for p in projects if (p.path / "setup.py").exists()]
```

#### 2. Programmatic Control

```python
from os_dashboard_ai_assistant import MasterOrchestrator

# Create instance
orchestrator = MasterOrchestrator()

# Start monitoring
orchestrator.start()

# Get status
report = orchestrator.generate_status_report()

# Stop
orchestrator.stop()
```

#### 3. Custom Recovery Strategies

```python
from scripts.self_healing_engine import SelfHealingEngine, RecoveryStrategy

engine = SelfHealingEngine()

# Add custom strategy
strategy = RecoveryStrategy(
    name="custom_fix",
    description="Fix custom error",
    commands=[
        "echo 'Fixing...'",
        "npm rebuild",
        "rm -rf node_modules",
        "npm install",
    ],
)

engine.recovery_strategies["custom_fix"] = strategy
```

---

## 🔌 API Reference

### REST API Endpoints

Base URL: `http://localhost:8000`

#### Get Orchestrator Status

```http
GET /api/orchestrator/status

Response:
{
  "timestamp": "2025-12-19 10:30:00",
  "root": "/home/user/Projects",
  "total_projects": 15,
  "projects": { ... },
  "todos": { ... },
  "monitors": { ... }
}
```

#### Get All Projects

```http
GET /api/orchestrator/projects

Response:
{
  "project-1": {
    "path": "/path/to/project-1",
    "status": "healthy",
    "branch": "main",
    ...
  },
  ...
}
```

#### Get Specific Project

```http
GET /api/orchestrator/projects/{project_name}

Response:
{
  "path": "/path/to/project",
  "status": "healthy",
  "branch": "main",
  "has_ai_autofix": true,
  "has_tests": true,
  "todo_count": 5
}
```

#### Get TODO Statistics

```http
GET /api/orchestrator/todos

Response:
{
  "total": 42,
  "by_priority": {
    "critical": 3,
    "high": 8,
    "normal": 25,
    "low": 6
  },
  "completed": 15
}
```

#### Get Monitor Status

```http
GET /api/orchestrator/monitors

Response:
{
  "running": 10,
  "healthy": 8,
  "stopped": 2,
  "error": 0
}
```

#### Get Project Logs

```http
GET /api/orchestrator/logs/{project_name}?lines=100

Response:
{
  "project": "my-project",
  "total_lines": 5420,
  "returned_lines": 100,
  "logs": [...]
}
```

#### Spawn Codex Sessions

```http
POST /api/orchestrator/spawn-codex
Content-Type: application/json

{
  "priority": "high",
  "project": "my-project",
  "max_sessions": 1
}

Response:
{
  "success": true,
  "returncode": 0,
  "output": "...",
  "error": ""
}
```

#### Health Check

```http
GET /api/orchestrator/health

Response:
{
  "status": "healthy",
  "orchestrator_running": true,
  "timestamp": "2025-12-19 10:30:00",
  "total_projects": 15,
  "active_monitors": 12
}
```

---

## 💡 Best Practices

### 1. Project Structure

Ensure your projects have the recommended structure:

```
my-project/
├── .git/                      # Required for discovery
├── scripts/
│   └── ai_auto_fix.py         # Enables auto-fix
├── tests/                     # Enables test detection
├── REMAINING_TODOS.md         # TODO tracking
├── requirements.txt           # Python deps
└── package.json               # Node deps
```

### 2. TODO Management

**Write Clear TODOs:**
```markdown
❌ Bad:
- [ ] Fix stuff

✅ Good:
- [ ] CRITICAL: Fix authentication bug in login endpoint (auth.py:45)
- [ ] HIGH: Add input validation for user registration form
- [ ] TODO: Refactor database connection pooling for better performance
```

**Mark Completed Items:**
```markdown
- [x] ✅ Implemented user authentication
- [x] Added email verification
- [ ] Add password reset functionality
```

### 3. Monitoring

**Check Status Regularly:**
```bash
# Every morning
python scripts/interactive_shell.py
(all-projects) $ status
(all-projects) $ health

# Review logs for issues
(all-projects) $ use critical-project
(critical-project) $ logs --lines 200
```

**Set Up Alerts:**
```bash
# Add cron job to check health
*/5 * * * * curl -s http://localhost:8000/api/orchestrator/health | \
  jq -r 'if .status != "healthy" then "ALERT: Orchestrator unhealthy" else empty end' | \
  mail -s "Orchestrator Alert" admin@example.com
```

### 4. Resource Management

**Control Resource Usage:**
```bash
# Limit projects monitored
python os_dashboard_ai_assistant.py --max-repos 10

# Adjust check intervals
python os_dashboard_ai_assistant.py --todo-check-interval 600
```

### 5. Security

**Protect Sensitive Data:**
```bash
# Use .gitignore
echo "logs/" >> .gitignore
echo "*.log" >> .gitignore

# Secure API endpoints (in production)
# Configure authentication in backend_api/main.py
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Orchestrator Not Starting

**Symptoms:**
- Process exits immediately
- No status report generated

**Solutions:**
```bash
# Check for errors
python os_dashboard_ai_assistant.py 2>&1 | tee orchestrator.log

# Verify dependencies
pip install -r requirements.txt

# Check permissions
chmod +x os_dashboard_ai_assistant.py
```

#### 2. Projects Not Discovered

**Symptoms:**
- `total_projects: 0` in status
- No monitors launching

**Solutions:**
```bash
# Check workspace path
ls -la ~/Projects/*/.git

# Increase max depth
python os_dashboard_ai_assistant.py --max-depth 6

# Check for .git directories
find ~/Projects -name ".git" -type d
```

#### 3. Monitors Not Starting

**Symptoms:**
- Projects discovered but no monitors running
- Monitor count: 0

**Solutions:**
```bash
# Ensure ai_auto_fix.py exists
find ~/Projects -path "*/scripts/ai_auto_fix.py"

# Check if script is executable
chmod +x */scripts/ai_auto_fix.py

# Test manually
cd my-project
python scripts/ai_auto_fix.py --help
```

#### 4. High CPU/Memory Usage

**Symptoms:**
- System slowdown
- High resource consumption

**Solutions:**
```bash
# Reduce monitored projects
python os_dashboard_ai_assistant.py --max-repos 5

# Increase check intervals
python os_dashboard_ai_assistant.py --todo-check-interval 900

# Disable auto-codex
python os_dashboard_ai_assistant.py --no-auto-codex
```

#### 5. Web UI Not Showing Data

**Symptoms:**
- Dashboard shows "Not Running"
- 404 errors on API calls

**Solutions:**
```bash
# Ensure backend is running
curl http://localhost:8000/api/health

# Check status report exists
ls -la logs/status_report.json

# Restart orchestrator
# Kill existing: pkill -f os_dashboard_ai_assistant
python os_dashboard_ai_assistant.py
```

### Debug Mode

Enable verbose logging:

```python
# In os_dashboard_ai_assistant.py
logging.basicConfig(level=logging.DEBUG)

# Or set environment variable
export OSDASH_DEBUG=1
python os_dashboard_ai_assistant.py
```

---

## ⚙️ Advanced Configuration

### Environment Variables

```bash
# Enable orchestrator with UI
export OSDASH_ENABLE_ORCHESTRATOR=1

# Custom workspace root
export OSDASH_WORKSPACE_ROOT=~/MyProjects

# API configuration
export OSDASH_API_HOST=0.0.0.0
export OSDASH_API_PORT=8000

# OpenAI API key for AI features
export OPENAI_API_KEY=sk-...
```

### Configuration File

Create `orchestrator_config.yaml`:

```yaml
workspace:
  root: ~/Projects
  max_depth: 5
  exclude_dirs:
    - node_modules
    - .venv
    - dist

monitoring:
  todo_check_interval: 300
  health_check_interval: 60
  auto_spawn_codex: true

limits:
  max_repos: 20
  max_recovery_attempts: 3

logging:
  level: INFO
  directory: logs
  rotate: true
  max_size: 10MB
```

### Custom Integrations

#### Slack Notifications

```python
# Add to os_dashboard_ai_assistant.py

import requests

def send_slack_notification(message):
    webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
    if webhook_url:
        requests.post(webhook_url, json={"text": message})

# In MasterOrchestrator.start()
send_slack_notification("🚀 Master Orchestrator started")
```

#### Email Alerts

```python
# Add email alerts for critical issues

import smtplib
from email.mime.text import MIMEText

def send_email_alert(subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = "orchestrator@example.com"
    msg['To'] = "admin@example.com"
    
    s = smtplib.SMTP('localhost')
    s.send_message(msg)
    s.quit()
```

---

## 📚 Additional Resources

- **Technical Spec**: See `Technical Spec Sheet (Version 6 Latest Version).txt`
- **Architecture Blueprint**: See `OSD_ARCHITECTURE_BLUEPRINT.md`
- **API Documentation**: Visit `/swagger` endpoint
- **Example Scripts**: See `examples/` directory
- **Test Suite**: See `tests/` directory

---

## 🤝 Support

For issues, questions, or contributions:

1. Check existing documentation
2. Review troubleshooting section
3. Check logs in `logs/` directory
4. Open an issue with detailed information

---

## 📝 License

Copyright © 2025 OS Dashboard AI Assistant Project  
All Rights Reserved

---

**Last Updated**: December 19, 2025  
**Version**: 1.0.0  
**Maintainer**: Sir Chief Fellow Director Principal Software Solutions Systems Engineer Architect
