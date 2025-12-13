import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import {
  Activity,
  AlertCircle,
  ArrowUpRight,
  CheckCircle,
  Cpu,
  FileText,
  Server,
  Shield,
  TrendingUp,
  LayoutDashboard,
} from 'lucide-react'
import type { LucideIcon } from 'lucide-react'
import { API } from '../api'
import apiClient, { apiPath } from '../lib/apiClient'
import { extractArray } from '../lib/responseHelpers'
import { useState } from 'react'
import type {
  BillingUsage,
  DashboardStats as DashboardStatsType,
  PersonasResponse,
  PersonaInfo,
} from '../types'
import { toast } from '../utils/toast'
import PageHeader from '../components/PageHeader'

const PERSONA_ROLES: Record<string, string> = {
  Chris: 'Human Owner · executive decisions',
  AIC: 'Auditor · validates outputs',
  Aria: 'Assistant · executes the day-to-day',
  Sora: 'Archive · protects lineage + memory',
}

const PERSONA_COLORS: Record<string, string> = {
  Chris: 'from-rose-500/30 via-transparent to-orange-500/20',
  AIC: 'from-indigo-500/30 via-transparent to-blue-500/20',
  Aria: 'from-emerald-500/30 via-transparent to-teal-500/20',
  Sora: 'from-cyan-500/30 via-transparent to-sky-500/20',
}

const PERSONA_ORDER = Object.keys(PERSONA_ROLES)
const DEFAULT_PERSONA_DEFINITIONS: PersonaInfo[] = PERSONA_ORDER.map((name) => ({
  name,
  role: PERSONA_ROLES[name] || 'Persona',
}))

interface ControlData {
  system: any
  planes: any
  daemons: any[]
  operations: any[]
  billing: BillingUsage | null
}

const DASHBOARD_REQUEST_TIMEOUT_MS = 4500

const buildOfflineDashboardSnapshot = (message?: string): DashboardStatsType => ({
  total_tasks: 0,
  tasks_by_status: {},
  tasks_by_priority: {},
  total_projects: 0,
  active_projects: 0,
  system_stats: {
    cpu_percent: 0,
    memory_percent: 0,
    disk_percent: 0,
  },
  security_status: {
    status: 'offline',
    message: message ?? 'Backend not available. Please ensure the backend server is running on port 8000.',
    updated_at: new Date().toISOString(),
    source: 'local',
  },
  persona_load: {},
  active_persona: 'AIC',
})

const buildDashboardSnapshotFromLegacy = async (): Promise<DashboardStatsType> => {
  const [tasks, projects, system] = await Promise.all([
    apiClient
      .get(apiPath('tasks'))
      .then((res) => extractArray(res.data, ['tasks', 'items']))
      .catch(() => []),
    apiClient
      .get(apiPath('projects'))
      .then((res) => extractArray(res.data, ['projects', 'items']))
      .catch(() => []),
    API.system().catch(() => ({
      cpu_percent: 0,
      memory: { used: 0, total: 1 },
      disk: { used: 0, total: 1 },
    })),
  ])

  const tasksByStatus = tasks.reduce((acc: Record<string, number>, task: any) => {
    acc[task.status] = (acc[task.status] || 0) + 1
    return acc
  }, {})

  const tasksByPriority = tasks.reduce((acc: Record<string, number>, task: any) => {
    acc[task.priority] = (acc[task.priority] || 0) + 1
    return acc
  }, {})
  const personaLoad = tasks.reduce((acc: Record<string, number>, task: any) => {
    const owner = task.owner || 'AIC'
    acc[owner] = (acc[owner] || 0) + 1
    return acc
  }, {} as Record<string, number>)

  const memory = (system as any)?.memory || {}
  const disk = (system as any)?.disk || {}
  const memoryPercent = memory.total ? Math.round((memory.used / memory.total) * 100) : 0
  const diskPercent = disk.total ? Math.round((disk.used / disk.total) * 100) : 0

  return {
    total_tasks: tasks.length,
    tasks_by_status: tasksByStatus,
    tasks_by_priority: tasksByPriority,
    total_projects: projects.length,
    active_projects: projects.filter((project: any) => project.status === 'active').length,
    system_stats: {
      cpu_percent: (system as any)?.cpu_percent || 0,
      memory_percent: memoryPercent,
      disk_percent: diskPercent,
    },
    security_status: {
      status: 'offline',
      message: 'Security monitoring not available',
      updated_at: new Date().toISOString(),
      source: 'local',
    },
    persona_load: personaLoad,
    active_persona: 'AIC',
  }
}

