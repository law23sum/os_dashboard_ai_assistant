import { FormEvent, useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { Search, Database, RefreshCw } from 'lucide-react'
import apiClient, { apiPath } from '../lib/apiClient'
import { SearchStatus, SearchResponse } from '../types'
import { toast } from '../utils/toast'

const fetchStatus = async (): Promise<SearchStatus> => {
  const { data } = await apiClient.get<SearchStatus>(apiPath('search/status'))
  return data
}

const performSearch = async (query: string): Promise<SearchResponse> => {
  const { data } = await apiClient.post<SearchResponse>(apiPath('search/query'), {
    query,
    limit: 12,
  })
  return data
}

export default function SearchEngine() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<SearchResponse | null>(null)

  const statusQuery = useQuery({
    queryKey: ['search-status'],
    queryFn: fetchStatus,
    refetchInterval: 30000,
  })

  const searchMutation = useMutation({
    mutationFn: performSearch,
    onSuccess: (data) => {
      setResults(data)
      toast.success(`Found ${data.total} matches`)
    },
    onError: (error: any) => {
      const message = error?.response?.data?.detail ?? 'Search failed'
      toast.error(message)
    },
  })

  const handleSubmit = (evt: FormEvent) => {
    evt.preventDefault()
    if (!query.trim()) {
      toast.error('Enter a query')
      return
    }
    searchMutation.mutate(query.trim())
  }

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
        Search service unavailable. Launch the backend server.
      </div>
    )
  }

  const status = statusQuery.data

  return (
    <div className="px-4 py-6 sm:px-0 space-y-6">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Search Engine</h2>
          <p className="text-gray-600 dark:text-gray-400">
            Lightweight semantic search bridging desktop + browser apps.
          </p>
        </div>
        <button
          onClick={() => statusQuery.refetch()}
          className="inline-flex items-center px-3 py-2 rounded-md border border-gray-300 dark:border-gray-600 text-sm text-gray-700 dark:text-gray-100 hover:bg-gray-50 dark:hover:bg-gray-700"
        >
          <RefreshCw className="w-4 h-4 mr-1" />
          Refresh Status
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-4">
          <p className="text-sm text-gray-500 dark:text-gray-400">Documents Indexed</p>
          <p className="text-3xl font-bold text-gray-900 dark:text-white">
            {status.documents_indexed}
          </p>
        </div>
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-4">
          <p className="text-sm text-gray-500 dark:text-gray-400">Tasks Indexed</p>
          <p className="text-3xl font-bold text-gray-900 dark:text-white">
            {status.tasks_indexed}
          </p>
        </div>
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-4">
          <p className="text-sm text-gray-500 dark:text-gray-400">Projects Indexed</p>
          <p className="text-3xl font-bold text-gray-900 dark:text-white">
            {status.projects_indexed}
          </p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Semantic Query
        </label>
        <div className="flex flex-col gap-3 md:flex-row">
          <div className="relative flex-1">
            <div className="pointer-events-none absolute inset-y-0 left-0 pl-3 flex items-center">
              <Search className="h-5 w-5 text-gray-400" />
            </div>
            <input
              type="text"
              className="w-full rounded-md border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white pl-10 py-2 focus:ring-primary-500 focus:border-primary-500"
              placeholder="Search tasks, projects, and documents..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
          </div>
          <button
            type="submit"
            className="inline-flex items-center justify-center px-4 py-2 rounded-md bg-primary-600 text-white hover:bg-primary-700"
            disabled={searchMutation.isLoading}
          >
            {searchMutation.isLoading ? 'Searching…' : 'Search'}
          </button>
        </div>
      </form>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-white dark:bg-gray-800 shadow rounded-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Results</h3>
            <Database className="w-5 h-5 text-primary-500" />
          </div>
          {results ? (
            results.results.length > 0 ? (
              <ul className="space-y-4">
                {results.results.map((result) => (
                  <li key={result.id} className="border border-gray-200 dark:border-gray-700 rounded-md p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm uppercase text-gray-500 dark:text-gray-400">
                          {result.kind}
                        </p>
                        <p className="text-lg font-semibold text-gray-900 dark:text-white">
                          {result.title}
                        </p>
                      </div>
                      <span className="text-sm text-gray-500 dark:text-gray-400">
                        Score {result.score}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-300 mt-2">{result.snippet}</p>
                    <div className="mt-3 flex flex-wrap gap-2">
                      {result.tags.map((tag) => (
                        <span
                          key={`${result.id}-${tag}`}
                          className="px-2 py-0.5 rounded-full text-xs bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-200"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-gray-500 dark:text-gray-400">No matches yet.</p>
            )
          ) : (
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Submit a query to view results.
            </p>
          )}
        </div>

        <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
            Engine Status
          </h3>
          <ul className="space-y-3 text-sm text-gray-600 dark:text-gray-300">
            <li>
              Embeddings:{' '}
              <span className="font-semibold">
                {status.embeddings_ready ? 'Ready' : 'Building'}
              </span>
            </li>
            <li>Index spans tasks + projects from the shared SQLite database.</li>
            <li>Use the browser or Electron build without duplication.</li>
          </ul>
        </div>
      </div>
    </div>
  )
}
