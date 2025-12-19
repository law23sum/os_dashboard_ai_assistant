# OS Dashboard Architecture Blueprint (v1000 outlook)

This living document describes the intentional architecture for the OS
Dashboard AI Assistant as it evolves toward the “version 1000” horizon. Append
entries as you make structural changes so future maintainers can trace our
decisions.

---

## 1. System Tenets

1. **Unified AI Control Plane** – All personas, daemon/driver controls,
   reasoning traces, and Assistants API integrations flow through a single
   React/Electron UI. Tkinter remains optional, not canonical.
2. **Event-driven FastAPI core** – Backend routers expose cohesive resource
   domains (`/ai/os/*`, `/operations`, `/reasoning`, `/office/realtime`, etc.)
   so the React client and automation scripts share one API surface.
3. **Scriptable automation** – `scripts/` hosts CLI workflows (auto-fix,
   shell, code interpreter, assistants demo). Launchers should call them where
   safe so log-tail, test, and AI-repair loops are automatic.
4. **Documentation as code** – Every major addition appends summary + detailed
   architecture notes (this file & `OSD_FUTURE_FEATURES.md`). Over time, these
   docs become the canonical change log/decision log.

## 2. High-level Component Map

```
┌───────────────────────────┐
│ React / Vite / Electron   │
│  - /ai/copilot            │
│  - /ai/os, /ai/nas, etc.  │
└─────────────┬─────────────┘
              │ REST / WebSocket
┌─────────────▼─────────────┐
│ FastAPI Routers           │
│  backend_api/routers/*    │
│  assistant_core services  │
└─────────────┬─────────────┘
              │ sqlite / files
┌─────────────▼─────────────┐
│ assistant_hub_gui legacy  │
│  (Tkinter, historical DB) │
└─────────────┬─────────────┘
              │ CLI bridges
┌─────────────▼─────────────┐
│ scripts/*.py/.sh          │
│  auto_fix, shell,         │
│  code_interpreter, demos  │
└───────────────────────────┘
```

## 3. 2025-12-12 Updates

### AI Copilot surface
- Consolidated persona, chat, writer, operations, reasoning, daemon control,
  driver throttles, and orchestrator toggles into one React page.
- Reused existing API clients (`apiPath`, `API`) so the UI mirrors Tkinter’s
  data sources without duplicating business logic.

### Assistants CLI integration
- Added `scripts/assistants_demo.py` with helper functions that mirror the
  notebook’s workflow (assistant creation, threads, runs, tool outputs,
  function demo). Uses the official `openai` SDK.
- README now points to the CLI, ensuring future engineers have a scripted path
  for complex tool flows.

## 4. Forward-looking Decisions

1. **Automation Launch Hooks**  
   When `start_ui.py` (or future project launchers) spin up services, they will
   optionally start `scripts/ai_auto_fix.py` with test specs. This keeps desktop
   and web shells self-healing.

2. **Assistants in UI**  
   Extend `/ai/copilot` with sections for Assistants threads/runs so the CLI
   outputs are visualized. Use FastAPI routers to store assistant metadata.

3. **NAS + Workflow parity**  
   The NAS dashboard already exists; integrate its control widgets into Copilot
   as collapsible panels so the full Tkinter parity lives in one workspace.

4. **Documentation cadence**  
   Every future change should:  
   - Update `OSD_FUTURE_FEATURES.md` with feature-level notes.  
   - Append architecture decisions here.  
   - Log TODOs in `OSD_TODO.md`.

## 5. Assistants telemetry bridge (2025-12-12)

- Added a local-only persistence layer (`localStorage`) for Assistants CLI runs inside
  `frontend/src/pages/AICopilot.tsx`. Until FastAPI endpoints exist, the UI logs
  question, tools, status, and notes per run so operators retain history even when
  the backend is offline.
- The widget mirrors Tkinter’s legacy logbook but leverages the React control room.
  Data is normalized with explicit tool/status guards to prevent corrupt entries.
- Clear separation of concerns: CLI automation still lives in `scripts/assistants_demo.py`
  while the UI simply reflects user-input telemetry, ensuring we can swap in real
  APIs later without rewriting the front end.
