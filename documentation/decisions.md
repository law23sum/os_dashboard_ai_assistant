## decisions
- Place required handoff files under `documentation/` using lower_snake_case to align with repository conventions.
- Treat `assistant_hub.api.server` as the canonical API entrypoint; keep `backend_api.main` as a compatibility shim until routes migrate to `/api/v1`.
- SQLite remains the default store for now with a migration path to PostgreSQL; migrations will manage schema versioning and seeds.
- Adopt token-based auth with role claims as the first secure-by-default step, delaying full SSO/OIDC until base flows stabilize.
- Consolidate automation under a single CLI (`osdash`) instead of scattering scripts; reuse existing orchestrator scripts internally.
