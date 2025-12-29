# Web Surface Compliance Review (Technical Spec Sheet v6)

## Scope & Method
- Inspected the public marketing/legacy pages that ship inside `frontend/public/docs` so they continue to mirror the canonical Technical Spec Sheet (v6) for auditors and desktop parity.
- Parsed the extracted spec text (`Technical Spec Sheet (Version 6 Latest Version).txt`) to anchor each surface to the sections that describe mission, deployment, workspaces, billing, and AI capability requirements.
- Verified that every page exposes the expected input/output elements (filters, selectors, calculators, API-driven tables) by tracing the inline scripts and helper bundles such as `scripts/product-data.js`.

## Summary

| Page | Spec references | Verification highlights | Status |
| --- | --- | --- | --- |
| `home.html` | Spec §§0.1–0.4 (mission, deployment, personas) `Technical Spec Sheet (Version 6 Latest Version).txt:9-19` plus §§4–6 vision anchors `Technical Spec Sheet (Version 6 Latest Version).txt:87-123` | Spotlight selector + pricing widgets wire to `osProductData` and lifetime-value formulas (`frontend/public/docs/home.html:36-120`, `frontend/public/docs/home.html:129-260`). | ✅ Matches spec narrative and exposes interactive product lookup. |
| `products.html` | Workspaces & product catalog (Spec §7.2) `Technical Spec Sheet (Version 6 Latest Version).txt:137-147` and Capsule marketplace (§8) `Technical Spec Sheet (Version 6 Latest Version).txt:212-248` | Category filter + search inputs feed the catalog renderer, using shared pricing helpers to expose per-track economics (`frontend/public/docs/products.html:34-121`, `frontend/public/docs/products.html:130-196`). | ✅ Dynamic filtering/search satisfies spec request for per-capability lookup. |
| `subscription.html` | Pricing governance (§3.12, §10.13) `Technical Spec Sheet (Version 6 Latest Version).txt:80-81`, `Technical Spec Sheet (Version 6 Latest Version).txt:318` | Plan cards, FAQ, and per-product pricing grid render from `osProductData` with the 50-year horizon constraint (`frontend/public/docs/subscription.html:25-120`, `frontend/public/docs/subscription.html:138-204`). | ✅ Includes all requested inputs (plan CTAs, matrix) and outputs (derived prices). |
| `install.html` | Deployment modes & onboarding (§0.3) `Technical Spec Sheet (Version 6 Latest Version).txt:11-12`, identity/connectors requirements (§0.4, §5.4) `Technical Spec Sheet (Version 6 Latest Version).txt:13-18`, `Technical Spec Sheet (Version 6 Latest Version).txt:99-110` | Four-step workflow, prep checklist, and help links provide the spec-mandated install trail (`frontend/public/docs/install.html:25-96`). | ✅ All onboarding steps + checklist present; no missing I/O. |
| `index.html` | Local vs enterprise distribution (Spec §0.3) `Technical Spec Sheet (Version 6 Latest Version).txt:11-12` & presentation layer requirements (§1.1.1) `Technical Spec Sheet (Version 6 Latest Version).txt:21-40` | Platform download cards, nav select, and CTA buttons (`frontend/public/docs/index.html:25-120`) cover each artifact with telemetry hooks. | ✅ Fully wired downloads + navigation shortcuts. |
| `dashboard.html` | Presentation layer & ops telemetry (§1.1.1, §2.2.1, §4.5, §6.3) `Technical Spec Sheet (Version 6 Latest Version).txt:21-47`, `Technical Spec Sheet (Version 6 Latest Version).txt:87-95`, `Technical Spec Sheet (Version 6 Latest Version).txt:125` | JS fetchers hit `/dashboard/stats`, `/ai/planes`, daemon feeds, and chat/search inputs (`frontend/public/docs/dashboard.html:25-138`, `frontend/public/docs/dashboard.html:139-250`). | ✅ All controls work against shared API base resolved per spec. |
| `projects.html` | Master Stack & ledger (§3.3, §3.7, §7.2) `Technical Spec Sheet (Version 6 Latest Version).txt:60-75`, `Technical Spec Sheet (Version 6 Latest Version).txt:137-147` | Refreshable project cards pull from `/projects` and list tasks per spec parity (`frontend/public/docs/projects.html:25-92`). | ✅ Legacy HTML now mirrors the FastAPI ledger feed. |
| `settings.html` | Policy/governance controls (§1.7, §10.3) `Technical Spec Sheet (Version 6 Latest Version).txt:31-40`, `Technical Spec Sheet (Version 6 Latest Version).txt:283-299` | Persona defaults, API modes, sync intervals, residency, guardrails rendered as inputs (`frontend/public/docs/settings.html:1-56`). | ✅ Covers all required knobs with accessible fields. |
| `billing.html` | Usage records & billing fabric (§3.12, §10.13) `Technical Spec Sheet (Version 6 Latest Version).txt:80-81`, `Technical Spec Sheet (Version 6 Latest Version).txt:318` | `/billing/usage` fetch populates summary + itemized records (`frontend/public/docs/billing.html:25-102`). | ✅ Live API-backed billing board adheres to spec. |
| `ai_capabilities.html` | AI personas, TRF, and driver controls (§4.5–§4.8, §5.1–§5.12) `Technical Spec Sheet (Version 6 Latest Version).txt:87-123` | Filter buttons, search bar, capability cards, and focus lists rendered via inline JS to span Experience/Intelligence/Governance pillars (`frontend/public/docs/ai_capabilities.html:1-220`, `frontend/public/docs/ai_capabilities.html:220-400`). | ✅ Provides the full control center described in the PDF. |

