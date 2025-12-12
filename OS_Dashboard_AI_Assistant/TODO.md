# OS Dashboard AI Assistant – TODO Backlog

_Last updated: 2025-02-14_

## Short-Term
1. **Dynamic persona registry** – externalize `assistant_core/ai.py` persona → model mappings to YAML/JSON so GPT upgrades do not require code edits. (Blueprint reference: v1000 – Milestone 1)
2. **Health fabric dashboard** – extend `/office/realtime` (and React counterpart) to visualize every workspace monitored by `scripts/project_auto_fix_manager.py`, including status, log cursors, and auto-fix iterations.
3. **Auto-fix manager polish** – add per-project override files (e.g., `.osdash-autofix.yml`) so teams can define custom commands/log directories without editing the manager.

## Mid-Term
4. **Compliance inference hooks** – integrate a classifier that watches Technical Spec Sheet interactions and dynamically tightens telemetry retention, encryption, and guardrails.
5. **Edge/desktop UX convergence** – refactor layout primitives to share a single navigation grammar for React web, Electron, and (future) AR/CLI shells.
6. **Office mesh expansion** – surface live citations and AI responses within Word/Excel add-ins, closing the loop between `/office/realtime` telemetry and user-visible pane updates.

## Long-Term
7. **Distributed self-heal mesh** – allow `project_auto_fix_manager.py` to coordinate remote hosts via SSH, giving enterprises a turnkey fleet healer.
8. **Ledger-grade audit streams** – persist auto-fix attempts/results alongside Office session events to an append-only store to exceed government/compliance requirements.
9. **Marketplace of copilots** – open the persona registry so partner-built copilots can be onboarded with baked-in governance (contracts, rate limits, logging).
