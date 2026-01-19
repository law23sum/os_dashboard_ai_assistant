import { useQuery } from '@tanstack/react-query'
import { useState, useEffect } from 'react'
import {
  Activity,
  Bot,
  CheckCircle2,
  XCircle,
  Clock,
  AlertTriangle,
  Folder,
  GitBranch,
  Terminal,
  ListTodo,
  Play,
  StopCircle,
  RefreshCw,
  BarChart3,
  Server,
  Zap,
} from 'lucide-react'
import apiClient from '../lib/apiClient'

type ProjectStatus = 'discovered' | 'running' | 'healthy' | 'unhealthy' | 'stopped' | 'error'

type Project = {
  path: string
  status: ProjectStatus
  branch: string | null
  has_ai_autofix: boolean
  has_tests: boolean
  todo_count: number
}

type TodoStats = {
  total: number
  by_priority: {
    critical: number
    high: number
    normal: number
    low: number
  }
  completed: number
}

type MonitorStats = {
  running: number
  healthy: number
  stopped: number
  error: number
}

type OrchestratorStatus = {
  timestamp: string
  root: string
  total_projects: number
  projects: Record<string, Project>
  todos: TodoStats
  monitors: MonitorStats
}

const fetchOrchestratorStatus = async (): Promise<OrchestratorStatus | null> => {
  try {
    // Try to read from the status report file via API
    const { data } = await apiClient.get('/api/orchestrator/status')
    return data as OrchestratorStatus
  } catch (error) {
    // Fallback to reading from static file if available
    try {
      const response = await fetch('/logs/status_report.json')
      if (response.ok) {
        return await response.json()
      }
    } catch (e) {
      console.error('Failed to fetch orchestrator status:', e)
    }
    return null
  }
}

const STATUS_ICONS: Record<ProjectStatus, typeof Activity> = {
  discovered: Folder,
  running: Play,
  healthy: CheckCircle2,
  unhealthy: AlertTriangle,
  stopped: StopCircle,
  error: XCircle,
}

const STATUS_COLORS: Record<ProjectStatus, string> = {
  discovered: 'text-gray-500',
  running: 'text-blue-500',
  healthy: 'text-green-500',
  unhealthy: 'text-yellow-500',
  stopped: 'text-gray-500',
  error: 'text-red-500',
}

const PRIORITY_COLORS = {
  critical: 'text-red-600 bg-red-50',
  high: 'text-orange-600 bg-orange-50',
  normal: 'text-blue-600 bg-blue-50',
  low: 'text-gray-600 bg-gray-50',
}