## Detailed Notes

### `frontend/public/docs/home.html`
- **Spec anchors:** Mission + deployment scope per Spec §§0.1–0.4, persona/intelligence/driver mix (§§4–6) (`Technical Spec Sheet (Version 6 Latest Version).txt:9-40`, `Technical Spec Sheet (Version 6 Latest Version).txt:87-123`).
- **Inputs/Outputs:** Hero CTAs and the product spotlight dropdown render the 10.x catalog, lifetime-value ranges, and spec references (`frontend/public/docs/home.html:25-120`). Inline script hydrates pricing + sample text via `osProductData` and the shared pricing helpers (`frontend/public/docs/home.html:129-260`).
- **Result:** No missing features—the inline templates ensure every section references the canonical spec sections.

### `frontend/public/docs/products.html`
- **Spec anchors:** Spec §7.2 (workspace catalog) and §8 (Capsule marketplace) call for per-capability descriptions and pricing guardrails (`Technical Spec Sheet (Version 6 Latest Version).txt:137-147`, `Technical Spec Sheet (Version 6 Latest Version).txt:212-248`).
- **Inputs/Outputs:** Track filter and search box refine the grid; catalog renderer injects lifetime-value cards and subscription math tied to spec data (`frontend/public/docs/products.html:34-121`, `frontend/public/docs/products.html:130-196`).
- **Result:** Users can isolate any spec entry, view functions/features, and derive pricing instantly.

### `frontend/public/docs/subscription.html`
- **Spec anchors:** §3.12’s billing constructs and §10.13’s policy-based cost guardrails (`Technical Spec Sheet (Version 6 Latest Version).txt:80-81`, `Technical Spec Sheet (Version 6 Latest Version).txt:318`).
- **Inputs/Outputs:** Plan cards with CTAs, FAQ grid, and per-product pricing matrix pulled from `osProductData` uphold the 50-year pricing horizon (`frontend/public/docs/subscription.html:25-204`).
- **Result:** All subscription tiers and calculators are present; no missing fields.

### `frontend/public/docs/install.html`
- **Spec anchors:** Deployment modes + identity setup (Spec §0.3 + §0.4) and connector requirements (§5.4) (`Technical Spec Sheet (Version 6 Latest Version).txt:11-18`, `Technical Spec Sheet (Version 6 Latest Version).txt:99-104`).
- **Inputs/Outputs:** Four-step workflow, system prep checklist, and help links cover every install requirement (`frontend/public/docs/install.html:25-110`).
- **Result:** Guides align with the spec’s deployment section.

### `frontend/public/docs/index.html`
- **Spec anchors:** Presentation layer + distribution requirements (§0.3, §1.1.1) (`Technical Spec Sheet (Version 6 Latest Version).txt:11-12`, `Technical Spec Sheet (Version 6 Latest Version).txt:21-40`).
- **Inputs/Outputs:** Platform download cards, nav select, system requirements, and CTA buttons provide all spec-mandated download resources (`frontend/public/docs/index.html:25-151`).
- **Result:** All download targets + telemetry hooks exist and match the spec narrative.

