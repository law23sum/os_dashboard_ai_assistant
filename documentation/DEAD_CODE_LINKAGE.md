# Legacy / Idle Components & E2E Hookups

The following modules currently have no active callers or UI entry points inside the
main workflow. Rather than delete them outright, this table captures how each piece
can be wired into the front–middle–back (GUI → API → DB) stack.

| Path | Current Status | Potential E2E Role | Next Steps |
| --- | --- | --- | --- |
| `ui/` (legacy web dashboard) | Deprecated entrypoint, prints "removed" | Reuse as kiosk-style thin client that consumes the FastAPI `/system` + `/ai/ask` endpoints for air-gapped deployments | Point `ui/main.py` at `ai_os.app.main` via `requests`, reuse new `docs/dashboard.html` assets |
| `assistant_core/dashboard/main_interface.py` | Legacy desktop shell, not invoked by `assistant_hub_gui` | Could host the desktop orchestrator but backed by the new API client to keep DB + daemon state in sync | Replace its local DB hooks with calls to `ai_os` REST endpoints, keep Tk layout as a lightweight offline mode |
| `assistant_hub_gui/assistant_hub/ui/terminal/cli.py` | Standalone CLI that does not register with FastAPI or GUI | Ideal for DevOps automation: expose the same commands through `/operations` so the CLI mirrors GUI actions | Wrap CLI commands in FastAPI routes (or call the routes) so daemon runs/DB writes remain consistent |
| `assistant_core/intelligence/office_ai_service.py` | New intelligence service without GUI controls | Connects document AI inference to the Writer Workspace once `ai_proxy` is wired for multi-tenant models | Expose this module via `/ai/office` and add a GUI tile under "Writer Workspace" that posts documents + receives edits |
| `assistant_hub_gui/ui/terminal/commands` | Historical command definitions, not surfaced in the new Tk tabs | Could seed the "Tools & Intelligence" tab with ready-made scripts that hit `/system`/`/ai/ask` then persist to DB | Convert command metadata to JSON spec, render it inside Tk + React so commands trigger FastAPI calls |

Document every additional idle module here so compliance + architecture reviews know
why code is retained and how it will connect end-to-end when activated.
