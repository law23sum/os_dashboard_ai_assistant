import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { RefreshCw, ServerCog, Play, StopCircle, RotateCw, HardDrive, Activity } from 'lucide-react'
import apiClient, { apiPath } from '../lib/apiClient'
import { AIOSStatus } from '../types'
import { toast } from '../utils/toast'

const fetchStatus = async (): Promise<AIOSStatus> => {
  const { data } = await apiClient.get<AIOSStatus>(apiPath('ai/os/status'))
  return data
}

export default function AIOS() {
  const queryClient = useQueryClient()
  const statusQuery = useQuery({
    queryKey: ['ai-os-status'],
    queryFn: fetchStatus,
    refetchInterval: 30000,
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
      queryClient.invalidateQueries({ queryKey: ['ai-os-status'] })
    },
    onError: () => toast.error('Failed to update orchestrator'),
  })

  const refreshWorkflows = useMutation({
    mutationFn: async () => {
      await apiClient.post(apiPath('ai/os/workflows/refresh'), { seed: Date.now() })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ai-os-status'] })
      toast.info('Workflows refreshed')
    },
  })

  if (statusQuery.isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
      </div>
    )
  }

  if (statusQuery.error || !statusQuery.data) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded">
        Unable to load AI OS status. Start the backend API to continue.
      </div>
    )
  }

  const data = statusQuery.data
  const orchestratorUp = data.orchestrator.status === 'running'

  return (
    <div className="px-4 py-6 sm:px-0 space-y-6">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">AI OS</h2>
          <p className="text-gray-600 dark:text-gray-400">
            Distributed orchestrator shared by the desktop + browser builds
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => orchestratorMutation.mutate('start')}
            className="inline-flex items-center px-3 py-2 rounded-md border border-gray-300 dark:border-gray-600 text-sm text-gray-700 dark:text-gray-100 hover:bg-gray-50 dark:hover:bg-gray-700"
          >
            <Play className="w-4 h-4 mr-1" />
            Start
          </button>
          <button
            onClick={() => orchestratorMutation.mutate('stop')}
            className="inline-flex items-center px-3 py-2 rounded-md border border-gray-300 dark:border-gray-600 text-sm text-gray-700 dark:text-gray-100 hover:bg-gray-50 dark:hover:bg-gray-700"
          >
            <StopCircle className="w-4 h-4 mr-1" />
            Stop
          </button>
          <button
            onClick={() => orchestratorMutation.mutate('restart')}
            className="inline-flex items-center px-3 py-2 rounded-md bg-primary-600 text-white hover:bg-primary-700 text-sm"
          >
            <RotateCw className="w-4 h-4 mr-1" />
            Restart
          </button>
          <button
            onClick={() => statusQuery.refetch()}
            className="inline-flex items-center px-3 py-2 rounded-md border border-primary-200 text-primary-600 hover:bg-primary-50 text-sm"
          >
            <RefreshCw className="w-4 h-4 mr-1" />
            Refresh
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">Orchestrator</p>
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
                  {orchestratorUp ? 'Running' : 'Stopped'}
                </h3>
              </div>
              <ServerCog
                className={`w-10 h-10 ${
                  orchestratorUp ? 'text-green-500' : 'text-gray-400 dark:text-gray-600'
                }`}
              />
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-gray-500 dark:text-gray-400">Version</p>
                <p className="text-gray-900 dark:text-white">{data.orchestrator.version}</p>
              </div>
              <div>
                <p className="text-gray-500 dark:text-gray-400">Workflows Active</p>
                <p className="text-gray-900 dark:text-white">
                  {data.orchestrator.workflows_active}
                </p>
              </div>
              <div>
                <p className="text-gray-500 dark:text-gray-400">Nodes Online</p>
                <p className="text-gray-900 dark:text-white">{data.orchestrator.nodes_online}</p>
              </div>
              <div>
                <p className="text-gray-500 dark:text-gray-400">Last Started</p>
                <p className="text-gray-900 dark:text-white">
                  {data.orchestrator.last_started
                    ? new Date(data.orchestrator.last_started).toLocaleString()
                    : '—'}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                  Active Workflows
                </h3>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Synchronized queue powering cross-platform UI
                </p>
              </div>
              <button
                onClick={() => refreshWorkflows.mutate()}
                className="inline-flex items-center px-3 py-2 rounded-md border border-gray-300 dark:border-gray-600 text-sm text-gray-700 dark:text-gray-100 hover:bg-gray-50 dark:hover:bg-gray-700"
              >
                <RefreshCw className="w-4 h-4 mr-1" />
                Shuffle
              </button>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700 text-sm">
                <thead className="bg-gray-50 dark:bg-gray-700">
                  <tr>
                    <th className="px-4 py-2 text-left font-medium text-gray-500 dark:text-gray-300">
                      Workflow
                    </th>
                    <th className="px-4 py-2 text-left font-medium text-gray-500 dark:text-gray-300">
                      Owner
                    </th>
                    <th className="px-4 py-2 text-left font-medium text-gray-500 dark:text-gray-300">
                      Status
                    </th>
                    <th className="px-4 py-2 text-left font-medium text-gray-500 dark:text-gray-300">
                      Progress
                    </th>
                    <th className="px-4 py-2 text-left font-medium text-gray-500 dark:text-gray-300">
                      ETA
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                  {data.workflows.map((workflow) => (
                    <tr key={workflow.id}>
                      <td className="px-4 py-3 text-gray-900 dark:text-white">{workflow.name}</td>
                      <td className="px-4 py-3 text-gray-600 dark:text-gray-300">{workflow.owner}</td>
                      <td className="px-4 py-3">
                        <span
                          className={`px-2 py-0.5 rounded-full text-xs font-semibold ${
                            workflow.status === 'running'
                              ? 'bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-200'
                              : workflow.status === 'queued'
                                ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/40 dark:text-yellow-200'
                                : 'bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-200'
                          }`}
                        >
                          {workflow.status}
                        </span>
                      </td>
                      <td className="px-4 py-3 w-48">
                        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                          <div
                            className="bg-primary-500 h-2 rounded-full"
                            style={{ width: `${workflow.progress}%` }}
                          ></div>
                        </div>
                      </td>
                      <td className="px-4 py-3 text-gray-600 dark:text-gray-300">
                        {workflow.eta_minutes ? `${workflow.eta_minutes}m` : '—'}
                      </td>
                    </tr>
                  ))}
                  {data.workflows.length === 0 && (
                    <tr>
                      <td
                        colSpan={5}
                        className="px-4 py-6 text-center text-gray-500 dark:text-gray-400"
                      >
                        No workflows active
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div className="space-y-6">
          <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Storage</h3>
              <HardDrive className="w-5 h-5 text-primary-500" />
            </div>
            <div className="space-y-3 text-sm">
              <div className="flex items-center justify-between">
                <span className="text-gray-500 dark:text-gray-400">Documents</span>
                <span className="text-gray-900 dark:text-white">{data.storage.documents_indexed}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-500 dark:text-gray-400">Embeddings</span>
                <span className="text-gray-900 dark:text-white">{data.storage.vector_embeddings}</span>
              </div>
              <div>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-gray-500 dark:text-gray-400">Disk Usage</span>
                  <span className="text-gray-900 dark:text-white">
                    {data.storage.disk_used_gb} / {data.storage.disk_total_gb} GB
                  </span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div
                    className="bg-primary-500 h-2 rounded-full"
                    style={{
                      width: `${Math.min(
                        100,
                        (data.storage.disk_used_gb / data.storage.disk_total_gb) * 100,
                      )}%`,
                    }}
                  ></div>
                </div>
              </div>
              <div className="text-gray-500 dark:text-gray-400">
                Last backup:{' '}
                {data.storage.last_backup
                  ? new Date(data.storage.last_backup).toLocaleString()
                  : '—'}
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Edge Nodes</h3>
              <Activity className="w-5 h-5 text-primary-500" />
            </div>
            <div className="space-y-4">
              {data.nodes.map((node) => (
                <div key={node.id} className="border border-gray-200 dark:border-gray-700 rounded-md p-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-900 dark:text-white">{node.id}</p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">{node.location}</p>
                    </div>
                    <span
                      className={`px-2 py-0.5 rounded-full text-xs font-semibold ${
                        node.status === 'online'
                          ? 'bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-200'
                          : node.status === 'maintenance'
                            ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/40 dark:text-yellow-200'
                            : 'bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-200'
                      }`}
                    >
                      {node.status}
                    </span>
                  </div>
                  <div className="mt-3">
                    <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400 mb-1">
                      <span>Load</span>
                      <span>{node.load_percent}%</span>
                    </div>
                    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1.5">
                      <div
                        className="bg-primary-500 h-1.5 rounded-full"
                        style={{ width: `${node.load_percent}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
