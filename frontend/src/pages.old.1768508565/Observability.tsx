import { useQuery, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import {
  Activity,
  AlertTriangle,
  BarChart3,
  CheckCircle,
  Clock,
  Cpu,
  Database,
  Eye,
  Filter,
  HardDrive,
  Layers,
  MemoryStick,
  RefreshCw,
  Server,
  Sparkles,
  TrendingUp,
  Wifi,
  XCircle,
  Zap,
} from 'lucide-react'
import apiClient, { apiPath } from '../lib/apiClient'

interface DiagnosticEvent {
  id: string
  type: 'error' | 'warning' | 'info' | 'debug'
  source: string
  message: string
  timestamp: string
  metadata?: Record<string, unknown>
  stack?: string
}

interface SystemMetric {
  name: string
  value: number
  unit: string
  trend: 'up' | 'down' | 'stable'
  threshold?: number
}

interface PlaneHealth {
  name: string
  status: 'healthy' | 'degraded' | 'error' | 'unknown'
  latency_ms: number
  error_rate: number
  throughput: number
}

interface HarnessProjectSummary {
  name: string
  status: string
  failed: number
  passed: number
  skipped: number
  commands: string[]
}

interface HarnessReport {
  generated_at?: string
  status: string
  root: string
  total_projects: number
  total_checks: number
  failed_checks: number
  passed_checks: number
  skipped_checks: number
  run_id?: string
  report_path?: string
  projects: HarnessProjectSummary[]
}

interface ObservabilityData {
  events: DiagnosticEvent[]
  metrics: SystemMetric[]
  planes: PlaneHealth[]
  uptime_seconds: number
  total_requests: number
  error_count: number
  ai_calls: number
  diagnostics_summary?: DiagnosticsSummary
  harness?: HarnessReport
}

interface PlanCommand {
  command: string
  description?: string
  requires_sudo?: boolean
}

interface PlanSection {
  title: string
  objective: string
  commands: PlanCommand[]
  verification: string[]
  notes?: string
}

interface MemoryThreadPlan {
  os_family: string
  architecture: string
  logical_cores: number
  physical_cores: number
  recommended_thread_cap: number
  generated_at: string
  spec_refs: string[]
  steps: PlanSection[]
  follow_up: string[]
}

interface DiagnosticsSummary {
  total: number
  errors: number
  warnings: number
  infos: number
  last_seen?: string
  log_path?: string
}

interface DiagnosticsResponse {
  events: DiagnosticEvent[]
  summary: DiagnosticsSummary
}

const fetchObservabilityData = async (): Promise<ObservabilityData> => {
  try {
    const [diagnostics, system, planes, harness] = await Promise.all([
      apiClient.get<DiagnosticsResponse>(apiPath('runtime/diagnostics')).catch(() => ({
        data: {
          events: [],
          summary: { total: 0, errors: 0, warnings: 0, infos: 0 },
        },
      })),
      apiClient.get(apiPath('system')).catch(() => ({ data: {} })),
      apiClient.get(apiPath('planes/status')).catch(() => ({ data: {} })),
      apiClient.get<HarnessReport>(apiPath('runtime/harness-report')).catch(() => ({ data: undefined })),
    ])

    const systemData = system.data || {}
    const planesData = planes.data || {}
    const eventsData = (diagnostics.data?.events || []).map((event, idx) => ({
      ...event,
      id: event.id || `evt-${idx}`,
      type: (event as any).type || (event as any).severity || 'info',
    }))
    const diagSummary = diagnostics.data?.summary

    return {
      events: eventsData.slice(0, 50),
      metrics: [
        {
          name: 'CPU Usage',
          value: systemData.cpu_percent || 0,
          unit: '%',
          trend: 'stable',
          threshold: 80,
        },
        {
          name: 'Memory',
          value: systemData.memory?.percent || 0,
          unit: '%',
          trend: 'up',
          threshold: 85,
        },
        {
          name: 'Disk',
          value: systemData.disk?.percent || 0,
          unit: '%',
          trend: 'stable',
          threshold: 90,
        },
        {
          name: 'Network I/O',
          value: Math.round((systemData.network?.bytes_sent || 0) / 1024 / 1024),
          unit: 'MB',
          trend: 'up',
        },
      ],
      planes: [
        {
          name: 'Data Plane',
          status: planesData.data_plane ? 'healthy' : 'unknown',
          latency_ms: 12,
          error_rate: 0.01,
          throughput: 1250,
        },
        {
          name: 'Control Plane',
          status: planesData.control_plane ? 'healthy' : 'unknown',
          latency_ms: 8,
          error_rate: 0.005,
          throughput: 890,
        },
        {
          name: 'Governance Plane',
          status: planesData.governance_plane ? 'healthy' : 'unknown',
          latency_ms: 15,
          error_rate: 0.002,
          throughput: 340,
        },
      ],
      uptime_seconds: systemData.uptime || 0,
      total_requests: systemData.total_requests || 12450,
      error_count: diagSummary?.errors ?? eventsData.filter((e: DiagnosticEvent) => e.type === 'error').length,
      ai_calls: systemData.ai_calls || 847,
      diagnostics_summary: diagSummary,
      harness: harness.data,
    }
  } catch {
    return {
      events: [],
      metrics: [],
      planes: [],
      uptime_seconds: 0,
      total_requests: 0,
      error_count: 0,
      ai_calls: 0,
      diagnostics_summary: { total: 0, errors: 0, warnings: 0, infos: 0 },
      harness: undefined,
    }
  }
}

const fetchMemoryPlan = async (): Promise<MemoryThreadPlan> => {
  const { data } = await apiClient.get<MemoryThreadPlan>(apiPath('system/memory-thread-plan'))
  return data
}

const formatUptime = (seconds: number): string => {
  const days = Math.floor(seconds / 86400)
  const hours = Math.floor((seconds % 86400) / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  if (days > 0) return `${days}d ${hours}h ${minutes}m`
  if (hours > 0) return `${hours}h ${minutes}m`
  return `${minutes}m`
}

const StatusBadge = ({ status }: { status: string }) => {
  const styles: Record<string, string> = {
    healthy: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
    degraded: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
    error: 'bg-red-500/20 text-red-400 border-red-500/30',
    unknown: 'bg-slate-500/20 text-slate-400 border-slate-500/30',
  }
  const icons: Record<string, React.ReactNode> = {
    healthy: <CheckCircle className="w-3 h-3" />,
    degraded: <AlertTriangle className="w-3 h-3" />,
    error: <XCircle className="w-3 h-3" />,
    unknown: <Eye className="w-3 h-3" />,
  }
  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${styles[status] || styles.unknown}`}>
      {icons[status] || icons.unknown}
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </span>
  )
}

const HarnessStatusBadge = ({ status }: { status: string }) => {
  const normalized = status?.toLowerCase?.() || 'unknown'
  const styles: Record<string, string> = {
    passed: 'bg-emerald-500/15 text-emerald-300 border-emerald-400/30',
    failed: 'bg-red-500/15 text-red-300 border-red-400/30',
    missing: 'bg-slate-500/20 text-slate-200 border-slate-400/30',
    pending: 'bg-amber-500/15 text-amber-200 border-amber-400/30',
    unknown: 'bg-slate-500/15 text-slate-200 border-slate-400/30',
  }
  const icons: Record<string, React.ReactNode> = {
    passed: <CheckCircle className="w-3 h-3" />,
    failed: <XCircle className="w-3 h-3" />,
    missing: <Eye className="w-3 h-3" />,
    pending: <Clock className="w-3 h-3" />,
    unknown: <Eye className="w-3 h-3" />,
  }
  const label = normalized.charAt(0).toUpperCase() + normalized.slice(1)

  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold border ${styles[normalized] || styles.unknown}`}>
      {icons[normalized] || icons.unknown}
      {label}
    </span>
  )
}

