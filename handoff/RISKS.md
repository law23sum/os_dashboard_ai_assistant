# Risks & Mitigations

Updated: 2025-12-17

- **Unauthenticated APIs** — Most routes are open; exposing the service would leak data or allow mutation. *Mitigation*: add token/role middleware and secure headers; gate mutating endpoints first; ship `.env.template` with required secrets.*
- **Schema drift & data loss** — SQLite schema is implicit and shared across surfaces; no migrations or backups. *Mitigation*: introduce migrations + schema versioning, move DB to deterministic data dir with backups, and add idempotent seeding guarded by env.*
- **Observability gaps** — Diagnostics rely on NDJSON log writes without rotation or metrics/traces; health signals are shallow. *Mitigation*: structured JSON logging with rotation, `/healthz` + `/readyz`, metrics stub, and surfacing request IDs in UI.*
- **CI/security blind spots** — Only release builders run; lint/tests/security scans are absent. *Mitigation*: add CI workflow covering lint/test + gitleaks/semgrep/pip audit/npm audit; publish osdash harness reports as artifacts.*
- **Test tooling missing** — `pytest` is not available in the current environment, so regressions could hide. *Mitigation*: add dev requirements (pytest/ruff) and ensure CI installs and runs them.*
- **Secrets in repo history** — `client_secret_*.json` lives in the tree; risk of accidental use. *Mitigation*: quarantine/remove from releases, enforce gitleaks, and document secrets handling with `.env.template`.*
- **Spec/documentation drift** — Spec index existed but chapter summaries are missing; contributors may follow stale docs. *Mitigation*: regenerate consolidated chapters and keep DECISIONS/TODO updated when behavior changes.*
