# Remaining TODOs — Guardian Grid Track

## 1. Automation Runtime
- [ ] Teach `scripts/ai_auto_fix.py` to accept a `--project-root /path/to/repo` flag so one installation can service sibling repos discovered by the orchestrator.
- [ ] Emit structured JSON/NDJSON snapshots from `project_autofix_orchestrator.py` (status per repo, timestamps, command line) that the React dashboard can ingest.
- [ ] Add regression tests (pytest) that stub subprocesses and verify orchestrator behavior for scan-only, dry-run, and graceful shutdown flows.

## 2. Experience Layer
- [ ] Surface orchestrator + auto-fix health status within the React dashboard (banner + diagnostics drawer), consuming the structured log snapshots.
- [ ] Extend `run.py` / launcher prompts to optionally kick off `project_autofix_orchestrator.py --scan-only` before presenting UX mode choices.

## 3. Documentation & Ops
- [ ] Add README section describing the orchestrator workflow, common flags, and integration expectations for sibling repos.
- [ ] Define remediation playbooks for repos lacking `scripts/ai_auto_fix.py` so the automation grid eventually covers 100% of `.git` folders.
- [ ] Create CI job that runs orchestrator in scan-only mode to prevent unnoticed drift in workspace coverage.

## 4. Workspace Auto-Guard Expansion
- [ ] Wire `scripts/workspace_auto_guard.py` JSON output into a FastAPI endpoint (`/workspace/health`) so remote agents and dashboards can query automation coverage.
- [ ] Teach `run.py` to expose a "Workspace Guard" launch mode that chains the orchestrator + auto-guard before surfacing UX prompts.
- [ ] Support per-repo `.osdash-auto.json` manifests so teams can override detected test commands or provide opt-out justifications.
- [ ] Design frontend visualizations (tiles + filters) that highlight skipped repos, failing commands, and stale timestamps from the auto-guard report.
