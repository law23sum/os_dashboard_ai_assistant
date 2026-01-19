# ADR 0001: Dockerized Environments and Kubernetes Orchestration

Status: Accepted
Date: 2025-12-31

## Context
The project needs repeatable local development, staged environments, and a production-grade runtime. The repo already includes Docker Compose files and a CI pipeline, but Kubernetes manifests were incomplete and not aligned with current services.

## Decision
- Standardize on Docker images for backend (FastAPI + SQLite persistence) and frontend (Vite build served by Nginx).
- Use Kubernetes as the orchestration layer for non-local environments.
- Adopt Kustomize overlays for dev, staging, and prod to manage namespaces, ingress hosts, and resource sizing.
- Add a preview environment per PR for early integration validation.
- Route `/api` to the backend and `/` to the frontend on the same host.
- Deploy to dev on `develop`, to staging on `main`, and to production on release tags.
- Release tags also trigger desktop OS packaging workflows (Windows/macOS/Linux).

## Options Considered
1. Single set of static YAML manifests
   - Rejected: environment drift and lack of promotion strategy.
2. Helm charts
   - Deferred: adds packaging overhead without a current chart ecosystem.
3. Kustomize overlays
   - Accepted: minimal tooling, clear environment diffs, works with kubectl.

## Consequences
- Secrets must be provided before deployment; placeholders should be replaced or managed externally.
- SQLite persistence means the backend runs as a single replica; scaling requires a database migration first.
- Production promotion is tied to release tags, giving an explicit gate before public release.

## Follow-ups
- If object storage grows, introduce S3-compatible storage and update `OBJECT_STORE_PROVIDER`.
- If horizontal scale is required, migrate persistence to Postgres and update the Kubernetes stack accordingly.
