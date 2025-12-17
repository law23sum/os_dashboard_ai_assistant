## implemented vs missing (spec v6 reference)
- Implemented (partial): layered split UI → FastAPI → domain engines; multi-plane concepts appear (dashboard, projects, tasks, monitoring, analytics, network/security routers); runtime diagnostics endpoint; offline/demo mode via launcher; multi-surface UIs (web, desktop, legacy Tkinter); driver/automation scaffolding in `assistant_core`.
- Implemented (minimal): config via env + dotenv; SQLite persistence; sample personas and AI reply generator; integrations gateway scaffolding; network monitoring/router surfaces; basic billing/usage stubs.
- Missing/weak: authN/authZ, roles/tenants, governance plane, policy packs; CIR/ledger/index/search formalization; capsule graph + versioning; billing engine and cost governance; TRF hooks and long-horizon reasoning traces; workspace abstractions with SLOs/SLIs; migration + schema evolution; observability (metrics/traces/log correlation); resilience patterns (retries/backoff/circuit breakers); secure-by-default headers and CSRF/anti-abuse; load/perf baselines.

## conflicts / ambiguities
- Dual API entrypoints (`assistant_hub.api.server` vs `backend_api.main`) with overlapping routers; choose `assistant_hub.api.server` as canonical and keep `backend_api.main` as compatibility shim.
- UI data expectations vs API schemas are implicit; some routers return demo/cached data without contract tests. Adopt typed schemas in FastAPI responses and a shared client SDK for React.
- SQLite location varies by env vars (`ASSISTANT_HUB_DB` vs default under assistant_hub_gui); align to a single default path under project data dir with migrations.

## prioritized gap list
- P0: AuthZ/authN baseline (token-based session + role guard), structured error schema, correlation IDs, request validation + security headers.
- P0: Database migrations/versioning, deterministic data dir, seeds for demo data; contract tests for key routes (dashboard/projects/tasks/runtime_diagnostics).
- P0: Unified CI running lint/format (ruff/eslint/prettier), pytest, vitest, and security scan (semgrep/gitleaks) on PRs.
- P1: Shared API client for React + typed endpoints; front-to-back E2E path for dashboard/projects/logs with live data; pagination and limits.
- P1: Observability stack (metrics via Prometheus-compatible exporter, structured logs, trace stubs) and health/readiness probes.
- P1: Consolidate API bootstrap through `assistant_hub.api.server` with compatibility mounts; deprecate duplicate router wiring.
- P2: Performance scaffolding (indexes, caching for summaries), load-test harness for critical endpoints, event stream for diagnostics.