const fetchDashboardStats = async (): Promise<DashboardStatsType> => {
  const controller = typeof AbortController !== 'undefined' ? new AbortController() : undefined
  let abortTimer: ReturnType<typeof setTimeout> | undefined
  if (controller) {
    abortTimer = setTimeout(() => controller.abort(), DASHBOARD_REQUEST_TIMEOUT_MS)
  }

  try {
    const response = await apiClient.get(apiPath('dashboard/stats'), {
      signal: controller?.signal,
      timeout: DASHBOARD_REQUEST_TIMEOUT_MS + 2500,
    })
    if (response.data) {
      return response.data
    }
  } catch (error) {
    const code = (error as { code?: string })?.code
    if (code !== 'ERR_CANCELED') {
      console.warn('dashboard/stats endpoint unavailable, using derived snapshot instead.', error)
    }
  } finally {
    if (abortTimer) {
      clearTimeout(abortTimer)
    }
  }

  try {
    return await buildDashboardSnapshotFromLegacy()
  } catch (error) {
    console.error('Failed to compute fallback dashboard stats', error)
    return buildOfflineDashboardSnapshot()
  }
}

const fetchPersonas = async (): Promise<PersonasResponse> => {
  const { data } = await apiClient.get<PersonasResponse>(apiPath('personas'))
  return data
}

const updateActivePersona = async (persona: string): Promise<PersonasResponse> => {
  const { data } = await apiClient.post<PersonasResponse>(apiPath('personas'), { persona })
  return data
}

const coerceList = <T = any>(payload: unknown, key?: string): T[] => {
  if (Array.isArray(payload)) {
    return payload as T[]
  }
  if (key && payload && typeof payload === 'object') {
    const container = payload as Record<string, unknown>
    if (Array.isArray(container[key])) {
      return container[key] as T[]
    }
  }
  return []
}

const fetchControlData = async (): Promise<ControlData> => {
  try {
    const [system, planes, daemonsPayload, operationsPayload, billingPayload] = await Promise.all([
      API.system().catch(() => ({
        cpu_percent: 0,
        memory: { used: 0, total: 1 },
        disk: { used: 0, total: 1 },
      })),
      API.planes().catch(() => ({})),
      API.daemons().catch(() => []),
      API.operations().catch(() => []),
      API.billing().catch(() => ({ estimated_cost: 0, currency: 'USD', records: [] })),
    ])
    return {
      system,
      planes,
      daemons: coerceList(daemonsPayload, 'daemons'),
      operations: coerceList(operationsPayload, 'operations'),
      billing:
        billingPayload && typeof billingPayload === 'object'
          ? (billingPayload as BillingUsage)
          : { estimated_cost: 0, currency: 'USD', records: [] },
    }
  } catch (error) {
    return {
      system: {},
      planes: {},
      daemons: [],
      operations: [],
      billing: { estimated_cost: 0, currency: 'USD', records: [] },
    }
  }
}

