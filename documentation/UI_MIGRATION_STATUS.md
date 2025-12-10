# UI Migration Status — Desktop ↔ Web Parity

This log tracks how the legacy Tkinter cockpit maps to the new React/TypeScript
experience so we can retire duplicate code safely. Each row lists the original
Tk tab/feature, the React route/component that replaces it, and the current
status.

| Tkinter Surface (`assistant_hub/gui.py`) | React Route / Component | Status & Notes |
| --- | --- | --- |
| Dashboard (Research & Simulation workspace) | `/` → `frontend/src/pages/Research.tsx` | ✅ Modernized. Shares state via `assistant_hub/research_workspace.py` and FastAPI `/research/*`. |
| Ops Dashboard (system stats, tasks summary) | `/dashboard` → `frontend/src/pages/Dashboard.tsx` | ✅ Ported. Displays task metrics, system resources, and matches legacy summary view. |
| Tasks tab | `/tasks` → `frontend/src/pages/Tasks.tsx` | ✅ React CRUD hooked to `/api/tasks` with Tk-style filters + summary panel. Legacy view retained only for automation-only bulk forms. |
| Projects tab | `/projects` → `frontend/src/pages/Projects.tsx` | 🔄 CRUD + Tk summary/ledger panels now live; attachments/insight flyouts still live in Tk until React panels ship. |
| AI Console / Chat | `/chat` → `frontend/src/pages/Chat.tsx` | 🔄 Compose/send now flows through `/api/chat` so the “Compose Message” panel works; streaming + tool feedback remain TODO. |
| Integrations hub | `/integrations` + `/integrations/api-connectors` | ✅ Shares `assistant_hub/integrations_workspace.py` + FastAPI `/integrations/*`; Tk modals now read the same connector summaries + incident feeds. |
| Analytics tab | `/analytics` → `frontend/src/pages/Analytics.tsx` | ✅ Bound to `assistant_hub/analytics_workspace.py` (`/api/analytics/*`) so the charts + drill-down cards mirror the Tk “Analytics” tab. Billing/operations exports still live in Tk. |
| Templates / Capsules | `/work/templates` → `frontend/src/pages/Templates.tsx` | ✅ Task template CRUD hits the new `/api/templates/*` endpoints while the governed document catalog + placeholders come from `assistant_hub/templates_workspace.py`, keeping Tk + React in lock-step. |
| Settings | `/settings` → `frontend/src/pages/Settings.tsx` | ✅ FastAPI `/api/settings` now persists theme/default view/system toggles; Tk surface only needed for legacy font sliders. |
| Monitoring / Observability | `/monitoring` → `frontend/src/pages/Monitoring.tsx` | ✅ Powered by `assistant_hub/monitoring_workspace.py`; Tk now falls back to the same workspace snapshot whenever the AI service is offline. |
| Legacy extras (AI Ops detail panes, Collaboration flyouts) | `/ai-ops`, `/collaboration` | ⚪ Routes scaffolded but still show placeholder copy; Tk continues handling these flows until the remaining flyouts migrate. |

### Shared Infrastructure
- **Backend** — `assistant_hub/api/server.py` now exposes every surface Tk relied on (tasks, projects, chat, daemons, billing, research state, etc.) so React and Tk use the same APIs.
- **Shared State** — Research (`assistant_hub/research_workspace.py`), Writer (`assistant_hub/writer_workspace.py`), Monitoring (`assistant_hub/monitoring_workspace.py`), and Templates (`assistant_hub/templates_workspace.py`) keep Tk + React views in sync.
- **Launcher** — `start_ui.py` is now the single entry point that prompts engineers to pick web vs desktop mode, keeping dev/test workflows in sync across surfaces.

Update this document whenever a Tk feature reaches parity in React so we can
track what remains before deleting the legacy GUI.
