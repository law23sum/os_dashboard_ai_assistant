# Decisions Log

Updated: 2025-12-17

- **Artifact location**: Maintain canonical handoff files under `handoff/` in-repo now that the home drop was removed.
- **Single-product scope**: Treat this repository as one multi-surface product (React UI + FastAPI + CLI + scripts + legacy GUI); no additional git roots discovered.
- **API canonical entrypoint**: Use `assistant_hub.api.server:create_app` as the authoritative FastAPI surface; keep `backend_api.main` only as a compatibility shim until all callers migrate.
- **Workspace CLI direction**: Evolve the existing `osdash` command (scan/test/run/doctor) instead of introducing a new binary; reuse harness/workspace helpers for discovery and reporting.
- **Observability baseline**: Standardize on correlation IDs + structured JSON logs, add `/healthz` + `/readyz`, and rotate NDJSON diagnostics before adopting external telemetry stacks.
- **Auth path**: Implement token/role middleware first (admin/operator/viewer), keeping UI-friendly headers; design for pluggable OIDC later without blocking local dev.
- **Harness correlation**: Attach a run-level UUID to every `osdash test` execution, propagate it to per-project and workspace JSON reports, and enforce timeouts on commands to avoid hung CI runs.
- **Spec canon index**: Maintain `documentation/consolidated_md/technical_spec_v6_alignment.md` as the single navigation surface mapping spec v6 chapters to legacy sources; prefer updates here before adding new documents.
