# ADR 0002: Migrate Persistence from SQLite to Postgres

Status: Proposed
Date: 2025-12-31

## Context
SQLite is a single-writer database and limits horizontal scaling for the API.
As we move toward multi-replica deployments, we need a server-grade database.

## Decision
Adopt Postgres as the primary persistence layer for production and staging.
Keep SQLite for local development and lightweight demos.

## Plan (Phased)
1. **Inventory + schema map**
   - Catalog all tables and sqlite-specific queries.
   - Define a Postgres schema (types, indexes, constraints).
2. **Data access layer**
   - Introduce a DB abstraction (SQLAlchemy or repository layer).
   - Keep API handlers stable while swapping storage.
3. **Dual-write (optional but recommended)**
   - Write to both SQLite and Postgres for a short window.
   - Validate parity with nightly checks.
4. **Backfill + cutover**
   - Migrate historical data to Postgres.
   - Flip `DATABASE_URL` to Postgres in staging, then prod.
5. **Deprecate SQLite in production**
   - Retain SQLite only for local/dev.

## Consequences
- Enables multi-replica backends and HPA.
- Requires migration tooling and a rollback path.
- Adds operational dependencies (backups, monitoring, migrations).

## Rollback
If Postgres cutover fails, revert `DATABASE_URL` to SQLite and disable HA overlays.
