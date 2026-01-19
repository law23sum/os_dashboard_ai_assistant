import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import {
  AlertTriangle,
  Bot,
  Check,
  CheckCircle,
  ChevronDown,
  ChevronRight,
  Clock,
  Code,
  FileCode,
  Filter,
  History,
  RefreshCw,
  Settings,
  Shield,
  Sparkles,
  Target,
  TrendingUp,
  Wrench,
  X,
  XCircle,
  Zap,
  Activity,
} from 'lucide-react'
import apiClient, { apiPath } from '../lib/apiClient'
import { toast } from '../utils/toast'

interface AutoFixIssue {
  id: string
  file_path: string
  line_number: number | null
  issue_type: 'error' | 'warning' | 'lint' | 'security' | 'performance'
  description: string
  severity: 'critical' | 'error' | 'warning' | 'info'
  detected_at: string
  status: 'pending' | 'analyzing' | 'fixing' | 'applied' | 'failed' | 'skipped'
  ai_analysis: string | null
  proposed_fix: string | null
  confidence: number
}

interface AutoFixReport {
  id: string
  started_at: string
  completed_at: string | null
  status: 'running' | 'completed' | 'failed'
  issues_detected: number
  issues_fixed: number
  issues_skipped: number
  summary: string
}

interface AutoFixConfig {
  enabled: boolean
  auto_apply_threshold: number
  scan_interval_seconds: number
  target_directories: string[]
  issue_types: string[]
}

interface AutoFixData {
  enabled: boolean
  last_scan: string | null
  issues_pending: number
  issues: AutoFixIssue[]
  reports: AutoFixReport[]
  config: AutoFixConfig
}

const fetchAutoFixData = async (): Promise<AutoFixData> => {
  try {
    const [status, issues, reports, config] = await Promise.all([
      apiClient.get(apiPath('autofix/status')).catch(() => ({ data: {} })),
      apiClient.get(apiPath('autofix/issues')).catch(() => ({ data: [] })),
      apiClient.get(apiPath('autofix/reports')).catch(() => ({ data: [] })),
      apiClient.get(apiPath('autofix/config')).catch(() => ({ data: {} })),
    ])

    // Demo data for showcase
    const demoIssues: AutoFixIssue[] = (issues.data || []).length > 0 ? issues.data : [
      {
        id: 'issue-1',
        file_path: 'frontend/src/pages/Dashboard.tsx',
        line_number: 142,
        issue_type: 'lint',
        description: 'Missing dependency in useEffect dependency array',
        severity: 'warning',
        detected_at: new Date(Date.now() - 3600000).toISOString(),
        status: 'pending',
        ai_analysis: 'The useEffect hook references `settings` but it\'s not listed in the dependency array.',
        proposed_fix: 'Add `settings` to the dependency array: [settings]',
        confidence: 0.92,
      },
      {
        id: 'issue-2',
        file_path: 'backend_api/routers/projects.py',
        line_number: 87,
        issue_type: 'security',
        description: 'Potential SQL injection vulnerability in dynamic query',
        severity: 'critical',
        detected_at: new Date(Date.now() - 7200000).toISOString(),
        status: 'pending',
        ai_analysis: 'User input is being directly interpolated into SQL query. Use parameterized queries instead.',
        proposed_fix: 'Replace string interpolation with SQLAlchemy bind parameters',
        confidence: 0.98,
      },
      {
        id: 'issue-3',
        file_path: 'assistant_core/automation_orchestrator.py',
        line_number: 234,
        issue_type: 'error',
        description: 'Unhandled exception in async task runner',
        severity: 'error',
        detected_at: new Date(Date.now() - 1800000).toISOString(),
        status: 'analyzing',
        ai_analysis: 'The async function lacks proper exception handling which can cause silent failures.',
        proposed_fix: 'Wrap the async call in try/except with proper logging',
        confidence: 0.85,
      },
      {
        id: 'issue-4',
        file_path: 'frontend/src/hooks/useSettings.ts',
        line_number: 45,
        issue_type: 'performance',
        description: 'Expensive computation in render path without memoization',
        severity: 'warning',
        detected_at: new Date(Date.now() - 5400000).toISOString(),
        status: 'applied',
        ai_analysis: 'The settings transformation runs on every render. Use useMemo to cache the result.',
        proposed_fix: 'Wrap the transformation in useMemo with appropriate dependencies',
        confidence: 0.88,
      },
    ]

    const demoReports: AutoFixReport[] = (reports.data || []).length > 0 ? reports.data : [
      {
        id: 'report-1',
        started_at: new Date(Date.now() - 86400000).toISOString(),
        completed_at: new Date(Date.now() - 86300000).toISOString(),
        status: 'completed',
        issues_detected: 12,
        issues_fixed: 8,
        issues_skipped: 4,
        summary: 'Fixed 8 lint issues and 2 performance optimizations across 15 files.',
      },
      {
        id: 'report-2',
        started_at: new Date(Date.now() - 172800000).toISOString(),
        completed_at: new Date(Date.now() - 172700000).toISOString(),
        status: 'completed',
        issues_detected: 5,
        issues_fixed: 5,
        issues_skipped: 0,
        summary: 'All issues resolved successfully. No manual review required.',
      },
    ]

    return {
      enabled: status.data?.enabled ?? true,
      last_scan: status.data?.last_scan ?? new Date(Date.now() - 3600000).toISOString(),
      issues_pending: demoIssues.filter((i) => i.status === 'pending').length,
      issues: demoIssues,
      reports: demoReports,
      config: config.data || {
        enabled: true,
        auto_apply_threshold: 0.9,
        scan_interval_seconds: 3600,
        target_directories: ['frontend/', 'backend_api/', 'assistant_core/'],
        issue_types: ['error', 'warning', 'lint', 'security', 'performance'],
      },
    }
  } catch {
    return {
      enabled: false,
      last_scan: null,
      issues_pending: 0,
      issues: [],
      reports: [],
      config: {
        enabled: false,
        auto_apply_threshold: 0.9,
        scan_interval_seconds: 3600,
        target_directories: [],
        issue_types: [],
      },
    }
  }
}

