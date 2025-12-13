# Tkinter → React Migration Mapping

This document tracks every Tkinter-only view in `assistant_hub_gui/assistant_hub/gui.py`
and the React/TypeScript surface that will replace it. The goal is to keep a single UI
codebase (React) that renders identically inside the browser and the desktop shell while
Tkinter remains available for legacy/offline workflows during the transition.

| Tkinter Tab / Section (`gui.py`) | React Feature Slice | Status | API Work Required | Notes |
| --- | --- | --- | --- | --- |
| `_build_dashboard_tab` | `frontend/src/pages/Dashboard` | ✅ Parity UI w/ persona load | `/api/dashboard/stats` includes persona summaries | Widgets, persona chips, and quick links mirror Tk layout |
| `_build_tasks_tab` | `frontend/src/pages/Tasks` | ✅ CRUD + filters shipped | Bulk update endpoints, template CRUD | React view uses Tk palette tokens and shared task templates |
| `_build_projects_tab` | `frontend/src/pages/Projects` | ✅ Core grid complete | `/api/projects` enhancements (ordering, dependencies) | Include OneNote/Doc links pulled from `/api/projects/{id}/links` |
| `_build_chat_tab` | `frontend/src/pages/Chat` | ✅ UI migrated (streaming TBD) | WebSockets for `/ws/chat`, file upload route | Tk role badges + terminal output replicated |
| `_build_integrations_tab` | `frontend/src/pages/Integrations` | ✅ Connector cards migrated | `/api/integrations` detailed status + actions | Collapsible cards share Tk gradients; API surface still expanding |
| `_build_tools_tab` | `frontend/src/pages/Tools` | ✅ Shared terminal with catalog | `/terminal`, `/terminal/commands` (FastAPI ✅) + `/api/automation/run` | React terminal uses shared Tk theme and spec-sheet quick actions |
| `_build_writer_workspace_tab` | `frontend/src/pages/Writer` | ✅ Editor + stats in React | `/api/writer/*` endpoints from Tk helpers | Governance badges + AI suggestions wired through shared state |
| `_build_ai_operations_tab` | `frontend/src/pages/AIOps` | ✅ Feed + filters migrated | Already exposed via `ai_os.app` (`/operations`, `/daemons`, `/search`, `/planes/status`) | React cards reuse Tk neon-glass style |
| `_build_analytics_tab` | `frontend/src/pages/Analytics` | ✅ Charts + metrics live | `/api/analytics/*` for drilldowns | Purple/teal sparkline gradients match Tk |
| `_build_settings_tab` | `frontend/src/pages/Settings` | ✅ Theme + prefs + persona defaults | `/api/settings`, `/api/preferences` | React switches adopt Tk accent colors; persona default + governance banner editors mirror Tk controls |
| `_build_ai_systems_tab` & additive tabs | `/ai/*` routes (`AdvancedAI`, `NAS`, `Security`, `EdgeComputing`, `Workflows`, `AdvancedSystems`) | ✅ UI placeholders implemented | `/api/advanced/{system}` endpoints powered by existing Python helpers | `AdvancedSystems` aggregates parity checklist + documentation links |
| `_build_neural_architecture_search_tab` | `frontend/src/pages/NAS` | ✅ Simulation controls migrated | `/api/nas/experiments`, `/api/nas/results` (placeholder) | Buttons, metrics, and logs keep Tk styling |
| `_build_security_threat_detection_tab` | `frontend/src/pages/Security` | ✅ Threat & scan UI live | `/api/security/threats`, `/api/security/scan`, `/api/security/report` | Detection list + risk metrics mirror Tk panes |
| `_build_edge_computing_tab` | `frontend/src/pages/EdgeComputing` | ✅ Node + deployment UI live | `/api/edge/nodes`, `/api/edge/deploy`, `/api/edge/network` (proposed) | Node cards + network diagrams reuse Tk neon palette |
| `_build_workflow_orchestration_tab` | `frontend/src/pages/Workflows` | ✅ Orchestrator controls live | `/api/workflows`, `/api/orchestrator/metrics`, `/api/orchestrator/control` | Timelines and progress bars echo the classic Tk panel |

## Shared Theme

All React views pull from the Tkinter-inspired palette exported by `frontend/src/theme/index.ts`
and the global CSS utilities in `frontend/src/index.css`. The palette mirrors `_build_color_palette`
inside `assistant_hub_gui/assistant_hub/gui.py`:

- `--osd-background`, `--osd-surface`, `--osd-border` — match the dark and light Tk backgrounds
- `--osd-accent`, `--osd-accentHover`, `--osd-pill` — reuse the indigo gradients/pills
- `--osd-success`, `--osd-warning`, `--osd-error` — bootstyle-inspired semantic badges

Because both the browser SPA and the desktop shell read the same CSS variables, the modern
glass aesthetic stays faithful to the Tkinter experience while benefiting from React layouts.

## Dev + Deployment Flow

1. `./start_ui.py` prompts engineers to run either the Tkinter cockpit or the React +
   FastAPI stack. Selecting the React mode boots `uvicorn ai_os.app.main:app --reload`
   (serving `/app`) and optionally the Vite dev server to mirror the browser experience.
2. React is the only UI codebase. Desktop executables bundle the FastAPI service
   (PyInstaller) plus an Electron/Tauri shell pointed at the same React bundle so Linux,
   Windows, and macOS share identical visuals.
3. Static HTML pages in `docs/` and the previous web prototypes remain available; when
   React reaches parity, each page’s content is migrated into the new components without
   removing the original markdown/HTML files, ensuring no documentation or assets vanish
   mid-migration.

Use this mapping as the checklist when porting Tk-specific features. Each row should be
marked complete once the React slice renders the same data, the FastAPI endpoints are in
place, and the shared theme keeps desktop + browser views consistent. The `/ai/systems`
route (Advanced Systems page) also includes an on-screen verification workflow to compare
Tkinter vs React during migration reviews.
