# Blueprint V+1000 – Future-State Roadmap

Updated: 2025-02-17

## 1) Target Architecture (evolutionary)
```mermaid
flowchart LR
UI[React/Electron/Tkinter] --> API[FastAPI Gateway]
API --> SVC[Service Layer\n(domains: projects|tasks|writer|observability|integrations)]
SVC --> DB[(SQLite -> Postgres)]
SVC --> MQ[(Event bus\nRedis/Kafka optional)]
API --> OBS[Observability\nlogs|metrics|traces]
OBS --> APM[(OTel collector)]
UI --> CDN[(Static assets)]
```
- Maintain clean boundary: UI → API → service layer → persistence → async/eventing.
- Gradual steps: keep SQLite for dev, add SQLModel migrations + indices; plan Postgres target with compatibility layer.

## 2) Module Boundaries & Interfaces
- `api`: FastAPI routers per domain, Pydantic schemas with correlation IDs, pagination, timeouts (httpx) and retries on outbound calls.
- `services`: project/task/workspace services, writer/capsule orchestration, diagnostics service, integrations (OneNote/Office). Use dependency injection via FastAPI `Depends`.
- `persistence`: repository interfaces for projects/tasks/documents/diagnostics; SQLite implementation now, Postgres-compatible layer next; migrations via Alembic.
- `async/eventing`: emit events for task updates, diagnostics, audits; start with SQLite-backed outbox; optional Redis/Kafka for multi-instance.
- `ui-kit`: shared React design system (layout, nav, cards, stats, tables, forms, skeletons, toasts); normalize spacing/typography and light/dark tokens.

## 3) Data Model & Migration Plan
- Core tables: users (placeholder), projects, tasks, documents, diagnostics_log, audit_log, capsules, settings. Add indices on `updated_at`, `project_id`, `status`.
- Migrations: add Alembic with baseline from current SQLite schema; generate env template + `scripts/db_migrate.py`; ship `make db/check` in CI.
- Data access: repository classes + DTOs; enforce pagination defaults (limit 50) and max limit.

## 4) UI Information Architecture
- Primary nav: Dashboard · Projects · Tasks · Runs/Jobs · Logs/Observability · Integrations · Settings · Help/Docs · Admin.
- Dashboard: system health, runtime diagnostics feed, recent tasks/projects, billing usage, quick actions (launch backend/frontend/tests).
- Projects/Tasks: paginated lists, filters (owner/status/priority), detail drawers with timeline + audit trail.
- Runs/Jobs: view automation runs (autofix, scripts), retry/abort, log tail.
- Observability: diagnostics stream, API latency/error charts, service uptime; empty/error/skeleton states.
- Settings: API keys, env templates, workspace root, feature flags; secure secrets via env var hints.
- Help/Docs: links to spec, Tk→React parity map, CLI reference.

## 5) Observability Plan
- Logging: structured JSON with `request_id`, `user_id`, `route`, `status`, `duration_ms`; write to file + console; rotate logs.
- Metrics: expose `/metrics` (Prometheus) via `prometheus-fastapi-instrumentator`; track request latency, error rate, background job durations.
- Traces: optional OpenTelemetry exporter; sample rate configurable; propagate trace IDs to frontend for correlation.
- Health: `/healthz` (fast), `/readyz` (DB connectivity, migrations), runtime diagnostics appended to NDJSON.

## 6) Security Model
- Roles: `admin`, `operator`, `viewer` (scopes: settings, integrations, write operations).
- AuthN: start with API key / bearer token middleware; future SSO (OIDC) flag. Store hashed tokens; no secrets in repo.
- AuthZ: per-route dependency enforcing role; UI guards hide restricted actions.
- Protections: enable CORS config, CSRF tokens for form posts, secure headers (HSTS/dev toggle), rate limiting per IP (SlowAPI).
- Secret handling: `.env.example` for all required vars; use `settings.py`/Pydantic BaseSettings; ensure no default secrets in code.

## 7) Release & Compatibility Strategy
- Step 1: Stabilize current stack (tests, lint, CI), expose workspace CLI (done), add pagination + schemas to key endpoints.
- Step 2: Introduce Alembic migrations + repository layer; add structured logging + metrics; wire Prometheus/OTel optional.
- Step 3: Add auth middleware + role guards; tighten CORS/headers; integrate dependency scans in CI.
- Step 4: Move long-running ops to async tasks; add event outbox and simple job runner; prepare Postgres migration path.
- Step 5: Harden desktop/web builds (codesign hooks, env validation) and finalize observability dashboards.