const severityColors: Record<string, string> = {
  critical: 'bg-red-500/20 text-red-400 border-red-500/30',
  error: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
  warning: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
  info: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
}

const statusColors: Record<string, string> = {
  pending: 'bg-slate-500/20 text-slate-400 border-slate-500/30',
  analyzing: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  fixing: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
  applied: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
  failed: 'bg-red-500/20 text-red-400 border-red-500/30',
  skipped: 'bg-slate-500/20 text-slate-400 border-slate-500/30',
}

const typeIcons: Record<string, React.ReactNode> = {
  error: <XCircle className="w-4 h-4" />,
  warning: <AlertTriangle className="w-4 h-4" />,
  lint: <Code className="w-4 h-4" />,
  security: <Shield className="w-4 h-4" />,
  performance: <Zap className="w-4 h-4" />,
}

const IssueCard = ({
  issue,
  onApply,
  onSkip,
  expanded,
  onToggle,
}: {
  issue: AutoFixIssue
  onApply: (id: string) => void
  onSkip: (id: string) => void
  expanded: boolean
  onToggle: () => void
}) => (
  <div className="glass-card group hover:border-white/20 transition-all">
    <div className="flex items-start gap-4">
      <div className={`p-2 rounded-lg border ${severityColors[issue.severity]}`}>
        {typeIcons[issue.issue_type]}
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-start justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className={`px-2 py-0.5 rounded text-xs font-medium border ${statusColors[issue.status]}`}>
                {issue.status}
              </span>
              <span className={`px-2 py-0.5 rounded text-xs font-medium border ${severityColors[issue.severity]}`}>
                {issue.severity}
              </span>
            </div>
            <p className="text-sm text-white mt-2">{issue.description}</p>
            <p className="text-xs text-slate-400 mt-1 flex items-center gap-2">
              <FileCode className="w-3 h-3" />
              {issue.file_path}
              {issue.line_number && <span>:{issue.line_number}</span>}
            </p>
          </div>
          <div className="flex items-center gap-2">
            {issue.status === 'pending' && (
              <>
                <button
                  onClick={() => onApply(issue.id)}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-500/20 text-emerald-400 text-xs font-medium hover:bg-emerald-500/30 transition-colors"
                >
                  <Check className="w-3.5 h-3.5" />
                  Apply Fix
                </button>
                <button
                  onClick={() => onSkip(issue.id)}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-500/20 text-slate-400 text-xs font-medium hover:bg-slate-500/30 transition-colors"
                >
                  <X className="w-3.5 h-3.5" />
                  Skip
                </button>
              </>
            )}
            <button
              onClick={onToggle}
              className="p-2 rounded-lg hover:bg-white/10 transition-colors"
            >
              {expanded ? (
                <ChevronDown className="w-4 h-4 text-slate-400" />
              ) : (
                <ChevronRight className="w-4 h-4 text-slate-400" />
              )}
            </button>
          </div>
        </div>

        {expanded && (
          <div className="mt-4 space-y-3">
            {issue.ai_analysis && (
              <div className="p-3 rounded-lg bg-indigo-500/10 border border-indigo-500/20">
                <div className="flex items-center gap-2 mb-2">
                  <Bot className="w-4 h-4 text-indigo-400" />
                  <p className="text-xs font-medium text-indigo-400">AI Analysis</p>
                </div>
                <p className="text-sm text-slate-300">{issue.ai_analysis}</p>
              </div>
            )}
            {issue.proposed_fix && (
              <div className="p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20">
                <div className="flex items-center gap-2 mb-2">
                  <Wrench className="w-4 h-4 text-emerald-400" />
                  <p className="text-xs font-medium text-emerald-400">Proposed Fix</p>
                </div>
                <p className="text-sm text-slate-300 font-mono">{issue.proposed_fix}</p>
              </div>
            )}
            <div className="flex items-center gap-4 text-xs text-slate-400">
              <span className="flex items-center gap-1">
                <Target className="w-3 h-3" />
                Confidence: {(issue.confidence * 100).toFixed(0)}%
              </span>
              <span className="flex items-center gap-1">
                <Clock className="w-3 h-3" />
                {new Date(issue.detected_at).toLocaleString()}
              </span>
            </div>
          </div>
        )}
      </div>
    </div>
  </div>
)

