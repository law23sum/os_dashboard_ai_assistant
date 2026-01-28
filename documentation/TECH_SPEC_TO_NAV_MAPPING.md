# Tech Spec v6 to Navigation Structure Mapping

**Generated:** 2025-12-21  
**Purpose:** Complete mapping from Technical Spec Sheet v6 sections to GUI navigation structure (Platforms → Categories → Features)

## Relationship Model (CORRECTED)

```
Edition (Personal/Enterprise)
  └─ Platform (ONE) → Categories (MANY)  [ONE-TO-MANY]
       └─ Category (ONE) → Features (MANY)  [ONE-TO-MANY]
            └─ Feature (ONE primary category, can reference others via links)
```

### Key Relationships:
- **Platform → Category**: ONE-TO-MANY (one platform contains many categories)
- **Category → Feature**: ONE-TO-MANY (one category contains many features)
- **Category → Platform**: MANY-TO-ONE (each category belongs to one primary platform)
- **Feature → Category**: MANY-TO-ONE (each feature belongs to one primary category, but similar features may exist in multiple categories with different scopes)

---

## Edition: Personal Workstation Edition

### Platform 1: Mission & Architecture (`/mission`)
**Spec Sections:** 0, 1, 2, 3

#### Category 1.1: Mission & Identity (`/mission/identity`)
**Spec Section:** 0
- `/mission/identity/overview` - Mission, scope, strategic objectives (0.1)
- `/mission/identity/principles` - Design principles, constraints, assumptions & non-goals (0.2)
- `/mission/identity/modes` - Deployment modes (Local, Cloud, Hybrid, Offline-First) (0.3)
- `/mission/identity/actors` - Identity surfaces & actor types (0.4)
- `/mission/identity/roles` - Users, tenants, roles (RBAC/ABAC overview) (0.4)
- `/mission/identity/personas` - Cognitive agents & personas overview (0.5)
- `/mission/identity/daemons` - Daemon families & system roles (0.6)
- `/mission/identity/ai-driver-stack` - AI + driver stack overview (0.7)
- `/mission/identity/model-layer` - Model provider abstraction & model layer (0.8)
- `/mission/identity/glossary` - Terminology & canonical definitions (0.9)
- `/mission/identity/todos` - Open questions / TODOs (0.10)

#### Category 1.2: Architecture & Principles (`/mission/architecture`)
**Spec Section:** 1
- `/mission/architecture/overview` - Logical layered architecture (1.1)
- `/mission/architecture/components` - Major components & interaction patterns (1.2)
- `/mission/architecture/principles` - Architectural principles (1.3)
- `/mission/architecture/mapping` - Component & responsibility mapping (1.4)
- `/mission/architecture/deploy-mapping` - Logical-to-physical mapping (1.5)
- `/mission/architecture/platform-envelope` - Core platform envelope & capability baselines (1.6)
- `/mission/architecture/orchestrator` - Driver-aware orchestrator (1.7)
- `/mission/architecture/modalities` - Interaction modalities (GUI/chat/voice/CLI/API) (1.7.2)
- `/mission/architecture/hitl` - Human-in-the-loop interfaces (1.7.6)
- `/mission/architecture/errors` - Error handling, recovery & explanation standards (1.7.7)
- `/mission/architecture/guardrails` - Safety & guardrail integration (1.7.8)
- `/mission/architecture/todos` - Open questions / TODOs (1.8)

#### Category 1.3: Planes Architecture (`/mission/planes`)
**Spec Section:** 2
- `/mission/planes/overview` - Data, control & governance planes (2.1, 2.2, 2.3)
- `/mission/planes/data` - Data plane (stores, indices, observability) (2.1)
- `/mission/planes/control` - Control plane (orchestration, scheduling, execution) (2.2)
- `/mission/planes/governance` - Governance/policy plane (2.3)
- `/mission/planes/cross-plane` - Cross-plane flows & invariants (2.4)
- `/mission/planes/failure-domains` - Failure domains & isolation boundaries (2.5)
- `/mission/planes/slos` - Plane-specific SLAs/SLOs & scaling patterns (2.6)
- `/mission/planes/todos` - Open questions / TODOs (2.7)

#### Category 1.4: Domain & Knowledge Model (`/mission/domain`)
**Spec Section:** 3
- `/mission/domain/overview` - Domain model overview (3)
- `/mission/domain/identity` - Users/tenants/roles & identity scopes (3.1, 3.2)
- `/mission/domain/projects` - Projects, workspaces, domains & profiles (3.3)
- `/mission/domain/tasks` - Task model (states, priority, ownership) (3.4)
- `/mission/domain/master-stack` - Master Stack & Project Intelligence (3.5)
- `/mission/domain/cir` - CIR (canonical internal representation) (3.6)
- `/mission/domain/ledger` - Project ledger (events, timelines, causal graph) (3.7)
- `/mission/domain/capsules` - Knowledge capsules, packs & capsule graph (3.8)
- `/mission/domain/environments` - Environment blueprints & machine profiles (3.9)
- `/mission/domain/my-stack` - My Stack Capsules & portable skill sharing (3.10)
- `/mission/domain/policies` - Policies, policy packs & governance artifacts (3.11)
- `/mission/domain/billing` - Usage records, cost entities & billing surfaces (3.12)
- `/mission/domain/twins` - Digital Twins, Cognitive Twins, Knowledge Atlas (3.13)
- `/mission/domain/time` - Temporal versioning, drift tracking & reconstruction (3.14)
- `/mission/domain/todos` - Open questions / TODOs (3.15)

---

### Platform 2: Mission Control (`/dashboard`)
**Spec Sections:** 1.7, 7.12

#### Category 2.1: Core Flight Deck (`/dashboard/flight-deck`)
**Spec Section:** 1.7, 7.2
- `/dashboard/flight-deck/overview` - Flight deck overview
- `/dashboard/flight-deck/dashboard` - Dashboard (home)
- `/dashboard/flight-deck/projects` - Projects (7.2)
- `/dashboard/flight-deck/tasks` - Tasks / inbox (3.4)
- `/dashboard/flight-deck/master-stack` - Master Stack (project graph, dependencies) (7.2.1)
- `/dashboard/flight-deck/approvals` - Approvals queue (HITL) (1.7.6)
- `/dashboard/flight-deck/timeline` - Activity timeline (ledger-driven) (3.7)
- `/dashboard/flight-deck/quick-actions` - Quick actions & run launcher
- `/dashboard/flight-deck/status` - System status summary (health/alerts) (11.9)

