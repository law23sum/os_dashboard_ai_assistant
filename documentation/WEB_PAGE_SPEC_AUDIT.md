# Web Page Spec Audit

| Route | Page | Spec refs | I/O coverage | Status |
| --- | --- | --- | --- | --- |
| `/ai/advanced` | AdvancedAI | §4.5–§4.9 | Advanced AI engine controls + capability matrix · 4Q/2M → ai/engine/run, ai/engine/status | ✅ |
| `/ai/autofix` | AutoFix | §5.12 · §8.13 | Auto-remediation scans, issue queue, fix reports, config editor · 4Q/4M → autofix/config (GET/PUT), autofix/issues, autofix/reports, autofix/scan, autofix/status | ✅ |
| `/ai/capsules` | CapsuleMarketplace | §8.18–§9.9 | Capsule/catalog marketplace with install/update flows + blueprint deploys · 4Q/4M → ai/capsules, ai/capsules/{id}/install, ai/capsules/{id}/run, ai/capsules/blueprints/{id}/deploy | ✅ |
| `/ai/copilot` | AICopilot | §4.1–§4.4 · §5.1 | Personas, driver metrics, AI copilots + writer streaming · 10Q/8M → ai/drivers/metrics, ai/drivers/throttle, ai/os/orchestrator, ai/os/status, chat/, operations/, personas, reasoning/history, writer/generate | ✅ |
| `/ai/edge` | EdgeComputing | §5.5 · §7.10 | Edge node telemetry, deployments, model optimization · 3Q/4M → edge-computing/deploy, edge-computing/models, edge-computing/models/optimize, edge-computing/node/manage, edge-computing/status | ✅ |
| `/ai/intents` | IntentProcessor | §1.7.3 | Intent capture list, realtime inference + ledger writes · 4Q/2M → intents, intents?limit=20 | ✅ |
| `/ai/mlops` | MLOps | §5.9.1 · §7.4.5 | Model train/eval/deploy inputs with hyperparameters · 0Q/2M → intelligence/mlops | ✅ |
| `/ai/nas` | NeuralArchitectureSearch | §5.9.3 · §7.4.8 | NAS experiment controls, runs, metrics · 2Q/5M → neural-architecture/nas/configure, neural-architecture/nas/experiment/start, neural-architecture/nas/experiment/stop, neural-architecture/nas/results/view, neural-architecture/nas/status | ✅ |
| `/ai/nas/simulator` | NAS | §5.9.3 · §7.4.8 | Simulator + concept deck for NAS flows · Static parity view (no fetch) | ✅ |
| `/ai/operations` | AIOps | §5.12 · §11.9 | Driver scheduler queue, daemons, reasoning traces per spec · 8Q/3M → ai/drivers/metrics, ai/drivers/throttle, ai/reasoning/run, ai/reasoning/status, ai/reasoning/traces, operations/, operations/summary | ✅ |
| `/ai/os` | AIOS | §2.2 · §5.1 | Orchestrator lifecycle, node health, workflow grid · 4Q/3M → ai/os/orchestrator, ai/os/status, ai/os/workflows/refresh | ✅ |
| `/ai/security` | Security | §10.1–§10.10 | Threat scans, incident queue, evidence exports · 2Q/5M → security/configure, security/event/investigate, security/report/view, security/scan/start, security/status | ✅ |
| `/ai/systems` | AdvancedSystems | §7 · §17 | Parity checklist linking Tkinter futures + React · Static parity view (no fetch) | ✅ |
| `/ai/vision` | ComputerVision | §5.9.1 · §7.4 | CV analysis/ocr/detect pipelines · 2Q/4M → computer-vision/analyze, computer-vision/detect, computer-vision/ocr, computer-vision/stats | ✅ |
| `/ai/workflows` | Workflows | §8.10–§8.16 | Workflow monitor, orchestrator start/stop · 2Q/3M → workflows/monitor, workflows/orchestrator/start, workflows/status | ✅ |
| `/analytics` | Analytics | §11.1–§11.4 | Task/project KPIs, health pills, downloadable reports · 2Q/0M → analytics/report, analytics/summary | ✅ |
| `/audit` | Audit | §11.5–§11.7 | Audit log timelines, evidence pack generator, runbooks · 5Q/2M → audit/checks/run, audit/logs, audit/summary | ✅ |
| `/billing` | Billing | §10.13 · §12.1 | Usage cards + evidence for billing guardrails · 2Q/0M → billing/usage | ✅ |
| `/chat` | Chat | §1.7.2 · §4.1 | Persona-aware chat surface with streaming + evidence context · 4Q/2M → chat/ | ✅ |
| `/collaboration` | Collaboration | §7.12 | Shared state & membership status panel · 2Q/2M → intelligence/collaboration, intelligence/collaboration/state | ✅ |
| `/dashboard` | Dashboard | §1.1–§2.3 · §11.1 | System telemetry, persona load, ledger + control-plane snapshot per mission/planes spec · 6Q/2M → ai/ask, dashboard/stats, personas, projects, search, tasks | ✅ |
| `/docs` | Docs | §18.1–§18.4 | Documentation catalog/search across preserved HTML · Static parity view (no fetch) | ✅ |
| `/docs/:page` | Documentation | §18.3 | Markdown/HTML renderer for doc manifest · Static parity view (fetch) | ✅ |
| `/docs/spec-sheet` | SpecSheet | Spec PDF v6 | Embedded PDF viewer + spec tracker · Static parity view (no fetch) | ✅ |
| `/future/:slug` | FutureDeck | §17 | Future envelopes/backlogs referencing Tk decks · Static parity view (no fetch) | ✅ |
| `/integrations` | Integrations | §9.18 | Connector health, automation toggles, office realtime summaries · 6Q/4M → integrations/summary, office/realtime/ai, office/realtime/summary | ✅ |
| `/integrations/api-connectors` | APIConnectors | §9.18 | Connector overview + action invocations · 4Q/2M → api-connectors/overview | ✅ |
| `/integrations/office` | OfficeRealtime | §7.3 · §9.18.1 | Office connectors, live co-author AI · 4Q/2M → office/realtime/ai, office/realtime/summary | ✅ |
| `/monitoring` | Monitoring | §11.8–§11.10 | Health & drift monitors / auto-remediation toggles · 0Q/2M → intelligence/monitoring | ✅ |
| `/observability` | Observability | §11.1–§11.14 | Planes health, diagnostics feed, uptime/metrics summary · 4Q/0M → planes/status, runtime/diagnostics, system | ✅ |
| `/personalization` | Personalization | §3.5 · §7.1 | Persona/tenant personalization controls · 0Q/2M → intelligence/personalization | ✅ |
| `/projects` | Projects | §3.5–§3.8 · §4.5–§4.8 | Ledger stream, TRF heuristics, reasoning traces for each project · 13Q/6M → projects, projects/intelligence, projects/ledger, projects/links, reasoning/history, reasoning/personas, reasoning/query, tasks | ✅ |
| `/research` | Research | §7.4 | Unified research orchestrator w/ design inputs + simulation snapshots · 0Q/0M → dashboard/stats, research/design, research/run, research/snapshot | ✅ |
| `/search` | SearchEngine | §6.5 | Search status + query interface over CIR/index · 2Q/2M → search/query, search/status | ✅ |
| `/settings` | Settings | §1.7.6 · §10.2 | Theme, persona defaults, governance banners & tenant prefs · Static parity view (no fetch) | ✅ |
| `/tasks` | Tasks | §3.4 · §7.2.2 | Task CRUD, owner/priority flows, kanban metrics · 4Q/4M → tasks | ✅ |
| `/vision` | VisionDeck | §17 | Vision deck reader for future HTML exports · Static parity view (fetch) | ✅ |
| `/work/templates` | Templates | §8.20 · §7.5 | Template gallery, document generators, task presets · 5Q/5M → templates, templates/create-task, templates/documents | ✅ |
| `/work/tools` | Tools | §5.2–§5.4 | Terminal bridge with command catalog + workspace shortcuts · 2Q/2M → terminal, terminal/commands | ✅ |
| `/work/writer` | Writer | §7.5.1–§7.5.5 | Writer workspace: drafts, AI suggestions, doc snapshots · 4Q/5M → writer/documents, writer/generate, writer/snapshot | ✅ |