export default function Dashboard() {
  const queryClient = useQueryClient()
  const { data, isLoading, error } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: fetchDashboardStats,
    refetchInterval: 30000,
  })
  const { data: controlData } = useQuery({
    queryKey: ['dashboard-control'],
    queryFn: fetchControlData,
    refetchInterval: 30000,
  })
  const personaQuery = useQuery({
    queryKey: ['personas'],
    queryFn: fetchPersonas,
    refetchInterval: 60000,
  })
  const personaMutation = useMutation({
    mutationFn: (persona: string) => updateActivePersona(persona),
    onSuccess: (payload) => {
      toast.success(`Switched to ${payload.active}`)
      queryClient.invalidateQueries({ queryKey: ['dashboard-stats'] })
      queryClient.invalidateQueries({ queryKey: ['personas'] })
    },
    onError: (mutationError) => {
      const message = mutationError instanceof Error ? mutationError.message : 'Unable to switch persona.'
      toast.error(message)
    },
  })

  const [searchTerm, setSearchTerm] = useState('')
  const [searchResults, setSearchResults] = useState<any[]>([])
  const [searchPending, setSearchPending] = useState(false)
  const [searchError, setSearchError] = useState<string | null>(null)
  const [assistantInput, setAssistantInput] = useState('')
  const [assistantReply, setAssistantReply] = useState<string>('')
  const [assistantPending, setAssistantPending] = useState(false)
  const [auditDetail, setAuditDetail] = useState<string>('Select an operation to view details.')

  if (isLoading) {
    return (
      <div className="px-4 py-6 sm:px-0">
        <div className="glass-card flex flex-col h-72 items-center justify-center text-slate-300 gap-4">
          <div className="h-12 w-12 animate-spin rounded-full border-2 border-white/30 border-t-white" />
          <p className="text-sm text-slate-400">Loading dashboard data...</p>
        </div>
      </div>
    )
  }

  if (error || !data) {
    return (
      <div className="px-4 py-6 sm:px-0">
        <div className="glass-card border-l-4 border-amber-400/60 text-sm text-slate-100 p-6">
          <div className="flex items-center gap-3 text-base font-semibold mb-3">
            <AlertCircle className="h-5 w-5 text-amber-300 flex-shrink-0" />
            <span>Backend Connection Issue</span>
          </div>
          <p className="mt-2 text-slate-300 mb-4">
            {error instanceof Error ? error.message : 'Unable to connect to backend server.'}
          </p>
          <div className="space-y-2 text-slate-300">
            <p className="text-xs uppercase tracking-wider text-slate-400 mb-2">Troubleshooting Steps:</p>
            <ol className="space-y-2 list-decimal list-inside">
              <li className="pl-2">Run <code className="rounded bg-black/30 px-2 py-1 text-xs font-mono">uvicorn backend_api.main:app --reload</code></li>
              <li className="pl-2">Verify FastAPI is reachable on <code className="rounded bg-black/30 px-2 py-1 text-xs font-mono">http://127.0.0.1:8000</code></li>
              <li className="pl-2">Refresh this page — it polls every 30 seconds.</li>
            </ol>
          </div>
          <button
            onClick={() => window.location.reload()}
            className="mt-4 px-4 py-2 bg-primary-500/20 hover:bg-primary-500/30 border border-primary-500/50 rounded-xl text-sm text-primary-300 transition-colors"
          >
            Retry Connection
          </button>
        </div>
      </div>
    )
  }

  const totalTasks = data.total_tasks || 0
  const personaLoad = data.persona_load || {}
  const fallbackActivePersona = data.active_persona || 'AIC'
  const personaDefinitions = personaQuery.data?.personas ?? DEFAULT_PERSONA_DEFINITIONS
  const activePersona = personaQuery.data?.active || fallbackActivePersona
  const personaError =
    personaQuery.error instanceof Error ? personaQuery.error.message : personaQuery.error ? 'Unable to load personas.' : null
  const handlePersonaChange = (nextPersona: string) => {
    if (!nextPersona || nextPersona === activePersona) {
      return
    }
    personaMutation.mutate(nextPersona)
  }
  const statusEntries = Object.entries(data.tasks_by_status || {})
  const priorityEntries = Object.entries(data.tasks_by_priority || {})
  const statCards: DashboardStat[] = [
    {
      title: 'Total Tasks',
      value: data.total_tasks,
      detail: `${Object.keys(data.tasks_by_status || {}).length || 0} states tracked`,
      icon: CheckCircle,
      accent: 'from-sky-500/20 via-transparent to-blue-500/10',
    },
    {
      title: 'Active Projects',
      value: data.active_projects,
      detail: `${data.total_projects} total`,
      icon: Activity,
      accent: 'from-emerald-400/20 via-transparent to-teal-500/10',
    },
    {
      title: 'Todo Backlog',
      value: data.tasks_by_status?.TODO || 0,
      detail: 'Awaiting action',
      icon: TrendingUp,
      accent: 'from-amber-400/25 via-transparent to-orange-500/5',
    },
    {
      title: 'CPU Usage',
      value: `${Math.round(data.system_stats.cpu_percent)}%`,
      detail: 'System load',
      icon: Cpu,
      accent: 'from-indigo-500/20 via-transparent to-purple-500/10',
    },
  ]

  const healthMetrics = [
    {
      label: 'CPU Load',
      value: Math.round(data.system_stats.cpu_percent),
      suffix: '%',
      icon: Cpu,
    },
    {
      label: 'Memory',
      value: Math.round(data.system_stats.memory_percent),
      suffix: '%',
      icon: Activity,
    },
    {
      label: 'Storage',
      value: Math.round(data.system_stats.disk_percent),
      suffix: '%',
      icon: Server,
    },
  ]

  const securityTone = data.security_status.status?.toLowerCase() || ''
  const securityAccent =
    securityTone.includes('offline') || securityTone.includes('error')
      ? 'border-red-400/70'
      : securityTone.includes('warn') || securityTone.includes('degraded')
      ? 'border-amber-400/70'
      : 'border-emerald-400/70'

  const preservedLinks = [
    { to: '/docs/dashboard', label: 'Legacy Dashboard HTML', description: 'Compare with Tkinter layout' },
    { to: '/docs/projects', label: 'Projects Workspace', description: 'Original doc set' },
    { to: '/docs/billing', label: 'Billing Console', description: 'Finance overview' },
  ]

  const daemons = controlData?.daemons ?? []
  const operations = controlData?.operations ?? []
  const billingUsage = controlData?.billing
  const disabledDaemon = daemons.find((daemon: any) => !daemon.enabled)
  const summaryTiles = [
    {
      title: 'Daemons',
      value: `${daemons.filter((d: any) => d.enabled).length}/${daemons.length}`,
      desc: 'Active automations',
    },
    {
      title: 'Search Hits',
      value: searchResults.length,
      desc: searchResults.length ? 'Latest query results' : 'Run a query below',
    },
    {
      title: 'Recent Ops',
      value: operations.length,
      desc: 'Past 24h',
    },
    {
      title: 'Needs attention',
      value: disabledDaemon?.name || 'All covered',
      desc: disabledDaemon ? 'Daemon paused' : 'No pending alerts',
    },
  ]

  const handleSearch = async () => {
    if (!searchTerm.trim()) return
    setSearchPending(true)
    setSearchError(null)
    try {
      const response = await apiClient.get(apiPath('search'), {
        params: { q: searchTerm.trim() },
      })
      const payload = response.data
      const results = Array.isArray(payload?.results) ? payload.results : Array.isArray(payload) ? payload : []
      setSearchResults(results)
    } catch (err) {
      setSearchError('Search failed. Ensure FastAPI is running.')
      setSearchResults([])
    } finally {
      setSearchPending(false)
      queryClient.invalidateQueries({ queryKey: ['dashboard-control'] })
    }
  }

  const handleAssistantSend = async () => {
    if (!assistantInput.trim()) return
    setAssistantPending(true)
    try {
      const response = await apiClient.post(apiPath('ai/ask'), { prompt: assistantInput.trim() })
      const payload = response.data || response
      setAssistantReply(payload.response || 'No response provided.')
    } catch (err) {
      setAssistantReply('Assistant unavailable. Check backend services.')
    } finally {
      setAssistantPending(false)
    }
  }

  const handleToggleDaemon = async (daemon: any) => {
    try {
      await API.toggleDaemon(daemon.name, !daemon.enabled)
      queryClient.invalidateQueries({ queryKey: ['dashboard-control'] })
    } catch (err) {
      // no-op, toast could be added later
    }
  }

  const handleRunDaemon = async (daemon: any) => {
    try {
      await API.runDaemon(daemon.name)
      queryClient.invalidateQueries({ queryKey: ['dashboard-control'] })
    } catch (err) {
      // silent fail
    }
  }

  const handleSelectOperation = async (operation: any) => {
    setAuditDetail('Loading audit detail...')
    try {
      const response = await apiClient.get(apiPath(`audit/${operation.id}`))
      const payload = response.data || response
      setAuditDetail(JSON.stringify(payload, null, 2))
    } catch (err) {
      setAuditDetail('Failed to load audit detail. Ensure backend is running.')
    }
  }

  return (
    <div className="space-y-8 text-slate-100">
      <PageHeader
        eyebrow="Command Center"
        title="Operational Dashboard"
        description="Shared React + Electron surface backed by the same FastAPI routes that powered the Tkinter GUI. Monitor tasks, projects, and telemetry without duplicating code."
        icon={LayoutDashboard}
        actions={
          <>
            <span className="pill-muted px-3 py-1.5">Projects · {data.active_projects}/{data.total_projects}</span>
            <span className="pill-muted px-3 py-1.5">Tasks · {totalTasks}</span>
            <Link className="btn-secondary" to="/docs/dashboard">
              <FileText className="h-4 w-4" />
              View Docs
            </Link>
          </>
        }
      />

      <div className="content-grid grid-cols-2 xl:grid-cols-4">
        {statCards.map((card) => (
          <DashboardStatCard
            key={card.title}
            title={card.title}
            value={card.value}
            detail={card.detail}
            icon={card.icon}
            accent={card.accent}
          />
        ))}
      </div>

      <section className="content-grid grid-cols-2 xl:grid-cols-4">
        {summaryTiles.map((tile) => (
          <div key={tile.title} className="glass-card">
            <p className="eyebrow-text">{tile.title}</p>
            <p className="mt-2 text-2xl font-semibold text-white">{tile.value}</p>
            <p className="text-sm text-slate-300">{tile.desc}</p>
          </div>
        ))}
        {billingUsage && (
          <div className="glass-card border border-white/10">
            <p className="eyebrow-text">Billing Snapshot</p>
            <p className="mt-2 text-2xl font-semibold text-white">
              ${billingUsage.estimated_cost.toFixed(2)} <span className="text-sm">{billingUsage.currency}</span>
            </p>
            <p className="text-sm text-slate-300">See more under Billing.</p>
          </div>
        )}
      </section>

      <div className="grid gap-6 xl:grid-cols-[2fr,1fr]">
        <div className="space-y-6">
          <section className="glass-card space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="eyebrow-text">Work Pulse</p>
                <h3 className="text-xl font-semibold text-white">Tasks & Priorities</h3>
              </div>
              <span className="pill-muted">Auto refresh · 30s</span>
            </div>
            <div className="grid gap-6 md:grid-cols-2">
              <ProgressGroup label="Status" entries={statusEntries} total={totalTasks} />
              <ProgressGroup label="Priority" entries={priorityEntries} total={totalTasks} />
            </div>
          </section>
          <PersonaLoadSection
            personaLoad={personaLoad}
            activePersona={activePersona}
            personas={personaDefinitions}
            onPersonaChange={handlePersonaChange}
            isUpdatingPersona={personaMutation.isPending}
            personaError={personaError}
          />
        </div>

        <div className="space-y-6">
          <section className="glass-card space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-white">System Health</h3>
              <span className="pill-muted">Shared backend</span>
            </div>
            <div className="space-y-3">
              {healthMetrics.map((metric) => (
                <HealthMetricCard
                  key={metric.label}
                  label={metric.label}
                  value={metric.value}
                  suffix={metric.suffix}
                  icon={metric.icon}
                />
              ))}
            </div>
          </section>
          <section className={`glass-card border-l-4 ${securityAccent} space-y-3`}>
            <div className="flex items-center gap-3">
              <Shield className="h-5 w-5 text-slate-200" />
              <div>
                <p className="text-xs uppercase tracking-[0.3em] text-slate-400">Security</p>
                <p className="text-lg font-semibold text-white">{data.security_status.status}</p>
              </div>
            </div>
            <p className="text-sm text-slate-300">{data.security_status.message}</p>
            <p className="text-xs text-slate-400">
              Last updated {new Date(data.security_status.updated_at).toLocaleString()} · Source:{' '}
              {data.security_status.source}
            </p>
          </section>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <section className="glass-card space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="eyebrow-text">Projects</p>
              <h3 className="text-xl font-semibold text-white">Project Pulse</h3>
              <p className="text-sm text-slate-300">Active initiatives across both desktop and browser clients.</p>
            </div>
            <Link className="btn-tonal text-xs" to="/projects">
              <ArrowUpRight className="h-4 w-4" />
              Open Projects
            </Link>
          </div>
          <div className="rounded-2xl border border-white/10 bg-white/5 p-5">
            <p className="text-xs uppercase tracking-[0.3em] text-slate-400">Active vs Total</p>
            <p className="mt-2 text-4xl font-semibold text-white">
              {data.active_projects}/{data.total_projects || 1}
            </p>
            <div className="mt-4 h-2 rounded-full bg-white/10">
              <div
                className="h-full rounded-full bg-gradient-to-r from-blue-500 to-indigo-500"
                style={{
                  width: `${percentage(data.active_projects, data.total_projects || 1)}%`,
                }}
              />
            </div>
          </div>
        </section>
        <section className="glass-card space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="eyebrow-text">Preserved Pages</p>
              <h3 className="text-xl font-semibold text-white">Tkinter HTML Reference</h3>
              <p className="text-sm text-slate-300">
                Validate the migration by hopping into the original HTML. React simply skins the same data.
              </p>
            </div>
            <Link className="btn-tonal text-xs" to="/docs">
              Browse Docs
            </Link>
          </div>
          <div className="space-y-3">
            {preservedLinks.map((link) => (
              <DocLink key={link.to} to={link.to} label={link.label} description={link.description} />
            ))}
          </div>
        </section>
      </div>

      <section className="grid gap-6 lg:grid-cols-2">
        <div className="glass-card space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="eyebrow-text">Quick AI Assistant</p>
              <h3 className="text-xl font-semibold text-white">Ask the Copilot</h3>
            </div>
            <button
              className="btn-tonal text-xs"
              onClick={() => {
                setAssistantInput('')
                setAssistantReply('')
              }}
            >
              Clear
            </button>
          </div>
          <textarea
            value={assistantInput}
            onChange={(e) => setAssistantInput(e.target.value)}
            rows={4}
            placeholder="Ask about tasks, incidents, or plans"
            className="w-full rounded-2xl border border-white/10 bg-white/5 p-3 text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500/50 transition-all"
            onKeyDown={(e) => {
              if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
                e.preventDefault()
                handleAssistantSend()
              }
            }}
          />
          <button
            className="btn-tonal disabled:opacity-50 disabled:cursor-not-allowed"
            onClick={handleAssistantSend}
            disabled={assistantPending || !assistantInput.trim()}
          >
            {assistantPending ? (
              <>
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin mr-2" />
                Sending…
              </>
            ) : (
              'Send (⌘+Enter)'
            )}
          </button>
          <div className="rounded-2xl border border-white/10 bg-white/5 p-3 text-sm text-slate-200 min-h-[60px] max-h-48 overflow-y-auto">
            {assistantReply || (
              <span className="text-slate-500 italic">Response will appear here...</span>
            )}
          </div>
        </div>
        <div className="glass-card space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="eyebrow-text">Planes</p>
              <h3 className="text-xl font-semibold text-white">Plane Status</h3>
            </div>
            <span className="pill-muted">/planes/status</span>
          </div>
          <div className="space-y-3 text-sm text-slate-300">
            <PlaneRow label="Data Plane" value={(controlData?.planes?.data_plane?.collections || []).join(', ') || '—'} />
            <PlaneRow
              label="Control Plane"
              value={`${controlData?.planes?.control_plane?.middlewares || 0} middleware(s)`}
            />
            <PlaneRow
              label="Governance"
              value={controlData?.planes?.governance_plane?.policy || 'Unknown'}
            />
          </div>
        </div>
      </section>

      <section className="grid gap-6 lg:grid-cols-2">
        <div className="glass-card space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="eyebrow-text">Unified Search</p>
              <h3 className="text-xl font-semibold text-white">Search everything</h3>
            </div>
          </div>
          <div className="flex gap-3">
            <input
              className="flex-1 rounded-2xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500/50 transition-all"
              placeholder="Search notes, PDFs, etc."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !searchPending && searchTerm.trim()) {
                  handleSearch()
                }
              }}
            />
            <button 
              className="btn-tonal disabled:opacity-50 disabled:cursor-not-allowed" 
              onClick={handleSearch} 
              disabled={searchPending || !searchTerm.trim()}
            >
              {searchPending ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin mr-2" />
                  Searching…
                </>
              ) : (
                'Search'
              )}
            </button>
          </div>
          {searchError && <p className="text-sm text-amber-300">{searchError}</p>}
          <div className="space-y-3 max-h-72 overflow-y-auto">
            {searchResults.map((result, index) => (
              <div key={`${result.id || index}`} className="rounded-2xl border border-white/10 bg-white/5 p-3 text-sm">
                <p className="font-semibold text-white">{result.node_title || result.title || 'Untitled result'}</p>
                <p className="text-slate-300 text-xs">{result.text_snippet || result.snippet || ''}</p>
              </div>
            ))}
            {!searchPending && !searchResults.length && <p className="text-sm text-slate-400">No results yet.</p>}
          </div>
        </div>
        <div className="glass-card space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="eyebrow-text">Daemons</p>
              <h3 className="text-xl font-semibold text-white">Daemon Control</h3>
            </div>
          </div>
          <div className="space-y-3 max-h-72 overflow-y-auto">
            {daemons.map((daemon: any) => (
              <div key={daemon.name} className="rounded-2xl border border-white/10 bg-white/5 p-3 text-sm text-white">
                <div className="flex items-center justify-between">
                  <p className="font-semibold">{daemon.name}</p>
                  <span className="text-xs text-slate-300">{daemon.risk_level || 'normal'}</span>
                </div>
                <p className="mt-1 text-xs text-slate-300">{daemon.description}</p>
                <div className="mt-3 flex gap-2">
                  <button className="btn-tonal text-xs" onClick={() => handleToggleDaemon(daemon)}>
                    {daemon.enabled ? 'Disable' : 'Enable'}
                  </button>
                  <button className="btn-tonal text-xs" onClick={() => handleRunDaemon(daemon)}>
                    Run now
                  </button>
                </div>
              </div>
            ))}
            {!daemons.length && <p className="text-sm text-slate-400">No daemons discovered.</p>}
          </div>
        </div>
      </section>

      <section className="grid gap-6 lg:grid-cols-2">
        <div className="glass-card space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="eyebrow-text">Activity Timeline</p>
              <h3 className="text-xl font-semibold text-white">Recent Operations</h3>
            </div>
            <button className="btn-tonal text-xs" onClick={() => queryClient.invalidateQueries({ queryKey: ['dashboard-control'] })}>
              Refresh
            </button>
          </div>
          <div className="space-y-3 max-h-72 overflow-y-auto">
            {operations.map((operation: any) => (
              <button
                key={operation.id}
                className="w-full rounded-2xl border border-white/10 bg-white/5 p-3 text-left text-sm text-white hover:border-white/30"
                onClick={() => handleSelectOperation(operation)}
              >
                <p className="font-semibold">{operation.intent || operation.title || `Operation #${operation.id}`}</p>
                <p className="text-xs text-slate-300">{new Date(operation.started_at).toLocaleString()}</p>
              </button>
            ))}
            {!operations.length && <p className="text-sm text-slate-400">No operations yet.</p>}
          </div>
        </div>
        <div className="glass-card space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="eyebrow-text">Audit Detail</p>
              <h3 className="text-xl font-semibold text-white">Evidence pane</h3>
            </div>
          </div>
          <pre className="max-h-72 overflow-y-auto rounded-2xl border border-white/10 bg-black/30 p-3 text-xs text-slate-200">
            {auditDetail}
          </pre>
        </div>
      </section>
    </div>
  )
}

