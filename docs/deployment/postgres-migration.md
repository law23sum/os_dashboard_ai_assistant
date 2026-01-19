# SQLite to Postgres Migration Plan

This plan enables safe migration to Postgres and unlocks multi-replica API scaling.

## Pre-Migration Checklist
- Confirm required tables and constraints.
- Agree on a Postgres schema and indexes.
- Establish backup/restore for both SQLite and Postgres.
- Add telemetry for migration parity (row counts, checksums).

## Phase 1: Schema and Access Layer
1. Create SQLAlchemy models (or a repository layer) that cover all tables.
2. Replace direct `sqlite3` usage in API paths with the shared data layer.
3. Add `DATABASE_URL` support and keep SQLite as the default when unset.

## Phase 2: Data Migration
1. Export SQLite data to a neutral format (JSON/CSV).
2. Import into Postgres with validation checks.
3. Compare counts, checksums, and critical query results.

## Backups (Postgres)
Use standard Postgres tooling once `DATABASE_URL` points at Postgres:

```bash
# Backup
pg_dump "$DATABASE_URL" --format=custom --file=osdash.backup

# Restore (drops/recreates objects as needed)
pg_restore --clean --if-exists --dbname="$DATABASE_URL" osdash.backup
```

## Phase 3: Staging Cutover
1. Configure `DATABASE_URL` for staging.
2. Deploy staging using the HA overlay (`k8s/overlays/prod-ha` pattern).
3. Run regression tests and smoke tests.

## Phase 4: Production Cutover
1. Enable Postgres on production with read-only maintenance window.
2. Backfill last changes (if dual-write is not used).
3. Switch `DATABASE_URL` and deploy HA overlay.
4. Monitor error rates, latency, and database health.

## Rollback Strategy
1. Revert `DATABASE_URL` to SQLite.
2. Deploy the standard production overlay (`k8s/overlays/prod`).
3. Restore SQLite data from backups if needed.

## K8s Scaffolding
- Optional Postgres add-on: `k8s/addons/postgres`
- HA overlay: `k8s/overlays/prod-ha`
