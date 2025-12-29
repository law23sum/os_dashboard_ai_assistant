# Risks & Mitigations

Updated: 2025-02-17

- **Unauthenticated APIs** — All endpoints currently open beyond CORS; risk of unauthorized access or data tampering. *Mitigation*: add bearer token middleware + role hints; gate mutating routes; document required headers; add tests.
- **No migrations/indexes** — SQLite schema unmanaged; production DB drift and slow queries likely. *Mitigation*: introduce Alembic migrations + version table; add indexes on key lookups; gate startup on migration state.
- **Limited observability** — Diagnostics are file-based only; no metrics/traces or log rotation. *Mitigation*: add structured logging + rotation, correlation IDs, `/healthz`/`/readyz`, metrics stub, and surface in UI.
- **CI gaps** — Release workflows build artifacts but do not run lint/test/security; regressions may slip. *Mitigation*: add unified CI workflow with pytest, npm test, lint, gitleaks/semgrep/trivy; wire workspace harness dry-run into PR checks.
- **Third-party integrations** — msgraph/msal and other connectors may be unavailable in dev/CI. *Mitigation*: provide stubs/fallbacks in tests; guard imports with optional deps; add health checks with graceful degradation.
- **Secret hygiene** — No `.env.template` and secret scanning not enforced. *Mitigation*: add template with required keys, enforce gitleaks/secretlint in CI, document local handling.
