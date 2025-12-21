import { useEffect, useMemo, useState, useCallback } from 'react'
import { Play, PlusCircle, RefreshCw } from 'lucide-react'
import apiClient, { apiPath } from '../lib/apiClient'

interface Parameter {
  name: string
  min: string
  max: string
}

interface Experiment {
  id: string
  name: string
  status: string
  progress: number
  total: number
  eta: string
  description: string
}

interface ModelInfo {
  id: string
  name: string
  status: string
  accuracy: number
  description: string
  last_updated: string
}

interface ReportInfo {
  title: string
  summary: string
  generated: string
}

interface KnowledgeGraph {
  nodes: { label: string; x: number; y: number }[]
  edges: [number, number][]
}

interface WorkspaceSnapshot {
  status_message: string
  simulation_config: {
    type: string
    model: string
    iterations: number
    confidence: number
    parameters: Parameter[]
  }
  metrics: {
    mean: number
    std: number
    min: number
    max: number
    confidence_interval: [number, number]
  }
  analytics: {
    series: number[]
    bounds: number[]
  }
  experiments: Experiment[]
  models: ModelInfo[]
  reports: ReportInfo[]
  knowledge_graph: KnowledgeGraph
  updated_at: string
}

interface SystemStats {
  cpu_percent: number
  memory?: { used?: number; total?: number }
}

interface Banner {
  type: 'success' | 'error'
  message: string
}

const fetchWorkspaceSnapshot = async (): Promise<WorkspaceSnapshot> => {
  const { data } = await apiClient.get<WorkspaceSnapshot>(apiPath('research/snapshot'))
  return data
}

const fetchSystemStats = async (): Promise<SystemStats> => {
  const { data } = await apiClient.get<{ system_stats: SystemStats }>(apiPath('dashboard/stats'))
  return data.system_stats
}

