/**
 * Navigation Manifest - Spec-Driven Structure
 * Based on Technical Spec Sheet Version 6
 * 
 * Top-level categories map to major spec sections
 * Left-side pages map to subsections within each category
 */

import {
  LayoutDashboard,
  CheckSquare,
  FolderKanban,
  MessageSquare,
  BookOpen,
  FlaskConical,
  LayoutTemplate,
  Terminal,
  Brain,
  Cpu,
  ServerCog,
  Bot,
  Zap,
  Layers,
  Workflow,
  Package,
  Wrench,
  Shield,
  Satellite,
  Eye,
  Dna,
  Plug,
  Network,
  Activity,
  Database,
  FileText,
  Archive,
  Search as SearchIcon,
  BarChart3,
  Radio,
  CreditCard,
  ClipboardList,
  Settings,
  Users,
  Target,
  Compass,
  Sparkles,
  HardDrive,
  Key,
  Lock,
  TrendingUp,
  Server,
  Cloud,
  AlertTriangle,
  GitBranch,
  Code,
  Calculator,
  FileCheck,
  Monitor,
  Container,
  Globe,
  Upload,
} from 'lucide-react'

export interface NavPage {
  path: string
  icon: React.ComponentType<{ className?: string }>
  label: string
  spec?: string
  description?: string
  backend?: string
  status?: 'existing' | 'new' | 'planned'
}

export interface NavGroup {
  label: string
  spec?: string
  description?: string
  items: NavPage[]
}

export interface NavCategory {
  path: string
  icon: React.ComponentType<{ className?: string }>
  label: string
  spec: string
  description: string
  groups: NavGroup[]
}