#### Category 2.2: Engagement & Persona Surfaces (`/dashboard/engagement`)
**Spec Section:** 0.5, 1.7.2
- `/dashboard/engagement/overview` - Engagement overview
- `/dashboard/engagement/chat` - Chat (1.7.2)
- `/dashboard/engagement/voice` - Voice & multimodal (1.7.2)
- `/dashboard/engagement/cli` - CLI / command palette (1.7.2)
- `/dashboard/engagement/collaboration` - Collaboration feed (mentions/comments) (7.12.3)
- `/dashboard/engagement/personalization` - Personalization
- `/dashboard/engagement/search` - Search & discovery (6.5)
- `/dashboard/engagement/explanations` - Plan previews & explanations history (1.7.6)
- `/dashboard/engagement/feedback` - Feedback loop & ratings

#### Category 2.3: Collaboration & Federation (`/dashboard/collaboration`)
**Spec Section:** 7.12
- `/dashboard/collaboration/overview` - Collaboration overview (7.12)
- `/dashboard/collaboration/membership` - Membership, roles & access scopes (7.12.1)
- `/dashboard/collaboration/shared-views` - Shared views & canonical project state (7.12.2)
- `/dashboard/collaboration/comments` - Review, commentary & annotations (7.12.3)
- `/dashboard/collaboration/pipelines` - Draft → review → publish pipelines (7.12.4)
- `/dashboard/collaboration/realtime` - Real-time vs async collaboration models (7.12.5)
- `/dashboard/collaboration/audit` - Ledger & audit integration for multi-user flows (7.12.6)
- `/dashboard/collaboration/run-here` - "Run this project here" wizard (7.12.7)
- `/dashboard/collaboration/my-stack-sharing` - Skills & setup sharing (7.12.8)
- `/dashboard/collaboration/federation` - Cross-tenant federation primitives [Enterprise] (7.12.9)
- `/dashboard/collaboration/todos` - Open questions / TODOs (7.14)

---

### Platform 3: Workspaces (`/workspaces`)
**Spec Section:** 7

#### Category 3.1: Dev & DevOps Workspace (`/workspaces/dev`)
**Spec Section:** 7.3
- `/workspaces/dev/overview` - Workspace overview (7.3)
- `/workspaces/dev/repo` - Repo & code explorer (7.3.1)
- `/workspaces/dev/environment` - Dev environment automation (7.3.3)
- `/workspaces/dev/commit-tasks` - Commit → task generator (7.3.2)
- `/workspaces/dev/merge-advisor` - Code merge advisor (7.3.1)
- `/workspaces/dev/reviews` - PR review & change intelligence
- `/workspaces/dev/cicd` - CI/CD integration (7.3.4)
- `/workspaces/dev/release-evidence` - Release evidence pack (8.17)
- `/workspaces/dev/tools` - Developer tools panel & system execution (7.3.5)
- `/workspaces/dev/sbom` - SBOM & dependency health (10.7.2)
- `/workspaces/dev/runbooks` - Runbooks & one-click dev ops (11.8)
- `/workspaces/dev/todos` - Open questions / TODOs

#### Category 3.2: Research & Simulation Workspace (`/workspaces/research`)
**Spec Section:** 7.4
- `/workspaces/research/overview` - Workspace overview (7.4)
- `/workspaces/research/lab` - Unified research lab (7.4.2)
- `/workspaces/research/data-sources` - Data sources & citation feeds (9.18.4)
- `/workspaces/research/experiments` - Experiment design & planning (7.4.4)
- `/workspaces/research/sweeps` - Parameter sweeps & scheduling (7.4.4)
- `/workspaces/research/simulation` - Simulation workbench (7.4.3)
- `/workspaces/research/cad-multiphysics` - CAD & multiphysics orchestrator (7.4.3, 5.9.2)
- `/workspaces/research/validation` - Model validation & benchmark harness (7.4.5)
- `/workspaces/research/optimization` - Algorithm benchmarking & optimization lab (7.4.9)
- `/workspaces/research/calibration` - Calibration & fitting studio (7.4.8)
- `/workspaces/research/digital-twins` - Digital twin builder & runtime (7.4.6)
- `/workspaces/research/composer` - Cross-domain simulation composer (7.4.7)
- `/workspaces/research/knowledge-graph` - Research knowledge graph & citation engine (7.4.10)
- `/workspaces/research/ip-assistant` - IP discovery & patent/paper drafting (7.4.11)
- `/workspaces/research/hpc` - Advanced lab & HPC orchestrator (7.4.12, 5.9.3)
- `/workspaces/research/training` - Training / curriculum & scenario generator (7.4.13)
- `/workspaces/research/cross-tool` - Cross-tool workspace bridge (7.4.14)
- `/workspaces/research/knowledge-atlas` - Knowledge atlas & simulation bridge (7.4.15)
- `/workspaces/research/todos` - Open questions / TODOs (7.14)

#### Category 3.3: Writer Workspace (`/workspaces/writer`)
**Spec Section:** 7.5
- `/workspaces/writer/overview` - Workspace overview (7.5)
- `/workspaces/writer/workstation` - Writer workstation engine (7.5.1)
- `/workspaces/writer/templates` - Templates & assets
- `/workspaces/writer/canon` - Canon & lore management (7.5.2)
- `/workspaces/writer/narrative` - Narrative guidance engine (7.5.3)
- `/workspaces/writer/drafting` - Drafting studio
- `/workspaces/writer/qa` - Story QA, continuity & consistency checks (7.5.4)
- `/workspaces/writer/collaboration` - Collaboration & review (7.5.5)
- `/workspaces/writer/publishing` - Publication pipeline (7.5.5)
- `/workspaces/writer/production` - Production & export (7.5.6)
- `/workspaces/writer/rights` - AI co-authorship & rights tracking (15.13)
- `/workspaces/writer/todos` - Open questions / TODOs

#### Category 3.4: Cybersecurity Workspace (`/workspaces/cyber`)
**Spec Section:** 7.7, 10.8
- `/workspaces/cyber/overview` - Workspace overview (7.7)
- `/workspaces/cyber/guardian` - Cybersecurity guardian (7.7.1)
- `/workspaces/cyber/assets` - Asset & surface inventory
- `/workspaces/cyber/threat-modeling` - Threat modeling (7.7.3, 10.1)
- `/workspaces/cyber/hardening` - Hardening playbooks & baselines (7.7.3)
- `/workspaces/cyber/findings` - Findings & risk scores (7.7.3, 10.8.2)
- `/workspaces/cyber/auto-remediation` - Security capsules & auto-remediation (7.7.2, 8.13)
- `/workspaces/cyber/incidents` - Incident detection & response (10.9)
- `/workspaces/cyber/forensics` - Forensics & evidence packs (10.9)
- `/workspaces/cyber/compliance` - Compliance mapping (10.4)
- `/workspaces/cyber/todos` - Open questions / TODOs

