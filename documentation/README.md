# Documentation Index (Spec v6 Aligned)

Start with `documentation/consolidated_md/technical_spec_v6_alignment.md`. It mirrors the Technical Spec Sheet (Version 6 Latest Edition) and routes you to the lower_snake_case canon summaries plus their legacy sources.

---

## Canon Summaries (consolidated_md/)
- `technical_spec_v6_alignment.md` (index; maps spec chapters to sources)
- `00_mission_identity_agents.md`
- `01_architecture_and_planes.md`
- `02_domain_and_reasoning.md`
- `03_driver_execution_layer.md`
- `04_data_and_storage.md`
- `05_workspaces_and_automation.md`
- `06_extensibility_and_security.md`
- `07_observability_and_reliability.md`
- `08_deployment_and_failure.md`
- `09_billing_and_roadmap.md`
- `10_meta_stack_layers.md`
- Diagrams/gaps: `architecture_network_map.md`, `implementation_gaps_and_fixes.md`

## Key Legacy Sources (kept for lineage)
- Vision & mission: `VISION.md`, `VISION_IMPLEMENTATION.md`, `AI_FEATURES_IMPLEMENTATION.md`, `GLOBAL_IMPACT_WHITE_PAPER.md`
- Architecture & principles: `OS_DASHBOARD_CANON_SYSTEM_SPEC.md`, `ARCHITECTURE_IMPLEMENTATION.md`, `OS_DashboardAIAssistantTOC.txt`
- Daemons & governance: `COGNITIVE_DAEMON_SYSTEM.md`, `DAEMON_FRAMEWORK_ARCHITECTURE.md`, `CONVERSATION_AI_INTEGRATION.md`
- Workspaces & migration: `WEB_MIGRATION_PLAN.md`, `UI_MIGRATION_STATUS.md`, `docs/frontend_migration_plan.md`, `workflows/README.md`
- Capsules & CIR: `DOCUMENT_TEMPLATES_AND_AUTOMATION.md`, `DOCUMENT_UPLOAD_DAEMON_INTEGRATION.md`, `CANONICAL_INTERNAL_REPRESENTATION.md`
- Deployment & costing: `DEPLOYMENT.md`, `FRONTEND_DEPLOYMENT.md`, `AWS_COST_ESTIMATE.md`
- Roadmap & gaps: `IMPLEMENTATION_ROADMAP.md`, `MISSING_FEATURES_SUMMARY.md`, `LOW_HANGING_FRUIT_FEATURES.md`, `NEW_FEATURES_ADDED.md`

## Contributing Notes
- Prefer lower_snake_case filenames for any new Markdown (see `consolidated_md/technical_spec_v6_alignment.md` for suggested renames).
- When editing a legacy doc, add a short reference back to the relevant canon chapter so readers can jump between summary and source.
- Keep spec numbering in headings to stay aligned with `Technical Spec Sheet (Version 6 Latest Edition).pdf` and `OS_DashboardAIAssistantTOC.txt`.