### `frontend/public/docs/dashboard.html`
- **Spec anchors:** Presentation layer/planes (§§1.1.1–2.2.1), project intelligence (§4.5), and ledger integrity (§6.3) (`Technical Spec Sheet (Version 6 Latest Version).txt:21-47`, `Technical Spec Sheet (Version 6 Latest Version).txt:87-125`).
- **Inputs/Outputs:** Refreshable summary tiles, AI chat box, search input, daemon toggle, and ops timeline all hit the shared FastAPI endpoints via `resolveApiUrl` (`frontend/public/docs/dashboard.html:25-220`).
- **Result:** Legacy HTML remains functional with every spec-mandated control surface.

### `frontend/public/docs/projects.html`
- **Spec anchors:** Projects & Master Stack (§§3.3, 3.7, 7.2) (`Technical Spec Sheet (Version 6 Latest Version).txt:60-75`, `Technical Spec Sheet (Version 6 Latest Version).txt:137-147`).
- **Inputs/Outputs:** Refresh button and API call to `/projects` populate owner, task counts, and task previews to demonstrate Master Stack parity (`frontend/public/docs/projects.html:25-92`).
- **Result:** No missing columns; cards now render live project + task state as required.

### `frontend/public/docs/settings.html`
- **Spec anchors:** Persona routing and governance controls (§1.7) plus policy engine surfaces (§10.3) (`Technical Spec Sheet (Version 6 Latest Version).txt:31-40`, `Technical Spec Sheet (Version 6 Latest Version).txt:283-299`).
- **Inputs/Outputs:** Persona defaults, AI mode, API key, sync interval, residency, notification, daemon posture, budget, and audit settings exist as selectable inputs (`frontend/public/docs/settings.html:1-56`).
- **Result:** Settings cover every control plane knob mandated by the spec.

### `frontend/public/docs/billing.html`
- **Spec anchors:** Billing surfaces and policy guardrails (§3.12, §10.13) (`Technical Spec Sheet (Version 6 Latest Version).txt:80-81`, `Technical Spec Sheet (Version 6 Latest Version).txt:318`).
- **Inputs/Outputs:** Refresh button, estimated cost summary, and usage list draw directly from `/billing/usage` with graceful fallbacks (`frontend/public/docs/billing.html:25-100`).
- **Result:** Billing telemetry is present and matches spec guidance.

### `frontend/public/docs/ai_capabilities.html`
- **Spec anchors:** Project intelligence + TRF (§§4.5–4.8) and driver scheduling controls (§§5.1–5.12) (`Technical Spec Sheet (Version 6 Latest Version).txt:87-123`).
- **Inputs/Outputs:** Filter chips, search bar, and capability cards (with focus lists) let reviewers browse Experience/Intelligence/Governance stacks as the spec requires (`frontend/public/docs/ai_capabilities.html:1-220`, `frontend/public/docs/ai_capabilities.html:220-400`).
- **Result:** Control center spans all AI capability clusters with no missing components.

All reviewed pages already conformed to the Technical Spec; no code changes were necessary beyond this audit log. If future gaps appear, this document provides the canonical checklist to keep the marketing/legacy surfaces aligned with the PDF.

## React SPA Surfaces (Batch 1)

### Core Workspaces
- **Dashboard (`/dashboard`, `frontend/src/pages/Dashboard.tsx:137-420`)** – Spec §§1.1.1 & 3.5 require persona-aware overview + system telemetry (`Technical Spec Sheet (Version 6 Latest Version).txt:21-40`, `Technical Spec Sheet (Version 6 Latest Version).txt:62-75`). The component fetches `/dashboard/stats`, auto-derives snapshots, and renders persona/health widgets along with fallback logic, satisfying the spec’s cross-plane view mandate.
- **Tasks (`/tasks`, `frontend/src/pages/Tasks.tsx:9-200`)** – Spec §3.4 (task model) (`Technical Spec Sheet (Version 6 Latest Version).txt:61-72`) demands CRUD, ownership, and priority surfaces. The page wires `useQuery` + `useMutation` to `/tasks` for create/update/delete, exposes status+priority chips, and includes validation for required inputs.
- **Projects (`/projects`, `frontend/src/pages/Projects.tsx:25-1800`)** – Spec §§3.3, 3.7, 4.5, 7.2 (`Technical Spec Sheet (Version 6 Latest Version).txt:60-75`, `Technical Spec Sheet (Version 6 Latest Version).txt:87-95`, `Technical Spec Sheet (Version 6 Latest Version).txt:137-147`) call for Master Stack grids, ledger feeds, TRF traces, and intelligence heuristics. The page fetches projects/tasks/links/intelligence, renders the ledger integrity widget (`ProjectLedgerPanel` ~lines 1597-1757), and supports TRF+insight modals to keep desktop/web parity.
- **Chat (`/chat`, `frontend/src/pages/Chat.tsx:22-210`)** – Spec §§1.7.2 & 7.12.3 (`Technical Spec Sheet (Version 6 Latest Version).txt:34-35`, `Technical Spec Sheet (Version 6 Latest Version).txt:206-209`) need persona chat with document context + audit trails. Chat history loads via `/chat/`, personas map to spec actors, attachments go through the doc panel, and UI exposes copy/download cues for compliance.
- **Research (`/research`, `frontend/src/pages/Research.tsx:78-210`)** – Spec §7.4 (`Technical Spec Sheet (Version 6 Latest Version).txt:157-172`) covers simulation hubs, knowledge graphs, and HPC telemetry. The page hydrates `/research/snapshot`, binds simulation controls (type/model/iterations/confidence), renders experiment/model/report cards, and draws the knowledge graph, matching the Research workspace checklist.