#### Category 3.5: Business & Finance Workspace (`/workspaces/finance`)
**Spec Section:** 7.8, 15
- `/workspaces/finance/overview` - Workspace overview (7.8)
- `/workspaces/finance/accounting` - Accounting & financing console (7.8.1)
- `/workspaces/finance/budgets` - Budgets & forecasting (7.8.2, 15.3)
- `/workspaces/finance/scenarios` - Strategy & financial scenario simulation (7.8.2)
- `/workspaces/finance/studio` - Scenario studio (7.8.3)
- `/workspaces/finance/cost-governance` - Cost governance (chargeback/showback) (15.5)
- `/workspaces/finance/billing-insights` - Billing & usage insights (15.2)
- `/workspaces/finance/todos` - Open questions / TODOs

#### Category 3.6: Operator & SRE Workspace (`/workspaces/sre`)
**Spec Section:** 7.10, 11, 12
- `/workspaces/sre/overview` - Workspace overview (7.10)
- `/workspaces/sre/health` - Health & drift monitors (7.10.1, 11.8)
- `/workspaces/sre/reliability` - Reliability dashboard (SLOs, error budgets) (12.6)
- `/workspaces/sre/oncall` - Alerting & on-call (11.9)
- `/workspaces/sre/runbooks` - Runbooks & auto-remediation playbooks (7.10.2, 11.8)
- `/workspaces/sre/sandbox` - Sandbox & testbed management (7.10.2, 5.11)
- `/workspaces/sre/capacity` - Capacity planning & benchmarking (12.8)
- `/workspaces/sre/incidents` - Incident management & postmortems (10.9, 14.5)
- `/workspaces/sre/todos` - Open questions / TODOs

#### Category 3.7: Archive & Continuity Workspace (`/workspaces/archive`)
**Spec Section:** 7.6, 6.7, 8.8
- `/workspaces/archive/overview` - Workspace overview (7.6)
- `/workspaces/archive/engine` - Archive / Continuity / Resonance Engine (7.6.1)
- `/workspaces/archive/temporal-reconstruction` - Temporal reconstruction & time-travel (7.6.2, 8.8)
- `/workspaces/archive/snapshots` - Snapshots & retention (6.7)
- `/workspaces/archive/legal-hold` - Legal hold & compliance (6.7)
- `/workspaces/archive/restore` - Restore & export (6.7)
- `/workspaces/archive/todos` - Open questions / TODOs

#### Category 3.8: Record Auditor & Logbook Workspace (`/workspaces/auditor`)
**Spec Section:** 7.9, 11.5, 11.6
- `/workspaces/auditor/overview` - Workspace overview (7.9)
- `/workspaces/auditor/logbook` - Record Auditor & Logbook Engine (7.9.1, 11.5)
- `/workspaces/auditor/evidence` - Evidence trails, compliance & forensics (7.9.2, 11.6)
- `/workspaces/auditor/regulator` - Regulator & auditor views (7.9.3, 10.5)
- `/workspaces/auditor/requests` - Evidence requests & sampling (10.5.2)
- `/workspaces/auditor/reports` - Audit reports & exports (11.7)
- `/workspaces/auditor/timeline` - Timeline & replay (8.8, 11.10)
- `/workspaces/auditor/todos` - Open questions / TODOs

#### Category 3.9: Digital Twin & Enterprise Twin Workspace (`/workspaces/twins`)
**Spec Section:** 7.11, 3.13
- `/workspaces/twins/overview` - Workspace overview (7.11)
- `/workspaces/twins/digital-twin` - Digital Twin Capsule Engine, Builder & Runtime (7.11.1)
- `/workspaces/twins/enterprise` - Agentic Enterprise Twin (7.11.2)
- `/workspaces/twins/reality-mesh` - Reality Twin Mesh (7.11.3)
- `/workspaces/twins/scenarios` - Scenario library & simulation (7.4.3)
- `/workspaces/twins/templates` - Twin templates & blueprints
- `/workspaces/twins/governance` - Twin governance & policies
- `/workspaces/twins/feeds` - Data feeds & sync
- `/workspaces/twins/todos` - Open questions / TODOs

---

### Platform 4: AI Fabric (`/ai`)
**Spec Sections:** 4, 5, 8

#### Category 4.1: Cognitive Agents & Reasoning (`/ai/cognitive`)
**Spec Section:** 4
- `/ai/cognitive/overview` - Cognitive agents overview (4)
- `/ai/cognitive/personas` - Personas as strategy bundles (4.1)
- `/ai/cognitive/aic` - AIC as Meta-Governor (4.2)
- `/ai/cognitive/daemons` - Daemon families & roles (4.3)
- `/ai/cognitive/daemon-runtime` - Daemon runtime, scheduling, scopes (4.4)
- `/ai/cognitive/project-intelligence` - Project Intelligence Subsystem (4.5)
- `/ai/cognitive/trf` - Theoretical Reasoning Framework (4.6)
- `/ai/cognitive/reasoning-time` - Reasoning over time (4.7)
- `/ai/cognitive/traces` - Reasoning traces & explanations (4.8)
- `/ai/cognitive/safety` - Cognitive safety & alignment (4.9)
- `/ai/cognitive/interactions` - Interactions with Driver Fabric (4.10)
- `/ai/cognitive/todos` - Open questions / TODOs (4.11)

#### Category 4.2: Driver Fabric & System Execution (`/ai/drivers`)
**Spec Section:** 5
- `/ai/drivers/overview` - Driver fabric overview (5)
- `/ai/drivers/taxonomy` - Driver taxonomy & design principles (5.1)
- `/ai/drivers/os` - OS Drivers (5.2)
- `/ai/drivers/unix` - Unix / Kernel Execution Layer (5.3)
- `/ai/drivers/package-env` - Package & Environment Management Drivers (5.4)
- `/ai/drivers/hardware` - Hardware Drivers (5.5)
- `/ai/drivers/software-saas` - Software & SaaS Drivers (5.6)
- `/ai/drivers/data` - Data Drivers & Catalogs (5.7)
- `/ai/drivers/workflow` - Workflow Drivers (5.8)
- `/ai/drivers/research-simulation` - Research & Simulation Drivers (5.9)
- `/ai/drivers/governance` - Governance & Policy Drivers (5.10)
- `/ai/drivers/sandbox` - Sandbox & Testbed Spawner (5.11)
- `/ai/drivers/scheduling` - Driver scheduling & prioritization (5.12)
- `/ai/drivers/failure-modes` - Execution-layer failure modes (5.13)
- `/ai/drivers/todos` - Open questions / TODOs (5.14)