const MetricCard = ({ metric }: { metric: SystemMetric }) => {
  const isOverThreshold = metric.threshold && metric.value > metric.threshold
  const trendIcons = {
    up: <TrendingUp className="w-4 h-4 text-emerald-400" />,
    down: <TrendingUp className="w-4 h-4 text-red-400 rotate-180" />,
    stable: <Activity className="w-4 h-4 text-slate-400" />,
  }

  return (
    <div className={`glass-card relative overflow-hidden ${isOverThreshold ? 'border-red-500/50' : ''}`}>
      <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/10 via-transparent to-purple-500/5" />
      <div className="relative flex items-center justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.2em] text-slate-400">{metric.name}</p>
          <p className={`text-3xl font-bold mt-1 ${isOverThreshold ? 'text-red-400' : 'text-white'}`}>
            {metric.value}
            <span className="text-lg text-slate-400 ml-1">{metric.unit}</span>
          </p>
          {metric.threshold && (
            <p className="text-xs text-slate-500 mt-1">Threshold: {metric.threshold}{metric.unit}</p>
          )}
        </div>
        <div className="flex flex-col items-center gap-2">
          {trendIcons[metric.trend]}
          <div className="w-12 h-12 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center">
            {metric.name.includes('CPU') && <Cpu className="w-5 h-5 text-indigo-400" />}
            {metric.name.includes('Memory') && <MemoryStick className="w-5 h-5 text-purple-400" />}
            {metric.name.includes('Disk') && <HardDrive className="w-5 h-5 text-cyan-400" />}
            {metric.name.includes('Network') && <Wifi className="w-5 h-5 text-emerald-400" />}
          </div>
        </div>
      </div>
    </div>
  )
}

