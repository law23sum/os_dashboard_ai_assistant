import { useEffect, useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { Cloud, Zap, Satellite, RefreshCw, Layers, Cpu, ServerCog } from 'lucide-react'
import apiClient, { apiPath } from '../lib/apiClient'
import { toast } from '../utils/toast'
import { EdgeComputingStatus, EdgeModel } from '../types'

export default function EdgeComputing() {
  const [selectedNode, setSelectedNode] = useState<string | undefined>()
  const [nodeAction, setNodeAction] = useState<'start' | 'stop' | 'restart' | 'maintenance'>('restart')
  const [deployResult, setDeployResult] = useState<string | null>(null)
  const [optimizeResult, setOptimizeResult] = useState<string | null>(null)

  const statusQuery = useQuery({
    queryKey: ['edge-status'],
    queryFn: async () => {
      const response = await apiClient.get<EdgeComputingStatus>(apiPath('edge-computing/status'))
      return response.data
    },
    refetchInterval: 12000,
  })

  const modelsQuery = useQuery({
    queryKey: ['edge-models'],
    queryFn: async () => {
      const response = await apiClient.get<EdgeModel[]>(apiPath('edge-computing/models'))
      return response.data
    },
  })

  useEffect(() => {
    if (!selectedNode && statusQuery.data?.nodes.length) {
      setSelectedNode(statusQuery.data.nodes[0].id)
    }
  }, [statusQuery.data, selectedNode])

  const deployMutation = useMutation({
    mutationFn: () =>
      apiClient.post(apiPath('edge-computing/deploy'), {
        model_id: 'model-automation',
        target_nodes: statusQuery.data?.nodes.slice(0, 3).map((n) => n.id) ?? [],
        strategy: statusQuery.data?.available_strategies[0] ?? 'Round Robin',
        priority: 'high',
      }),
    onSuccess: (payload) => {
      toast.success(payload.data?.message ?? 'Model deployment scheduled')
      setDeployResult(JSON.stringify(payload.data || payload, null, 2))
      statusQuery.refetch()
    },
    onError: () => toast.error('Model deployment failed'),
  })

  const manageMutation = useMutation({
    mutationFn: () =>
      apiClient.post(apiPath('edge-computing/node/manage'), {
        node_id: selectedNode,
        action: nodeAction,
      }),
    onSuccess: (payload) => {
      toast.success(payload.data?.message ?? 'Node updated')
      statusQuery.refetch()
    },
    onError: () => toast.error('Node management failed'),
  })

  const optimizeMutation = useMutation({
    mutationFn: () =>
      apiClient.post(apiPath('edge-computing/models/optimize'), {
        type: 'latency',
        target_improvement: 0.12,
      }),
    onSuccess: (payload) => {
      toast.success(payload.data?.message ?? 'Optimization complete')
      setOptimizeResult(JSON.stringify(payload.data || payload, null, 2))
    },
    onError: () => toast.error('Optimization failed'),
  })

  const status = statusQuery.data

  return (
    <div className="px-4 py-6 sm:px-0 space-y-6">
      <header className="glass-panel p-6 border border-[color:var(--osd-border)]">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.5em] text-[color:var(--osd-muted)]">Distributed AI</p>
            <h1 className="text-3xl font-semibold flex items-center gap-3 text-[color:var(--osd-text)]">
              <Cloud className="w-8 h-8 text-[color:var(--osd-accent)]" />
              Edge Computing & Distributed AI
            </h1>
            <p className="mt-2 text-sm text-[color:var(--osd-muted)] max-w-3xl">
              Monitor every node, deploy AI models, and optimize latency across globally distributed hardware.
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => deployMutation.mutate()}
              disabled={deployMutation.isPending}
              className="btn-tonal bg-[color:var(--osd-accent)] text-white hover:bg-[color:var(--osd-accentHover)]"
            >
              <Zap className="w-4 h-4" />
              Deploy Model
            </button>
            <button
              onClick={() => optimizeMutation.mutate()}
              disabled={optimizeMutation.isPending}
              className="btn-tonal border border-[color:var(--osd-border)] text-[color:var(--osd-text)]"
            >
              <Layers className="w-4 h-4" />
              Optimize
            </button>
            <button
              onClick={() => statusQuery.refetch()}
              className="btn-tonal border border-[color:var(--osd-border)] text-[color:var(--osd-text)]"
            >
              <RefreshCw className="w-4 h-4" />
              Refresh
            </button>
          </div>
        </div>
      </header>

      <section className="grid gap-4 md:grid-cols-3">
        <Metric label="Total nodes" value={`${status?.metrics.total_nodes ?? 0}`} />
        <Metric label="Active nodes" value={`${status?.metrics.active_nodes ?? 0}`} />
        <Metric label="Average latency" value={`${status?.metrics.average_latency ?? 0}`} suffix=" ms" />
      </section>

      <section className="grid gap-6 lg:grid-cols-[1.3fr,0.7fr]">
        <div className="glass-panel p-6 border border-[color:var(--osd-border)] space-y-5">
          <div className="flex items-center gap-2">
            <ServerCog className="w-5 h-5 text-[color:var(--osd-accent)]" />
            <h2 className="text-lg font-semibold text-[color:var(--osd-text)]">Edge Nodes</h2>
          </div>
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {status?.nodes.map((node) => (
              <div key={node.id} className="flex flex-col gap-2 rounded-xl border border-[color:var(--osd-border)] bg-[color:var(--osd-surfaceAlt)] p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-semibold text-[color:var(--osd-text)]">{node.location}</p>
                    <p className="text-xs text-[color:var(--osd-muted)]">Node ID · {node.id}</p>
                  </div>
                  <span className="glass-pill text-[color:var(--osd-text)]">
                    {node.status.toUpperCase()}
                  </span>
                </div>
                <div className="flex items-center justify-between text-xs text-[color:var(--osd-muted)]">
                  <span>Load {node.load_percent}%</span>
                  <span>Models {node.model_count}</span>
                  <span>Heartbeat {new Date(node.last_heartbeat).toLocaleTimeString()}</span>
                </div>
              </div>
            ))}
          </div>
          <div className="grid gap-3 text-sm text-[color:var(--osd-muted)]">
            <label className="space-y-1">
              Node
              <select
                value={selectedNode}
                onChange={(e) => setSelectedNode(e.target.value)}
                className="w-full rounded-xl bg-[color:var(--osd-surfaceAlt)] border border-[color:var(--osd-border)] px-3 py-2 text-[color:var(--osd-text)] focus:border-[color:var(--osd-accent)] focus:outline-none"
              >
                {status?.nodes.map((node) => (
                  <option key={node.id} value={node.id}>
                    {node.location}
                  </option>
                ))}
              </select>
            </label>
            <label className="space-y-1">
              Action
              <select
                value={nodeAction}
                onChange={(e) => setNodeAction(e.target.value as typeof nodeAction)}
                className="w-full rounded-xl bg-[color:var(--osd-surfaceAlt)] border border-[color:var(--osd-border)] px-3 py-2 text-[color:var(--osd-text)] focus:border-[color:var(--osd-accent)] focus:outline-none"
              >
                <option value="start">Start</option>
                <option value="stop">Stop</option>
                <option value="restart">Restart</option>
                <option value="maintenance">Maintenance</option>
              </select>
            </label>
            <button
              onClick={() => manageMutation.mutate()}
              disabled={!selectedNode || manageMutation.isPending}
              className="btn-tonal border border-[color:var(--osd-border)] text-[color:var(--osd-text)]"
            >
              Manage Node
            </button>
          </div>
        </div>
        <div className="glass-panel p-6 border border-[color:var(--osd-border)] space-y-5">
          <div className="flex items-center gap-2">
            <Satellite className="w-5 h-5 text-[color:var(--osd-accent)]" />
            <h2 className="text-lg font-semibold text-[color:var(--osd-text)]">Models</h2>
          </div>
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {modelsQuery.data?.slice(0, 5).map((model) => (
              <div
                key={model.id}
                className="rounded-xl border border-[color:var(--osd-border)] bg-[color:var(--osd-surfaceAlt)] p-3 text-sm text-[color:var(--osd-muted)]"
              >
                <div className="flex items-center justify-between">
                  <p className="font-semibold text-[color:var(--osd-text)]">{model.name}</p>
                  <span className="text-xs">{model.type}</span>
                </div>
                <p>Accuracy {model.accuracy.toFixed(3)} · Latency {model.latency_ms}ms</p>
              </div>
            ))}
          </div>
          {deployResult && (
            <pre className="rounded-xl bg-[color:var(--osd-surfaceAlt)] border border-[color:var(--osd-border)] p-3 text-xs text-[color:var(--osd-muted)] font-mono overflow-auto max-h-40">
              {deployResult}
            </pre>
          )}
          {optimizeResult && (
            <pre className="rounded-xl bg-[color:var(--osd-surfaceAlt)] border border-[color:var(--osd-border)] p-3 text-xs text-[color:var(--osd-muted)] font-mono overflow-auto max-h-40">
              {optimizeResult}
            </pre>
          )}
        </div>
      </section>

      <section className="glass-panel p-6 border border-[color:var(--osd-border)] space-y-4">
        <h2 className="text-lg font-semibold text-[color:var(--osd-text)]">Recent Deployments</h2>
        <div className="space-y-3">
          {status?.recent_deployments?.map((deployment) => (
            <div key={deployment.model_id} className="flex items-center justify-between rounded-xl border border-[color:var(--osd-border)] bg-[color:var(--osd-surfaceAlt)] p-3 text-sm text-[color:var(--osd-muted)]">
              <div>
                <p className="font-semibold text-[color:var(--osd-text)]">{deployment.model_name}</p>
                <p>
                  Nodes targeted: {deployment.target_nodes} · Status {deployment.status}
                </p>
              </div>
              <span className="text-xs">{new Date(deployment.deployed_at).toLocaleString()}</span>
            </div>
          ))}
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
