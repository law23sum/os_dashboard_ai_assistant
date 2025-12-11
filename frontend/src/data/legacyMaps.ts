export interface LegacyDocLink {
  label: string
  description: string
  href: string
  kind: 'HTML' | 'Markdown' | 'PDF' | 'Tool'
}

export interface LegacyDocGroup {
  title: string
  summary: string
  items: LegacyDocLink[]
}

export const legacyDocGroups: LegacyDocGroup[] = [
  {
    title: 'Orientation',
    summary: 'Reference packets the Tkinter cockpit exposed in its top navigation dropdown.',
    items: [
      {
        label: 'Project directory overview',
        description: 'Flat text tree that documents every repo folder the desktop shell relied on.',
        href: '/docs/project_directory_structure',
        kind: 'Markdown',
      },
      {
        label: 'Table of contents (PDF)',
        description: 'Legacy PDF map showing every Tkinter screen and documentation artifact.',
        href: '/docs/table_of_content_os_dashboard_ai_assistant.pdf',
        kind: 'PDF',
      },
      {
        label: 'Documentation README',
        description: 'High-level README from /documentation that Tkinter linked in its docs dropdown.',
        href: '/docs/README.md',
        kind: 'Markdown',
      },
      {
        label: 'Command cheatsheet',
        description: 'Original command glossary surfaced beside the Tkinter terminal.',
        href: '/docs/commands.md',
        kind: 'Markdown',
      },
    ],
  },
  {
    title: 'Mission Control',
    summary: 'Landing decks and implementation briefs the Tkinter AI OS tab launched.',
    items: [
      {
        label: 'Dashboard landing',
        description: 'Preserved HTML hero page from /docs/index.html.',
        href: '/docs/index.html',
        kind: 'HTML',
      },
      {
        label: 'AI capabilities',
        description: 'Catalog of AI behaviors and personas from the original marketing site.',
        href: '/docs/ai_capabilities.html',
        kind: 'HTML',
      },
      {
        label: 'Implementation summary',
        description: 'Top-level build summary referenced during Tkinter migration reviews.',
        href: '/docs/IMPLEMENTATION_SUMMARY.md',
        kind: 'Markdown',
      },
      {
        label: 'Implementation roadmap',
        description: 'Detailed sequencing plan for shipping the OS Dashboard migration.',
        href: '/docs/IMPLEMENTATION_ROADMAP.md',
        kind: 'Markdown',
      },
      {
        label: 'New features added',
        description: 'Running changelog used in the Tkinter console.',
        href: '/docs/NEW_FEATURES_ADDED.md',
        kind: 'Markdown',
      },
    ],
  },
  {
    title: 'Architecture & Engines',
    summary: 'Canon documents the Tkinter AI OS dropdown exposed for architecture sign-off.',
    items: [
      {
        label: 'Canonical Internal Representation',
        description: 'Spec describing how documents map into the shared representation.',
        href: '/docs/CANONICAL_INTERNAL_REPRESENTATION.md',
        kind: 'Markdown',
      },
      {
        label: 'Daemon framework overview',
        description: 'Explains the automation framework the Tkinter AI Ops panels controlled.',
        href: '/docs/DAEMON_FRAMEWORK_ARCHITECTURE.md',
        kind: 'Markdown',
      },
      {
        label: 'Cognitive daemon system',
        description: 'In-depth write-up on the cognitive daemon orchestration.',
        href: '/docs/COGNITIVE_DAEMON_SYSTEM.md',
        kind: 'Markdown',
      },
      {
        label: 'Architecture implementation',
        description: 'Step-by-step architecture roll-out that fed the Tkinter dashboards.',
        href: '/docs/ARCHITECTURE_IMPLEMENTATION.md',
        kind: 'Markdown',
      },
      {
        label: 'OS Canon system spec',
        description: 'Full canonical spec Tkinter used to justify advanced features.',
        href: '/docs/OS_DASHBOARD_CANON_SYSTEM_SPEC.md',
        kind: 'Markdown',
      },
    ],
  },
  {
    title: 'Automation & Pipelines',
    summary: 'Docs targeted by the Tools + AI Ops tabs for tasking daemons.',
    items: [
      {
        label: 'AI Office agent realtime',
        description: 'Realtime agent design that powers the Tkinter AI console.',
        href: '/docs/AI_OFFICE_AGENT_REALTIME.md',
        kind: 'Markdown',
      },
      {
        label: 'Document upload design',
        description: 'UI/UX design doc for the ingestion panel.',
        href: '/docs/DOCUMENT_UPLOAD_DESIGN.md',
        kind: 'Markdown',
      },
      {
        label: 'Document upload integration',
        description: 'Integration notes for hooking uploads into automations.',
        href: '/docs/DOCUMENT_UPLOAD_DAEMON_INTEGRATION.md',
        kind: 'Markdown',
      },
      {
        label: 'Document upload implementation',
        description: 'Implementation guide for turning uploads into workflows.',
        href: '/docs/DOCUMENT_UPLOAD_IMPLEMENTATION.md',
        kind: 'Markdown',
      },
      {
        label: 'Document templates & automation',
        description: 'Template system blueprint mirrored in the Templates tab.',
        href: '/docs/DOCUMENT_TEMPLATES_AND_AUTOMATION.md',
        kind: 'Markdown',
      },
      {
        label: 'Automation orchestration',
        description: 'Outlines how orchestrators schedule capsules/daemons.',
        href: '/docs/AUTOMATION_ORCHESTRATION_INTEGRATION.md',
        kind: 'Markdown',
      },
      {
        label: 'File task extraction',
        description: 'Design notes for extracting tasks from uploaded docs.',
        href: '/docs/FILE_TASK_EXTRACTION_FEATURE.md',
        kind: 'Markdown',
      },
    ],
  },
  {
    title: 'Integrations & Enterprise',
    summary: 'Enterprise deployment artifacts surfaced in the Tkinter Integrations tab.',
    items: [
      {
        label: 'OneDrive/Office integration',
        description: 'Playbook for connecting Microsoft workspaces.',
        href: '/docs/ONEDRIVE_INTEGRATION.md',
        kind: 'Markdown',
      },
      {
        label: 'OS Dashboard Enterprise',
        description: 'Enterprise SKU overview referenced on sales calls.',
        href: '/docs/OS_DASHBOARD_ENTERPRISE.md',
        kind: 'Markdown',
      },
      {
        label: 'Third-party credentials setup',
        description: 'Checklist Tkinter surfaced when provisioning connectors.',
        href: '/docs/THIRD_PARTY_CREDENTIALS_SETUP.md',
        kind: 'Markdown',
      },
      {
        label: 'AWS cost estimate',
        description: 'Rough cost model used for the infrastructure widget.',
        href: '/docs/AWS_COST_ESTIMATE.md',
        kind: 'Markdown',
      },
    ],
  },
  {
    title: 'Security & Governance',
    summary: 'Audit + policy docs from the Tkinter Audit tab.',
    items: [
      {
        label: 'Conversation AI integration',
        description: 'Explains the regulated conversation layer.',
        href: '/docs/CONVERSATION_AI_INTEGRATION.md',
        kind: 'Markdown',
      },
      {
        label: 'Global impact white paper',
        description: 'High-level governance/ethics brief referenced by the Audit panel.',
        href: '/docs/GLOBAL_IMPACT_WHITE_PAPER.md',
        kind: 'Markdown',
      },
      {
        label: 'Salvaged code summary',
        description: 'Due diligence notes the Tkinter security tab linked.',
        href: '/docs/SALVAGED_CODE_SUMMARY.md',
        kind: 'Markdown',
      },
    ],
  },
  {
    title: 'Vision & Portfolio',
    summary: 'All the future envelopes that originated inside the Tkinter Future tab.',
    items: [
      {
        label: 'Vision brief',
        description: 'High-level north star memo.',
        href: '/docs/VISION.md',
        kind: 'Markdown',
      },
      {
        label: 'Vision implementation',
        description: 'Detailed implementation notes for the OS Dashboard vision.',
        href: '/docs/VISION_IMPLEMENTATION.md',
        kind: 'Markdown',
      },
      {
        label: 'Future feature portfolio',
        description: 'Legacy backlog table mirrored in today’s Future Deck.',
        href: '/docs/FUTURE_FEATURE_PORTFOLIO.md',
        kind: 'Markdown',
      },
      {
        label: 'Core OS roadmap',
        description: 'HTML deck for the Core OS horizon.',
        href: '/docs/future_core_os.html',
        kind: 'HTML',
      },
      {
        label: 'Advanced horizons roadmap',
        description: 'HTML deck for the Advanced horizon.',
        href: '/docs/future_advanced.html',
        kind: 'HTML',
      },
      {
        label: 'Super capabilities roadmap',
        description: 'HTML deck for the Super capsule tier.',
        href: '/docs/future_super.html',
        kind: 'HTML',
      },
      {
        label: 'Hyper network roadmap',
        description: 'HTML deck for the Hyper network horizon.',
        href: '/docs/future_hyper.html',
        kind: 'HTML',
      },
      {
        label: 'Ultra scale roadmap',
        description: 'HTML deck for the Ultra scale roadmap.',
        href: '/docs/future_ultra.html',
        kind: 'HTML',
      },
      {
        label: 'Supreme tier roadmap',
        description: 'HTML deck for the Supreme tier.',
        href: '/docs/future_supreme.html',
        kind: 'HTML',
      },
      {
        label: 'Ascend roadmap',
        description: 'HTML deck for the Ascend envelope.',
        href: '/docs/future_ascend.html',
        kind: 'HTML',
      },
      {
        label: 'Meta envelope roadmap',
        description: 'HTML deck for the Meta envelope.',
        href: '/docs/future_meta.html',
        kind: 'HTML',
      },
    ],
  },
  {
    title: 'Settings & Reference',
    summary: 'Ops docs Tkinter exposed in the Settings dropdown.',
    items: [
      {
        label: 'Settings dashboard',
        description: 'Legacy HTML settings landing page.',
        href: '/docs/settings.html',
        kind: 'HTML',
      },
      {
        label: 'Deployment guide',
        description: 'Full deployment runbook mirrored in Tkinter’s settings tab.',
        href: '/docs/DEPLOYMENT.md',
        kind: 'Markdown',
      },
      {
        label: 'Feature opportunities',
        description: 'Backlog of future improvements the Tkinter UI highlighted.',
        href: '/docs/FEATURE_OPPORTUNITIES.md',
        kind: 'Markdown',
      },
      {
        label: 'Missing features summary',
        description: 'Audit list of parity gaps between Tkinter and web.',
        href: '/docs/MISSING_FEATURES_SUMMARY.md',
        kind: 'Markdown',
      },
      {
        label: 'Low hanging feature wins',
        description: 'Quick wins backlog used by the settings checklist.',
        href: '/docs/LOW_HANGING_FRUIT_FEATURES.md',
        kind: 'Markdown',
      },
      {
        label: 'CyberChef (offline)',
        description: 'Bundled CyberChef build the Tkinter Tools tab opened.',
        href: '/docs/CyberChef_v10.19.4/CyberChef_v10.19.4.html',
        kind: 'Tool',
      },
    ],
  },
]

