# Naming Taxonomy

This document defines the canonical tier taxonomy for AI OS. Use these tiers for catalog entries, documentation, and UI copy to prevent naming drift.

## Canonical Tier Taxonomy (Highest to Lowest)

1. Product
2. Capability
3. System
4. Platform
5. Service
6. Module
7. Feature
8. Process
9. Pipeline

### Definitions

Product: edition/SKU/bundle/pack mapping to enabled capabilities + constraints (policy profiles, driver packs).

Capability: value-level "what it can do", feature-flagged/packaged, maps to systems/modules/services.

System: bounded domain subsystem with persistent state/invariants and lifecycle.

Platform: shared substrate primitives used by multiple systems; holds invariants.

Service: deployable runtime/API boundary (Enterprise); may compile into modules locally.

Module: pluggable unit referenced by Workspace.enabled_modules.

Feature: fine-grained toggle/behavior (UI/API) behind feature flags.

Process/Pipeline: named workflow/loop/pipeline (often encoded as Capsules/Workflows).

## Catalog Conventions

- Catalog entries must declare a `tier` value from the canonical list above.
- Capability layer (Core/Advanced/Super/Hyper/Ultra/...) remains a separate field for roadmap layering, not taxonomy tier.
- "Fabric" labels are treated as Platform tier in the catalog when they represent shared substrate primitives.
