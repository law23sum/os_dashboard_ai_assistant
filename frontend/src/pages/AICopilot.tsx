import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useEffect, useMemo, useState } from 'react'
import type { FormEvent } from 'react'
import {
  Brain,
  Send,
  MessageSquare,
  Bot,
  FileText,
  Activity,
  Wand2,
  Sparkles,
  Loader2,
  ServerCog,
  Play,
  StopCircle,
  RotateCw,
  Cpu,
  Plug,
} from 'lucide-react'
import apiClient, { apiPath } from '../lib/apiClient'
import { extractArray } from '../lib/responseHelpers'
import { API } from '../api'
import type {
  PersonasResponse,
  ChatMessage,
  DocumentOperation,
  ReasoningTrace,
  DriverSchedulingSnapshot,
  DriverQueueMetric,
  AIOSStatus,
} from '../types'
import { toast } from '../utils/toast'

type AssistantTool = 'code_interpreter' | 'file_search' | 'function_calling'
type AssistantStatus = 'completed' | 'running' | 'error'

type AssistantSession = {
  id: string
  assistant_id: string
  thread_id: string
  run_id: string
  question: string
  tools: AssistantTool[]
  status: AssistantStatus
  timestamp: string
  notes?: string
}

const ASSISTANT_SESSION_STORAGE = 'osd_assistant_sessions'

const ASSISTANT_TOOL_OPTIONS: { label: string; value: AssistantTool }[] = [
  { label: 'Code Interpreter', value: 'code_interpreter' },
  { label: 'File Search', value: 'file_search' },
  { label: 'Function Calling', value: 'function_calling' },
]

const ASSISTANT_STATUS_OPTIONS: { label: string; value: AssistantStatus }[] = [
  { label: 'Completed', value: 'completed' },
  { label: 'Running', value: 'running' },
  { label: 'Needs Attention', value: 'error' },
]

const ASSISTANT_TOOL_LABELS: Record<AssistantTool, string> = {
  code_interpreter: 'Code Interpreter',
  file_search: 'File Search',
  function_calling: 'Function Calling',
}

const isAssistantTool = (value: unknown): value is AssistantTool =>
  typeof value === 'string' && Object.prototype.hasOwnProperty.call(ASSISTANT_TOOL_LABELS, value)

const isAssistantStatus = (value: unknown): value is AssistantStatus =>
  typeof value === 'string' && ASSISTANT_STATUS_OPTIONS.some((option) => option.value === value)

const fetchPersonas = async (): Promise<PersonasResponse> => {
  const { data } = await apiClient.get<PersonasResponse>(apiPath('personas'))
  return data
}

const updatePersona = async (persona: string): Promise<PersonasResponse> => {
  const { data } = await apiClient.post<PersonasResponse>(apiPath('personas'), { persona })
  return data
}

const fetchChatHistory = async (persona: string): Promise<ChatMessage[]> => {
  const { data } = await apiClient.get(apiPath('chat/'), { params: { persona } })
  return extractArray<ChatMessage>(data, ['messages', 'items'])
}

const sendChatMessage = async (payload: { persona: string; content: string }): Promise<void> => {
  await apiClient.post(apiPath('chat/'), {
    persona: payload.persona,
    role: 'user',
    kind: 'chat',
    content: payload.content,
  })
}

const generateNarrative = async (payload: {
  doc_type: string
  theme: string
  genre: string
  title: string
}): Promise<string> => {
  const { data } = await apiClient.post<{ content: string }>(apiPath('writer/generate'), payload)
  return data.content
}

const fetchOperations = async (): Promise<DocumentOperation[]> => {
  const { data } = await apiClient.get(apiPath('operations/'), { params: { limit: 25 } })
  return extractArray<DocumentOperation>(data, ['operations', 'items'])
}

const fetchReasoningHistory = async (): Promise<ReasoningTrace[]> => {
  const { data } = await apiClient.get<ReasoningTrace[]>(apiPath('reasoning/history'), {
    params: { limit: 6 },
  })
  return data
}

const fetchDriverMetrics = async (): Promise<DriverSchedulingSnapshot | null> => {
  try {
    const { data } = await apiClient.get<DriverSchedulingSnapshot>(apiPath('ai/drivers/metrics'))
    return data
  } catch (error) {
    return null
  }
}

const fetchAIOSStatus = async (): Promise<AIOSStatus | null> => {
  try {
    const { data } = await apiClient.get<AIOSStatus>(apiPath('ai/os/status'))
    return data
  } catch (error) {
    return null
  }
}

const fetchDaemons = async (): Promise<any[]> => {
  try {
    const response = await API.daemons()
    if (Array.isArray(response)) {
      return response
    }
    if (response && typeof response === 'object' && Array.isArray(response.daemons)) {
      return response.daemons
    }
    return []
  } catch (error) {
    return []
  }
}