const ReportCard = ({ report }: { report: AutoFixReport }) => (
  <div className="p-4 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 transition-colors">
    <div className="flex items-center justify-between mb-3">
      <div className="flex items-center gap-3">
        <div className={`p-2 rounded-lg ${
          report.status === 'completed' ? 'bg-emerald-500/20' : 
          report.status === 'running' ? 'bg-blue-500/20' : 'bg-red-500/20'
        }`}>
          {report.status === 'completed' ? (
            <CheckCircle className="w-4 h-4 text-emerald-400" />
          ) : report.status === 'running' ? (
            <RefreshCw className="w-4 h-4 text-blue-400 animate-spin" />
          ) : (
            <XCircle className="w-4 h-4 text-red-400" />
          )}
        </div>
        <div>
          <p className="text-sm font-medium text-white">
            {new Date(report.started_at).toLocaleDateString()}
          </p>
          <p className="text-xs text-slate-400">
            {new Date(report.started_at).toLocaleTimeString()}
          </p>
        </div>
      </div>
      <div className="text-right">
        <p className="text-lg font-bold text-white">{report.issues_fixed}/{report.issues_detected}</p>
        <p className="text-xs text-slate-400">Fixed</p>
      </div>
    </div>
    <p className="text-sm text-slate-300">{report.summary}</p>
  </div>
)

