# Future TODOs & Opportunity Backlog

> **STATUS UPDATE (December 2025)**: Significant infrastructure completed! See notes below.

## ✅ Completed Items

### Auto-Fix & Multi-Repo Workflows
- [x] Created `scripts/unified_project_orchestrator.py` to enumerate all git repositories
- [x] Implemented `.osdash-auto.json` manifest system for per-repo configuration
- [x] Created `scripts/codex_continuation_daemon.py` for automatic handoff protocol
- [x] Built `WorkspaceHealthDashboard.tsx` for visualization

### Experience Layer
- [x] Created unified launcher `scripts/osdash_launcher.py` with multiple modes
- [x] Built workspace health API endpoints (`/api/workspace/*`)

---

## Diagnostics & Observability
- [ ] Persist `/api/runtime/diagnostics` events into SQLite (new `runtime_events` table) with rotation + retention policies.
- [ ] Build an internal dashboard under `/app/observability` to review diagnostics, filter by persona/plane, and trigger AI-assisted remediation.
- [ ] Extend the diagnostics SDK to Electron main/preload processes so crashes outside the renderer are also logged.
- [ ] Add distributed tracing integration (OpenTelemetry) for end-to-end request tracking.

## Plane & Capsule Roadmap
- [ ] Materialize plane metadata tables (data/control/governance) plus APIs to provision and monitor plane health.
- [ ] Promote capsule ledgering into the FastAPI routers so every automation step emits immutable hashes per Technical Spec §6.
- [ ] Rebuild the TRF/Project Intelligence panels in React using live ledger + capsule traces.
- [ ] Implement capsule versioning and rollback capabilities.

## UX & Frontend Enhancements
- [ ] Introduce offline/low-bandwidth modes with Suspense fallbacks for each primary route (Dashboard, Projects, AI Ops).
- [ ] Implement global notifications summarizing diagnostics + background AI fixes so users gain immediate context.
- [ ] Expand documentation hub with interactive blueprints derived from `docs/FUTURE_VERSION_1000_BLUEPRINT.md`.
- [ ] Add real-time WebSocket updates for WorkspaceHealthDashboard.
- [ ] Create interactive dependency graph visualization for multi-project workspaces.

## NEW: Intelligent Automation (Priority)
- [ ] Implement AI-powered test generation for uncovered code paths.
- [ ] Create predictive failure detection using historical patterns.
- [ ] Build automated code review suggestions integration.
- [ ] Add semantic TODO categorization using embeddings.

## NEW: Enterprise Features
- [ ] Multi-tenant workspace isolation for team collaboration.
- [ ] Role-based access control for sensitive operations.
- [ ] Audit log export for compliance requirements.
- [ ] SSO integration (OIDC/SAML) for enterprise deployments.

## NEW: Developer Experience
- [ ] VS Code extension for inline TODO management.
- [ ] GitHub/GitLab integration for issue synchronization.
- [ ] CLI tool for quick workspace health checks.
- [ ] Pre-commit hooks for automatic health verification.

---

## Continuation Protocol

To trigger a follow-up Codex/AI session, the system now uses `.osdash-continuation.json`:

1. Run: `python scripts/unified_project_orchestrator.py --root . --execute --continue-todos`
2. This generates `.osdash-continuation.json` with:
   - Priority TODOs requiring attention
   - Failed projects needing repair
   - Recommended actions
   - Context for next session
3. Run: `python scripts/codex_continuation_daemon.py --once`
4. Or use: `python scripts/osdash_launcher.py --mode daemon`

The continuation daemon can automatically:
- Generate prompts for manual AI invocation
- Open Cursor/VS Code with the prompt
- Launch a new terminal session
- Call AI APIs directly (if configured)

> When triggering a follow-up Codex session, the continuation payload is automatically read to continue the execution chain.
