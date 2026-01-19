import { useEffect, useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { Workflow, Play, RefreshCw, FileCode, Zap } from 'lucide-react'
import apiClient, { apiPath } from '../lib/apiClient'
import { toast } from '../utils/toast'
import { WorkflowOrchestratorStatus, WorkflowMonitorResponse } from '../types'

export default function Workflows() {
  const [monitorResult, setMonitorResult] = useState<string | null>(null)
  const [selectedWorkflow, setSelectedWorkflow] = useState<string | null>(null)

  const statusQuery = useQuery({
    queryKey: ['workflow-status'],
    queryFn: async () => {
      const response = await apiClient.get<WorkflowOrchestratorStatus>(apiPath('workflows/status'))
      return response.data
    },
    refetchInterval: 9000,
  })

  const startMutation = useMutation({
    mutationFn: () => apiClient.post(apiPath('workflows/orchestrator/start'), {}),
    onSuccess: (payload) => {
      toast.success(payload.data?.message ?? 'Orchestrator activated')
      statusQuery.refetch()
    },
    onError: () => toast.error('Failed to start orchestrator'),
  })

  const monitorMutation = useMutation({
    mutationFn: (workflowId: string) =>
      apiClient.post<WorkflowMonitorResponse>(apiPath('workflows/monitor'), {
        workflow_id: workflowId,
      }),
    onSuccess: (payload) => {
      toast.success('Workflow monitored')
      setMonitorResult(JSON.stringify(payload.data || payload, null, 2))
    },
    onError: () => toast.error('Monitoring failed'),
  })

  const status = statusQuery.data
  const active = status?.active_workflows ?? []

  useEffect(() => {
    if (active.length && !selectedWorkflow) {
      setSelectedWorkflow(active[0].id)
    }
  }, [active, selectedWorkflow])

  return (
    <div className="space-y-6 px-4 py-6 sm:px-0">
      <header className="glass-panel border border-[color:var(--osd-border)] p-6">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.5em] text-[color:var(--osd-muted)]">Workflow Orchestration</p>
            <h1 className="flex items-center gap-3 text-3xl font-semibold text-[color:var(--osd-text)]">
              <Workflow className="h-8 w-8 text-[color:var(--osd-accent)]" />
              Workflow Coordinator
            </h1>
            <p className="mt-2 max-w-3xl text-sm text-[color:var(--osd-muted)]">
              AI-native workflows and capsules keep automation consistent whether you launch from desktop or the web.
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => startMutation.mutate()}
              disabled={startMutation.isPending}
              className="btn-tonal bg-[color:var(--osd-accent)] text-white hover:bg-[color:var(--osd-accentHover)] disabled:opacity-60"
            >
              <Play className="h-4 w-4" />
              Start Orchestrator
            </button>
            <button
              onClick={() => statusQuery.refetch()}
              className="btn-tonal border border-[color:var(--osd-border)] text-[color:var(--osd-text)]"
            >
              <RefreshCw className="h-4 w-4" />
              Refresh
            </button>
          </div>
        </div>
      </header>

      <section className="grid gap-4 md:grid-cols-4">
        <Metric label="Active workflows" value={`${status?.metrics.active_workflows ?? 0}`} />
        <Metric label="Completed today" value={`${status?.metrics.completed_today ?? 0}`} />
        <Metric label="Success rate" value={`${(status?.metrics.success_rate ?? 0).toFixed(2)}`} suffix=" %" />
        <Metric label="Queue length" value={`${status?.metrics.queue_length ?? 0}`} />
      </section>

      <section className="glass-panel space-y-4 border border-[color:var(--osd-border)] p-6">
        <div className="flex items-center gap-2">
          <Zap className="h-5 w-5 text-[color:var(--osd-accent)]" />
          <h2 className="text-lg font-semibold text-[color:var(--osd-text)]">Active Workflows</h2>
        </div>
        <div className="space-y-4">
          {active.length ? (
            active.map((workflow) => (
              <div
                key={workflow.id}
                className="grid gap-2 rounded-xl border border-[color:var(--osd-border)] bg-[color:var(--osd-surfaceAlt)] p-4"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-semibold text-[color:var(--osd-text)]">{workflow.name}</p>
                    <p className="text-xs text-[color:var(--osd-muted)]">
                      Owner {workflow.owner} · Priority {workflow.priority}
                    </p>
                  </div>
                  <span className="glass-pill text-[color:var(--osd-text)]">{workflow.status}</span>
                </div>
                <div className="flex items-center justify-between text-xs text-[color:var(--osd-muted)]">
                  <span>{workflow.progress_percent}% progress</span>
                  <span>{workflow.current_step}</span>
                  <span>{workflow.estimated_completion ?? 'ETA unknown'}</span>
                </div>
                <div className="h-2 w-full rounded-full bg-[color:var(--osd-border)]">
                  <div
                    className="h-full rounded-full bg-[color:var(--osd-accent)]"
                    style={{ width: `${workflow.progress_percent}%` }}
                  />
                </div>
                <div className="flex flex-wrap items-center gap-2 text-xs text-[color:var(--osd-muted)]">
                  <button
                    onClick={() => monitorMutation.mutate(workflow.id)}
                    className="text-[color:var(--osd-accent)] hover:text-[color:var(--osd-accentHover)]"
                  >
                    Monitor
                  </button>
                </div>
              </div>
            ))
          ) : (
            <p className="text-sm text-[color:var(--osd-muted)]">No workflows currently running.</p>
          )}
        </div>
      </section>

      <section className="grid gap-4 lg:grid-cols-[0.7fr,1.3fr]">
        <div className="glass-panel space-y-4 border border-[color:var(--osd-border)] p-6">
          <div className="flex items-center gap-2">
            <FileCode className="h-5 w-5 text-[color:var(--osd-accent)]" />
            <h2 className="text-lg font-semibold text-[color:var(--osd-text)]">Templates</h2>
          </div>
          <div className="space-y-3 text-sm text-[color:var(--osd-muted)]">
            {status?.available_templates?.map((template) => (
              <div
                key={template.id}
                className="rounded-xl border border-[color:var(--osd-border)] bg-[color:var(--osd-surfaceAlt)] p-3"
              >
                <p className="font-semibold text-[color:var(--osd-text)]">{template.name}</p>
                <p>{template.description}</p>
                <p className="text-xs text-[color:var(--osd-muted)]">
                  Duration {template.estimated_duration}m · Success {(template.success_rate * 100).toFixed(1)}%
                </p>
              </div>
            ))}
            {!status?.available_templates?.length && (
              <p className="text-xs text-[color:var(--osd-muted)]">No templates published yet.</p>
            )}
          </div>
        </div>
        <div className="glass-panel space-y-4 border border-[color:var(--osd-border)] p-6">
          <div className="flex items-center gap-2">
            <Zap className="h-5 w-5 text-[color:var(--osd-accent)]" />
            <h2 className="text-lg font-semibold text-[color:var(--osd-text)]">Monitor Output</h2>
          </div>
          <pre className="max-h-72 overflow-auto rounded-xl border border-[color:var(--osd-border)] bg-[color:var(--osd-surfaceAlt)] p-3 font-mono text-xs text-[color:var(--osd-muted)]">
            {monitorResult ?? 'Invoke monitor on a workflow to stream detailed logs.'}
          </pre>
        </div>
      </section>
    </div>
  )
}

function Metric({ label, value, suffix = '' }: { label: string; value: string; suffix?: string }) {
  return (
    <div className="rounded-xl border border-[color:var(--osd-border)] bg-[color:var(--osd-surfaceAlt)] p-4">
      <p className="text-xs text-[color:var(--osd-muted)]">{label}</p>
      <p className="text-2xl font-semibold text-[color:var(--osd-text)]">
        {value}
        {suffix && <span className="text-sm font-medium text-[color:var(--osd-muted)]">{suffix}</span>}
      </p>
    </div>
  )
}