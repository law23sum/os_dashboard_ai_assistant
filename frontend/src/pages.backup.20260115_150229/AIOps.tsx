import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { RefreshCw, Brain, Activity, Sparkles, Cpu } from 'lucide-react'
import { useEffect, useMemo, useState } from 'react'
import apiClient, { apiPath } from '../lib/apiClient'
import { extractArray } from '../lib/responseHelpers'
import type {
  DocumentOperation,
  DocumentOperationSummary,
  ReasoningTrace,
  ReasoningStatus,
  DriverSchedulingSnapshot,
} from '../types'
import { toast } from '../utils/toast'
import PageHeader from '../components/PageHeader'

const statusOptions = ['all', 'queued', 'running', 'succeeded', 'failed', 'needs_review']

const statusColors: Record<string, string> = {
  queued: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200',
  running: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
  succeeded: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
  failed: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
  needs_review: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
}

const fetchOperations = async (
  status?: string,
  integrationType?: string,
): Promise<DocumentOperation[]> => {
  const params: Record<string, string | number> = { limit: 50 }
  if (status && status !== 'all') params.status = status
  if (integrationType) params.integration_type = integrationType
  const { data } = await apiClient.get(apiPath('operations/'), {
    params,
  })
  return extractArray<DocumentOperation>(data, ['operations', 'items'])
}

const fetchSummary = async (): Promise<DocumentOperationSummary> => {
  const { data } = await apiClient.get<DocumentOperationSummary>(apiPath('operations/summary'))
  return data
}

const fetchReasoningStatus = async (): Promise<ReasoningStatus> => {
  try {
    const { data } = await apiClient.get<ReasoningStatus>(apiPath('ai/reasoning/status'))
    return data
  } catch (error: any) {
    if (error?.response?.status === 503) {
      return {
        available: false,
        initialized: false,
        personas: [],
        daemons: [],
        recent_traces: 0,
      }
    }
    throw error
  }
}

const fetchReasoningTraces = async (): Promise<ReasoningTrace[]> => {
  try {
    const { data } = await apiClient.get<ReasoningTrace[]>(apiPath('ai/reasoning/traces'))
    return data
  } catch (error: any) {
    if (error?.response?.status === 503) {
      return []
    }
    throw error
  }
}

const runReasoningQuery = async (payload: { query: string; persona?: string }) => {
  const { data } = await apiClient.post<{ trace: ReasoningTrace; status: ReasoningStatus }>(
    apiPath('ai/reasoning/run'),
    payload,
  )
  return data
}

const fetchDriverMetrics = async (): Promise<DriverSchedulingSnapshot> => {
  const { data } = await apiClient.get<DriverSchedulingSnapshot>(apiPath('ai/drivers/metrics'))
  return data
}

const updateDriverThrottle = async (payload: {
  driver_id: string
  mode: 'auto' | 'manual'
  target_rate: number
}) => {
  const { data } = await apiClient.post<DriverSchedulingSnapshot>(apiPath('ai/drivers/throttle'), payload)
  return data
}

const formatTimestamp = (value?: string | null) => {
  if (!value) return '—'
  return new Date(value).toLocaleString()
}