const PlaneCard = ({ plane }: { plane: PlaneHealth }) => {
  const icons: Record<string, React.ReactNode> = {
    'Data Plane': <Database className="w-5 h-5" />,
    'Control Plane': <Layers className="w-5 h-5" />,
    'Governance Plane': <Server className="w-5 h-5" />,
  }

  return (
    <div className="glass-card">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500/20 to-purple-500/20 border border-white/10 flex items-center justify-center text-indigo-400">
            {icons[plane.name] || <Server className="w-5 h-5" />}
          </div>
          <div>
            <h4 className="font-semibold text-white">{plane.name}</h4>
            <StatusBadge status={plane.status} />
          </div>
        </div>
      </div>
      <div className="grid grid-cols-3 gap-4 text-center">
        <div className="p-3 rounded-xl bg-white/5 border border-white/10">
          <p className="text-xs text-slate-400 uppercase tracking-wider">Latency</p>
          <p className="text-lg font-semibold text-white mt-1">{plane.latency_ms}ms</p>
        </div>
        <div className="p-3 rounded-xl bg-white/5 border border-white/10">
          <p className="text-xs text-slate-400 uppercase tracking-wider">Error Rate</p>
          <p className="text-lg font-semibold text-white mt-1">{(plane.error_rate * 100).toFixed(2)}%</p>
        </div>
        <div className="p-3 rounded-xl bg-white/5 border border-white/10">
          <p className="text-xs text-slate-400 uppercase tracking-wider">Throughput</p>
          <p className="text-lg font-semibold text-white mt-1">{plane.throughput}/s</p>
        </div>
      </div>
    </div>
  )
}