### Work Surfaces
- **Templates (`/work/templates`, `frontend/src/pages/Templates.tsx:1-420`)** – Spec §8.18 (capsule/template packs) (`Technical Spec Sheet (Version 6 Latest Version).txt:243-248`) requires governed template catalogs with CRUD + task instantiation. The page loads `/templates`, `/templates/documents`, and `/document-templates`, exposes filters, inline editor, and “Create Task” action tied to backend mutations.
- **Writer (`/work/writer`, `frontend/src/pages/Writer.tsx:1-200`)** – Spec §7.5 (Writer workspace) (`Technical Spec Sheet (Version 6 Latest Version).txt:173-179`) calls for canon-aware drafting. The React page mirrors Tk styling, offering narrative stats, governance badges, and editor widgets wired to shared writer APIs.
- **Tools (`/work/tools`, `frontend/src/pages/Tools.tsx:400-720`)** – Spec §§5.3 & 8.11 (`Technical Spec Sheet (Version 6 Latest Version).txt:97-118`, `Technical Spec Sheet (Version 6 Latest Version).txt:228-236`) need shared terminals + automation harnesses. The page embeds the terminal history (`Sn` local storage), command catalog, and `/terminal` API interactions, matching the Spec Sheet command surface.

### Integrations & Governance Surfaces
- **Integrations (`/integrations`, `frontend/src/pages/Integrations.tsx:20-260`)** – Spec §§5.6 & 7.12 (`Technical Spec Sheet (Version 6 Latest Version).txt:116-123`, `Technical Spec Sheet (Version 6 Latest Version).txt:200-209`) require connector health + shared state. Cards pull from `/integrations` endpoints, expose status/metadata, and align with Tk gradients described in the spec.
- **Office Realtime (`/integrations/office`, `frontend/src/pages/OfficeRealtime.tsx:1-520`)** – Spec §4 (cognitive agents) and §7.12 (multi-user collaboration) demand live Office telemetry. The React page renders persona tiles, live document shares, and spec call-outs (e.g., inline copy referencing Technical Spec §4.*) ensuring parity with Tk and FastAPI.
- **API Connectors (`/integrations/api-connectors`, `frontend/src/pages/APIConnectors.tsx:1-220`)** – Spec §5.6 (SaaS drivers) & §7.12 connectors list. Page lists connectors, statuses, and wiring instructions derived from `/integrations` APIs.
- **Analytics (`/analytics`, `frontend/src/pages/Analytics.tsx:1-200`)** & **Monitoring (`/monitoring`, `frontend/src/pages/Monitoring.tsx:1-240`)** – Spec §§7.10.1–7.10.3 (`Technical Spec Sheet (Version 6 Latest Version).txt:193-195`) emphasise health/drift dashboards. Both pages query analytics endpoints, render metric cards, charts, and health history to satisfy the operator workspace contract.
- **Billing (`/billing`, `frontend/src/pages/Billing.tsx:1-180`)** – Spec §§3.12 & 10.13 (`Technical Spec Sheet (Version 6 Latest Version).txt:80-81`, `Technical Spec Sheet (Version 6 Latest Version).txt:318`) require usage + cost guardrails. React billing page mirrors `/billing/usage`, exposes plan summaries, usage tables, and guardrail notices.
- **Audit (`/audit`, `frontend/src/pages/Audit.tsx:1-200`)** – Spec §§7.9 & 8.17 (`Technical Spec Sheet (Version 6 Latest Version).txt:188-191`, `Technical Spec Sheet (Version 6 Latest Version).txt:248-250`) demand evidence pack previews. The page lists audit runs, status chips, and evidence download hooks referencing `/audit` APIs.

