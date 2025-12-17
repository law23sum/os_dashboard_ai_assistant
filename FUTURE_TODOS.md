# Future TODOs & Opportunity Backlog

## Diagnostics & Observability
- [ ] Persist `/api/runtime/diagnostics` events into SQLite (new `runtime_events` table) with rotation + retention policies.
- [ ] Build an internal dashboard under `/app/observability` to review diagnostics, filter by persona/plane, and trigger AI-assisted remediation.
- [ ] Extend the diagnostics SDK to Electron main/preload processes so crashes outside the renderer are also logged.

## Plane & Capsule Roadmap
- [ ] Materialize plane metadata tables (data/control/governance) plus APIs to provision and monitor plane health.
- [ ] Promote capsule ledgering into the FastAPI routers so every automation step emits immutable hashes per Technical Spec §6.
- [ ] Rebuild the TRF/Project Intelligence panels in React using live ledger + capsule traces.

## Auto-Fix & Multi-Repo Workflows
- [ ] Teach `scripts/ai_auto_fix.py` to enumerate sibling git repositories (via `~/Projects/*/.git`) and run repo-specific test suites before invoking AI repair.
- [ ] Provide a manifest file mapping each repo to its launch/test commands so the orchestrator scales beyond this project.
- [ ] Document a “handoff protocol” so future Codex runs can read this TODO file, spawn a new shell, and seed the next assistant invocation automatically.

## UX & Frontend Enhancements
- [ ] Introduce offline/low-bandwidth modes with Suspense fallbacks for each primary route (Dashboard, Projects, AI Ops).
- [ ] Implement global notifications summarizing diagnostics + background AI fixes so users gain immediate context.
- [ ] Expand documentation hub with interactive blueprints derived from `docs/FUTURE_VERSION_1000_BLUEPRINT.md`.

> When triggering a follow-up Codex session, pass this TODO file verbatim so the next assistant continues the execution chain (per the user’s AI-auto-fix directive).
