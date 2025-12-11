export type RequirementStatus = 'complete' | 'in_progress' | 'pending'

export interface SpecRequirement {
  id: string
  title: string
  description: string
  status: RequirementStatus
  specRefs: string[]
  sourceDocs: { label: string; href?: string }[]
  nextSteps: string[]
}

export const statusMeta: Record<RequirementStatus, { label: string; chipClass: string; description: string }> = {
  complete: {
    label: 'Complete',
    chipClass: 'bg-emerald-500/15 border border-emerald-400/40 text-emerald-200',
    description: 'Delivered in the shared React + FastAPI stack',
  },
  in_progress: {
    label: 'In Progress',
    chipClass: 'bg-amber-400/15 border border-amber-300/40 text-amber-100',
    description: 'Actively being migrated per MIGRATION_CONTINUED.md',
  },
  pending: {
    label: 'Pending',
    chipClass: 'bg-slate-500/15 border border-slate-400/40 text-slate-200',
    description: 'Still open per Technical Spec Sheet',
  },
}

export const specRequirements: SpecRequirement[] = [
  {
    id: 'project-ledger',
    title: 'Project Ledger + Capsule Alignment',
    description:
      'Ledger events, capsule snapshots, and project metadata have a single API so web + desktop stay in lockstep.',
    status: 'complete',
    specRefs: ['Spec §3.7', 'Spec §6.3', 'Spec §8.7'],
    sourceDocs: [
      { label: 'MIGRATION_CONTINUED.md · Project Ledger & Spec Alignment', href: '/docs/migration_continued.md' },
      { label: 'Technical Spec Sheet v6', href: '/spec-sheet' },
    ],
    nextSteps: ['Verify ledger events stream to Evidence Pack builder', 'Expose hash-chain verifier to auditors'],
  },
  {
    id: 'project-intelligence',
    title: 'Project Intelligence + TRF Surface',
    description:
      'React Projects view must expose per-project risk heuristics, TRF traces, and persona health from the spec.',
    status: 'in_progress',
    specRefs: ['Spec §4.5 — §4.8'],
    sourceDocs: [
      { label: 'MIGRATION_CONTINUED.md · Remaining Task #1', href: '/docs/migration_continued.md' },
      { label: 'Technical Spec Sheet §4.5–§4.8', href: '/spec-sheet' },
    ],
    nextSteps: ['Add TRF trace modal to /projects', 'Persist health scores via /api/projects/intelligence'],
  },
  {
    id: 'driver-scheduling',
    title: 'Driver Scheduling & Backpressure',
    description:
      'AIOps dashboard needs queue telemetry and guardrails that match Driver Scheduling requirements.',
    status: 'in_progress',
    specRefs: ['Spec §5.12', 'Spec §12.5'],
    sourceDocs: [
      { label: 'MIGRATION_CONTINUED.md · Driver Scheduling Instrumentation', href: '/docs/migration_continued.md' },
      { label: 'Technical Spec Sheet §5.12', href: '/spec-sheet' },
    ],
    nextSteps: ['Publish /api/ai/drivers metrics', 'Visualize queue depth + throttle knobs in /ai/operations'],
  },
  {
    id: 'collaboration-federation',
    title: 'Collaboration & Federation Primitives',
    description:
      'Multi-user state, shared annotations, and “Run This Project Here” need a visible roadmap.',
    status: 'pending',
    specRefs: ['Spec §7.12'],
    sourceDocs: [
      { label: 'MIGRATION_CONTINUED.md · Collaboration & Federation', href: '/docs/migration_continued.md' },
      { label: 'Technical Spec Sheet §7.12', href: '/spec-sheet' },
    ],
    nextSteps: ['Design tenant/user tables', 'Add membership selector to Projects and Tasks'],
  },
  {
    id: 'evidence-packs',
    title: 'Evidence Pack & Audit Export',
    description:
      'Web app must generate regulator-grade bundles per Evidence Pack templates.',
    status: 'pending',
    specRefs: ['Spec §8.17', 'Spec §11.6'],
    sourceDocs: [
      { label: 'Technical Spec Sheet §8.17 / §11.6', href: '/spec-sheet' },
    ],
    nextSteps: ['Expose /api/evidence-packs endpoint', 'Add download button to Audit space'],
  },
]
