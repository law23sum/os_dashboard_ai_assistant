# AI OS - Scripts Directory

This directory contains all automation scripts for the AI OS system.

## 🎯 Core Scripts

### Unified Project Management

- **`unified_project_orchestrator.py`** - Master orchestrator for all Git projects
  - Discovers all Git repositories
  - Manages auto-fix monitors
  - Provides health monitoring
  - Generates comprehensive reports

- **`unified_terminal_shell.py`** - Interactive terminal interface
  - Unified commands for all projects
  - Real-time status updates
  - Cross-project operations

- **`unified_launcher.py`** - Single entry point launcher
  - Launches backend, frontend, orchestrator
  - Unified startup for all components

### Auto-Fix & Monitoring

- **`ai_auto_fix.py`** - AI-powered auto-fix script
  - Monitors logs for errors
  - Automatically fixes bugs using AI
  - Supports multiple projects

- **`project_autofix_orchestrator.py`** - Multi-project auto-fix orchestrator
  - Fans out auto-fix monitors across repos
  - Parallel/sequential execution modes

- **`workspace_auto_guard.py`** - Workspace health guard
  - Scans workspace for Git projects
  - Detects automation capabilities
  - Executes test suites

- **`workspace_autofix_shell.py`** - Interactive workspace shell
  - Project selection interface
  - Test execution with auto-fix fallback

### Enhanced Scripts

- **`enhance_ai_autofix.py`** - Cross-project auto-fix wrapper
  - Works with `--project-root` parameter
  - Fallback mode for projects without own script

### Setup & Testing

- **`setup_unified_system.sh`** - One-time setup script
  - Makes scripts executable
  - Creates symlinks
  - Checks dependencies

- **`test_unified_system.py`** - Comprehensive test suite
  - Tests all components
  - Verifies integration
  - Reports test results

## 📖 Usage Examples

### Basic Discovery

```bash
# Discover all projects
python scripts/unified_project_orchestrator.py

# Scan specific workspace
python scripts/unified_project_orchestrator.py --root ~/Projects
```

### Auto-Fix Management

```bash
# Start auto-fix monitors
python scripts/unified_project_orchestrator.py --auto-fix --daemon

# Stop monitors
# (Ctrl+C or kill process)
```

### Interactive Shell

```bash
# Start shell
python scripts/unified_terminal_shell.py

# Commands:
#   list          - List projects
#   status        - Health status
#   monitor <name> - Start monitor
#   test <name>   - Run tests
#   fix <name>    - Trigger fix
#   report        - Generate report
```

### Unified Launcher

```bash
# Launch everything
python scripts/unified_launcher.py all

# Launch web interface
python scripts/unified_launcher.py web

# Launch orchestrator only
python scripts/unified_launcher.py orchestrator
```

## 🔗 Integration

All scripts integrate with:

- **Backend API**: `backend_api/routers/project_orchestrator.py`
- **Frontend UI**: `frontend/src/pages/ProjectOrchestrator.tsx`
- **Existing Scripts**: Works with `ai_auto_fix.py`, `workspace_auto_guard.py`, etc.

## 📚 Documentation

- **Quick Start**: `../QUICK_START.md`
- **Full Documentation**: `../docs/UNIFIED_PROJECT_SYSTEM.md`
- **Implementation Summary**: `../IMPLEMENTATION_SUMMARY.md`

## 🛠️ Development

### Adding New Scripts

1. Place script in `scripts/` directory
2. Make executable: `chmod +x scripts/new_script.py`
3. Add shebang: `#!/usr/bin/env python3`
4. Document in this README
5. Add to `setup_unified_system.sh` if needed

### Testing

```bash
# Run test suite
python scripts/test_unified_system.py

# Test specific component
python scripts/unified_project_orchestrator.py --scan-only
```

## 📋 Script Dependencies

### Required
- Python 3.8+
- Git (for project discovery)

### Optional
- FastAPI (for backend integration)
- Node.js/npm (for frontend)
- OpenAI API key (for AI auto-fix)

## 🎯 Best Practices

1. **Use Executable Scripts**: All scripts should be executable
2. **Documentation**: Include docstrings and usage examples
3. **Error Handling**: Graceful error handling and recovery
4. **Logging**: Use structured logging for debugging
5. **Testing**: Test scripts before committing

## 🆘 Troubleshooting

### Script Not Executable

```bash
chmod +x scripts/script_name.py
```

### Import Errors

```bash
# Ensure REPO_ROOT is in Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Permission Errors

```bash
# Check file permissions
ls -l scripts/

# Fix if needed
chmod 755 scripts/*.py
```

## 📞 Support

For issues or questions:
- Check documentation in `../docs/`
- Review Technical Spec Sheet (Version 6)
- Check `../REMAINING_TODOS.md` for known issues