#### Category 4.3: Capsules & Workflow Automation (`/ai/capsules`)
**Spec Section:** 8
- `/ai/capsules/overview` - Capsule system overview (8)
- `/ai/capsules/taxonomy` - Capsule taxonomy (8.1)
- `/ai/capsules/structure` - Capsule structure, metadata, tests (8.2)
- `/ai/capsules/manifests` - Capsule manifests & environment specs (8.3)
- `/ai/capsules/lifecycle` - Capsule lifecycle (8.4)
- `/ai/capsules/execution` - Capsule execution engine & sandboxing (8.5)
- `/ai/capsules/dependencies` - Capsule–Driver, Capsule–Workspace dependencies (8.6)
- `/ai/capsules/ledger` - Project Ledger Model (8.7)
- `/ai/capsules/lineage` - Lineage, replay, time-travel (8.8)
- `/ai/capsules/mining` - Knowledge mining & resonance (8.9)
- `/ai/capsules/workflow` - Workflow Engine & orchestration (8.10)
- `/ai/capsules/synthesizer` - Workflow → App Synthesizer (8.11)
- `/ai/capsules/blueprints` - Environment Blueprints & Rebuild (8.12)
- `/ai/capsules/auto-remediation` - Auto-Remediation Playbooks (8.13)
- `/ai/capsules/cli-api` - CLI → API → Service Wrappers (8.14)
- `/ai/capsules/sandbox` - Sandbox & Testbed Spawner (8.15)
- `/ai/capsules/health` - Health & Drift Monitoring (8.16)
- `/ai/capsules/evidence` - Evidence Pack Generator (8.17)
- `/ai/capsules/composer` - Cross-Capsule Composer (8.18)
- `/ai/capsules/operator-studio` - Operator Studio (8.19)
- `/ai/capsules/templates` - Capsule Template Packs (8.20)
- `/ai/capsules/profession-os` - Profession OS Bundles (8.21)
- `/ai/capsules/my-stack` - My Stack Capsules (8.22)
- `/ai/capsules/self-evolving` - Self-Evolving Capsule Ecosystem (8.23)
- `/ai/capsules/governance` - Capsule Governance & Versioning (8.24)
- `/ai/capsules/collaboration` - Multi-User Capsule Collaboration (8.25)
- `/ai/capsules/narrative` - Narrative Capsules & Story Pipelines (8.27)
- `/ai/capsules/todos` - Open questions / TODOs (8.26)

---

### Platform 5: Data & Knowledge (`/data`)
**Spec Section:** 6

#### Category 5.1: Core Data Stores (`/data/stores`)
**Spec Section:** 6.1-6.4
- `/data/stores/overview` - Data stores overview (6)
- `/data/stores/cir` - CIR Store, Document Indexing (6.2)
- `/data/stores/ledger` - Project Ledger Store (6.3)
- `/data/stores/capsules` - Capsule Store, Binary Artifacts (6.4)
- `/data/stores/logical-model` - Logical Storage Model (6.1)

#### Category 5.2: Search & Retrieval (`/data/search`)
**Spec Section:** 6.5
- `/data/search/overview` - Search & retrieval overview (6.5)
- `/data/search/full-text` - Full-Text Search
- `/data/search/semantic` - Semantic/Vector Search
- `/data/search/structured` - Structured Search
- `/data/search/indices` - Index Management

#### Category 5.3: Observability Stores (`/data/observability`)
**Spec Section:** 6.6, 11
- `/data/observability/overview` - Observability stores overview (6.6)
- `/data/observability/metrics` - Metrics Store (11.2)
- `/data/observability/logs` - Logs Store (11.3)
- `/data/observability/traces` - Traces Store (11.4)

#### Category 5.4: Archive & Backup (`/data/archive`)
**Spec Section:** 6.7
- `/data/archive/overview` - Archive & backup overview (6.7)
- `/data/archive/backup` - Backup & Retention
- `/data/archive/legal-hold` - Legal Hold
- `/data/archive/retention` - Retention Policies
- `/data/archive/time-travel` - Time-Travel Surfaces

#### Category 5.5: Multi-Region & Replication (`/data/replication`)
**Spec Section:** 6.8
- `/data/replication/overview` - Multi-region overview (6.8)
- `/data/replication/consistency` - Consistency Models
- `/data/replication/disaster-recovery` - DR for Data

#### Category 5.6: Encryption & Integrity (`/data/security`)
**Spec Section:** 6.9
- `/data/security/overview` - Encryption & integrity overview (6.9)
- `/data/security/encryption` - Data Encryption
- `/data/security/key-management` - Key Management
- `/data/security/integrity` - Integrity Protections

---

### Platform 6: Governance & Security (`/governance`)
**Spec Section:** 10

#### Category 6.1: Policy & Governance Engine (`/governance/policy`)
**Spec Section:** 10.3
- `/governance/policy/overview` - Policy engine overview (10.3)
- `/governance/policy/dsl` - Policy DSL, Models & Evaluation Points (10.3.1)
- `/governance/policy/zero-trust` - Zero-Trust Boundaries (10.3.2)
- `/governance/policy/safety-harness` - Safety Harness Builder (10.3.3)
- `/governance/policy/simulator` - Policy / Governance Sandbox Simulator (10.3.4)

#### Category 6.2: Identity & Access (`/governance/identity`)
**Spec Section:** 10.2
- `/governance/identity/overview` - Identity & access overview (10.2)
- `/governance/identity/users` - Users, Tenants, Roles
- `/governance/identity/rbac-abac` - RBAC/ABAC
- `/governance/identity/sso` - SSO (OIDC/SAML)
- `/governance/identity/apikeys` - API Keys & Tokens

#### Category 6.3: Compliance Packs (`/governance/compliance`)
**Spec Section:** 10.4
- `/governance/compliance/overview` - Compliance packs overview (10.4)
- `/governance/compliance/gdpr` - GDPR
- `/governance/compliance/hipaa` - HIPAA
- `/governance/compliance/sox` - SOX
- `/governance/compliance/pci-dss` - PCI-DSS
- `/governance/compliance/iso27001` - ISO27001
- `/governance/compliance/soc2` - SOC2
- `/governance/compliance/ccpa` - CCPA
- `/governance/compliance/nist` - NIST
- `/governance/compliance/eu-ai-act` - EU AI Act