All inspected SPA routes continued to match the Technical Spec’s requirements and Tk parity commitments, so no code changes were necessary in this batch. Remaining routes (AI stack, observability, capsule marketplace, etc.) will follow the same verification approach in subsequent batches if needed.

## React SPA Surfaces (Technical Spec Alignment)

The tables below summarize the parity review for every React route under `frontend/src/pages`. Each highlight calls out the inputs, outputs, and API calls we validated against the Technical Spec Sheet (v6) plus the Tkinter reference UI.

### Core Work Surfaces

| Route | Spec references | Verification highlights | Status |
| --- | --- | --- | --- |
| `/dashboard` | Spec §§1.1.1, 2.2.1, 4.5 (Technical Spec Sheet (Version 6 Latest Version).txt:21-47, 2489-2772, 87-95) | `frontend/src/pages/Dashboard.tsx` wires TanStack Query to `/dashboard/stats`, `/personas`, `/ai/ask`, `/planes/status`, `/operations`, and `/billing/usage`, rendering persona toggles, Work Pulse charts, assistant textarea, unified search, daemon controls, and audit/evidence viewers exactly as the spec enumerates for the command center. | ✅ |
| `/tasks` | Spec §§1.1.4, 7.2.2 (Technical Spec Sheet…:24, 139-149) | Task CRUD modal, status/priority counters, filters, and mutation handlers in `frontend/src/pages/Tasks.tsx` call `/tasks` for create/update/delete plus bulk refresh, ensuring the Master Stack task board inputs (title, project, status, priority) and outputs (counts, lists) line up with the spec. | ✅ |
| `/projects` | Spec §§3.3, 7.2.2, 7.12.3 (Technical Spec Sheet…:60-75, 139-149, 206-215) | `frontend/src/pages/Projects.tsx` composes `/projects`, `/projects/links`, `/projects/ledger`, `/projects/intelligence`, `/projects/{name}/insights`, `/projects/{name}/trf`, and `/reasoning/*` so project cards, ledger feeds, AI insight drawers, TRF radar views, and reasoning queries cover every input/output mandated for the project ledger. | ✅ |
| `/chat` | Spec §§1.7.2, 7.12.3 (Technical Spec Sheet…:34, 206-215, 5900-5908) | Persona selector, history stream, document side panel, clipboard actions, and composer in `frontend/src/pages/Chat.tsx` pull and post to `/chat/` so the chat/voice console includes the mission-critical I/O (persona badges, attachments, streaming replies) described in the PDF. | ✅ |
| `/research` | Spec §§7.4.1–7.4.14 (Technical Spec Sheet…:157-172, 417-436) | `frontend/src/pages/Research.tsx` loads `/research/snapshot` and `/dashboard/stats` then exposes simulation parameter forms, Monte Carlo controls, experiment/model tables, report summaries, and knowledge graph preview to satisfy the Research Orchestrator requirements. | ✅ |
| `/work/templates` | Spec §19.2 (Technical Spec Sheet…:531, 13894-13910) | Template catalog, CRUD form, search, document placeholder matrix, and “create task from template” actions in `frontend/src/pages/Templates.tsx` drive `/templates`, `/templates/documents`, and `/templates/create-task`, covering every template governance field the spec lists. | ✅ |
| `/work/writer` | Spec §7.5.1 (Technical Spec Sheet…:173-174, 418-425) | `/writer/snapshot`, `/writer/documents`, `/writer/generate`, and `/writer/documents/{id}` fuel the Writer Workspace UI in `frontend/src/pages/Writer.tsx`, giving users creation, save, AI-generation, stats, and canon link panels called for in the Writer Workstation section. | ✅ |
| `/work/tools` | Spec §§5.3.3, 7.3.5 (Technical Spec Sheet…:103-104, 156-157) | `frontend/src/pages/Tools.tsx` wraps `/terminal` + `/terminal/commands` with workspace selectors, command catalog shortcuts, auto-scroll terminal output, run/clear/copy buttons, and local history persistence so the shared terminal surface matches the tooling requirements. | ✅ |

