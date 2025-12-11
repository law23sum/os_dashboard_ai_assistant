export interface FutureDeckEntry {
  code: string
  title: string
  budget: string
  summary: string
}

export interface FutureDeck {
  slug: string
  badge: string
  badgeColor: string
  heroTitle: string
  description: string
  backlog: FutureDeckEntry[]
  checklist: string[]
  notes: string[]
}

const checklistTemplate = [
  'Drivers & environment needs',
  'Capsule packs to design',
  'Policy / governance hooks',
  'Success metrics & pilots',
]

const notesTemplate = [
  'Capture architectural sketches and scenario flows.',
  'List dependencies, regulators, and risk domains.',
  'Pin open research questions or required telemetry.',
]

const deck = (slug: string, badge: string, badgeColor: string, backlog: FutureDeckEntry[]): FutureDeck => ({
  slug,
  badge,
  badgeColor,
  heroTitle: 'Future Feature Portfolio',
  description: 'Placeholder canvas for design explorations across capsules, environment drivers, and governance layers.',
  backlog,
  checklist: [...checklistTemplate],
  notes: [...notesTemplate],
})

export const futureDecks: Record<string, FutureDeck> = {
  meta: deck('meta', 'Meta Envelope', '#10b981', [
    {
      code: '10.50',
      title: 'Full Meta-Stack Envelope',
      budget: '$1.6T–$5.4T+',
      summary:
        'All layers (advanced + super + hyper + ultra + supreme + ascend) deployed together as a civilization-scale fabric.',
    },
  ]),
  supreme: deck('supreme', 'Supreme', '#facc15', [
    {
      code: '10.43',
      title: 'Ontological Compiler',
      budget: '$60–220B',
      summary:
        "Compiles an org's worldview into executable ontologies consumed by every capsule and agent.",
    },
    {
      code: '10.44',
      title: 'Canon of Truth Engine',
      budget: '$80–260B',
      summary: 'Maintains living beliefs with evidence, counterexamples, and refutations across time.',
    },
    {
      code: '10.45',
      title: 'Reality Contract Layer',
      budget: '$50–180B',
      summary: 'Links automation to explicit reality triggers so systems can revert or self-correct.',
    },
    {
      code: '10.46',
      title: 'Human–System Co-Evolution Orchestrator',
      budget: '$40–150B',
      summary: 'Plans how roles, skills, and automation evolve together without misalignment.',
    },
    {
      code: '10.47',
      title: 'Successor Architect & Legacy Seeder',
      budget: '$30–120B',
      summary:
        'Encodes institutional legacies and doctrines as capsule libraries for future stewards.',
    },
    {
      code: '10.48',
      title: 'Unified Law of Work & Meaning Engine',
      budget: '$80–280B',
      summary: "Meta-objective layer that defines what 'good' means for work, automation, and society.",
    },
  ]),
  ascend: deck('ascend', 'Ascend', '#8b5cf6', [
    {
      code: '10.49',
      title: 'Sovereign Norm & Obligation Stack — Ascend Capabilities Layer',
      budget: '$120–400B',
      summary:
        'The sovereign governance membrane between automation and the real world: a realtime obligation sentinel + norm-collision engine + constitutional policy VM + decision-proof ledger.',
    },
  ]),
  ultra: deck('ultra', 'Ultra Scale', '#f97316', [
    { code: '10.33', title: 'Cognitive Twin Fabric', budget: '$60–210B', summary: 'Living models of people, teams, and roles to optimize staffing and augmentations.' },
    { code: '10.34', title: 'Strategy Garden & Capsule Fund', budget: '$40–160B', summary: 'Portfolio view where strategies exist as capsule graphs with budget + ROI tracking.' },
    { code: '10.35', title: 'Reality Twin Mesh', budget: '$70–230B', summary: 'Multi-layer twin of products, infra, markets, and financials for impact simulations.' },
    { code: '10.36', title: 'Temporal Backtesting Engine', budget: '$40–150B', summary: "Replays history with alternate capsule graphs to learn from 'ghost' decisions." },
    { code: '10.37', title: 'Law-of-the-OS & AI Court', budget: '$50–180B', summary: 'Formal internal law layer that arbitrates responsibility when automation misbehaves.' },
    { code: '10.38', title: 'Inter-OS Federation', budget: '$60–210B', summary: 'Standards and trust fabric for multiple OS Dashboard networks to interoperate.' },
    { code: '10.39', title: 'Meta-Design Studio', budget: '$45–160B', summary: 'System that redesigns the platform itself based on telemetry and friction signals.' },
    { code: '10.40', title: 'Cognitive Economy Engine', budget: '$70–240B', summary: 'Allocator that decides which humans, agents, or capsules tackle work for max ROI.' },
    { code: '10.41', title: 'Multi-Reality Storyboard', budget: '$40–150B', summary: 'Immersive visualization of branching future strategies and capsule graphs.' },
    { code: '10.42', title: 'Alignment Monitor', budget: '$50–170B', summary: 'Continuously checks whether automation behaviors still match intent and ethics.' },
  ]),
  hyper: deck('hyper', 'Hyper Network', '#ec4899', [
    { code: '10.26', title: 'HyperFoundry', budget: '$60–220B', summary: 'Automation-native venture studio that ideates new capsule bundles from usage telemetry.' },
    { code: '10.27', title: 'HyperLab', budget: '$50–180B', summary: 'Cross-org research grid with shared datasets, compute, and reproducible study capsules.' },
    { code: '10.28', title: 'HyperRegent', budget: '$70–240B', summary: 'Regulators gain tenancy inside the platform, running regulation capsules on live data.' },
    { code: '10.29', title: 'HyperSymphony', budget: '$60–210B', summary: 'Revenue-sharing cross-org capsule flows where each participant owns different steps.' },
    { code: '10.30', title: 'HyperDaemon', budget: '$80–260B', summary: 'Systemic risk sentinel watching capsule networks, markets, and infra for cascading failures.' },
    { code: '10.31', title: 'HyperContinuity', budget: '$40–150B', summary: 'Portable lifetime knowledge + trust graph for individuals and orgs.' },
    { code: '10.32', title: 'HyperGenesis', budget: '$50–190B', summary: 'High-fidelity world simulation layer for macro strategy rehearsals.' },
  ]),
  super: deck('super', 'Super Capabilities', '#0ea5e9', [
    { code: '10.19', title: 'Agentic Enterprise Twin', budget: '$70–230B', summary: 'Living twin of an org’s structure, workflows, KPIs, and risks for scenario planning and delegation.' },
    { code: '10.20', title: 'Global Policy & Regulation Fabric', budget: '$90–300B', summary: 'Executable policies shared between regulators and operators with traceable enforcement.' },
    { code: '10.21', title: 'Temporal Reasoning & Time-Cascade Engine', budget: '$40–150B', summary: 'Models how capsules and policies propagate over quarters, enabling branch-and-bound planning.' },
    { code: '10.22', title: 'Cross-Domain Knowledge & Law Synthesizer', budget: '$50–180B', summary: 'Finds shared abstractions and capsule templates that generalize across industries.' },
    { code: '10.23', title: 'Inter-OS Knowledge Network', budget: '$35–140B', summary: 'An anonymized exchange of best practices between separate OS Dashboard deployments.' },
    { code: '10.24', title: 'Autonomous Knowledge Steward', budget: '$30–110B', summary: 'Always-on curator that prunes contradictions and suggests ontology refactors over years.' },
    { code: '10.25', title: 'HyperMesh', budget: '$120–380B', summary: 'Federated execution mesh so capsules can span partners, suppliers, and regulators safely.' },
  ]),
  advanced: deck('advanced', 'Advanced Horizons', '#a855f7', [
    { code: '10.14', title: 'Advanced Research, Simulation & Digital Twin Platform', budget: '$40–160B', summary: 'Extends the research hub into CAD/CAE/HPC-grade digital twins for complex physical systems.' },
    { code: '10.15', title: 'Autonomous Research Conductor (ARC)', budget: '$60–220B', summary: 'Plans and adapts long-horizon research programs, reallocating compute and budget automatically.' },
    { code: '10.16', title: 'Symbolic–Numeric Theory Discovery Engine', budget: '$40–180B', summary: 'Searches for governing equations and cross-domain laws, feeding the canon and ontological layers.' },
    { code: '10.17', title: 'Self-Evolving Capsule Ecosystem', budget: '$80–260B', summary: 'Monitors capsule usage and proposes safer, faster variants under governance supervision.' },
    { code: '10.18', title: 'Enterprise & Civilization Knowledge Market', budget: '$120–400B', summary: 'Marketplace for capsules, blueprints, research packs, and curricula across sectors.' },
  ]),
  core_os: deck('core_os', 'Core OS Engines', '#1f6feb', [
    { code: '10.1', title: 'Master Stack & Project Management Engine', budget: '$45–160B', summary: 'Daily cockpit for files, capsules, and project state across env drivers and workflow synthesis.' },
    { code: '10.2', title: 'Code Merge Advisor', budget: '$110–380B', summary: 'Compresses merge risk across repos while orchestrating build/test/deploy pipelines.' },
    { code: '10.3', title: 'Commit → Task Generator', budget: '$30–100B', summary: 'Translates diffs into backlog items and keeps them synced with repository and environment state.' },
    { code: '10.4', title: 'Research Orchestrator & Simulation Hub', budget: '$30–130B', summary: 'Coordinates notebooks, HPC jobs, and lab tools so research programs run like automated workflows.' },
    { code: '10.5', title: 'Writer Workstation Engine', budget: '$15–65B', summary: 'Creator OS where lore, canon, assets, and publishing workflows live in one capsule-aware stack.' },
    { code: '10.6', title: 'Archive / Continuity / Resonance Engine', budget: '$160–500B', summary: 'Long-memory substrate capturing documents, environments, capsules, and execution traces.' },
    { code: '10.7', title: 'Cybersecurity Guardian', budget: '$35–150B', summary: 'Secure coding + runtime co-pilot that hardens configs, enforces policy, and distributes remediation capsules.' },
    { code: '10.8', title: 'Business Accounting & Financing Console', budget: '$45–190B', summary: 'Finance cockpit linking banks, ledgers, and automations for compliant creative work.' },
    { code: '10.9', title: 'Record Auditor & Logbook', budget: '$35–130B', summary: 'End-to-end audit trail across intent, agent action, Unix commands, env drift, and capsule lineage.' },
    { code: '10.10', title: 'Executable Capsules & Marketplace', budget: '$230–750B', summary: 'Ecosystem where workflows ship as executable capsules with environment manifests and monetizable packs.' },
    { code: '10.11', title: 'Policy & Governance Engine', budget: '$160–450B', summary: 'Enforces who/what may execute commands, environment changes, or capsules across enterprises.' },
    { code: '10.12', title: 'AI Billing & Usage Fabric', budget: '$30–140B', summary: 'Meters models, drivers, and capsule runs so automation can be routed, governed, and priced.' },
    { code: '10.13', title: 'OS Dashboard AI Assistant Platform', budget: '$950B–$2.5T+', summary: 'Full stack orchestrating people, apps, Unix, and governance end-to-end.' },
  ]),
}

export const getFutureDeck = (slug?: string) => {
  if (!slug) return undefined
  return futureDecks[slug.toLowerCase()]
}