#### Category 6.4: Regulator Fabric (`/governance/regulator`)
**Spec Section:** 10.5
- `/governance/regulator/overview` - Regulator fabric overview (10.5)
- `/governance/regulator/tenancy` - Regulator & Auditor Tenancy Models (10.5.1)
- `/governance/regulator/evidence-access` - Evidence Access & Sampling (10.5.2)
- `/governance/regulator/apis` - Read-Only Inspection APIs

#### Category 6.5: Data Protection (`/governance/dataprotection`)
**Spec Section:** 10.6
- `/governance/dataprotection/overview` - Data protection overview (10.6)
- `/governance/dataprotection/classification` - Data Classification
- `/governance/dataprotection/residency` - Data Residency
- `/governance/dataprotection/encryption` - Encryption & Keys (10.6.1)
- `/governance/dataprotection/masking` - Data Masking (10.6.2)
- `/governance/dataprotection/tokenization` - Tokenization (10.6.2)

#### Category 6.6: Security Monitoring (`/governance/security`)
**Spec Section:** 10.8, 10.9
- `/governance/security/overview` - Security monitoring overview (10.8)
- `/governance/security/guard-rails` - Cybersecurity Guard Rails (10.8.1)
- `/governance/security/monitor` - Security Monitor & Risk Scores (10.8.2)
- `/governance/security/alignment` - Alignment Monitor (10.8.3)
- `/governance/security/incidents` - Incident Detection & Response (10.9)
- `/governance/security/threat-model` - Threat Model (10.1)

---

### Platform 7: Observability & Evidence (`/observability`)
**Spec Section:** 11

#### Category 7.1: Record Auditor (`/observability/auditor`)
**Spec Section:** 11.5, 11.6
- `/observability/auditor/overview` - Record auditor overview (11.5)
- `/observability/auditor/logbook` - Logbook Engine
- `/observability/auditor/timeline` - Timeline & Causal Graph
- `/observability/auditor/audit-logs` - Audit Log Architecture (11.6)
- `/observability/auditor/retention` - Retention Policies

#### Category 7.2: Evidence Packs (`/observability/evidence`)
**Spec Section:** 11.7
- `/observability/evidence/overview` - Evidence packs overview (11.7)
- `/observability/evidence/generator` - Evidence Pack Generator
- `/observability/evidence/audit-ready` - Audit-Ready Bundles
- `/observability/evidence/export` - Export for Auditors

#### Category 7.3: Metrics & Telemetry (`/observability/metrics`)
**Spec Section:** 11.2, 11.3, 11.4
- `/observability/metrics/overview` - Metrics & telemetry overview (11.2)
- `/observability/metrics/model` - Metrics Model
- `/observability/metrics/logging` - Structured Logging (11.3)
- `/observability/metrics/tracing` - Distributed Tracing (11.4)

#### Category 7.4: Health & Monitoring (`/observability/health`)
**Spec Section:** 11.8, 11.9
- `/observability/health/overview` - Health & monitoring overview (11.8)
- `/observability/health/checks` - Health Checks
- `/observability/health/self-healing` - Self-Healing
- `/observability/health/auto-remediation` - Auto-Remediation Playbooks
- `/observability/health/runbooks` - Runbooks
- `/observability/health/dashboards` - Dashboards & Alerting (11.9)
- `/observability/health/oncall` - On-Call Operations

#### Category 7.5: Temporal Analysis (`/observability/temporal`)
**Spec Section:** 11.10
- `/observability/temporal/overview` - Temporal analysis overview (11.10)
- `/observability/temporal/backtesting` - Temporal Backtesting
- `/observability/temporal/replay` - Replay Engine
- `/observability/temporal/counterfactuals` - Counterfactuals

#### Category 7.6: Integration Points (`/observability/integration`)
**Spec Section:** 11.11-11.15
- `/observability/integration/archive` - Archive / Continuity Integration (11.11)
- `/observability/integration/regulator` - Regulator Fabric Integration (11.12)
- `/observability/integration/hyperdaemon` - HyperDaemon Feeds (11.13)
- `/observability/integration/meta-stack` - Meta-Stack Observability (11.14)

---

### Platform 8: Operations & Infrastructure (`/operations`)
**Spec Sections:** 12, 13, 14

#### Category 8.1: Performance & Scalability (`/operations/performance`)
**Spec Section:** 12
- `/operations/performance/overview` - Performance overview (12)
- `/operations/performance/targets` - Performance Targets & SLAs/SLOs (12.1)
- `/operations/performance/load-profiles` - Load Profiles & Sizing (12.2)
- `/operations/performance/scaling` - Scaling Strategies (12.3)
- `/operations/performance/driver-performance` - Driver Performance (12.4)
- `/operations/performance/backpressure` - Backpressure & Throttling (12.5)
- `/operations/performance/reliability` - Reliability Patterns (12.6)
- `/operations/performance/failure-scenarios` - Failure Scenarios (12.7)
- `/operations/performance/capacity` - Capacity Planning (12.8)
- `/operations/performance/resilience` - Resilience of Unix/System Execution (12.9)
- `/operations/performance/research-workloads` - Research & Simulation Workloads (12.10)

#### Category 8.2: Deployment Models (`/operations/deployment`)
**Spec Section:** 13.1-13.4
- `/operations/deployment/overview` - Deployment models overview (13)
- `/operations/deployment/local` - Local Mode Architecture (13.2)
- `/operations/deployment/cloud` - Cloud / Enterprise Architecture (13.3)
- `/operations/deployment/hybrid` - Hybrid & Edge Architectures (13.4)
- `/operations/deployment/modes` - Deployment Modes Overview (13.1)

#### Category 8.3: Infrastructure Topologies (`/operations/infrastructure`)
**Spec Section:** 13.5-13.8
- `/operations/infrastructure/overview` - Infrastructure overview (13.5)
- `/operations/infrastructure/network` - Network Topology (13.5)
- `/operations/infrastructure/storage` - Storage, Queues, Search Topologies (13.6)
- `/operations/infrastructure/hpc` - HPC & Research Cluster Integration (13.7)
- `/operations/infrastructure/config` - Configuration Management (13.8)

#### Category 8.4: Multi-Region & DR (`/operations/bcdr`)
**Spec Section:** 13.9, 14.6
- `/operations/bcdr/overview` - Multi-region & DR overview (13.9)
- `/operations/bcdr/multi-region` - Multi-Region Deployment (13.9)
- `/operations/bcdr/disaster-recovery` - Disaster Recovery Topologies (14.6)
- `/operations/bcdr/drills` - DR Drills & Exercises

