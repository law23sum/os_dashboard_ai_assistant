import { useState, useEffect } from 'react'
import { RefreshCw, Loader2, GitBranch, Terminal, FileCode } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import apiClient, { apiPath } from '../lib/apiClient'

interface ChangeMonitorProps {
  className?: string
  chatMessages?: Array<{ id: number; kind?: string; persona?: string; content?: string; created_at?: string }>
}

interface ChangeLogData {
  working_tree: string
  recent_commits: string
  agent_activity: string
}

const fetchChangeLog = async (): Promise<ChangeLogData> => {
  try {
    const { data } = await apiClient.get<ChangeLogData>(apiPath('git/change-log'))
    return data
  } catch (error) {
    // Fallback if endpoint doesn't exist
    return {
      working_tree: '(unavailable)',
      recent_commits: '(unavailable)',
      agent_activity: 'No recent agent commands yet.',
    }
  }
}

export default function ChangeMonitor({ className = '', chatMessages = [] }: ChangeMonitorProps) {
  const [isRefreshing, setIsRefreshing] = useState(false)

  const { data: changeLog, refetch } = useQuery({
    queryKey: ['change-log'],
    queryFn: fetchChangeLog,
    refetchInterval: 10000, // Refresh every 10 seconds
  })

  // Summarize agent activity from chat messages
  const summarizeAgentActivity = (): string => {
    const recentActions = chatMessages
      .filter((msg) => msg.kind === 'terminal' || msg.kind === 'terminal_result')
      .slice(-10)

    if (recentActions.length === 0) {
      return 'No recent agent commands yet.'
    }

    return recentActions
      .map((msg) => {
        const timestamp = msg.created_at
          ? new Date(msg.created_at).toLocaleString()
          : 'Unknown time'
        const firstLine = msg.content?.split('\n')[0] || ''
        return `[${timestamp}] ${msg.persona || 'Agent'}: ${firstLine}`
      })
      .join('\n')
  }

  const handleRefresh = async () => {
    setIsRefreshing(true)
    await refetch()
    setTimeout(() => setIsRefreshing(false), 500)
  }

  const agentActivity = summarizeAgentActivity()
  const displayData = changeLog || {
    working_tree: '(loading...)',
    recent_commits: '(loading...)',
    agent_activity: agentActivity,
  }

  return (
    <div className={`flex flex-col bg-slate-900/50 border-t border-slate-700/50 ${className}`}>
      {/* Header */}
      <div className="p-3 border-b border-slate-700/50 bg-slate-900/70 backdrop-blur-sm">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <FileCode className="w-4 h-4 text-primary-400" />
            <h4 className="text-xs font-semibold text-slate-200 uppercase tracking-wider">Live Change Monitor</h4>
          </div>
          <button
            onClick={handleRefresh}
            disabled={isRefreshing}
            className="flex items-center gap-1.5 px-2.5 py-1.5 bg-slate-800/80 hover:bg-slate-700 border border-slate-700/50 text-slate-300 rounded-lg transition-colors text-[11px] disabled:opacity-50"
            title="Refresh change log"
          >
            {isRefreshing ? (
              <Loader2 className="w-3 h-3 animate-spin" />
            ) : (
              <RefreshCw className="w-3 h-3" />
            )}
            Refresh
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4">
        <div className="space-y-3">
          {/* Working Tree */}
          <div className="bg-slate-900/40 border border-slate-700/50 rounded-lg p-3">
            <div className="flex items-center gap-2 mb-2">
              <GitBranch className="w-4 h-4 text-primary-400" />
              <h5 className="text-xs font-semibold text-slate-200 uppercase tracking-wider">Working Tree</h5>
            </div>
            <div className="bg-slate-900/60 border border-slate-700/60 rounded-lg p-3 text-[11px] text-slate-300 whitespace-pre-wrap font-mono leading-relaxed max-h-32 overflow-y-auto">
              {displayData.working_tree || '(clean or unavailable)'}
            </div>
          </div>

          {/* Recent Commits */}
          <div className="bg-slate-900/40 border border-slate-700/50 rounded-lg p-3">
            <div className="flex items-center gap-2 mb-2">
              <FileCode className="w-4 h-4 text-primary-400" />
              <h5 className="text-xs font-semibold text-slate-200 uppercase tracking-wider">Recent Commits</h5>
            </div>
            <div className="bg-slate-900/60 border border-slate-700/60 rounded-lg p-3 text-[11px] text-slate-300 whitespace-pre-wrap font-mono leading-relaxed max-h-32 overflow-y-auto">
              {displayData.recent_commits || '(unavailable)'}
            </div>
          </div>

          {/* Agent Activity */}
          <div className="bg-slate-900/40 border border-slate-700/50 rounded-lg p-3">
            <div className="flex items-center gap-2 mb-2">
              <Terminal className="w-4 h-4 text-primary-400" />
              <h5 className="text-xs font-semibold text-slate-200 uppercase tracking-wider">Agent Activity</h5>
            </div>
            <div className="bg-slate-900/60 border border-slate-700/60 rounded-lg p-3 text-[11px] text-slate-300 whitespace-pre-wrap font-mono leading-relaxed max-h-32 overflow-y-auto">
              {agentActivity || 'No recent agent commands yet.'}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