const formatDate = (value?: string | null) => {
  if (!value) return '—'
  return new Date(value).toLocaleString()
}

export default function AICopilot() {
  const queryClient = useQueryClient()
  const personasQuery = useQuery({ queryKey: ['personas'], queryFn: fetchPersonas })
  const [activePersona, setActivePersona] = useState('AIC')
  const [chatInput, setChatInput] = useState('')
  const [docTheme, setDocTheme] = useState('Executive summary')
  const [docTitle, setDocTitle] = useState('Quarterly Readout')
  const [docGenre, setDocGenre] = useState('Professional')
  const [docType, setDocType] = useState('Briefing')
  const [driverTargets, setDriverTargets] = useState<Record<string, number>>({})
  const [assistantSessions, setAssistantSessions] = useState<AssistantSession[]>([])
  const [assistantQuestion, setAssistantQuestion] = useState('Summarize the latest audit log')
  const [assistantTools, setAssistantTools] = useState<AssistantTool[]>(['code_interpreter'])
  const [assistantNotes, setAssistantNotes] = useState('')
  const [assistantStatus, setAssistantStatus] = useState<AssistantStatus>('completed')

  useEffect(() => {
    if (typeof window === 'undefined') return
    try {
      const cached = window.localStorage.getItem(ASSISTANT_SESSION_STORAGE)
      if (!cached) return
      const parsed = JSON.parse(cached)
      if (!Array.isArray(parsed)) return
      const sanitized: AssistantSession[] = parsed
        .filter((session) => session && typeof session.id === 'string' && typeof session.question === 'string')
        .map((session) => {
          const safeTools: AssistantTool[] = Array.isArray(session.tools)
            ? session.tools.filter((tool: unknown): tool is AssistantTool => isAssistantTool(tool))
            : []
          const safeStatus: AssistantStatus = isAssistantStatus(session.status) ? session.status : 'completed'
          const normalized: AssistantSession = {
            id: session.id,
            assistant_id: typeof session.assistant_id === 'string' ? session.assistant_id : 'cli-local',
            thread_id: typeof session.thread_id === 'string' ? session.thread_id : `thread-${session.id}`,
            run_id: typeof session.run_id === 'string' ? session.run_id : `run-${session.id}`,
            question: session.question,
            tools: safeTools.length ? safeTools : ['code_interpreter'],
            status: safeStatus,
            timestamp: typeof session.timestamp === 'string' ? session.timestamp : new Date().toISOString(),
            notes: typeof session.notes === 'string' ? session.notes : undefined,
          }
          return normalized
        })
      setAssistantSessions(sanitized)
    } catch (error) {
      console.warn('Failed to restore assistant sessions', error)
    }
  }, [])

  useEffect(() => {
    if (typeof window === 'undefined') return
    if (!assistantSessions.length) {
      window.localStorage.removeItem(ASSISTANT_SESSION_STORAGE)
      return
    }
    window.localStorage.setItem(ASSISTANT_SESSION_STORAGE, JSON.stringify(assistantSessions))
  }, [assistantSessions])

  const personaMutation = useMutation({
    mutationFn: updatePersona,
    onSuccess: (payload) => {
      toast.success(`Active persona set to ${payload.active}`)
      queryClient.invalidateQueries({ queryKey: ['personas'] })
    },
    onError: (error) => {
      toast.error(error instanceof Error ? error.message : 'Unable to update persona')
    },
  })

  const chatQuery = useQuery({
    queryKey: ['copilot-chat', activePersona],
    queryFn: () => fetchChatHistory(activePersona),
    refetchInterval: 15000,
  })

  const chatMutation = useMutation({
    mutationFn: sendChatMessage,
    onSuccess: () => {
      setChatInput('')
      queryClient.invalidateQueries({ queryKey: ['copilot-chat', activePersona] })
    },
    onError: () => toast.error('Unable to send message'),
  })

  const docMutation = useMutation({
    mutationFn: generateNarrative,
    onSuccess: (content) => {
      toast.info('Draft ready in the Writer workspace')
      navigator.clipboard
        .writeText(content)
        .then(() => toast.success('Draft copied to clipboard'))
        .catch(() => {})
    },
    onError: () => toast.error('Generation failed'),
  })

  const operationsQuery = useQuery({
    queryKey: ['copilot-operations'],
    queryFn: fetchOperations,
    refetchInterval: 20000,
  })

  const reasoningQuery = useQuery({
    queryKey: ['copilot-reasoning'],
    queryFn: fetchReasoningHistory,
    refetchInterval: 40000,
  })

  const driverMetricsQuery = useQuery({
    queryKey: ['copilot-driver-metrics'],
    queryFn: fetchDriverMetrics,
    refetchInterval: 25000,
  })

  const aiosStatusQuery = useQuery({
    queryKey: ['copilot-aios'],
    queryFn: fetchAIOSStatus,
    refetchInterval: 30000,
  })

  const daemonsQuery = useQuery({
    queryKey: ['copilot-daemons'],
    queryFn: fetchDaemons,
    refetchInterval: 20000,
  })

  const personas = personasQuery.data?.personas ?? []
  const chatMessages = chatQuery.data ?? []
  const operations = operationsQuery.data ?? []
  const reasoningTraces = reasoningQuery.data ?? []
  const driverSnapshot = driverMetricsQuery.data
  const aiosStatus = aiosStatusQuery.data
  const daemons = daemonsQuery.data ?? []
  const assistantHistory = assistantSessions.slice(0, 6)
  const assistantLogDisabled = !assistantQuestion.trim() || assistantTools.length === 0

  const personaDescs = useMemo(() => {
    return personas.reduce<Record<string, string>>((acc, persona) => {
      acc[persona.name] = persona.role
      return acc
    }, {})
  }, [personas])

  const toggleAssistantTool = (tool: AssistantTool) => {
    setAssistantTools((prev) => {
      if (prev.includes(tool)) {
        return prev.filter((value) => value !== tool)
      }
      return [...prev, tool]
    })
  }

  const handleAssistantLog = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const question = assistantQuestion.trim()
    if (!question) {
      toast.error('Add a question or command to log the run')
      return
    }
    if (!assistantTools.length) {
      toast.error('Select at least one tool that was used')
      return
    }
    const seed = `${Date.now()}-${Math.random().toString(16).slice(2)}`
    const timestamp = new Date().toISOString()
    const newSession: AssistantSession = {
      id: `session-${seed}`,
      assistant_id: 'cli-local',
      thread_id: `thread-${seed}`,
      run_id: `run-${seed}`,
      question,
      tools: assistantTools,
      status: assistantStatus,
      timestamp,
      notes: assistantNotes.trim() || undefined,
    }
    setAssistantSessions((prev) => [newSession, ...prev].slice(0, 40))
    setAssistantQuestion('')
    setAssistantNotes('')
    if (assistantStatus !== 'running') {
      setAssistantStatus('completed')
    }
    toast.success('Assistants CLI run logged')
  }

  const handleClearAssistantLog = () => {
    setAssistantSessions([])
    toast.info('Cleared local Assistants history')
  }

  const handlePersonaSelect = (persona: string) => {
    setActivePersona(persona)
    personaMutation.mutate(persona)
  }

  const handleSend = () => {
    if (!chatInput.trim()) return
    chatMutation.mutate({ persona: activePersona, content: chatInput.trim() })
  }

  const handleGenerateDoc = () => {
    docMutation.mutate({
      doc_type: docType,
      theme: docTheme,
      genre: docGenre,
      title: docTitle,
    })
  }

  const daemonToggleMutation = useMutation({
    mutationFn: async ({ name, enabled }: { name: string; enabled: boolean }) =>
      API.toggleDaemon(name, enabled),
    onSuccess: (_, variables) => {
      toast.success(`${variables.enabled ? 'Enabled' : 'Disabled'} ${variables.name}`)
      queryClient.invalidateQueries({ queryKey: ['copilot-daemons'] })
    },
    onError: () => toast.error('Unable to update daemon'),
  })

  const daemonRunMutation = useMutation({
    mutationFn: (name: string) => API.runDaemon(name),
    onSuccess: (_, name) => {
      toast.info(`Triggered ${name}`)
      queryClient.invalidateQueries({ queryKey: ['copilot-daemons'] })
    },
    onError: () => toast.error('Daemon run failed'),
  })

  const orchestratorMutation = useMutation({
    mutationFn: async (action: 'start' | 'stop' | 'restart') => {
      const { data } = await apiClient.post<AIOSStatus>(apiPath('ai/os/orchestrator'), { action })
      return data
    },
    onSuccess: (_, action) => {
      const labels: Record<typeof action, string> = {
        start: 'started',
        stop: 'stopped',
        restart: 'restarted',
      }
      toast.success(`Orchestrator ${labels[action]}`)
      queryClient.invalidateQueries({ queryKey: ['copilot-aios'] })
    },
    onError: () => toast.error('Failed to update orchestrator'),
  })

  const driverThrottleMutation = useMutation({
    mutationFn: async ({
      driver_id,
      mode,
      target_rate,
    }: {
      driver_id: string
      mode: 'auto' | 'manual'
      target_rate: number
    }) => {
      await apiClient.post(apiPath('ai/drivers/throttle'), {
        driver_id,
        mode,
        target_rate,
      })
    },
    onSuccess: () => {
      toast.success('Driver throttle updated')
      queryClient.invalidateQueries({ queryKey: ['copilot-driver-metrics'] })
    },
    onError: () => toast.error('Unable to update driver target'),
  })

  const handleDriverRateChange = (driverId: string, value: number) => {
    setDriverTargets((prev) => ({ ...prev, [driverId]: value }))
  }

  const handleDriverApply = (driverId: string, mode: 'auto' | 'manual') => {
    const queue = driverSnapshot?.queues.find((entry) => entry.driver_id === driverId)
    const target = driverTargets[driverId] ?? queue?.admission_rate ?? 0.85
    driverThrottleMutation.mutate({
      driver_id: driverId,
      mode,
      target_rate: mode === 'auto' ? 0.85 : target,
    })
  }

  const orchestratorStatus = aiosStatus?.orchestrator.status ?? 'unknown'

  return (
    <div className="px-4 py-6 sm:px-0 space-y-6">
      <header>
        <p className="text-xs uppercase tracking-[0.35em] text-gray-500 dark:text-gray-500">AI Control Room</p>
        <h2 className="text-3xl font-bold text-gray-900 dark:text-white mt-1">Copilot Console</h2>
        <p className="text-gray-600 dark:text-gray-400 mt-2 max-w-3xl">
          Unified panel for personas, conversations, document generation, reasoning traces, and the new
          OpenAI Assistants workflow. Mirrors the legacy Tkinter capabilities while layering in the latest CLI tools.
        </p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <section className="bg-white dark:bg-gray-900/70 border border-gray-200 dark:border-gray-800 rounded-2xl p-5 space-y-4">
          <div className="flex items-center gap-3">
            <Brain className="w-5 h-5 text-primary-500" />
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Personas & Operating Mode</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400">Switch the lead persona across all AI workflows.</p>
            </div>
          </div>
          <div className="space-y-2">
            {personas.length === 0 && <p className="text-sm text-gray-500">Loading personas...</p>}
            {personas.map((persona) => (
              <button
                key={persona.name}
                onClick={() => handlePersonaSelect(persona.name)}
                className={`w-full text-left px-4 py-3 rounded-xl border ${
                  activePersona === persona.name
                    ? 'bg-primary-600 text-white border-primary-500'
                    : 'border-gray-200 dark:border-gray-800 text-gray-800 dark:text-gray-100 bg-gray-50 dark:bg-gray-800/60'
                }`}
              >
                <div className="font-semibold">{persona.name}</div>
                <div className="text-xs opacity-80">{persona.role}</div>
              </button>
            ))}
          </div>
        </section>

        <section className="bg-white dark:bg-gray-900/70 border border-gray-200 dark:border-gray-800 rounded-2xl p-5 space-y-4 lg:col-span-2">
          <div className="flex items-center gap-3">
            <MessageSquare className="w-5 h-5 text-primary-500" />
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Dialogue & Triage</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                One-tap access to the shared chat stream for the selected persona.
              </p>
            </div>
          </div>
          <div className="min-h-[220px] bg-gray-50 dark:bg-gray-900/40 rounded-xl p-4 space-y-3 overflow-y-auto">
            {chatMessages.slice(-6).map((msg) => (
              <div key={msg.id} className="flex flex-col text-sm">
                <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
                  <span className="font-semibold text-gray-700 dark:text-gray-200">{msg.persona}</span>
                  <span>{new Date(msg.created_at).toLocaleTimeString()}</span>
                </div>
                <div className="text-gray-800 dark:text-gray-100">{msg.content}</div>
              </div>
            ))}
            {chatMessages.length === 0 && <p className="text-sm text-gray-500">No history yet. Start the conversation.</p>}
          </div>
          <div className="flex gap-3">
            <input
              type="text"
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              placeholder={`Ask ${activePersona} anything...`}
              className="flex-1 px-4 py-2 rounded-xl border border-gray-200 dark:border-gray-700 bg-transparent focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
            <button
              onClick={handleSend}
              disabled={chatMutation.isPending || !chatInput.trim()}
              className="inline-flex items-center px-4 py-2 rounded-xl bg-primary-600 text-white hover:bg-primary-700 disabled:opacity-50"
            >
              {chatMutation.isPending ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Send className="w-4 h-4 mr-2" />}
              Send
            </button>
          </div>
        </section>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <section className="bg-white dark:bg-gray-900/70 border border-gray-200 dark:border-gray-800 rounded-2xl p-5 space-y-3">
          <div className="flex items-center gap-3">
            <FileText className="w-5 h-5 text-primary-500" />
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Document Generator</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400">Fast narrative drafts streamed into the Writer workspace.</p>
            </div>
          </div>
          <input
            value={docTitle}
            onChange={(e) => setDocTitle(e.target.value)}
            className="w-full px-3 py-2 rounded-lg border border-gray-200 dark:border-gray-700 bg-transparent text-sm"
            placeholder="Title"
          />
          <input
            value={docTheme}
            onChange={(e) => setDocTheme(e.target.value)}
            className="w-full px-3 py-2 rounded-lg border border-gray-200 dark:border-gray-700 bg-transparent text-sm"
            placeholder="Theme / summary"
          />
          <div className="grid grid-cols-2 gap-3">
            <select
              value={docType}
              onChange={(e) => setDocType(e.target.value)}
              className="px-3 py-2 rounded-lg border border-gray-200 dark:border-gray-700 bg-transparent text-sm"
            >
              {['Briefing', 'Memo', 'Analysis', 'Report'].map((type) => (
                <option key={type} value={type}>
                  {type}
                </option>
              ))}
            </select>
            <select
              value={docGenre}
              onChange={(e) => setDocGenre(e.target.value)}
              className="px-3 py-2 rounded-lg border border-gray-200 dark:border-gray-700 bg-transparent text-sm"
            >
              {['Professional', 'Narrative', 'Executive', 'Technical'].map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </div>
          <button
            onClick={handleGenerateDoc}
            disabled={docMutation.isPending}
            className="inline-flex items-center justify-center w-full px-4 py-2 rounded-xl bg-gray-900 text-white hover:bg-gray-800 disabled:opacity-50"
          >
            {docMutation.isPending ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Wand2 className="w-4 h-4 mr-2" />}
            Generate Draft
          </button>
          <p className="text-xs text-gray-500 dark:text-gray-400">
            Output is copied to your clipboard and saved to <strong>Writer → Documents</strong>.
          </p>
        </section>

        <section className="bg-white dark:bg-gray-900/70 border border-gray-200 dark:border-gray-800 rounded-2xl p-5 space-y-3">
          <div className="flex items-center gap-3">
            <Activity className="w-5 h-5 text-primary-500" />
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Operations Ledger</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400">Live view of AI document ops mirrored from Tkinter.</p>
            </div>
          </div>
          <div className="space-y-3 text-sm">
            {operations.slice(0, 5).map((op) => (
              <div key={op.id} className="p-3 rounded-lg border border-gray-100 dark:border-gray-800 bg-gray-50 dark:bg-gray-900/40">
                <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
                  <span>{op.integration_type}</span>
                  <span>{formatDate(op.started_at)}</span>
                </div>
                <div className="font-semibold text-gray-900 dark:text-gray-100">{op.title}</div>
                <div className="text-xs uppercase tracking-wide text-primary-600 mt-1">{op.status}</div>
              </div>
            ))}
            {operations.length === 0 && <p className="text-gray-500 dark:text-gray-400 text-sm">No queued operations.</p>}
          </div>
        </section>

        <section className="bg-white dark:bg-gray-900/70 border border-gray-200 dark:border-gray-800 rounded-2xl p-5 space-y-3">
          <div className="flex items-center gap-3">
            <Bot className="w-5 h-5 text-primary-500" />
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Reasoning Traces</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400">Latest canonical reasoning runs from the AI OS plane.</p>
            </div>
          </div>
          <div className="space-y-3 text-sm">
            {reasoningTraces.slice(0, 4).map((trace) => (
              <div key={trace.id} className="p-3 rounded-lg border border-gray-100 dark:border-gray-800 bg-gray-50 dark:bg-gray-900/40">
                <div className="text-xs text-gray-500 dark:text-gray-400">{formatDate(trace.created_at)}</div>
                <div className="font-semibold text-gray-900 dark:text-gray-100">{trace.query}</div>
                <div className="text-xs text-gray-600 dark:text-gray-400 mt-1">{trace.final_conclusion}</div>
              </div>
            ))}
            {reasoningTraces.length === 0 && (
              <p className="text-gray-500 dark:text-gray-400 text-sm">No reasoning traces yet. Run one from AI Ops → Reasoning.</p>
            )}
          </div>
        </section>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <section className="bg-white dark:bg-gray-900/70 border border-gray-200 dark:border-gray-800 rounded-2xl p-5 space-y-3">
          <div className="flex items-center gap-3">
            <ServerCog className="w-5 h-5 text-primary-500" />
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">AI Orchestrator</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400">Snapshot of the shared AI OS runtime.</p>
            </div>
          </div>
          {aiosStatus ? (
            <>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">Status</p>
                  <p className="text-xl font-semibold text-gray-900 dark:text-white capitalize">{orchestratorStatus}</p>
                </div>
                <div className="text-right text-xs text-gray-500">
                  <p>Workflows {aiosStatus.orchestrator.workflows_active}</p>
                  <p>Nodes {aiosStatus.orchestrator.nodes_online}</p>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-2 text-xs text-gray-500 dark:text-gray-400">
                <div>
                  <p className="uppercase tracking-[0.3em]">Last start</p>
                  <p className="font-semibold text-gray-900 dark:text-gray-100">
                    {aiosStatus.orchestrator.last_started
                      ? new Date(aiosStatus.orchestrator.last_started).toLocaleString()
                      : '—'}
                  </p>
                </div>
                <div>
                  <p className="uppercase tracking-[0.3em]">Version</p>
                  <p className="font-semibold text-gray-900 dark:text-gray-100">{aiosStatus.orchestrator.version}</p>
                </div>
              </div>
              <div className="flex flex-wrap gap-2 pt-2">
                <button
                  onClick={() => orchestratorMutation.mutate('start')}
                  className="flex-1 inline-flex items-center justify-center gap-1 rounded-xl border border-gray-200 px-3 py-1.5 text-xs text-gray-800 dark:text-gray-100 dark:border-gray-700"
                >
                  <Play className="w-4 h-4" /> Start
                </button>
                <button
                  onClick={() => orchestratorMutation.mutate('stop')}
                  className="flex-1 inline-flex items-center justify-center gap-1 rounded-xl border border-gray-200 px-3 py-1.5 text-xs text-gray-800 dark:text-gray-100 dark:border-gray-700"
                >
                  <StopCircle className="w-4 h-4" /> Stop
                </button>
                <button
                  onClick={() => orchestratorMutation.mutate('restart')}
                  className="flex-1 inline-flex items-center justify-center gap-1 rounded-xl bg-primary-600 text-white px-3 py-1.5 text-xs"
                >
                  <RotateCw className="w-4 h-4" /> Restart
                </button>
              </div>
            </>
          ) : (
            <p className="text-sm text-gray-500 dark:text-gray-400">AI OS offline. Start the backend to view status.</p>
          )}
        </section>

        <section className="bg-white dark:bg-gray-900/70 border border-gray-200 dark:border-gray-800 rounded-2xl p-5 space-y-3">
          <div className="flex items-center gap-3">
            <Plug className="w-5 h-5 text-primary-500" />
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Daemon Control</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400">Mirrors the Tkinter daemon toggles.</p>
            </div>
          </div>
          <div className="space-y-3 text-sm">
            {daemons.slice(0, 5).map((daemon) => (
              <div
                key={daemon.name}
                className="p-3 rounded-xl border border-gray-100 dark:border-gray-800 bg-gray-50 dark:bg-gray-900/50 flex items-center justify-between gap-3"
              >
                <div>
                  <div className="font-semibold text-gray-900 dark:text-gray-100">{daemon.name}</div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">
                    {daemon.description || daemon.summary || 'Daemon monitoring task queues'}
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => daemonToggleMutation.mutate({ name: daemon.name, enabled: !daemon.enabled })}
                    className={`px-3 py-1.5 rounded-lg text-xs font-semibold ${
                      daemon.enabled
                        ? 'bg-emerald-500/20 text-emerald-700'
                        : 'bg-gray-300/40 text-gray-700 dark:bg-gray-800 dark:text-gray-300'
                    }`}
                  >
                    {daemon.enabled ? 'Enabled' : 'Disabled'}
                  </button>
                  <button
                    onClick={() => daemonRunMutation.mutate(daemon.name)}
                    className="px-3 py-1.5 rounded-lg border border-gray-200 dark:border-gray-700 text-xs text-gray-700 dark:text-gray-200"
                  >
                    Trigger
                  </button>
                </div>
              </div>
            ))}
            {!daemons.length && (
              <p className="text-sm text-gray-500 dark:text-gray-400">No daemons detected on this backend.</p>
            )}
          </div>
        </section>

        <section className="bg-white dark:bg-gray-900/70 border border-gray-200 dark:border-gray-800 rounded-2xl p-5 space-y-3">
          <div className="flex items-center gap-3">
            <Cpu className="w-5 h-5 text-primary-500" />
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Driver Scheduling</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400">Admission control + throttles.</p>
            </div>
          </div>
          {driverMetricsQuery.isLoading ? (
            <div className="flex items-center justify-center h-32">
              <div className="h-8 w-8 animate-spin rounded-full border-b-2 border-primary-500" />
            </div>
          ) : driverSnapshot ? (
            <div className="space-y-3 text-sm">
              {driverSnapshot.queues.slice(0, 3).map((queue: DriverQueueMetric) => {
                const sliderValue = driverTargets[queue.driver_id] ?? queue.admission_rate
                return (
                  <div key={queue.driver_id} className="p-3 rounded-xl border border-gray-100 dark:border-gray-800 bg-gray-50 dark:bg-gray-900/40">
                    <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
                      <span className="font-semibold text-gray-900 dark:text-gray-100">{queue.label}</span>
                      <span>Queue {queue.queue_depth}</span>
                    </div>
                    <div className="mt-2 grid grid-cols-2 gap-2 text-xs text-gray-600 dark:text-gray-300">
                      <div>
                        <p>Latency</p>
                        <p className="font-semibold text-gray-900 dark:text-white">{queue.avg_latency_ms} ms</p>
                      </div>
                      <div>
                        <p>Admission</p>
                        <p className="font-semibold text-gray-900 dark:text-white">
                          {(queue.admission_rate * 100).toFixed(0)}%
                        </p>
                      </div>
                    </div>
                    <label className="mt-3 block text-xs text-gray-600 dark:text-gray-300">
                      Target {(sliderValue * 100).toFixed(0)}%
                    </label>
                    <input
                      type="range"
                      min={0.2}
                      max={1}
                      step={0.05}
                      value={sliderValue}
                      onChange={(event) => handleDriverRateChange(queue.driver_id, Number(event.target.value))}
                      className="w-full"
                    />
                    <div className="mt-3 flex gap-2">
                      <button
                        onClick={() => handleDriverApply(queue.driver_id, 'manual')}
                        className="flex-1 rounded-lg border border-gray-200 dark:border-gray-700 px-3 py-1.5 text-xs text-gray-800 dark:text-gray-100"
                        disabled={driverThrottleMutation.isLoading}
                      >
                        Apply Manual
                      </button>
                      <button
                        onClick={() => handleDriverApply(queue.driver_id, 'auto')}
                        className="rounded-lg border border-gray-200 dark:border-gray-700 px-3 py-1.5 text-xs text-gray-800 dark:text-gray-100"
                        disabled={driverThrottleMutation.isLoading}
                      >
                        Auto
                      </button>
                    </div>
                  </div>
                )
              })}
            </div>
          ) : (
            <p className="text-sm text-gray-500 dark:text-gray-400">Driver telemetry unavailable.</p>
          )}
        </section>
      </div>

      <section className="bg-white dark:bg-gray-900/70 border border-gray-200 dark:border-gray-800 rounded-2xl p-5 space-y-4">
        <div className="flex items-center gap-3">
          <Sparkles className="w-5 h-5 text-primary-500" />
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Assistants API + Advanced Tools</h3>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Pair the legacy Tkinter flows with the new shell/code interpreter/assistants bridges.
            </p>
          </div>
        </div>
        <div className="grid md:grid-cols-2 gap-4 text-sm text-gray-700 dark:text-gray-200">
          <div className="p-4 rounded-xl border border-gray-100 dark:border-gray-800 bg-gray-50 dark:bg-gray-900/40">
            <h4 className="font-semibold mb-2">Shell + Code Interpreter CLIs</h4>
            <p>
              Run <code>scripts/ai_shell_runner.py</code> for direct filesystem access or{' '}
              <code>scripts/ai_code_interpreter.py</code> for sandboxed math/data work. These mirror the legacy
              “Tools” tab but lean on OpenAI’s built-in tooling.
            </p>
          </div>
          <div className="p-4 rounded-xl border border-gray-100 dark:border-gray-800 bg-gray-50 dark:bg-gray-900/40">
            <h4 className="font-semibold mb-2">Assistants CLI (Notebook parity)</h4>
            <p>
              Use <code>scripts/assistants_demo.py</code> to recreate the multi-step Assistants notebook locally,
              including Code Interpreter, File Search, and custom function demos. Outputs stream back into this UI
              via shared personas and document operations.
            </p>
          </div>
        </div>
        <div className="p-4 rounded-xl border border-dashed border-primary-200 dark:border-primary-800 bg-primary-50/60 dark:bg-primary-500/10 text-sm text-gray-800 dark:text-gray-100">
          <div className="flex flex-col gap-1 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <h4 className="font-semibold">Assistants CLI Activity</h4>
              <p className="text-xs text-gray-600 dark:text-gray-300">
                Log each <code>python scripts/assistants_demo.py</code> run so the React console mirrors the Tkinter logbook.
                Notes stay in <code>localStorage</code> until cleared.
              </p>
            </div>
            <button
              type="button"
              onClick={handleClearAssistantLog}
              className="mt-2 inline-flex items-center justify-center rounded-lg border border-primary-200 px-3 py-1.5 text-xs font-semibold text-primary-700 hover:bg-primary-100 dark:text-primary-200 dark:border-primary-700 dark:hover:bg-primary-700/30"
            >
              Clear log
            </button>
          </div>
          <form className="mt-4 space-y-3" onSubmit={handleAssistantLog}>
            <label className="block text-xs uppercase text-gray-500 dark:text-gray-300 tracking-[0.3em]">
              Question / command
              <input
                value={assistantQuestion}
                onChange={(e) => setAssistantQuestion(e.target.value)}
                placeholder="Summarize audit findings..."
                className="mt-1 w-full rounded-xl border border-gray-200 dark:border-gray-700 bg-white/50 dark:bg-gray-900/40 px-3 py-2 text-sm text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </label>
            <div>
              <p className="text-xs uppercase text-gray-500 dark:text-gray-300 tracking-[0.3em]">Tools</p>
              <div className="mt-2 flex flex-wrap gap-2">
                {ASSISTANT_TOOL_OPTIONS.map((option) => {
                  const active = assistantTools.includes(option.value)
                  return (
                    <button
                      type="button"
                      key={option.value}
                      onClick={() => toggleAssistantTool(option.value)}
                      className={`rounded-full border px-3 py-1 text-xs font-semibold ${
                        active
                          ? 'border-primary-500 bg-primary-100 text-primary-800 dark:bg-primary-800/50 dark:text-white'
                          : 'border-gray-200 dark:border-gray-700 text-gray-700 dark:text-gray-200'
                      }`}
                      aria-pressed={active}
                    >
                      {option.label}
                    </button>
                  )
                })}
              </div>
            </div>
            <div className="grid gap-3 md:grid-cols-2">
              <label className="text-xs uppercase text-gray-500 dark:text-gray-300 tracking-[0.3em]">
                Run status
                <select
                  value={assistantStatus}
                  onChange={(event) => setAssistantStatus(event.target.value as AssistantStatus)}
                  className="mt-1 w-full rounded-xl border border-gray-200 dark:border-gray-700 bg-white/50 dark:bg-gray-900/40 px-3 py-2 text-sm text-gray-900 dark:text-gray-100"
                >
                  {ASSISTANT_STATUS_OPTIONS.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </label>
              <label className="text-xs uppercase text-gray-500 dark:text-gray-300 tracking-[0.3em]">
                Notes
                <textarea
                  value={assistantNotes}
                  onChange={(event) => setAssistantNotes(event.target.value)}
                  rows={2}
                  placeholder="Key outputs, follow-ups..."
                  className="mt-1 w-full rounded-xl border border-gray-200 dark:border-gray-700 bg-white/50 dark:bg-gray-900/40 px-3 py-2 text-sm text-gray-900 dark:text-gray-100"
                />
              </label>
            </div>
            <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
              <p className="text-xs text-gray-600 dark:text-gray-400">
                Tip: add <code>--dump-json</code> in the CLI to capture assistants output for deeper audits.
              </p>
              <button
                type="submit"
                disabled={assistantLogDisabled}
                className="inline-flex items-center justify-center rounded-xl bg-primary-600 px-4 py-2 text-sm font-semibold text-white hover:bg-primary-700 disabled:opacity-40"
              >
                {assistantLogDisabled ? 'Add details to log' : 'Log Assistants run'}
              </button>
            </div>
          </form>
          <div className="mt-6">
            <h5 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Recent CLI activity</h5>
            <div className="mt-3 space-y-3">
              {assistantHistory.length === 0 && (
                <p className="text-xs text-gray-600 dark:text-gray-400">
                  No entries yet. After you run <code>scripts/assistants_demo.py</code>, jot the highlights here.
                </p>
              )}
              {assistantHistory.map((session) => (
                <div
                  key={session.id}
                  className="rounded-xl border border-gray-100 dark:border-gray-800 bg-white/60 dark:bg-gray-900/40 p-3"
                >
                  <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
                    <span>{new Date(session.timestamp).toLocaleString()}</span>
                    <span
                      className={`rounded-full px-2 py-0.5 text-[0.65rem] font-semibold uppercase tracking-wide ${
                        session.status === 'completed'
                          ? 'bg-emerald-500/15 text-emerald-700'
                          : session.status === 'running'
                          ? 'bg-amber-500/15 text-amber-700'
                          : 'bg-rose-500/15 text-rose-700'
                      }`}
                    >
                      {session.status}
                    </span>
                  </div>
                  <p className="mt-2 text-sm font-semibold text-gray-900 dark:text-gray-100">{session.question}</p>
                  {session.notes && <p className="mt-1 text-xs text-gray-600 dark:text-gray-300">{session.notes}</p>}
                  <div className="mt-2 flex flex-wrap gap-1">
                    {session.tools.map((tool) => (
                      <span
                        key={`${session.id}-${tool}`}
                        className="rounded-full bg-gray-200/70 dark:bg-gray-800 px-2 py-0.5 text-[0.65rem] uppercase tracking-wide text-gray-700 dark:text-gray-200"
                      >
                        {ASSISTANT_TOOL_LABELS[tool]}
                      </span>
                    ))}
                  </div>
                  <div className="mt-2 grid grid-cols-2 gap-2 text-[0.65rem] text-gray-500 dark:text-gray-400">
                    <span>
                      Run: <code className="text-[0.6rem]">{session.run_id}</code>
                    </span>
                    <span className="text-right">
                      Thread: <code className="text-[0.6rem]">{session.thread_id}</code>
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}
