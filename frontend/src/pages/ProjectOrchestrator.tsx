import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import {
  Activity,
  AlertCircle,
  CheckCircle,
  Code,
  GitBranch,
  Play,
  Square,
  RefreshCw,
  TrendingUp,
  Shield,
  Zap,
} from 'lucide-react'
import PageHeader from '../components/PageHeader'
import apiClient, { apiPath } from '../lib/apiClient'
import { toast } from '../utils/toast'

interface ProjectInfo {
  name: string
  path: string
  health: 'healthy' | 'degraded' | 'unhealthy' | 'unknown'
  has_autofix: boolean
  has_tests: boolean
  language: string
  last_check: string | null
  error_count: number
  fix_count: number
  metadata: Record<string, any>
}

interface ProjectReport {
  timestamp: string
  total_projects: number
  projects: ProjectInfo[]
  summary: {
    healthy: number
    degraded: number
    unhealthy: number
    unknown: number
    with_autofix: number
    with_tests: number
  }
}

interface AnalyticsSummary {
  total_projects: number
  healthy: number
  degraded: number
  unhealthy: number
  with_autofix: number
  with_tests: number
  health_percentage: number
  autofix_coverage: number
}

const HEALTH_COLORS = {
  healthy: 'text-green-600 bg-green-50 border-green-200',
  degraded: 'text-yellow-600 bg-yellow-50 border-yellow-200',
  unhealthy: 'text-red-600 bg-red-50 border-red-200',
  unknown: 'text-gray-600 bg-gray-50 border-gray-200',
}

const HEALTH_ICONS = {
  healthy: CheckCircle,
  degraded: AlertCircle,
  unhealthy: AlertCircle,
  unknown: Activity,
}

