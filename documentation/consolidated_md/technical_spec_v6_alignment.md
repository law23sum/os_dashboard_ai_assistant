# Technical Spec v6 Alignment Index

Updated: 2025-02-17  
Sources: `Technical Spec Sheet (Version 6 Latest Version).txt`, `documentation/README.md`, consolidated canon in `documentation/consolidated_md/`.

This index mirrors the spec’s numbering and links each chapter to the canon summaries and primary legacy sources so contributors can navigate quickly.

## Canon Chapters → Summaries
- **0. Mission & Personas** — `00_mission_identity_agents.md`; legacy: `VISION.md`, `COGNITIVE_DAEMON_SYSTEM.md`.
- **1. Architecture & Planes** — `01_architecture_and_planes.md`; legacy: `ARCHITECTURE_IMPLEMENTATION.md`, `OS_DASHBOARD_CANON_SYSTEM_SPEC.md`.
- **2. Domain & Reasoning** — `02_domain_and_reasoning.md`; legacy: `CONVERSATION_AI_INTEGRATION.md`, `AI_FEATURES_IMPLEMENTATION.md`.
- **3. Driver Execution Layer** — `03_driver_execution_layer.md`; legacy: `AUTOMATION_ORCHESTRATION_INTEGRATION.md`, `QUEUE_STACK_MAP.md`.
- **4. Data & Storage** — `04_data_and_storage.md`; legacy: `DOCUMENT_TEMPLATES_AND_AUTOMATION.md`, `CANONICAL_INTERNAL_REPRESENTATION.md`.
- **5. Workspaces & Automation** — `05_workspaces_and_automation.md`; legacy: `WEB_MIGRATION_PLAN.md`, `UI_MIGRATION_STATUS.md`, `DOCUMENT_UPLOAD_IMPLEMENTATION.md`.
- **6. Extensibility & Security** — `06_extensibility_and_security.md`; legacy: `OS_DASHBOARD_ENTERPRISE.md`, `DOCUMENT_UPLOAD_DAEMON_INTEGRATION.md`.
- **7. Observability & Reliability** — `07_observability_and_reliability.md`; legacy: `IMPLEMENTATION_ROADMAP.md`, `FEATURE_OPPORTUNITIES.md`.
- **8. Deployment & Failure Modes** — `08_deployment_and_failure.md`; legacy: `DEPLOYMENT.md`, `ENGINEERING_COMPLEXITY_ANALYSIS.md`.
- **9. Billing & Roadmap** — `09_billing_and_roadmap.md`; legacy: `AWS_COST_ESTIMATE.md`, `GLOBAL_IMPACT_WHITE_PAPER.md`.
- **10. Meta-Stack Layers** — `10_meta_stack_layers.md`; legacy: `OS_DashboardAIAssistantTOC.txt`, `FUTURE_FEATURE_PORTFOLIO.md`.

## Implementation Pointers
- **Observability hooks**: `/runtime/diagnostics`, `/system/memory-thread-plan`, and new workspace health endpoints keep spec §11 visible in UI.
- **Workspace automation**: `assistant_hub.ui.terminal.harness` powers `osdash` and `/api/workspace/*` to satisfy spec §1.7/§4.1 control-plane checks.
- **Docs lineage**: when editing legacy Markdown, add a backlink to the canon chapter above to preserve provenance.

## Known Gaps to Track
- Missing migrations and auth hardening (spec §10).
- CI security scans (gitleaks/semgrep) and load-test scaffolds still pending (spec §12/§15).
- Meta-stack visuals should be refreshed in `architecture_network_map.md` to mirror the new workspace health flows.
