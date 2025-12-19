# Portfolio TODO · 2025-12-12

> Append new TODOs instead of deleting prior ones so execution history stays transparent. Reference these tasks when launching Codex/autofix sessions.

## Active Items
- [ ] **Daemonize Portfolio Guardian** – wrap `scripts/portfolio_supervisor.py` with a launch agent or tmux session so it runs automatically when git repos change (ties back to the “execute whenever a project runs” requirement).
- [ ] **Blueprint Telemetry API** – expose a `/api/office/realtime/blueprint` endpoint so the frontend, desktop GUI, and CLI share the same roadmap signals instead of recomputing locally.
- [ ] **Realtime queue autoscaler** – extend `assistant_core.integrations.office_realtime.AIOfficeWebSocketRouter` to scale worker pools based on `queue_depth` thresholds surfaced in the UI.
- [ ] **UI instrumentation** – capture UX analytics (interaction counts, playbook usage) to prove the interface remains “seamless/intuitive” as features grow.

## Opportunities & Future Features
- [ ] **Cross-project manifest registry** – ingest add-in manifests from every git repo detected by the supervisor so Office clients can switch contexts without leaving the dashboard.
- [ ] **Autonomous compliance ledger** – stream Portfolio Guardian results into a signed ledger table (SQLite + hash chain) to meet enterprise/government evidentiary standards.
- [ ] **Adaptive persona routing** – feed persona selection (Aria/AIC/Sora) into the realtime router so each AI job inherits the correct policy + tone automatically.

When starting a new engineering session, read these TODOs aloud (or pass them to Codex) to keep execution synchronized with the blueprint. Add your own items below the relevant heading to extend the queue.