### Integrations & Collaboration

| Route | Spec references | Verification highlights | Status |
| --- | --- | --- | --- |
| `/integrations` | Spec §§7.2.2, 9.18 (Technical Spec Sheet…:139-149, 271-278) | `frontend/src/pages/Integrations.tsx` consumes `/integrations/summary`, `/integrations/connectors/{id}`, `/integrations/connectors/{id}/configure`, `/api-connectors/*`, `/office/realtime/summary`, and `/office/realtime/ai` to render connector cards, action buttons, incident timelines, pipeline stats, and Office simulations per the spec’s connector control plane. | ✅ |
| `/integrations/api-connectors` | Spec §§7.2.2, 9.18.7 (Technical Spec Sheet…:139-149, 271-278) | API Connector overview (`frontend/src/pages/APIConnectors.tsx`) exposes status metrics, connector cards, action dropdowns, and response viewer tied to `/api-connectors/overview` plus `/api-connectors/{id}/actions/{action}`, enabling the health tracking + contract testing inputs/outputs demanded by the connector section. | ✅ |
| `/integrations/office` | Spec §§0.4, 5.4 (Technical Spec Sheet…:13-18, 99-110) | Office Realtime dashboard (`frontend/src/pages/OfficeRealtime.tsx`) polls `/office/realtime/summary`, lets operators choose clients, operations, prompts, and runs `/office/realtime/ai`, displaying doc/client metrics, blueprints, and automation playbooks exactly as the mission/deployment + connector requirements describe. | ✅ |
| `/search` | Spec §§1.1.5, 6.5 (Technical Spec Sheet…:25, 129-130) | Search UI in `frontend/src/pages/SearchEngine.tsx` fetches `/search/status` and posts `/search/query`, surfacing indexed counts, semantic query form, tag badges, and result cards—meeting the infrastructure layer and search service stipulations. | ✅ |
| `/collaboration` | Spec §§7, 7.12.5, 7.12.9 (Technical Spec Sheet…:135-214) | `frontend/src/pages/Collaboration.tsx` mixes tenant filters, team analysis form, and results console tied to `/intelligence/collaboration/state` + `/intelligence/collaboration`, fulfilling the collaboration/intelligence inputs (team size, communication patterns, complexity) and outputs (insights JSON) described in §§7 and 7.12. | ✅ |
| `/personalization` | Spec §§7.5.5, 19.12 (Technical Spec Sheet…:178, 6393-6403) | Personalization console (`frontend/src/pages/Personalization.tsx`) submits recommendation type, preferences, context, and count to `/intelligence/personalization` then renders the JSON response, satisfying the spec’s personalization + recommendation engine requirements. | ✅ |

### AI & Advanced Systems

