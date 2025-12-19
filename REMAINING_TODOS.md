# Remaining TODOs — Guardian Grid Track

> **STATUS UPDATE (December 2025)**: Major infrastructure implemented! See completed items below.

## ✅ Completed (Guardian Grid Phase 1)

### Automation Runtime
- [x] Created `scripts/unified_project_orchestrator.py` - Master orchestrator discovering all git projects with TODO extraction
- [x] Created `scripts/codex_continuation_daemon.py` - Automatic TODO handoff between AI sessions
- [x] Implemented structured JSON reporting for dashboard consumption
- [x] Added `.osdash-auto.json` manifest support for per-project configuration

### Experience Layer  
- [x] Created `WorkspaceHealthDashboard.tsx` - React component for workspace visualization
- [x] Created `/api/workspace/health` endpoints for health monitoring
- [x] Created `scripts/osdash_launcher.py` - Unified launcher with mode selection

### Workspace Auto-Guard
- [x] Wired workspace health into FastAPI (`/api/workspace/health`, `/api/workspace/todos`, `/api/workspace/metrics`)
- [x] Support for `.osdash-auto.json` manifests per repository
- [x] Continuation payload system for AI session handoff

---

## 1. Automation Runtime (Remaining)
- [ ] Teach `scripts/ai_auto_fix.py` to accept a `--project-root /path/to/repo` flag so one installation can service sibling repos discovered by the orchestrator.
- [ ] Add regression tests (pytest) that stub subprocesses and verify orchestrator behavior for scan-only, dry-run, and graceful shutdown flows.
- [ ] Implement automatic AI model selection based on task complexity in the continuation daemon.

## 2. Experience Layer (Remaining)
- [ ] Add real-time WebSocket updates to WorkspaceHealthDashboard for live monitoring.
- [ ] Implement notification system for critical health alerts.
- [ ] Add visual timeline of auto-fix runs and their outcomes.

## 3. Documentation & Ops
- [ ] Add README section describing the orchestrator workflow, common flags, and integration expectations for sibling repos.
- [ ] Define remediation playbooks for repos lacking `scripts/ai_auto_fix.py` so the automation grid eventually covers 100% of `.git` folders.
- [ ] Create CI job that runs orchestrator in scan-only mode to prevent unnoticed drift in workspace coverage.
- [ ] Document the continuation handoff protocol for cross-session TODO management.

## 4. Workspace Auto-Guard Expansion
- [ ] Design frontend visualizations (tiles + filters) that highlight skipped repos, failing commands, and stale timestamps from the auto-guard report.
- [ ] Implement scheduled background scans with configurable intervals.
- [ ] Add integration with GitHub Actions for PR-triggered health checks.

## 5. NEW: Multi-Workspace Federation
- [ ] Support scanning multiple workspace roots simultaneously.
- [ ] Implement cross-workspace TODO aggregation and prioritization.
- [ ] Create workspace groups for organization-level health monitoring.

## 6. NEW: Intelligent Auto-Remediation
- [ ] Train models on historical fix patterns for predictive remediation.
- [ ] Implement rollback capabilities when auto-fixes cause regressions.
- [ ] Add confidence scoring for AI-generated patches before auto-application.
