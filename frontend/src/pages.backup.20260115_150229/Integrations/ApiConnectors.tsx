import { useState, useMemo } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  PlugZap,
  RefreshCw,
  Activity,
  AlertTriangle,
  Shield,
  Zap,
  Clock3,
} from 'lucide-react'
import apiClient, { apiPath } from '../lib/apiClient'
import { ConnectorOverview, ConnectorStatus } from '../types'
import { toast } from '../utils/toast'

interface ConnectorActionResponse {
  connector_id: string
  action: string
  result: unknown
}

const statusStyles: Record<string, string> = {
  healthy: 'bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-300',
  degraded: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/40 dark:text-yellow-200',
  disconnected: 'bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-200',
}

const fetchOverview = async (): Promise<ConnectorOverview> => {
  const { data } = await apiClient.get<ConnectorOverview>(apiPath('api-connectors/overview'))
  return data
}

const formatTimestamp = (value?: string | null) => {
  if (!value) return '—'
  return new Date(value).toLocaleString()
}

const badgeColor = (severity: string) => {
  switch (severity) {
    case 'error':
      return 'bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-200'
    case 'warning':
      return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/40 dark:text-yellow-200'
    default:
      return 'bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-200'
  }
}

export default function APIConnectors() {
  const queryClient = useQueryClient()
  const [selectedActions, setSelectedActions] = useState<Record<string, string>>({})
  const [lastResponse, setLastResponse] = useState<ConnectorActionResponse | null>(null)

  const overviewQuery = useQuery({
    queryKey: ['api-connectors-overview'],
    queryFn: fetchOverview,
    refetchInterval: 60000,
  })

  const actionMutation = useMutation({
    mutationFn: async ({ connectorId, action }: { connectorId: string; action: string }) => {
      const { data } = await apiClient.post<ConnectorActionResponse>(
        apiPath(`api-connectors/${connectorId}/actions/${action}`),
      )
      return data
    },
    onSuccess: (data, { action }) => {
      setLastResponse(data)
      toast.success(`Action "${action}" completed on ${data.connector_id}`)
      queryClient.invalidateQueries({ queryKey: ['api-connectors-overview'] })
    },
    onError: (error: any) => {
      const detail = error?.response?.data?.detail ?? 'Connector action failed'
      toast.error(detail)
    },
  })

  const data = overviewQuery.data

  const summaryCards = useMemo(() => {
    if (!data) return []
    return [
      {
        label: 'Total Connectors',
        value: data.summary.total,
        icon: PlugZap,
        accent: 'bg-primary-100 text-primary-700 dark:bg-primary-900/40 dark:text-primary-200',
      },
      {
        label: 'Healthy',
        value: data.summary.connected,
        icon: Shield,
        accent: 'bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-200',
      },
      {
        label: 'Needs Attention',
        value: data.summary.degraded + data.summary.disconnected,
        icon: AlertTriangle,
        accent: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/40 dark:text-yellow-200',
      },
      {
        label: 'Avg Health Score',
        value: `${data.summary.average_health}%`,
        icon: Activity,
        accent: 'bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-200',
      },
    ]
  }, [data])

  const handleAction = (connector: ConnectorStatus, action: string) => {
    if (!action) return
    actionMutation.mutate({ connectorId: connector.id, action })
  }

  if (overviewQuery.isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
      </div>
    )
  }

  if (overviewQuery.error || !data) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded">
        Unable to load API connectors. Please ensure the backend server is running.
      </div>
    )
  }

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between mb-8">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">API Connectors</h2>
          <p className="text-gray-600 dark:text-gray-400">
            Shared integration surface for desktop + web experiences
          </p>
        </div>
        <button
          onClick={() => overviewQuery.refetch()}
          className="inline-flex items-center px-4 py-2 rounded-md bg-primary-600 text-white hover:bg-primary-700"
        >
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh
        </button>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4 mb-6">
        {summaryCards.map((card) => {
          const Icon = card.icon
          return (
            <div key={card.label} className="bg-white dark:bg-gray-800 shadow rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <p className="text-sm text-gray-500 dark:text-gray-400">{card.label}</p>
                <span className={`px-2 py-1 text-xs font-semibold rounded-md ${card.accent}`}>
                  <Icon className="w-4 h-4" />
                </span>
              </div>
              <p className="text-2xl font-semibold text-gray-900 dark:text-white">{card.value}</p>
            </div>
          )
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Connectors</h3>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Shared across Electron + browser builds
                </p>
              </div>
              <span className="inline-flex items-center text-sm text-gray-500 dark:text-gray-400">
                <Zap className="w-4 h-4 mr-1 text-primary-500" />
                Auto sync enabled
              </span>
            </div>
            <div className="space-y-4">
              {data.connectors.map((connector) => (
                <div
                  key={connector.id}
                  className="border border-gray-200 dark:border-gray-700 rounded-lg p-4"
                >
                  <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-3">
                    <div>
                      <div className="flex items-center gap-2">
                        <h4 className="text-lg font-medium text-gray-900 dark:text-white">
                          {connector.name}
                        </h4>
                        <span
                          className={`px-2 py-0.5 text-xs font-semibold rounded-full ${
                            statusStyles[connector.status] ?? statusStyles['healthy']
                          }`}
                        >
                          {connector.status}
                        </span>
                      </div>
                      <p className="text-sm text-gray-500 dark:text-gray-400">
                        {connector.category}
                      </p>
                    </div>
                    {connector.error && (
                      <div className="text-sm text-red-600 dark:text-red-400">
                        {connector.error}
                      </div>
                    )}
                  </div>
                  <div className="mt-4 grid grid-cols-1 sm:grid-cols-3 gap-4 text-sm">
                    <div className="flex items-center text-gray-600 dark:text-gray-300">
                      <Activity className="w-4 h-4 mr-2 text-primary-500" />
                      {connector.item_count} items
                    </div>
                    <div className="flex items-center text-gray-600 dark:text-gray-300">
                      <Clock3 className="w-4 h-4 mr-2 text-primary-500" />
                      {formatTimestamp(connector.last_sync)}
                    </div>
                    <div className="flex items-center text-gray-600 dark:text-gray-300">
                      <Shield className="w-4 h-4 mr-2 text-primary-500" />
                      Health {connector.health_score}%
                    </div>
                  </div>
                  <div className="mt-4 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
                    <div className="text-sm text-gray-500 dark:text-gray-400">
                      Pending actions: {connector.pending_actions}
                    </div>
                    <div className="flex flex-col sm:flex-row gap-2">
                      <select
                        value={selectedActions[connector.id] ?? connector.actions[0]?.name ?? 'status'}
                        onChange={(e) =>
                          setSelectedActions((prev) => ({
                            ...prev,
                            [connector.id]: e.target.value,
                          }))
                        }
                        className="rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white focus:ring-primary-500 focus:border-primary-500 text-sm"
                      >
                        {connector.actions.map((action) => (
                          <option key={action.name} value={action.name}>
                            {action.label}
                          </option>
                        ))}
                      </select>
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleAction(connector, 'status')}
                          className="px-3 py-2 rounded-md border border-gray-300 dark:border-gray-600 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700"
                          disabled={actionMutation.isLoading}
                        >
                          Status
                        </button>
                        <button
                          onClick={() => handleAction(connector, 'sync')}
                          className="px-3 py-2 rounded-md border border-gray-300 dark:border-gray-600 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700"
                          disabled={actionMutation.isLoading}
                        >
                          Sync
                        </button>
                        <button
                          onClick={() =>
                            handleAction(
                              connector,
                              selectedActions[connector.id] ??
                                connector.actions[0]?.name ??
                                'status',
                            )
                          }
                          className="px-3 py-2 rounded-md bg-primary-600 text-white hover:bg-primary-700 text-sm"
                          disabled={actionMutation.isLoading}
                        >
                          Run
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
              {data.connectors.length === 0 && (
                <div className="text-center text-gray-500 dark:text-gray-400 py-6">
                  No connectors registered
                </div>
              )}
            </div>
          </div>

          {lastResponse && (
            <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                Latest Action
              </h3>
              <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
                {lastResponse.connector_id} • {lastResponse.action} •{' '}
                {formatTimestamp(new Date().toISOString())}
              </p>
              <pre className="bg-gray-900 text-green-300 rounded-lg p-4 text-xs overflow-auto">
                {JSON.stringify(lastResponse.result, null, 2)}
              </pre>
            </div>
          )}
        </div>

        <div className="space-y-6">
          <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Activity</h3>
              <Activity className="w-5 h-5 text-primary-500" />
            </div>
            <div className="space-y-4">
              {data.activity.map((item) => (
                <div key={`${item.connector_id}-${item.timestamp}`}>
                  <div className="flex items-center justify-between text-sm">
                    <span className="font-medium text-gray-900 dark:text-white">
                      {item.connector_id}
                    </span>
                    <span className={`px-2 py-0.5 rounded-full text-xs ${badgeColor(item.severity)}`}>
                      {item.severity}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">{item.message}</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {formatTimestamp(item.timestamp)}
                  </p>
                  {item.details && (
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">{item.details}</p>
                  )}
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Actions</h3>
              <RefreshCw className="w-4 h-4 text-primary-500" />
            </div>
            <div className="space-y-3 max-h-96 overflow-y-auto text-sm">
              {Object.entries(data.actions_catalog).map(([connectorId, actions]) => (
                <div key={connectorId}>
                  <p className="font-medium text-gray-900 dark:text-white uppercase text-xs mb-2">
                    {connectorId}
                  </p>
                  <div className="space-y-1">
                    {actions.map((action) => (
                      <div
                        key={`${connectorId}-${action.name}`}
                        className="border border-gray-200 dark:border-gray-700 rounded-md p-2"
                      >
                        <p className="text-gray-900 dark:text-white">{action.label}</p>
                        {action.description && (
                          <p className="text-xs text-gray-500 dark:text-gray-400">
                            {action.description}
                          </p>
                        )}
                      </div>
                    ))}
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