export default function ProjectOrchestrator() {
  const queryClient = useQueryClient()
  const [selectedProject, setSelectedProject] = useState<string | null>(null)

  const { data: projects, isLoading: projectsLoading } = useQuery<ProjectInfo[]>({
    queryKey: ['project-orchestrator', 'discover'],
    queryFn: async () => {
      const res = await apiClient.get(apiPath('projects/discover'))
      return res.data
    },
    refetchInterval: 30000, // Refresh every 30 seconds
  })

  const { data: report } = useQuery<ProjectReport>({
    queryKey: ['project-orchestrator', 'report'],
    queryFn: async () => {
      const res = await apiClient.get(apiPath('projects/report'))
      return res.data
    },
    refetchInterval: 60000, // Refresh every minute
  })

  const { data: analytics } = useQuery<AnalyticsSummary>({
    queryKey: ['project-orchestrator', 'analytics'],
    queryFn: async () => {
      const res = await apiClient.get(apiPath('projects/analytics/summary'))
      return res.data
    },
    refetchInterval: 30000,
  })

  const startAutofixMutation = useMutation({
    mutationFn: async (projectName: string) => {
      const res = await apiClient.post(apiPath(`projects/${projectName}/autofix/start`))
      return res.data
    },
    onSuccess: (data, projectName) => {
      toast.success(`Auto-fix monitor started for ${projectName}`)
      queryClient.invalidateQueries({ queryKey: ['project-orchestrator'] })
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to start auto-fix monitor')
    },
  })

  const stopAutofixMutation = useMutation({
    mutationFn: async (projectName: string) => {
      const res = await apiClient.post(apiPath(`projects/${projectName}/autofix/stop`))
      return res.data
    },
    onSuccess: (data, projectName) => {
      toast.success(`Auto-fix monitor stopped for ${projectName}`)
      queryClient.invalidateQueries({ queryKey: ['project-orchestrator'] })
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to stop auto-fix monitor')
    },
  })

  const refreshMutation = useMutation({
    mutationFn: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ['project-orchestrator', 'discover'] }),
        queryClient.invalidateQueries({ queryKey: ['project-orchestrator', 'report'] }),
        queryClient.invalidateQueries({ queryKey: ['project-orchestrator', 'analytics'] }),
      ])
    },
    onSuccess: () => {
      toast.success('Projects refreshed')
    },
  })

  if (projectsLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Project Orchestrator"
        description="Unified management and monitoring for all Git projects in your workspace"
        icon={GitBranch}
      />

      {/* Analytics Summary */}
      {analytics && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-lg border p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Projects</p>
                <p className="text-2xl font-bold">{analytics.total_projects}</p>
              </div>
              <Code className="w-8 h-8 text-blue-600" />
            </div>
          </div>

          <div className="bg-white rounded-lg border p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Health Score</p>
                <p className="text-2xl font-bold">{analytics.health_percentage.toFixed(1)}%</p>
              </div>
              <TrendingUp className="w-8 h-8 text-green-600" />
            </div>
          </div>

          <div className="bg-white rounded-lg border p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Auto-Fix Coverage</p>
                <p className="text-2xl font-bold">{analytics.autofix_coverage.toFixed(1)}%</p>
              </div>
              <Zap className="w-8 h-8 text-yellow-600" />
            </div>
          </div>

          <div className="bg-white rounded-lg border p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">With Tests</p>
                <p className="text-2xl font-bold">{analytics.with_tests}</p>
              </div>
              <Shield className="w-8 h-8 text-purple-600" />
            </div>
          </div>
        </div>
      )}

      {/* Health Summary */}
      {report && (
        <div className="bg-white rounded-lg border p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Health Summary</h2>
            <button
              onClick={() => refreshMutation.mutate()}
              disabled={refreshMutation.isPending}
              className="flex items-center gap-2 px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 ${refreshMutation.isPending ? 'animate-spin' : ''}`} />
              Refresh
            </button>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600">{report.summary.healthy}</div>
              <div className="text-sm text-gray-600">Healthy</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-yellow-600">{report.summary.degraded}</div>
              <div className="text-sm text-gray-600">Degraded</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-red-600">{report.summary.unhealthy}</div>
              <div className="text-sm text-gray-600">Unhealthy</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-gray-600">{report.summary.unknown}</div>
              <div className="text-sm text-gray-600">Unknown</div>
            </div>
          </div>
        </div>
      )}

      {/* Projects List */}
      <div className="bg-white rounded-lg border">
        <div className="p-6 border-b">
          <h2 className="text-lg font-semibold">Projects</h2>
          <p className="text-sm text-gray-600 mt-1">
            {projects?.length || 0} Git repositories discovered
          </p>
        </div>
        <div className="divide-y">
          {projects && projects.length > 0 ? (
            projects.map((project) => {
              const HealthIcon = HEALTH_ICONS[project.health]
              return (
                <div
                  key={project.name}
                  className={`p-4 hover:bg-gray-50 transition-colors ${
                    selectedProject === project.name ? 'bg-blue-50' : ''
                  }`}
                  onClick={() => setSelectedProject(selectedProject === project.name ? null : project.name)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4 flex-1">
                      <div className={`p-2 rounded-lg border ${HEALTH_COLORS[project.health]}`}>
                        <HealthIcon className="w-5 h-5" />
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <h3 className="font-semibold">{project.name}</h3>
                          <span className="text-xs px-2 py-1 bg-gray-100 rounded text-gray-600">
                            {project.language}
                          </span>
                          {project.has_autofix && (
                            <span className="text-xs px-2 py-1 bg-green-100 text-green-700 rounded">
                              Auto-Fix
                            </span>
                          )}
                          {project.has_tests && (
                            <span className="text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded">
                              Tests
                            </span>
                          )}
                        </div>
                        <p className="text-sm text-gray-600 mt-1">{project.path}</p>
                        {project.last_check && (
                          <p className="text-xs text-gray-500 mt-1">
                            Last check: {new Date(project.last_check).toLocaleString()}
                          </p>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {project.has_autofix && (
                        <>
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              startAutofixMutation.mutate(project.name)
                            }}
                            disabled={startAutofixMutation.isPending}
                            className="flex items-center gap-1 px-3 py-1.5 text-sm bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
                          >
                            <Play className="w-4 h-4" />
                            Start
                          </button>
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              stopAutofixMutation.mutate(project.name)
                            }}
                            disabled={stopAutofixMutation.isPending}
                            className="flex items-center gap-1 px-3 py-1.5 text-sm bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50"
                          >
                            <Square className="w-4 h-4" />
                            Stop
                          </button>
                        </>
                      )}
                    </div>
                  </div>
                  {selectedProject === project.name && (
                    <div className="mt-4 pt-4 border-t">
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <span className="text-gray-600">Errors:</span>{' '}
                          <span className="font-semibold">{project.error_count}</span>
                        </div>
                        <div>
                          <span className="text-gray-600">Fixes:</span>{' '}
                          <span className="font-semibold">{project.fix_count}</span>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )
            })
          ) : (
            <div className="p-8 text-center text-gray-500">
              No projects discovered. Ensure Git repositories exist in the workspace.
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
