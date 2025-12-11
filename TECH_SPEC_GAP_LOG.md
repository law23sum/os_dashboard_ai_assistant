# Technical Spec Gap Log

This log tracks the gaps between the canonical specification in `OS DashboardAIAssistantTOC.txt`
and the current implementation. Each entry captures the spec section, the required capability,
the current state, direct evidence inside the repository, and the proposed remediation plan.

## Summary

- **Planes architecture (Spec §2)** is only modeled as thin stubs inside `ai_os/app/planes/`
  and is not wired into FastAPI or the React UI. Data, control, and governance flows still run
  through the same process without isolation, violating the explicit separation mandated by the
  spec.
- **Project ledger + capsule automation (Spec §3.7, §8)** exist only as dataclasses under
  `assistant_core/domain/models.py` and are not persisted or surfaced through the API/UI.
- **Project intelligence + TRF UI (Spec §4.5–§4.8)** were removed from the Tkinter UI and have
  not been rebuilt in React, so personas/AIC cannot expose risk scores, reasoning traces, or
  TRF intents.
- **Driver scheduling & backpressure (Spec §5.12)** are stuck inside the conceptual
  `assistant_core/driver_orchestrator_architecture.py` mock; no runtime code connects driver
  health or priority queues to actual FastAPI endpoints.
- **Observability / governance storage (Spec §6)** never materialized; nothing persists the
  hash-chained ledger, policy packs, or residency metadata.
- **Domain workspaces (Spec §7)** are placeholder React routes without the multi-tool engines,
  CAD/HPC connectors, or digital-twin runtime described in the spec.
- **Collaboration & federation (Spec §7.12)** are missing entirely: there is no user/tenant
  management or shared project state across personas/tenants.

## Gap Inventory

| Spec Section | Capability | Current State | Evidence | Impact | Proposed Fix |
| --- | --- | --- | --- | --- | --- |
| §2.1–§2.3 Planes | Explicit Data / Control / Governance planes with isolation, SLAs, and APIs | Only stubs in `ai_os/app/planes/*.py`; FastAPI launches everything inside a single process without plane boundaries or adapters | `ai_os/app/main.py:179` instantiates `DataPlane`, `ControlPlane`, `GovernancePlane` with in-memory `SimpleDataBackend`, but no callers ever use them | No enforcement of plane-specific invariants, no knobs for policy enforcement or audit separation | Promote plane classes to first-class services (separate modules or processes), register them on FastAPI, and update React to call plane-aware endpoints |
| §3.7 Project Ledger & §8 Capsule System | Immutable ledger + capsule workflow synthesis | Domain models exist but no persistence, API, or UI surfaces; React “Project Ledger” table is a stub that only re-lists project metadata | `assistant_core/domain/models.py:286-381` defines ledger classes; `frontend/src/pages/Projects.tsx:494-567` renders a “Project Ledger” table with project rows instead of ledger events | Canon audit trail is missing, blocking automation review, capsule chaining, and spec compliance | Create a `project_events` table, record events from the tasks/projects routers, expose `/api/projects/ledger`, and render live events in the React Projects view |
| §4.5 Project Intelligence & §4.6–§4.8 TRF UI | Project “brain” health cards, reasoning traces, TRF queries | Tkinter view hooks removed and React never rebuilt equivalents; there is no API returning per-project health or TRF traces | `documentation/root/IMPLEMENTATION_GAPS_AND_FIXES.md` flags Project Intelligence & TRF UI as missing; no `/api/project-intelligence` routes exist | Personas cannot expose health/risk, TRF is invisible, and spec-required governance views are absent | Restore Project Intelligence surface (FastAPI endpoint + React card) first, then add TRF query modal mirroring the Tkinter tooling |
| §5.12 Driver Scheduling / Admission Control | Driver scheduler with backpressure & queue governance | `assistant_core/driver_orchestrator_architecture.py:520-660` contains conceptual planner/fabric classes, but no production code links them to FastAPI, and React never visualizes queues | No prioritization or throttling; automation runs without guardrails | Promote the execution planner + driver registry into the runtime, expose queue metrics over `/api/ai/drivers`, and build an AIOps panel for backpressure |
| §6.3 Project Ledger Store & §6.9 Integrity Protections | Hash-chained ledger persisted with integrity checks | No SQLite table or API for ledger events; no hashing/integrity verification occurs | `assistant_hub_gui/assistant_hub/db.py` lacks ledger tables; `assistant_core/versioning` never references ledger events | Audit chain required by spec cannot be verified | Same remediation as §3.7 plus integrity check endpoints |
| §7.4 Research & Simulation Workspace, §7.11 Digital Twin Workspace | CAD/HPC orchestration, digital twin capsules, environment blueprints | React routes exist (`frontend/src/pages/Research.tsx`, `AdvancedSystems.tsx`), but they only show placeholder cards; there is no backend for HPC connectors or twin capsules | No code implements HPC drivers, CAD integrations, or digital twin renders; search for “digital_twin” returns only enum values | Fails “Advanced Workforce / Digital Twin” deliverables and enterprise use cases | Stand up MVP APIs under `/api/research/*` and `/api/digital-twin/*`, reuse driver layer for simulations, and render results inside the React workspaces |
| §7.12 Collaboration & Federation | Multi-user project membership, tenant roles, shared annotations | No user/tenant tables or APIs; everything assumes a single local owner (“Chris”) | `assistant_hub_gui/assistant_hub/db.py` only stores projects/tasks; routers hard-code owner defaults (e.g., `backend_api/routers/tasks.py:37`) | Cannot satisfy spec requirements for shared workspaces, regulator access, or “Run This Project Here” flows | Add user + tenant tables, expose membership APIs, and surface shared-state indicators in React |

## Implementation Plan

1. **Project Ledger MVP** (in progress): add a durable ledger table, emit events from project/task mutations, and expose `/api/projects/ledger` with hash-chain verification so React can render live audit trails.
2. **Project Intelligence surface**: once the ledger is live, compute health/risk heuristics per project and expose them via FastAPI for the React dashboard.
3. **Planes separation**: refactor the FastAPI startup to register plane adapters (Data/Control/Governance) and proxy all storage & automation calls through the appropriate plane.
4. **Driver scheduler hooks**: promote the driver orchestrator into runtime code, publish queue metrics, and add UI controls for admission control.
5. **Collaboration primitives**: design multi-user tables + APIs and update the UI to select personas/owners per project or task.
