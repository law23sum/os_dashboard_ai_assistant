import { Shield, Workflow, Cpu, Network, Radar, Layers, ServerCog, Wrench, FileSpreadsheet, Compass } from 'lucide-react'

type SystemCard = {
  id: string
  title: string
  description: string
  status: 'available' | 'in-progress'
  icon: React.ComponentType<{ className?: string }>
  doc?: string
}

const systems: SystemCard[] = [
  {
    id: 'edge',
    title: 'Edge Computing Fabric',
    description:
      'Manages distributed AI nodes, deploy pipelines, and network telemetry just like the Tkinter Edge tab.',
    status: 'available',
    icon: Network,
    doc: '/docs/future_core_os.html',
  },
  {
    id: 'security',
    title: 'Security Threat Detection',
    description:
      'Runs AI-powered threat sweeps, correlates incidents, and mirrors the Tkinter threat dashboard elements.',
    status: 'available',
    icon: Shield,
    doc: '/docs/security.html',
  },
  {
    id: 'workflow',
    title: 'Workflow Orchestration',
    description:
      'Controls daemon schedules, approval chains, and automation DAGs. Replicates the Tkinter workflow pane.',
    status: 'available',
    icon: Workflow,
    doc: '/docs/future_core_os.html#workflows',
  },
  {
    id: 'nas',
    title: 'Neural Architecture Search',
    description:
      'Provides experiment controls, population stats, and timeline charts for NAS sessions from the Tkinter NAS tab.',
    status: 'available',
    icon: Cpu,
    doc: '/docs/future_advanced.html',
  },
  {
    id: 'audit',
    title: 'Security & Audit Center',
    description:
      'Audit log explorer, compliance toggles, and reporting automations inspired by the Tkinter audit system.',
    status: 'available',
    icon: Radar,
    doc: '/docs/future_core_os.html#compliance',
  },
  {
    id: 'infrastructure',
    title: 'Integrations & Infrastructure',
    description:
      'One pane for connectors, pipelines, and infrastructure health. Matches the Tkinter integrations infrastructure tab.',
    status: 'available',
    icon: Layers,
    doc: '/docs/projects.html',
  },
  {
    id: 'tools',
    title: 'Tools Intelligence Hub',
    description:
      'Catalog of CLI routines, orchestrated AI tools, and compliance-safe automations lifted from the Tkinter tools intelligence tab.',
    status: 'available',
    icon: Wrench,
    doc: '/docs/billing.html',
  },
  {
    id: 'aios',
    title: 'AI OS Cockpit',
    description:
      'Combines daemon control, safe-mode toggles, and operations feed as seen in the Tkinter AI OS cockpit.',
    status: 'available',
    icon: ServerCog,
    doc: '/docs/ai_capabilities.html',
  },
  {
    id: 'specs',
    title: 'Specs & Systems Library',
    description:
      'Central reference for canonical specs, knowledge graph pivots, and governance docs.',
    status: 'available',
    icon: FileSpreadsheet,
    doc: '/docs/index.html',
  },
  {
    id: 'future',
    title: 'Future Features & Driver Layer',
    description:
      'Roadmap visualization for the driver layer and future tier docs. Mirrors the Tkinter future features tab.',
    status: 'available',
    icon: Compass,
    doc: '/docs/future_super.html',
  },
]

const statusBadges: Record<SystemCard['status'], string> = {
  available: 'Available now',
  'in-progress': 'In progress',
}

const statusClass: Record<SystemCard['status'], string> = {
  available: 'bg-[rgba(99,102,241,0.15)] text-[color:var(--osd-accent)]',
  'in-progress': 'bg-[rgba(255,255,255,0.08)] text-[color:var(--osd-muted)]',
}

