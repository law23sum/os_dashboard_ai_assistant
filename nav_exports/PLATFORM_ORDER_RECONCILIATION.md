# Platform Order Reconciliation

## Current platform order (from iaManifest)
- Mission Control
- Workspaces
- AI Fabric
- Data & Knowledge
- Drivers & Integrations
- Docs & Spec
- Settings & Admin
- Legacy Recovery
- Mission & Architecture
- Governance & Security
- Observability & Evidence
- Operations & Infrastructure
- Vision & Meta-Stack
- Roadmap & Risks

## Required platform order
- Core
- Common
- Audit Official Records
- Automation
- Settings
- Admin
- Workstation
- Systems
- Simulations
- Research
- Encyclopedia
- Libraries
- Knowledge

## Gaps
- missing_required: Core, Common, Audit Official Records, Automation, Settings, Admin, Workstation, Systems, Simulations, Research, Encyclopedia, Libraries, Knowledge
- extra_current: Mission Control, Workspaces, AI Fabric, Data & Knowledge, Drivers & Integrations, Docs & Spec, Settings & Admin, Legacy Recovery, Mission & Architecture, Governance & Security, Observability & Evidence, Operations & Infrastructure, Vision & Meta-Stack, Roadmap & Risks

## Required changes (no route breaks)
- Add platforms for any missing required labels (new top-level tabs).
- Rename existing platform labels to match required labels where mapping is intended, keeping their `path` unchanged.
- Reorder the platforms array in `frontend/src/data/iaManifest.from_json.ts` to match the required order.
- If splitting a platform (e.g., `Settings & Admin` → `Settings` + `Admin`), keep category `homeRoute` values unchanged and assign categories to the new platform buckets.

## Suggested label mapping (conservative, route-preserving)
- Mission Control → Core
- Workspaces → Workstation
- AI Fabric → Automation
- Drivers & Integrations → Systems
- Governance & Security → Audit Official Records
- Settings & Admin → Settings + Admin (split categories)
- Docs & Spec → Libraries
- Vision & Meta-Stack → Encyclopedia
- Data & Knowledge → Knowledge
- Observability & Evidence → Common or Audit Official Records (choose one to avoid overlap)
- Operations & Infrastructure → Common or Systems (choose one to avoid overlap)
- Mission & Architecture → Common (if not already used)
- Roadmap & Risks → Research or Common (depending on desired placement)

Note: The suggested mapping preserves routes by only changing platform labels and category assignment; adjust as needed for IA intent.