import { useMemo, useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Sparkles,
  X,
  Target,
  Rocket,
  ClipboardList,
  Copy,
  MessageSquare,
  CheckCircle2,
  Lightbulb,
} from 'lucide-react'
import { toast } from '../utils/toast'

interface GuidePrompt {
  label: string
  persona: string
  prompt: string
}

interface GuideAction {
  title: string
  detail: string
  prompt: string
}

interface GuideTutorial {
  title: string
  description: string
}

interface GuideProfile {
  matchers: RegExp[]
  persona: string
  personaRole: string
  title: string
  summary: string
  signal: string
  health: 'nominal' | 'watch' | 'alert'
  actions: GuideAction[]
  prompts: GuidePrompt[]
  tutorials: GuideTutorial[]
}

const GUIDE_LIBRARY: GuideProfile[] = [
  {
    matchers: [/^\/$/, /^\/dashboard$/],
    persona: 'Aria',
    personaRole: 'Flow Orchestrator',
    title: 'Mission Control Assistant',
    summary:
      'Aria is watching live telemetry, nudging you toward the widgets and workflows that unblock the day.',
    signal: 'Cadence stable · 92% coverage',
    health: 'nominal',
    actions: [
      {
        title: 'Re-evaluate focus',
        detail: 'Sweep KPIs, tasks, and project cards so the most urgent work sits above the fold.',
        prompt:
          'Review the dashboard telemetry and list the three highest leverage actions I should take right now.',
      },
      {
        title: 'Escalate blockers',
        detail: 'Let Aria flag stale tasks or metrics before they derail the mission cadence.',
        prompt:
          'Highlight every blocker older than 24h and suggest the fastest path to resolution (owner + tactic).',
      },
    ],
    prompts: [
      {
        label: 'Executive brief',
        persona: 'Aria',
        prompt:
          'Give me a concise executive brief of what the dashboard shows plus the one thing that demands attention.',
      },
      {
        label: 'Cross-team sync',
        persona: 'AIC',
        prompt: 'Compare the dashboard KPIs with the task board and surface any mismatches or missing owners.',
      },
    ],
    tutorials: [
      {
        title: 'Use priority beacons',
        description: 'Hover over a widget to see which persona owns it and trigger an AI action instantly.',
      },
      {
        title: 'Quick launch automations',
        description: 'Pin widgets into the quick-launch row so Aria can refresh them whenever you land here.',
      },
      {
        title: 'Share ops notes',
        description: 'Copy a prompt below to capture exactly what Aria is seeing for the next operator.',
      },
    ],
  },
  {
    matchers: [/^\/tasks/],
    persona: 'AIC',
    personaRole: 'Audit Copilot',
    title: 'Task Board Navigator',
    summary:
      'AIC validates dependencies, due dates, and persona balance so the task grid stays aligned with reality.',
    signal: '4 items blocked · review queue',
    health: 'watch',
    actions: [
      {
        title: 'Dependency sweep',
        detail: 'Check which in-progress tasks hinge on incomplete work and queue nudges to the right owners.',
        prompt:
          'List every task whose dependency is not met and specify the owner + unblock recommendation.',
      },
      {
        title: 'Auto-prioritize next 48h',
        detail: 'Ask the copilot to re-rank the backlog around the next two days of outcomes.',
        prompt: 'Reorder the top of the backlog with reasoning focused on the next 48 hours.',
      },
    ],
    prompts: [
      {
        label: 'Stand-up digest',
        persona: 'AIC',
        prompt:
          'Write a stand-up digest summarizing all new task activity (owner, status, ask) to share in chat.',
      },
      {
        label: 'Risk heatmap',
        persona: 'Aria',
        prompt:
          'Analyze the task board and produce a risk heatmap showing where we are likely to slip this week.',
      },
    ],
    tutorials: [
      {
        title: 'Persona lanes',
        description: 'Filter by persona to let the AI inspect one operator lane at a time.',
      },
      {
        title: 'Time-to-done',
        description: 'Use the time remaining badges to decide which items deserve AI help first.',
      },
      {
        title: 'Bulk prompts',
        description: 'Select multiple tasks and run one of the prompts to broadcast a status reset.',
      },
    ],
  },
  {
    matchers: [/^\/projects/],
    persona: 'Aria',
    personaRole: 'Strategic Planner',
    title: 'Project Atlas Guide',
    summary:
      'Aria keeps briefs, linked docs, and decision logs coherent so projects always tell the right story.',
    signal: 'Portfolio healthy · 3 briefs stale',
    health: 'nominal',
    actions: [
      {
        title: 'Refresh briefs',
        detail: 'Pull the latest metrics + learnings into executive-ready blurbs.',
        prompt:
          'Summarize each top-tier project with health, next deliverable, and the single biggest risk to remove.',
      },
      {
        title: 'Link documents',
        detail: 'Make sure research, dashboards, and docs are attached so AI agents stay grounded.',
        prompt:
          'Audit the currently open project and list missing artifacts or integrations that the AI needs.',
      },
    ],
    prompts: [
      {
        label: 'Investor snapshot',
        persona: 'Sora',
        prompt:
          'Draft an investor-ready snapshot summarizing momentum, blockers, and capital needs for this portfolio.',
      },
      {
        label: 'Reallocate effort',
        persona: 'Aria',
        prompt: 'Identify which project should gain resources and which should pause, with reasoning.',
      },
    ],
    tutorials: [
      {
        title: 'Beacon indicators',
        description: 'Each project tile shows beacons Aria watches—open them to see health signals.',
      },
      {
        title: 'Capsule links',
        description: 'Attach workflow capsules directly to projects so automations stay in context.',
      },
      {
        title: 'Version compare',
        description: 'Use the history drawer to diff previous briefs against today’s draft.',
      },
    ],
  },
  {
    matchers: [/^\/chat/],
    persona: 'Sora',
    personaRole: 'Conversation Director',
    title: 'Chat Studio Coach',
    summary:
      'Sora routes personas, references attachments, and suggests phrasing so every reply compounds.',
    signal: 'Multi-persona routing active',
    health: 'nominal',
    actions: [
      {
        title: 'Cite attachments',
        detail: 'Drag a document in and ask Sora to cite exact sections.',
        prompt:
          'Using the currently attached document, craft a reply that cites specific sections and lists next steps.',
      },
      {
        title: 'Blend personas',
        detail: 'Hand off parts of the conversation to AIC or Aria when needed.',
        prompt:
          'Rewrite the last response with AIC auditing compliance and Aria proposing follow-up actions.',
      },
    ],
    prompts: [
      {
        label: 'Escalate to audit mode',
        persona: 'AIC',
        prompt:
          'Take over this thread as AIC and verify that every claim has a cited reference or artifact.',
      },
      {
        label: 'Creative polish',
        persona: 'Sora',
        prompt:
          'Rewrite the latest reply with a storytelling tone while keeping commitments unchanged.',
      },
    ],
    tutorials: [
      {
        title: 'Persona braid',
        description: 'Switch personas in the composer to get multi-voice outputs in one reply.',
      },
      {
        title: 'Command palette',
        description: 'Type / to call up commands, knowledge, or automations without leaving chat.',
      },
      {
        title: 'Document workspace',
        description: 'Keep attachments fresh via the panel to amplify AI recall.',
      },
    ],
  },
  {
    matchers: [/^\/ai\/operations/, /^\/ai\/autofix/, /^\/ai\/os/],
    persona: 'AIC',
    personaRole: 'Ops Sentinel',
    title: 'AI Ops Companion',
    summary: 'AIC inspects driver throttles, operations queues, and governance diff logs for drift.',
    signal: '2 drivers throttled · monitor closely',
    health: 'watch',
    actions: [
      {
        title: 'Tune drivers',
        detail: 'Ask the AI to recommend throttle adjustments before touching the sliders.',
        prompt:
          'Review current driver metrics and propose throttle adjustments that keep throughput high without spiking spend.',
      },
      {
        title: 'Summarize failures',
        detail: 'Compile any recent operation failures, root causes, and remediation steps.',
        prompt:
          'Summarize the last ten document operations, flagging failures plus suggested fixes or rollbacks.',
      },
    ],
    prompts: [
      {
        label: 'Incident brief',
        persona: 'AIC',
        prompt:
          'Generate an incident brief if any driver has been offline in the past hour, including impact and owner.',
      },
      {
        label: 'Workflow savings',
        persona: 'Aria',
        prompt:
          'Inspect running workflows and suggest automation opportunities that save at least 25% cycle time.',
      },
    ],
    tutorials: [
      {
        title: 'Reasoning traces',
        description: 'Open trace logs to see how the AI analyzed a failing run step-by-step.',
      },
      {
        title: 'Driver target sliders',
        description: 'Pair manual tweaks with AI recommendations to stay within guardrails.',
      },
      {
        title: 'Governance feed',
        description: 'Anchor every operation to an audit record so compliance is effortless.',
      },
    ],
  },
  {
    matchers: [/^\/workspace\/health$/],
    persona: 'Chris',
    personaRole: 'Reliability Operator',
    title: 'Workspace Health Guide',
    summary:
      'Chris helps you scan every repo, run safe checks, and trigger auto-fix loops with an audit-friendly workflow.',
    signal: 'Run a dry-run first · enable autofix only when needed',
    health: 'nominal',
    actions: [
      {
        title: 'Run safe dry-run',
        detail: 'Preview commands without executing anything risky.',
        prompt:
          'In Workspace Health, run a dry-run scan and summarize which repos would execute which checks. Highlight any missing autofix scripts.',
      },
      {
        title: 'Execute checks with autofix',
        detail: 'Run checks and invoke auto-fix only on failures.',
        prompt:
          'Execute workspace checks with autofix enabled. Summarize failures and point to the report path + run_id.',
      },
    ],
    prompts: [
      {
        label: 'CLI quickstart (multi-repo)',
        persona: 'Chris',
        prompt:
          "Give me the exact CLI commands to: (1) scan sibling repos, (2) launch the autofix orchestrator, (3) run a single repo through preflight + execute using scripts/osd_run.sh.",
      },
      {
        label: 'Codex handoff prompt',
        persona: 'AIC',
        prompt:
          'Generate a Codex-ready prompt that includes the latest failing check outputs plus REMAINING_TODOS.md and FUTURE_TODOS.md, then list the minimum steps to get back to green.',
      },
    ],
    tutorials: [
      {
        title: 'Start with dry-run',
        description: 'Use dry-run to verify what will execute before turning on auto-fix.',
      },
      {
        title: 'Prefer per-repo remediation',
        description:
          'If a single repo fails, fix it first (or run scripts/osd_autofix.py) before fanning changes out.',
      },
      {
        title: 'Capture evidence',
        description:
          'Use the report_path/run_id fields to attach the evidence to Audit / incident notes.',
      },
    ],
  },
]

