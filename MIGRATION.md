# Naming & Taxonomy Migration (AI OS)

This migration aligns naming, taxonomy, and routing with the 2026-01-03 canon spec. It preserves backward compatibility while establishing AI OS as the primary product naming spine.

## Rename Map (Old → New)
- OS Dashboard AI Assistant → AI OS (product family; first mention may include “AI OS (formerly OS Dashboard AI Assistant)”)
- Overall OS Dashboard AI Assistant Platform → AI OS Platform
- Overall OS Dashboard AI Assistant Platform Envelope → AI OS Core Platform Envelope
- OS Dashboard (UI surface) → AI OS Console
- OS Dashboard AI Assistant (orchestrator component) → AI OS Orchestrator
- Project Management System (PMS) → Intelligence Project Management (IPM)
- Master Stack & Project Management Engine → Master Stack & Intelligence Project Management Engine
- Advanced Research, Simulation & Digital Twin Platform Envelope → AI OS Research, Simulation & Digital Twin Platform Envelope

## API Deprecation Policy
- Primary API: `/api/ipm`
- Legacy alias: `/api/pms` (deprecated)
- Deprecation signal: responses from `/api/pms` include `Deprecation: true`, a `Sunset` date, and a `Warning` header.
- Sunset target: 2026-06-30 (adjust as needed when a formal deprecation schedule is published).

## Legacy Storage Identifiers
- Storage identifiers remain stable to reduce migration risk.
- Examples: `pms_*` tables/collections and `pms`-prefixed event types remain unchanged.
- Public naming is now IPM; internal mapping preserves legacy IDs.

## Taxonomy & Drift Guardrails
- Catalog entries must explicitly declare `artifact_type` and (for capabilities) `capability_layer`.
- Drift checks: run `npm run check:naming-drift` to detect deprecated public names and missing taxonomy metadata.
