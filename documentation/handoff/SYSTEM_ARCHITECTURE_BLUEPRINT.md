# System Architecture Blueprint · Version +1000 Outlook

> Permanent design record for the OS_Dashboard_AI_Assistant program. Append new sections instead of rewriting prior history so the blueprint evolves transparently.

## Table of Contents
1. [Repository Reconnaissance](#1-repository-reconnaissance)
2. [Version +1000 Architecture](#2-version-1000-architecture)
   1. [Experience Plane](#21-experience-plane)
   2. [Intelligence & Automation Plane](#22-intelligence--automation-plane)
   3. [Governance & Compliance Plane](#23-governance--compliance-plane)
3. [Implementation Delta – 2025-12-12](#3-implementation-delta--2025-12-12)
4. [Forward Integration Hooks](#4-forward-integration-hooks)
5. [Reference Artifacts](#5-reference-artifacts)

---

## 1. Repository Reconnaissance
- **Frontends** (React/Vite in `frontend/`, plus auxiliary clients inside `assistant_hub_gui/`). They already expose many control surfaces (Office realtime, AI control rooms, dashboards).
- **Middle tier** (`backend_api/`, `assistant_core/`) provides FastAPI routers, AI orchestration, and the Office realtime router. The canonical Technical Spec Sheet (v6) dictates three canonical “planes” (Experience, Intelligence, Governance).
- **Automation scripts** (`scripts/run_tests_with_autofix.py`, `scripts/ai_auto_fix.py`) already pair deterministic tests with AI-driven remediation but operate on a single repo at a time.
- **Data/Governance assets** (SQLite state, documentation under `documentation/`, OS Dashboard TOCs) capture operational knowledge yet lacked an append-only feature/architecture ledger.

The above observations informed the blueprint so the future stack honors the current intent while pushing far toward the requested version +1000 vision.

## 2. Version +1000 Architecture

### 2.1 Experience Plane
- **Unified Realtime Fabric** – Every Office surface (Word, PowerPoint, Excel, OneNote, web dashboard) subscribes to the router and renders status/roadmap cards. The upgraded `OfficeRealtime` page now visualizes mesh density, queue health, and blueprint readiness so operators see a future-proof UX.
- **Playbook-first UI** – Automation playbooks (Narrative Composer, Insight Loom, Portfolio Guardian) are embedded directly into the UI so non-technical operators can trigger complex chains with one glance.
- **Blueprint Telemetry** – Interface exposes the Technical Spec banner, showing Experience/Intelligence/Governance signals. This keeps the GUI “simple + intuitive” even while referencing a sophisticated roadmap.

### 2.2 Intelligence & Automation Plane
- **Portfolio Guardian** – `scripts/portfolio_supervisor.py` crawls every git project, runs `scripts/run_tests_with_autofix.py` (or heuristics such as `pytest`/`npm test`), and reuses the existing AI auto-fix loop. This fulfills the requirement to “apply the scripts to all projects by identifying the .git”.
- **AI Queue Telemetry** – The frontend blueprint cards compute queue density (`pendingJobs`, `queueDepth`) and express readiness (e.g., “Scale queue first”) so the automation plane stays observable.
- **Chained Office playbooks** – Prompt presets (generate/analyze vs. Word/PowerPoint/OneNote) describe how AI actions will cascade across applications, foreshadowing multi-app document synthesis in the v+1000 era.

### 2.3 Governance & Compliance Plane
- **Append-only documentation** – `FEATURES_CHANGELOG.md`, this blueprint, and `PORTFOLIO_TODO.md` live under `OS_Dashboard_AI_Assistant/` so every future operation has a recorded rationale, mirroring the Technical Spec governance mandates.
- **Manifest + policy guardrails** – The UI retains manifest previews, ledger banners, and the governance callout while adding blueprint overlays so compliance stays visible regardless of feature count.
- **Auto-detection boundaries** – The portfolio supervisor ignores sensitive directories (e.g., `node_modules`, `.venv`) and requires explicit roots/env vars to avoid unintended traversal, aligning with security best practices.

## 3. Implementation Delta – 2025-12-12
- Launched **Portfolio Guardian** automation (new Python entrypoint) so the AI auto-fix/test harness can fan out to every repo discovered under configured roots.
- Elevated the **OfficeRealtime** experience with blueprint telemetry, roadmap cards, and automation playbooks that directly reference backend signals (`pendingJobs`, `queueDepth`, live clients). This keeps the UX intuitive while embedding the future architecture story.
- Created the **feature log, blueprint, and TODO** documents to institutionalize governance per request (append-only, stored in `OS_Dashboard_AI_Assistant/`).

## 4. Forward Integration Hooks
1. **Daemonization** – Wrap `scripts/portfolio_supervisor.py` with a lightweight launch agent (e.g., `scripts/portfolio_supervisor.sh`) that watches filesystem events and runs the supervisor whenever git activity occurs.
2. **Blueprint data API** – Introduce `/api/office/realtime/blueprint` returning the UI’s derived telemetry so other clients (desktop GUI, CLI) can reuse the same future-state signals.
3. **Autonomous repair queue** – When the supervisor sees a failure, auto-open a JIRA/GitHub issue with the associated blueprint phase to connect remediation tasks to the roadmap.

## 5. Reference Artifacts
- `Technical Spec Sheet (Version 6 Latest Version).pdf` – canonical requirements and persona responsibilities.
- `backend_api/routers/office.py` + `assistant_core/integrations/office_realtime.py` – current realtime router implementation the blueprint extends.
- `scripts/run_tests_with_autofix.py` / `scripts/ai_auto_fix.py` – AI-enabled regression harness leveraged by the Portfolio Guardian supervisor.
- `frontend/src/pages/OfficeRealtime.tsx` – upgraded Experience plane view rendering mesh telemetry + automation playbooks.

> Continue appending future milestones, deltas, and integration hooks here so the architecture blueprint remains the single source of truth for “version +1000” alignment.

## 6. Workspace Auto-Guard Addendum (2025-12-12)
- **Command surface**: Introduced `scripts/workspace_auto_guard.py` so any `.git` folder—whether or not it already ships `ai_auto_fix.py`—gets attached to the automation mesh. The helper emits JSON blueprints of the commands it would run (ai_auto_fix, `run_tests_with_autofix.py`, `pytest`, `npm test`) and optionally executes them sequentially.
- **Dual-layer automation**: Pair `workspace_auto_guard.py` (test discovery + reporting) with `scripts/project_autofix_orchestrator.py` (long-running monitors) to satisfy the “scripts apply to all projects” directive without overwhelming host resources.
- **Observability hook**: Future frontend cards must ingest the JSON report (`logs/workspace_guard.json`) so operators can see which repositories are compliant, skipped, or awaiting configuration overrides.

## 7. Workspace Auto-Fix Shell Addendum (2025-12-12 Evening)
- **Interactive terminal**: `scripts/workspace_autofix_shell.py` layers a guided CLI over the guard/orchestrator duo so operators can pick specific repos (or run-all) and immediately execute “test → ai_auto_fix” loops with consistent logging.
- **Heuristic command routing**: The shell prioritizes `scripts/run_tests_with_autofix.py` when present, then falls back to canonical heuristics (`npm test -- --runInBand`, `pytest -q`). Failures automatically emit `--test <label=cmd>` payloads to `ai_auto_fix.py`, ensuring every project benefits from AI remediation without additional wiring.
- **Telemetry alignment**: Logs land in `logs/workspace_shell/<repo>.log`, mirroring the guard’s JSON output so backend telemetry endpoints and future UI banners can merge both sources into a single automation health feed.
- **Future UX hook**: The React layout must surface a “Workspace Automation” badge fed by these logs; the planned badge states (Healthy / Healing / Attention Needed) map directly to shell exit codes and AI attempt counters.
