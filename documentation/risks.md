## risks and mitigations
- Missing auth/roles today exposes sensitive routes; add token + role guards first, then tighten CORS/headers. Mitigation: ship auth middleware in initial increment.
- No DB migrations; schema drift can corrupt state. Mitigation: introduce Alembic with version table and seeds; run migrations in launcher.
- Observability is minimal (no metrics/traces); failures could be silent. Mitigation: add structured logging with correlation IDs, metrics endpoint, and diagnostics WebSocket feed.
- CI gap: lint/tests/security not enforced. Mitigation: create unified workflow running ruff/pytest/eslint/prettier/vitest/semgrep.
- Dual API entrypoints risk divergence. Mitigation: make assistant_hub.api.server authoritative and mount legacy routes for compatibility until removed.
- Frontend may hit stale/demo data when backend absent. Mitigation: typed API client with clear offline mode flag and UI states for loading/error/empty.