export default function Research() {
  const [workspace, setWorkspace] = useState<WorkspaceSnapshot | null>(null)
  const [systemStats, setSystemStats] = useState<SystemStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [actionBusy, setActionBusy] = useState(false)
  const [banner, setBanner] = useState<Banner | null>(null)
  const [simulationType, setSimulationType] = useState('monte_carlo')
  const [modelId, setModelId] = useState('financial_risk')
  const [iterations, setIterations] = useState(1000)
  const [confidence, setConfidence] = useState(0.95)
  const [parameters, setParameters] = useState<Parameter[]>([])

  useEffect(() => {
    let mounted = true
    const load = async () => {
      try {
        const [snapshot, stats] = await Promise.all([fetchWorkspaceSnapshot(), fetchSystemStats()])
        if (!mounted) return
        setWorkspace(snapshot)
        setSystemStats(stats)
      } catch (err) {
        if (mounted) {
          setBanner({
            type: 'error',
            message: err instanceof Error ? err.message : 'Failed to load workspace',
          })
        }
      } finally {
        if (mounted) setLoading(false)
      }
    }
    load()
    return () => {
      mounted = false
    }
  }, [])

  useEffect(() => {
    if (!workspace) return
    const cfg = workspace.simulation_config
    setSimulationType(cfg.type)
    setModelId(cfg.model)
    setIterations(cfg.iterations)
    setConfidence(cfg.confidence)
    setParameters(cfg.parameters || [])
  }, [workspace])

  const summary = useMemo(() => {
    if (!workspace) {
      return { experiments: 0, running: 0, reports: 0, models: 0 }
    }
    return {
      experiments: workspace.experiments.length,
      running: workspace.experiments.filter((exp) => exp.status === 'running').length,
      reports: workspace.reports.length,
      models: workspace.models.length,
    }
  }, [workspace])

  const statCards = [
    { icon: '🧪', label: 'Experiments', value: summary.experiments, accent: 'from-cyan-400/30 to-blue-500/5' },
    { icon: '⚡', label: 'Running', value: summary.running, accent: 'from-amber-300/30 to-orange-500/10' },
    { icon: '📚', label: 'Reports', value: summary.reports, accent: 'from-emerald-300/25 to-teal-500/5' },
    { icon: '🧠', label: 'Models', value: summary.models, accent: 'from-violet-400/30 to-purple-700/5' },
  ]

  const metrics = workspace
    ? [
        { label: 'Mean', value: workspace.metrics.mean.toFixed(1) },
        { label: 'Std Dev', value: workspace.metrics.std.toFixed(1) },
        { label: 'Min', value: workspace.metrics.min.toFixed(1) },
        { label: 'Max', value: workspace.metrics.max.toFixed(1) },
      ]
    : []

  const showBanner = (next: Banner) => {
    setBanner(next)
    setTimeout(() => setBanner(null), 4000)
  }

  const refreshWorkspace = async (silent = false) => {
    if (!silent) setLoading(true)
    try {
      const [snapshot, stats] = await Promise.all([fetchWorkspaceSnapshot(), fetchSystemStats()])
      setWorkspace(snapshot)
      setSystemStats(stats)
      if (!silent) showBanner({ type: 'success', message: 'Workspace refreshed.' })
    } catch (err) {
      if (!silent) {
        showBanner({
          type: 'error',
          message: err instanceof Error ? err.message : 'Refresh failed.',
        })
      }
    } finally {
      if (!silent) setLoading(false)
    }
  }

  const runSimulation = async () => {
    if (!workspace) return
    setActionBusy(true)
    try {
      await apiClient.post(apiPath('research/run'), {
        sim_type: simulationType,
        model_id: modelId,
        iterations,
      })
      await refreshWorkspace(true)
      showBanner({ type: 'success', message: 'Simulation started.' })
    } catch (err) {
      showBanner({
        type: 'error',
        message: err instanceof Error ? err.message : 'Simulation failed to start.',
      })
    } finally {
      setActionBusy(false)
    }
  }

  const designExperiment = async () => {
    if (!workspace) return
    setActionBusy(true)
    try {
      const vars = parameters.filter((p) => p.name.trim()).map((p) => p.name.trim())
      await apiClient.post(apiPath('research/design'), { design_type: 'parameter_sweep', variables: vars })
      await refreshWorkspace(true)
      showBanner({ type: 'success', message: 'Experiment design ready.' })
    } catch (err) {
      showBanner({
        type: 'error',
        message: err instanceof Error ? err.message : 'Experiment design failed.',
      })
    } finally {
      setActionBusy(false)
    }
  }

  const addParameter = () => {
    setParameters((prev) => [...prev, { name: '', min: '', max: '' }])
  }

  const updateParameter = (index: number, field: keyof Parameter, value: string) => {
    setParameters((prev) => prev.map((param, i) => (i === index ? { ...param, [field]: value } : param)))
  }

  const removeParameter = (index: number) => {
    setParameters((prev) => prev.filter((_, i) => i !== index))
  }

  // Memoize select handlers to prevent unnecessary re-renders
  const handleSimulationTypeChange = useCallback((e: React.ChangeEvent<HTMLSelectElement>) => {
    setSimulationType(e.target.value)
  }, [])

  const handleModelIdChange = useCallback((e: React.ChangeEvent<HTMLSelectElement>) => {
    setModelId(e.target.value)
  }, [])

  const handleIterationsChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setIterations(Number(e.target.value))
  }, [])

  const handleConfidenceChange = useCallback((e: React.ChangeEvent<HTMLSelectElement>) => {
    setConfidence(Number(e.target.value))
  }, [])

  if (loading) {
    return (
      <div className="flex h-80 items-center justify-center">
        <div className="h-12 w-12 animate-spin rounded-full border-2 border-white/30 border-t-white" />
      </div>
    )
  }

  if (!workspace) {
    return (
      <div className="glass-card text-center text-sm text-slate-300">
        Unable to load research workspace. Please try again later.
      </div>
    )
  }

  const [ciLow, ciHigh] = workspace.metrics.confidence_interval

  return (
    <div className="px-4 py-6 sm:px-0 space-y-6 text-slate-100">
      {banner && (
        <div
          className={`glass-card border-l-4 ${
            banner.type === 'error' ? 'border-red-400/60' : 'border-emerald-400/60'
          }`}
        >
          <p className="text-sm">{banner.message}</p>
        </div>
      )}

      <div className="glass-card flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <p className="eyebrow-text">Research</p>
          <h1 className="mt-1 text-3xl font-bold text-white">Research & Simulation Workspace</h1>
          <p className="mt-2 text-sm text-slate-300">{workspace.status_message}</p>
        </div>
        <div className="flex flex-wrap gap-3">
          <button className="btn-tonal" onClick={() => refreshWorkspace(false)}>
            <RefreshCw className="h-4 w-4" />
            Refresh
          </button>
          <button className="btn-tonal" onClick={designExperiment} disabled={actionBusy}>
            <PlusCircle className="h-4 w-4" />
            Design Experiment
          </button>
          <button
            onClick={runSimulation}
            disabled={actionBusy}
            className="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-blue-500 to-indigo-500 px-5 py-2 text-sm font-semibold shadow-lg shadow-blue-500/20 transition hover:opacity-90 disabled:opacity-60"
          >
            <Play className="h-4 w-4" />
            Run Simulation
          </button>
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {statCards.map((stat) => (
          <StatCard key={stat.label} icon={stat.icon} label={stat.label} value={stat.value} accent={stat.accent} />
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="glass-card space-y-6">
          <div className="flex items-start justify-between">
            <div>
              <h3 className="text-lg font-semibold text-white">Simulation Configuration</h3>
              {systemStats && (
                <p className="text-xs text-slate-400">
                  CPU {Math.round(systemStats.cpu_percent)}% · RAM{' '}
                  {formatBytes(systemStats.memory?.used)}/{formatBytes(systemStats.memory?.total)}
                </p>
              )}
            </div>
          </div>
          <div className="grid gap-4 md:grid-cols-2">
            <label className="text-sm text-slate-200">
              Type
              <select
                value={simulationType}
                onChange={(e) => {
                  e.stopPropagation()
                  handleSimulationTypeChange(e)
                }}
                className="mt-1 w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white focus:border-primary-500 focus:outline-none transition-all hover:border-white/20 active:scale-[0.98] cursor-pointer"
                style={{ 
                  WebkitAppearance: 'none',
                  MozAppearance: 'none',
                  cursor: 'pointer',
                }}
              >
                <option value="monte_carlo">Monte Carlo</option>
                <option value="agent_based">Agent-Based</option>
                <option value="discrete_event">Discrete Event</option>
                <option value="system_dynamics">System Dynamics</option>
              </select>
            </label>
            <label className="text-sm text-slate-200">
              Model
              <select
                value={modelId}
                onChange={(e) => {
                  e.stopPropagation()
                  handleModelIdChange(e)
                }}
                className="mt-1 w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white focus:border-primary-500 focus:outline-none transition-all hover:border-white/20 active:scale-[0.98] cursor-pointer"
                style={{ 
                  WebkitAppearance: 'none',
                  MozAppearance: 'none',
                  cursor: 'pointer',
                }}
              >
                {workspace.models.map((model) => (
                  <option key={model.id} value={model.id}>
                    {model.name}
                  </option>
                ))}
              </select>
            </label>
            <label className="text-sm text-slate-200">
              Iterations
              <input
                type="number"
                min={100}
                value={iterations}
                onChange={handleIterationsChange}
                className="mt-1 w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white focus:border-primary-500 focus:outline-none"
              />
            </label>
            <label className="text-sm text-slate-200">
              Confidence
              <select
                value={confidence}
                onChange={handleConfidenceChange}
                className="mt-1 w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white focus:border-primary-500 focus:outline-none"
              >
                <option value={0.9}>90%</option>
                <option value={0.95}>95%</option>
                <option value={0.99}>99%</option>
              </select>
            </label>
          </div>
        </div>
        <div className="glass-card space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-white">Parameters</h3>
            <button className="btn-tonal text-xs" onClick={addParameter}>
              <PlusCircle className="h-4 w-4" />
              Add
            </button>
          </div>
          {parameters.length === 0 ? (
            <p className="text-sm text-slate-300">No parameters configured.</p>
          ) : (
            <div className="space-y-3">
              {parameters.map((param, index) => (
                <ParameterRow
                  key={`${param.name}-${index}`}
                  param={param}
                  onUpdate={(field, value) => updateParameter(index, field, value)}
                  onRemove={() => removeParameter(index)}
                />
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="glass-card space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-white">Active Experiments</h3>
            <span className="pill-muted">Updated {workspace.updated_at}</span>
          </div>
          <div className="space-y-3">
            {workspace.experiments.map((experiment) => (
              <ExperimentCard key={experiment.id} experiment={experiment} />
            ))}
          </div>
        </div>
        <div className="glass-card space-y-4">
          <h3 className="text-lg font-semibold text-white">Simulation Metrics</h3>
          <div className="grid gap-3 sm:grid-cols-2">
            {metrics.map((metric) => (
              <MetricChip key={metric.label} label={metric.label} value={metric.value} />
            ))}
          </div>
          <p className="text-sm text-slate-400">
            Confidence interval: {ciLow.toFixed(1)} – {ciHigh.toFixed(1)}
          </p>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="glass-card space-y-4">
          <h3 className="text-lg font-semibold text-white">Model Registry</h3>
          <div className="space-y-3">
            {workspace.models.map((model) => (
              <ModelCard key={model.id} model={model} />
            ))}
          </div>
        </div>
        <div className="glass-card space-y-4">
          <h3 className="text-lg font-semibold text-white">Simulation Analytics</h3>
          <AnalyticsChart series={workspace.analytics.series} bounds={workspace.analytics.bounds} />
        </div>
      </div>

      <div className="glass-card space-y-4">
        <h3 className="text-lg font-semibold text-white">Research Knowledge Graph</h3>
        <KnowledgeGraph graph={workspace.knowledge_graph} />
      </div>

      <div className="glass-card space-y-4">
        <h3 className="text-lg font-semibold text-white">Research Reports & Publications</h3>
        <div className="grid gap-4 md:grid-cols-2">
          {workspace.reports.map((report) => (
            <ReportCard key={report.title} report={report} />
          ))}
        </div>
      </div>
    </div>
  )
}

function StatCard({
  icon,
  label,
  value,
  accent,
}: {
  icon: string
  label: string
  value: number
  accent: string
}) {
  return (
    <div className="glass-card relative overflow-hidden">
      <div className={`pointer-events-none absolute inset-0 bg-gradient-to-br ${accent}`} />
      <div className="relative flex items-center justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.2em] text-slate-400">{label}</p>
          <p className="mt-2 text-3xl font-semibold text-white">{value}</p>
        </div>
        <div className="text-3xl">{icon}</div>
      </div>
    </div>
  )
}

function MetricChip({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-center">
      <p className="text-xs uppercase tracking-wider text-slate-400">{label}</p>
      <p className="text-2xl font-semibold text-white">{value}</p>
    </div>
  )
}

function ParameterRow({
  param,
  onUpdate,
  onRemove,
}: {
  param: Parameter
  onUpdate: (field: keyof Parameter, value: string) => void
  onRemove: () => void
}) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 p-3">
      <div className="flex flex-col gap-3 md:flex-row">
        <input
          value={param.name}
          onChange={(e) => onUpdate('name', e.target.value)}
          placeholder="Parameter"
          className="flex-1 rounded-xl border border-white/10 bg-white/10 px-3 py-2 text-sm text-white focus:border-primary-500 focus:outline-none"
        />
        <input
          value={param.min}
          onChange={(e) => onUpdate('min', e.target.value)}
          placeholder="Min"
          className="flex-1 rounded-xl border border-white/10 bg-white/10 px-3 py-2 text-sm text-white focus:border-primary-500 focus:outline-none"
        />
        <input
          value={param.max}
          onChange={(e) => onUpdate('max', e.target.value)}
          placeholder="Max"
          className="flex-1 rounded-xl border border-white/10 bg-white/10 px-3 py-2 text-sm text-white focus:border-primary-500 focus:outline-none"
        />
        <button className="btn-tonal text-xs" onClick={onRemove}>
          Remove
        </button>
      </div>
    </div>
  )
}

function ExperimentCard({ experiment }: { experiment: Experiment }) {
  const pct = progressPercent(experiment.progress, experiment.total)
  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-semibold text-white">{experiment.name}</p>
          <p className="text-xs text-slate-400">{experiment.description}</p>
        </div>
        <span className="pill-muted text-[10px] uppercase">{experiment.status}</span>
      </div>
      <div className="mt-3">
        <div className="h-2 rounded-full bg-white/10">
          <div
            className="h-2 rounded-full bg-gradient-to-r from-cyan-400 to-blue-500"
            style={{ width: `${pct}%` }}
          />
        </div>
        <div className="mt-2 flex items-center justify-between text-xs text-slate-400">
          <span>
            {experiment.progress.toLocaleString()} / {experiment.total.toLocaleString()} ({pct}%)
          </span>
          <span>{experiment.eta}</span>
        </div>
      </div>
    </div>
  )
}

function ModelCard({ model }: { model: ModelInfo }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-semibold text-white">{model.name}</p>
          <p className="text-xs text-slate-400">{model.description}</p>
        </div>
        <div className="text-right text-xs text-slate-400">
          <p>{model.status}</p>
          <p>{(model.accuracy * 100).toFixed(0)}% acc.</p>
        </div>
      </div>
      <p className="mt-2 text-xs text-slate-500">Updated {model.last_updated}</p>
    </div>
  )
}

function ReportCard({ report }: { report: ReportInfo }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
      <p className="text-sm font-semibold text-white">{report.title}</p>
      <p className="mt-2 text-xs text-slate-400">{report.summary}</p>
      <div className="mt-3 flex items-center justify-between text-xs text-slate-500">
        <span>{report.generated}</span>
        <button className="btn-tonal px-3 py-1 text-[11px]">Download</button>
      </div>
    </div>
  )
}

function AnalyticsChart({ series, bounds }: { series: number[]; bounds: number[] }) {
  if (!series || series.length < 2) {
    return <p className="text-sm text-slate-300">Not enough analytics data.</p>
  }
  const maxVal = Math.max(...series, ...bounds, 1)
  const seriesPoints = series
    .map((value, idx) => {
      const x = (idx / (series.length - 1)) * 100
      const y = 100 - (value / maxVal) * 100
      return `${x},${y}`
    })
    .join(' ')
  return (
    <svg viewBox="0 0 100 100" className="h-64 w-full">
      <polyline points={seriesPoints} fill="none" stroke="#38bdf8" strokeWidth={2.5} />
    </svg>
  )
}

function KnowledgeGraph({ graph }: { graph: KnowledgeGraph }) {
  return (
    <svg viewBox="0 0 700 320" className="h-64 w-full">
      {graph.edges.map(([start, end], idx) => {
        const from = graph.nodes[start]
        const to = graph.nodes[end]
        if (!from || !to) return null
        return (
          <line
            key={`${start}-${end}-${idx}`}
            x1={from.x}
            y1={from.y}
            x2={to.x}
            y2={to.y}
            stroke="rgba(148,163,184,0.4)"
            strokeWidth={2}
          />
        )
      })}
      {graph.nodes.map((node, idx) => (
        <g key={`${node.label}-${idx}`}>
          <circle cx={node.x} cy={node.y} r={36} fill="rgba(59,130,246,0.25)" stroke="rgba(59,130,246,0.6)" />
          <text
            x={node.x}
            y={node.y}
            textAnchor="middle"
            alignmentBaseline="middle"
            fill="#e2e8f0"
            fontSize="12"
          >
            {node.label}
          </text>
        </g>
      ))}
    </svg>
  )
}

function formatBytes(value?: number) {
  if (!value) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  let unit = 0
  let val = value
  while (val >= 1024 && unit < units.length - 1) {
    val /= 1024
    unit += 1
  }
  return `${val.toFixed(1)} ${units[unit]}`
}

function progressPercent(progress: number, total: number) {
  if (!total) return 0
  return Math.min(100, Math.round((progress / total) * 100))
}