export default function AutoFix() {
  const queryClient = useQueryClient()
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [expandedIssue, setExpandedIssue] = useState<string | null>(null)
  const [isConfigOpen, setIsConfigOpen] = useState(false)
  const [configDraft, setConfigDraft] = useState<AutoFixConfig | null>(null)
  const [directoryInput, setDirectoryInput] = useState('')

  const { data, isLoading } = useQuery({
    queryKey: ['autofix'],
    queryFn: fetchAutoFixData,
    refetchInterval: 30000,
  })

  const scanMutation = useMutation({
    mutationFn: () => apiClient.post(apiPath('autofix/scan')),
    onSuccess: () => {
      toast.success('Scan initiated')
      queryClient.invalidateQueries({ queryKey: ['autofix'] })
    },
    onError: () => toast.error('Failed to start scan'),
  })

  const applyMutation = useMutation({
    mutationFn: (issueId: string) => apiClient.post(apiPath(`autofix/issues/${issueId}/apply`)),
    onSuccess: () => {
      toast.success('Fix applied successfully')
      queryClient.invalidateQueries({ queryKey: ['autofix'] })
    },
    onError: () => toast.error('Failed to apply fix'),
  })

  const skipMutation = useMutation({
    mutationFn: (issueId: string) => apiClient.post(apiPath(`autofix/issues/${issueId}/skip`)),
    onSuccess: () => {
      toast.info('Issue skipped')
      queryClient.invalidateQueries({ queryKey: ['autofix'] })
    },
    onError: () => toast.error('Failed to skip issue'),
  })

  const updateConfigMutation = useMutation({
    mutationFn: (payload: AutoFixConfig) => apiClient.put(apiPath('autofix/config'), payload),
    onSuccess: () => {
      toast.success('Configuration saved')
      queryClient.invalidateQueries({ queryKey: ['autofix'] })
      setIsConfigOpen(false)
    },
    onError: () => toast.error('Failed to update configuration'),
  })

  const openConfigModal = () => {
    if (!data?.config) return
    setConfigDraft({
      ...data.config,
      target_directories: [...data.config.target_directories],
      issue_types: [...data.config.issue_types],
    })
    setDirectoryInput('')
    setIsConfigOpen(true)
  }

  const handleAddDirectory = () => {
    if (!configDraft) return
    const next = directoryInput.trim()
    if (!next) return
    if (!configDraft.target_directories.includes(next)) {
      setConfigDraft({ ...configDraft, target_directories: [...configDraft.target_directories, next] })
    }
    setDirectoryInput('')
  }

  const removeDirectory = (dir: string) => {
    if (!configDraft) return
    setConfigDraft({
      ...configDraft,
      target_directories: configDraft.target_directories.filter((item) => item !== dir),
    })
  }

  const toggleIssueType = (issueType: string) => {
    if (!configDraft) return
    const exists = configDraft.issue_types.includes(issueType)
    setConfigDraft({
      ...configDraft,
      issue_types: exists
        ? configDraft.issue_types.filter((item) => item !== issueType)
        : [...configDraft.issue_types, issueType],
    })
  }

  const handleSaveConfig = () => {
    if (!configDraft) return
    updateConfigMutation.mutate(configDraft)
  }

  const filteredIssues = data?.issues.filter(
    (issue) => statusFilter === 'all' || issue.status === statusFilter
  ) || []

  if (isLoading) {
    return (
      <div className="px-4 py-6 sm:px-0">
        <div className="glass-card flex h-72 items-center justify-center">
          <div className="h-12 w-12 animate-spin rounded-full border-2 border-white/30 border-t-white" />
        </div>
      </div>
    )
  }

  const pendingCount = data?.issues.filter((i) => i.status === 'pending').length || 0
  const appliedCount = data?.issues.filter((i) => i.status === 'applied').length || 0
  const criticalCount = data?.issues.filter((i) => i.severity === 'critical' && i.status === 'pending').length || 0

  const { data: orchestratorStatus } = useQuery({
    queryKey: ['orchestratorStatus'],
    queryFn: async () => {
      try {
        const res = await fetch('/autofix_status.json')
        return await res.json()
      } catch {
        return null
      }
    },
    refetchInterval: 5000,
  })

  return (
    <div className="px-4 py-6 sm:px-0 space-y-8 text-slate-100">
      {/* Orchestrator Status Banner */}
      {orchestratorStatus && (
        <div className="glass-card border-l-4 border-l-emerald-500 bg-emerald-500/10 p-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
                <Activity className="w-5 h-5 text-emerald-400 animate-pulse" />
                <div>
                    <p className="font-medium text-emerald-200">Orchestrator Active</p>
                    <p className="text-xs text-emerald-400/70">Last update: {orchestratorStatus.last_update} — {orchestratorStatus.last_message}</p>
                </div>
            </div>
        </div>
      )}

      {/* Header */}
      <section className="glass-card relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/20 via-teal-500/10 to-cyan-500/10" />
        <div className="relative flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <p className="eyebrow-text flex items-center gap-2">
              <Wrench className="w-4 h-4" />
              Self-Healing System
            </p>
            <h1 className="mt-2 text-3xl font-semibold text-white">Auto-Fix Console</h1>
            <p className="mt-3 max-w-2xl text-sm text-slate-300">
              AI-powered issue detection and automated remediation across the codebase. 
              Review, approve, and track fixes with full audit trail.
            </p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={() => scanMutation.mutate()}
              disabled={scanMutation.isPending}
              className="btn-tonal flex items-center gap-2"
            >
              <RefreshCw className={`w-4 h-4 ${scanMutation.isPending ? 'animate-spin' : ''}`} />
              {scanMutation.isPending ? 'Scanning...' : 'Run Scan'}
            </button>
            <button
              type="button"
              onClick={openConfigModal}
              className="btn-tonal flex items-center gap-2"
            >
              <Settings className="w-4 h-4" />
              Configure
            </button>
          </div>
        </div>
      </section>

      {/* Stats */}
      <div className="grid gap-4 sm:grid-cols-4">
        <div className="glass-card relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-amber-500/20 via-transparent to-orange-500/10" />
          <div className="relative">
            <p className="eyebrow-text">Pending Issues</p>
            <p className="text-3xl font-bold text-white mt-2">{pendingCount}</p>
            <p className="text-sm text-slate-300 mt-1">Awaiting review</p>
          </div>
        </div>
        <div className="glass-card relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-red-500/20 via-transparent to-pink-500/10" />
          <div className="relative">
            <p className="eyebrow-text">Critical</p>
            <p className="text-3xl font-bold text-white mt-2">{criticalCount}</p>
            <p className="text-sm text-slate-300 mt-1">High priority</p>
          </div>
        </div>
        <div className="glass-card relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/20 via-transparent to-teal-500/10" />
          <div className="relative">
            <p className="eyebrow-text">Fixed</p>
            <p className="text-3xl font-bold text-white mt-2">{appliedCount}</p>
            <p className="text-sm text-slate-300 mt-1">Auto-remediated</p>
          </div>
        </div>
        <div className="glass-card relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/20 via-transparent to-purple-500/10" />
          <div className="relative flex items-center gap-3">
            <Sparkles className="w-8 h-8 text-indigo-400" />
            <div>
              <p className="eyebrow-text">Confidence</p>
              <p className="text-3xl font-bold text-white">
                {data?.config.auto_apply_threshold ? `${(data.config.auto_apply_threshold * 100).toFixed(0)}%` : 'N/A'}
              </p>
              <p className="text-sm text-slate-300">Auto-apply threshold</p>
            </div>
          </div>
        </div>
      </div>

      {/* Issues List */}
      <section>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <AlertTriangle className="w-5 h-5 text-amber-400" />
            <h2 className="text-xl font-semibold text-white">Detected Issues</h2>
          </div>
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-slate-400" />
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white"
            >
              <option value="all">All Status</option>
              <option value="pending">Pending</option>
              <option value="analyzing">Analyzing</option>
              <option value="applied">Applied</option>
              <option value="skipped">Skipped</option>
              <option value="failed">Failed</option>
            </select>
          </div>
        </div>

        <div className="space-y-4">
          {filteredIssues.length === 0 ? (
            <div className="glass-card text-center py-12">
              <CheckCircle className="w-12 h-12 mx-auto mb-4 text-emerald-400 opacity-50" />
              <p className="text-slate-400">No issues found</p>
              <p className="text-xs text-slate-500 mt-1">Run a scan to detect new issues</p>
            </div>
          ) : (
            filteredIssues.map((issue) => (
              <IssueCard
                key={issue.id}
                issue={issue}
                onApply={(id) => applyMutation.mutate(id)}
                onSkip={(id) => skipMutation.mutate(id)}
                expanded={expandedIssue === issue.id}
                onToggle={() => setExpandedIssue(expandedIssue === issue.id ? null : issue.id)}
              />
            ))
          )}
        </div>
      </section>

      {/* Recent Reports */}
      <section className="glass-card">
        <div className="flex items-center gap-3 mb-6">
          <History className="w-5 h-5 text-indigo-400" />
          <div>
            <h2 className="text-xl font-semibold text-white">Recent Scan Reports</h2>
            <p className="text-sm text-slate-400">History of auto-fix runs</p>
          </div>
        </div>

        <div className="space-y-3">
          {data?.reports.map((report) => (
            <ReportCard key={report.id} report={report} />
          ))}
        </div>
      </section>

      {/* v1000 Banner */}
      <section className="glass-card border border-dashed border-emerald-500/30 bg-gradient-to-r from-emerald-500/10 via-teal-500/10 to-cyan-500/10">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center">
            <TrendingUp className="w-6 h-6 text-white" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-white">Version 1000 Auto-Fix</h3>
            <p className="text-sm text-slate-300">
              Coming soon: Multi-repo scanning, CI/CD integration, regression test generation,
              and ML-powered fix confidence calibration.
            </p>
          </div>
        </div>
      </section>

      {isConfigOpen && configDraft && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 px-4 py-8"
          role="dialog"
          aria-modal="true"
        >
          <div className="w-full max-w-2xl rounded-3xl border border-white/10 bg-slate-900/90 p-6 shadow-2xl backdrop-blur">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="eyebrow-text flex items-center gap-2">
                  <Settings className="w-4 h-4" />
                  Auto-Fix Configuration
                </p>
                <h3 className="mt-2 text-2xl font-semibold text-white">Tune remediation settings</h3>
                <p className="text-sm text-slate-300">
                  Spec 5.12 & 8.13 call for operator controls across scan cadence, directories, and thresholds.
                </p>
              </div>
              <button
                type="button"
                onClick={() => setIsConfigOpen(false)}
                className="rounded-full border border-white/10 p-2 text-slate-400 hover:bg-white/5 hover:text-white"
                aria-label="Close Auto-Fix configuration panel"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="mt-6 space-y-6">
              <div className="flex items-center justify-between rounded-2xl border border-white/10 bg-white/5 p-4">
                <div>
                  <p className="text-sm text-slate-300">Auto-apply fixes</p>
                  <p className="text-xs text-slate-400">Let high-confidence patches apply automatically with audit logging.</p>
                </div>
                <button
                  type="button"
                  onClick={() => setConfigDraft({ ...configDraft, enabled: !configDraft.enabled })}
                  className={`relative inline-flex h-8 w-16 items-center rounded-full border ${configDraft.enabled ? 'border-emerald-400 bg-emerald-500/20' : 'border-white/15 bg-white/10'}`}
                >
                  <span
                    className={`inline-block h-6 w-6 transform rounded-full bg-white transition ${configDraft.enabled ? 'translate-x-8' : 'translate-x-1'}`}
                  />
                </button>
              </div>

              <div>
                <div className="flex items-center justify-between text-sm text-slate-300">
                  <span>Auto-apply threshold</span>
                  <span className="text-white font-semibold">{(configDraft.auto_apply_threshold * 100).toFixed(0)}%</span>
                </div>
                <input
                  type="range"
                  min={50}
                  max={100}
                  value={Math.round(configDraft.auto_apply_threshold * 100)}
                  onChange={(event) =>
                    setConfigDraft({
                      ...configDraft,
                      auto_apply_threshold: Number(event.target.value) / 100,
                    })
                  }
                  className="mt-2 w-full accent-emerald-400"
                />
              </div>

              <div className="grid gap-6 md:grid-cols-2">
                <label className="flex flex-col space-y-1 text-sm text-slate-300">
                  Scan interval (seconds)
                  <input
                    type="number"
                    min={300}
                    step={60}
                    value={configDraft.scan_interval_seconds}
                    onChange={(event) =>
                      setConfigDraft({
                        ...configDraft,
                        scan_interval_seconds: Number(event.target.value),
                      })
                    }
                    className="rounded-2xl border border-white/10 bg-white/5 px-3 py-2 text-white focus:border-white/30 focus:outline-none"
                  />
                  <span className="text-xs text-slate-500">
                    ~{Math.round(configDraft.scan_interval_seconds / 60)} minutes between scans
                  </span>
                </label>
                <div>
                  <p className="text-sm text-slate-300 mb-2">Issue types</p>
                  <div className="flex flex-wrap gap-2">
                    {['error', 'warning', 'lint', 'security', 'performance'].map((type) => {
                      const active = configDraft.issue_types.includes(type)
                      return (
                        <button
                          key={type}
                          type="button"
                          onClick={() => toggleIssueType(type)}
                          className={`rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em] ${
                            active
                              ? 'bg-emerald-500/20 text-emerald-200 border border-emerald-500/40'
                              : 'bg-white/5 text-slate-300 border border-white/10'
                          }`}
                        >
                          {type}
                        </button>
                      )
                    })}
                  </div>
                </div>
              </div>

              <div>
                <p className="text-sm text-slate-300">Target directories</p>
                <div className="mt-2 flex flex-wrap gap-2">
                  {configDraft.target_directories.map((dir) => (
                    <span
                      key={dir}
                      className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-white"
                    >
                      {dir}
                      <button
                        type="button"
                        onClick={() => removeDirectory(dir)}
                        className="text-slate-400 hover:text-white"
                        aria-label={`Remove ${dir}`}
                      >
                        <X className="w-3 h-3" />
                      </button>
                    </span>
                  ))}
                  {configDraft.target_directories.length === 0 && (
                    <span className="rounded-full border border-dashed border-white/20 px-3 py-1 text-xs text-slate-400">
                      No directories selected
                    </span>
                  )}
                </div>
                <div className="mt-3 flex gap-3">
                  <input
                    type="text"
                    placeholder="e.g. frontend/"
                    value={directoryInput}
                    onChange={(event) => setDirectoryInput(event.target.value)}
                    onKeyDown={(event) => {
                      if (event.key === 'Enter') {
                        event.preventDefault()
                        handleAddDirectory()
                      }
                    }}
                    className="flex-1 rounded-2xl border border-white/10 bg-white/5 px-3 py-2 text-white focus:border-white/30 focus:outline-none"
                  />
                  <button
                    type="button"
                    onClick={handleAddDirectory}
                    className="rounded-2xl border border-white/10 bg-white/10 px-4 py-2 text-sm font-semibold text-white hover:border-white/30"
                  >
                    Add
                  </button>
                </div>
              </div>
            </div>

            <div className="mt-6 flex justify-end gap-3">
              <button
                type="button"
                onClick={() => setIsConfigOpen(false)}
                className="rounded-2xl border border-white/10 px-4 py-2 text-sm font-semibold text-slate-300 hover:border-white/30"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleSaveConfig}
                disabled={updateConfigMutation.isPending}
                className="rounded-2xl bg-emerald-500/20 px-5 py-2 text-sm font-semibold text-emerald-200 hover:bg-emerald-500/30 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {updateConfigMutation.isPending ? 'Saving...' : 'Save changes'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}





