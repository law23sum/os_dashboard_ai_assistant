import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ClipboardList, ShieldCheck, AlertTriangle, Activity, RefreshCw } from 'lucide-react'
import apiClient, { apiPath } from '../lib/apiClient'
import { AuditSummary, AuditLogEntry, AuditCheckResponse } from '../types'
import { toast } from '../utils/toast'

const fetchSummary = async (): Promise<AuditSummary> => {
  const { data } = await apiClient.get<AuditSummary>(apiPath('audit/summary'))
  return data
}

const fetchLogs = async (): Promise<AuditLogEntry[]> => {
  const { data } = await apiClient.get<AuditLogEntry[]>(apiPath('audit/logs'), {
    params: { limit: 25 },
  })
  return data
}

export default function Audit() {
  const queryClient = useQueryClient()
  const [lastRun, setLastRun] = useState<AuditCheckResponse | null>(null)

  const summaryQuery = useQuery({
    queryKey: ['audit-summary'],
    queryFn: fetchSummary,
    refetchInterval: 60000,
  })

  const logsQuery = useQuery({
    queryKey: ['audit-logs'],
    queryFn: fetchLogs,
    refetchInterval: 45000,
  })

  const runCheckMutation = useMutation({
    mutationFn: async () => {
      const { data } = await apiClient.post<AuditCheckResponse>(apiPath('audit/checks/run'))
      return data
    },
    onSuccess: (data) => {
      setLastRun(data)
      toast.success('Compliance check completed')
      queryClient.invalidateQueries({ queryKey: ['audit-summary'] })
      queryClient.invalidateQueries({ queryKey: ['audit-logs'] })
    },
    onError: () => toast.error('Unable to run compliance check'),
  })

  if (summaryQuery.isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
      </div>
    )
  }

  if (summaryQuery.error || !summaryQuery.data) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded">
        Unable to load audit system. Start the backend server.
      </div>
    )
  }

  const summary = summaryQuery.data
  const logs = logsQuery.data ?? []

  return (
    <div className="px-4 py-6 sm:px-0 space-y-6">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Audit System</h2>
          <p className="text-gray-600 dark:text-gray-400">
            Compliance monitoring shared between desktop + web surfaces.
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => summaryQuery.refetch()}
            className="inline-flex items-center px-3 py-2 rounded-md border border-gray-300 dark:border-gray-600 text-sm text-gray-700 dark:text-gray-100 hover:bg-gray-50 dark:hover:bg-gray-700"
          >
            <RefreshCw className="w-4 h-4 mr-1" />
            Refresh
          </button>
          <button
            onClick={() => runCheckMutation.mutate()}
            className="inline-flex items-center px-3 py-2 rounded-md bg-primary-600 text-white hover:bg-primary-700 text-sm"
            disabled={runCheckMutation.isLoading}
          >
            <ShieldCheck className="w-4 h-4 mr-1" />
            Run Compliance Check
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
          <p className="text-sm text-gray-500 dark:text-gray-400">Risk Score</p>
          <p className="text-3xl font-bold text-gray-900 dark:text-white">{summary.risk_score}</p>
          <p className="text-xs text-gray-500 dark:text-gray-400">Lower is better</p>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
          <p className="text-sm text-gray-500 dark:text-gray-400">Controls Healthy</p>
          <p className="text-3xl font-bold text-gray-900 dark:text-white">
            {summary.controls_healthy}/{summary.controls_in_place}
          </p>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
          <p className="text-sm text-gray-500 dark:text-gray-400">Outstanding Actions</p>
          <p className="text-3xl font-bold text-gray-900 dark:text-white">
            {summary.outstanding_actions}
          </p>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
          <p className="text-sm text-gray-500 dark:text-gray-400">Last Check</p>
          <p className="text-lg font-semibold text-gray-900 dark:text-white">
            {new Date(summary.last_check).toLocaleString()}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Compliance Frameworks
              </h3>
              <ClipboardList className="w-5 h-5 text-primary-500" />
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {summary.metrics.map((metric) => (
                <div
                  key={metric.framework}
                  className="border border-gray-200 dark:border-gray-700 rounded-md p-4"
                >
                  <div className="flex items-center justify-between">
                    <p className="font-semibold text-gray-900 dark:text-white">
                      {metric.framework}
                    </p>
                    <span
                      className={`px-2 py-0.5 rounded-full text-xs font-semibold ${
                        metric.status === 'healthy'
                          ? 'bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-200'
                          : 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/40 dark:text-yellow-200'
                      }`}
                    >
                      {metric.status}
                    </span>
                  </div>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white mt-2">
                    {metric.score}%
                  </p>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    Last checked {new Date(metric.last_checked).toLocaleString()}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                    Issues: {metric.issues}
                  </p>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                  Audit Activity
                </h3>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Latest governance events mirrored across desktop + web.
                </p>
              </div>
              <Activity className="w-5 h-5 text-primary-500" />
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700 text-sm">
                <thead className="bg-gray-50 dark:bg-gray-700">
                  <tr>
                    <th className="px-4 py-2 text-left text-gray-500 dark:text-gray-300 font-medium">
                      Event
                    </th>
                    <th className="px-4 py-2 text-left text-gray-500 dark:text-gray-300 font-medium">
                      Resource
                    </th>
                    <th className="px-4 py-2 text-left text-gray-500 dark:text-gray-300 font-medium">
                      User
                    </th>
                    <th className="px-4 py-2 text-left text-gray-500 dark:text-gray-300 font-medium">
                      Status
                    </th>
                    <th className="px-4 py-2 text-left text-gray-500 dark:text-gray-300 font-medium">
                      Timestamp
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                  {logs.map((log) => (
                    <tr key={log.id}>
                      <td className="px-4 py-3 text-gray-900 dark:text-white">{log.event}</td>
                      <td className="px-4 py-3 text-gray-600 dark:text-gray-300">{log.resource}</td>
                      <td className="px-4 py-3 text-gray-600 dark:text-gray-300">{log.user}</td>
                      <td className="px-4 py-3 text-gray-600 dark:text-gray-300">{log.status}</td>
                      <td className="px-4 py-3 text-gray-600 dark:text-gray-300">
                        {new Date(log.timestamp).toLocaleString()}
                      </td>
                    </tr>
                  ))}
                  {logs.length === 0 && (
                    <tr>
                      <td colSpan={5} className="px-4 py-6 text-center text-gray-500 dark:text-gray-400">
                        No recent audit activity.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div className="space-y-6">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Compliance Run History
              </h3>
              <AlertTriangle className="w-5 h-5 text-primary-500" />
            </div>
            {lastRun ? (
              <div className="space-y-2 text-sm text-gray-600 dark:text-gray-300">
                <p>
                  <span className="font-medium">Started:</span>{' '}
                  {new Date(lastRun.started_at).toLocaleString()}
                </p>
                <p>
                  <span className="font-medium">Completed:</span>{' '}
                  {new Date(lastRun.completed_at).toLocaleString()}
                </p>
                <p>
                  <span className="font-medium">Issues Found:</span> {lastRun.issues_found}
                </p>
                <p>{lastRun.notes}</p>
              </div>
            ) : (
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Run the compliance check to capture a new log.
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