export default function AdvancedSystems() {
  return (
    <div className="px-4 py-6 sm:px-0 space-y-8">
      <section className="glass-panel p-6 md:p-8">
        <p className="glass-pill inline-flex items-center gap-2">
          <SparklesIcon className="w-4 h-4" />
          Advanced Systems
        </p>
        <div className="mt-4 flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <h2 className="text-3xl lg:text-4xl font-semibold text-[color:var(--osd-text)]">
              Tkinter Tabs → React Surfaces
            </h2>
            <p className="text-[color:var(--osd-muted)] mt-3 max-w-2xl">
              Every advanced Tkinter workspace now has a React counterpart. The cards below show
              parity status, route mappings, and the documentation source that guided each design.
            </p>
          </div>
        </div>
      </section>

      <section className="glass-panel p-6 md:p-8 space-y-4">
        <header className="flex flex-col gap-2">
          <h3 className="text-2xl font-semibold">Parity Checklist</h3>
          <p className="text-sm text-[color:var(--osd-muted)]">
            Compare Tkinter tabs under <code>assistant_hub_gui/assistant_hub/gui.py</code> with the
            React routes. All cards share the same glass aesthetic across desktop and browser.
          </p>
        </header>
        <div className="glass-grid glass-grid--two">
          {systems.map((system) => {
            const Icon = system.icon
            return (
              <article key={system.id} className="glass-panel p-5 border border-[color:var(--osd-border)]">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Icon className="w-5 h-5 text-[color:var(--osd-accent)]" />
                    <h4 className="font-semibold">{system.title}</h4>
                  </div>
                  <span className={`text-xs px-3 py-1 rounded-full ${statusClass[system.status]}`}>
                    {statusBadges[system.status]}
                  </span>
                </div>
                <p className="text-sm text-[color:var(--osd-muted)] mt-3">{system.description}</p>
                {system.doc && (
                  <a
                    href={system.doc}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-2 text-sm text-[color:var(--osd-accent)] hover:text-[color:var(--osd-accentHover)] mt-4"
                  >
                    View Documentation ↗
                  </a>
                )}
              </article>
            )
          })}
        </div>
      </section>

      <section className="glass-panel p-6 md:p-8 space-y-4">
        <header>
          <h3 className="text-2xl font-semibold">Verification Workflow</h3>
          <p className="text-sm text-[color:var(--osd-muted)]">
            Run <code>python start_ui.py</code> and pick desktop or web to cross-check Tkinter and
            React surfaces. Each panel below highlights what to confirm before marking a tab
            complete.
          </p>
        </header>
        <VerificationList />
      </section>
    </div>
  )
}

const SparklesIcon = ({ className }: { className?: string }) => (
  <svg viewBox="0 0 24 24" className={className} fill="currentColor">
    <path d="M12 2l1.5 4.5L18 8l-4.5 1.5L12 14l-1.5-4.5L6 8l4.5-1.5L12 2zM4 14l.8 2.2L8 17l-2.2.8L5 20l-.8-2.2L2 17l2.2-.8L4 14zm12 3l1 2.5 2.5 1-2.5 1L16 24l-1-2.5-2.5-1 2.5-1L16 17z" />
  </svg>
)

const verificationSteps = [
  {
    title: 'Compare Legacy Tkinter UI',
    detail:
      'Launch the Tkinter GUI (`python -m assistant_hub_gui.main`) and capture screenshots for each advanced tab.',
  },
  {
    title: 'Open React Route',
    detail:
      'Visit the matching `/ai/*` route in the browser or the Electron shell. Confirm cards, tables, and actions exist.',
  },
  {
    title: 'Check Shared Theme',
    detail:
      'Verify gradient backgrounds, borders, and badges are consistent across surfaces (Tk palette mirrored via CSS variables).',
  },
  {
    title: 'Validate API Coverage',
    detail:
      'Ensure the FastAPI endpoints used by the Tkinter view are available (`assistant_hub/api/server.py` or `ai_os/app`).',
  },
  {
    title: 'Mark Checklist',
    detail:
      'Update `docs/tk_to_react_mapping.md` once the React experience reaches feature parity for that tab.',
  },
]

const VerificationList = () => (
  <ol className="grid gap-4 md:grid-cols-2">
    {verificationSteps.map((step, idx) => (
      <li key={step.title} className="glass-panel border border-[color:var(--osd-border)] p-4">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[color:var(--osd-muted)]">
          Step {String(idx + 1).padStart(2, '0')}
        </p>
        <h4 className="text-lg font-semibold mt-2">{step.title}</h4>
        <p className="text-sm text-[color:var(--osd-muted)] mt-1">{step.detail}</p>
      </li>
    ))}
  </ol>
)
