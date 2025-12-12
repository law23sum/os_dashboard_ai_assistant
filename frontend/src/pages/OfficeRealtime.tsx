import { useEffect, useMemo, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import {
  Activity,
  AlertCircle,
  Code,
  FileCode,
  FileText,
  RefreshCw,
  Send,
  Server,
  Terminal,
  Users,
} from 'lucide-react'
import apiClient, { apiPath } from '../lib/apiClient'
import type { OfficeRealtimeClient, OfficeRealtimeSummary } from '../types'
import { toast } from '../utils/toast'

const fetchRealtimeSummary = async (): Promise<OfficeRealtimeSummary> => {
  const { data } = await apiClient.get<OfficeRealtimeSummary>(apiPath('office/realtime/summary'))
  return data
}

type OfficeOperation = 'analyze' | 'generate' | 'suggest'

interface TriggerPayload {
  operation: OfficeOperation
  client_id?: string
  target?: string
  payload?: Record<string, any>
}

const triggerOfficeJob = async (payload: TriggerPayload) => {
  const body = {
    operation: payload.operation,
    client_id: payload.client_id,
    target: payload.target,
    payload: payload.payload,
  }
  const { data } = await apiClient.post(apiPath('office/realtime/ai'), body)
  return data
}

export default function OfficeRealtime() {
  const queryClient = useQueryClient()
  const { data, isLoading, isFetching, refetch } = useQuery({
    queryKey: ['office-realtime-summary'],
    queryFn: fetchRealtimeSummary,
    refetchInterval: 45000,
  })

  const [operation, setOperation] = useState<OfficeOperation>('analyze')
  const [clientId, setClientId] = useState<string | undefined>()
  const [targetApp, setTargetApp] = useState('word')
  const [prompt, setPrompt] = useState('')

  useEffect(() => {
    if (!clientId && data?.clients?.length) {
      setClientId(data.clients[0].client_id)
    }
  }, [clientId, data?.clients])

  const triggerMutation = useMutation({
    mutationFn: triggerOfficeJob,
    onSuccess: (response) => {
      toast.success('AI job queued successfully')
      queryClient.invalidateQueries({ queryKey: ['office-realtime-summary'] })
      if (response?.metrics?.duration_ms) {
        const ms = response.metrics.duration_ms.toFixed(0)
        toast.info(`Completed in ${ms} ms`)
      }
    },
    onError: (error) => {
      toast.error(error instanceof Error ? error.message : 'Failed to trigger AI action')
    },
  })

  const participantCount = data?.clients?.length ?? 0
  const documentCount = data?.documents?.length ?? 0
  const pendingJobs = data?.ai_metrics?.pending_jobs ?? 0
  const queueDepth = data?.ai_metrics?.queue_depth ?? 0

  const selectedClient = useMemo(() => {
    if (!clientId || !data) return undefined
    return data.clients.find((client) => client.client_id === clientId)
  }, [clientId, data])

  const handleTrigger = () => {
    if (!clientId) {
      toast.error('Select a client before triggering AI')
      return
    }
    triggerMutation.mutate({
      operation,
      client_id: clientId,
      target: targetApp || undefined,
      payload: prompt ? { prompt } : {},
    })
  }

  if (isLoading || !data) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500" />
      </div>
    )
  }

  const { documents, clients, docs_links, manifest_preview, governance } = data
  const jobs = data.recent_jobs ?? []

  const lastResultSummary = useMemo(() => {
    const payload = triggerMutation.data?.result
    if (!payload) return 'Job acknowledged by realtime router'
    if (typeof payload === 'string') {
      return payload
    }
    if (payload.result) {
      if (typeof payload.result === 'string') {
        return payload.result
      }
      if (typeof payload.result === 'object' && payload.result.status) {
        return payload.result.status
      }
    }
    if (payload.status) {
      return payload.status
    }
    try {
      return JSON.stringify(payload).slice(0, 200)
    } catch {
      return 'Job completed'
    }
  }, [triggerMutation.data])

  return (
    <div className="px-4 py-6 sm:px-0 space-y-6">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.35em] text-gray-500 dark:text-gray-400">Office Mesh</p>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Realtime Office Fabric</h2>
          <p className="text-gray-600 dark:text-gray-400">
            Mirrors the Tkinter AI Office agent: live sessions, AI queue telemetry, and manifest preview.
          </p>
        </div>
        <div className="flex items-center gap-3">
          {isFetching && <span className="text-xs text-gray-500">Refreshing…</span>}
          <button
            onClick={() => refetch()}
            className="inline-flex items-center px-4 py-2 rounded-md bg-primary-600 text-white text-sm font-medium hover:bg-primary-700"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </button>
        </div>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard icon={Users} label="Connected Clients" value={participantCount} accent="text-sky-500" />
        <MetricCard icon={FileText} label="Active Documents" value={documentCount} accent="text-emerald-500" />
        <MetricCard icon={Activity} label="Pending Jobs" value={pendingJobs} accent="text-amber-500" />
        <MetricCard icon={Server} label="AI Queue Depth" value={queueDepth} accent="text-purple-500" />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <div className="xl:col-span-2 space-y-4">
          <section className="border border-gray-200 dark:border-gray-700 rounded-2xl bg-white dark:bg-gray-900/70 p-4">
            <header className="flex items-center justify-between mb-4">
              <div>
                <p className="text-xs uppercase tracking-[0.3em] text-gray-500 dark:text-gray-400">Documents</p>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Live Collaboration Decks</h3>
              </div>
            </header>
            <div className="grid sm:grid-cols-2 gap-4">
              {documents.map((doc) => (
                <div key={doc.document_id} className="border border-gray-200 dark:border-gray-700 rounded-xl p-4 space-y-3">
                  <div>
                    <p className="text-xs text-gray-500 dark:text-gray-400">{doc.document_id}</p>
                    <h4 className="text-lg font-semibold text-gray-900 dark:text-white">{doc.title}</h4>
                    {doc.summary && <p className="text-sm text-gray-600 dark:text-gray-400">{doc.summary}</p>}
                  </div>
                  <div>
                    <p className="text-xs uppercase text-gray-500 tracking-[0.2em]">Participants</p>
                    <div className="mt-2 flex flex-wrap gap-2">
                      {doc.participants.map((participant) => (
                        <ParticipantBadge key={participant.client_id} client={participant} />
                      ))}
                    </div>
                  </div>
                </div>
              ))}
              {!documents.length && (
                <div className="col-span-full text-sm text-gray-500 dark:text-gray-400">
                  No active documents yet. Use the AI trigger to kick off a session.
                </div>
              )}
            </div>
          </section>

          <section className="border border-gray-200 dark:border-gray-700 rounded-2xl bg-white dark:bg-gray-900/70 p-4 space-y-4">
            <header className="flex items-center justify-between">
              <div>
                <p className="text-xs uppercase tracking-[0.3em] text-gray-500 dark:text-gray-400">AI Control</p>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Trigger Office AI</h3>
              </div>
              {triggerMutation.isLoading && <span className="text-xs text-gray-500">Dispatching…</span>}
            </header>
            <div className="grid md:grid-cols-3 gap-3">
              <div className="space-y-1">
                <label className="text-xs uppercase text-gray-500">Operation</label>
                <select
                  className="w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-transparent px-3 py-2 text-sm"
                  value={operation}
                  onChange={(event) => setOperation(event.target.value as OfficeOperation)}
                >
                  <option value="analyze">Analyze content</option>
                  <option value="generate">Generate content</option>
                  <option value="suggest">Suggest fixes</option>
                </select>
              </div>
              <div className="space-y-1">
                <label className="text-xs uppercase text-gray-500">Client</label>
                <select
                  className="w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-transparent px-3 py-2 text-sm"
                  value={clientId}
                  onChange={(event) => setClientId(event.target.value)}
                >
                  {clients.map((client) => (
                    <option key={client.client_id} value={client.client_id}>
                      {client.application} · {client.user_id || client.client_id}
                    </option>
                  ))}
                </select>
              </div>
              <div className="space-y-1">
                <label className="text-xs uppercase text-gray-500">Target</label>
                <select
                  className="w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-transparent px-3 py-2 text-sm"
                  value={targetApp}
                  onChange={(event) => setTargetApp(event.target.value)}
                >
                  <option value="word">Word</option>
                  <option value="powerpoint">PowerPoint</option>
                  <option value="excel">Excel</option>
                  <option value="onenote">OneNote</option>
                  <option value="web_dashboard">Web Dashboard</option>
                </select>
              </div>
            </div>
            <div className="space-y-2">
              <label className="text-xs uppercase text-gray-500">Prompt / Context</label>
              <textarea
                className="w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-transparent px-3 py-2 text-sm min-h-[100px]"
                value={prompt}
                onChange={(event) => setPrompt(event.target.value)}
                placeholder="Describe the update or analysis you want the AI copilot to perform…"
              />
            </div>
            {selectedClient && (
              <div className="border border-dashed border-gray-300 dark:border-gray-700 rounded-lg p-3 text-xs text-gray-600 dark:text-gray-400 flex items-start gap-2">
                <AlertCircle className="w-4 h-4 mt-0.5 text-amber-500" />
                <div>
                  <p>
                    Routing via <strong>{selectedClient.application}</strong> session{' '}
                    <code className="bg-gray-100 dark:bg-gray-800 px-1 rounded">{selectedClient.session_id}</code>. Live
                    participants: {selectedClient.capabilities.join(', ') || 'standard AI assists'}.
                  </p>
                </div>
              </div>
            )}
            <button
              onClick={handleTrigger}
              disabled={triggerMutation.isLoading}
              className="inline-flex items-center justify-center w-full sm:w-auto px-5 py-2 rounded-lg bg-primary-600 text-white text-sm font-medium hover:bg-primary-700 disabled:opacity-60"
            >
              <Send className="w-4 h-4 mr-2" />
              Send to AI Copilot
            </button>
            {triggerMutation.data && (
              <div className="text-sm text-gray-600 dark:text-gray-400 border border-gray-200 dark:border-gray-800 rounded-lg p-3">
                <p className="font-semibold text-gray-900 dark:text-white">Last Result</p>
                <p className="mt-1">{lastResultSummary}</p>
              </div>
            )}
          </section>

          <section className="border border-gray-200 dark:border-gray-700 rounded-2xl bg-white dark:bg-gray-900/70 p-4">
            <header className="flex items-center justify-between mb-3">
              <div>
                <p className="text-xs uppercase tracking-[0.3em] text-gray-500 dark:text-gray-400">Jobs</p>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Recent AI Activity</h3>
              </div>
            </header>
            <div className="overflow-x-auto">
              <table className="min-w-full text-sm">
                <thead>
                  <tr className="text-left text-xs uppercase tracking-[0.2em] text-gray-500 dark:text-gray-400">
                    <th className="py-2 pr-4">Job</th>
                    <th className="py-2 pr-4">Client</th>
                    <th className="py-2 pr-4">Operation</th>
                    <th className="py-2 pr-4">Status</th>
                    <th className="py-2 pr-4 text-right">Duration</th>
                  </tr>
                </thead>
                <tbody>
                  {jobs.map((job) => (
                    <tr key={job.job_id} className="border-t border-gray-200 dark:border-gray-800">
                      <td className="py-2 pr-4 font-mono text-xs">{job.job_id.split('-')[0]}</td>
                      <td className="py-2 pr-4">{job.client_id}</td>
                      <td className="py-2 pr-4">{job.message_type.replace(/ai_|_request/gi, '')}</td>
                      <td className="py-2 pr-4">
                        <span
                          className={`px-2 py-1 text-xs rounded ${
                            job.success
                              ? 'bg-emerald-500/10 text-emerald-600'
                              : 'bg-rose-500/10 text-rose-600'
                          }`}
                        >
                          {job.status}
                        </span>
                      </td>
                      <td className="py-2 pr-4 text-right">{job.duration_ms.toFixed(0)} ms</td>
                    </tr>
                  ))}
                  {!jobs.length && (
                    <tr>
                      <td colSpan={5} className="py-4 text-center text-gray-500">
                        No AI jobs yet.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </section>
        </div>

        <div className="space-y-4">
          <section className="border border-gray-200 dark:border-gray-700 rounded-2xl bg-white dark:bg-gray-900/70 p-4 space-y-3">
            <header>
              <p className="text-xs uppercase tracking-[0.3em] text-gray-500 dark:text-gray-400">Manifest</p>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                <FileCode className="w-4 h-4" /> Office Add-in Preview
              </h3>
            </header>
            <pre className="text-xs overflow-auto bg-gray-900 text-green-200 rounded-lg p-3 leading-relaxed max-h-72">
              {manifest_preview}
            </pre>
            <div className="text-xs text-gray-500 flex items-center gap-2">
              <Code className="w-4 h-4" /> Served via `/docs/AI_OFFICE_AGENT_REALTIME.md`
            </div>
          </section>

          <section className="border border-gray-200 dark:border-gray-700 rounded-2xl bg-white dark:bg-gray-900/70 p-4 space-y-3">
            <header>
              <p className="text-xs uppercase tracking-[0.3em] text-gray-500 dark:text-gray-400">Docs</p>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                <FileText className="w-4 h-4" /> Reference Links
              </h3>
            </header>
            <ul className="space-y-2">
              {docs_links.map((link) => (
                <li key={link.href} className="text-sm">
                  <a
                    className="text-primary-600 dark:text-primary-400 hover:underline"
                    href={link.href}
                    target="_blank"
                    rel="noreferrer"
                  >
                    {link.label}
                  </a>
                  {link.description && (
                    <p className="text-xs text-gray-500 dark:text-gray-400">{link.description}</p>
                  )}
                </li>
              ))}
            </ul>
          </section>

          <section className="border border-gray-200 dark:border-gray-700 rounded-2xl bg-white dark:bg-gray-900/70 p-4 space-y-3">
            <header>
              <p className="text-xs uppercase tracking-[0.3em] text-gray-500 dark:text-gray-400">Governance</p>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                <Terminal className="w-4 h-4" /> Control Room
              </h3>
            </header>
            <div className="text-sm text-gray-700 dark:text-gray-300 space-y-2">
              {Object.entries(governance || {}).map(([key, value]) => (
                <div key={key}>
                  <p className="text-xs uppercase tracking-[0.35em] text-gray-500">{key}</p>
                  <p>{value}</p>
                </div>
              ))}
            </div>
          </section>

          <section className="border border-gray-200 dark:border-gray-700 rounded-2xl bg-white dark:bg-gray-900/70 p-4 space-y-3">
            <header>
              <p className="text-xs uppercase tracking-[0.3em] text-gray-500 dark:text-gray-400">Clients</p>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                <Users className="w-4 h-4" /> Connected Sessions
              </h3>
            </header>
            <div className="space-y-3">
              {clients.map((client) => (
                <div key={client.client_id} className="text-sm border border-gray-200 dark:border-gray-800 rounded-lg p-3">
                  <p className="font-semibold text-gray-900 dark:text-white">{client.application}</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">{client.user_id || client.client_id}</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Document: {client.document_id || '—'}</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Capabilities: {client.capabilities.join(', ') || 'standard'}</p>
                </div>
              ))}
            </div>
          </section>
        </div>
      </div>
    </div>
  )
}

function ParticipantBadge({ client }: { client: OfficeRealtimeClient }) {
  return (
    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-primary-500/10 text-primary-600 dark:text-primary-300">
      {client.application}
    </span>
  )
}

interface MetricCardProps {
  icon: React.ComponentType<{ className?: string }>
  label: string
  value: number
  accent: string
}

function MetricCard({ icon: Icon, label, value, accent }: MetricCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900/70 p-4">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs text-gray-500 dark:text-gray-400">{label}</p>
          <p className={`text-2xl font-semibold ${accent}`}>{value}</p>
        </div>
        <Icon className={`w-6 h-6 ${accent}`} />
      </div>
    </div>
  )
}
