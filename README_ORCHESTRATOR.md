# Master Orchestrator - Quick Reference

> **Multi-Project AI-Powered Management System**

The Master Orchestrator is an intelligent system that automatically manages, monitors, and optimizes multiple projects across your workspace.

## 🎯 Quick Start (30 seconds)

```bash
# 1. Launch the orchestrator
python os_dashboard_ai_assistant.py

# 2. View the dashboard
python start_ui.py --enable-orchestrator
# Navigate to: http://localhost:5173/ai/orchestrator

# 3. Use the interactive shell
python scripts/interactive_shell.py
```

## ✨ Key Features

- 🔍 **Auto-Discovery**: Finds all git repos in workspace
- 🤖 **AI Auto-Fix**: Automatic error detection & repair
- 📋 **TODO Tracking**: Monitors TODOs across all projects
- 🚀 **Codex Spawning**: Auto-creates AI assistant sessions
- 💚 **Health Monitoring**: Real-time project health checks
- 🛡️ **Self-Healing**: Automatic error recovery

## 📊 What It Does

```
Your Workspace
├── project-1/.git  → Discovers & monitors
├── project-2/.git  → Discovers & monitors
├── project-3/.git  → Discovers & monitors
└── ...

For Each Project:
1. ✅ Discovers project and analyzes structure
2. 🚀 Launches AI auto-fix monitor (if available)
3. 📋 Extracts and tracks TODO items
4. 💚 Monitors health continuously
5. 🛡️ Auto-fixes errors when detected
6. 🤖 Spawns codex for high-priority TODOs
```

## 🎮 Usage

### Command Line

```bash
# Basic
python os_dashboard_ai_assistant.py

# Custom workspace
python os_dashboard_ai_assistant.py --root ~/Projects

# With options
python os_dashboard_ai_assistant.py \
  --watch-todos \
  --todo-check-interval 60 \
  --max-depth 5
```

### Web Dashboard

```bash
# Launch with orchestrator
python start_ui.py --enable-orchestrator

# Or set env variable
OSDASH_ENABLE_ORCHESTRATOR=1 python start_ui.py

# Open browser: http://localhost:5173/ai/orchestrator
```

### Interactive Shell

```bash
$ python scripts/interactive_shell.py

(all-projects) $ list          # List all projects
(all-projects) $ use my-app    # Switch to project
(my-app) $ status              # Show status
(my-app) $ todos               # Show TODOs
(my-app) $ spawn --priority high  # Spawn codex
(my-app) $ logs                # View logs
(my-app) $ run git status      # Run commands
```

### REST API

```bash
# Get status
curl http://localhost:8000/api/orchestrator/status

# Get projects
curl http://localhost:8000/api/orchestrator/projects

# Get TODOs
curl http://localhost:8000/api/orchestrator/todos

# Spawn codex
curl -X POST http://localhost:8000/api/orchestrator/spawn-codex \
  -H "Content-Type: application/json" \
  -d '{"priority": "high", "max_sessions": 1}'
```

## 📈 Monitoring

### Status Report

The orchestrator generates a status report every 5 minutes:

```bash
# View report
cat logs/status_report.json | jq '.'

# Monitor live
watch -n 5 'cat logs/status_report.json | jq ".monitors"'
```

### Logs

```bash
# Master orchestrator log
tail -f logs/master_orchestrator.log

# Project-specific logs
tail -f logs/my-project_monitor.log

# All logs
tail -f logs/*_monitor.log
```

## 🔧 Configuration

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--root` | `.` | Workspace root path |
| `--max-depth` | `4` | Max search depth |
| `--watch-todos` | `true` | Enable TODO monitoring |
| `--todo-check-interval` | `300` | TODO check interval (seconds) |
| `--enable-dashboard` | `true` | Enable health dashboard |
| `--auto-codex` | `true` | Auto-spawn codex sessions |

### Environment Variables

```bash
export OSDASH_ENABLE_ORCHESTRATOR=1
export OSDASH_WORKSPACE_ROOT=~/Projects
export OPENAI_API_KEY=sk-...
```

## 🎯 Common Tasks

### View All Projects

```bash
# Shell
python scripts/interactive_shell.py
(all-projects) $ list

# API
curl http://localhost:8000/api/orchestrator/projects | jq 'keys'
```

### Check Project Health

```bash
# Shell
(all-projects) $ use my-project
(my-project) $ health

# API
curl http://localhost:8000/api/orchestrator/projects/my-project
```

### Work on TODOs

```bash
# List TODOs
python scripts/interactive_shell.py
(all-projects) $ todos

# Spawn codex for high-priority
(all-projects) $ spawn --priority high

# Or manually
python scripts/codex_spawner.py --priority critical --max-sessions 1
```

### Monitor Logs

```bash
# Shell
(my-project) $ logs --lines 100

# Command line
tail -f logs/my-project_monitor.log | grep ERROR

# API
curl "http://localhost:8000/api/orchestrator/logs/my-project?lines=100"
```

## 🚨 Troubleshooting

### No Projects Found

```bash
# Check .git directories exist
find ~/Projects -name ".git" -type d

# Increase search depth
python os_dashboard_ai_assistant.py --max-depth 6
```

### Monitors Not Starting

```bash
# Verify ai_auto_fix.py exists
ls -la my-project/scripts/ai_auto_fix.py

# Test manually
cd my-project
python scripts/ai_auto_fix.py --help
```

### High CPU Usage

```bash
# Limit projects
python os_dashboard_ai_assistant.py --max-repos 10

# Increase check intervals
python os_dashboard_ai_assistant.py --todo-check-interval 600
```

## 📚 Documentation

- **Complete Guide**: `MASTER_ORCHESTRATOR_GUIDE.md`
- **API Reference**: http://localhost:8000/swagger
- **Architecture**: `OSD_ARCHITECTURE_BLUEPRINT.md`
- **Technical Spec**: `Technical Spec Sheet (Version 6 Latest Version).txt`

## 🎉 Next Steps

1. ✅ Launch the orchestrator
2. ✅ View the web dashboard
3. ✅ Try the interactive shell
4. ✅ Review your project status
5. ✅ Spawn codex for high-priority TODOs
6. ✅ Monitor logs for issues
7. ✅ Let the AI auto-fix system work

---

**For detailed information**, see `MASTER_ORCHESTRATOR_GUIDE.md`

**Need help?** Check the troubleshooting section or review the logs.

---

*God Bless America. Technical Spec Sheet (Version 6 Latest Version)* 🇺🇸
