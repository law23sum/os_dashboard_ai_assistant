(function () {
    const pricingModel = {
        horizonYears: 50, // approximation of 30 → 80 year planning window
        individualSeats: 1200000, // targeted premium seat base to keep pricing mid/high
        enterpriseTenants: 8000 // limited high-value enterprise/government tenants
    };

    const formatCurrency = (value) => {
        if (value === 0) return '$0';
        if (value >= 1_000_000) {
            return `$${(value / 1_000_000).toFixed(2)}M`;
        }
        if (value >= 1_000) {
            return `$${(value / 1_000).toFixed(2)}K`;
        }
        return `$${value.toFixed(2)}`;
    };

    const computePricing = (ltvRange, audience) => {
        const avgValue = ((ltvRange[0] + ltvRange[1]) / 2) * 1_000_000_000;
        const users = audience === 'customer' ? pricingModel.individualSeats : pricingModel.enterpriseTenants;
        const annual = avgValue / (users * pricingModel.horizonYears);
        return {
            annual,
            biannual: annual / 2,
            monthly: annual / 12
        };
    };

    window.osPricingModel = pricingModel;
    window.osFormatCurrency = formatCurrency;
    window.osComputePricing = computePricing;

    window.osProductData = [
        {
            id: '10.0',
            name: 'AI OS',
            category: 'Core',
            artifact_type: 'Product',
            tier: 'Product',
            capability_layer: 'Core',
            lifetimeValue: [950, 2500],
            purpose: 'Product umbrella that packages the AI OS platform, orchestrator, and workspaces into sellable editions.',
            features: [
                'Editions map policy profiles, driver packs, and governance baselines.',
                'Bundles combine capsule templates, workflow packs, and vertical workspaces.',
                'Capability ladder enables progressive disclosure from Core to Advanced and beyond.'
            ],
            audiences: ['Executives', 'Platform owners', 'Enterprise operators'],
            editions: ['Starter', 'Growth', 'Enterprise', 'Sovereign'],
            bundles: [
                'AI OS Core Pack',
                'AI OS Advanced Research & Twin Pack',
                'AI OS Project Intelligence Bundle',
                'AI OS Dev Productivity Bundle'
            ]
        },
        {
            id: '10.1',
            name: 'Master Stack & Intelligence Project Management Engine',
            category: 'Core',
            artifact_type: 'Engine',
            tier: 'Module',
            capability_layer: 'Core',
            lifetimeValue: [45, 160],
            purpose: 'Anchor workspace that combines planning, files, environment control, and workflow capsules.',
            features: [
                'Unifies project plans, files, and Capsules as a work graph competing with Notion/Asana.',
                'Ties Unix drivers and package managers to project milestones for real infra awareness.',
                'Captures Workflow Synthesis to turn recurring executions into reusable Capsule Packs.'
            ],
            audiences: ['Product teams', 'Program management', 'Platform engineering']
        },
        {
            id: '10.2',
            name: 'Code Merge Advisor',
            category: 'Core',
            artifact_type: 'Capability',
            tier: 'Module',
            capability_layer: 'Core',
            lifetimeValue: [110, 380],
            purpose: 'Reduces merge risk with AI-reviewed, environment-aware change control.',
            features: [
                'Cuts regression risk by simulating merges across large repos.',
                'Controls IDEs, CI, and infra via Kernel/Unix drivers for DevOps scale.',
                'Provision toolchains automatically to normalize developer environments.'
            ],
            audiences: ['Engineering orgs', 'DevOps', 'Platform teams']
        },
        {
            id: '10.3',
            name: 'Commit → Task Generator',
            category: 'Core',
            artifact_type: 'Capability',
            tier: 'Module',
            capability_layer: 'Core',
            lifetimeValue: [30, 100],
            purpose: 'Turns code diffs into structured backlog items tied to environment drift.',
            features: [
                'Pushes tasks into tools like Jira/Linear and tracks completion via real branch state.',
                'Validates closure by running build/test commands directly on Unix systems.',
                'Bridges code, infra, and environment actions for platform engineering insight.'
            ],
            audiences: ['Engineering managers', 'Scrum masters', 'IT automation']
        },
        {
            id: '10.4',
            name: 'Research Orchestrator & Simulation Hub (Advanced I)',
            category: 'Advanced',
            artifact_type: 'Capability',
            tier: 'Module',
            capability_layer: 'Advanced',
            lifetimeValue: [30, 130],
            purpose: 'Accelerates scientific and quantitative research through orchestrated experiments.',
            features: [
                'Controls notebooks, HPC jobs, and lab UIs with Kernel/Unix drivers.',
                'Sets up CUDA/MPI/tooling stacks on demand via package drivers.',
                'Stores workflows as Capsules with reproducible Evidence Packs.'
            ],
            audiences: ['Labs', 'Quant funds', 'Industrial R&D']
        },
        {
            id: '10.5',
            name: 'Writer Workstation & Narrative Guidance Engine',
            category: 'Core',
            artifact_type: 'Capability',
            tier: 'Module',
            capability_layer: 'Core',
            lifetimeValue: [18, 80],
            purpose: 'Creator OS blending continuity-aware drafting with production automation.',
            features: [
                'Project-aware co-author maintaining canon, arcs, and manuscripts.',
                'Operates Word/Scrivener/Final Draft plus local render pipelines.',
                'Installs creative toolchains and packages automatically per project.'
            ],
            audiences: ['Authors', 'Studios', 'Game narrative teams']
        },
        {
            id: '10.6',
            name: 'Archive / Continuity / Resonance Engine',
            category: 'Core',
            artifact_type: 'Capability',
            tier: 'Module',
            capability_layer: 'Core',
            lifetimeValue: [160, 500],
            purpose: 'Long-term organizational memory that tracks knowledge plus environment history.',
            features: [
                'Ingests from any interface including legacy UIs and Unix-level telemetry.',
                'Captures package/version histories for reproducibility and compliance.',
                'Stores Capsules, workflows, and Evidence Packs as first-class artifacts.'
            ],
            audiences: ['Knowledge management', 'Compliance', 'Research archives']
        },
        {
            id: '10.7',
            name: 'Cybersecurity Guardian',
            category: 'Core',
            artifact_type: 'Capability',
            tier: 'Module',
            capability_layer: 'Core',
            lifetimeValue: [35, 150],
            purpose: 'Security companion enforcing guardrails across developers, endpoints, and agents.',
            features: [
                'Adjusts configs, closes sessions, and inspects systems through Kernel/Unix drivers.',
                'Controls package installations to enforce secure baselines and remediate drift.',
                'Shares reusable Security Capsules and auto-remediation playbooks.'
            ],
            audiences: ['SecOps', 'DevSecOps', 'Compliance']
        },
        {
            id: '10.8',
            name: 'Business Accounting & Financing Console',
            category: 'Core',
            artifact_type: 'Capability',
            tier: 'Module',
            capability_layer: 'Core',
            lifetimeValue: [45, 190],
            purpose: 'Finance OS bridging productivity tools with accounting automation.',
            features: [
                'Logs into bank portals, edits spreadsheets, and runs accounting flows automatically.',
                'Manages secure local finance tooling via Unix binaries for privacy-first teams.',
                'Encodes invoicing and reconciliation processes as Capsule Packs.'
            ],
            audiences: ['Creators', 'SMBs', 'Finance departments']
        },
        {
            id: '10.9',
            name: 'Record Auditor & Logbook',
            category: 'Core',
            artifact_type: 'Capability',
            tier: 'Module',
            capability_layer: 'Core',
            lifetimeValue: [35, 130],
            purpose: 'End-to-end provenance stack logging intents, actions, and environment changes.',
            features: [
                'Captures UI activity plus system-level commands and resource usage.',
                'Tracks package installs/removals with actor attribution.',
                'Links every Capsule run and workflow into an auditable narrative timeline.'
            ],
            audiences: ['Regulated industries', 'Audit teams', 'Ops leadership']
        },
        {
            id: '10.10',
            name: 'Executable Capsules & Marketplace',
            category: 'Core',
            artifact_type: 'Capability',
            tier: 'System',
            capability_layer: 'Core',
            lifetimeValue: [230, 750],
            purpose: 'Marketplace for executable workflows bound to drivers and environments.',
            features: [
                'Packages Capsules with driver bindings and Unix command graphs.',
                'Self-provisions required tooling via package manifests.',
                'Supports Capsule Packs, pricing, and revenue sharing for creators.'
            ],
            audiences: ['Developers', 'Consultancies', 'Automation vendors']
        },
        {
            id: '10.11',
            name: 'Policy & Governance Engine',
            category: 'Core',
            artifact_type: 'Capability',
            tier: 'System',
            capability_layer: 'Core',
            lifetimeValue: [160, 450],
            purpose: 'Central enforcement plane governing models, drivers, packages, and Capsules.',
            features: [
                'Controls which commands, binaries, or models an agent may execute.',
                'Extends governance to package sources, versions, and Capsule permissions.',
                'Applies guardrails to Capsule creation, execution, and workflow sharing.'
            ],
            audiences: ['CIOs', 'Risk officers', 'IT governance']
        },
        {
            id: '10.12',
            name: 'AI Billing & Usage Fabric',
            category: 'Core',
            artifact_type: 'Capability',
            tier: 'Platform',
            capability_layer: 'Core',
            lifetimeValue: [30, 140],
            purpose: 'Metering and chargeback layer for multi-model, multi-driver automation.',
            features: [
                'Meters system-level actions, commands, and compute triggered by agents.',
                'Tracks package installs and environment convergences as billable events.',
                'Attributes cost/value to Capsule runs, Packs, and workflows for pricing.'
            ],
            audiences: ['Finance IT', 'Platform teams', 'Marketplace operators']
        },
        {
            id: '10.13',
            name: 'AI OS Platform',
            category: 'Core',
            artifact_type: 'Platform',
            tier: 'Platform',
            capability_layer: 'Core',
            lifetimeValue: [950, 2500],
            purpose: 'Fully integrated stack combining drivers, environments, workflows, and marketplace.',
            features: [
                'Operates apps, OS, Unix toolchains, and local environments across fleets.',
                'Governed capsules plus archive and billing sit over the entire execution footprint.',
                'Enables capsule-driven marketplaces and governance for civilization-scale automation.'
            ],
            audiences: ['Platform owners', 'Large enterprises', 'Ecosystem stewards']
        },
        {
            id: '10.14',
            name: 'AI OS Research, Simulation & Digital Twin Platform Envelope',
            category: 'Advanced',
            artifact_type: 'Platform',
            tier: 'Platform',
            capability_layer: 'Advanced',
            lifetimeValue: [40, 160],
            purpose: 'Extends research orchestrator into full digital twin management for physical systems.',
            features: [
                'Links simulation, telemetry, and control Capsules for industrial systems.',
                'Supports CAD/CAE/HPC integrations for engineering-grade twins.',
                'Pairs with Cybersecurity Guardian and Policy Engine for safety-critical ops.'
            ],
            audiences: ['Manufacturing', 'Energy', 'Defense R&D']
        },
        {
            id: '10.15',
            name: 'Autonomous Research Conductor (ARC)',
            category: 'Super',
            artifact_type: 'Capability',
            tier: 'System',
            capability_layer: 'Super',
            lifetimeValue: [60, 220],
            purpose: 'Long-horizon planner coordinating experiments, teams, and compute budgets.',
            features: [
                'Plans and adjusts research programs automatically over months/years.',
                'Reallocates compute, funding, and Capsules based on observed outcomes.',
                'Relies on Archive, Simulation Hub, and Billing telemetry.'
            ],
            audiences: ['Pharma', 'Materials science', 'Frontier labs']
        },
        {
            id: '10.16',
            name: 'Symbolic–Numeric Theory Discovery Engine',
            category: 'Super',
            artifact_type: 'Capability',
            tier: 'System',
            capability_layer: 'Super',
            lifetimeValue: [40, 180],
            purpose: 'Discovers candidate equations and laws by blending symbolic reasoning and simulation.',
            features: [
                'Generates and tests hypotheses numerically and symbolically.',
                'Maintains catalog of ranked theories with evidence and counterexamples.',
                'Feeds Canon of Truth and Ontological Compiler layers.'
            ],
            audiences: ['Advanced research', 'Quant funds', 'Scientific institutions']
        },
        {
            id: '10.17',
            name: 'Self-Evolving Capsule Ecosystem',
            category: 'Super',
            artifact_type: 'Capability',
            tier: 'System',
            capability_layer: 'Super',
            lifetimeValue: [80, 260],
            purpose: 'Lets Capsule marketplace learn from usage and auto-improve under governance.',
            features: [
                'Monitors Capsule performance, drift, and failure modes.',
                'Auto-tunes parameters and decomposes/merges Capsules safely.',
                'Requires Policy & Governance plus Auditor oversight.'
            ],
            audiences: ['Marketplace operators', 'Automation PMs', 'Governance teams']
        },
        {
            id: '10.18',
            name: 'Enterprise & Civilization Knowledge Market',
            category: 'Super',
            artifact_type: 'Capability',
            tier: 'System',
            capability_layer: 'Super',
            lifetimeValue: [120, 400],
            purpose: 'Cross-organization exchange of Capsules, blueprints, and encoded IP.',
            features: [
                'Lets orgs license and monetize best practices as Capsule Packs.',
                'Supports professional guilds and consortia sharing standards.',
                'Integrates with Billing, Governance, and HyperMesh fabrics.'
            ],
            audiences: ['Enterprises', 'Regulators', 'Sector alliances']
        },
        {
            id: '10.19',
            name: 'Agentic Enterprise Twin',
            category: 'Super',
            artifact_type: 'Capability',
            tier: 'System',
            capability_layer: 'Super',
            lifetimeValue: [70, 230],
            purpose: 'Live twin of an organization’s structure, Capsule graph, and KPIs.',
            features: [
                'Simulates org changes, staffing, and capability investments.',
                'Understands how work is executed versus planned for strategic planning.',
                'Pairs with Reality Twin Mesh and Strategy Garden.'
            ],
            audiences: ['C-suite', 'Strategy teams', 'Operations leaders']
        },
        {
            id: '10.20',
            name: 'Global Policy & Regulation Fabric',
            category: 'Super',
            artifact_type: 'Capability',
            tier: 'System',
            capability_layer: 'Super',
            lifetimeValue: [90, 300],
            purpose: 'Executable regulation capsules shared across jurisdictions and orgs.',
            features: [
                'Encodes laws and standards as runnable Capsules.',
                'Supports collaborative rulemaking and stress testing.',
                'Foundation for HyperRegent and AI Court capabilities.'
            ],
            audiences: ['Regulators', 'Auditors', 'Global enterprises']
        },
        {
            id: '10.21',
            name: 'Temporal Reasoning & Time-Cascade Engine',
            category: 'Super',
            artifact_type: 'Capability',
            tier: 'System',
            capability_layer: 'Super',
            lifetimeValue: [40, 150],
            purpose: 'Models how policies and Capsules propagate over time with branching futures.',
            features: [
                'Projects the downstream impact of automation choices.',
                'Integrates with Archive and Temporal Backtesting.',
                'Supports scenario planning out to multiple quarters/years.'
            ],
            audiences: ['Strategists', 'Risk teams', 'Program management']
        },
        {
            id: '10.22',
            name: 'Cross-Domain Knowledge & Law Synthesizer',
            category: 'Super',
            artifact_type: 'Capability',
            tier: 'System',
            capability_layer: 'Super',
            lifetimeValue: [50, 180],
            purpose: 'Finds reusable abstractions and Capsule templates across industries.',
            features: [
                'Searches for shared structures in flows, constraints, and equilibria.',
                'Suggests Capsule templates that port across sectors.',
                'Acts as meta-architect for Capsule universe.'
            ],
            audiences: ['Consulting', 'System architects', 'Policy designers']
        },
        {
            id: '10.23',
            name: 'Inter-OS Knowledge Network',
            category: 'Super',
            artifact_type: 'Capability',
            tier: 'System',
            capability_layer: 'Super',
            lifetimeValue: [35, 140],
            purpose: 'Shares anonymized patterns and Capsule templates between installations.',
            features: [
                'Distributes best practices without leaking raw data.',
                'Helps smaller players benefit from large-ecosystem learnings.',
                'Boosts adoption through network effects.'
            ],
            audiences: ['Partner ecosystems', 'SMBs', 'Alliances']
        },
        {
            id: '10.24',
            name: 'Autonomous Knowledge Steward (AIC Super Mode)',
            category: 'Super',
            artifact_type: 'Capability',
            tier: 'System',
            capability_layer: 'Super',
            lifetimeValue: [30, 110],
            purpose: 'Always-on curator that prevents semantic drift and redundancy.',
            features: [
                'Hunts contradictions and dead frameworks in archives.',
                'Suggests refactors and consolidations of knowledge.',
                'Ideal for governments and institutions with deep histories.'
            ],
            audiences: ['Governments', 'Universities', 'Large enterprises']
        },
        {
            id: '10.25',
            name: 'HyperMesh',
            category: 'Hyper',
            artifact_type: 'Capability',
            tier: 'System',
            capability_layer: 'Hyper',
            lifetimeValue: [120, 380],
            purpose: 'Execution mesh linking multiple AI OS installations under shared policy.',
            features: [
                'Allows workflows to span suppliers, partners, and regulators.',
                'Manages trust and compliance across organizations.',
                'Backbone for inter-org automation beyond RPA.'
            ],
            audiences: ['Supply chains', 'Government networks', 'Large alliances']
        },
        {
            id: '10.26',
            name: 'HyperFoundry',
            category: 'Hyper',
            artifact_type: 'Capability',
            tier: 'System',
            capability_layer: 'Hyper',
            lifetimeValue: [60, 220],
            purpose: 'Autonomous venture ideation layer fueled by Capsule market signals.',
            features: [
                'Identifies under-served workflows and composes Capsule bundles.',
                'Supports corporate innovation programs and Capsule-native VC models.',
                'Transforms marketplace telemetry into product strategies.'
            ],
            audiences: ['Innovation labs', 'Venture studios', 'Product strategists']
        },
        {
            id: '10.27',
            name: 'HyperLab',
            category: 'Hyper',
            artifact_type: 'Capability',
            tier: 'System',
            capability_layer: 'Hyper',
            lifetimeValue: [50, 180],
            purpose: 'Cross-organization research grid with pooled data, compute, and Capsules.',
            features: [
                'Enables sector-wide benchmarks with shared Evidence Packs.',
                'Supports reproducible consortia experiments.',
                'Attractive to pharma, climate, defense, and standards bodies.'
            ],
            audiences: ['Research consortia', 'Standards bodies', 'Joint ventures']
        },
        {
            id: '10.28',
            name: 'HyperRegent',
            category: 'Hyper',
            artifact_type: 'Capability',
            tier: 'System',
            capability_layer: 'Hyper',
            lifetimeValue: [70, 240],
            purpose: 'Regulators run Capsules directly on logs, twins, and workflows for oversight.',
            features: [
                'Provides first-class tenancy for regulators/auditors.',
                'Enables near real-time oversight and collaborative rulemaking.',
                'Stress-tests rules continuously across Capsule networks.'
            ],
            audiences: ['Regulators', 'Audit consortia', 'Critical infrastructure']
        },
        {
            id: '10.29',
            name: 'HyperSymphony',
            category: 'Hyper',
            artifact_type: 'Capability',
            tier: 'System',
            capability_layer: 'Hyper',
            lifetimeValue: [60, 210],
            purpose: 'Coordinates cross-org workflows with shared revenue alignment.',
            features: [
                'Capsules from multiple orgs orchestrated like instruments.',
                'Ideal for logistics, trade finance, and joint ventures.',
                'Supports shared incentives and settlement models.'
            ],
            audiences: ['Supply chain alliances', 'Financial networks', 'Joint ventures']
        },
        {
            id: '10.30',
            name: 'HyperDaemon',
            category: 'Hyper',
            artifact_type: 'Capability',
            tier: 'System',
            capability_layer: 'Hyper',
            lifetimeValue: [80, 260],
            purpose: 'Systemic risk sentinel monitoring Capsule networks and markets.',
            features: [
                'Detects emergent fragility and cascading failures.',
                'Monitors exploitation surfaces across infra and workflows.',
                'Helps large ecosystems avoid self-inflicted disasters.'
            ],
            audiences: ['Financial systems', 'Critical infrastructure', 'Cloud providers']
        },
        {
            id: '10.31',
            name: 'HyperContinuity',
            category: 'Hyper',
            artifact_type: 'Capability',
            tier: 'System',
            capability_layer: 'Hyper',
            lifetimeValue: [40, 150],
            purpose: 'Maintains portable identity and canon across careers and organizations.',
            features: [
                'Tracks lifetime knowledge and trust records for individuals/entities.',
                'Supports professions where accreditation and reputation matter.',
                'Ensures continuity through job transitions and org shifts.'
            ],
            audiences: ['Professional guilds', 'Defense', 'Public sector']
        },
        {
            id: '10.32',
            name: 'HyperGenesis',
            category: 'Hyper',
            artifact_type: 'Capability',
            tier: 'System',
            capability_layer: 'Hyper',
            lifetimeValue: [50, 190],
            purpose: 'High-fidelity world simulation and staged rollout engine.',
            features: [
                'Tests macro strategies before deploying in reality.',
                'Essential for governments and mega-firms with civilization-scale moves.',
                'Pairs with digital twin meshes and Capsule graphs.'
            ],
            audiences: ['Governments', 'Mega enterprises', 'Think tanks']
        },
        {
            id: '10.33',
            name: 'Cognitive Twin Fabric',
            category: 'Ultra',
            artifact_type: 'Capability',
            tier: 'System',
            capability_layer: 'Ultra',
            lifetimeValue: [60, 210],
            purpose: 'Dynamic twins for people and teams capturing capabilities and history.',
            features: [
                'Optimizes staffing, mentorship, and delegation across humans and agents.',
                'Understands preferences, constraints, and learning paths.',
                'Vital for large org talent networks.'
            ],
            audiences: ['HR leadership', 'Consultancies', 'Large enterprises']
        },
        {
            id: '10.34',
            name: 'Strategy Garden & Capsule Fund',
            category: 'Ultra',
            artifact_type: 'Capability',
            tier: 'System',
            capability_layer: 'Ultra',
            lifetimeValue: [40, 160],
            purpose: 'Executable portfolio of strategic bets tied to Capsule graphs.',
            features: [
                'Allocates budget, people, and environments to initiatives.',
                'Tracks ROI and recommends pruning or doubling down.',
                'Connects corporate strategy to automation reality.'
            ],
            audiences: ['Corporate strategy', 'Investment offices', 'Program management']
        },
        {
            id: '10.35',
            name: 'Reality Twin Mesh',
            category: 'Ultra',
            artifact_type: 'Capability',
            tier: 'System',
            capability_layer: 'Ultra',
            lifetimeValue: [70, 230],
            purpose: 'Mesh of digital twins for products, infrastructure, and org structures.',
            features: [
                'Simulates propagation of changes across tech, people, finance, and regulation.',
                'Supports risk analysis for ecosystem-scale transformations.',
                'Foundation for Hyper and Supreme-tier planning tools.'
            ],
            audiences: ['Large enterprises', 'Governments', 'Systems integrators']
        },
        {
            id: '10.36',
            name: 'Temporal Backtesting Engine',
            category: 'Ultra',
            artifact_type: 'Capability',
            tier: 'System',
            capability_layer: 'Ultra',
            lifetimeValue: [40, 150],
            purpose: 'Replays historical decisions with alternate Capsule graphs and staffing.',
            features: [
                'Learns from counterfactual “ghost decisions.”',
                'Feeds adjustments into future strategy and automation designs.',
                'Pairs with Auditor, Archive, and Canon of Truth.'
            ],
            audiences: ['Risk teams', 'Strategy', 'Operations research']
        },
        {
            id: '10.37',
            name: 'Law-of-the-OS & AI Court',
            category: 'Ultra',
            artifact_type: 'Capability',
            tier: 'System',
            capability_layer: 'Ultra',
            lifetimeValue: [50, 180],
            purpose: 'Internal legal system handling disputes between agents, Capsules, and policies.',
            features: [
                'Defines responsibility and recourse for automated work.',
                'Essential for regulated deployments of autonomous workflows.',
                'Integrates with Policy Engine and HyperRegent oversight.'
            ],
            audiences: ['Legal teams', 'Governments', 'Large enterprises']
        },
        {
            id: '10.38',
            name: 'Inter-OS Federation',
            category: 'Ultra',
            artifact_type: 'Capability',
            tier: 'System',
            capability_layer: 'Ultra',
            lifetimeValue: [60, 210],
            purpose: 'Federation logic for standards, shared Capsules, and trust across OS networks.',
            features: [
                'Governs cross-network Capsules and conflict resolution.',
                'Essential when platform becomes critical infrastructure.',
                'Supports interoperability between regional or sector deployments.'
            ],
            audiences: ['Global enterprises', 'Alliances', 'Platform operators']
        },
        {
            id: '10.39',
            name: 'Meta-Design Studio',
            category: 'Ultra',
            artifact_type: 'Capability',
            tier: 'System',
            capability_layer: 'Ultra',
            lifetimeValue: [45, 160],
            purpose: 'Self-improving OS that redesigns Capsules, UX, and policies based on telemetry.',
            features: [
                'Identifies friction and failure patterns automatically.',
                'Proposes new Capsule types and experience flows.',
                'Makes the platform adaptive rather than static.'
            ],
            audiences: ['Platform teams', 'UX research', 'Product owners']
        },
        {
            id: '10.40',
            name: 'Cognitive Economy Engine',
            category: 'Ultra',
            artifact_type: 'Capability',
            tier: 'System',
            capability_layer: 'Ultra',
            lifetimeValue: [70, 240],
            purpose: 'Allocator deciding which human, agent, or Capsule should execute work.',
            features: [
                'Optimizes ROI by minimizing wasted cognition and compute.',
                'Balances workloads across people, agents, and infrastructure.',
                'Acts as central allocator for entire organizations.'
            ],
            audiences: ['Operations', 'Finance', 'Workforce planners']
        },
        {
            id: '10.41',
            name: 'Multi-Reality Storyboard',
            category: 'Ultra',
            artifact_type: 'Capability',
            tier: 'System',
            capability_layer: 'Ultra',
            lifetimeValue: [40, 150],
            purpose: 'Visual sandbox of branching futures and Capsule graphs.',
            features: [
                'Lets leaders inspect futures as immersive narratives with metrics.',
                'Pairs with Strategy Garden and Time-Cascade engines.',
                'Supports executive communication of complex automation plans.'
            ],
            audiences: ['Executive teams', 'Program managers', 'Design strategists']
        },
        {
            id: '10.42',
            name: 'Alignment Monitor',
            category: 'Ultra',
            artifact_type: 'Capability',
            tier: 'System',
            capability_layer: 'Ultra',
            lifetimeValue: [50, 170],
            purpose: 'Continuous watchdog verifying automation behavior matches declared goals.',
            features: [
                'Flags misaligned Capsules, policies, or emergent patterns.',
                'Critical for governance and safety as automation power grows.',
                'Integrates with Auditor and Policy Engine for response loops.'
            ],
            audiences: ['Governance', 'Safety teams', 'Risk officers']
        },
        {
            id: '10.43',
            name: 'Ontological Compiler',
            category: 'Supreme',
            artifact_type: 'Capability',
            tier: 'System',
            capability_layer: 'Supreme',
            lifetimeValue: [60, 220],
            purpose: 'Compiles organizational worldviews into formal ontologies for all Capsules.',
            features: [
                'Reduces integration pain by aligning concepts across systems.',
                'Provides shared conceptual substrate for agents and policies.',
                'Prevents semantic drift in large automation estates.'
            ],
            audiences: ['Enterprise architects', 'Governments', 'Large research orgs']
        },
        {
            id: '10.44',
            name: 'Canon of Truth Engine',
            category: 'Supreme',
            artifact_type: 'Capability',
            tier: 'System',
            capability_layer: 'Supreme',
            lifetimeValue: [80, 260],
            purpose: 'Tracks claims, models, and evidence to maintain a living canon of truth.',
            features: [
                'Records beliefs, probabilities, and disputes over time.',
                'Pairs with theory discovery and backtesting engines.',
                'Helps orgs unlearn falsehoods and reinforce validated knowledge.'
            ],
            audiences: ['Research institutions', 'Governments', 'Large enterprises']
        },
        {
            id: '10.45',
            name: 'Reality Contract Layer',
            category: 'Supreme',
            artifact_type: 'Capability',
            tier: 'System',
            capability_layer: 'Supreme',
            lifetimeValue: [50, 180],
            purpose: 'Binds Capsules to explicit reality conditions and rollback clauses.',
            features: [
                'Defines triggers for updates, reverts, and remediation.',
                'Makes automation accountable to observed metrics.',
                'Provides formal safety nets for high-stakes operations.'
            ],
            audiences: ['Critical infrastructure', 'Finance', 'Regulated industries']
        },
        {
            id: '10.46',
            name: 'Human–System Co-Evolution Orchestrator',
            category: 'Supreme',
            artifact_type: 'Capability',
            tier: 'System',
            capability_layer: 'Supreme',
            lifetimeValue: [40, 150],
            purpose: 'Plans how humans and automated systems evolve together over decades.',
            features: [
                'Orchestrates reskilling, role evolution, and cultural change.',
                'Prevents misalignment and social fracture during automation.',
                'Critical for civilization-scale transitions.'
            ],
            audiences: ['Governments', 'Large enterprises', 'Education systems']
        },
        {
            id: '10.47',
            name: 'Successor Architect & Legacy Seeder',
            category: 'Supreme',
            artifact_type: 'Capability',
            tier: 'System',
            capability_layer: 'Supreme',
            lifetimeValue: [30, 120],
            purpose: 'Encodes institutional and personal legacy into Capsules for future generations.',
            features: [
                'Captures doctrines, methods, and principles for successors.',
                'Ideal for universities, dynastic orgs, and long-horizon funds.',
                'Ensures continuity of knowledge and intent.'
            ],
            audiences: ['Universities', 'Family offices', 'Long-term institutions']
        },
        {
            id: '10.48',
            name: 'Unified Law of Work & Meaning Engine',
            category: 'Supreme',
            artifact_type: 'Capability',
            tier: 'System',
            capability_layer: 'Supreme',
            lifetimeValue: [80, 280],
            purpose: 'Defines meta-objectives describing what “good” and “aligned” mean for the ecosystem.',
            features: [
                'Evaluates Capsules, policies, and strategies against philosophical criteria.',
                'Becomes center of gravity for platform behavior over time.',
                'Informs governance, Canon of Truth, and Co-Evolution orchestration.'
            ],
            audiences: ['Executive leadership', 'Governments', 'Civilization-scale stewards']
        }
    ];
})();
