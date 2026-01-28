---
name: databases-engineering
description: Design schemas and write queries for SQL and NoSQL databases. Use for tasks involving database design, migrations, indexing, or query optimization.
---

# Databases Engineering

## Overview
Deliver schema and query changes safely with attention to migrations and performance.

## Quick Start
- Confirm the database type (SQLite, MySQL, Postgres, Redis, MongoDB).
- Identify migration tooling used in the repo.

## Workflow
1. Review schema and data access layer.
2. Draft migrations with rollback paths where possible.
3. Optimize queries with indexes and explain plans.
4. Validate with realistic data sizes.

## Common Tasks
- Add tables, columns, and constraints.
- Create indexes to support query patterns.
- Write safe data backfills.

## Guardrails
- Avoid locking large tables without batching.
- Keep migrations idempotent where possible.
- Document irreversible changes.
