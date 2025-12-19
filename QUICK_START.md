# Quick Start Guide - Unified Project Orchestrator System

## 🚀 Get Started in 3 Steps

### Step 1: Setup (One-Time)

```bash
# Make scripts executable and setup symlinks
./scripts/setup_unified_system.sh

# Or manually:
chmod +x scripts/*.py
```

### Step 2: Discover Your Projects

```bash
# Discover all Git projects in your workspace
python scripts/unified_project_orchestrator.py

# Or use the unified launcher
python scripts/unified_launcher.py orchestrator
```

### Step 3: Choose Your Interface

#### Option A: Web Dashboard (Recommended)
```bash
# Start backend + frontend
python scripts/unified_launcher.py web

# Then navigate to: http://localhost:5173/workspace/orchestrator
```

#### Option B: Terminal Shell
```bash
# Interactive command-line interface
python scripts/unified_terminal_shell.py

# Available commands:
#   list          - List all projects
#   status        - Show health status
#   monitor <name> - Start auto-fix monitor
#   test <name>   - Run tests
#   fix <name>    - Trigger auto-fix
#   report        - Generate report
```

#### Option C: REST API
```bash
# Start backend
python scripts/unified_launcher.py web --no-frontend

# Use API endpoints:
curl http://localhost:8000/api/projects/discover
curl http://localhost:8000/api/projects/report
curl http://localhost:8000/api/projects/analytics/summary
```

## 📋 Common Tasks

### Enable Auto-Fix for All Projects

```bash
# Start orchestrator with auto-fix enabled
python scripts/unified_project_orchestrator.py --auto-fix --daemon
```

### Check Project Health

```bash
# Quick health check
python scripts/unified_project_orchestrator.py --output health.json

# View in terminal shell
python scripts/unified_terminal_shell.py
> status
```

### Run Tests for a Project

```bash
# Via terminal shell
python scripts/unified_terminal_shell.py
> test myproject

# Or directly
cd /path/to/project
pytest -q  # or npm test
```

### Generate Comprehensive Report

```bash
# JSON report
python scripts/unified_project_orchestrator.py --output report.json

# Via terminal shell
python scripts/unified_terminal_shell.py
> report report.json
```

## 🎯 Use Cases

### Daily Development Workflow

1. **Morning**: Check project health
   ```bash
   python scripts/unified_terminal_shell.py
   > status
   ```

2. **During Work**: Auto-fix monitors run in background
   ```bash
   python scripts/unified_project_orchestrator.py --auto-fix --daemon
   ```

3. **End of Day**: Review fixes and generate report
   ```bash
   python scripts/unified_terminal_shell.py
   > report daily-report.json
   ```

### Project Onboarding

1. **Discover**: Find all projects
   ```bash
   python scripts/unified_project_orchestrator.py --scan-only
   ```

2. **Setup**: Add auto-fix scripts to projects missing them
   ```bash
   # Copy ai_auto_fix.py to project
   cp scripts/ai_auto_fix.py /path/to/project/scripts/
   ```

3. **Monitor**: Start monitoring
   ```bash
   python scripts/unified_project_orchestrator.py --auto-fix --daemon
   ```

### CI/CD Integration

```bash
# In your CI pipeline
python scripts/unified_project_orchestrator.py --output ci-report.json

# Check health score
HEALTH_SCORE=$(python -c "import json; print(json.load(open('ci-report.json'))['summary']['healthy'])")
if [ "$HEALTH_SCORE" -lt 80 ]; then
    echo "Health score below threshold"
    exit 1
fi
```

## 🔧 Configuration

### Environment Variables

```bash
export OSDASH_WORKSPACE_ROOT=~/Projects
export OSDASH_MAX_DEPTH=5
export OSDASH_HEALTH_INTERVAL=60
```

### Project-Specific Config

Create `.osdash-config.json` in project root:

```json
{
  "autofix": {
    "enabled": true,
    "script": "scripts/ai_auto_fix.py",
    "args": ["--logs-only", "--daemon"]
  },
  "tests": {
    "command": ["pytest", "-q"],
    "enabled": true
  }
}
```

## 🆘 Troubleshooting

### Projects Not Discovered

```bash
# Increase search depth
python scripts/unified_project_orchestrator.py --max-depth 10

# Check specific directory
python scripts/unified_project_orchestrator.py --root /path/to/workspace
```

### Auto-Fix Not Starting

```bash
# Check if script exists
ls scripts/ai_auto_fix.py

# Test manually
python scripts/ai_auto_fix.py --logs-only --no-daemon
```

### Health Status Unknown

```bash
# Check log directories exist
ls logs/ frontend/logs/

# Run health check manually
python scripts/unified_project_orchestrator.py
```

## 📚 Next Steps

- Read full documentation: `docs/UNIFIED_PROJECT_SYSTEM.md`
- View implementation details: `IMPLEMENTATION_SUMMARY.md`
- Check remaining TODOs: `REMAINING_TODOS.md`

## 💡 Pro Tips

1. **Use Daemon Mode**: Keep orchestrator running for continuous monitoring
2. **Regular Reports**: Generate reports weekly for trend analysis
3. **Health Alerts**: Set up monitoring for health score thresholds
4. **Cross-Project**: Use analytics to identify patterns across projects
5. **Automation**: Integrate with your existing CI/CD pipelines

## 🎉 You're Ready!

The unified system is now operational. Start with the web dashboard for the best experience, or use the terminal shell for quick operations.

**Happy coding!** 🚀