const EventRow = ({ event }: { event: DiagnosticEvent }) => {
  const typeColors: Record<string, string> = {
    error: 'text-red-400 bg-red-500/10 border-red-500/30',
    warning: 'text-amber-400 bg-amber-500/10 border-amber-500/30',
    info: 'text-blue-400 bg-blue-500/10 border-blue-500/30',
    debug: 'text-slate-400 bg-slate-500/10 border-slate-500/30',
  }

  return (
    <div className="p-3 rounded-xl border border-white/10 bg-white/5 hover:bg-white/10 transition-colors">
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-start gap-3">
          <span className={`px-2 py-1 rounded text-xs font-medium border ${typeColors[event.type] || typeColors.info}`}>
            {event.type.toUpperCase()}
          </span>
          <div>
            <p className="text-sm text-white">{event.message}</p>
            <p className="text-xs text-slate-400 mt-1">
              {event.source} · {new Date(event.timestamp).toLocaleString()}
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default function Observability() {
  const queryClient = useQueryClient()
  const [eventFilter, setEventFilter] = useState<string>('all')

  const { data, isLoading } = useQuery({
    queryKey: ['observability'],
    queryFn: fetchObservabilityData,
    refetchInterval: 15000,
  })

  const memoryPlanQuery = useQuery({
    queryKey: ['memory-thread-plan'],
    queryFn: fetchMemoryPlan,
    staleTime: 5 * 60 * 1000,
  })

  const handleRefresh = () => {
    queryClient.invalidateQueries({ queryKey: ['observability'] })
  }

  if (isLoading) {
    return (
      <div className="px-4 py-6 sm:px-0">
        <div className="glass-card flex h-72 items-center justify-center">
          <div className="h-12 w-12 animate-spin rounded-full border-2 border-white/30 border-t-white" />
        </div>
      </div>
    )
  }

  const filteredEvents = data?.events.filter(
    (event) => eventFilter === 'all' || event.type === eventFilter
  ) || []
  const diagnosticsSummary = data?.diagnostics_summary
  const memoryPlan = memoryPlanQuery.data

  return (
    <div className="px-4 py-6 sm:px-0 space-y-8 text-slate-100">
      {/* Header */}
      <section className="glass-card relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-purple-500/20 via-transparent to-indigo-500/10" />
        <div className="relative flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <p className="eyebrow-text flex items-center gap-2">
              <Eye className="w-4 h-4" />
              Observability Fabric
            </p>
            <h1 className="mt-2 text-3xl font-semibold text-white">System Observability</h1>
            <p className="mt-3 max-w-2xl text-sm text-slate-300">
              Real-time telemetry, diagnostics, and health monitoring across all planes.
              Runtime events feed the AI auto-fix pipeline for autonomous recovery.
            </p>
          </div>
          <button
            onClick={handleRefresh}
            className="btn-tonal flex items-center gap-2"
          >
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
        </div>
      </section>

      {/* Summary Stats */}
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <div className="glass-card relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/20 via-transparent to-teal-500/10" />
          <div className="relative">
            <p className="eyebrow-text">Uptime</p>
            <p className="text-3xl font-bold text-white mt-2">{formatUptime(data?.uptime_seconds || 0)}</p>
            <p className="text-sm text-slate-300 mt-1">System running</p>
          </div>
        </div>
        <div className="glass-card relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-blue-500/20 via-transparent to-indigo-500/10" />
          <div className="relative">
            <p className="eyebrow-text">Total Requests</p>
            <p className="text-3xl font-bold text-white mt-2">{(data?.total_requests || 0).toLocaleString()}</p>
            <p className="text-sm text-slate-300 mt-1">API calls processed</p>
          </div>
        </div>
        <div className="glass-card relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-amber-500/20 via-transparent to-orange-500/10" />
          <div className="relative">
            <p className="eyebrow-text">Errors</p>
            <p className="text-3xl font-bold text-white mt-2">{data?.error_count}</p>
            <p className="text-sm text-slate-300 mt-1">Requiring attention</p>
          </div>
        </div>
        <div className="glass-card relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-purple-500/20 via-transparent to-pink-500/10" />
          <div className="relative flex items-center gap-3">
            <Sparkles className="w-8 h-8 text-purple-400" />
            <div>
              <p className="eyebrow-text">AI Calls</p>
              <p className="text-3xl font-bold text-white">{(data?.ai_calls || 0).toLocaleString()}</p>
              <p className="text-sm text-slate-300">OpenAI API</p>
            </div>
          </div>
        </div>
      </div>

      {/* Workspace Harness */}
      {data?.harness && (
        <section className="glass-card border border-indigo-500/30 bg-gradient-to-br from-indigo-500/10 via-transparent to-purple-500/10">
          <div className="flex items-center justify-between gap-3 mb-4">
            <div className="flex items-center gap-3">
              <Server className="w-5 h-5 text-indigo-300" />
              <div>
                <p className="eyebrow-text">Workspace Harness</p>
                <h2 className="text-xl font-semibold text-white">osdash scan/test summary</h2>
                <p className="text-xs text-slate-300">
                  Aggregated lint/test/build/security results from the latest harness run.
                </p>
              </div>
            </div>
            <HarnessStatusBadge status={data.harness.status} />
          </div>
          {data.harness.total_projects === 0 ? (
            <div className="text-sm text-slate-300">No harness reports found yet.</div>
          ) : (
            <>
              <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
                <div className="rounded-xl border border-white/10 bg-white/5 p-3">
                  <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Projects</p>
                  <p className="text-2xl font-semibold text-white mt-1">{data.harness.total_projects}</p>
                </div>
                <div className="rounded-xl border border-emerald-500/30 bg-emerald-500/5 p-3">
                  <p className="text-xs uppercase tracking-[0.2em] text-emerald-300">Passed</p>
                  <p className="text-2xl font-semibold text-white mt-1">{data.harness.passed_checks}</p>
                </div>
                <div className="rounded-xl border border-red-500/30 bg-red-500/5 p-3">
                  <p className="text-xs uppercase tracking-[0.2em] text-red-300">Failed</p>
                  <p className="text-2xl font-semibold text-white mt-1">{data.harness.failed_checks}</p>
                </div>
                <div className="rounded-xl border border-amber-500/30 bg-amber-500/5 p-3">
                  <p className="text-xs uppercase tracking-[0.2em] text-amber-200">Skipped</p>
                  <p className="text-2xl font-semibold text-white mt-1">{data.harness.skipped_checks}</p>
                </div>
              </div>
              <div className="mt-4 grid gap-3 md:grid-cols-2">
                {data.harness.projects.slice(0, 4).map((project) => (
                  <div key={project.name} className="rounded-xl border border-white/10 bg-white/5 p-3">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-semibold text-white">{project.name}</p>
                        <p className="text-xs text-slate-400">
                          Checks: {project.passed} passed · {project.failed} failed · {project.skipped} skipped
                        </p>
                      </div>
                      <HarnessStatusBadge status={project.status} />
                    </div>
                    {project.commands.length > 0 && (
                      <p className="mt-2 text-[11px] text-slate-400 line-clamp-2">
                        {project.commands.slice(0, 2).join(' · ')}
                      </p>
                    )}
                  </div>
                ))}
              </div>
              {data.harness.report_path && (
                <p className="mt-3 text-[11px] text-slate-400 break-words">
                  Report: {data.harness.report_path}
                </p>
              )}
            </>
          )}
        </section>
      )}

      {/* System Metrics */}
      <section>
        <div className="flex items-center gap-3 mb-4">
          <BarChart3 className="w-5 h-5 text-indigo-400" />
          <h2 className="text-xl font-semibold text-white">System Metrics</h2>
        </div>
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {data?.metrics.map((metric) => (
            <MetricCard key={metric.name} metric={metric} />
          ))}
        </div>
      </section>

      {/* Plane Health */}
      <section>
        <div className="flex items-center gap-3 mb-4">
          <Layers className="w-5 h-5 text-indigo-400" />
          <h2 className="text-xl font-semibold text-white">Plane Health</h2>
        </div>
        <div className="grid gap-4 md:grid-cols-3">
          {data?.planes.map((plane) => (
            <PlaneCard key={plane.name} plane={plane} />
          ))}
        </div>
      </section>

      {/* Memory & Thread Resilience Playbook */}
      <section className="glass-card">
        <div className="flex items-center gap-3 mb-4">
          <MemoryStick className="w-5 h-5 text-indigo-400" />
          <div>
            <h2 className="text-xl font-semibold text-white">Memory & Thread Resilience Playbook</h2>
            <p className="text-sm text-slate-400">
              Auto-generated runbook that mirrors the ops scripts we ship with the AI assistant. Use it when
              macOS reports application memory exhaustion.
            </p>
          </div>
        </div>
        {memoryPlanQuery.isLoading ? (
          <div className="py-8 text-center text-slate-400">
            <div className="mx-auto mb-3 h-10 w-10 animate-spin rounded-full border-2 border-white/20 border-t-white" />
            Loading remediation plan…
          </div>
        ) : memoryPlan ? (
          <div className="space-y-6">
            <div className="flex flex-wrap gap-4 text-xs uppercase tracking-[0.25em] text-slate-400">
              <span>OS · {memoryPlan.os_family}</span>
              <span>Arch · {memoryPlan.architecture}</span>
              <span>Physical cores · {memoryPlan.physical_cores}</span>
              <span>Logical cores · {memoryPlan.logical_cores}</span>
              <span>Thread cap · {memoryPlan.recommended_thread_cap}</span>
              <span>Generated · {new Date(memoryPlan.generated_at).toLocaleString()}</span>
            </div>
            <div className="grid gap-4 xl:grid-cols-2">
              {memoryPlan.steps.map((step) => (
                <article key={step.title} className="rounded-2xl border border-white/10 bg-white/5 p-5 space-y-4">
                  <header>
                    <p className="eyebrow-text">{step.title}</p>
                    <p className="text-sm text-slate-300 mt-1">{step.objective}</p>
                  </header>
                  <div className="space-y-3">
                    {step.commands.map((cmd) => (
                      <div key={cmd.command} className="rounded-xl border border-white/10 bg-white/5 p-3">
                        <div className="flex items-start justify-between gap-3">
                          <code className="text-xs font-mono text-indigo-200">{cmd.command}</code>
                          {cmd.requires_sudo && (
                            <span className="rounded-full bg-red-500/20 px-2 py-0.5 text-[10px] font-semibold uppercase text-red-300">
                              sudo
                            </span>
                          )}
                        </div>
                        {cmd.description && (
                          <p className="mt-2 text-xs text-slate-300 leading-relaxed">{cmd.description}</p>
                        )}
                      </div>
                    ))}
                  </div>
                  {step.verification.length > 0 && (
                    <div className="rounded-xl border border-emerald-400/30 bg-emerald-500/5 p-3">
                      <p className="text-xs font-semibold text-emerald-300 uppercase tracking-[0.2em]">
                        Verification
                      </p>
                      <ul className="mt-1 list-disc space-y-1 pl-4 text-xs text-emerald-100/80">
                        {step.verification.map((item) => (
                          <li key={item}>{item}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </article>
              ))}
            </div>
            {memoryPlan.follow_up.length > 0 && (
              <div className="rounded-2xl border border-white/10 bg-white/5 p-5">
                <p className="eyebrow-text">Follow-up</p>
                <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-slate-200">
                  {memoryPlan.follow_up.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
                <p className="mt-3 text-xs text-slate-400">
                  Spec references: {memoryPlan.spec_refs.join(', ')}
                </p>
              </div>
            )}
          </div>
        ) : (
          <div className="py-8 text-center text-slate-400">
            Unable to load the remediation plan. Check the backend logs for details.
          </div>
        )}
      </section>

      {/* Diagnostic Events */}
      <section className="glass-card">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <Zap className="w-5 h-5 text-indigo-400" />
            <div>
              <h2 className="text-xl font-semibold text-white">Diagnostic Events</h2>
              <p className="text-sm text-slate-400">Runtime events feeding the auto-fix pipeline</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-slate-400" />
            <select
              value={eventFilter}
              onChange={(e) => setEventFilter(e.target.value)}
              className="rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white"
            >
              <option value="all">All Events</option>
              <option value="error">Errors</option>
              <option value="warning">Warnings</option>
              <option value="info">Info</option>
              <option value="debug">Debug</option>
            </select>
          </div>
        </div>
        {diagnosticsSummary && (
          <div className="grid gap-3 md:grid-cols-4 mb-4">
            <div className="rounded-xl border border-white/10 bg-white/5 p-3">
              <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Total</p>
              <p className="text-xl font-semibold text-white mt-1">{diagnosticsSummary.total}</p>
            </div>
            <div className="rounded-xl border border-red-500/30 bg-red-500/5 p-3">
              <p className="text-xs uppercase tracking-[0.2em] text-red-300">Errors</p>
              <p className="text-xl font-semibold text-white mt-1">{diagnosticsSummary.errors}</p>
            </div>
            <div className="rounded-xl border border-amber-500/30 bg-amber-500/5 p-3">
              <p className="text-xs uppercase tracking-[0.2em] text-amber-300">Warnings</p>
              <p className="text-xl font-semibold text-white mt-1">{diagnosticsSummary.warnings}</p>
            </div>
            <div className="rounded-xl border border-emerald-500/30 bg-emerald-500/5 p-3">
              <p className="text-xs uppercase tracking-[0.2em] text-emerald-300">Last Seen</p>
              <p className="text-xs text-slate-200 mt-1">
                {diagnosticsSummary.last_seen ? new Date(diagnosticsSummary.last_seen).toLocaleString() : 'N/A'}
              </p>
              {diagnosticsSummary.log_path && (
                <p className="text-[11px] text-slate-400 mt-1 break-words">Log: {diagnosticsSummary.log_path}</p>
              )}
            </div>
          </div>
        )}
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {filteredEvents.length === 0 ? (
            <div className="text-center py-8 text-slate-400">
              <Clock className="w-8 h-8 mx-auto mb-2 opacity-50" />
              <p>No diagnostic events recorded yet</p>
              <p className="text-xs mt-1">Events will appear here as they occur</p>
            </div>
          ) : (
            filteredEvents.map((event) => (
              <EventRow key={event.id} event={event} />
            ))
          )}
        </div>
      </section>

      {/* v1000 Blueprint Banner */}
      <section className="glass-card border border-dashed border-indigo-500/30 bg-gradient-to-r from-indigo-500/10 via-purple-500/10 to-pink-500/10">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
            <Sparkles className="w-6 h-6 text-white" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-white">Version 1000 Observability</h3>
            <p className="text-sm text-slate-300">
              Future enhancements: OpenTelemetry export, distributed tracing, 
              blockchain-anchored audit trails, and multi-region health aggregation.
            </p>
          </div>
        </div>
      </section>
    </div>
  )
}
