import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Brain, Sparkles, GaugeCircle, Zap, RefreshCw } from 'lucide-react'
import apiClient, { apiPath } from '../lib/apiClient'
import { AdvancedAIStatus, AdvancedAIResult } from '../types'
import { toast } from '../utils/toast'

const fetchStatus = async (): Promise<AdvancedAIStatus> => {
  const { data } = await apiClient.get<AdvancedAIStatus>(apiPath('ai/engine/status'))
  return data
}

export default function AdvancedAI() {
  const queryClient = useQueryClient()
  const [result, setResult] = useState<AdvancedAIResult | null>(null)

  const statusQuery = useQuery({
    queryKey: ['advanced-ai-status'],
    queryFn: fetchStatus,
    refetchInterval: 60000,
  })

  const runMutation = useMutation({
    mutationFn: async (mode: 'initialize' | 'process_request' | 'generate_insights' | 'optimize') => {
      const { data } = await apiClient.post<AdvancedAIResult>(apiPath('ai/engine/run'), { mode })
      return data
    },
    onSuccess: (data) => {
      setResult(data)
      toast.success(data.title)
      queryClient.invalidateQueries({ queryKey: ['advanced-ai-status'] })
    },
    onError: () => toast.error('Advanced AI action failed'),
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
        Unable to load Advanced AI status.
      </div>
    )
  }

  const data = statusQuery.data

  return (
    <div className="px-4 py-6 sm:px-0 space-y-6">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Advanced AI Engine</h2>
          <p className="text-gray-600 dark:text-gray-400">
            Multi-modal intelligence shared between the Electron and browser surfaces
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => statusQuery.refetch()}
            className="inline-flex items-center px-3 py-2 rounded-md border border-gray-300 dark:border-gray-600 text-sm text-gray-700 dark:text-gray-100 hover:bg-gray-50 dark:hover:bg-gray-700"
          >
            <RefreshCw className="w-4 h-4 mr-1" />
            Refresh
          </button>
          <button
            onClick={() => runMutation.mutate('initialize')}
            className="inline-flex items-center px-3 py-2 rounded-md bg-primary-600 text-white hover:bg-primary-700 text-sm"
          >
            <Zap className="w-4 h-4 mr-1" />
            Initialize
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">Status</p>
                <h3 className="text-2xl font-semibold text-gray-900 dark:text-white">
                  {data.health === 'online' ? 'Online' : 'Offline'}
                </h3>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Last run:{' '}
                  {data.last_run ? new Date(data.last_run).toLocaleString() : 'not yet initialized'}
                </p>
              </div>
              <Brain
                className={`w-12 h-12 ${
                  data.health === 'online' ? 'text-primary-500' : 'text-gray-400 dark:text-gray-600'
                }`}
              />
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-sm">
              <div>
                <p className="text-gray-500 dark:text-gray-400">Requests Today</p>
                <p className="text-gray-900 dark:text-white">{data.metrics.requests_today}</p>
              </div>
              <div>
                <p className="text-gray-500 dark:text-gray-400">Insights</p>
                <p className="text-gray-900 dark:text-white">{data.metrics.insights_generated}</p>
              </div>
              <div>
                <p className="text-gray-500 dark:text-gray-400">Autonomy</p>
                <p className="text-gray-900 dark:text-white">{data.metrics.autonomy_level}</p>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Capabilities</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {data.capabilities.map((capability) => (
                <div
                  key={capability.id}
                  className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 flex items-start gap-3"
                >
                  <GaugeCircle
                    className={`w-5 h-5 ${
                      capability.enabled ? 'text-primary-500' : 'text-gray-400 dark:text-gray-600'
                    }`}
                  />
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">{capability.label}</p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">{capability.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="space-y-6">
          <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Controls</h3>
            <div className="space-y-3">
              {[
                { label: 'Process Request', mode: 'process_request' as const, description: 'Route an AI workload with guardrails' },
                { label: 'Generate Insights', mode: 'generate_insights' as const, description: 'Stream anomalies + KPIs' },
                { label: 'Autonomous Optimization', mode: 'optimize' as const, description: 'Run closed-loop optimization' },
              ].map((action) => (
                <button
                  key={action.mode}
                  onClick={() => runMutation.mutate(action.mode)}
                  className="w-full text-left border border-gray-200 dark:border-gray-700 rounded-md px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-700"
                >
                  <p className="font-medium text-gray-900 dark:text-white">{action.label}</p>
                  <p className="text-sm text-gray-500 dark:text-gray-400">{action.description}</p>
                </button>
              ))}
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Output</h3>
            {result ? (
              <>
                <p className="text-sm text-gray-500 dark:text-gray-400 mb-2">
                  {new Date(result.timestamp).toLocaleString()}
                </p>
                <p className="font-medium text-gray-900 dark:text-white">{result.title}</p>
                <p className="text-sm text-gray-600 dark:text-gray-300 mt-2">{result.output}</p>
                <div className="mt-4 grid grid-cols-3 gap-4 text-center">
                  <div>
                    <p className="text-xs text-gray-500 dark:text-gray-400">Latency</p>
                    <p className="text-sm text-gray-900 dark:text-white">{result.metrics.latency_ms} ms</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500 dark:text-gray-400">Tokens</p>
                    <p className="text-sm text-gray-900 dark:text-white">{result.metrics.tokens_used}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500 dark:text-gray-400">Confidence</p>
                    <p className="text-sm text-gray-900 dark:text-white">
                      {(result.metrics.confidence * 100).toFixed(1)}%
                    </p>
                  </div>
                </div>
              </>
            ) : (
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Run an action to view the latest Advanced AI output.
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
