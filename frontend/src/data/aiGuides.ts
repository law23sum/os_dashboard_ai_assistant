import {
  Activity,
  BookOpen,
  BookOpenCheck,
  Brain,
  GitCommit,
  HardDriveDownload,
  ListChecks,
  PenSquare,
  Scroll,
  Server,
  Shield,
  SlidersHorizontal,
  Tool,
  UserPlus,
  Wrench,
} from 'lucide-react'
import type { LucideIcon } from 'lucide-react'

export interface AIGuidePrompt {
  label: string
  prompt: string
}

export interface AIGuideAction {
  id: string
  label: string
  description: string
  icon: LucideIcon
  intent: 'explain' | 'optimize' | 'review'
  pill?: string
}

export interface AIGuideConfig {
  id: string
  persona: string
  headline: string
  description: string
  specRefs: string[]
  prompts: AIGuidePrompt[]
  actions: AIGuideAction[]
  recommendations: string[]
}

const registry: Record<string, AIGuideConfig> = {
  '/': {
    id: 'dashboard',
    persona: 'AIC · Mission Control',
    headline: 'Live mission overview',
    description:
      'I synthesize telemetry, ledger health, and priority stacks pulled directly from FastAPI. Ask me for a summary before diving into any workspace.',
    specRefs: ['Spec §1.7', 'Spec §4.5'],
    prompts: [
      { label: 'Summarize top risks', prompt: 'Summarize the highest-risk projects and why they are red.' },
      { label: 'Pulse check', prompt: 'Give me a 3-line health pulse based on current telemetry.' },
    ],
    actions: [
      {
        id: 'ledger-scan',
        label: 'Ledger integrity scan',
        description: 'Verify latest events and the hash chain before approvals.',
        icon: Shield,
        intent: 'review',
        pill: 'Audit',
      },
      {
        id: 'prioritize',
        label: 'Reorder priorities',
        description: 'Let me reshuffle tasks based on TRF attention and cost.',
        icon: Activity,
        intent: 'optimize',
      },
    ],
    recommendations: [
      'Use quick prompts whenever you need an AI-produced executive brief.',
      'Ledger scan stays synced with Projects → Ledger, so alerts propagate everywhere.',
    ],
  },
  '/projects': {
    id: 'projects',
    persona: 'Sora · Project Intelligence',
    headline: 'I watch TRF, ledger, and capsule health for every workspace.',
    description:
      'Ask me for reasoning traces, capsule risks, or next actions; I read the same APIs that populate the Projects tab so guidance is contextual.',
    specRefs: ['Spec §4.5–§4.8', 'Spec §3.7'],
    prompts: [
      { label: 'Next best action', prompt: 'What is the next best action for the currently selected project?' },
      { label: 'Explain risks', prompt: 'Explain why the highlighted project is high risk and suggest a mitigation plan.' },
      { label: 'Capsule alignment', prompt: 'Are capsule runs drifting from manifests for any project? List top 2 issues.' },
    ],
    actions: [
      {
        id: 'trf-review',
        label: 'Review TRF traces',
        description: 'Open the TRF drawer to inspect entropy/resonance shifts.',
        icon: Brain,
        intent: 'explain',
      },
      {
        id: 'ledger',
        label: 'Audit hash chain',
        description: 'Jump to ledger filters when I surface an integrity warning.',
        icon: BookOpenCheck,
        intent: 'review',
      },
      {
        id: 'auto-plan',
        label: 'Generate plan draft',
        description: 'Let me draft a mitigation plan and push it into Tasks.',
        icon: ListChecks,
        intent: 'optimize',
        pill: 'beta',
      },
    ],
    recommendations: [
      'Whenever you open a project, tap “Review TRF traces” to keep cognition + ledger aligned.',
      'Use the prompts to prefill Chat — they carry the same context objects I see.',
    ],
  },
  '/tasks': {
    id: 'tasks',
    persona: 'Aria · Flow Steward',
    headline: 'Triage workload + unblock tasks with me.',
    description:
      'I watch task priority, owners, and status transitions. Ask me to re-plan or to nudge another persona when something stalls.',
    specRefs: ['Spec §3.4', 'Spec §7.2'],
    prompts: [
      { label: 'Unblock items', prompt: 'Identify blocked tasks and propose unblocking steps.' },
      { label: 'Rebalance', prompt: 'Rebalance workload across personas for the next 48 hours.' },
    ],
    actions: [
      {
        id: 'commit-tie',
        label: 'Link commits → tasks',
        description: 'Ensure Commit→Task mapping is intact before marking done.',
        icon: GitCommit,
        intent: 'review',
      },
      {
        id: 'delegate',
        label: 'Delegate via AI',
        description: 'Let me spin up a draft task + owner pairing for you.',
        icon: UserPlus,
        intent: 'optimize',
      },
    ],
    recommendations: ['Use AI delegation for repetitive triage; it mirrors Tkinter automation.'],
  },
  '/ai/operations': {
    id: 'aiops',
    persona: 'Echo · Driver Guardian',
    headline: 'Driver scheduling + guardrails',
    description:
      'I throttle drivers and watch queue depth. Lean on me before you trigger automations that could breach policy budgets.',
    specRefs: ['Spec §5.12', 'Spec §12.5'],
    prompts: [
      { label: 'Queue health', prompt: 'Summarize driver queue health and recommend throttles.' },
      { label: 'Policy risk', prompt: 'Are any drivers close to breaching governance policy or budget?' },
    ],
    actions: [
      {
        id: 'throttle',
        label: 'Adjust throttles',
        description: 'Use the slider + AI recommendation to keep p95 stable.',
        icon: SlidersHorizontal,
        intent: 'optimize',
      },
      {
        id: 'explain-daemons',
        label: 'Explain daemon status',
        description: 'Ask me to justify why daemons are paused or degraded.',
        icon: Activity,
        intent: 'explain',
      },
    ],
    recommendations: ['Always run a queue health prompt before deploying new workflows.'],
  },
  '/ai/copilot': {
    id: 'copilot',
    persona: 'AIC · Copilot',
    headline: 'Chat + persona orchestration',
    description: 'I keep session notes, run assistant tools, and can pre-seed prompts for you.',
    specRefs: ['Spec §4.1', 'Spec §9.18'],
    prompts: [
      { label: 'Session brief', prompt: 'Summarize the current assistant thread and what it accomplished.' },
      { label: 'Tool plan', prompt: 'Plan which tools to run (code interpreter, file search, function calling) for the stated question.' },
    ],
    actions: [
      {
        id: 'assistant-kit',
        label: 'Curate assistant kit',
        description: 'Toggle toolset per thread, guided by my suggestions.',
        icon: Tool,
        intent: 'optimize',
      },
      {
        id: 'snapshot',
        label: 'Record session snapshot',
        description: 'Save the session state to Projects → Ledger for audit.',
        icon: HardDriveDownload,
        intent: 'review',
      },
    ],
    recommendations: ['Pin the best prompt templates so repeated work stays consistent.'],
  },
  '/work/writer': {
    id: 'writer',
    persona: 'Aria · Canon Writer',
    headline: 'Story + canon guardrails',
    description: 'I balance creative drafting with canon constraints; lean on me to keep tonality and metadata consistent.',
    specRefs: ['Spec §7.5'],
    prompts: [
      { label: 'Canon check', prompt: 'Does this draft conflict with current canon entries? Highlight issues.' },
      { label: 'Tone polish', prompt: 'Polish this document for executive tone without removing cited data.' },
    ],
    actions: [
      {
        id: 'lore',
        label: 'Sync lore packets',
        description: 'Push accepted drafts into canon/pipeline tables.',
        icon: Scroll,
        intent: 'review',
      },
      {
        id: 'draft',
        label: 'Generate first draft',
        description: 'Use Generate Narrative — I will prep a draft with tags + metadata.',
        icon: PenSquare,
        intent: 'optimize',
      },
    ],
    recommendations: ['Let AI do the first pass, then you refine; throughput doubles.'],
  },
  '/observability': {
    id: 'observability',
    persona: 'Oracle · Continuity',
    headline: 'Telemetry + diagnostics',
    description: 'I correlate diagnostics, runtime metrics, and plane health so you can respond before SLOs slip.',
    specRefs: ['Spec §11'],
    prompts: [
      { label: 'Anomaly triage', prompt: 'Highlight anomalies across planes and suggest mitigations.' },
      { label: 'Evidence pack', prompt: 'Assemble an evidence pack of the latest incidents.' },
    ],
    actions: [
      {
        id: 'plane-handoff',
        label: 'Data plane handoff',
        description: 'Use my notes before escalating to infra teams.',
        icon: Server,
        intent: 'explain',
      },
      {
        id: 'autofix',
        label: 'Trigger Auto-Fix',
        description: 'Jump into Auto-Fix when I flag eligible issues.',
        icon: Wrench,
        intent: 'optimize',
      },
    ],
    recommendations: ['Use evidence packs as attachments when pinging regulators or SRE.'],
  },
}

const fallbackConfig: AIGuideConfig = {
  id: 'default',
  persona: 'AIC · Guide',
  headline: 'Contextual intelligence overlay',
  description: 'Use this helper to copy prompts or open reference material directly from any surface.',
  specRefs: ['Spec §0.1'],
  prompts: [
    { label: 'Summarize this page', prompt: 'Give me a 2 sentence summary of the page I am on and how to use it.' },
  ],
  actions: [
    {
      id: 'docs',
      label: 'Open docs mapping',
      description: 'Jump to Docs → Migration map for parity checks.',
      icon: BookOpen,
      intent: 'explain',
    },
  ],
  recommendations: ['Use the prompts whenever you need page-specific tutoring from AIC.'],
}

export const resolveAIGuideConfig = (pathname: string): AIGuideConfig => {
  if (!pathname) return fallbackConfig
  const match = Object.keys(registry)
    .filter((key) => pathname === key || pathname.startsWith(key))
    .sort((a, b) => b.length - a.length)[0]
  return match ? registry[match] : fallbackConfig
}