const DEFAULT_GUIDE: GuideProfile = {
  matchers: [/^.*/],
  persona: 'Aria',
  personaRole: 'Systems Guide',
  title: 'AI Companion',
  summary:
    'The AI companion watches every workspace, steering you toward the next best action without extra clicks.',
  signal: 'Ready when you are',
  health: 'nominal',
  actions: [
    {
      title: 'Explain this surface',
      detail: 'Ask for a quick orientation whenever you land on a new page.',
      prompt: 'Describe this page, the data in view, and the top next steps you recommend.',
    },
    {
      title: 'Predict blockers',
      detail: 'Let the AI highlight the next thing that could break.',
      prompt: 'Based on what is on screen, what is the most likely blocker within 48 hours?',
    },
  ],
  prompts: [
    {
      label: 'Summarize context',
      persona: 'Aria',
      prompt: 'Summarize what this page is showing me and provide the next two moves.',
    },
    {
      label: 'Recommend automation',
      persona: 'AIC',
      prompt: 'Suggest an automation or workflow I should trigger from here.',
    },
  ],
  tutorials: [
    {
      title: 'Keep the panel nearby',
      description: 'Collapse it when you need space—your preference is remembered per device.',
    },
    {
      title: 'Send prompts to chat',
      description: 'Use the launch buttons to route context directly into the Chat console.',
    },
    {
      title: 'Copy as runbook',
      description: 'Copy any guidance to share with the next operator or auditor.',
    },
  ],
}