export default function MasterOrchestrator() {
  const [autoRefresh, setAutoRefresh] = useState(true)
  
  const { data: status, isLoading, error, refetch } = useQuery({
    queryKey: ['orchestrator-status'],
    queryFn: fetchOrchestratorStatus,
    refetchInterval: autoRefresh ? 5000 : false, // Refresh every 5 seconds
    retry: 3,
  })

  useEffect(() => {
    // Auto-refresh every 5 seconds if enabled
    if (autoRefresh) {
      const interval = setInterval(() => {
        refetch()
      }, 5000)
      return () => clearInterval(interval)
    }
  }, [autoRefresh, refetch])

  if (isLoading) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center h-64">
          <div className="flex items-center space-x-2">
            <RefreshCw className="w-5 h-5 animate-spin text-blue-500" />
            <span className="text-gray-600">Loading orchestrator status...</span>
          </div>
        </div>
      </div>
    )
  }

  if (error || !status) {
    return (
      <div className="p-6">
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
          <div className="flex items-start space-x-3">
            <AlertTriangle className="w-6 h-6 text-yellow-600 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-yellow-900 mb-2">
                Master Orchestrator Not Running
              </h3>
              <p className="text-yellow-700 mb-4">
                The Master AI Orchestrator is not currently active. Launch it to enable
                multi-project AI auto-fix and TODO monitoring.
              </p>
              <div className="bg-white rounded border border-yellow-200 p-4 font-mono text-sm">
                <div className="text-gray-700 mb-2"># Start the master orchestrator:</div>
                <div className="text-blue-600">python os_dashboard_ai_assistant.py</div>
                <div className="text-gray-700 mt-4 mb-2"># Or enable via UI launcher:</div>
                <div className="text-blue-600">python start_ui.py --enable-orchestrator</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  const projects = Object.entries(status.projects)

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center space-x-3">
            <Bot className="w-8 h-8 text-blue-600" />
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Master Orchestrator</h1>
              <p className="text-gray-600">Multi-project AI auto-fix & TODO management</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-3">
            <button
              onClick={() => setAutoRefresh(!autoRefresh)}
              className={`px-3 py-2 rounded-lg border ${
                autoRefresh
                  ? 'bg-blue-50 border-blue-200 text-blue-700'
                  : 'bg-gray-50 border-gray-200 text-gray-600'
              } hover:bg-opacity-80 transition-colors flex items-center space-x-2`}
            >
              {autoRefresh ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span className="text-sm font-medium">Auto-refresh</span>
                </>
              ) : (
                <>
                  <RefreshCw className="w-4 h-4" />
                  <span className="text-sm font-medium">Paused</span>
                </>
              )}
            </button>
            
            <button
              onClick={() => refetch()}
              className="px-3 py-2 rounded-lg bg-blue-600 text-white hover:bg-blue-700 transition-colors flex items-center space-x-2"
            >
              <RefreshCw className="w-4 h-4" />
              <span className="text-sm font-medium">Refresh Now</span>
            </button>
          </div>
        </div>
        
        <div className="text-sm text-gray-500">
          Last updated: {new Date(status.timestamp).toLocaleString()}
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center justify-between mb-2">
            <div className="text-sm font-medium text-gray-600">Total Projects</div>
            <Folder className="w-5 h-5 text-gray-400" />
          </div>
          <div className="text-3xl font-bold text-gray-900">{status.total_projects}</div>
          <div className="text-xs text-gray-500 mt-1">Discovered in workspace</div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center justify-between mb-2">
            <div className="text-sm font-medium text-gray-600">Active Monitors</div>
            <Activity className="w-5 h-5 text-green-400" />
          </div>
          <div className="text-3xl font-bold text-green-600">
            {status.monitors.running + status.monitors.healthy}
          </div>
          <div className="text-xs text-gray-500 mt-1">
            {status.monitors.running} running, {status.monitors.healthy} healthy
          </div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center justify-between mb-2">
            <div className="text-sm font-medium text-gray-600">Pending TODOs</div>
            <ListTodo className="w-5 h-5 text-blue-400" />
          </div>
          <div className="text-3xl font-bold text-blue-600">
            {status.todos.total - status.todos.completed}
          </div>
          <div className="text-xs text-gray-500 mt-1">
            {status.todos.completed} completed
          </div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center justify-between mb-2">
            <div className="text-sm font-medium text-gray-600">High Priority</div>
            <Zap className="w-5 h-5 text-orange-400" />
          </div>
          <div className="text-3xl font-bold text-orange-600">
            {status.todos.by_priority.critical + status.todos.by_priority.high}
          </div>
          <div className="text-xs text-gray-500 mt-1">
            {status.todos.by_priority.critical} critical, {status.todos.by_priority.high} high
          </div>
        </div>
      </div>

      {/* TODO Priority Breakdown */}
      <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
        <div className="flex items-center space-x-2 mb-4">
          <BarChart3 className="w-5 h-5 text-gray-600" />
          <h2 className="text-lg font-semibold text-gray-900">TODO Priority Breakdown</h2>
        </div>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {Object.entries(status.todos.by_priority).map(([priority, count]) => (
            <div key={priority} className={`rounded-lg p-4 ${PRIORITY_COLORS[priority as keyof typeof PRIORITY_COLORS]}`}>
              <div className="text-sm font-medium uppercase mb-1">{priority}</div>
              <div className="text-2xl font-bold">{count}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Projects List */}
      <div className="bg-white rounded-lg border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex items-center space-x-2">
            <Server className="w-5 h-5 text-gray-600" />
            <h2 className="text-lg font-semibold text-gray-900">Projects</h2>
          </div>
        </div>

        <div className="divide-y divide-gray-200">
          {projects.length === 0 ? (
            <div className="px-6 py-8 text-center text-gray-500">
              No projects discovered yet
            </div>
          ) : (
            projects.map(([name, project]) => {
              const StatusIcon = STATUS_ICONS[project.status]
              const statusColor = STATUS_COLORS[project.status]
              
              return (
                <div key={name} className="px-6 py-4 hover:bg-gray-50 transition-colors">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <StatusIcon className={`w-5 h-5 ${statusColor}`} />
                        <h3 className="text-lg font-semibold text-gray-900">{name}</h3>
                        <span className={`px-2 py-0.5 rounded text-xs font-medium ${statusColor} bg-opacity-10`}>
                          {project.status}
                        </span>
                      </div>
                      
                      <div className="flex items-center space-x-4 text-sm text-gray-600 mb-2">
                        <div className="flex items-center space-x-1">
                          <Folder className="w-4 h-4" />
                          <span className="font-mono text-xs">{project.path}</span>
                        </div>
                        
                        {project.branch && (
                          <div className="flex items-center space-x-1">
                            <GitBranch className="w-4 h-4" />
                            <span>{project.branch}</span>
                          </div>
                        )}
                      </div>
                      
                      <div className="flex items-center space-x-4 text-sm">
                        {project.has_ai_autofix ? (
                          <span className="flex items-center space-x-1 text-green-600">
                            <CheckCircle2 className="w-4 h-4" />
                            <span>AI Auto-fix</span>
                          </span>
                        ) : (
                          <span className="flex items-center space-x-1 text-gray-400">
                            <XCircle className="w-4 h-4" />
                            <span>No AI Auto-fix</span>
                          </span>
                        )}
                        
                        {project.has_tests ? (
                          <span className="flex items-center space-x-1 text-green-600">
                            <CheckCircle2 className="w-4 h-4" />
                            <span>Tests</span>
                          </span>
                        ) : (
                          <span className="flex items-center space-x-1 text-gray-400">
                            <XCircle className="w-4 h-4" />
                            <span>No Tests</span>
                          </span>
                        )}
                        
                        {project.todo_count > 0 && (
                          <span className="flex items-center space-x-1 text-blue-600">
                            <ListTodo className="w-4 h-4" />
                            <span>{project.todo_count} TODOs</span>
                          </span>
                        )}
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-2 ml-4">
                      <button
                        className="p-2 rounded hover:bg-gray-100 transition-colors"
                        title="View logs"
                      >
                        <Terminal className="w-4 h-4 text-gray-600" />
                      </button>
                      <button
                        className="p-2 rounded hover:bg-gray-100 transition-colors"
                        title="View TODOs"
                      >
                        <ListTodo className="w-4 h-4 text-gray-600" />
                      </button>
                    </div>
                  </div>
                </div>
              )
            })
          )}
        </div>
      </div>

      {/* Monitor Status */}
      <div className="mt-6 bg-white rounded-lg border border-gray-200 p-6">
        <div className="flex items-center space-x-2 mb-4">
          <Activity className="w-5 h-5 text-gray-600" />
          <h2 className="text-lg font-semibold text-gray-900">Monitor Status</h2>
        </div>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="flex items-center space-x-3">
            <div className="w-3 h-3 rounded-full bg-blue-500"></div>
            <div>
              <div className="text-sm text-gray-600">Running</div>
              <div className="text-xl font-bold text-gray-900">{status.monitors.running}</div>
            </div>
          </div>
          
          <div className="flex items-center space-x-3">
            <div className="w-3 h-3 rounded-full bg-green-500"></div>
            <div>
              <div className="text-sm text-gray-600">Healthy</div>
              <div className="text-xl font-bold text-gray-900">{status.monitors.healthy}</div>
            </div>
          </div>
          
          <div className="flex items-center space-x-3">
            <div className="w-3 h-3 rounded-full bg-gray-500"></div>
            <div>
              <div className="text-sm text-gray-600">Stopped</div>
              <div className="text-xl font-bold text-gray-900">{status.monitors.stopped}</div>
            </div>
          </div>
          
          <div className="flex items-center space-x-3">
            <div className="w-3 h-3 rounded-full bg-red-500"></div>
            <div>
              <div className="text-sm text-gray-600">Errors</div>
              <div className="text-xl font-bold text-gray-900">{status.monitors.error}</div>
            </div>
          </div>
        </div>
      </div>

      {/* Help Section */}
      <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-6">
        <div className="flex items-start space-x-3">
          <Bot className="w-6 h-6 text-blue-600 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-blue-900 mb-2">
              About the Master Orchestrator
            </h3>
            <p className="text-blue-700 mb-4">
              The Master Orchestrator automatically discovers all git repositories in your workspace,
              launches AI auto-fix monitors for each project, and tracks TODO items across all codebases.
            </p>
            
            <div className="space-y-2 text-sm text-blue-800">
              <div><strong>Features:</strong></div>
              <ul className="list-disc list-inside space-y-1 ml-4">
                <li>Automatic project discovery via .git detection</li>
                <li>AI-powered auto-fix for errors and warnings</li>
                <li>TODO monitoring and codex spawning</li>
                <li>Real-time health monitoring</li>
                <li>Comprehensive logging and reporting</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}