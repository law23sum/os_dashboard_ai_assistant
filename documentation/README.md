# Documentation Index

This folder centralizes the reference material for the OS Dashboard AI Assistant Platform. The **canonical ordering** now mirrors `OS DashboardAIAssistantTOC.txt`: every section below references the spec chapter, the key Markdown(s), and the runtime surfaces that satisfy it. Use this page alongside `documentation/OS_DashboardAIAssistantTOC.md` when you need to trace an implementation back to the canon.

---

## 0 — Mission, Modes, Identity & Cognitive Agents
- Vision & mission: `VISION.md`, `VISION_IMPLEMENTATION.md`, `GLOBAL_IMPACT_WHITE_PAPER.md`
- Operating models & objectives: `OS_DASHBOARD_ENTERPRISE.md`, `IMPLEMENTATION_SUMMARY.md`, `ENGINEERING_COMPLEXITY_ANALYSIS.md`
- Personas & daemons narrative: `AI_FEATURES_IMPLEMENTATION.md`, `DAEMON_FRAMEWORK_ARCHITECTURE.md`
- Roadmaps / deltas: `IMPLEMENTATION_ROADMAP.md`, `LOW_HANGING_FRUIT_FEATURES.md`, `FEATURE_OPPORTUNITIES.md`, `MISSING_FEATURES_SUMMARY.md`, `NEW_FEATURES_ADDED.md`

## 1 — Architectural Overview & Principles
- Canon spec + layered architecture: `OS_DASHBOARD_CANON_SYSTEM_SPEC.md`, `ARCHITECTURE_IMPLEMENTATION.md`
- Driver-aware orchestrator + automation flow: `AUTOMATION_ORCHESTRATION_INTEGRATION.md`, `assistant_hub/ARCHITECTURE.md`
- Presentation & migration blueprint: `WEB_MIGRATION_PLAN.md`, `FRONTEND_DEPLOYMENT.md` (React desktop), `docs/frontend_migration_plan.md`

## 2 — Planes Architecture (Data / Control / Governance)
- Planes and control-loop insights: `AI_OFFICE_AGENT_REALTIME.md`, `COGNITIVE_DAEMON_SYSTEM.md`
- Policy layer & governance guardrails: `CONVERSATION_AI_INTEGRATION.md`, `documentation/reference/os-dashboard-ai-assistant-platform/CHANGELOG.md` (policy history)

## 3 — Core Domain & Knowledge Model
- CIR & document taxonomy: `CANONICAL_INTERNAL_REPRESENTATION.md`, `DOCUMENT_TEMPLATES_AND_AUTOMATION.md`
- Task/project ledger: `DOCUMENT_UPLOAD_DESIGN.md`, `DOCUMENT_UPLOAD_IMPLEMENTATION.md`
- Knowledge capsules & workspace stories: `DOCUMENT_UPLOAD_DAEMON_INTEGRATION.md`, `DOCUMENT_UPLOAD_DESIGN.md`, `DOCUMENT_UPLOAD_IMPLEMENTATION.md`

## 4 — Cognitive Agents, Reasoning & Daemon Framework
- Cognitive framework + personas: `AI_FEATURES_IMPLEMENTATION.md`, `COGNITIVE_DAEMON_SYSTEM.md`
- Daemon runtime & automation controller: `DAEMON_FRAMEWORK_ARCHITECTURE.md`, `assistant_hub_gui/assistant_hub/ARCHITECTURE.md`
- Research & reasoning overlays: `api_research.md`, `WEB_MIGRATION_PLAN.md` (desktop research workspace)

## 5 — Driver Architecture & System Execution Layer
- OS / SaaS driver specs: `ARCHITECTURE_IMPLEMENTATION.md` (Section 5), `assistant_hub/ARCHITECTURE.md`
- Git/Office integrations & automation capsules: `ONEDRIVE_INTEGRATION.md`, `FILE_TASK_EXTRACTION_FEATURE.md`, `assistant_hub_gui/samples/*.md`

## 6 — Data & Storage Architecture
- Data stores & observability: `AWS_COST_ESTIMATE.md`, `DEPLOYMENT.md`, `AI_OFFICE_AGENT_REALTIME.md` (telemetry)
- Config references & samples: `config/samples/*.md`, `assistant_hub_gui/samples/*.md`

## 7 — Workspaces, Domain Engines & Collaboration
- Workspace engines & workflows: `workflows/README.md`, `assistant_hub_gui/assistant_hub/ARCHITECTURE.md`
- Writer / Research / DevOS overlays: `api_research.md`, `documentation/reference/os-dashboard-ai-assistant-platform/README.md`
- Migration tracker (Tk → React parity): `UI_MIGRATION_STATUS.md`

## 8 — Capsule System, Ledger & Automation
- Capsules & release packets: `DOCUMENT_TEMPLATES_AND_AUTOMATION.md`, `DOCUMENT_UPLOAD_DAEMON_INTEGRATION.md`
- Automation guidance & CLI surface: `commands.md`, `assistant_hub/ARCHITECTURE.md`

## 9+ — Deployment, Ops & Testing (Supporting Appendices)
- Deployment & costing: `DEPLOYMENT.md`, `AWS_COST_ESTIMATE.md`, `docs/ui_deployment.md`
- Test & verification references: `documentation/.pytest_cache/README.md` (placeholder until pytest suite expands)
- Reference libraries: `documentation/reference/**`

Every new Markdown or implementation note should declare the spec section(s) it fulfills and be linked from the appropriate numbered list above. This keeps the documentation synchronized with `OS_DashboardAIAssistantTOC.md`, ensures newcomers can find the canonical artifact quickly, and satisfies the “read-all-MDs and reorganize per TOC” directive from the Canon specification.
