# Feature Change Log — OS Dashboard AI Assistant

## 2025-12-11 · Vision Release v1000.0
- **Added**: Multi-surface auto-healing regime that keeps the `ai_auto_fix` monitor alive even when optional AI dependencies are absent, ensuring self-heal telemetry never halts during missing-package scenarios.
- **Added**: `scripts/project_autofix_orchestrator.py` blueprint (see architecture log) to fan out repo-wide self-repair bootstrapping for every tracked workspace git checkout.
- **Added**: Unified future-state UX charter describing seamless transitions between browser, desktop, and legacy shells with adaptive onboarding.
- **Modified**: Auto-fix telemetry messaging clarifies when AI suggestions are degraded, preventing silent failures in developer sessions.
- **Modified**: Operating procedures now require cross-surface smoke tests before `start_ui.py` prompt completes, codified in the Blueprint doc.
- **Removed**: Manual expectation that developers babysit per-repo bug triage; automation now detects dependent repos automatically via the orchestrator.

Future entries must append (never overwrite) this log to preserve the decision trail.

## 2025-12-12 · Horizon Release v1000.1
- **Added**: `scripts/workspace_autofix_shell.py`, an interactive pane that scans sibling git checkouts, launches their tests (pytest, npm, or `run_tests_with_autofix.py`), and automatically escalates failures to `ai_auto_fix.py`.
- **Added**: README guidance for the workspace shell so operators can wire the terminal workflow into launch daemons, CI, or kiosk consoles without spelunking source files.
- **Modified**: Auto-fix rollouts now emit structured logs under `logs/workspace_shell/`, giving the blueprint’s telemetry feed a normalized place to scrape evidence of healing attempts.
- **Modified**: Architecture blueprint + TODO ledger highlight how the workspace shell, orchestrator, and UI should converge so every surface advertises its automation health status.
- **Future**: Backpack tasks (see TODO log) cover wiring the React UI banner + backend health API so the automation posture shows up visually, not just in terminals.

## 2025-12-11 · Guardian Grid Patch v1000.1
- **Added**: Implemented `scripts/project_autofix_orchestrator.py`, a workspace scanner that auto-detects `.git` roots, launches their `ai_auto_fix` monitors in parallel/sequential modes, and streams health to `logs/autofix_orchestrator.log`.
- **Added**: CLI affordances for include/exclude filters, depth limits, dry-run + scan modes, environment overrides, and graceful signal handling so the orchestrator can live alongside other launchers.
- **Modified**: Automation runbooks now mandate orchestrator scans before large launches; repos missing `scripts/ai_auto_fix.py` are cataloged for remediation instead of blocking the grid.

## 2025-12-12 · Workspace Guardian v1000.1
- **Added**: `scripts/workspace_auto_guard.py` for full-workspace discovery of `.git` projects plus auto-detected smoke-test hooks (ai_auto_fix, regression suite, pytest, npm test) with optional fallback orchestration.
- **Added**: README coverage documenting how `project_autofix_orchestrator.py` (daemons) + `workspace_auto_guard.py` (test planners) combine for complete automation fences.
- **Modified**: System Architecture Blueprint gains dual-layer automation notes and JSON health-feed requirements so the React dashboard can surface multi-repo readiness in future builds.
- **Added**: Workspace TODO ledger + action plan (see `OS_Dashboard_AI_Assistant/REMAINING_TODOS.md`) feeding the next Codex invocation without re-triage overhead.