export const navigationManifest: NavCategory[] = [
  {
    path: '/mission',
    icon: Target,
    label: 'Mission & Architecture',
    spec: '§0, §1, §2',
    description: 'Mission, modes, identity, architecture, and planes',
    groups: [
      {
        label: 'Mission & Identity',
        spec: '§0',
        description: 'Mission, modes, identity surfaces, cognitive agents',
        items: [
          { path: '/mission/overview', icon: Target, label: 'Mission & Scope', spec: '§0.1', backend: 'routers.platform', status: 'new' },
          { path: '/mission/modes', icon: Layers, label: 'Deployment Modes', spec: '§0.3', backend: 'routers.platform', status: 'new' },
          { path: '/mission/identity', icon: Users, label: 'Identity & Roles', spec: '§0.4', backend: 'routers.settings', status: 'new' },
          { path: '/ai/personas', icon: Bot, label: 'Cognitive Agents & Personas', spec: '§0.5', backend: 'routers.personas', status: 'new' },
          { path: '/mission/daemons', icon: ServerCog, label: 'Daemon Families', spec: '§0.6', backend: 'routers.ai_systems', status: 'new' },
          { path: '/mission/ai-stack', icon: Brain, label: 'AI + Driver Stack', spec: '§0.7', backend: 'routers.ai_systems', status: 'new' },
          { path: '/mission/models', icon: Dna, label: 'Model Provider Layer', spec: '§0.8', backend: 'routers.ai_systems', status: 'new' },
        ],
      },
      {
        label: 'Architecture & Principles',
        spec: '§1',
        description: 'Logical architecture, components, principles',
        items: [
          { path: '/mission/architecture', icon: Layers, label: 'Architecture Overview', spec: '§1.1', backend: 'routers.platform', status: 'new' },
          { path: '/mission/components', icon: Package, label: 'Major Components', spec: '§1.2', backend: 'routers.platform', status: 'new' },
          { path: '/mission/principles', icon: Shield, label: 'Architectural Principles', spec: '§1.3', backend: 'routers.platform', status: 'new' },
          { path: '/mission/mapping', icon: Network, label: 'Component Mapping', spec: '§1.4-1.5', backend: 'routers.platform', status: 'new' },
          { path: '/mission/orchestrator', icon: Cpu, label: 'Driver-Aware Orchestrator', spec: '§1.7', backend: 'routers.ai_systems', status: 'new' },
        ],
      },
      {
        label: 'Planes Architecture',
        spec: '§2',
        description: 'Data, control, and governance planes',
        items: [
          { path: '/mission/planes/data', icon: Database, label: 'Data Plane', spec: '§2.1', backend: 'routers.platform', status: 'new' },
          { path: '/mission/planes/control', icon: Cpu, label: 'Control Plane', spec: '§2.2', backend: 'routers.platform', status: 'new' },
          { path: '/mission/planes/governance', icon: Shield, label: 'Governance Plane', spec: '§2.3', backend: 'routers.settings', status: 'new' },
          { path: '/mission/planes/cross-plane', icon: Network, label: 'Cross-Plane Flows', spec: '§2.4', backend: 'routers.platform', status: 'new' },
        ],
      },
    ],
  },
  {
    path: '/dashboard',
    icon: LayoutDashboard,
    label: 'Mission Control',
    spec: '§1.7, §3.3-3.4',
    description: 'Core orchestrator surfaces for driver-aware planning loop',
    groups: [
      {
        label: 'Core Flight Deck',
        spec: '§1.7',
        description: 'Dashboard, tasks, and projects for the driver-aware loop',
        items: [
          { path: '/', icon: LayoutDashboard, label: 'Dashboard', spec: '§1.7.1', backend: 'routers.dashboard', status: 'existing' },
          { path: '/tasks', icon: CheckSquare, label: 'Tasks', spec: '§3.4', backend: 'routers.tasks', status: 'existing' },
          { path: '/projects', icon: FolderKanban, label: 'Projects', spec: '§3.3, §7.2', backend: 'routers.projects', status: 'existing' },
        ],
      },
      {
        label: 'Engagement & Persona Surfaces',
        spec: '§7.12, §0.5',
        description: 'Chat, collaboration, and personalization',
        items: [
          { path: '/chat', icon: MessageSquare, label: 'Chat', spec: '§1.7.2, §7.12.3', backend: 'routers.chat', status: 'existing' },
          { path: '/chat/responses', icon: Sparkles, label: 'Responses API Chat', spec: '§1.7.2', backend: 'routers.responses_api', status: 'new', description: 'Modern chat interface with Responses API' },
          { path: '/collaboration', icon: Users, label: 'Collaboration', spec: '§7.12', backend: 'routers.projects', status: 'existing' },
          { path: '/personalization', icon: Target, label: 'Personalization', spec: '§0.5', backend: 'routers.settings', status: 'existing' },
          { path: '/search', icon: SearchIcon, label: 'Search & Discovery', spec: '§6.5, §3.6', backend: 'routers.search', status: 'existing' },
        ],
      },
    ],
  },
  {
    path: '/workspaces',
    icon: BookOpen,
    label: 'Workspaces',
    spec: '§7',
    description: 'Domain engines and collaboration workspaces',
    groups: [
      {
        label: 'Dev & DevOps Workspace',
        spec: '§7.3',
        description: 'Code & change intelligence, CI/CD integration',
        items: [
          { path: '/workspaces/dev', icon: Code, label: 'Dev Workspace', spec: '§7.3', backend: 'routers.ai_systems', status: 'new' },
          { path: '/workspaces/dev/merge-advisor', icon: GitBranch, label: 'Code Merge Advisor', spec: '§7.3.1', backend: 'routers.git', status: 'new' },
          { path: '/workspaces/dev/commit-tasks', icon: CheckSquare, label: 'Commit → Task Generator', spec: '§7.3.2', backend: 'routers.git', status: 'new' },
          { path: '/workspaces/dev/cicd', icon: Workflow, label: 'CI/CD Integration', spec: '§7.3.4', backend: 'routers.workflow_orchestration', status: 'new' },
          { path: '/work/tools', icon: Terminal, label: 'Developer Tools', spec: '§7.3.5', backend: 'routers.terminal', status: 'existing' },
        ],
      },
      {
        label: 'Research & Simulation Workspace',
        spec: '§7.4',
        description: 'Unified research lab, simulations, and digital twins',
        items: [
          { path: '/research', icon: FlaskConical, label: 'Research Hub', spec: '§7.4.1', backend: 'routers.research', status: 'existing' },
          { path: '/workspaces/research/lab', icon: FlaskConical, label: 'Unified Research Lab', spec: '§7.4.2', backend: 'routers.research', status: 'new' },
          { path: '/workspaces/research/simulation', icon: Layers, label: 'Simulation Workbench', spec: '§7.4.3', backend: 'routers.research', status: 'new' },
          { path: '/workspaces/research/experiments', icon: Dna, label: 'Experiment Design', spec: '§7.4.4', backend: 'routers.research', status: 'new' },
          { path: '/workspaces/research/validation', icon: FileCheck, label: 'Model Validation', spec: '§7.4.5', backend: 'routers.neural_architecture', status: 'new' },
          { path: '/workspaces/research/digital-twins', icon: Layers, label: 'Digital Twin Builder', spec: '§7.4.6', backend: 'routers.neural_architecture', status: 'new' },
          { path: '/workspaces/research/hpc', icon: Server, label: 'HPC Orchestrator', spec: '§7.4.12', backend: 'routers.research', status: 'new' },
        ],
      },
      {
        label: 'Writer Workspace',
        spec: '§7.5',
        description: 'Writer workstation, canon & lore management',
        items: [
          { path: '/work/writer', icon: BookOpen, label: 'Writer Workstation', spec: '§7.5.1', backend: 'routers.writer', status: 'existing' },
          { path: '/work/templates', icon: LayoutTemplate, label: 'Templates', spec: '§8.20', backend: 'routers.templates', status: 'existing' },
          { path: '/workspaces/writer/canon', icon: FileText, label: 'Canon & Lore', spec: '§7.5.2', backend: 'routers.writer', status: 'new' },
          { path: '/workspaces/writer/narrative', icon: Sparkles, label: 'Narrative Guidance', spec: '§7.5.3', backend: 'routers.writer', status: 'new' },
          { path: '/workspaces/writer/qa', icon: FileCheck, label: 'Story QA & Continuity', spec: '§7.5.4', backend: 'routers.writer', status: 'new' },
        ],
      },
      {
        label: 'Cybersecurity Workspace',
        spec: '§7.7',
        description: 'Security guardian, threat modeling, auto-remediation',
        items: [
          { path: '/ai/security', icon: Shield, label: 'Security Guardian', spec: '§7.7.1', backend: 'routers.security_threat', status: 'existing' },
          { path: '/workspaces/cyber/threat-modeling', icon: AlertTriangle, label: 'Threat Modeling', spec: '§7.7.3', backend: 'routers.security_threat', status: 'new' },
          { path: '/workspaces/cyber/auto-remediation', icon: Wrench, label: 'Auto-Remediation', spec: '§7.7.2', backend: 'routers.autofix', status: 'new' },
        ],
      },
      {
        label: 'Business & Finance Workspace',
        spec: '§7.8',
        description: 'Business accounting, financial scenario simulation',
        items: [
          { path: '/workspaces/finance', icon: Calculator, label: 'Business Console', spec: '§7.8.1', backend: 'routers.analytics', status: 'new' },
          { path: '/workspaces/finance/scenarios', icon: TrendingUp, label: 'Strategy Simulation', spec: '§7.8.2-7.8.3', backend: 'routers.analytics', status: 'new' },
        ],
      },
      {
        label: 'Operator & SRE Workspace',
        spec: '§7.10',
        description: 'Health monitoring, sandbox management, reliability',
        items: [
          { path: '/workspaces/sre', icon: Monitor, label: 'SRE Workspace', spec: '§7.10', backend: 'routers.runtime_diagnostics', status: 'new' },
          { path: '/workspaces/sre/health', icon: Activity, label: 'Health & Drift Monitors', spec: '§7.10.1', backend: 'routers.runtime_diagnostics', status: 'new' },
          { path: '/workspaces/sre/sandbox', icon: Container, label: 'Sandbox Management', spec: '§7.10.2', backend: 'routers.platform', status: 'new' },
          { path: '/workspaces/sre/reliability', icon: Server, label: 'Reliability Dashboard', spec: '§7.10.3', backend: 'routers.runtime_diagnostics', status: 'new' },
        ],
      },
      {
        label: 'Archive & Continuity Workspace',
        spec: '§7.6',
        description: 'Archive, continuity, resonance, temporal reconstruction',
        items: [
          { path: '/workspaces/archive', icon: Archive, label: 'Archive Workspace', spec: '§7.6.1', backend: 'routers.documents', status: 'new' },
          { path: '/workspaces/archive/time-travel', icon: Compass, label: 'Temporal Reconstruction', spec: '§7.6.2', backend: 'routers.documents', status: 'new' },
        ],
      },
      {
        label: 'Record Auditor & Logbook Workspace',
        spec: '§7.9',
        description: 'Record auditor, evidence trails, compliance views',
        items: [
          { path: '/workspaces/auditor', icon: ClipboardList, label: 'Record Auditor', spec: '§7.9.1', backend: 'routers.audit', status: 'new' },
          { path: '/workspaces/auditor/evidence', icon: FileCheck, label: 'Evidence Trails', spec: '§7.9.2', backend: 'routers.audit', status: 'new' },
          { path: '/workspaces/auditor/regulator', icon: Shield, label: 'Regulator Views', spec: '§7.9.3', backend: 'routers.audit', status: 'new' },
        ],
      },
      {
        label: 'Digital Twin & Enterprise Twin Workspace',
        spec: '§7.11',
        description: 'Digital twins, enterprise twins, reality twin mesh',
        items: [
          { path: '/workspaces/twins', icon: Layers, label: 'Digital Twin Builder', spec: '§7.11.1', backend: 'routers.neural_architecture', status: 'new' },
          { path: '/workspaces/twins/enterprise', icon: Globe, label: 'Enterprise Twin', spec: '§7.11.2', backend: 'routers.neural_architecture', status: 'new' },
          { path: '/workspaces/twins/reality-mesh', icon: Network, label: 'Reality Twin Mesh', spec: '§7.11.3', backend: 'routers.neural_architecture', status: 'new' },
        ],
      },
    ],
  },
  {
    path: '/ai',
    icon: Brain,
    label: 'AI Fabric',
    spec: '§4, §5, §8',
    description: 'Cognitive agents, drivers, capsules, and automation',
    groups: [
      {
        label: 'Cognitive Agents & Reasoning',
        spec: '§4',
        description: 'Personas, daemons, TRF, reasoning framework',
        items: [
          { path: '/ai/copilot', icon: Bot, label: 'AI Copilot', spec: '§4.1', backend: 'routers.intelligence', status: 'existing' },
          { path: '/ai/advanced', icon: Brain, label: 'Advanced AI Engine', spec: '§4.6', backend: 'routers.intelligence', status: 'existing' },
          { path: '/ai/personas', icon: Users, label: 'Personas & Agents', spec: '§4.1, §0.5', backend: 'routers.personas', status: 'new' },
          { path: '/ai/daemons', icon: Bot, label: 'Daemon Framework', spec: '§4.3-4.4', backend: 'routers.ai_systems', status: 'new' },
          { path: '/ai/trf', icon: Layers, label: 'Theoretical Reasoning Framework', spec: '§4.6', backend: 'routers.reasoning', status: 'new' },
          { path: '/ai/project-intelligence', icon: Brain, label: 'Project Intelligence', spec: '§4.5', backend: 'routers.intelligence', status: 'new' },
        ],
      },
      {
        label: 'Driver Fabric & System Execution',
        spec: '§5',
        description: 'OS drivers, package managers, system execution',
        items: [
          { path: '/ai/operations', icon: Cpu, label: 'AI Operations', spec: '§5.12', backend: 'routers.ai_systems', status: 'existing' },
          { path: '/ai/os', icon: ServerCog, label: 'AI OS Control', spec: '§5.2-5.3', backend: 'routers.platform', status: 'existing' },
          { path: '/ai/drivers', icon: Plug, label: 'Driver Registry', spec: '§5.1', backend: 'routers.platform', status: 'new' },
          { path: '/ai/drivers/os', icon: ServerCog, label: 'OS Drivers', spec: '§5.2', backend: 'routers.platform', status: 'new' },
          { path: '/ai/drivers/package', icon: Package, label: 'Package & Env Drivers', spec: '§5.4', backend: 'routers.platform', status: 'new' },
          { path: '/ai/drivers/hardware', icon: Cpu, label: 'Hardware Drivers', spec: '§5.5', backend: 'routers.platform', status: 'new' },
          { path: '/ai/drivers/software', icon: Code, label: 'Software & SaaS Drivers', spec: '§5.6', backend: 'routers.integrations', status: 'new' },
          { path: '/ai/drivers/data', icon: Database, label: 'Data Drivers', spec: '§5.7', backend: 'routers.integrations', status: 'new' },
          { path: '/ai/drivers/research', icon: FlaskConical, label: 'Research & Simulation Drivers', spec: '§5.9', backend: 'routers.research', status: 'new' },
          { path: '/ai/drivers/sandbox', icon: Container, label: 'Sandbox & Testbed', spec: '§5.11', backend: 'routers.platform', status: 'new' },
        ],
      },
      {
        label: 'Capsules & Workflow Automation',
        spec: '§8',
        description: 'Capsule system, workflow orchestration, automation',
        items: [
          { path: '/ai/workflows', icon: Workflow, label: 'Workflow Orchestrator', spec: '§8.10', backend: 'routers.workflow_orchestration', status: 'existing' },
          { path: '/ai/capsules', icon: Package, label: 'Capsule Marketplace', spec: '§8, §9.6', backend: 'routers.capsules', status: 'existing' },
          { path: '/ai/autofix', icon: Wrench, label: 'Auto-Fix Console', spec: '§8.13', backend: 'routers.autofix', status: 'existing' },
          { path: '/ai/capsules/ledger', icon: FileText, label: 'Project Ledger', spec: '§8.7', backend: 'routers.audit', status: 'new' },
          { path: '/ai/capsules/lineage', icon: GitBranch, label: 'Lineage & Replay', spec: '§8.8', backend: 'routers.runtime_diagnostics', status: 'new' },
          { path: '/ai/capsules/operator-studio', icon: Layers, label: 'Operator Studio', spec: '§8.19', backend: 'routers.workflow_orchestration', status: 'new' },
          { path: '/ai/capsules/templates', icon: LayoutTemplate, label: 'Capsule Templates', spec: '§8.20', backend: 'routers.capsules', status: 'new' },
          { path: '/ai/capsules/my-stack', icon: Package, label: 'My Stack Capsules', spec: '§8.22', backend: 'routers.capsules', status: 'new' },
        ],
      },
      {
        label: 'MLOps & Neural Architecture',
        spec: '§7.4, §5.4',
        description: 'MLOps, NAS, model validation, experiments',
        items: [
          { path: '/ai/mlops', icon: Bot, label: 'MLOps', spec: '§7.3.4', backend: 'routers.neural_architecture', status: 'existing' },
          { path: '/ai/nas', icon: Dna, label: 'NAS Console', spec: '§7.4', backend: 'routers.neural_architecture', status: 'existing' },
          { path: '/ai/nas/experiments', icon: FlaskConical, label: 'Experiment Console', spec: '§7.4.4', backend: 'routers.neural_architecture', status: 'existing' },
          { path: '/ai/nas/simulator', icon: Layers, label: 'NAS Simulator', spec: '§7.4', backend: 'routers.neural_architecture', status: 'existing' },
        ],
      },
      {
        label: 'Edge & Vision',
        spec: '§13.4, §4',
        description: 'Edge computing, computer vision, multimodal',
        items: [
          { path: '/ai/edge', icon: Satellite, label: 'Edge Computing', spec: '§13.4', backend: 'routers.edge_computing', status: 'existing' },
          { path: '/ai/vision', icon: Eye, label: 'Computer Vision', spec: '§4 multimodal', backend: 'routers.computer_vision', status: 'existing' },
        ],
      },
      {
        label: 'Intent Processing',
        spec: '§1.7.3',
        description: 'Intent model, context assembly, planning loop',
        items: [
          { path: '/ai/intents', icon: Zap, label: 'Intent Processor', spec: '§1.7.3', backend: 'routers.intents', status: 'existing' },
          { path: '/ai/systems', icon: Layers, label: 'Systems Map', spec: '§1.1', backend: 'routers.ai_systems', status: 'existing' },
        ],
      },
    ],
  },
  {
    path: '/drivers',
    icon: Plug,
    label: 'Drivers & Integrations',
    spec: '§5, §9',
    description: 'Driver registry, connectors, marketplace, extensibility',
    groups: [
      {
        label: 'Driver Registry & Management',
        spec: '§5.1, §9.4',
        description: 'Driver taxonomy, SDK, distribution channels',
        items: [
          { path: '/integrations', icon: Plug, label: 'Overview', spec: '§9.18', backend: 'routers.integrations', status: 'existing' },
          { path: '/drivers/registry', icon: Database, label: 'Driver Registry', spec: '§5.1', backend: 'routers.platform', status: 'new' },
          { path: '/drivers/sdk', icon: Code, label: 'Driver SDK', spec: '§9.3-9.4', backend: 'routers.platform', status: 'new' },
          { path: '/drivers/publishing', icon: Upload, label: 'Publishing Flow', spec: '§9.5', backend: 'routers.platform', status: 'new' },
        ],
      },
      {
        label: 'Connectors & Integrations',
        spec: '§9.18',
        description: 'Productivity suites, code hosts, finance, research data',
        items: [
          { path: '/integrations/api-connectors', icon: Network, label: 'API Connectors', spec: '§9.18', backend: 'routers.api_connectors', status: 'existing' },
          { path: '/integrations/office', icon: Activity, label: 'Office Realtime', spec: '§9.18.1', backend: 'routers.office', status: 'existing' },
          { path: '/drivers/integrations/productivity', icon: FileText, label: 'Productivity Suites', spec: '§9.18.1', backend: 'routers.integrations', status: 'new' },
          { path: '/drivers/integrations/code', icon: GitBranch, label: 'Code Hosts & CI/CD', spec: '§9.18.2', backend: 'routers.git', status: 'new' },
          { path: '/drivers/integrations/finance', icon: Calculator, label: 'Finance & Banking', spec: '§9.18.3', backend: 'routers.integrations', status: 'new' },
          { path: '/drivers/integrations/research', icon: FlaskConical, label: 'Research Data Sources', spec: '§9.18.4', backend: 'routers.research', status: 'new' },
          { path: '/drivers/integrations/legacy', icon: Terminal, label: 'Legacy & Mainframe', spec: '§9.18.5', backend: 'routers.terminal', status: 'new' },
          { path: '/drivers/integrations/cloud', icon: Cloud, label: 'Cloud Providers', spec: '§9.18.6', backend: 'routers.integrations', status: 'new' },
        ],
      },
      {
        label: 'Driver Packs & Marketplace',
        spec: '§9.6-9.8',
        description: 'Capsule marketplace, driver packs, vertical editions',
        items: [
          { path: '/drivers/marketplace', icon: Globe, label: 'Marketplace', spec: '§9.6', backend: 'routers.capsules', status: 'new' },
          { path: '/drivers/packs', icon: Package, label: 'Driver Packs', spec: '§9.8', backend: 'routers.platform', status: 'new' },
          { path: '/drivers/vertical-editions', icon: Layers, label: 'Vertical Editions', spec: '§9.8', backend: 'routers.platform', status: 'new' },
          { path: '/drivers/enterprise-store', icon: Server, label: 'Enterprise App Store', spec: '§9.9', backend: 'routers.capsules', status: 'new' },
        ],
      },
      {
        label: 'Risk & Governance',
        spec: '§9.11',
        description: 'Third-party risk management, review processes',
        items: [
          { path: '/drivers/risk', icon: AlertTriangle, label: 'Third-Party Risk', spec: '§9.11', backend: 'routers.integrations', status: 'new' },
        ],
      },
    ],
  },
  {
    path: '/data',
    icon: Database,
    label: 'Data & Knowledge',
    spec: '§3, §6',
    description: 'CIR store, ledger, capsules, indices, archive',
    groups: [
      {
        label: 'Core Data Stores',
        spec: '§6.1-6.4',
        description: 'CIR, ledger, capsule store, binary artifacts',
        items: [
          { path: '/data/cir', icon: FileText, label: 'CIR Store', spec: '§3.6, §6.2', backend: 'routers.documents', status: 'new' },
          { path: '/data/ledger', icon: ClipboardList, label: 'Project Ledger', spec: '§3.7, §6.3', backend: 'routers.audit', status: 'new' },
          { path: '/data/capsules', icon: Package, label: 'Capsule Store', spec: '§6.4', backend: 'routers.capsules', status: 'new' },
          { path: '/data/artifacts', icon: Archive, label: 'Binary Artifacts', spec: '§6.4', backend: 'routers.capsules', status: 'new' },
        ],
      },
      {
        label: 'Indices & Search',
        spec: '§6.5',
        description: 'Full-text, semantic, vector, graph indices',
        items: [
          { path: '/data/indices', icon: SearchIcon, label: 'Indices Overview', spec: '§6.5', backend: 'routers.search', status: 'new' },
          { path: '/data/indices/fulltext', icon: FileText, label: 'Full-Text Search', spec: '§6.5', backend: 'routers.search', status: 'new' },
          { path: '/data/indices/semantic', icon: Brain, label: 'Semantic/Vector Search', spec: '§6.5', backend: 'routers.search', status: 'new' },
          { path: '/data/indices/graph', icon: Network, label: 'Graph Index', spec: '§6.5', backend: 'routers.search', status: 'new' },
        ],
      },
      {
        label: 'Observability Stores',
        spec: '§6.6',
        description: 'Metrics, logs, traces, observability data',
        items: [
          { path: '/data/metrics', icon: BarChart3, label: 'Metrics Store', spec: '§6.6', backend: 'routers.analytics', status: 'new' },
          { path: '/data/logs', icon: FileText, label: 'Logs Store', spec: '§6.6', backend: 'routers.analytics', status: 'new' },
          { path: '/data/traces', icon: Network, label: 'Traces Store', spec: '§6.6', backend: 'routers.runtime_diagnostics', status: 'new' },
        ],
      },
      {
        label: 'Archive & Retention',
        spec: '§6.7',
        description: 'Archive, backup, retention, legal hold, time-travel',
        items: [
          { path: '/data/archive', icon: Archive, label: 'Archive', spec: '§6.7', backend: 'routers.documents', status: 'new' },
          { path: '/data/backup', icon: HardDrive, label: 'Backup & Retention', spec: '§6.7', backend: 'routers.documents', status: 'new' },
          { path: '/data/legal-hold', icon: Lock, label: 'Legal Hold', spec: '§6.7', backend: 'routers.audit', status: 'new' },
        ],
      },
      {
        label: 'Data Protection',
        spec: '§6.9',
        description: 'Encryption, key management, integrity protections',
        items: [
          { path: '/data/encryption', icon: Lock, label: 'Encryption & Keys', spec: '§6.9', backend: 'routers.settings', status: 'new' },
          { path: '/data/integrity', icon: Shield, label: 'Integrity Protections', spec: '§6.9', backend: 'routers.settings', status: 'new' },
        ],
      },
      {
        label: 'Replication & DR',
        spec: '§6.8',
        description: 'Multi-region replication, consistency, disaster recovery',
        items: [
          { path: '/data/replication', icon: Globe, label: 'Multi-Region Replication', spec: '§6.8', backend: 'routers.platform', status: 'new' },
          { path: '/data/consistency', icon: Network, label: 'Consistency Models', spec: '§6.8', backend: 'routers.platform', status: 'new' },
        ],
      },
    ],
  },
  {
    path: '/governance',
    icon: Shield,
    label: 'Governance & Security',
    spec: '§10, §15',
    description: 'Policy engine, compliance, billing, identity, regulator fabric',
    groups: [
      {
        label: 'Policy & Governance Engine',
        spec: '§10.3',
        description: 'Policy DSL, evaluation, safety harnesses',
        items: [
          { path: '/governance/policy', icon: Shield, label: 'Policy Engine', spec: '§10.3', backend: 'routers.settings', status: 'new' },
          { path: '/governance/policy/dsl', icon: Code, label: 'Policy DSL', spec: '§10.3.1', backend: 'routers.settings', status: 'new' },
          { path: '/governance/policy/safety', icon: Lock, label: 'Safety Harnesses', spec: '§10.3.3', backend: 'routers.settings', status: 'new' },
          { path: '/governance/policy/simulator', icon: Layers, label: 'Policy Simulator', spec: '§10.3.4', backend: 'routers.settings', status: 'new' },
        ],
      },
      {
        label: 'Compliance & Regulator Fabric',
        spec: '§10.4-10.5',
        description: 'Compliance packs, regulator fabric, inspection APIs',
        items: [
          { path: '/governance/compliance', icon: FileCheck, label: 'Compliance Packs', spec: '§10.4', backend: 'routers.audit', status: 'new' },
          { path: '/governance/regulator', icon: Shield, label: 'Regulator Fabric', spec: '§10.5', backend: 'routers.audit', status: 'new' },
          { path: '/governance/regulator/tenancy', icon: Users, label: 'Regulator Tenancy', spec: '§10.5.1', backend: 'routers.audit', status: 'new' },
          { path: '/governance/regulator/evidence', icon: ClipboardList, label: 'Evidence Access', spec: '§10.5.2', backend: 'routers.audit', status: 'new' },
        ],
      },
      {
        label: 'Identity & Access',
        spec: '§10.2, §0.4',
        description: 'Identity, authentication, authorization, RBAC/ABAC',
        items: [
          { path: '/governance/identity', icon: Users, label: 'Identity & Roles', spec: '§10.2, §0.4', backend: 'routers.settings', status: 'new' },
          { path: '/governance/identity/auth', icon: Key, label: 'Authentication', spec: '§10.2', backend: 'routers.settings', status: 'new' },
          { path: '/governance/identity/rbac', icon: Shield, label: 'RBAC/ABAC', spec: '§10.2', backend: 'routers.settings', status: 'new' },
        ],
      },
      {
        label: 'Data Protection & Classification',
        spec: '§10.6',
        description: 'Data classification, residency, encryption, masking',
        items: [
          { path: '/governance/data-protection', icon: Lock, label: 'Data Protection', spec: '§10.6', backend: 'routers.settings', status: 'new' },
          { path: '/governance/data-protection/classification', icon: FileText, label: 'Data Classification', spec: '§10.6', backend: 'routers.settings', status: 'new' },
          { path: '/governance/data-protection/residency', icon: Globe, label: 'Data Residency', spec: '§10.6', backend: 'routers.settings', status: 'new' },
          { path: '/governance/data-protection/masking', icon: Eye, label: 'Data Masking', spec: '§10.6.2', backend: 'routers.settings', status: 'new' },
        ],
      },
      {
        label: 'Security Monitoring & Response',
        spec: '§10.8-10.9',
        description: 'Security monitoring, risk scoring, incident response',
        items: [
          { path: '/governance/security/monitoring', icon: Monitor, label: 'Security Monitoring', spec: '§10.8', backend: 'routers.security_threat', status: 'new' },
          { path: '/governance/security/risk', icon: AlertTriangle, label: 'Risk Scoring', spec: '§10.8.2', backend: 'routers.security_threat', status: 'new' },
          { path: '/governance/security/alignment', icon: Target, label: 'Alignment Monitor', spec: '§10.8.3', backend: 'routers.security_threat', status: 'new' },
          { path: '/governance/security/incidents', icon: AlertTriangle, label: 'Incident Response', spec: '§10.9', backend: 'routers.security_threat', status: 'new' },
        ],
      },
      {
        label: 'AI Billing & Cost Governance',
        spec: '§15',
        description: 'AI billing, usage fabric, budgets, cost guardrails',
        items: [
          { path: '/billing', icon: CreditCard, label: 'Billing & Usage', spec: '§15.2', backend: 'routers.analytics', status: 'existing' },
          { path: '/governance/billing/usage', icon: BarChart3, label: 'Usage Fabric', spec: '§15.2', backend: 'routers.analytics', status: 'new' },
          { path: '/governance/billing/budgets', icon: Calculator, label: 'Budgets & Quotas', spec: '§15.3', backend: 'routers.analytics', status: 'new' },
          { path: '/governance/billing/guardrails', icon: Shield, label: 'Cost Guardrails', spec: '§15.3', backend: 'routers.analytics', status: 'new' },
          { path: '/governance/billing/optimizer', icon: TrendingUp, label: 'Billing Optimizer', spec: '§15.4', backend: 'routers.analytics', status: 'new' },
          { path: '/governance/billing/multi-tenant', icon: Users, label: 'Multi-Tenant Billing', spec: '§15.5', backend: 'routers.analytics', status: 'new' },
        ],
      },
    ],
  },
  {
    path: '/observability',
    icon: Radio,
    label: 'Observability & Evidence',
    spec: '§11',
    description: 'Telemetry, audit, evidence packs, record auditor',
    groups: [
      {
        label: 'Telemetry & Metrics',
        spec: '§11.1-11.2',
        description: 'Observability goals, SLIs, SLOs, metrics model',
        items: [
          { path: '/analytics', icon: BarChart3, label: 'Analytics', spec: '§11.1', backend: 'routers.analytics', status: 'existing' },
          { path: '/monitoring', icon: Activity, label: 'Monitoring', spec: '§11.9', backend: 'routers.analytics', status: 'existing' },
          { path: '/observability', icon: Radio, label: 'Observability', spec: '§11.2-11.4', backend: 'routers.runtime_diagnostics', status: 'existing' },
          { path: '/observability/metrics', icon: BarChart3, label: 'Metrics Model', spec: '§11.2', backend: 'routers.analytics', status: 'new' },
          { path: '/observability/slis', icon: Target, label: 'SLIs & SLOs', spec: '§11.1', backend: 'routers.analytics', status: 'new' },
        ],
      },
      {
        label: 'Logging & Tracing',
        spec: '§11.3-11.4',
        description: 'Structured logging, distributed tracing, request graphs',
        items: [
          { path: '/observability/logging', icon: FileText, label: 'Structured Logging', spec: '§11.3', backend: 'routers.analytics', status: 'new' },
          { path: '/observability/tracing', icon: Network, label: 'Distributed Tracing', spec: '§11.4', backend: 'routers.runtime_diagnostics', status: 'new' },
        ],
      },
      {
        label: 'Record Auditor & Logbook',
        spec: '§11.5',
        description: 'Record auditor, intent-to-process trails',
        items: [
          { path: '/observability/record-auditor', icon: ClipboardList, label: 'Record Auditor', spec: '§11.5', backend: 'routers.audit', status: 'new' },
          { path: '/audit', icon: ClipboardList, label: 'Audit Evidence', spec: '§11.6-11.7', backend: 'routers.audit', status: 'existing' },
        ],
      },
      {
        label: 'Evidence & Audit',
        spec: '§11.6-11.7',
        description: 'Audit logs, evidence stores, evidence pack generator',
        items: [
          { path: '/observability/evidence', icon: FileCheck, label: 'Evidence Packs', spec: '§11.7', backend: 'routers.audit', status: 'new' },
          { path: '/observability/audit-logs', icon: FileText, label: 'Audit Logs', spec: '§11.6', backend: 'routers.audit', status: 'new' },
          { path: '/observability/retention', icon: Archive, label: 'Retention Policies', spec: '§11.6', backend: 'routers.audit', status: 'new' },
        ],
      },
      {
        label: 'Health & Self-Healing',
        spec: '§11.8',
        description: 'Health checks, self-healing, auto-remediation, runbooks',
        items: [
          { path: '/observability/health', icon: Activity, label: 'Health Checks', spec: '§11.8', backend: 'routers.runtime_diagnostics', status: 'new' },
          { path: '/observability/self-healing', icon: Wrench, label: 'Self-Healing', spec: '§11.8', backend: 'routers.autofix', status: 'new' },
          { path: '/observability/runbooks', icon: BookOpen, label: 'Runbooks', spec: '§11.8', backend: 'routers.workflow_orchestration', status: 'new' },
        ],
      },
      {
        label: 'Dashboards & Alerting',
        spec: '§11.9',
        description: 'Dashboards, alerting, on-call operations',
        items: [
          { path: '/observability/dashboards', icon: LayoutDashboard, label: 'Dashboards', spec: '§11.9', backend: 'routers.dashboard', status: 'new' },
          { path: '/observability/alerting', icon: AlertTriangle, label: 'Alerting', spec: '§11.9', backend: 'routers.analytics', status: 'new' },
        ],
      },
      {
        label: 'Temporal Backtesting & Replay',
        spec: '§11.10',
        description: 'Temporal backtesting, replay engine, counterfactuals',
        items: [
          { path: '/observability/replay', icon: Compass, label: 'Replay Engine', spec: '§11.10', backend: 'routers.runtime_diagnostics', status: 'new' },
          { path: '/observability/backtesting', icon: TrendingUp, label: 'Temporal Backtesting', spec: '§11.10', backend: 'routers.runtime_diagnostics', status: 'new' },
        ],
      },
    ],
  },
  {
    path: '/operations',
    icon: Server,
    label: 'Operations & Infrastructure',
    spec: '§12, §13, §14',
    description: 'Performance, scalability, deployment, failure modes',
    groups: [
      {
        label: 'Performance & Scalability',
        spec: '§12',
        description: 'Performance targets, SLAs, scaling strategies',
        items: [
          { path: '/operations/performance', icon: TrendingUp, label: 'Performance', spec: '§12.1', backend: 'routers.analytics', status: 'new' },
          { path: '/operations/scaling', icon: Server, label: 'Scaling Strategies', spec: '§12.3', backend: 'routers.platform', status: 'new' },
          { path: '/operations/driver-performance', icon: Cpu, label: 'Driver Performance', spec: '§12.4', backend: 'routers.platform', status: 'new' },
          { path: '/operations/backpressure', icon: Network, label: 'Backpressure & Throttling', spec: '§12.5', backend: 'routers.platform', status: 'new' },
          { path: '/operations/reliability', icon: Shield, label: 'Reliability Patterns', spec: '§12.6', backend: 'routers.runtime_diagnostics', status: 'new' },
          { path: '/operations/capacity', icon: BarChart3, label: 'Capacity Planning', spec: '§12.8', backend: 'routers.analytics', status: 'new' },
        ],
      },
      {
        label: 'Deployment Models',
        spec: '§13.1-13.4',
        description: 'Local, cloud, hybrid, edge architectures',
        items: [
          { path: '/operations/deployment', icon: Cloud, label: 'Deployment Modes', spec: '§13.1', backend: 'routers.platform', status: 'new' },
          { path: '/operations/deployment/local', icon: ServerCog, label: 'Local Mode', spec: '§13.2', backend: 'routers.platform', status: 'new' },
          { path: '/operations/deployment/cloud', icon: Cloud, label: 'Cloud/Enterprise', spec: '§13.3', backend: 'routers.platform', status: 'new' },
          { path: '/operations/deployment/hybrid', icon: Network, label: 'Hybrid & Edge', spec: '§13.4', backend: 'routers.edge_computing', status: 'new' },
        ],
      },
      {
        label: 'Infrastructure & Topology',
        spec: '§13.5-13.9',
        description: 'Network topology, storage, queues, search, HPC',
        items: [
          { path: '/systems/network', icon: Network, label: 'Network Monitoring', spec: '§13.5', backend: 'routers.network_monitoring', status: 'existing' },
          { path: '/operations/topology', icon: Network, label: 'Network Topology', spec: '§13.5', backend: 'routers.platform', status: 'new' },
          { path: '/operations/storage', icon: HardDrive, label: 'Storage Topology', spec: '§13.6', backend: 'routers.platform', status: 'new' },
          { path: '/operations/queues', icon: Workflow, label: 'Queues & Search', spec: '§13.6', backend: 'routers.platform', status: 'new' },
          { path: '/operations/hpc', icon: Server, label: 'HPC Integration', spec: '§13.7', backend: 'routers.research', status: 'new' },
          { path: '/operations/config', icon: Settings, label: 'Configuration Management', spec: '§13.8', backend: 'routers.settings', status: 'new' },
          { path: '/operations/multi-region', icon: Globe, label: 'Multi-Region & DR', spec: '§13.9', backend: 'routers.platform', status: 'new' },
        ],
      },
      {
        label: 'Upgrades & Migration',
        spec: '§13.10',
        description: 'Upgrades, migration, backwards compatibility, rollback',
        items: [
          { path: '/operations/upgrades', icon: TrendingUp, label: 'Upgrades', spec: '§13.10', backend: 'routers.platform', status: 'new' },
          { path: '/operations/migration', icon: GitBranch, label: 'Migration', spec: '§13.10', backend: 'routers.platform', status: 'new' },
          { path: '/operations/rollback', icon: AlertTriangle, label: 'Rollback Strategy', spec: '§13.10', backend: 'routers.platform', status: 'new' },
        ],
      },
      {
        label: 'Failure Modes & Resilience',
        spec: '§14',
        description: 'Failure taxonomy, detection, recovery, risk',
        items: [
          { path: '/operations/failure', icon: AlertTriangle, label: 'Failure Modes', spec: '§14.1', backend: 'routers.runtime_diagnostics', status: 'new' },
          { path: '/operations/detection', icon: Monitor, label: 'Detection Mechanisms', spec: '§14.2', backend: 'routers.runtime_diagnostics', status: 'new' },
          { path: '/operations/recovery', icon: Wrench, label: 'Recovery Strategies', spec: '§14.3', backend: 'routers.autofix', status: 'new' },
          { path: '/operations/data-protection', icon: Shield, label: 'Data Loss Protection', spec: '§14.4', backend: 'routers.platform', status: 'new' },
          { path: '/operations/security-incidents', icon: AlertTriangle, label: 'Security Incidents', spec: '§14.5', backend: 'routers.security_threat', status: 'new' },
          { path: '/operations/bc-dr', icon: Server, label: 'Business Continuity & DR', spec: '§14.6', backend: 'routers.platform', status: 'new' },
        ],
      },
    ],
  },
  {
    path: '/vision',
    icon: Sparkles,
    label: 'Vision & Meta-Stack',
    spec: '§17',
    description: 'Meta-stack capability layers from Core to Ascend',
    groups: [
      {
        label: 'Vision Deck Hub',
        spec: '§17 Overview',
        description: 'Meta-stack overview and capability map',
        items: [
          { path: '/vision', icon: Compass, label: 'Vision Deck Hub', spec: '§17', backend: 'routers.documents', status: 'existing' },
        ],
      },
      {
        label: 'Core OS Engines',
        spec: '§17.2',
        description: 'Layer 1 - Core capabilities and low-hanging fruit',
        items: [
          { path: '/future/core_os', icon: Layers, label: 'Core OS Engines', spec: '§17.2', backend: 'routers.documents', status: 'existing' },
        ],
      },
      {
        label: 'Advanced Horizons',
        spec: '§17.3',
        description: 'Layer 2 - Advanced research, simulation, digital twins',
        items: [
          { path: '/future/advanced', icon: Brain, label: 'Advanced Horizons', spec: '§17.3', backend: 'routers.documents', status: 'existing' },
        ],
      },
      {
        label: 'Super Capabilities',
        spec: '§17.4',
        description: 'Layer 3 - Meta-systems over the stack',
        items: [
          { path: '/future/super', icon: Dna, label: 'Super Capabilities', spec: '§17.4', backend: 'routers.documents', status: 'existing' },
        ],
      },
      {
        label: 'Hyper Network',
        spec: '§17.5',
        description: 'Layer 4 - Inter-OS and ecosystem-scale',
        items: [
          { path: '/future/hyper', icon: Satellite, label: 'Hyper Network', spec: '§17.5', backend: 'routers.documents', status: 'existing' },
        ],
      },
      {
        label: 'Ultra Scale',
        spec: '§17.6',
        description: 'Layer 5 - Ecosystem-scale cognition',
        items: [
          { path: '/future/ultra', icon: Workflow, label: 'Ultra Scale', spec: '§17.6', backend: 'routers.documents', status: 'existing' },
        ],
      },
      {
        label: 'Supreme',
        spec: '§17.7',
        description: 'Layer 6 - Ontological and civilizational meta-layer',
        items: [
          { path: '/future/supreme', icon: Shield, label: 'Supreme', spec: '§17.7', backend: 'routers.documents', status: 'existing' },
        ],
      },
      {
        label: 'Ascend',
        spec: '§17.8',
        description: 'Layer 7 - Sovereign norm and obligation stack',
        items: [
          { path: '/future/ascend', icon: Shield, label: 'Ascend', spec: '§17.8', backend: 'routers.documents', status: 'existing' },
        ],
      },
      {
        label: 'Meta Envelope',
        spec: '§17 Overview',
        description: 'Full meta-stack envelope and governance',
        items: [
          { path: '/future/meta', icon: Compass, label: 'Meta Envelope', spec: '§17', backend: 'routers.documents', status: 'existing' },
        ],
      },
    ],
  },
  {
    path: '/docs',
    icon: FileText,
    label: 'Docs & Spec',
    spec: '§18, §19',
    description: 'Documentation, spec sheet, references, appendices',
    groups: [
      {
        label: 'Documentation Hub',
        spec: '§19',
        description: 'Main documentation and reference materials',
        items: [
          { path: '/docs', icon: FileText, label: 'Docs Hub', spec: '§19', backend: 'routers.documents', status: 'existing' },
          { path: '/docs/spec-sheet', icon: Compass, label: 'Technical Spec Sheet', spec: '§18', backend: 'routers.documents', status: 'existing' },
        ],
      },
      {
        label: 'Reference Artifacts',
        spec: '§19.1-19.4',
        description: 'Capsule manifests, driver manifests, policy examples, evidence packs',
        items: [
          { path: '/docs/reference/capsules', icon: Package, label: 'Capsule Manifests', spec: '§19.1', backend: 'routers.documents', status: 'new' },
          { path: '/docs/reference/drivers', icon: Plug, label: 'Driver Manifests', spec: '§19.2', backend: 'routers.documents', status: 'new' },
          { path: '/docs/reference/policies', icon: Shield, label: 'Policy Examples', spec: '§19.3', backend: 'routers.documents', status: 'new' },
          { path: '/docs/reference/evidence', icon: FileCheck, label: 'Evidence Pack Templates', spec: '§19.4', backend: 'routers.documents', status: 'new' },
        ],
      },
      {
        label: 'API Reference',
        spec: '§19.10',
        description: 'API and interface reference index',
        items: [
          { path: '/docs/api', icon: Code, label: 'API Reference', spec: '§19.10', backend: 'routers.documents', status: 'new' },
        ],
      },
      {
        label: 'Migration & Integration',
        spec: '§19.12',
        description: 'Migration patterns and integration guides',
        items: [
          { path: '/docs/migration_continued.md', icon: FileText, label: 'Migration Continued', spec: '§19.12', backend: 'routers.documents', status: 'existing' },
        ],
      },
    ],
  },
  {
    path: '/settings',
    icon: Settings,
    label: 'Settings & Admin',
    spec: '§0.4, §10.2',
    description: 'User settings, tenant admin, identity management',
    groups: [
      {
        label: 'User & Tenant Settings',
        spec: '§0.4',
        description: 'User preferences, tenant configuration',
        items: [
          { path: '/settings', icon: Settings, label: 'Settings', spec: '§0.4', backend: 'routers.settings', status: 'existing' },
        ],
      },
    ],
  },
  {
    path: '/roadmap',
    icon: Compass,
    label: 'Roadmap & Risks',
    spec: '§16',
    description: 'Open questions, risks, roadmap, and spec maintenance',
    groups: [
      {
        label: 'Roadmap & Planning',
        spec: '§16',
        description: 'Phased delivery, milestones, long-term bets',
        items: [
          { path: '/roadmap/overview', icon: Compass, label: 'Roadmap Overview', spec: '§16.3', backend: 'routers.documents', status: 'new' },
          { path: '/roadmap/phases', icon: Layers, label: 'Phased Delivery', spec: '§16.3', backend: 'routers.documents', status: 'new' },
          { path: '/roadmap/milestones', icon: Target, label: 'Milestones', spec: '§16.3', backend: 'routers.documents', status: 'new' },
          { path: '/roadmap/future', icon: Sparkles, label: 'Long-Term Bets', spec: '§16.4', backend: 'routers.documents', status: 'new' },
        ],
      },
      {
        label: 'Risks & Decisions',
        spec: '§16.1-16.2, 16.5',
        description: 'Open questions, risks, decision log',
        items: [
          { path: '/roadmap/risks', icon: AlertTriangle, label: 'Risk Register', spec: '§16.5', backend: 'routers.documents', status: 'new' },
          { path: '/roadmap/decisions', icon: FileCheck, label: 'Decision Log', spec: '§16.8', backend: 'routers.documents', status: 'new' },
          { path: '/roadmap/gaps', icon: AlertTriangle, label: 'Known Gaps', spec: '§16.2', backend: 'routers.documents', status: 'new' },
          { path: '/roadmap/questions', icon: MessageSquare, label: 'Open Questions', spec: '§16.1', backend: 'routers.documents', status: 'new' },
        ],
      },
      {
        label: 'Spec Maintenance',
        spec: '§16.6-16.7',
        description: 'Spec versioning, change management, future capabilities',
        items: [
          { path: '/roadmap/spec', icon: FileText, label: 'Spec Versioning', spec: '§16.6', backend: 'routers.documents', status: 'new' },
          { path: '/roadmap/future-capabilities', icon: Sparkles, label: 'Future Capabilities', spec: '§16.7', backend: 'routers.documents', status: 'new' },
        ],
      },
    ],
  },
]

// Helper to get all pages from a category
export const getAllPagesFromCategory = (category: NavCategory): NavPage[] => {
  return category.groups.flatMap((group) => group.items)
}

// Helper to find category by path
export const findCategoryByPath = (path: string): NavCategory | undefined => {
  return navigationManifest.find((cat) => path.startsWith(cat.path))
}

// Helper to find page by path
export const findPageByPath = (path: string): NavPage | undefined => {
  for (const category of navigationManifest) {
    for (const group of category.groups) {
      const page = group.items.find((item) => item.path === path)
      if (page) return page
    }
  }
  return undefined
}


