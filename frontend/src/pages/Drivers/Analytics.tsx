import { useQuery } from '@tanstack/react-query'
import {
  BarChart3,
  RefreshCw,
  Download,
  ClipboardCopy,
  AlertTriangle,
  Users,
  Activity,
  Target,
} from 'lucide-react'
import apiClient, { apiPath } from '../lib/apiClient'
import type { AnalyticsSummary } from '../types'
import { useState } from 'react'
import { toast } from '../utils/toast'

const fetchAnalyticsSummary = async (): Promise<AnalyticsSummary> => {
  const { data } = await apiClient.get<AnalyticsSummary>(apiPath('analytics/summary'))
  return data
}

const fetchAnalyticsReport = async (): Promise<string> => {
  const { data } = await apiClient.get<{ report: string }>(apiPath('analytics/report'))
  return data.report
}

export default function Analytics() {
  const summaryQuery = useQuery({
    queryKey: ['analytics-summary'],
    queryFn: fetchAnalyticsSummary,
    refetchInterval: 60000,
  })

  const [report, setReport] = useState<string>('')
  const [isGenerating, setIsGenerating] = useState(false)

  const handleGenerateReport = async () => {
    try {
      setIsGenerating(true)
      const text = await fetchAnalyticsReport()
      setReport(text)
      toast.success('Analytics report ready')
    } finally {
      setIsGenerating(false)
    }
  }

  const copyReport = async () => {
    if (!report) return
    await navigator.clipboard.writeText(report)
    toast.success('Copied report to clipboard')
  }

  if (summaryQuery.isLoading || !summaryQuery.data) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[color:var(--osd-accent)]"></div>
      </div>
    )
  }

  const summary = summaryQuery.data

  return (
    <div className="px-4 py-6 sm:px-0 space-y-6">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Analytics</h2>
          <p className="text-gray-600 dark:text-gray-400">
            Unified analytics shared between the Tkinter shell and the React dashboard.
          </p>
        </div>
        <button
          onClick={() => summaryQuery.refetch()}
          className="inline-flex items-center px-4 py-2 rounded-md bg-primary-600 text-white text-sm font-medium hover:bg-primary-700"
        >
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <StatCard label="Completion Rate" value={`${summary.tasks.completion_rate}%`} icon={BarChart3} />
        <StatCard label="Active Projects" value={Object.keys(summary.projects).length.toString()} icon={Target} />
        <StatCard label="Logged Hours" value={`${summary.time_tracking.logged_hours}h`} icon={Activity} />
      </div>

      <section className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4 flex items-center">
          <BarChart3 className="w-5 h-5 mr-2 text-primary-500" />
          Task Status
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatusPill label="Done" value={summary.tasks.done} color="green" />
          <StatusPill label="In Progress" value={summary.tasks.in_progress} color="blue" />
          <StatusPill label="Todo" value={summary.tasks.todo} color="yellow" />
          <StatusPill label="Blocked" value={summary.tasks.blocked} color="red" />
        </div>
      </section>

      <section className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Project Health</h3>
          <div className="space-y-4 max-h-96 overflow-y-auto pr-2">
            {Object.entries(summary.project_health).map(([name, stats]) => (
              <div key={name} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                <div className="flex justify-between items-center mb-2">
                  <div>
                    <h4 className="text-base font-semibold text-gray-900 dark:text-white">{name}</h4>
                    <p className="text-xs text-gray-500 dark:text-gray-400">{stats.total_tasks} tasks</p>
                  </div>
                  <span className={`text-xs px-2 py-1 rounded-full capitalize ${healthColor(stats.health_status)}`}>
                    {stats.health_status}
                  </span>
                </div>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Completion: {stats.completion_rate}% · Blocked: {stats.blocked} · Overdue: {stats.overdue}
                </p>
                <div className="mt-2 w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1.5">
                  <div
                    className="bg-primary-500 h-1.5 rounded-full"
                    style={{ width: `${stats.completion_rate}%` }}
                  />
                </div>
              </div>
            ))}
            {Object.keys(summary.project_health).length === 0 && (
              <p className="text-sm text-gray-500 dark:text-gray-400">No project data yet.</p>
            )}
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Workload Distribution</h3>
          <div className="space-y-3">
            {Object.entries(summary.workload).map(([persona, stats]) => (
              <div key={persona} className="border border-gray-200 dark:border-gray-700 rounded-lg p-3 flex items-center justify-between">
                <div>
                  <p className="text-sm font-semibold text-gray-900 dark:text-white">{persona}</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {stats.task_count} tasks · {stats.estimated_hours}h est · {stats.logged_hours}h logged
                  </p>
                </div>
                <span className={`text-xs px-2 py-1 rounded-full ${stats.overloaded ? 'bg-rose-100 text-rose-600 dark:bg-rose-900/40 dark:text-rose-200' : 'bg-emerald-100 text-emerald-600 dark:bg-emerald-900/40 dark:text-emerald-200'}`}>
                  {stats.overloaded ? 'Overloaded' : 'Balanced'}
                </span>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4 flex items-center">
            <AlertTriangle className="w-5 h-5 mr-2 text-amber-500" />
            Deadline Reminders
          </h3>
          <div className="space-y-3 max-h-72 overflow-y-auto pr-2">
            {summary.deadline_reminders.length === 0 && (
              <p className="text-sm text-gray-500 dark:text-gray-400">No deadlines in the next week.</p>
            )}
            {summary.deadline_reminders.map((reminder) => (
              <div key={reminder.task_id} className="border border-gray-200 dark:border-gray-700 rounded-lg p-3">
                <p className="text-sm font-semibold text-gray-900 dark:text-white">{reminder.title}</p>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  {reminder.project} · Due in {reminder.days_until} days
                </p>
                <span className={`text-xs px-2 py-1 rounded-full mt-2 inline-block ${urgencyColor(reminder.urgency)}`}>
                  {reminder.urgency}
                </span>
              </div>
            ))}
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4 flex items-center">
            <Users className="w-5 h-5 mr-2 text-primary-500" />
            Smart Suggestions
          </h3>
          <div className="space-y-3 max-h-72 overflow-y-auto pr-2">
            {summary.suggestions.length === 0 && (
              <p className="text-sm text-gray-500 dark:text-gray-400">No suggestions right now.</p>
            )}
            {summary.suggestions.map((suggestion) => (
              <div key={`${suggestion.type}-${suggestion.task_id}`} className="border border-gray-200 dark:border-gray-700 rounded-lg p-3">
                <p className="text-sm font-semibold text-gray-900 dark:text-white">
                  {suggestion.message}
                </p>
                <span className={`text-xs px-2 py-1 rounded-full mt-2 inline-block ${urgencyColor(suggestion.priority as any)}`}>
                  {suggestion.priority}
                </span>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white">Analytics Report</h3>
          <div className="space-x-2">
            <button
              onClick={handleGenerateReport}
              disabled={isGenerating}
              className="inline-flex items-center px-3 py-2 rounded-md bg-primary-600 text-white text-sm font-medium hover:bg-primary-700 disabled:opacity-60"
            >
              <Download className="w-4 h-4 mr-1" />
              {isGenerating ? 'Generating…' : 'Generate Report'}
            </button>
            <button
              onClick={copyReport}
              disabled={!report}
              className="inline-flex items-center px-3 py-2 rounded-md border border-gray-300 dark:border-gray-600 text-sm font-medium text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-60"
            >
              <ClipboardCopy className="w-4 h-4 mr-1" />
              Copy
            </button>
          </div>
        </div>
        <textarea
          readOnly
          value={report}
          rows={8}
          className="w-full rounded-md border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-900 text-sm text-gray-900 dark:text-gray-100 p-3 font-mono resize-none"
          placeholder="Generate the report to view details..."
        />
      </section>
    </div>
  )
}

function urgencyColor(level: 'low' | 'medium' | 'high' | string) {
  switch (level) {
    case 'high':
      return 'bg-rose-100 text-rose-600 dark:bg-rose-900/40 dark:text-rose-200'
    case 'medium':
      return 'bg-amber-100 text-amber-600 dark:bg-amber-900/40 dark:text-amber-200'
    default:
      return 'bg-emerald-100 text-emerald-600 dark:bg-emerald-900/40 dark:text-emerald-200'
  }
}

function healthColor(status: string) {
  switch (status) {
    case 'healthy':
      return 'bg-emerald-100 text-emerald-600 dark:bg-emerald-900/40 dark:text-emerald-200'
    case 'warning':
      return 'bg-amber-100 text-amber-600 dark:bg-amber-900/40 dark:text-amber-200'
    default:
      return 'bg-rose-100 text-rose-600 dark:bg-rose-900/40 dark:text-rose-200'
  }
}

function StatCard({ label, value, icon: Icon }: { label: string; value: string; icon: React.ComponentType<{ className?: string }> }) {
  return (
    <div className="rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900/70 p-4 flex items-center justify-between">
      <div>
        <p className="text-xs text-gray-500 dark:text-gray-400">{label}</p>
        <p className="text-2xl font-semibold text-gray-900 dark:text-white">{value}</p>
      </div>
      <Icon className="w-6 h-6 text-primary-500" />
    </div>
  )
}

function StatusPill({ label, value, color }: { label: string; value: number; color: 'green' | 'blue' | 'yellow' | 'red' }) {
  const map = {
    green: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-200',
    blue: 'bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-200',
    yellow: 'bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-200',
    red: 'bg-rose-100 text-rose-700 dark:bg-rose-900/40 dark:text-rose-200',
  } as const
  return (
    <div className={`rounded-lg p-3 text-center ${map[color]}`}>
      <p className="text-xs uppercase tracking-wide">{label}</p>
      <p className="text-2xl font-semibold">{value}</p>
    </div>
  )
}
