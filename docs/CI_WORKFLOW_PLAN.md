# CI Workflow Plan (Backend + Frontend)

Goals
- Parity with local `osdash test --dry-run`: lint, tests, dependency checks.
- Works on Linux/macOS/Windows runners; uses new DB path `~/.osdash/data/assistant_hub.db` by default.

Jobs
1) Backend (matrix ubuntu/macos/windows)
   - Python 3.11
   - Install `requirements.txt`
   - Run `python -m assistant_hub.scripts.db_migrate`
   - Lint (ruff/flake8 if present)
   - Pytest (short-circuit `--maxfail=5`, `--tb=short`, coverage threshold ~60)

2) Frontend (ubuntu)
   - Node 20, `npm ci`
   - `npm run lint` (if configured)
   - `npm test -- --runInBand` (or `npm run test`), then `npm run build`

3) Compose smoke (ubuntu)
   - `docker compose up -d`
   - Probe `/health` or `/api/health`

4) Debian parity smoke (ubuntu)
   - Run container, install deps, import core modules.

5) Optional
   - Secret scan (gitleaks/semgrep)
   - pip/npm audit (warn-only)
   - k6/locust load-test smoke once scripts land.

Env
- `ASSISTANT_HUB_DATA_DIR=/tmp/osdash-data`
- `ASSISTANT_HUB_DB=/tmp/osdash-data/assistant_hub.db`

Notes
- Use caching for pip/npm.
- Preserve existing workflows; this plan can be merged into `.github/workflows/ci.yml`.