#### Category 8.5: Failure & Risk (`/operations/risk`)
**Spec Section:** 14
- `/operations/risk/overview` - Failure & risk overview (14)
- `/operations/risk/taxonomy` - Failure Taxonomy (14.1)
- `/operations/risk/detection` - Detection Mechanisms (14.2)
- `/operations/risk/recovery` - Recovery Strategies (14.3)
- `/operations/risk/data-loss` - Data Loss & Corruption Protections (14.4)
- `/operations/risk/security-incidents` - Security Incidents (14.5)
- `/operations/risk/business-continuity` - Business Continuity (14.6)
- `/operations/risk/systemic-risk` - Systemic Risk Modeling (14.7)
- `/operations/risk/policy-interplay` - Policy Engine Interplay (14.8)

#### Category 8.6: Upgrade & Migration (`/operations/upgrade`)
**Spec Section:** 13.10
- `/operations/upgrade/overview` - Upgrade & migration overview (13.10)
- `/operations/upgrade/upgrade` - Upgrade Strategy
- `/operations/upgrade/migration` - Migration Strategy
- `/operations/upgrade/backwards-compatibility` - Backwards Compatibility
- `/operations/upgrade/rollback` - Rollback Strategy

---

### Platform 9: Drivers & Integrations (`/drivers`)
**Spec Section:** 5, 9

#### Category 9.1: Driver Registry (`/drivers/registry`)
**Spec Section:** 5.1, 9.4
- `/drivers/registry/overview` - Driver registry overview (5.1)
- `/drivers/registry/management` - Driver Registry & Management
- `/drivers/registry/sdk` - Driver SDK (9.4)
- `/drivers/registry/versioning` - Driver Versioning & Deprecation
- `/drivers/registry/testing` - Driver Testing & Validation

#### Category 9.2: OS & System Drivers (`/drivers/os`)
**Spec Section:** 5.2, 5.3
- `/drivers/os/overview` - OS drivers overview (5.2)
- `/drivers/os/filesystem` - Filesystem Driver
- `/drivers/os/processes` - Processes Driver
- `/drivers/os/windows` - Windows Driver
- `/drivers/os/containers` - Containers Driver
- `/drivers/os/networking` - Networking Driver
- `/drivers/os/unix-execution` - Unix / Kernel Execution Layer (5.3)

#### Category 9.3: Software & SaaS Drivers (`/drivers/integrations`)
**Spec Section:** 5.6, 9.18
- `/drivers/integrations/overview` - Software & SaaS drivers overview (5.6)
- `/drivers/integrations/productivity` - Productivity Suites (9.18.1)
- `/drivers/integrations/code` - Code Hosts & CI/CD (9.18.2)
- `/drivers/integrations/finance` - Finance & Banking (9.18.3)
- `/drivers/integrations/research` - Research Data Sources (9.18.4)
- `/drivers/integrations/legacy` - Legacy & Mainframe (9.18.5)
- `/drivers/integrations/cloud` - Cloud Providers (9.18.6)

#### Category 9.4: Marketplace (`/drivers/marketplace`)
**Spec Section:** 9.6-9.11
- `/drivers/marketplace/overview` - Marketplace overview (9.6)
- `/drivers/marketplace/executable-capsules` - Executable Capsules (9.6)
- `/drivers/marketplace/templates` - Capsule Template Packs (9.7)
- `/drivers/marketplace/driver-packs` - Driver Packs & Vertical Editions (9.8)
- `/drivers/marketplace/enterprise-store` - Enterprise App Store (9.9)
- `/drivers/marketplace/curator` - Marketplace Curator (9.10)
- `/drivers/marketplace/risk` - Third-Party Risk Management (9.11)
- `/drivers/marketplace/reviews` - Reviews & Ratings
- `/drivers/marketplace/security-review` - Security Review Pipeline

---

### Platform 10: Vision & Meta-Stack (`/vision`)
**Spec Section:** 17

#### Category 10.1: Vision Deck Hub (`/vision/vision-deck`)
**Spec Section:** 17
- `/vision/vision-deck/overview` - Vision deck overview
- `/vision/vision-deck/roadmap` - Vision Roadmap
- `/vision/vision-deck/glossary` - Vision Glossary

#### Category 10.2: Core OS Engines (`/vision/core-os`)
**Spec Section:** 17.2
- `/vision/core-os/overview` - Core OS engines overview (17.2)
- `/vision/core-os/master-stack` - Master Stack (17.2.1)
- `/vision/core-os/dev-productivity` - Dev Productivity Envelope (17.2.2)
- `/vision/core-os/research-orchestrator` - Research Orchestrator (17.2.3)
- `/vision/core-os/writer-workstation` - Writer Workstation Engine (17.2.4)
- `/vision/core-os/archive-continuity` - Archive / Continuity Engine (17.2.5)
- `/vision/core-os/cybersecurity` - Cybersecurity Guardian (17.2.6)
- `/vision/core-os/business-accounting` - Business Accounting Console (17.2.7)
- `/vision/core-os/record-auditor` - Record Auditor (17.2.8)
- `/vision/core-os/executable-capsules` - Executable Capsules (17.2.9)
- `/vision/core-os/policy-governance` - Policy & Governance Engine (17.2.10)
- `/vision/core-os/ai-billing` - AI Billing & Usage Fabric (17.2.11)
- `/vision/core-os/matrix` - Capability Matrix

#### Category 10.3: Advanced Capabilities (`/vision/advanced`)
**Spec Section:** 17.3
- `/vision/advanced/overview` - Advanced capabilities overview (17.3)
- `/vision/advanced/research-lab` - Unified Research Lab (17.3.1)
- `/vision/advanced/simulation-workbench` - Simulation Workbench (17.3.2)
- `/vision/advanced/experiment-design` - Experiment Design Engine (17.3.3)
- `/vision/advanced/model-validation` - Model Validation Harness (17.3.4)
- `/vision/advanced/digital-twins` - Digital Twin Engine (17.3.5)
- `/vision/advanced/simulation-composer` - Cross-Domain Simulation Composer (17.3.6)
- `/vision/advanced/calibration` - Model Calibration Studio (17.3.7)
- `/vision/advanced/optimization` - Algorithm Benchmarking Lab (17.3.8)
- `/vision/advanced/knowledge-graph` - Research Knowledge Graph (17.3.9)
- `/vision/advanced/ip-assistant` - IP Discovery Assistant (17.3.10)
- `/vision/advanced/hpc` - Advanced Lab & HPC Orchestrator (17.3.11)
- `/vision/advanced/training` - Training & Curriculum Generator (17.3.12)
- `/vision/advanced/scenario-studio` - Scenario & Strategy Simulation Studio (17.3.13)
- `/vision/advanced/policy-simulator` - Policy Sandbox Simulator (17.3.14)
- `/vision/advanced/cross-tool` - Cross-Tool Research Workspace (17.3.15)
- `/vision/advanced/knowledge-atlas` - Knowledge Atlas (17.3.16)
- `/vision/advanced/matrix` - Capability Matrix

