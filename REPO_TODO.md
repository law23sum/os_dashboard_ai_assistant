# OS Dashboard AI Assistant · TODO Ledger (2025-12-12)

1. **Automation Status API**
   - Build `/api/automation/status` inside `backend_api` that summarizes `logs/workspace_shell` and `logs/auto_fix`.
   - Surface repo counts, latest failure timestamps, and outstanding AI fix attempts.
   - Secure endpoint with existing FastAPI dependency stack (API keys + persona scopes).

2. **Frontend Automation Banner**
   - Inject a “Workspace Automation” badge into `frontend/src/components/Layout.tsx` above the nav.
   - States: `HEALTHY`, `HEALING`, `ATTENTION NEEDED`, each linking to the automation docs.
   - Consume the status API and poll every 30 seconds with exponential backoff when offline.

3. **Workspace Shell Telemetry**
   - Export structured JSON alongside the log files so observability collectors can scrape machine-readable stats.
   - Consider adding `--json` flag to `workspace_autofix_shell.py` for CI integrations.

4. **AI Credential Routing**
   - Allow per-repo OpenAI API keys or persona overrides so the shell can run against heterogeneous tenants.
   - Persist preferences either in `assistant_core.db` or `.env.local` templates per project.

5. **Ops Playbook**
   - Document a runbook for kiosk/terminal deployments (auto-login shell executing `workspace_autofix_shell.py --non-interactive --run-all`).
   - Include fallback instructions when npm/python tooling is missing; shell should downgrade gracefully and emit actionable messages.