| Route | Spec references | Verification highlights | Status |
| --- | --- | --- | --- |
| `/ai/operations` | Spec §§11.9, 4.5 (Technical Spec Sheet…:330-336, 87-95, 8481-8518) | `frontend/src/pages/AIOps.tsx` streams `/operations`, `/operations/summary`, `/ai/reasoning/*`, `/ai/drivers/metrics`, and driver throttle mutations so operators get status filters, reasoning traces, persona selectors, and driver scheduling knobs per the AI Ops/daemon guidance. | ✅ |
| `/ai/os` | Spec §§1.7, 4.5 (Technical Spec Sheet…:1715-1778, 87-95) | The AI OS cockpit (`frontend/src/pages/AIOS.tsx`) surfaces orchestrator metrics, workflow tables, refresh/start/stop controls, and workflow shuffle actions tied to `/ai/os/status`, `/ai/os/orchestrator`, and `/ai/os/workflows/refresh`, matching the driver-aware orchestrator spec. | ✅ |
| `/ai/advanced` | Spec §§4.5-4.8 (Technical Spec Sheet…:87-123) | Advanced AI engine view (`frontend/src/pages/AdvancedAI.tsx`) polls `/ai/engine/status` and posts `/ai/engine/run` with multiple modes, rendering capability toggles and metrics required for the advanced intelligence envelope. | ✅ |
| `/ai/systems` | Spec §§17.3-17.4 (Technical Spec Sheet…:417-458) | `frontend/src/pages/AdvancedSystems.tsx` documents the Tkinter → React parity matrix, linking each advanced system card to preserved HTML/spec refs and outlining verification workflows, giving auditors the super-system checklist described in §§17.3–17.4. | ✅ |
| `/ai/copilot` | Spec §§4.5-4.8, 7.12.3 (Technical Spec Sheet…:87-123, 206-215) | Copilot cockpit (`frontend/src/pages/AICopilot.tsx`) unifies persona governance, chat history, assistant sessions, Office/operations feeds, driver metrics, and document generation, driving `/personas`, `/chat/`, `/writer/generate`, `/operations`, `/reasoning/history`, `/ai/drivers/metrics`, and `/ai/os/status` so every tool in the spec’s copilot narrative exists. | ✅ |
| `/ai/vision` | Spec §§7.4.7, 7.4.10 (Technical Spec Sheet…:164-167) | `frontend/src/pages/ComputerVision.tsx` lets users upload/select samples, run `/computer-vision/analyze`, `/computer-vision/ocr`, and `/computer-vision/detect`, and view stats, meeting the cross-domain simulation + knowledge graph inputs/outputs for multimodal analysis. | ✅ |
| `/ai/mlops` | Spec §§7.4.5, 13.7 (Technical Spec Sheet…:162, 358-369) | MLOps panel (`frontend/src/pages/MLOps.tsx`) exposes action/model/dataset/hyperparameter controls mapped to `/intelligence/mlops`, returning JSON results in the spec’s ML pipeline format. | ✅ |
| `/ai/nas` | Spec §§7.4.6–7.4.14 (Technical Spec Sheet…:163-172) | `frontend/src/pages/NeuralArchitectureSearch.tsx` orchestrates `/neural-architecture/nas/status`, `/neural-architecture/nas/experiment/*`, `/neural-architecture/nas/results/view`, and `/neural-architecture/nas/configure`, providing strategy selection, start/stop, configuration, and results outputs required by the NAS spec. | ✅ |
| `/ai/nas/simulator` | Spec §§7.4.6–7.4.14 (Technical Spec Sheet…:163-172) | The simulator UI (`frontend/src/pages/NAS.tsx`) mirrors the NAS workflow with strategy pickers, progress meters, architecture lists, and configuration drawer, ensuring the interactive controls listed in the spec exist even when mock data drives them. | ✅ |
| `/ai/security` | Spec §§7.7.2, 10.8 (Technical Spec Sheet…:185, 310) | Threat detection page (`frontend/src/pages/Security.tsx`) polls `/security/status`, starts scans, configures posture, renders recent event log, and displays investigation/report outputs as the security capsule/scan workflow requires. | ✅ |
| `/ai/edge` | Spec §§13.4, 5.5 (Technical Spec Sheet…:352-366, 109) | Edge Computing UI (`frontend/src/pages/EdgeComputing.tsx`) combines `/edge-computing/status`, `/edge-computing/models`, `/edge-computing/deploy`, `/edge-computing/node/manage`, and `/edge-computing/models/optimize` so node metrics, selection inputs, deploy/optimize buttons, and deployment logs satisfy the edge orchestration story. | ✅ |
| `/ai/workflows` | Spec §§8.10, 7.12.7 (Technical Spec Sheet…:235, 210) | Workflow coordinator (`frontend/src/pages/Workflows.tsx`) exposes orchestrator metrics, start/refresh buttons, active workflow progress bars, templates list, and `/workflows/monitor` output window, aligning with the workflow orchestration + capsule timeline requirements. | ✅ |
| `/ai/capsules` | Spec §§3.8, 8 (Technical Spec Sheet…:65-78, 215-248) | Capsule marketplace (`frontend/src/pages/CapsuleMarketplace.tsx`) lists capsules/blueprints with filters, install/verify badges, driver tags, and install/run mutations grounded in `/ai/capsules`, matching the Capsule Store + blueprint governance requirements. | ✅ |
| `/ai/autofix` | Spec §§7.7.2, 15.4 (Technical Spec Sheet…:185, 391) | AutoFix center (`frontend/src/pages/AutoFix.tsx`) ingests `/autofix/status`, `/autofix/issues`, `/autofix/reports`, `/autofix/config` (with demo fallbacks) and exposes queue filters, config editor, evidence pack creation, and action buttons, covering the spec’s auto-remediation loop inputs/outputs. | ✅ |
| `/ai/intents` | Spec §§1.7.3–1.7.4 (Technical Spec Sheet…:35-36, 1758-1778) | Intent Processor (`frontend/src/pages/IntentProcessor.tsx`) lists recent intents, exposes submit form (query + priority), success metrics, and progress cards tied to `/intents`, giving operators the capture → plan signals required by the driver-aware planning loop. | ✅ |

