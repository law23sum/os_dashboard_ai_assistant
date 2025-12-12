# OS Dashboard TODOs (current focus)

Date: 2025-12-12  
Owner: Sir Chief Fellow Director Principal Software Solutions Systems Engineer Architect

1. **Launch Automation Hooks**
   - Update `start_ui.py` (and other launch scripts) so they can optionally
     start `scripts/ai_auto_fix.py` with pre-configured test specs.
   - Ensure the auto-fix monitor can tail frontend + backend logs without
     manual intervention.

2. **Assistants UI Integration**
   - ✅ Phase 1: `/ai/copilot` now captures Assistants CLI runs locally (question,
     tools, status, notes) to mirror the Tkinter logbook.
   - Next: add FastAPI endpoints/DB tables so we can sync assistant metadata and
     show live runs/threads when the backend is online.

3. **NAS & Workflow Panels**
   - Port NAS simulator controls and workflow orchestrator charts into the
     Copilot console (collapsible sections, same data sources as `/ai/nas` and
     `/ai/os`).

4. **Docs Maintenance**
   - Keep appending feature + architecture notes into
     `OSD_FUTURE_FEATURES.md` and `OSD_ARCHITECTURE_BLUEPRINT.md` for every
     substantial change.
   - If critical code snippets need long-term preservation, create additional
     doc files with clear filenames.

5. **Opportunities / Future Features**
   - Consider exposing the shell/code-interpreter/assistants CLIs via Electron
     webviews for users who prefer GUI buttons.
   - Explore multi-project automation: detect sibling git repos, run the
     AI auto-fix loops, and report status inside the dashboard.
