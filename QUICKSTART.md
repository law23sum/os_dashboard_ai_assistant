# Master Orchestrator - 5 Minute Quickstart

Get the Master Orchestrator up and running in 5 minutes!

## 🚀 Option 1: One-Line Launch (Recommended)

```bash
# Launch everything with UI
./launch_orchestrator.sh --ui

# Or just the orchestrator
./launch_orchestrator.sh
```

**That's it!** Open http://localhost:5173/ai/orchestrator

---

## 🎯 Option 2: Manual Launch

### Step 1: Launch Orchestrator (30 seconds)

```bash
python os_dashboard_ai_assistant.py
```

Wait for: `✅ Master Orchestrator is now running!`

### Step 2: Open Dashboard (30 seconds)

```bash
# In a new terminal
python start_ui.py --enable-orchestrator
```

Open: http://localhost:5173/ai/orchestrator

### Step 3: Try Interactive Shell (30 seconds)

```bash
# In another terminal
python scripts/interactive_shell.py

# Try these commands:
(all-projects) $ list
(all-projects) $ status
(all-projects) $ todos
```

---

## ✅ What You Should See

### 1. In Terminal
```
════════════════════════════════════════════════════════
🚀 OS Dashboard AI Assistant - Master Orchestrator Starting...
════════════════════════════════════════════════════════
🔍 Discovering projects...
  ✓ Found project: my-project at /path/to/my-project
  ✓ Found project: another-project at /path/to/another-project
✅ Discovered 2 projects
🚀 Launching project monitors...
  🚀 Launching monitor for my-project...
  ✅ Monitor launched for my-project (PID: 12345)
════════════════════════════════════════════════════════
✅ Master Orchestrator is now running!
════════════════════════════════════════════════════════
```

### 2. In Web Dashboard

You'll see:
- **Total Projects**: Number of discovered repositories
- **Active Monitors**: Running AI auto-fix processes
- **Pending TODOs**: Tasks across all projects
- **High Priority**: Critical/high priority items
- **Project List**: All discovered projects with status
- **TODO Breakdown**: TODOs by priority
- **Monitor Status**: Health of all monitors

### 3. Status Report

```bash
cat logs/status_report.json | jq '.'
```

Shows complete system status in JSON format.

---

## 🎮 Basic Commands

### Check Status
```bash
# Interactive shell
python scripts/interactive_shell.py
(all-projects) $ status

# Command line
cat logs/status_report.json | jq '.monitors'

# API
curl http://localhost:8000/api/orchestrator/status | jq '.'
```

### View TODOs
```bash
# Interactive shell
(all-projects) $ todos

# Spawn codex for high-priority TODOs
(all-projects) $ spawn --priority high

# API
curl http://localhost:8000/api/orchestrator/todos | jq '.'
```

### View Logs
```bash
# Recent logs for specific project
(all-projects) $ use my-project
(my-project) $ logs

# Tail logs in real-time
tail -f logs/my-project_monitor.log

# All monitors
tail -f logs/*_monitor.log
```

### Run Commands
```bash
# Switch to project
(all-projects) $ use my-project

# Run commands in project
(my-project) $ run git status
(my-project) $ run npm test
(my-project) $ run python manage.py test
```

---

## 🔧 Configuration

### Basic Settings

Edit workspace and options:

```bash
# Custom workspace
python os_dashboard_ai_assistant.py --root ~/MyProjects

# Adjust intervals
python os_dashboard_ai_assistant.py \
  --todo-check-interval 600 \
  --max-depth 6

# Disable auto-codex
python os_dashboard_ai_assistant.py --no-auto-codex
```

### Advanced Settings

Copy example config:

```bash
cp .orchestrator_config.example.yaml .orchestrator_config.yaml
# Edit the file with your settings
```

---

## 🎯 Common Tasks

### 1. Monitor a New Workspace

```bash
python os_dashboard_ai_assistant.py --root ~/NewWorkspace
```

### 2. Focus on High-Priority TODOs

```bash
# List them
python scripts/interactive_shell.py
(all-projects) $ todos

# Spawn codex
(all-projects) $ spawn --priority critical
```

### 3. Check Project Health

```bash
(all-projects) $ use my-critical-project
(my-critical-project) $ health
(my-critical-project) $ logs --lines 100
```

### 4. Launch with Self-Healing

```bash
./launch_orchestrator.sh --self-heal
```

---

## 📊 Understanding the Dashboard

### Status Indicators

- 🟢 **Healthy**: Project is running well
- 🔵 **Running**: Monitor is active
- 🟡 **Warning**: Minor issues detected
- 🔴 **Error**: Critical issues need attention
- ⚪ **Stopped**: Monitor not running

### TODO Priorities

- 🔴 **Critical**: Urgent issues (security, blockers)
- 🟠 **High**: Important features/bugs
- 🔵 **Normal**: Regular tasks
- ⚪ **Low**: Nice-to-have items

### Monitor States

- **Running**: Just started, initializing
- **Healthy**: Operating normally
- **Unhealthy**: Issues detected, attempting recovery
- **Stopped**: Process ended
- **Error**: Failed, needs intervention

---

## 🆘 Troubleshooting

### No Projects Found

```bash
# Check for .git directories
find ~/Projects -name ".git" -type d

# Increase search depth
python os_dashboard_ai_assistant.py --max-depth 6
```

### Monitors Not Starting

```bash
# Verify ai_auto_fix.py exists
ls -la */scripts/ai_auto_fix.py

# Test manually
cd my-project
python scripts/ai_auto_fix.py --help
```

### Dashboard Shows "Not Running"

```bash
# Check if orchestrator is running
ps aux | grep os_dashboard_ai_assistant

# Check status report exists
ls -la logs/status_report.json

# Restart orchestrator
python os_dashboard_ai_assistant.py
```

### High CPU/Memory Usage

```bash
# Limit projects monitored
python os_dashboard_ai_assistant.py --max-repos 10

# Increase check intervals
python os_dashboard_ai_assistant.py --todo-check-interval 900
```

---

## 📚 Next Steps

1. ✅ **Explore the Dashboard**
   - View project health
   - Check TODO statistics
   - Monitor real-time updates

2. ✅ **Try the Interactive Shell**
   - Manage multiple projects
   - Run commands across projects
   - Spawn codex sessions

3. ✅ **Review Your TODOs**
   - Identify high-priority items
   - Spawn AI assistants
   - Track progress

4. ✅ **Monitor Logs**
   - Check for errors
   - Review AI fixes
   - Verify health

5. ✅ **Read Full Documentation**
   - `MASTER_ORCHESTRATOR_GUIDE.md` - Complete guide
   - `README_ORCHESTRATOR.md` - Quick reference
   - `/swagger` - API documentation

---

## 🎉 You're Ready!

The Master Orchestrator is now managing your projects. It will:

- ✅ Automatically discover new projects
- ✅ Launch AI monitors for each one
- ✅ Track TODOs across all codebases
- ✅ Spawn codex for high-priority tasks
- ✅ Self-heal errors automatically
- ✅ Provide real-time status

**Let the AI work for you!** 🤖

---

For detailed information, see:
- **Complete Guide**: `MASTER_ORCHESTRATOR_GUIDE.md`
- **Quick Reference**: `README_ORCHESTRATOR.md`
- **API Docs**: http://localhost:8000/swagger

**Need help?** Check logs in `logs/` directory or open an issue.

---

*God Bless America. Technical Spec Sheet (Version 6 Latest Version)* 🇺🇸