export interface FutureTierDoc {
  slug: string
  label: string
  summary: string
  htmlHref: string
}

export const futureTierDocs: FutureTierDoc[] = [
  {
    slug: 'core_os',
    label: 'Core OS Engines',
    summary: 'Execution plan for the foundational OS engines Tkinter showcased.',
    htmlHref: '/docs/future_core_os.html',
  },
  {
    slug: 'advanced',
    label: 'Advanced Horizons',
    summary: 'Future-facing capsules covering advanced automation envelopes.',
    htmlHref: '/docs/future_advanced.html',
  },
  {
    slug: 'super',
    label: 'Super Capabilities',
    summary: 'Next-tier capsules with higher autonomy and scope.',
    htmlHref: '/docs/future_super.html',
  },
  {
    slug: 'hyper',
    label: 'Hyper Network',
    summary: 'Network-scale orchestration concepts from the Tkinter future deck.',
    htmlHref: '/docs/future_hyper.html',
  },
  {
    slug: 'ultra',
    label: 'Ultra Scale',
    summary: 'Ultra-scale envelopes balancing automation and governance.',
    htmlHref: '/docs/future_ultra.html',
  },
  {
    slug: 'supreme',
    label: 'Supreme Tier',
    summary: 'Supreme-tier ontological/planning capsules.',
    htmlHref: '/docs/future_supreme.html',
  },
  {
    slug: 'ascend',
    label: 'Ascend',
    summary: 'Ascend envelope that stitches multiple capsules together.',
    htmlHref: '/docs/future_ascend.html',
  },
  {
    slug: 'meta',
    label: 'Meta Envelope',
    summary: 'Meta-level roadmap that unifies all future horizons.',
    htmlHref: '/docs/future_meta.html',
  },
]
