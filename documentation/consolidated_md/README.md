# Consolidated Canon (Spec v6 Aligned)

This folder is the **canonical, lower_snake_case** index for every Markdown that supports the Technical Spec Sheet (Version 6 Latest Edition). Each file below consolidates the scattered notes in `documentation/` into spec-shaped chapters so contributors can land on the right surface without trawling dozens of legacy docs.

Use `technical_spec_v6_alignment.md` as the entry point. It mirrors the spec’s numbering and links to the chapter summaries here plus the underlying source notes (kept in `documentation/` for provenance).

---

## Canon Files (lower_snake_case)
- `technical_spec_v6_alignment.md` — chapter index + source mapping.
- `architecture_network_map.md` — end-to-end swim-lanes across UI → orchestrator → drivers → daemons (supersedes legacy diagram notes).
- `implementation_gaps_and_fixes.md` — current gaps, remediation tracks, and owners.
- `00_mission_identity_agents.md` — mission, modes, identity surfaces, personas, daemon families.
- `01_architecture_and_planes.md` — layered architecture plus data/control/governance plane responsibilities.
- `02_domain_and_reasoning.md` — core domain objects, knowledge model, cognitive framework, and daemon scaffolding.
- `03_driver_execution_layer.md` — driver taxonomy, orchestration contracts, safety hooks.
- `04_data_and_storage.md` — CIR, indices, ledger, storage envelopes, and encryption views.
- `05_workspaces_and_automation.md` — workspace engines, capsules, ledger, workflow synthesis.
- `06_extensibility_and_security.md` — plugin/pack ecosystem, marketplace, governance, policy, regulator fabric.
- `07_observability_and_reliability.md` — telemetry, audit/evidence, performance, scale, and reliability baselines.
- `08_deployment_and_failure.md` — deployment topologies, migration/rollback, failure taxonomies, recovery playbooks.
- `09_billing_and_roadmap.md` — billing fabric, cost guardrails, roadmap, risks, and spec maintenance.
- `10_meta_stack_layers.md` — Core → Advanced → Hyper layers with cross-layer invariants.

---

## Source Intake
- **Technical Spec Sheet (Version 6 Latest Edition).pdf** and `OS DashboardAIAssistantTOC.txt` drive the structure.
- Legacy Markdown inputs live in `documentation/` (mission, architecture, daemons, deployment, migration, etc.). Where possible, the canon chapters reference the most relevant legacy files so you can deep-dive without losing lineage.
- If you add or rename legacy files, update `technical_spec_v6_alignment.md` so the spec-to-source mapping stays accurate.
