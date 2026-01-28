import { useMemo, useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import {
  X,
  Sparkles,
  MessageSquare,
  Bot,
  FileText,
  Wand2,
  Target,
  Rocket,
  ClipboardList,
  Copy,
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
        description: 'Use the history drawer to diff previous briefs against today\'s draft.',
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

interface UnifiedAIPanelProps {
  currentPath: string
  open: boolean
  onToggle: (open: boolean) => void
}

export function UnifiedAIPanel({ currentPath, open, onToggle }: UnifiedAIPanelProps) {
  const navigate = useNavigate()
  const guide = useMemo(() => matchGuide(currentPath), [currentPath])

  const quickActions = [
    {
      icon: MessageSquare,
      label: 'Chat',
      path: '/chat',
      description: 'Start a conversation',
    },
    {
      icon: Bot,
      label: 'AI Copilot',
      path: '/ai/copilot',
      description: 'Full copilot console',
    },
    {
      icon: FileText,
      label: 'Writer',
      path: '/work/writer',
      description: 'Document generation',
    },
    {
      icon: Wand2,
      label: 'Research',
      path: '/research',
      description: 'Research hub',
    },
  ]

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

  if (!open) return null

  const accent = personaAccent[guide.persona] ?? 'from-slate-700 to-slate-900'
  const healthColor =
    guide.health === 'alert'
      ? 'text-rose-300'
      : guide.health === 'watch'
        ? 'text-amber-300'
        : 'text-emerald-300'

  return (
    <div className="fixed right-0 top-0 bottom-0 w-96 bg-gradient-to-b from-slate-900 via-slate-900/98 to-slate-900 backdrop-blur-xl border-l border-slate-700/50 shadow-2xl z-[55] flex flex-col overflow-hidden animate-in slide-in-from-right duration-300">
      {/* Header */}
      <div className="p-5 border-b border-slate-700/50 bg-gradient-to-r from-slate-800/50 to-slate-900/50 flex items-center justify-between flex-shrink-0">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-gradient-to-br from-primary-500/30 to-violet-500/30 border border-primary-400/20 shadow-lg">
            <Sparkles className="w-5 h-5 text-primary-300" />
          </div>
          <div>
            <h3 className="text-base font-semibold text-white">AI Assistant</h3>
            <p className="text-xs text-slate-400 mt-0.5">{guide.persona} · {guide.personaRole}</p>
          </div>
        </div>
        <button
          onClick={() => onToggle(false)}
          className="p-2 hover:bg-slate-800/80 rounded-lg transition-all text-slate-400 hover:text-white hover:rotate-90 duration-200"
          aria-label="Close panel"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Content - Scrollable */}
      <div className="flex-1 overflow-y-auto p-5 space-y-5 scrollbar-thin scrollbar-thumb-slate-700 scrollbar-track-transparent">
        {/* Contextual Guidance Section */}
        <div className={`rounded-2xl border border-white/10 bg-gradient-to-b ${accent} p-5 space-y-4 shadow-lg`}>
          <div>
            <h4 className="text-sm font-semibold text-white">{guide.title}</h4>
            <p className="text-xs text-white/80 mt-1">{guide.summary}</p>
          </div>

          <div className="rounded-xl border border-white/10 bg-black/30 p-4 backdrop-blur-sm">
            <div className="flex items-center gap-2 text-white mb-2">
              <div className={`p-1.5 rounded-lg ${healthColor === 'text-emerald-300' ? 'bg-emerald-500/20' : healthColor === 'text-amber-300' ? 'bg-amber-500/20' : 'bg-rose-500/20'}`}>
                <Sparkles className="w-3.5 h-3.5" />
              </div>
              <span className="text-xs uppercase tracking-[0.3em] text-white/70 font-medium">Signal</span>
            </div>
            <p className={`text-sm font-semibold ${healthColor} leading-relaxed`}>{guide.signal}</p>
          </div>

          {/* Recommended Actions */}
          {guide.actions.length > 0 && (
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-white">
                <Target className="w-4 h-4" />
                <span className="text-xs uppercase tracking-[0.3em] text-white/70">Recommended actions</span>
              </div>
              {guide.actions.map((action) => (
                <div key={action.title} className="rounded-xl border border-white/10 bg-white/5 hover:bg-white/10 p-4 space-y-3 transition-all duration-200 group">
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1">
                      <p className="text-sm font-semibold text-white mb-1.5">{action.title}</p>
                      <p className="text-xs text-white/70 leading-relaxed">{action.detail}</p>
                    </div>
                    <button
                      type="button"
                      className="px-4 py-1.5 text-xs font-medium rounded-full bg-gradient-to-r from-primary-500/20 to-violet-500/20 border border-primary-400/30 text-white hover:from-primary-500/30 hover:to-violet-500/30 transition-all duration-200 whitespace-nowrap"
                      onClick={() =>
                        handleLaunch({ label: action.title, persona: guide.persona, prompt: action.prompt })
                      }
                    >
                      Run
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* AI Prompts */}
          {guide.prompts.length > 0 && (
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-white">
                <ClipboardList className="w-4 h-4" />
                <span className="text-xs uppercase tracking-[0.3em] text-white/70">AI Prompts</span>
              </div>
              {guide.prompts.map((prompt) => (
                <div key={prompt.label} className="rounded-xl border border-white/10 bg-black/30 hover:bg-black/40 p-4 transition-all duration-200 group">
                  <div className="flex items-center justify-between mb-2">
                    <p className="text-sm font-semibold text-white">{prompt.label}</p>
                    <span className="text-[0.65rem] uppercase tracking-[0.3em] text-white/80 bg-white/10 px-2 py-1 rounded-full">
                      {prompt.persona}
                    </span>
                  </div>
                  <p className="text-xs text-white/75 mt-2 leading-relaxed mb-3">{prompt.prompt}</p>
                  <div className="flex items-center gap-2 text-xs">
                    <button
                      type="button"
                      className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white/10 hover:bg-white/20 text-white/90 hover:text-white transition-all duration-200"
                      onClick={() => handleCopy(prompt)}
                    >
                      <Copy className="w-3.5 h-3.5" />
                      Copy
                    </button>
                    <button
                      type="button"
                      className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-primary-500/20 hover:bg-primary-500/30 border border-primary-400/30 text-white hover:text-white transition-all duration-200"
                      onClick={() => handleLaunch(prompt)}
                    >
                      <MessageSquare className="w-3.5 h-3.5" />
                      Launch
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Tutorials */}
          {guide.tutorials.length > 0 && (
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-white">
                <Lightbulb className="w-4 h-4" />
                <span className="text-xs uppercase tracking-[0.3em] text-white/70">Tutorial cues</span>
              </div>
              {guide.tutorials.map((tutorial) => (
                <div key={tutorial.title} className="rounded-xl border border-white/10 bg-white/5 hover:bg-white/10 p-4 flex gap-3 transition-all duration-200 group">
                  <div className="p-1.5 rounded-lg bg-emerald-500/20 border border-emerald-400/30 flex-shrink-0 h-fit">
                    <CheckCircle2 className="w-4 h-4 text-emerald-300" />
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-semibold text-white mb-1">{tutorial.title}</p>
                    <p className="text-xs text-white/70 leading-relaxed">{tutorial.description}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Quick Actions Section */}
        <div className="pt-4 border-t border-slate-700/50">
          <p className="text-xs uppercase tracking-wider text-slate-500 mb-4 font-semibold">Quick Actions</p>
          <div className="space-y-2.5">
            {quickActions.map((action) => {
              const Icon = action.icon
              const isActive = currentPath === action.path || currentPath.startsWith(action.path + '/')
              return (
                <Link
                  key={action.path}
                  to={action.path}
                  onClick={() => onToggle(false)}
                  className={`
                    flex items-center gap-3 p-3.5 rounded-xl border transition-all duration-200 group
                    ${
                      isActive
                        ? 'border-primary-500/70 bg-gradient-to-r from-primary-500/20 to-primary-500/10 text-white shadow-lg shadow-primary-500/20'
                        : 'border-slate-700/50 bg-slate-800/30 hover:bg-slate-800/50 hover:border-slate-600 text-slate-200 hover:shadow-md'
                    }
                  `}
                >
                  <div
                    className={`p-2.5 rounded-lg transition-all duration-200 ${
                      isActive ? 'bg-primary-500/30 shadow-lg shadow-primary-500/20' : 'bg-slate-700/50 group-hover:bg-slate-700/70'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium">{action.label}</p>
                    <p className="text-xs text-slate-400 truncate mt-0.5">{action.description}</p>
                  </div>
                  {isActive && (
                    <div className="w-2 h-2 rounded-full bg-primary-400 animate-pulse" />
                  )}
                </Link>
              )
            })}
          </div>
        </div>

        {/* Current Page Info */}
        <div className="pt-4 border-t border-slate-700/50">
          <p className="text-xs uppercase tracking-wider text-slate-500 mb-3 font-semibold">Current Page</p>
          <div className="p-3.5 rounded-xl border border-slate-700/50 bg-slate-800/40 backdrop-blur-sm">
            <p className="text-xs text-slate-300 font-mono break-all leading-relaxed">{currentPath}</p>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="p-5 border-t border-slate-700/50 bg-gradient-to-t from-slate-900 to-transparent flex-shrink-0 space-y-3">
        <Link
          to="/chat"
          onClick={() => onToggle(false)}
          className="w-full flex items-center justify-center gap-2.5 px-4 py-3 bg-white/10 hover:bg-white/20 border border-white/20 text-white rounded-xl transition-all duration-200 text-sm font-medium hover:shadow-lg hover:shadow-white/10"
        >
          <Rocket className="w-4 h-4" />
          Continue in Chat
        </Link>
        <Link
          to="/ai/copilot"
          onClick={() => onToggle(false)}
          className="w-full flex items-center justify-center gap-2.5 px-4 py-3 bg-gradient-to-r from-primary-500 to-violet-600 text-white rounded-xl hover:from-primary-600 hover:to-violet-700 transition-all duration-200 text-sm font-semibold shadow-lg shadow-primary-500/30 hover:shadow-xl hover:shadow-primary-500/40"
        >
          <Sparkles className="w-4 h-4" />
          Open Full Console
        </Link>
      </div>
    </div>
  )
}