interface DashboardStat {
  title: string
  value: number | string
  detail: string
  icon: LucideIcon
  accent: string
}

function DashboardStatCard({ title, value, detail, icon: Icon, accent }: DashboardStat) {
  return (
    <div className="glass-card relative overflow-hidden">
      <div className={`pointer-events-none absolute inset-0 bg-gradient-to-br ${accent}`} />
      <div className="relative flex items-start justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.3em] text-slate-400">{title}</p>
          <p className="mt-2 text-3xl font-semibold text-white">{value}</p>
          <p className="text-sm text-slate-300">{detail}</p>
        </div>
        <div className="rounded-2xl border border-white/10 bg-white/5 p-3 text-white">
          <Icon className="h-5 w-5" />
        </div>
      </div>
    </div>
  )
}

function PersonaLoadSection({
  personaLoad,
  activePersona,
  personas,
  onPersonaChange,
  isUpdatingPersona,
  personaError,
}: {
  personaLoad: Record<string, number>
  activePersona?: string
  personas: PersonaInfo[]
  onPersonaChange?: (persona: string) => void
  isUpdatingPersona?: boolean
  personaError?: string | null
}) {
  const personaOrder = personas.length ? personas : DEFAULT_PERSONA_DEFINITIONS
  const personaRoleMap = personaOrder.reduce<Record<string, string>>((acc, entry) => {
    acc[entry.name] = entry.role || PERSONA_ROLES[entry.name] || 'Persona'
    return acc
  }, { ...PERSONA_ROLES })
  const baseNames = personaOrder.map((entry) => entry.name)
  const additionalNames = Object.keys(personaLoad).filter((name) => !baseNames.includes(name))
  const personasToDisplay = [...baseNames, ...additionalNames]
  const total = personasToDisplay.reduce((sum, persona) => sum + (personaLoad[persona] || 0), 0)

  return (
    <section className="glass-card space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <p className="eyebrow-text">Persona Focus</p>
          <h3 className="text-xl font-semibold text-white">Load by Persona</h3>
          <p className="text-sm text-slate-300">
            Mirrors the Tkinter dashboard chip showing how many incomplete tasks each persona owns.
          </p>
        </div>
        <div className="flex flex-col items-end gap-2 text-xs text-slate-300">
          <label className="flex flex-col gap-1 text-right">
            Active Persona
            <select
              value={activePersona || ''}
              onChange={(event) => onPersonaChange?.(event.target.value)}
              disabled={isUpdatingPersona}
              className="rounded-xl border border-white/10 bg-white/5 px-3 py-1 text-sm text-white focus:border-white/40 focus:outline-none"
            >
              {personasToDisplay.map((persona) => (
                <option key={persona} value={persona}>
                  {persona}
                </option>
              ))}
            </select>
          </label>
          {isUpdatingPersona && <span className="text-[0.65rem] uppercase tracking-[0.3em] text-slate-400">Switching…</span>}
        </div>
      </div>
      {personaError && (
        <p className="rounded-2xl border border-amber-400/40 bg-amber-500/10 px-4 py-2 text-xs text-amber-100">
          Persona directory unavailable: {personaError}
        </p>
      )}
      {total === 0 && (
        <p className="rounded-2xl border border-dashed border-white/10 px-4 py-3 text-sm text-slate-400">
          No active tasks yet — once Capsules assign work, persona load shows up here.
        </p>
      )}
      <div className="space-y-3">
        {personasToDisplay.map((persona) => {
          const count = personaLoad[persona] || 0
          const percent = total ? Math.round((count / total) * 100) : 0
          const isActive = persona === activePersona
          const gradient =
            PERSONA_COLORS[persona] || 'from-slate-500/25 via-transparent to-slate-700/10'
          return (
            <div
              key={persona}
              className={`rounded-2xl border border-white/10 bg-white/5 p-4 text-sm text-white transition ${
                isActive ? 'ring-1 ring-[color:var(--osd-accent)]' : ''
              }`}
            >
              <div className="flex items-center justify-between gap-3">
              <div>
                <p className="text-base font-semibold">{persona}</p>
                <p className="text-xs text-slate-300">{personaRoleMap[persona] || 'Persona'}</p>
              </div>
              <span className="rounded-full border border-white/10 bg-white/10 px-3 py-1 text-xs">
                {count} open
              </span>
            </div>
              <div className="mt-3 h-2 rounded-full bg-white/10">
                <div
                  className={`h-full rounded-full bg-gradient-to-r ${gradient}`}
                  style={{ width: `${percent}%` }}
                />
              </div>
              <p className="mt-2 text-xs text-slate-300">{percent}% of incomplete tasks</p>
            </div>
          )
        })}
      </div>
    </section>
  )
}

