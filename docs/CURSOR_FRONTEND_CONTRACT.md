# Frontend Contract for Automation & Workspace UX

This brief summarizes the API shapes Cursor should consume and the UI components to build.

## API Shapes

- `GET /health` or `/healthz` or `/readyz`
  - Response envelope: `{status, request_id, correlation_id, data:{db, uptime_ms, version}}`
  - Use for header badge / basic connectivity.

- `GET /automation/status`
  - Envelope: `{status, request_id, correlation_id, data:{workspace_shell, auto_fix, events}}`
  - `workspace_shell`/`auto_fix`: `{exists, files, latest}` based on logs.
  - `events`: optional JSONL entries from `logs/automation_status.jsonl` (max 50).
  - UI: automation badge (HEALTHY/HEALING/ATTENTION NEEDED) with polling/backoff and link to docs.

- `GET /workspace/health`
  - Provided by `backend_api/routers/workspace_health.py`.
  - Response: `{status, request_id, correlation_id, data:{root, scan_timestamp, summary, projects[]}}`
  - Projects include health_score, statuses, todos, autofix/test/lint status, warnings/errors.
  - UI: tiles + filters for skipped/failing/stale, accessible indicators.

## UI Components

- Automation badge/banner:
  - States: HEALTHY / HEALING / ATTENTION NEEDED.
  - Poll `/automation/status` every 30s; exponential backoff on failure.
  - Link to automation docs; ensure aria-label + keyboard focus.

- Workspace Guard panel:
  - Use `/workspace/health` to render per-project cards; filter by status and staleness.
  - Show counts from summary; expose errors/warnings for quick triage.
  - Accessible chips/badges; avoid color-only cues.

- Health indicator:
  - Use `/healthz` for quick connectivity; show correlation_id in debug tooltip to help support.

## Accessibility & UX Notes

- All badges/buttons: `aria-label`, focus visible, keyboard navigable.
- Use consistent color tokens for statuses; provide text labels.
- Loading/error/empty states for each panel; avoid spinners without labels.

## Polling & Error Handling

- Poll automation + workspace health every 30s; on failure, back off (e.g., 30s → 60s → 120s) and show “offline” state with retry.
- Surface `request_id`/`correlation_id` in dev tools to aid debugging.
