# Unified Project Orchestrator System

## Overview

The Unified Project Orchestrator System provides seamless, intuitive management and monitoring for all Git projects in your workspace. It automatically discovers all Git repositories, applies AI OS auto-fix scripts, monitors health, and provides unified interfaces for interacting with all projects.

## Architecture

### Core Components

1. **Unified Project Orchestrator** (`scripts/unified_project_orchestrator.py`)
   - Discovers all Git repositories in the workspace
   - Manages auto-fix monitors for each project
   - Provides health monitoring and reporting
   - Integrates with backend API

2. **Unified Terminal Shell** (`scripts/unified_terminal_shell.py`)
   - Interactive command-line interface
   - Unified commands for all projects
   - Real-time project status
   - Cross-project operations

3. **Backend API Router** (`backend_api/routers/project_orchestrator.py`)
   - REST API endpoints for project discovery
   - Health monitoring APIs
   - Auto-fix management endpoints
   - Cross-project analytics

4. **Frontend UI** (`frontend/src/pages/ProjectOrchestrator.tsx`)
   - Visual project dashboard
   - Real-time health monitoring
   - Project management interface
   - Analytics and reporting

## Features

### Automatic Project Discovery
- Scans workspace for all `.git` directories
- Detects project capabilities (auto-fix, tests, language)
- Builds comprehensive project inventory

### Auto-Fix Integration
- Automatically applies `ai_auto_fix.py` to eligible projects
- Monitors logs and detects errors
- Auto-resolves bugs using AI/codex
- Tracks fix history and success rates

### Health Monitoring
- Real-time health status for all projects
- Categorizes projects as healthy, degraded, unhealthy, or unknown
- Periodic health checks with configurable intervals
- Health event tracking and alerting

### Unified Interfaces
- **Terminal Shell**: Interactive CLI for all projects
- **Web Dashboard**: Visual interface with real-time updates
- **REST API**: Programmatic access for integrations

### Cross-Project Analytics
- Health score calculation
- Auto-fix coverage metrics
- Test coverage statistics
- Project language distribution

## Usage

### Command Line

#### Unified Project Orchestrator

```bash
# Discover all projects
python scripts/unified_project_orchestrator.py

# Scan specific workspace
python scripts/unified_project_orchestrator.py --root ~/Projects

# Enable auto-fix monitors
python scripts/unified_project_orchestrator.py --auto-fix

# Daemon mode with continuous monitoring
python scripts/unified_project_orchestrator.py --daemon --auto-fix

# Generate JSON report
python scripts/unified_project_orchestrator.py --output report.json
```

#### Unified Terminal Shell

```bash
# Start interactive shell
python scripts/unified_terminal_shell.py

# Available commands:
#   list              - List all discovered projects
#   status            - Show health status
#   monitor <name>    - Start auto-fix monitor
#   stop <name>       - Stop auto-fix monitor
#   test <name>       - Run tests for a project
#   fix <name>        - Trigger manual auto-fix
#   report [file]     - Generate report
#   refresh           - Refresh project list
#   help              - Show help
#   exit/quit         - Exit shell
```

### Web Interface

Access the Project Orchestrator dashboard at:
- `/workspace/orchestrator` or `/projects/orchestrator`

Features:
- Visual project list with health indicators
- Real-time status updates
- Start/stop auto-fix monitors
- Analytics summary
- Health score visualization

### REST API

#### Discover Projects
```bash
GET /api/projects/discover?root=/path/to/workspace&max_depth=5
```

#### Get Project Report
```bash
GET /api/projects/report?root=/path/to/workspace&max_depth=5
```

#### Get Project Health
```bash
GET /api/projects/{project_name}/health
```

#### Start Auto-Fix Monitor
```bash
POST /api/projects/{project_name}/autofix/start
```

#### Stop Auto-Fix Monitor
```bash
POST /api/projects/{project_name}/autofix/stop
```

#### Get Analytics Summary
```bash
GET /api/projects/analytics/summary
```

## Setup

### Quick Setup

```bash
# Run setup script
./scripts/setup_unified_system.sh
```

This will:
- Make all scripts executable
- Check Python dependencies
- Create symlinks for easy access
- Test project discovery

### Manual Setup

1. **Make scripts executable:**
   ```bash
   chmod +x scripts/unified_project_orchestrator.py
   chmod +x scripts/unified_terminal_shell.py
   ```

2. **Install dependencies:**
   ```bash
   pip install -r backend_api/requirements.txt
   ```

3. **Create symlinks (optional):**
   ```bash
   mkdir -p ~/.local/bin
   ln -s $(pwd)/scripts/unified_project_orchestrator.py ~/.local/bin/osdash-orchestrator
   ln -s $(pwd)/scripts/unified_terminal_shell.py ~/.local/bin/osdash-shell
   ```

## Integration with Existing Scripts

The Unified Project Orchestrator integrates seamlessly with existing AI OS scripts:

- **`ai_auto_fix.py`**: Auto-applied to all eligible projects
- **`project_autofix_orchestrator.py`**: Enhanced with unified discovery
- **`workspace_auto_guard.py`**: Integrated health monitoring
- **`workspace_autofix_shell.py`**: Unified terminal interface

## Configuration

### Environment Variables

- `OSDASH_WORKSPACE_ROOT`: Default workspace root (defaults to repo root)
- `OSDASH_MAX_DEPTH`: Maximum directory depth for discovery (default: 5)
- `OSDASH_HEALTH_INTERVAL`: Health check interval in seconds (default: 60)

### Project-Specific Configuration

Projects can provide `.osdash-config.json` in their root directory:

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
  },
  "health": {
    "check_interval": 60,
    "log_dirs": ["logs", "frontend/logs"]
  }
}
```

## Best Practices

1. **Regular Health Checks**: Run orchestrator in daemon mode for continuous monitoring
2. **Auto-Fix Coverage**: Ensure all projects have `ai_auto_fix.py` for self-healing
3. **Test Infrastructure**: Maintain test suites for all projects
4. **Health Monitoring**: Review health reports regularly
5. **Cross-Project Analytics**: Use analytics to identify patterns and improvements

## Troubleshooting

### Projects Not Discovered

- Check that `.git` directory exists in project root
- Verify `--max-depth` is sufficient
- Ensure directory permissions allow scanning

### Auto-Fix Not Starting

- Verify `scripts/ai_auto_fix.py` exists in project
- Check Python dependencies are installed
- Review project logs for errors

### Health Status Unknown

- Ensure log directories exist
- Check log file permissions
- Verify health check interval is appropriate

## Future Enhancements

- [ ] Project dependency graph visualization
- [ ] Cross-project test execution
- [ ] Automated project onboarding
- [ ] Integration with CI/CD systems
- [ ] Advanced analytics and reporting
- [ ] Project templates and scaffolding
- [ ] Multi-workspace support
- [ ] Cloud sync and collaboration

## Technical Spec Compliance

This system implements requirements from the Technical Spec Sheet (Version 6):

- **Section 7.3**: Dev & DevOps Workspace integration
- **Section 8.13**: Auto-Remediation Playbooks
- **Section 11.8**: Health Checks and Self-Healing
- **Section 17.2.2**: Dev Productivity Envelope

## Support

For issues, questions, or contributions:
- Review existing scripts in `scripts/` directory
- Check Technical Spec Sheet for architectural guidance
- Review TODO files for planned enhancements
