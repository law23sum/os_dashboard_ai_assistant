import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Plug,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Server,
  RefreshCw,
  Activity as ActivityIcon,
  Shield,
} from 'lucide-react'
import { useEffect, useMemo, useState } from 'react'
import apiClient, { apiPath } from '../lib/apiClient'
import type {
  IntegrationSnapshot,
  IntegrationConnectorDetails,
  IntegrationActivity,
  ConnectorConfiguration,
} from '../types'
import { toast } from '../utils/toast'

const fetchIntegrationSnapshot = async (): Promise<IntegrationSnapshot> => {
  const { data } = await apiClient.get<IntegrationSnapshot>(apiPath('integrations/summary'))
  return data
}

const performConnectorAction = async ({
  connectorId,
  action,
}: {
  connectorId: string
  action: 'connect' | 'disconnect' | 'test'
}) => {
  const { data } = await apiClient.post(apiPath(`api-connectors/${connectorId}/actions/${action}`), {
    options: {},
  })
  return data
}

const fetchConnectorConfiguration = async (connectorId: string): Promise<ConnectorConfiguration> => {
  const { data } = await apiClient.get<ConnectorConfiguration>(apiPath(`integrations/connectors/${connectorId}`))
  return data
}

const saveConnectorConfiguration = async ({
  connectorId,
  settings,
}: {
  connectorId: string
  settings: Record<string, any>
}) => {
  const { data } = await apiClient.post(apiPath(`integrations/connectors/${connectorId}/configure`), {
    settings,
  })
  return data
}