const personaAccent: Record<string, string> = {
  Aria: 'from-rose-500/20 to-fuchsia-500/10',
  AIC: 'from-sky-500/20 to-cyan-500/10',
  Sora: 'from-amber-500/20 to-orange-500/10',
}

const matchGuide = (path: string): GuideProfile => {
  const found = GUIDE_LIBRARY.find((guide) => guide.matchers.some((matcher) => matcher.test(path)))
  return found ?? DEFAULT_GUIDE
}

interface SidebarProps {
  pathname: string
}

export default function AIGuideSidebar({ pathname }: SidebarProps) {
  const navigate = useNavigate()
  const guide = useMemo(() => matchGuide(pathname), [pathname])
  const [collapsed, setCollapsed] = useState(() => {
    if (typeof window === 'undefined') return false
    return window.localStorage.getItem('osd-ai-guide-collapsed') === 'true'
  })

  useEffect(() => {
    if (typeof window === 'undefined') return
    window.localStorage.setItem('osd-ai-guide-collapsed', collapsed ? 'true' : 'false')
  }, [collapsed])

  const handleCopy = async (prompt: GuidePrompt) => {
    try {
      await navigator.clipboard.writeText(prompt.prompt)
      toast.success(`Prompt copied for ${prompt.persona}`)
    } catch (error) {
      toast.error('Unable to copy prompt. Copy manually instead.')
    }
  }

  const handleLaunch = (prompt: GuidePrompt) => {
    navigate('/chat', { state: { autoprompt: prompt.prompt } })
    toast.info(`Prompt queued for ${prompt.persona} in Chat`)
  }

  if (collapsed) {
    return (
      <aside className="hidden lg:flex flex-col w-12 flex-shrink-0 items-center">
        <button
          type="button"
          className="mt-2 flex flex-col items-center gap-1 rounded-2xl border border-white/10 bg-slate-900/70 text-white px-2 py-4 hover:bg-slate-900"
          onClick={() => setCollapsed(false)}
          aria-label="Expand AI guidance"
        >
          <Sparkles className="w-4 h-4 text-amber-200" />
          <span className="text-[0.6rem] tracking-[0.4em] uppercase text-white/70">AI</span>
        </button>
      </aside>
    )
  }

  const accent = personaAccent[guide.persona] ?? 'from-slate-700 to-slate-900'
  const healthColor =
    guide.health === 'alert'
      ? 'text-rose-300'
      : guide.health === 'watch'
        ? 'text-amber-300'
        : 'text-emerald-300'

  return (
    <aside className="hidden lg:block w-full lg:w-96 flex-shrink-0">
      <div className={`rounded-3xl border border-white/10 bg-gradient-to-b ${accent} p-4 shadow-2xl backdrop-blur`}> 
        <div className="flex items-start justify-between">
          <div>
            <p className="text-[0.65rem] uppercase tracking-[0.4em] text-white/70">
              {guide.persona} · {guide.personaRole}
            </p>
            <h2 className="text-lg font-semibold text-white">{guide.title}</h2>
            <p className="text-sm text-white/80 mt-1">{guide.summary}</p>
          </div>
          <button
            type="button"
            className="p-2 rounded-full text-white hover:bg-white/10"
            onClick={() => setCollapsed(true)}
            aria-label="Collapse AI guidance"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="mt-4 rounded-2xl border border-white/10 bg-black/20 p-3">
          <div className="flex items-center gap-2 text-white">
            <Sparkles className="w-4 h-4" />
            <span className="text-xs uppercase tracking-[0.3em] text-white/70">Signal</span>
          </div>
          <p className={`text-sm font-semibold mt-1 ${healthColor}`}>{guide.signal}</p>
        </div>

        <section className="mt-4 space-y-3">
          <div className="flex items-center gap-2 text-white">
            <Target className="w-4 h-4" />
            <span className="text-xs uppercase tracking-[0.3em] text-white/70">Recommended actions</span>
          </div>
          {guide.actions.map((action) => (
            <div key={action.title} className="rounded-2xl border border-white/10 bg-white/5 p-3 space-y-2">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="text-sm font-semibold text-white">{action.title}</p>
                  <p className="text-xs text-white/70">{action.detail}</p>
                </div>
                <button
                  type="button"
                  className="px-3 py-1 text-xs rounded-full bg-white/15 text-white hover:bg-white/25"
                  onClick={() =>
                    handleLaunch({ label: action.title, persona: guide.persona, prompt: action.prompt })
                  }
                >
                  Run
                </button>
              </div>
            </div>
          ))}
        </section>

        <section className="mt-4 space-y-3">
          <div className="flex items-center gap-2 text-white">
            <ClipboardList className="w-4 h-4" />
            <span className="text-xs uppercase tracking-[0.3em] text-white/70">AI Prompts</span>
          </div>
          {guide.prompts.map((prompt) => (
            <div key={prompt.label} className="rounded-2xl border border-white/10 bg-black/30 p-3">
              <div className="flex items-center justify-between">
                <p className="text-sm font-semibold text-white">{prompt.label}</p>
                <span className="text-[0.65rem] uppercase tracking-[0.3em] text-white/80">
                  {prompt.persona}
                </span>
              </div>
              <p className="text-xs text-white/75 mt-1">{prompt.prompt}</p>
              <div className="flex items-center gap-2 mt-2 text-xs text-white/80">
                <button
                  type="button"
                  className="flex items-center gap-1 hover:text-white"
                  onClick={() => handleCopy(prompt)}
                >
                  <Copy className="w-3 h-3" />
                  Copy
                </button>
                <button
                  type="button"
                  className="flex items-center gap-1 hover:text-white"
                  onClick={() => handleLaunch(prompt)}
                >
                  <MessageSquare className="w-3 h-3" />
                  Launch
                </button>
              </div>
            </div>
          ))}
        </section>

        <section className="mt-4 space-y-3">
          <div className="flex items-center gap-2 text-white">
            <Lightbulb className="w-4 h-4" />
            <span className="text-xs uppercase tracking-[0.3em] text-white/70">Tutorial cues</span>
          </div>
          {guide.tutorials.map((tutorial) => (
            <div key={tutorial.title} className="rounded-2xl border border-white/10 bg-white/5 p-3 flex gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-300 mt-0.5" />
              <div>
                <p className="text-sm font-semibold text-white">{tutorial.title}</p>
                <p className="text-xs text-white/70">{tutorial.description}</p>
              </div>
            </div>
          ))}
        </section>

        <button
          type="button"
          className="mt-4 w-full flex items-center justify-center gap-2 rounded-2xl bg-white/15 text-white py-2 hover:bg-white/25"
          onClick={() => navigate('/chat')}
        >
          <Rocket className="w-4 h-4" />
          Continue in Chat
        </button>
      </div>
    </aside>
  )
}