function ProgressGroup({
  label,
  entries,
  total,
}: {
  label: string
  entries: [string, number][]
  total: number
}) {
  if (!entries.length) {
    return (
      <div>
        <p className="text-sm font-semibold text-white">{label}</p>
        <p className="text-sm text-slate-400">No data yet.</p>
      </div>
    )
  }

  return (
      <div className="space-y-3">
      <p className="text-sm font-semibold text-white">{label}</p>
      {entries.map(([name, count]) => (
        <div key={name}>
          <div className="flex items-center justify-between text-xs uppercase tracking-[0.2em] text-slate-400">
            <span>{name}</span>
            <span>{count}</span>
          </div>
          <div className="mt-2 h-2 rounded-full bg-white/10">
            <div
              className="h-full rounded-full bg-gradient-to-r from-blue-500 to-indigo-500"
              style={{ width: `${percentage(count, total)}%` }}
            />
          </div>
        </div>
      ))}
    </div>
  )
}

function HealthMetricCard({
  label,
  value,
  suffix,
  icon: Icon,
}: {
  label: string
  value: number
  suffix?: string
  icon: LucideIcon
}) {
  return (
    <div className="flex items-center gap-3 rounded-2xl border border-white/10 bg-white/5 p-3">
      <div className="rounded-2xl border border-white/10 bg-white/5 p-3">
        <Icon className="h-4 w-4 text-white" />
      </div>
      <div>
        <p className="text-xs uppercase tracking-[0.3em] text-slate-400">{label}</p>
        <p className="text-2xl font-semibold text-white">
          {value}
          {suffix}
        </p>
      </div>
    </div>
  )
}

function DocLink({ to, label, description }: { to: string; label: string; description: string }) {
  return (
    <Link
      to={to}
      className="flex items-center justify-between rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white transition hover:border-white/30 hover:bg-white/10"
    >
      <div>
        <p className="font-semibold">{label}</p>
        <p className="text-xs text-slate-300">{description}</p>
      </div>
      <ArrowUpRight className="h-4 w-4 text-slate-300" />
    </Link>
  )
}

function percentage(value: number, total: number): number {
  if (!total) return 0
  return Math.min(100, Math.round((value / total) * 100))
}

function PlaneRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex flex-col rounded-2xl border border-white/10 bg-white/5 p-3 text-sm text-slate-200">
      <p className="text-xs uppercase tracking-[0.3em] text-slate-400">{label}</p>
      <p className="mt-1 text-white">{value}</p>
    </div>
  )
}