export default function Integrations() {
  const queryClient = useQueryClient()
  const { data, isLoading } = useQuery({
    queryKey: ['integrations-snapshot'],
    queryFn: fetchIntegrationSnapshot,
    refetchInterval: 60000,
  })
  const [selectedConnector, setSelectedConnector] = useState<IntegrationConnectorDetails | null>(null)

  const actionMutation = useMutation({
    mutationFn: performConnectorAction,
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['integrations-snapshot'] })
      const actionText = variables.action === 'test' ? 'Test triggered' : `Connector ${variables.action}ed`
      toast.success(actionText)
    },
    onError: (error) => {
      toast.error(error instanceof Error ? error.message : 'Integration action failed')
    },
  })

  if (isLoading || !data) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
      </div>
    )
  }

  const { summary, connectors, pipelines, incidents, activity } = data

  const statusPills = useMemo(
    () => [
      { label: 'Connected', value: summary.connected, color: 'text-emerald-500', icon: CheckCircle },
      { label: 'Degraded', value: summary.degraded, color: 'text-amber-500', icon: AlertTriangle },
      { label: 'Disconnected', value: summary.disconnected, color: 'text-rose-500', icon: XCircle },
      { label: 'Total', value: summary.total, color: 'text-primary-500', icon: Plug },
    ],
    [summary],
  )

  return (
    <div className="px-4 py-6 sm:px-0 space-y-6">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Integrations & Infrastructure</h2>
          <p className="text-gray-600 dark:text-gray-400">
            Shared connectors, pipelines, and sync health for both desktop and web shells.
          </p>
        </div>
        <button
          onClick={() => queryClient.invalidateQueries({ queryKey: ['integrations-snapshot'] })}
          className="inline-flex items-center px-4 py-2 rounded-md bg-primary-600 text-white text-sm font-medium hover:bg-primary-700"
        >
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh
        </button>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {statusPills.map(({ label, value, color, icon: Icon }) => (
          <div key={label} className="rounded-xl border border-gray-200 dark:border-gray-700 bg-white/70 dark:bg-gray-900/60 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-gray-500 dark:text-gray-400">{label}</p>
                <p className={`text-2xl font-semibold ${color}`}>{value}</p>
              </div>
              <Icon className={`w-5 h-5 ${color}`} />
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-4">
          {connectors.map((connector) => (
            <div
              key={connector.id}
              className="border border-gray-200 dark:border-gray-700 rounded-xl bg-white dark:bg-gray-900/70 p-4 flex flex-col md:flex-row md:items-center md:justify-between gap-4"
            >
              <div className="flex items-start gap-3">
                <div className={`w-10 h-10 rounded-full flex items-center justify-center ${connector.connected ? 'bg-emerald-500/10 text-emerald-500' : 'bg-gray-500/10 text-gray-400'}`}>
                  <Plug className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{connector.name}</h3>
                  <p className="text-sm text-gray-500 dark:text-gray-400">{connector.category}</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    {connector.connected ? 'Connected' : 'Disconnected'} · {connector.throughput}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <button
                  className="px-3 py-2 text-sm font-medium rounded-md border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-800"
                  onClick={() => actionMutation.mutate({ connectorId: connector.id, action: 'test' })}
                >
                  Test
                </button>
                <button
                  className={`px-3 py-2 text-sm font-medium rounded-md ${
                    connector.connected
                      ? 'bg-red-100 text-red-700 hover:bg-red-200 dark:bg-red-900/50 dark:text-red-200'
                      : 'bg-primary-600 text-white hover:bg-primary-700'
                  }`}
                  onClick={() =>
                    actionMutation.mutate({
                      connectorId: connector.id,
                      action: connector.connected ? 'disconnect' : 'connect',
                    })
                  }
                >
                  {connector.connected ? 'Disconnect' : 'Connect'}
                </button>
                <button
                  className="px-3 py-2 text-sm font-medium rounded-md bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-gray-100"
                  onClick={() => setSelectedConnector(connector)}
                >
                  Details
                </button>
              </div>
            </div>
          ))}
        </div>

        <div className="space-y-4">
          <div className="border border-gray-200 dark:border-gray-700 rounded-xl bg-white dark:bg-gray-900/70 p-4">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3 flex items-center">
              <Server className="w-5 h-5 mr-2 text-primary-500" /> Pipelines
            </h3>
            <div className="space-y-3">
              {pipelines.map((pipeline) => (
                <div key={pipeline.id} className="rounded-lg border border-gray-200 dark:border-gray-700 p-3">
                  <p className="text-sm font-semibold text-gray-900 dark:text-white">{pipeline.name}</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">{pipeline.status} · {pipeline.throughput}</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Latency: {pipeline.latency_ms} ms</p>
                </div>
              ))}
            </div>
          </div>
          <div className="border border-gray-200 dark:border-gray-700 rounded-xl bg-white dark:bg-gray-900/70 p-4">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3 flex items-center">
              <AlertTriangle className="w-5 h-5 mr-2 text-amber-500" /> Incidents
            </h3>
            <div className="space-y-3 max-h-64 overflow-y-auto pr-2">
              {incidents.length === 0 && <p className="text-sm text-gray-500">No incidents logged.</p>}
              {incidents.map((incident) => (
                <div key={incident.id} className="rounded-lg border border-gray-200 dark:border-gray-700 p-3">
                  <p className="text-sm font-semibold text-gray-900 dark:text-white">{incident.title}</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">{incident.connector} · {incident.severity}</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">{new Date(incident.timestamp).toLocaleString()}</p>
                  <p className="text-xs text-gray-600 dark:text-gray-300 mt-1">{incident.detail}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white dark:bg-gray-900/80 border border-gray-200 dark:border-gray-700 rounded-xl p-4">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center">
            <ActivityIcon className="w-5 h-5 mr-2 text-primary-500" /> Activity Log
          </h3>
        </div>
        <div className="space-y-3 max-h-72 overflow-y-auto pr-2">
          {activity.length === 0 && <p className="text-sm text-gray-500 dark:text-gray-400">No recent connector activity.</p>}
          {activity.map((entry: IntegrationActivity) => (
            <div key={entry.id} className="flex items-start gap-3 border border-gray-200 dark:border-gray-800 rounded-lg p-3">
              <Shield className={`w-4 h-4 mt-1 ${entry.status === 'success' ? 'text-emerald-400' : 'text-rose-400'}`} />
              <div>
                <p className="text-sm text-gray-900 dark:text-white font-semibold">
                  {entry.action.toUpperCase()} · {entry.connector}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400">{new Date(entry.timestamp).toLocaleString()}</p>
                <p className="text-xs text-gray-600 dark:text-gray-300 mt-1">{entry.detail}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {selectedConnector && (
        <ConnectorModal
          connector={selectedConnector}
          onClose={() => setSelectedConnector(null)}
          onAction={(action) => actionMutation.mutate({ connectorId: selectedConnector.id, action })}
          onSettingsSaved={() => queryClient.invalidateQueries({ queryKey: ['integrations-snapshot'] })}
        />
      )}
    </div>
  )
}

function ConnectorModal({
  connector,
  onClose,
  onAction,
  onSettingsSaved,
}: {
  connector: IntegrationConnectorDetails
  onClose: () => void
  onAction: (action: 'connect' | 'disconnect' | 'test') => void
  onSettingsSaved: () => void
}) {
  const { data: configuration, isLoading } = useQuery({
    queryKey: ['connector-config', connector.id],
    queryFn: () => fetchConnectorConfiguration(connector.id),
  })
  const [settings, setSettings] = useState<Record<string, any>>({})
  const saveMutation = useMutation({
    mutationFn: saveConnectorConfiguration,
    onSuccess: () => {
      toast.success('Connector settings saved')
      onSettingsSaved()
    },
    onError: (error) => {
      toast.error(error instanceof Error ? error.message : 'Failed to save connector settings')
    },
  })

  useEffect(() => {
    if (configuration) {
      setSettings(configuration.current_settings || {})
    }
  }, [configuration, connector.id])

  const handleSettingChange = (field: string, value: string | number) => {
    setSettings((prev) => ({ ...prev, [field]: value }))
  }

  const handleSave = () => {
    if (!configuration) return
    saveMutation.mutate({ connectorId: connector.id, settings })
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-xl w-full max-w-lg border border-gray-200 dark:border-gray-700 p-6 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white">{connector.name}</h3>
            <p className="text-sm text-gray-500 dark:text-gray-400">{connector.category}</p>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">✕</button>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <Detail label="Status" value={connector.status} />
          <Detail label="Health" value={connector.health} />
          <Detail label="Latency" value={`${connector.latency_ms || 0} ms`} />
          <Detail label="Throughput" value={connector.throughput} />
          <Detail label="Last Sync" value={connector.last_sync || '—'} />
          <Detail label="Targets" value={connector.targets.join(', ')} />
        </div>
        <p className="text-sm text-gray-600 dark:text-gray-300">{connector.notes}</p>

        <div className="space-y-3">
          <p className="text-xs uppercase tracking-wide text-gray-500 dark:text-gray-400">Connection Settings</p>
          {isLoading && (
            <div className="flex items-center justify-center py-6">
              <div className="h-6 w-6 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" />
            </div>
          )}
          {!isLoading && configuration && (
            <>
              {Object.keys(configuration.settings_schema || {}).length === 0 && (
                <p className="text-sm text-gray-500">No configurable settings for this connector.</p>
              )}
              {Object.entries(configuration.settings_schema || {}).map(([field, schema]) => (
                <div key={field} className="space-y-1">
                  <label className="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">
                    {schema.label}
                  </label>
                  <input
                    type={schema.type === 'password' ? 'password' : schema.type === 'number' ? 'number' : 'text'}
                    placeholder={schema.placeholder}
                    min={schema.min}
                    max={schema.max}
                    value={settings[field] ?? ''}
                    onChange={(event) =>
                      handleSettingChange(
                        field,
                        schema.type === 'number' ? Number(event.target.value) : event.target.value,
                      )
                    }
                    className="w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-white/80 dark:bg-gray-800 px-3 py-2 text-sm text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                </div>
              ))}
            </>
          )}
        </div>

        <div className="flex flex-wrap gap-2 pt-2 border-t border-gray-200 dark:border-gray-800">
          <button
            className="px-3 py-2 text-sm font-medium rounded-md bg-primary-600 text-white hover:bg-primary-700"
            onClick={() => onAction('test')}
          >
            Test Connection
          </button>
          <button
            className="px-3 py-2 text-sm font-medium rounded-md bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-gray-200"
            onClick={() => onAction(connector.connected ? 'disconnect' : 'connect')}
          >
            {connector.connected ? 'Disconnect' : 'Connect'}
          </button>
          <button
            className="px-3 py-2 text-sm font-medium rounded-md bg-emerald-600 text-white hover:bg-emerald-700 disabled:opacity-60"
            onClick={handleSave}
            disabled={isLoading || saveMutation.isPending || !configuration}
          >
            {saveMutation.isPending ? 'Saving...' : 'Save Settings'}
          </button>
        </div>
      </div>
    </div>
  )
}

function Detail({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-lg border border-gray-200 dark:border-gray-800 p-3">
      <p className="text-xs text-gray-500 dark:text-gray-400">{label}</p>
      <p className="text-sm font-semibold text-gray-900 dark:text-white">{value}</p>
    </div>
  )
}