export default function AIOps() {
  const queryClient = useQueryClient()
  const [statusFilter, setStatusFilter] = useState('all')
  const [integrationFilter, setIntegrationFilter] = useState('')
  const [reasoningInput, setReasoningInput] = useState('')
  const [persona, setPersona] = useState('aic')
  const [activeTrace, setActiveTrace] = useState<ReasoningTrace | null>(null)
  const [driverTargets, setDriverTargets] = useState<Record<string, number>>({})

  const operationsQuery = useQuery({
    queryKey: ['operations', statusFilter, integrationFilter],
    queryFn: () => fetchOperations(statusFilter, integrationFilter),
    refetchInterval: 15000,
  })

  const summaryQuery = useQuery({
    queryKey: ['operations-summary'],
    queryFn: fetchSummary,
    refetchInterval: 30000,
  })

  const reasoningStatusQuery = useQuery({
    queryKey: ['reasoning-status'],
    queryFn: fetchReasoningStatus,
    refetchInterval: 30000,
  })

  const reasoningHistoryQuery = useQuery({
    queryKey: ['reasoning-traces'],
    queryFn: fetchReasoningTraces,
    refetchInterval: 45000,
  })

  const driverMetricsQuery = useQuery({
    queryKey: ['driver-metrics'],
    queryFn: fetchDriverMetrics,
    refetchInterval: 20000,
  })

  const reasoningMutation = useMutation({
    mutationFn: runReasoningQuery,
    onSuccess: (data) => {
      setActiveTrace(data.trace)
      toast.success('Reasoning trace generated')
      queryClient.invalidateQueries({ queryKey: ['reasoning-status'] })
      queryClient.invalidateQueries({ queryKey: ['reasoning-traces'] })
    },
    onError: (error: any) => {
      const detail = error?.response?.data?.detail ?? error?.message ?? 'Reasoning request failed'
      toast.error(detail)
    },
  })

  const driverThrottleMutation = useMutation({
    mutationFn: updateDriverThrottle,
    onSuccess: () => {
      toast.success('Driver throttle updated')
      queryClient.invalidateQueries({ queryKey: ['driver-metrics'] })
    },
    onError: () => toast.error('Unable to update driver throttle'),
  })

  const operations = operationsQuery.data ?? []
  const summary = summaryQuery.data
  const reasoningStatus = reasoningStatusQuery.data
  const reasoningHistory = reasoningHistoryQuery.data ?? []
  const personaChoices = useMemo(() => {
    if (reasoningStatus?.personas?.length) {
      return reasoningStatus.personas
    }
    return [{ id: 'aic', type: 'aic' }]
  }, [reasoningStatus?.personas])

  useEffect(() => {
    if (!personaChoices.some((option) => option.type === persona)) {
      setPersona(personaChoices[0]?.type ?? 'aic')
    }
  }, [personaChoices, persona])

  const runningDaemons =
    reasoningStatus?.daemons?.filter((daemon) => daemon.status === 'running').length ?? 0
  const totalDaemons = reasoningStatus?.daemons?.length ?? 0
  const driverSnapshot = driverMetricsQuery.data

  const handleDriverRateChange = (driverId: string, value: number) => {
    setDriverTargets((prev) => ({ ...prev, [driverId]: value }))
  }

  const handleDriverMode = (driverId: string, mode: 'auto' | 'manual') => {
    const queue = driverSnapshot?.queues.find((item) => item.driver_id === driverId)
    const target = driverTargets[driverId] ?? queue?.admission_rate ?? 0.85
    driverThrottleMutation.mutate({
      driver_id: driverId,
      mode,
      target_rate: mode === 'auto' ? 0.85 : target,
    })
  }

  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="AI Fabric"
        title="AI Operations"
        description="Governance feed for document automations and daemon workflows"
        icon={Cpu}
        actions={
          <button
            onClick={() => {
              operationsQuery.refetch()
              summaryQuery.refetch()
              driverMetricsQuery.refetch()
            }}
            className="btn-primary"
          >
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
        }
      />

      <div className="glass-card page-section">
        <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Driver Scheduling & Backpressure
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Spec §5.12 control plane telemetry mirrored from the Tkinter cockpit.
            </p>
          </div>
          <span className="text-xs uppercase tracking-[0.3em] text-gray-500 dark:text-gray-400">
            {driverSnapshot?.updated_at ? `Updated ${new Date(driverSnapshot.updated_at).toLocaleTimeString()}` : 'Awaiting data'}
          </span>
        </div>
        {driverMetricsQuery.isLoading ? (
          <div className="flex h-32 items-center justify-center">
            <div className="h-8 w-8 animate-spin rounded-full border-b-2 border-primary-500" />
          </div>
        ) : (
          <>
            <div className="mt-4 content-grid grid-cols-1 md:grid-cols-3">
              {driverSnapshot?.queues.map((queue) => {
                const sliderValue = driverTargets[queue.driver_id] ?? queue.admission_rate
                return (
                  <article key={queue.driver_id} className="rounded-2xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 p-4 shadow-sm">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-semibold text-gray-900 dark:text-white">{queue.label}</p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">
                          Queue depth {queue.queue_depth} · max {queue.max_concurrency}
                        </p>
                      </div>
                      <span
                        className={`rounded-full px-2 py-0.5 text-xs font-semibold ${
                          queue.throttled
                            ? 'bg-amber-500/20 text-amber-700 dark:bg-amber-500/30 dark:text-amber-100'
                            : 'bg-emerald-500/20 text-emerald-700 dark:bg-emerald-500/30 dark:text-emerald-100'
                        }`}
                      >
                        {queue.throttled ? 'Throttled' : 'Auto'}
                      </span>
                    </div>
                    <dl className="mt-3 grid grid-cols-2 gap-2 text-xs text-gray-500 dark:text-gray-400">
                      <div>
                        <dt className="uppercase tracking-[0.3em]">Latency</dt>
                        <dd className="text-sm font-semibold text-gray-900 dark:text-white">{queue.avg_latency_ms} ms</dd>
                      </div>
                      <div>
                        <dt className="uppercase tracking-[0.3em]">Admission</dt>
                        <dd className="text-sm font-semibold text-gray-900 dark:text-white">
                          {(queue.admission_rate * 100).toFixed(0)}%
                        </dd>
                      </div>
                      <div>
                        <dt className="uppercase tracking-[0.3em]">Backlog</dt>
                        <dd className="text-sm font-semibold text-gray-900 dark:text-white">{queue.backlog_seconds}s</dd>
                      </div>
                      <div>
                        <dt className="uppercase tracking-[0.3em]">Spec</dt>
                        <dd className="text-sm font-semibold text-gray-900 dark:text-white">{queue.spec_refs.join(', ')}</dd>
                      </div>
                    </dl>
                    <div className="mt-4">
                      <label className="text-xs font-medium text-gray-700 dark:text-gray-300">
                        Admission Target {Math.round(sliderValue * 100)}%
                      </label>
                      <input
                        type="range"
                        min={0.2}
                        max={1}
                        step={0.05}
                        value={sliderValue}
                        onChange={(event) => handleDriverRateChange(queue.driver_id, Number(event.target.value))}
                        className="mt-1 w-full"
                      />
                      <div className="mt-3 flex items-center gap-2">
                        <button
                          type="button"
                          onClick={() => handleDriverMode(queue.driver_id, 'manual')}
                          className="flex-1 rounded-md border border-gray-200 bg-white px-3 py-1.5 text-xs font-semibold text-gray-800 shadow-sm hover:border-primary-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100"
                          disabled={driverThrottleMutation.isPending}
                        >
                          Apply Manual
                        </button>
                        <button
                          type="button"
                          onClick={() => handleDriverMode(queue.driver_id, 'auto')}
                          className="rounded-md border border-gray-200 px-3 py-1.5 text-xs font-semibold text-gray-800 hover:border-primary-500 dark:border-gray-700 dark:text-gray-100"
                          disabled={driverThrottleMutation.isPending}
                        >
                          Auto Mode
                        </button>
                      </div>
                    </div>
                  </article>
                )
              })}
            </div>
            {driverSnapshot?.recommendations?.length ? (
              <div className="mt-4 rounded-2xl border border-dashed border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-900/60 p-4 text-sm text-gray-600 dark:text-gray-300">
                <p className="font-semibold mb-2 flex items-center gap-2">
                  <Sparkles className="h-4 w-4 text-primary-500" />
                  Recommendations
                </p>
                <ul className="space-y-1">
                  {driverSnapshot.recommendations.map((rec) => (
                    <li key={`${rec.driver_id}-${rec.action}`} className="flex items-center gap-2">
                      <span className="rounded-full border border-gray-300 px-2 py-0.5 text-xs uppercase tracking-[0.3em] dark:border-gray-600">
                        {rec.severity}
                      </span>
                      <span className="text-sm">{rec.recommendation}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ) : null}
          </>
        )}
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4 mb-6">
        {statusOptions.slice(1).map((status) => (
          <div
            key={status}
            className="bg-white dark:bg-gray-800 shadow rounded-lg p-4 flex flex-col space-y-1"
          >
            <span className="text-sm text-gray-500 dark:text-gray-400 uppercase tracking-wide">
              {status.replace('_', ' ')}
            </span>
            <span className="text-2xl font-semibold text-gray-900 dark:text-white">
              {summary ? summary[status as keyof DocumentOperationSummary] : '—'}
            </span>
          </div>
        ))}
      </div>

      <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Status
            </label>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            >
              {statusOptions.map((option) => (
                <option key={option} value={option}>
                  {option === 'all' ? 'All statuses' : option.replace('_', ' ')}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Integration Type
            </label>
            <input
              type="text"
              value={integrationFilter}
              onChange={(e) => setIntegrationFilter(e.target.value)}
              placeholder="e.g. onenote, word, excel"
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            />
          </div>
        </div>
      </div>

      <div className="bg-white dark:bg-gray-800 shadow rounded-lg overflow-hidden">
        {operationsQuery.isLoading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
          </div>
        ) : operations.length === 0 ? (
          <div className="text-center py-12 text-gray-500 dark:text-gray-400">
            No operations found for the selected filters.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Title
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Project
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Integration
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Persona
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Started
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Completed
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                {operations.map((operation) => (
                  <tr key={operation.id}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900 dark:text-white">
                        {operation.title}
                      </div>
                      <div className="text-xs text-gray-500 dark:text-gray-400">
                        {operation.operation}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                      {operation.project_id}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white uppercase">
                      {operation.integration_type}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          statusColors[operation.status] ?? statusColors['queued']
                        }`}
                      >
                        {operation.status.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                      {operation.persona}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                      {formatTimestamp(operation.started_at)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                      {formatTimestamp(operation.completed_at)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6 space-y-6 mt-8">
        <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.3em] text-gray-500 dark:text-gray-400">
              Cognitive Layer
            </p>
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white">TRF Reasoning Console</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Run persona-guided reasoning queries and inspect the latest traces from the theoretical reasoning framework.
            </p>
          </div>
          <button
            onClick={() => {
              reasoningStatusQuery.refetch()
              reasoningHistoryQuery.refetch()
            }}
            className="inline-flex items-center rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-900 px-3 py-2 text-sm font-medium text-gray-700 dark:text-gray-100 hover:bg-gray-50 dark:hover:bg-gray-800"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh Status
          </button>
        </div>

        {!reasoningStatus?.available ? (
          <div className="rounded-2xl border border-dashed border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-900/40 p-4 text-sm text-gray-600 dark:text-gray-300">
            Cognitive framework is not available in this build. Install <code>assistant_core</code> extras
            to enable TRF reasoning.
          </div>
        ) : (
          <>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="rounded-2xl border border-white/5 bg-primary-50/30 dark:bg-primary-900/20 p-4">
                <div className="flex items-center gap-2 text-sm text-primary-600 dark:text-primary-300">
                  <Brain className="w-4 h-4" />
                  Personas Online
                </div>
                <p className="mt-2 text-2xl font-semibold text-gray-900 dark:text-white">
                  {reasoningStatus.personas.length}
                </p>
              </div>
              <div className="rounded-2xl border border-white/5 bg-emerald-50/30 dark:bg-emerald-900/20 p-4">
                <div className="flex items-center gap-2 text-sm text-emerald-600 dark:text-emerald-300">
                  <Activity className="w-4 h-4" />
                  Active Daemons
                </div>
                <p className="mt-2 text-2xl font-semibold text-gray-900 dark:text-white">
                  {runningDaemons}/{totalDaemons}
                </p>
              </div>
              <div className="rounded-2xl border border-white/5 bg-amber-50/30 dark:bg-amber-900/20 p-4">
                <div className="flex items-center gap-2 text-sm text-amber-600 dark:text-amber-300">
                  <Sparkles className="w-4 h-4" />
                  Recent Traces
                </div>
                <p className="mt-2 text-2xl font-semibold text-gray-900 dark:text-white">
                  {reasoningStatus.recent_traces}
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-[2fr,1fr] gap-6">
              <div className="rounded-2xl border border-gray-200 dark:border-gray-700 p-4 space-y-4">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  Reasoning Query
                </label>
                <textarea
                  value={reasoningInput}
                  onChange={(event) => setReasoningInput(event.target.value)}
                  rows={3}
                  placeholder="e.g. Explain why the compliance backlog keeps slipping and what to do next."
                  className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
                <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
                  <select
                    value={persona}
                    onChange={(event) => setPersona(event.target.value)}
                    className="rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-900 text-sm px-3 py-2 text-gray-700 dark:text-gray-200 focus:outline-none focus:ring-2 focus:ring-primary-500"
                  >
                    {personaChoices.map((option) => (
                      <option key={option.id} value={option.type}>
                        {option.type.toUpperCase()}
                      </option>
                    ))}
                  </select>
                  <button
                    onClick={() => reasoningMutation.mutate({ query: reasoningInput, persona })}
                    disabled={!reasoningInput.trim() || reasoningMutation.isPending}
                    className="inline-flex items-center justify-center rounded-lg bg-primary-600 px-4 py-2 text-sm font-semibold text-white hover:bg-primary-700 disabled:opacity-50"
                  >
                    {reasoningMutation.isPending ? 'Running…' : 'Run reasoning'}
                  </button>
                </div>
                {reasoningMutation.isError && (
                  <p className="text-sm text-rose-500">
                    {(reasoningMutation.error as Error)?.message ?? 'Reasoning request failed.'}
                  </p>
                )}
              </div>

              <div className="rounded-2xl border border-gray-200 dark:border-gray-700 p-4">
                <h4 className="text-sm font-semibold text-gray-900 dark:text-white mb-3">
                  Recent Traces
                </h4>
                {reasoningHistory.length === 0 ? (
                  <p className="text-sm text-gray-500 dark:text-gray-400">No reasoning traces yet.</p>
                ) : (
                  <div className="space-y-2">
                    {reasoningHistory.map((trace) => (
                      <button
                        key={trace.id}
                        onClick={() => setActiveTrace(trace)}
                        className="w-full text-left rounded-xl border border-gray-200 dark:border-gray-700 px-3 py-2 hover:border-primary-400"
                      >
                        <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                          {trace.query}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">
                          {new Date(trace.created_at).toLocaleTimeString()} ·{' '}
                          {((trace.overall_confidence ?? 0) * 100).toFixed(0)}% confidence
                        </p>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>

            <div className="rounded-2xl border border-gray-200 dark:border-gray-700 p-4">
              <h4 className="text-sm font-semibold text-gray-900 dark:text-white mb-3">
                Reasoning Trace
              </h4>
              {activeTrace ? (
                <div className="space-y-4">
                  <div>
                    <p className="text-xs uppercase tracking-[0.3em] text-gray-500 dark:text-gray-400">
                      {activeTrace.persona_type ? activeTrace.persona_type.toUpperCase() : 'AIC'}
                    </p>
                    <p className="text-lg font-semibold text-gray-900 dark:text-white">{activeTrace.query}</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {activeTrace.final_conclusion} ·{' '}
                      {((activeTrace.overall_confidence ?? 0) * 100).toFixed(0)}% confidence
                    </p>
                  </div>
                  <div className="grid gap-3">
                    {activeTrace.steps.map((step) => (
                      <div
                        key={step.id}
                        className="rounded-2xl border border-gray-200 dark:border-gray-700 p-3 bg-gray-50 dark:bg-gray-900/40"
                      >
                        <p className="text-xs uppercase tracking-[0.3em] text-gray-500 dark:text-gray-400">
                          {step.operator.replace(/_/g, ' ')}
                        </p>
                        <p className="text-sm font-semibold text-gray-900 dark:text-white">{step.conclusion}</p>
                        {step.premises.length > 0 && (
                          <ul className="mt-1 text-xs text-gray-500 dark:text-gray-400 list-disc list-inside">
                            {step.premises.map((premise) => (
                              <li key={premise}>{premise}</li>
                            ))}
                          </ul>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Run a reasoning query or select a trace to inspect the TRF details.
                </p>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  )
}
