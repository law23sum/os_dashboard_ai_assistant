import { useQuery } from '@tanstack/react-query'
import { RefreshCw } from 'lucide-react'
import { useState } from 'react'
import apiClient, { apiPath } from '../lib/apiClient'
import { DocumentOperation, DocumentOperationSummary } from '../types'

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
  const { data } = await apiClient.get<DocumentOperation[]>(apiPath('operations/'), {
    params,
  })
  return data
}

const fetchSummary = async (): Promise<DocumentOperationSummary> => {
  const { data } = await apiClient.get<DocumentOperationSummary>(apiPath('operations/summary'))
  return data
}

const formatTimestamp = (value?: string | null) => {
  if (!value) return '—'
  return new Date(value).toLocaleString()
}

export default function AIOps() {
  const [statusFilter, setStatusFilter] = useState('all')
  const [integrationFilter, setIntegrationFilter] = useState('')

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

  const operations = operationsQuery.data ?? []
  const summary = summaryQuery.data

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">AI Operations</h2>
          <p className="text-gray-600 dark:text-gray-400">
            Governance feed for document automations and daemon workflows
          </p>
        </div>
        <button
          onClick={() => {
            operationsQuery.refetch()
            summaryQuery.refetch()
          }}
          className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700"
        >
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh
        </button>
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
    </div>
  )
}
