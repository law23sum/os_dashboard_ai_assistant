# Risks & Mitigations

Updated: 2025-12-17

- **No auth/authorization on APIs**: Routes are effectively open locally; risk of data leakage or misuse. *Mitigation*: add bearer/session middleware with roles; gate mutating routes; secure headers and CORS defaults per env.
- **SQLite as single source of truth**: Concurrency/durability limits and no migrations/versioning. *Mitigation*: add Alembic migrations, deterministic data dir, indexes, and optional Postgres with backups/checksums.
- **Observability depth**: Correlation IDs exist, but metrics/traces/rotation are missing, so failures are hard to triage. *Mitigation*: structured JSON logs + rotation, Prometheus exporter, trace stubs, surface request IDs to UI and CLI reports.
- **CI/tooling gaps**: No unified lint/test/security workflow and pytest is not available in the current env. *Mitigation*: add CI workflow, declare dev requirements (pytest, ruff, eslint), and gate merges on green runs.
- **Mocked UI data flows**: Several pages render static/demo payloads; drift from backend contracts. *Mitigation*: align API schemas, add contract tests and MSW fixtures, implement loading/error states.
- **Secret handling**: Env templates exist without validation; risk of missing/unsafe defaults. *Mitigation*: add `.env.template`, doctor checks, and gitleaks/semgrep scans; remove default passwords from docker-compose for prod builds.
- **Legacy/compat surfaces**: `backend_api.main` and Tkinter UI share schema but lack migrations; changes could break them silently. *Mitigation*: compatibility tests, shared migration layer, documented deprecation plan.