#### Category 10.4: Super Capabilities (`/vision/super`)
**Spec Section:** 17.4
- `/vision/super/overview` - Super capabilities overview (17.4)
- `/vision/super/arc` - Autonomous Research Conductor (17.4.1)
- `/vision/super/trf-super` - Symbolic–Numeric Theory Discovery Engine (17.4.2)
- `/vision/super/self-evolving` - Self-Evolving Capsule Ecosystem (17.4.3)
- `/vision/super/knowledge-market` - Enterprise & Civilization Knowledge Market (17.4.4)
- `/vision/super/enterprise-twin` - Agentic Enterprise Twin (17.4.5)
- `/vision/super/global-policy` - Global Policy & Regulation Fabric (17.4.6)
- `/vision/super/temporal-reasoning` - Temporal Reasoning Engine (17.4.7)
- `/vision/super/knowledge-synthesizer` - Cross-Domain Knowledge Synthesizer (17.4.8)
- `/vision/super/inter-os-network` - Inter-OS Knowledge Network (17.4.9)
- `/vision/super/aic-super` - Autonomous Knowledge Steward (17.4.10)
- `/vision/super/matrix` - Capability Matrix

#### Category 10.5: Hyper Capabilities (`/vision/hyper`)
**Spec Section:** 17.5
- `/vision/hyper/overview` - Hyper capabilities overview (17.5)
- `/vision/hyper/hypermesh` - HyperMesh (17.5.1)
- `/vision/hyper/hyperfoundry` - HyperFoundry (17.5.2)
- `/vision/hyper/hyperlab` - HyperLab (17.5.3)
- `/vision/hyper/hyperregent` - HyperRegent (17.5.4)
- `/vision/hyper/hypersymphony` - HyperSymphony (17.5.5)
- `/vision/hyper/hyperdaemon` - HyperDaemon (17.5.6)
- `/vision/hyper/hypercontinuity` - HyperContinuity (17.5.7)
- `/vision/hyper/hypergenesis` - HyperGenesis (17.5.8)

#### Category 10.6: Ultra Capabilities (`/vision/ultra`)
**Spec Section:** 17.6
- `/vision/ultra/overview` - Ultra capabilities overview (17.6)
- `/vision/ultra/cognitive-twin` - Cognitive Twin Fabric (17.6.1)
- `/vision/ultra/strategy-garden` - Strategy Garden (17.6.2)
- `/vision/ultra/reality-mesh` - Reality Twin Mesh (17.6.3)
- `/vision/ultra/temporal-backtesting` - Temporal Backtesting Engine (17.6.4)
- `/vision/ultra/law-of-os` - Law-of-the-OS & AI Court (17.6.5)
- `/vision/ultra/inter-os-federation` - Inter-OS Federation (17.6.6)
- `/vision/ultra/meta-design` - Meta-Design Studio (17.6.7)
- `/vision/ultra/cognitive-economy` - Cognitive Economy Engine (17.6.8)
- `/vision/ultra/multi-reality` - Multi-Reality Storyboard (17.6.9)
- `/vision/ultra/alignment-monitor` - Alignment Monitor (17.6.10)

#### Category 10.7: Supreme Capabilities (`/vision/supreme`)
**Spec Section:** 17.7
- `/vision/supreme/overview` - Supreme capabilities overview (17.7)
- `/vision/supreme/ontological-compiler` - Ontological Compiler (17.7.1)
- `/vision/supreme/canon-of-truth` - Canon of Truth Engine (17.7.2)
- `/vision/supreme/reality-contract` - Reality Contract Layer (17.7.3)
- `/vision/supreme/co-evolution` - Human–System Co-Evolution Orchestrator (17.7.4)
- `/vision/supreme/successor-architect` - Successor Architect (17.7.5)
- `/vision/supreme/law-of-work` - Unified Law of Work & Meaning Engine (17.7.6)

#### Category 10.8: Ascend Capabilities (`/vision/ascend`)
**Spec Section:** 17.8
- `/vision/ascend/overview` - Ascend capabilities overview (17.8)
- `/vision/ascend/obligation-sentinel` - Realtime Obligation Sentinel (17.8.1)
- `/vision/ascend/breach-detector` - Latent Breach Detector (17.8.2)
- `/vision/ascend/norm-collision` - Norm Collision & Treaty Engine (17.8.3)
- `/vision/ascend/constitutional-policy` - Constitutional Policy VM (17.8.4)
- `/vision/ascend/decision-proof` - Decision-Proof Ledger (17.8.5)
- `/vision/ascend/governance-shell` - Home & Org Governance Shell (17.8.6)

---

### Platform 11: Docs & Spec (`/docs`)
**Spec Section:** 18, 19

#### Category 11.1: Getting Started (`/docs/getting-started`)
- `/docs/getting-started/overview` - Getting started overview
- `/docs/getting-started/quick-start` - Quick Start Guide
- `/docs/getting-started/tutorials` - Tutorials
- `/docs/getting-started/migration` - Migration Guides

#### Category 11.2: Technical Spec (`/docs/spec`)
**Spec Section:** 18
- `/docs/spec/overview` - Technical spec overview (18)
- `/docs/spec/specsheet` - Technical Spec Sheet
- `/docs/spec/canon-mapping` - Canon Mapping (18.1)
- `/docs/spec/capability-index` - Capability → Section Index (18.2)
- `/docs/spec/implementation-anchors` - Implementation Anchors (18.3)
- `/docs/spec/canon-usage` - Canon Usage (18.4)
- `/docs/spec/todo-index` - TODO / Decision Index (18.5)

#### Category 11.3: API Reference (`/docs/api`)
**Spec Section:** 19.10
- `/docs/api/overview` - API reference overview (19.10)
- `/docs/api/model-provider` - Model Provider API (19.10.1)
- `/docs/api/driver-registry` - Driver Registry & Execution APIs (19.10.2)
- `/docs/api/capsule-runtime` - Capsule Runtime APIs (19.10.3)
- `/docs/api/policy-governance` - Policy & Governance APIs (19.10.4)
- `/docs/api/billing-usage` - Billing & Usage Fabric APIs (19.10.5)
- `/docs/api/federation` - Federation Gateway APIs (19.10.6)

