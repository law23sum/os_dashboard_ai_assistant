# OS Dashboard AI Assistant — Blueprint V+1000

Updated: 2025-12-17

## Target Architecture (evolutionary, spec v6 aligned)
```mermaid
flowchart LR
  subgraph UI["UI Surfaces"]
    Web[Web UI (React/Vite)]
    Desktop[Desktop (Electron shell)]
    CLI[CLI (osdash)]
  end

  subgraph API["API Boundary (FastAPI)"]
    Auth[Auth middleware\n(token/session + roles)]
    Gateways[REST Routers\n(workspaces, observability, integrations, billing)]
  end

  subgraph SVC["Service Layer"]
    Workspaces[Workspaces/Projects/Tasks]
    ObservabilitySvc[Observability & Diagnostics]
    IntegrationsSvc[Drivers & Connectors]
    BillingSvc[Billing & Policy]
  end

  subgraph Data["Persistence & Messaging"]
    DB[(SQLite ➜ Postgres)]
    Cache[(Cache)]
    Events[[Event Bus / Job Queue]]
    Storage[(Artifacts/Attachments)]
  end

  subgraph Telemetry["Observability"]
    Logs[Structured Logs\n+ Request IDs]
    Metrics[Metrics (Prometheus)]
    Traces[Traces/Spans]
  end

  UI -->|HTTP/WebSocket| API
  CLI -->|Harness/Reports| API
  API --> Auth --> Gateways --> SVC
  SVC --> DB
  SVC --> Cache
  SVC --> Events
  SVC --> Storage
  API --> Telemetry
  SVC --> Telemetry
  UI -->|Surfaced status| Telemetry
```

## Evolutionary Phases (Version +1000 path)
1) **Stabilize & observe (short term)**  
   - Add CI workflow (lint/test/security) and env validation.  
   - Add request IDs, structured JSON logs, `/healthz` and `/readyz`.  
   - Normalize SQLite path + migrations seed.  
   - Wire UI dashboard/projects/logs to typed API payloads with pagination.
2) **Secure & govern (near term)**  
   - Token/session auth with roles (admin/operator/viewer); secure headers.  
   - Policy hooks for cost/driver budgets; audit log for mutations.  
   - Secret/dependency scans and baseline gitleaks/semgrep/trivy.  
   - Pagination + rate limits + retry/backoff for outbound calls.
3) **Scale & extend (mid term)**  
   - Optional Postgres backend; async job queue for long-running AI/driver tasks.  
   - Caching/memoization for dashboards; indexing for projects/tasks/logs.  
   - Metrics + traces exporters; load-test scaffolding for `/dashboard/summary` and `/tasks`.  
   - Plugin/driver pack lifecycle and marketplace scaffolding aligned to spec.

## Module Boundaries
- **frontend/** — Presentation only; fetches typed client SDK (`frontend/src/api`) targeting `/api/*`; uses shared design system tokens/components; routes for Dashboard, Projects, Tasks/Runs, Observability/Logs, Settings, Integrations, Docs/Help, Admin.
- **assistant_hub.api** — FastAPI app factory with middleware (auth, request IDs, timing), routers by domain (workspaces, observability, integrations, billing, admin), consistent error envelope, OpenAPI/SDK generation.
- **assistant_hub.services** *(to formalize)* — Pure domain services for projects/tasks, diagnostics, integrations, billing/policy; unit-testable without FastAPI.
- **assistant_hub.persistence** *(to formalize)* — Session factory, Alembic migrations, schema version table, SQLite default path `~/.osdash/data/assistant_hub.db`, optional Postgres via `DATABASE_URL`, pagination helpers.
- **assistant_hub.observability** — Structured logging config, request IDs, health/readiness, metrics stub, NDJSON runtime diagnostics with rotation.
- **async/eventing** — Job queue (RQ/Celery/Arq) for long-running AI/driver tasks; event bus for audit and status beacons consumed by Observability UI.
- **scripts/osdash harness** — Workspace runner for `scan|test|run|doctor`, unified reporting, optional autofix loop; publishes reports under `logs/osdash/` and to CI artifacts.

## Data Model & Migration Approach
- Introduce migration folder (Alembic/SQLModel) with `schema_migrations` table and deterministic DB path under `~/.osdash/data/`.  
- Add indexes on `projects.name`, `projects.slug`, `tasks.project_id`, `tasks.status`, `tasks.updated_at`.  
- Pagination + limits on list endpoints; default `page_size` capped (e.g., 50).  
- Seed/demo data guarded by `OSDASH_SEED_DEMO=1`; avoid prod seeding.  
- Attachments stored under `~/.osdash/storage/` with metadata rows; integrity checksums required.

## UI Information Architecture
- **Navigation**: Dashboard · Projects · Tasks/Runs · Logs/Observability · Integrations · Settings · Docs/Help · Admin.  
- **Dashboard**: Cards for plane health, recent activity, open tasks, usage/billing preview, alerts.  
- **Projects**: List + detail (tasks, runs, timeline, attachments); filters/pagination; create/edit flow with validation.  
- **Tasks/Runs**: Queue/status view, retries/history, owner/agent persona, pagination and streaming logs for active runs.  
- **Observability**: Live diagnostics feed (request IDs), plane status, uptime/error counts, node resource stats, download NDJSON.  
- **Settings**: Environment + secrets template, feature flags, data dir location, auth tokens.  
- **Integrations**: Catalog + connect/test flows; driver pack metadata surfaced.  
- **Docs/Help/Admin**: In-app docs linked to spec chapters; admin tools for migrations, background worker status, cache clear.

## Observability Plan
- Middleware injects `X-Request-ID` (persisted in logs/diagnostics and echoed to UI); structured JSON logs; correlation on errors.  
- `/healthz` (liveness) and `/readyz` (DB + cache + queue).  
- Prometheus-compatible metrics stub (request counts/latency, error counts, queue depth).  
- NDJSON runtime diagnostics with rotation and retention policy; CLI harness attaches correlation IDs to reports.  
- UI shows request IDs, latency, error badges, and plane health from `/planes/status`.

## Security Model
- Token-based auth initially (static token/env) → pluggable OIDC later; roles (admin/operator/viewer) enforced via dependency guards.  
- Secure headers (HSTS when TLS, content-security-policy, referrer-policy); CORS restricted per env.  
- Input validation with Pydantic models + bounded payload sizes; idempotency keys for mutating endpoints.  
- Secrets via env + `.env.template`; secrets never committed.  
- CSRF considered for browser auth modes; disabled for token-only API by default.

## Performance & Complexity Discipline
- Pagination on list endpoints; caching/memoization for dashboard summaries; indexes on frequent lookups.  
- Retry/backoff + timeouts on outbound drivers/integrations; circuit-breaker guardrails for flaky deps.  
- Load-test harness (k6/locust) targeting `/dashboard/summary`, `/tasks`, `/runtime/diagnostics`; streaming for long responses where helpful.  
- Complexity goals: O(log n) lookups via indexes, O(1) request enrichment via caches, bounded O(n) only for paged lists.

## Release & Migration Strategy
- **Milestone 1**: CI workflow + request IDs/logging + health endpoints + deterministic DB path/migrations; harness reports uploaded.  
- **Milestone 2**: Auth roles + pagination/indexes + API contract typing + Observability UI wired to live data.  
- **Milestone 3**: Async queue + metrics/traces exporters + Postgres option + load-test scaffolding + integration hardening.  
- Backward compatibility: keep `backend_api.main` shim and legacy Tkinter UI until new surfaces are stable; mark deprecation schedule in docs.
