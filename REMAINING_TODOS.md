# Remaining TODOs — Guardian Grid Track

## 1. Automation Runtime
- [x] Teach `scripts/ai_auto_fix.py` to accept a `--project-root /path/to/repo` flag so one installation can service sibling repos discovered by the orchestrator.
- [x] Emit structured JSON/NDJSON snapshots from `project_autofix_orchestrator.py` (status per repo, timestamps, command line) that the React dashboard can ingest.
- [ ] Add regression tests (pytest) that stub subprocesses and verify orchestrator behavior for scan-only, dry-run, and graceful shutdown flows.

## 2. Experience Layer
- [x] Surface orchestrator + auto-fix health status within the React dashboard (banner + diagnostics drawer), consuming the structured log snapshots.
- [ ] Extend `run.py` / launcher prompts to optionally kick off `project_autofix_orchestrator.py --scan-only` before presenting UX mode choices.
- [x] Extend `run.py` / launcher prompts to optionally kick off `project_autofix_orchestrator.py --scan-only` before presenting UX mode choices.

## 3. Documentation & Ops
- [x] Add README section describing the orchestrator workflow, common flags, and integration expectations for sibling repos.
- [x] Define remediation playbooks for repos lacking `scripts/ai_auto_fix.py` so the automation grid eventually covers 100% of `.git` folders.
- [ ] Create CI job that runs orchestrator in scan-only mode to prevent unnoticed drift in workspace coverage.

## 4. Workspace Auto-Guard Expansion
- [x] Wire `scripts/workspace_auto_guard.py` JSON output into a FastAPI endpoint (`/workspace/health`) so remote agents and dashboards can query automation coverage.
- [x] Teach `run.py` to expose a "Workspace Guard" launch mode that chains the orchestrator + auto-guard before surfacing UX prompts.
- [ ] Support per-repo `.osdash-auto.json` manifests so teams can override detected test commands or provide opt-out justifications.
- [ ] Design frontend visualizations (tiles + filters) that highlight skipped repos, failing commands, and stale timestamps from the auto-guard report.

## 5. Unified Project Orchestrator System (NEW)
- [x] Create unified project orchestrator that discovers all .git repos and applies auto-fix scripts
- [x] Enhance frontend with seamless project management UI and real-time monitoring
- [x] Create backend APIs for project discovery, health monitoring, and auto-fix orchestration
- [x] Build unified terminal shell interface for interacting with all projects
- [x] Integrate AI-powered bug detection and auto-resolution across all projects
- [x] Add new features: project health dashboard, auto-remediation, cross-project analytics
- [x] Create comprehensive documentation and setup scripts
- [ ] Add project dependency graph visualization
- [ ] Implement cross-project test execution
- [ ] Add automated project onboarding workflow
- [ ] Integrate with CI/CD systems
- [ ] Add advanced analytics and reporting features
- [ ] Create project templates and scaffolding
- [ ] Support multi-workspace management
- [ ] Add cloud sync and collaboration features

## 6. Integration Enhancements
- [ ] Create unified launcher script that combines orchestrator + terminal shell + web UI
- [ ] Add project health alerts and notifications
- [ ] Implement project performance benchmarking
- [ ] Add project security scanning integration
- [ ] Create project onboarding wizard
- [ ] Add project templates library
- [ ] Implement project sharing and collaboration features

## 7. Advanced Features
- [ ] Cross-project dependency analysis
- [ ] Automated project migration tools
- [ ] Project health prediction using ML
- [ ] Automated code review integration
- [ ] Project performance optimization suggestions
- [ ] Cross-project code pattern detection
- [ ] Automated documentation generation
- [ ] Project compliance checking

## Next Steps for Codex Integration

When triggering a follow-up Codex session, pass this TODO file verbatim so the next assistant continues the execution chain. The unified system is now operational and ready for:

1. **Testing**: Run `python scripts/unified_project_orchestrator.py --auto-fix` to test discovery and auto-fix
2. **Web UI**: Access `/workspace/orchestrator` in the web interface
3. **Terminal Shell**: Run `python scripts/unified_terminal_shell.py` for interactive management
4. **API Integration**: Use REST endpoints for programmatic access

The system is designed to be:
- **Seamless**: Automatic discovery and integration
- **Simple**: Intuitive interfaces (CLI, Web, API)
- **Intuitive**: Clear commands and visual feedback
- **Efficient**: Optimized performance and resource usage
- **Reliable**: Robust error handling and recovery
- **Protected**: Security best practices throughout
- **Updatable**: Easy to extend and maintain
- **Reusable**: Modular components for all projects
