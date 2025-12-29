export type GuidancePersona = 'Chris' | 'Aria' | 'Sora' | 'AIC'

export interface GuidanceStep {
  title: string
  detail: string
}

export type GuidanceQuickAction =
  | { type: 'navigate'; label: string; description?: string; route: string }
  | { type: 'link'; label: string; description?: string; href: string }
  | { type: 'prompt'; label: string; description?: string; prompt: string }

export interface AIGuidanceEntry {
  id: string
  routes: string[]
  persona: GuidancePersona
  title: string
  summary: string
  specAnchors: string[]
  tutorialSteps: GuidanceStep[]
  recommendations: GuidanceQuickAction[]
  cues: string[]
}

const wildcardMatch = (pattern: string, pathname: string): boolean => {
  if (pattern === '*') return true
  if (pattern.endsWith('*')) {
    const base = pattern.slice(0, -1)
    return pathname.startsWith(base)
  }
  return pathname === pattern
}

export const aiGuidanceEntries: AIGuidanceEntry[] = [
  {
    id: 'dashboard',
    routes: ['/', '/dashboard'],
    persona: 'AIC',
    title: 'Mission Control Overview',
    summary: 'AIC monitors the composite health of projects, personas, and daemons so you can make a call within 30 seconds.',
    specAnchors: ['Spec §1.1 Presentation Layer', 'Spec §1.7 Driver-Aware Loop', 'Spec §7.12 Collaboration'],
    tutorialSteps: [
      { title: 'Scan telemetry', detail: 'Validate CPU, memory, and security banners before delegating.' },
      { title: 'Balance personas', detail: 'Use persona load tiles to redistribute work or activate a daemon.' },
      { title: 'Launch intent', detail: 'Trigger a quick assistant prompt or jump into Tasks/Projects via shortcuts.' },
    ],
    recommendations: [
      { type: 'navigate', label: 'Jump to Tasks', description: 'Open prioritized backlog', route: '/tasks' },
      {
        type: 'prompt',
        label: 'AIC status brief',
        description: 'Copy into Chat to synthesize context',
        prompt: 'AIC, summarize the operational dashboard and tell me which project needs human attention next.',
      },
      { type: 'link', label: 'Spec excerpt', description: 'Review §1.7 orchestration notes', href: '/docs/spec-sheet#page=3' },
    ],
    cues: ['System posture', 'Persona load', 'Intent pipeline'],
  },
  {
    id: 'tasks',
    routes: ['/tasks'],
    persona: 'Aria',
    title: 'Task Orchestration Coach',
    summary: 'Aria triages statuses, bulk updates, and template alignment for the Master Stack worklist.',
    specAnchors: ['Spec §1.1.4 Domain Layer', 'Spec §7.2.2 Master Stack'],
    tutorialSteps: [
      { title: 'Review status mix', detail: 'Check the TODO/IN PROGRESS ratios and unblock anything stuck.' },
      { title: 'Apply templates', detail: 'Use task templates for repetitive work before creating one-offs.' },
      { title: 'Sync owners', detail: 'Ensure persona owners align with project priorities.' },
    ],
    recommendations: [
      { type: 'navigate', label: 'Open Templates', description: 'Leverage repeatable playbooks', route: '/work/templates' },
      {
        type: 'prompt',
        label: 'Bulk status prompt',
        description: 'Paste into Chat to resolve or escalate tasks',
        prompt: 'Aria, review the current tasks board and propose status updates plus owners for anything blocked more than 2 days.',
      },
      { type: 'link', label: 'Task Spec Notes', href: '/docs/migration_continued.md' },
    ],
    cues: ['Status mix', 'Template coverage', 'Owner load'],
  },
  {
    id: 'projects',
    routes: ['/projects', '/projects/*'],
    persona: 'Sora',
    title: 'Project Intelligence Surface',
    summary: 'Sora keeps the ledger, TRF traces, and capsule hooks synchronized for every initiative.',
    specAnchors: ['Spec §3.3 Projects & Workspaces', 'Spec §4.5 Project Intelligence'],
    tutorialSteps: [
      { title: 'Inspect ledger events', detail: 'Ensure commits, incidents, and approvals form an unbroken chain.' },
      { title: 'Open TRF traces', detail: 'Read the reasoning trace when risk climbs above “guarded”.' },
      { title: 'Update owners', detail: 'Use the insights drawer to rebalance persona owners across initiatives.' },
    ],
    recommendations: [
      { type: 'navigate', label: 'Ledger Insights', description: 'Jump to latest activity timeline', route: '/projects' },
      {
        type: 'prompt',
        label: 'Ledger summary prompt',
        description: 'Copy to Chat for Sora',
        prompt: 'Sora, summarize the ledger deltas for Project Atlas and flag policy, budget, or schedule drift.',
      },
      { type: 'link', label: 'Ledger Spec', href: '/docs/spec-sheet#page=5' },
    ],
    cues: ['Ledger drift', 'Risk score', 'Owner coverage'],
  },
  {
    id: 'chat',
    routes: ['/chat'],
    persona: 'Chris',
    title: 'Copilot Collaboration',
    summary: 'Chris keeps human + AI personas aligned while routing attachments and new intents through governance.',
    specAnchors: ['Spec §1.7.2 Interaction Modalities', 'Spec §7.12.3 Project Chat'],
    tutorialSteps: [
      { title: 'Pick persona', detail: 'Align persona to the project context before sending messages.' },
      { title: 'Attach evidence', detail: 'Use the document panel so AI responses cite the right files.' },
      { title: 'Capture decisions', detail: 'Copy outcomes back into Projects or Audit surfaces.' },
    ],
    recommendations: [
      { type: 'navigate', label: 'View Documents Panel', description: 'Toggle attachments for context', route: '/chat' },
      {
        type: 'prompt',
        label: 'Context briefing',
        prompt: 'Chris, summarize our last three chat exchanges and prep a decision log entry for Audit.',
      },
      { type: 'link', label: 'Conversation Spec', href: '/docs/CONVERSATION_STATE.md' },
    ],
    cues: ['Persona role', 'Attachment scope', 'Decision log'],
  },
  {
    id: 'research',
    routes: ['/research'],
    persona: 'Aria',
    title: 'Research Workbench Mentor',
    summary: 'Aria orchestrates experiments, parameter sweeps, and report snapshots inside the research workspace.',
    specAnchors: ['Spec §7.4 Research & Simulation', 'Spec §17.3 Advanced Research'],
    tutorialSteps: [
      { title: 'Sync snapshot', detail: 'Refresh the workspace to pull in latest experiments + metrics.' },
      { title: 'Tune parameters', detail: 'Adjust simulation type, iterations, and confidence before running.' },
      { title: 'Generate reports', detail: 'Export findings or send to Writer Workspace for narratives.' },
    ],
    recommendations: [
      { type: 'navigate', label: 'Open Writer Workspace', description: 'Document findings instantly', route: '/work/writer' },
      {
        type: 'prompt',
        label: 'Experiment prompt',
        prompt: 'Aria, evaluate the current Monte Carlo simulation results and recommend the next parameter sweep.',
      },
      { type: 'link', label: 'Research Spec', href: '/docs/spec-sheet#page=6' },
    ],
    cues: ['Snapshot freshness', 'Parameters', 'Report backlog'],
  },
  {
    id: 'templates-writer',
    routes: ['/work/writer', '/work/templates'],
    persona: 'Aria',
    title: 'Writer Workspace Guidance',
    summary: 'Keep lore, canon, and template governance aligned with CIR entries before publishing.',
    specAnchors: ['Spec §7.5 Writer Workspace', 'Spec §3.6 CIR'],
    tutorialSteps: [
      { title: 'Select template', detail: 'Pick the approved template before editing or generating content.' },
      { title: 'Capture canon notes', detail: 'Update canon cards + stats after each AI-assisted revision.' },
      { title: 'Sync to CIR', detail: 'Export drafts into documents and archives for reuse.' },
    ],
    recommendations: [
      { type: 'navigate', label: 'Templates Catalog', description: 'Browse governance packs', route: '/work/templates' },
      {
        type: 'prompt',
        label: 'Continuity prompt',
        prompt: 'Aria, compare this draft against the canon summary and highlight conflicting statements.',
      },
      { type: 'link', label: 'Docs Hub', href: '/docs' },
    ],
    cues: ['Template parity', 'Canon sync', 'AI draft quality'],
  },
  {
    id: 'tools',
    routes: ['/work/tools'],
    persona: 'Chris',
    title: 'Automation Terminal Coach',
    summary: 'Chris ensures terminal sessions and automation commands respect policy + evidence logging.',
    specAnchors: ['Spec §5.3 Legacy Bridges', 'Spec §7.3.5 Developer Tools'],
    tutorialSteps: [
      { title: 'Pick workspace', detail: 'Set the correct cwd or workspace before running commands.' },
      { title: 'Use catalog', detail: 'Leverage curated commands for repeatable tasks.' },
      { title: 'Capture output', detail: 'Copy results into Audit/Evidence when tasks complete.' },
    ],
    recommendations: [
      { type: 'prompt', label: 'Terminal prompt', prompt: 'Chris, prepare a git hygiene checklist for the current repo.' },
      { type: 'link', label: 'Automation Scripts', href: '/docs/scripts' },
    ],
    cues: ['Workspace target', 'Command history', 'Evidence logging'],
  },
  {
    id: 'integrations',
    routes: ['/integrations'],
    persona: 'Chris',
    title: 'Connector Control Room',
    summary: 'Chris validates connector health, incidents, and Office simulations to keep the driver fabric wired.',
    specAnchors: ['Spec §9.18 Integrations', 'Spec §5.4 Identity & Connectors'],
    tutorialSteps: [
      { title: 'Check connector states', detail: 'Review Connected/Degraded counts and incidents feed.' },
      { title: 'Test pipelines', detail: 'Use the “Test” action before editing configuration.' },
      { title: 'Simulate Office AI', detail: 'Trigger sample jobs to validate round-trip automation.' },
    ],
    recommendations: [
      { type: 'navigate', label: 'API Connectors View', route: '/integrations/api-connectors' },
      {
        type: 'prompt',
        label: 'Connector triage prompt',
        prompt: 'Chris, audit today’s integrations summary and suggest which connectors we should restart or re-auth.',
      },
      { type: 'link', label: 'Connector Spec', href: '/docs/spec-sheet#page=7' },
    ],
    cues: ['Connector health', 'Incidents', 'Office telemetry'],
  },
  {
    id: 'api-connectors',
    routes: ['/integrations/api-connectors', '/api-connectors'],
    persona: 'Sora',
    title: 'API Connector Sentry',
    summary: 'Sora cross-checks connector SLAs, security posture, and runtime notes for each adapter.',
    specAnchors: ['Spec §9.18.7 Adapters & Testing'],
    tutorialSteps: [
      { title: 'Review summary tiles', detail: 'Confirm total, healthy, and degraded numbers align with SLAs.' },
      { title: 'Inspect connector cards', detail: 'Open the connectors needing attention and test their hooks.' },
      { title: 'Capture response', detail: 'Use the panel to log quick notes back to Audit.' },
    ],
    recommendations: [
      { type: 'navigate', label: 'Back to Integrations', route: '/integrations' },
      {
        type: 'prompt',
        label: 'Connector QA prompt',
        prompt: 'Sora, evaluate each degraded connector and suggest patch steps ranked by risk.',
      },
    ],
    cues: ['Health score', 'Test hooks', 'Audit trail'],
  },
  {
    id: 'office-realtime',
    routes: ['/integrations/office', '/integrations/office-realtime'],
    persona: 'Aria',
    title: 'Office Mesh Supervisor',
    summary: 'Aria aligns document meshes, queue health, and automation playbooks for Office clients.',
    specAnchors: ['Spec §0.4 Identity Surfaces', 'Spec §5.4 Connectors'],
    tutorialSteps: [
      { title: 'Pick client session', detail: 'Select the live session to analyze or send prompts to.' },
      { title: 'Monitor queue health', detail: 'Keep pending jobs + queue depth within SLA.' },
      { title: 'Trigger playbooks', detail: 'Use automation cards (Portfolio Guardian, etc.) to keep docs in sync.' },
    ],
    recommendations: [
      { type: 'prompt', label: 'Document diff prompt', prompt: 'Aria, diff the active Office doc meshes and flag drift.' },
      { type: 'link', label: 'Office Deployment Notes', href: '/docs/install.html' },
    ],
    cues: ['Client harmony', 'Automation playbooks', 'Queue health'],
  },
  {
    id: 'analytics',
    routes: ['/analytics'],
    persona: 'AIC',
    title: 'Productivity Intelligence',
    summary: 'AIC interprets completion rates, project health, and workload distribution to keep guardrails tight.',
    specAnchors: ['Spec §7.2 Analytics', 'Spec §11 Observability'],
    tutorialSteps: [
      { title: 'Check status tiles', detail: 'Scan completion rate, active projects, and logged hours.' },
      { title: 'Open workload cards', detail: 'Ensure personas are not overloaded and adjust assignments.' },
      { title: 'Run AI report', detail: 'Generate or copy the analytics report for stakeholders.' },
    ],
    recommendations: [
      { type: 'navigate', label: 'Monitoring Console', route: '/monitoring' },
      {
        type: 'prompt',
        label: 'Analytics briefing',
        prompt: 'AIC, analyze the analytics dashboard and recommend two actions that improve throughput immediately.',
      },
      { type: 'link', label: 'Analytics Spec', href: '/docs/spec-sheet#page=9' },
    ],
    cues: ['Completion rate', 'Workload', 'Suggestions feed'],
  },
  {
    id: 'monitoring',
    routes: ['/monitoring', '/observability'],
    persona: 'Chris',
    title: 'Reliability & Observability',
    summary: 'Chris fuses metrics, logs, and traces into actionable troubleshooting steps.',
    specAnchors: ['Spec §11 Observability', 'Spec §7.7 Reliability'],
    tutorialSteps: [
      { title: 'Parse metrics JSON', detail: 'Input CPU/memory/disk metrics as JSON before running analysis.' },
      { title: 'Tune thresholds', detail: 'Adjust monitoring windows + thresholds to avoid alert fatigue.' },
      { title: 'Capture results', detail: 'Copy the AI output or feed it into AutoFix/Audit.' },
    ],
    recommendations: [
      { type: 'navigate', label: 'Observability Panel', route: '/observability' },
      {
        type: 'prompt',
        label: 'Self-heal prompt',
        prompt: 'Chris, inspect the observability cards and outline the next self-heal actions.',
      },
    ],
    cues: ['Metric inputs', 'Thresholds', 'Evidence pack'],
  },
  {
    id: 'audit-billing',
    routes: ['/audit', '/billing'],
    persona: 'AIC',
    title: 'Governance & Billing Fabric',
    summary: 'AIC assembles compliance packs, usage records, and billing guardrails.',
    specAnchors: ['Spec §10.3 Governance', 'Spec §15 Billing'],
    tutorialSteps: [
      { title: 'Review controls', detail: 'Check framework cards and evidence counts.' },
      { title: 'Run compliance check', detail: 'Trigger `/audit/checks/run` to refresh controls.' },
      { title: 'Export pack', detail: 'Generate evidence pack with optional project filter.' },
    ],
    recommendations: [
      { type: 'prompt', label: 'Evidence prompt', prompt: 'AIC, compile an evidence pack for the last 24 hours of AI activity and summarize anomalies.' },
      { type: 'navigate', label: 'Billing Usage', route: '/billing' },
    ],
    cues: ['Risk score', 'Evidence packs', 'Usage ledger'],
  },
  {
    id: 'settings',
    routes: ['/settings'],
    persona: 'Sora',
    title: 'Control Plane Settings',
    summary: 'Sora keeps theme, governance, residency, and daemon knobs aligned with policy.',
    specAnchors: ['Spec §1.7 Control Plane', 'Spec §10 Policy Engine'],
    tutorialSteps: [
      { title: 'Persona defaults', detail: 'Ensure default personas + automation behaviors are correct.' },
      { title: 'Residency & guardrails', detail: 'Update residency, guardrails, and budgets per tenant requirements.' },
      { title: 'Sync theme', detail: 'Apply theme tokens so desktop + web share the same palette.' },
    ],
    recommendations: [
      { type: 'navigate', label: 'Docs: Settings', route: '/docs/settings.html' },
      { type: 'prompt', label: 'Policy prompt', prompt: 'Sora, audit the current settings and list any policy deviations versus spec.' },
    ],
    cues: ['Persona defaults', 'Governance banners', 'Budget guardrails'],
  },
  {
    id: 'ai-operations',
    routes: ['/ai/operations', '/ai/os', '/ai/intents'],
    persona: 'Chris',
    title: 'AI Ops & Driver Fabric',
    summary: 'Chris enforces driver throttles, intent queues, and daemon policies.',
    specAnchors: ['Spec §5.12 Driver Scheduling', 'Spec §8 Capsule System'],
    tutorialSteps: [
      { title: 'Inspect queue depth', detail: 'Ensure driver queues stay within the target rate before throttling.' },
      { title: 'Audit reasoning', detail: 'Open reasoning traces for long-running intents.' },
      { title: 'Adjust throttles', detail: 'Use throttle controls to switch between auto/manual rates.' },
    ],
    recommendations: [
      { type: 'navigate', label: 'Intent Processor', route: '/ai/intents' },
      { type: 'navigate', label: 'AutoFix Center', route: '/ai/autofix' },
      {
        type: 'prompt',
        label: 'Driver status prompt',
        prompt: 'Chris, generate a driver scheduling heat-map and flag which queues need manual throttles.',
      },
    ],
    cues: ['Queue depth', 'Reasoning traces', 'Daemon status'],
  },
  {
    id: 'ai-copilot',
    routes: ['/ai/copilot'],
    persona: 'AIC',
    title: 'Copilot Command Bar',
    summary: 'AIC pairs personas, document ops, and assistant sessions into a single cockpit.',
    specAnchors: ['Spec §4 Cognitive Layer', 'Spec §7.12 Collaboration'],
    tutorialSteps: [
      { title: 'Switch personas', detail: 'Align persona/regulator settings before sending questions.' },
      { title: 'Review document ops', detail: 'Glance at recent document operations and reasoning traces.' },
      { title: 'Queue assistant run', detail: 'Log the tools used for each assistant session for audit traceability.' },
    ],
    recommendations: [
      { type: 'navigate', label: 'Launch Chat Console', route: '/chat' },
      {
        type: 'prompt',
        label: 'Copilot prompt',
        prompt: 'AIC, from the copilot console suggest my next best action for work + governance.',
      },
    ],
    cues: ['Persona state', 'Assistant runs', 'Driver metrics'],
  },
  {
    id: 'ai-advanced',
    routes: ['/ai/advanced'],
    persona: 'Sora',
    title: 'Advanced AI Engine',
    summary: 'Sora calibrates advanced AI capabilities, latency stats, and autonomous optimization.',
    specAnchors: ['Spec §4.5 Intelligence Capabilities'],
    tutorialSteps: [
      { title: 'Check health state', detail: 'Confirm the engine is online before triggering actions.' },
      { title: 'Review capability list', detail: 'Ensure each capability matches spec requirements.' },
      { title: 'Run action', detail: 'Execute initialize/process/generate/optimize when needed and log outputs.' },
    ],
    recommendations: [
      { type: 'prompt', label: 'Advanced AI prompt', prompt: 'Sora, optimize the Advanced AI engine for today’s workload (include latency + autonomy levels).' },
      { type: 'link', label: 'Advanced Spec', href: '/docs/spec-sheet#page=4' },
    ],
    cues: ['Health status', 'Capability mix', 'Output log'],
  },
  {
    id: 'ai-vision',
    routes: ['/ai/vision', '/computer-vision'],
    persona: 'Aria',
    title: 'Multimodal Console',
    summary: 'Aria guides OCR, detection, and diagram insights for uploaded or sample imagery.',
    specAnchors: ['Spec §7.4.7 Digital Twin Capsules', 'Spec §4 Multimodal Agents'],
    tutorialSteps: [
      { title: 'Choose sample or upload', detail: 'Load a screenshot/diagram relevant to the workspace.' },
      { title: 'Run analysis', detail: 'Execute analyze/OCR/detect flows sequentially.' },
      { title: 'Log highlights', detail: 'Push insights back into Projects or Writer workspace.' },
    ],
    recommendations: [
      { type: 'prompt', label: 'Vision prompt', prompt: 'Aria, convert this detection output into a project status summary.' },
      { type: 'link', label: 'Vision Deck', href: '/vision' },
    ],
    cues: ['Input source', 'Analysis mode', 'Highlights'],
  },
  {
    id: 'ai-nas',
    routes: ['/ai/nas', '/ai/nas/experiments', '/ai/nas/simulator'],
    persona: 'Chris',
    title: 'NAS Experiment Guide',
    summary: 'Chris keeps neural architecture experiments scoped, logged, and optimized.',
    specAnchors: ['Spec §7.4.6 NAS Engine'],
    tutorialSteps: [
      { title: 'Review status', detail: 'Confirm experiment status + metrics before starting another run.' },
      { title: 'Configure strategy', detail: 'Set search space, strategy, and generations to spec-approved values.' },
      { title: 'Capture best architecture', detail: 'Log best-fitness architectures into Projects or Docs.' },
    ],
    recommendations: [
      { type: 'prompt', label: 'NAS prompt', prompt: 'Chris, evaluate the NAS metrics and tell me if we should run one more generation.' },
      { type: 'link', label: 'NAS Spec', href: '/docs/spec-sheet#page=6' },
    ],
    cues: ['Strategy', 'Generations', 'Fitness history'],
  },
  {
    id: 'ai-security',
    routes: ['/ai/security', '/security', '/systems/security'],
    persona: 'AIC',
    title: 'Security Threat Detection',
    summary: 'AIC orchestrates scans, investigations, and reports across the security capsule.',
    specAnchors: ['Spec §7.7 Security Capsules', 'Spec §10.8 Risk Scoring'],
    tutorialSteps: [
      { title: 'Start the scan', detail: 'Run scan with the right scope/residency token.' },
      { title: 'Investigate events', detail: 'Open events and record investigations for compliance.' },
      { title: 'Generate report', detail: 'Use the report view to share recommendations.' },
    ],
    recommendations: [
      { type: 'prompt', label: 'Incident prompt', prompt: 'AIC, summarize today’s security scan and propose mitigation steps.' },
      { type: 'navigate', label: 'Go to Audit', route: '/audit' },
    ],
    cues: ['Scan scope', 'Threat backlog', 'Auto response'],
  },
  {
    id: 'ai-edge',
    routes: ['/ai/edge', '/ai/edge-computing', '/systems/edge'],
    persona: 'Chris',
    title: 'Edge Fabric Director',
    summary: 'Chris manages distributed nodes, deployment wavefronts, and optimization routines.',
    specAnchors: ['Spec §13.4 Hybrid & Edge', 'Spec §5.5 Hardware Drivers'],
    tutorialSteps: [
      { title: 'Assess nodes', detail: 'Check totals, loads, and heartbeat times.' },
      { title: 'Plan deployment', detail: 'Select nodes/strategy before deploying a model.' },
      { title: 'Optimize latency', detail: 'Run optimization jobs when latency drifts above target.' },
    ],
    recommendations: [
      { type: 'prompt', label: 'Edge prompt', prompt: 'Chris, choose the three best nodes for an urgent deployment and explain why.' },
      { type: 'link', label: 'Edge Spec', href: '/docs/spec-sheet#page=12' },
    ],
    cues: ['Node load', 'Deployment plan', 'Optimization'],
  },
  {
    id: 'ai-workflows',
    routes: ['/ai/workflows', '/systems/workflows'],
    persona: 'Sora',
    title: 'Workflow Orchestration',
    summary: 'Sora synchronizes orchestrator state, templates, and monitor output with driver fabric health.',
    specAnchors: ['Spec §8.10 Workflow Engine'],
    tutorialSteps: [
      { title: 'Check orchestrator status', detail: 'Start or refresh orchestrator before scheduling runs.' },
      { title: 'Inspect active workflows', detail: 'Track progress and owners for each automation.' },
      { title: 'Monitor logs', detail: 'Use the monitor output to capture audit-ready evidence.' },
    ],
    recommendations: [
      { type: 'navigate', label: 'AutoFix Queue', route: '/ai/autofix' },
      { type: 'prompt', label: 'Workflow prompt', prompt: 'Sora, review active workflows and tell me which to escalate.' },
    ],
    cues: ['Orchestrator status', 'Workflow progress', 'Monitor output'],
  },
  {
    id: 'ai-capsules',
    routes: ['/ai/capsules'],
    persona: 'Aria',
    title: 'Capsule Marketplace',
    summary: 'Aria curates capsule packs, install states, and blueprint recommendations.',
    specAnchors: ['Spec §3.8 Capsule Store', 'Spec §8 Capsule System'],
    tutorialSteps: [
      { title: 'Filter catalog', detail: 'Use categories/tags to zero in on needed capsules.' },
      { title: 'Check verification', detail: 'Ensure capsules are verified + policy aligned before install.' },
      { title: 'Review blueprints', detail: 'Bundle capsules via blueprint suggestions for faster onboarding.' },
    ],
    recommendations: [
      { type: 'prompt', label: 'Capsule prompt', prompt: 'Aria, recommend the best capsule pack for a regulated research tenant.' },
      { type: 'link', label: 'Capsule Spec', href: '/docs/spec-sheet#page=8' },
    ],
    cues: ['Install status', 'Drivers required', 'Blueprint fit'],
  },
  {
    id: 'ai-autofix',
    routes: ['/ai/autofix'],
    persona: 'Chris',
    title: 'AutoFix Control Center',
    summary: 'Chris triages AI-generated fixes, config thresholds, and evidence logging for automated remediation.',
    specAnchors: ['Spec §7.7 Auto-Remediation', 'Spec §15.4 Billing Optimizer'],
    tutorialSteps: [
      { title: 'Review pending issues', detail: 'Filter by severity and select issues to auto-apply or escalate.' },
      { title: 'Tune config', detail: 'Adjust auto-apply threshold and scan interval according to policy.' },
      { title: 'Check reports', detail: 'Download AutoFix reports for compliance or developer review.' },
    ],
    recommendations: [
      { type: 'prompt', label: 'AutoFix prompt', prompt: 'Chris, prioritize the current AutoFix backlog and call out anything needing human review.' },
      { type: 'navigate', label: 'Go to Monitoring', route: '/monitoring' },
    ],
    cues: ['Issue severity', 'Config thresholds', 'Reports'],
  },
  {
    id: 'docs',
    routes: ['/docs', '/docs/spec-sheet'],
    persona: 'AIC',
    title: 'Documentation Navigator',
    summary: 'AIC links preserved HTML, markdown refs, and spec tracker for quick parity checks.',
    specAnchors: ['Spec §19.12 Documentation'],
    tutorialSteps: [
      { title: 'Use search/filter', detail: 'Filter docs by tags, categories, or parity scores.' },
      { title: 'Open preserved HTML', detail: 'Launch Tkinter-era HTML for comparison when reviewing migration.' },
      { title: 'Sync spec tracker', detail: 'Reference MIGRATION_CONTINUED + Spec Sheet entries for parity.' },
    ],
    recommendations: [
      { type: 'link', label: 'Open Technical Spec PDF', href: '/docs/spec-sheet' },
      {
        type: 'prompt',
        label: 'Doc parity prompt',
        prompt: 'AIC, analyze the docs manifest and list any surfaces still marked partial/legacy.',
      },
    ],
    cues: ['Category order', 'Parity score', 'Spec tracker'],
  },
  {
    id: 'vision-deck',
    routes: ['/vision', '/vision-deck', '/future', '/future/*'],
    persona: 'Sora',
    title: 'Vision Deck Navigator',
    summary: 'Sora links future decks, backlogs, and implementation checklists for roadmap planning.',
    specAnchors: ['Spec §17.6 Strategic Sandbox'],
    tutorialSteps: [
      { title: 'Pick a deck', detail: 'Use the left rail to jump between future envelopes.' },
      { title: 'Skim backlog + checklist', detail: 'Review backlog cards and implementation checklist for readiness.' },
      { title: 'Open legacy HTML', detail: 'Open the preserved Tkinter deck for audit trails.' },
    ],
    recommendations: [
      { type: 'prompt', label: 'Future prompt', prompt: 'Sora, summarize this future deck and outline the next experiment needed.' },
      { type: 'link', label: 'Vision Spec', href: '/docs/future_meta.html' },
    ],
    cues: ['Deck selection', 'Implementation notes', 'Legacy link'],
  },
  {
    id: 'search',
    routes: ['/search', '/search-engine'],
    persona: 'AIC',
    title: 'Semantic Search Coach',
    summary: 'AIC guides query formulation and dataset coverage for the embedded search engine.',
    specAnchors: ['Spec §6.5 Search & Retrieval'],
    tutorialSteps: [
      { title: 'Check status', detail: 'Ensure search index + embeddings are ready before querying.' },
      { title: 'Craft queries', detail: 'Use semantic phrasing or filters to narrow down tasks/projects/docs.' },
      { title: 'Tag results', detail: 'Copy key results back into Projects/Docs for traceability.' },
    ],
    recommendations: [
      { type: 'prompt', label: 'Search prompt', prompt: 'AIC, give me the best query to find all security-related tasks across projects.' },
      { type: 'navigate', label: 'Go to Docs Hub', route: '/docs' },
    ],
    cues: ['Index readiness', 'Query quality', 'Result tagging'],
  },
  {
    id: 'collaboration',
    routes: ['/collaboration'],
    persona: 'Chris',
    title: 'Collaboration Intelligence',
    summary: 'Chris analyzes tenant membership, communication patterns, and productivity forecasts.',
    specAnchors: ['Spec §7 Workspaces & Collaboration', 'Spec §7.12 Federation'],
    tutorialSteps: [
      { title: 'Filter by tenant', detail: 'Use the tenant filter to isolate a team before running AI analysis.' },
      { title: 'Collect patterns', detail: 'Describe communication patterns and complexities in the form.' },
      { title: 'Log recommendations', detail: 'Copy the AI output back into Projects or Docs.' },
    ],
    recommendations: [
      { type: 'prompt', label: 'Team insight prompt', prompt: 'Chris, predict how this team’s productivity will shift if we add two AI drivers.' },
      { type: 'link', label: 'Collaboration Spec', href: '/docs/spec-sheet#page=6' },
    ],
    cues: ['Tenant filter', 'Patterns', 'Recommendation log'],
  },
  {
    id: 'personalization',
    routes: ['/personalization'],
    persona: 'Aria',
    title: 'Personalization Engine',
    summary: 'Aria tailors recommendation inputs (preferences, context, max recs) for user-specific insights.',
    specAnchors: ['Spec §7.5.5 Collaboration & Publication', 'Spec §19.12 Recommendations'],
    tutorialSteps: [
      { title: 'Select engine type', detail: 'Choose content/collaborative/hybrid modes per use case.' },
      { title: 'Provide preferences', detail: 'List explicit preferences and context for better AI recall.' },
      { title: 'Set max recs', detail: 'Control recommendation volume to avoid overload.' },
    ],
    recommendations: [
      { type: 'prompt', label: 'Recommendation prompt', prompt: 'Aria, generate recommendations for a cyber defense tenant using collaborative filtering.' },
      { type: 'navigate', label: 'Collaboration Intelligence', route: '/collaboration' },
    ],
    cues: ['Engine type', 'Preferences', 'Result log'],
  },
  {
    id: 'default',
    routes: ['*'],
    persona: 'AIC',
    title: 'Contextual Assistant',
    summary: 'AIC adapts to the current workspace, providing quick prompts and references so no surface lacks AI coaching.',
    specAnchors: ['Spec §4 Cognitive Layer', 'Spec §7 Workspaces'],
    tutorialSteps: [
      { title: 'Skim workspace mission', detail: 'Read the top-left summary to remember why this surface exists.' },
      { title: 'Trigger AI walkthrough', detail: 'Use the prompt below when you need a guided tour.' },
      { title: 'Log decisions', detail: 'Push any decisions into Projects, Audit, or Docs right away.' },
    ],
    recommendations: [
      { type: 'prompt', label: 'Walkthrough prompt', prompt: 'AIC, give me a focused walkthrough of this workspace and list two recommended follow-up actions.' },
      { type: 'link', label: 'Docs Hub', href: '/docs' },
    ],
    cues: ['Workspace mission', 'Persona alignment', 'Spec parity'],
  },
]

export const resolveGuidanceEntry = (pathname: string): AIGuidanceEntry => {
  const entry = aiGuidanceEntries.find((item) => item.routes.some((route) => wildcardMatch(route, pathname)))
  return entry ?? aiGuidanceEntries[aiGuidanceEntries.length - 1]
}