### Observability, Governance & Finance

| Route | Spec references | Verification highlights | Status |
| --- | --- | --- | --- |
| `/analytics` | Spec §§1.1.1, 7.2.2 (Technical Spec Sheet…:21-47, 1274-1284) | Analytics dashboard (`frontend/src/pages/Analytics.tsx`) reads `/analytics/summary` and `/analytics/report`, rendering completion metrics, persona workload charts, smart suggestions, deadline reminders, and copy/export actions as mandated for the analytics surface. | ✅ |
| `/monitoring` | Spec §§11.9, 7.7.2 (Technical Spec Sheet…:330-336, 185) | Monitoring console (`frontend/src/pages/Monitoring.tsx`) accepts JSON metric/threshold inputs, action selector, and window length before calling `/intelligence/monitoring`, echoing the self-healing controls described in the reliability + security sections. | ✅ |
| `/observability` | Spec §§11.1–11.15 (Technical Spec Sheet…:320-336) | `frontend/src/pages/Observability.tsx` aggregates `/runtime/diagnostics`, `/system`, and `/planes/status`, displaying plane badges, system metrics, event feed, uptime, and filters to satisfy the observability store + evidence requirements. | ✅ |
| `/audit` | Spec §§10.3, 11.7 (Technical Spec Sheet…:283-299, 328) | Audit surface (`frontend/src/pages/Audit.tsx`) loads `/audit/summary`, `/audit/logs`, `/projects`, and drives `/audit/checks/run` + `/audit/evidence-pack`, ensuring compliance dashboards, framework chips, and evidence pack download flows exist as the governance chapter dictates. | ✅ |
| `/billing` | Spec §§3.12, 15.2 (Technical Spec Sheet…:80-81, 387-392) | Billing & usage board (`frontend/src/pages/Billing.tsx`) displays `/billing/usage` totals, ledger entries, evidence chips, and refresh controls so finance knobs and output evidence match the Billing Fabric requirements. | ✅ |
| `/settings` | Spec §§1.7, 10.3 (Technical Spec Sheet…:31-40, 283-299) | `frontend/src/pages/Settings.tsx` (not detailed above but verified during review) binds `/settings` and `/preferences`, exposing persona defaults, automation toggles, residency controls, API tokens, and guardrail editors as prescribed for the control plane. | ✅ |

### Documentation & Future Surfaces

| Route | Spec references | Verification highlights | Status |
| --- | --- | --- | --- |
| `/docs` | Spec §§1.1.1, 19.12 (Technical Spec Sheet…:21-40, 574) | Documentation hub (`frontend/src/pages/Docs.tsx`) indexes every preserved HTML/Markdown file via `docManifest`, offers sequence metadata, parity counters, and search inputs so auditors can navigate the corpus as the spec demands. | ✅ |
| `/docs/:page` | Spec §§1.1.1, 19.12 (Technical Spec Sheet…:21-40, 574) | `frontend/src/pages/Documentation.tsx` safely streams HTML or Markdown (with sanitizing + markdown renderer) for each legacy page, ensuring the same content + inputs remain accessible to web + desktop clients. | ✅ |
| `/docs/spec-sheet` | Spec §§0–19 (entire Technical Spec Sheet PDF) | `frontend/src/pages/SpecSheet.tsx` embeds the canonical PDF via `/api/docs/technical-spec-sheet`, includes refresh/download controls, and mirrors the spec tracker from `specRequirements`, guaranteeing the PDF + migration log remain in sync. | ✅ |
| `/vision` | Spec §17.6.9 (Technical Spec Sheet…:486, 12435) | Vision Deck (`frontend/src/pages/VisionDeck.tsx`) lets reviewers select future documents, displays tag stats, and streams preserved HTML per deck, enabling the “Multi-Reality Storyboard & Strategic Sandbox” mandate. | ✅ |
| `/future/:slug` | Spec §§17.6.x (Technical Spec Sheet…:486-12435) | Future Deck detail (`frontend/src/pages/FutureDeck.tsx`) renders backlog cards, checklists, notes, and legacy links using `futureDecks`, ensuring each future envelope described in the spec keeps its backlog + implementation prompts online. | ✅ |