#### Category 11.4: Reference Artifacts (`/docs/reference`)
**Spec Section:** 19
- `/docs/reference/overview` - Reference artifacts overview (19)
- `/docs/reference/capsules` - Reference Capsule Manifests (19.1)
- `/docs/reference/drivers` - Reference Driver Manifests (19.2)
- `/docs/reference/policies` - Reference Policy Examples (19.3)
- `/docs/reference/evidence` - Reference Evidence Pack Structures (19.4)
- `/docs/reference/diagrams` - Reference Diagrams (19.5)
- `/docs/reference/glossary` - Glossary (19.6)
- `/docs/reference/changelog` - Changelog (19.7)
- `/docs/reference/user-journeys` - Example User Journeys (19.11)
- `/docs/reference/migration-patterns` - Migration Patterns (19.12)

---

### Platform 12: Roadmap & Risks (`/roadmap`)
**Spec Section:** 16

#### Category 12.1: Future Capabilities (`/roadmap/future`)
**Spec Section:** 16.2, 16.3, 16.7
- `/roadmap/future/overview` - Future capabilities overview (16)
- `/roadmap/future/known-gaps` - Known Gaps for v1 vs vNext (16.2)
- `/roadmap/future/phased-delivery` - Phased Delivery & Milestones (16.3)
- `/roadmap/future/candidate-capabilities` - Candidate Future Capability Lines (16.7)

#### Category 12.2: Risk Register (`/roadmap/risks`)
**Spec Section:** 16.5
- `/roadmap/risks/overview` - Risk register overview (16.5)
- `/roadmap/risks/risk-register` - Risk Register
- `/roadmap/risks/de-risking` - De-Risking Plan
- `/roadmap/risks/validation` - Validation Milestones

#### Category 12.3: Open Questions (`/roadmap/questions`)
**Spec Section:** 16.1, 16.4, 16.8
- `/roadmap/questions/overview` - Open questions overview (16.8)
- `/roadmap/questions/design-decisions` - Cross-Section Design Decisions (16.1)
- `/roadmap/questions/long-term-bets` - Long-Term Bets (16.4)
- `/roadmap/questions/todo-index` - Consolidated TODO Index (16.8)

---

### Platform 13: Settings & Admin (`/settings`)
**Spec Section:** 10.2, 13.8

#### Category 13.1: User Settings (`/settings/user`)
- `/settings/user/overview` - User settings overview
- `/settings/user/profile` - User Profile
- `/settings/user/preferences` - Preferences
- `/settings/user/apikeys` - API Keys & Tokens

#### Category 13.2: System Configuration (`/settings/system`)
**Spec Section:** 13.8
- `/settings/system/overview` - System configuration overview (13.8)
- `/settings/system/config` - Configuration Management
- `/settings/system/secrets` - Secrets & Credential Management
- `/settings/system/upgrades` - Upgrade Channels

---

## Edition: Enterprise Control Plane Add‑Ons

**IMPORTANT:** Enterprise is NOT a separate set of platforms. All platforms are **SHARED** between Personal and Enterprise editions.

**Key Principle (from GUI Structure docs):**
> "Treat Personal vs Enterprise primarily as **edition / capability gating** (feature flags + RBAC), not as two separate IA trees. Use a 'Mode' switch plus conditional nav visibility."

**What Enterprise Adds:**
Enterprise edition adds **additional features and categories** within the same 13 platforms, marked with `[Enterprise]` tags. These are capability extensions, not separate platforms.

### Enterprise-Specific Features (within shared platforms):

#### Within Mission Control Platform:
- `/dashboard/collaboration/federation` - Cross-tenant federation primitives **[Enterprise]**

#### Within Governance & Security Platform:
- `/governance/billing/multi-tenant` - Multi-tenant billing / chargeback **[Enterprise]**
- `/governance/billing/invoicing` - Invoicing & revenue share **[Enterprise]**
- Enterprise-specific compliance packs
- Regulator Fabric (enterprise-grade)
- SCIM Provisioning
- Enterprise SSO/SAML/OIDC

#### Within Drivers & Integrations Platform:
- `/drivers/marketplace/enterprise-store` - Enterprise app store **[Enterprise]**

#### Within Settings & Admin Platform:
- `/settings/tenant` - Tenant & Org Admin **[Enterprise]**
- Multi-tenant configuration
- Enterprise billing & chargeback settings
- Regulator access controls

#### Within Workspaces Platform:
- Enterprise collaboration features
- Multi-tenant project management
- Enterprise twin extensions

**Note:** The "Enterprise Control Plane Add‑Ons" section in the navigation JSON shows the same platforms with enterprise-specific features highlighted, not separate exclusive platforms. Personal users see a subset; Enterprise users see additional features based on RBAC and feature flags.

---

## Summary Statistics

### Personal Workstation Edition:
- **Platforms**: 13 (all platforms are shared)
- **Categories**: 66
- **Features**: ~569 (from merged navigation JSON)
- **Access**: Single-user, offline-first, minimal tenancy

### Enterprise Control Plane Add‑Ons:
- **Platforms**: Same 13 platforms (NOT separate platforms)
- **Additional Categories**: Enterprise-specific categories within shared platforms
- **Additional Features**: Enterprise-specific features marked `[Enterprise]`
- **Access**: Multi-user, multi-tenant, governed execution, compliance, chargeback, federation
- **Key Difference**: Feature flags + RBAC show/hide enterprise features based on edition

### Total Structure:
- **Total Platforms**: 13 (shared between both editions)
- **Total Categories**: 66+ (66 base + enterprise-specific categories)
- **Total Features**: ~569+ (base features + enterprise-specific features)

### Total Web Pages Required:
- **Estimated**: 600+ feature pages
- **Category Home Pages**: 68
- **Platform Landing Pages**: 15

---

## Relationship Validation

✅ **CORRECTED LOGIC:**
1. **Platform → Category**: ONE-TO-MANY ✓
2. **Category → Platform**: MANY-TO-ONE (each category belongs to one primary platform) ✓
3. **Category → Feature**: ONE-TO-MANY ✓
4. **Feature → Category**: MANY-TO-ONE (each feature belongs to one primary category) ✓

📝 **Notes:**
- Some features may conceptually span categories (e.g., 'Projects' appears in multiple contexts)
- Some categories may conceptually span platforms (e.g., 'Collaboration' touches multiple areas)
- In practice, each category/feature is assigned to ONE primary platform/category for navigation
- Cross-references and related items are handled via links, not duplicate entries

---

**Last Updated:** 2025-12-21  
**Based on:** Technical Spec Sheet v6 (1146 lines)

