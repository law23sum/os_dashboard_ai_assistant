# BLUEPRINT V+1000 — Target System (Incremental Roadmap)

Updated: 2025-02-16

## Target Architecture
```mermaid
flowchart LR
  UI[React/Electron SPA] --> API[FastAPI Edge (/api)]
  API --> SVC[Service Layer\n(Tasks, Projects, Intelligence, Integrations, Harness)]
  SVC --> DB[(Postgres/SQLite\n+ Alembic)]
  SVC --> BUS[Async Queue\n(RQ/Celery placeholder)]
  BUS --> WORKERS[Drivers/Daemons\n(Planes-aware)]
  SVC --> OBS[Telemetry Gateway\n(OpenTelemetry exporters)]
  OBS --> APM[Logs/Metrics/Traces]
```

### Module Boundaries
- **Presentation**: React/Vite SPA + Electron shell; shared UI kit (layout/nav/cards/forms/toasts) and skeleton states. Observability consumes diagnostics + harness report APIs.
- **API Boundary**: FastAPI routers grouped by domains (projects/tasks/ledger, intelligence/TRF, integrations, observability). Add auth dependencies per route.
- **Service Layer**: Python services with dependency injection (DB/session + providers). Tasks/Projects emit ledger events; Intelligence computes health/risk; Harness service reads/writes reports and summarizes CI readiness.
- **Persistence**: Postgres (SQLite for dev) with Alembic migrations; tables for users/tenants, projects, tasks, ledger_events (hash-chained), integrations, harness_runs.
- **Async/Eventing**: Queue for long-running driver actions and AI jobs; emit events to Observability and ledger.

### Data Model (MVP)
- `users(id, email, role, tenant_id, created_at)`
- `tenants(id, name, plan)`
- `projects(id, name, status, priority, owner_id, tenant_id, created_at)`
- `tasks(id, project_id, title, status, priority, due_date, owner_id, created_at)`
- `ledger_events(id, project_id, actor, action, payload_json, hash, prev_hash, created_at)`
- `harness_runs(id, root_path, status, passed, failed, skipped, report_path, created_at)`

### UI Information Architecture
- **Dashboard**: project/task health, plane status, latest harness run, error budget card.
- **Projects**: list + ledger timeline, filters, per-project intelligence (risk/resonance), TRF trace modal.
- **Runs/Jobs**: harness runs, driver queue, retry/backoff controls.
- **Observability**: diagnostics stream + metrics/traces, harness summary, retention notices.
- **Integrations**: API connectors, Office realtime, driver packs (install/health).
- **Settings**: env templates, auth tokens, feature flags, log retention toggles.

### Observability Plan
- Standardize structured logging (JSON) with correlation IDs.
- Export metrics/traces via OpenTelemetry (FastAPI middleware + client spans); ship to local OTLP collector by default.
- Rotate diagnostics/harness logs with size cap; surface retention status in UI.
- Health endpoints: `/healthz`, `/readyz`, plane-specific `/planes/*`.

### Security Model
- AuthN: bearer token session (fastapi-users or lightweight dependency), optional local API key for dev.
- AuthZ: role + tenant scoped; gate mutating routes; enforce tenant filters in queries.
- Secrets: `.env.template` + `.env.example` per environment; never commit secrets; gitleaks in CI.
- Input validation: Pydantic models at boundaries; output encoding for UI docs.

### Release Strategy (Incremental)
1) **Stabilize foundation**: add pytest/Frontend CI, dependency checks, `.env.template`, Alembic baseline, harness report endpoint (done) + retention.
2) **Data/ledger**: implement ledger_events table + APIs/UI; add hash verification and migrations; seed demo data.
3) **Auth/tenancy**: introduce user/tenant tables + auth dependencies; update routes/UI controls.
4) **Planes & observability**: expose plane adapters + health, add OTEL exporters, metrics widgets.
5) **Intelligence/TRF & research**: build intelligence cards + TRF traces; wire research/digital twin routes to mock drivers, then real connectors.
6) **Performance/reliability**: indexes, pagination, caching (project/task lists), queue backpressure, load-test scaffolding for critical APIs.
