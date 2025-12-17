import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import {
  ArrowRight,
  Bot,
  CheckCircle,
  Clock,
  Layers,
  Play,
  RefreshCw,
  Send,
  Sparkles,
  Target,
  XCircle,
  Zap,
} from 'lucide-react'
import apiClient, { apiPath } from '../lib/apiClient'
import { toast } from '../utils/toast'

interface IntentRequest {
  id: string
  query: string
  status: 'planning' | 'executing' | 'completed' | 'failed'
  priority: 'low' | 'normal' | 'high' | 'critical'
  created_at: string
  steps_total: number
  steps_completed: number
  final_result?: string
}

const fetchIntents = async (): Promise<IntentRequest[]> => {
  try {
    const response = await apiClient.get(apiPath('intents?limit=20'))
    return response.data || []
  } catch {
    // Demo data
    return [
      {
        id: 'int-1',
        query: 'Analyze project health and generate risk report',
        status: 'completed',
        priority: 'high',
        created_at: new Date(Date.now() - 3600000).toISOString(),
        steps_total: 4,
        steps_completed: 4,
        final_result: 'Report generated successfully with 3 risk factors identified.',
      },
      {
        id: 'int-2',
        query: 'Sync all Microsoft Graph documents to local storage',
        status: 'executing',
        priority: 'normal',
        created_at: new Date(Date.now() - 1800000).toISOString(),
        steps_total: 6,
        steps_completed: 3,
      },
      {
        id: 'int-3',
        query: 'Run security scan on backend API endpoints',
        status: 'planning',
        priority: 'critical',
        created_at: new Date(Date.now() - 600000).toISOString(),
        steps_total: 0,
        steps_completed: 0,
      },
    ]
  }
}

const statusStyles: Record<string, { bg: string; text: string; icon: React.ReactNode }> = {
  planning: { bg: 'bg-blue-500/20', text: 'text-blue-400', icon: <Bot className="w-4 h-4" /> },
  executing: { bg: 'bg-amber-500/20', text: 'text-amber-400', icon: <RefreshCw className="w-4 h-4 animate-spin" /> },
  completed: { bg: 'bg-emerald-500/20', text: 'text-emerald-400', icon: <CheckCircle className="w-4 h-4" /> },
  failed: { bg: 'bg-red-500/20', text: 'text-red-400', icon: <XCircle className="w-4 h-4" /> },
}

const priorityStyles: Record<string, string> = {
  low: 'bg-slate-500/20 text-slate-400',
  normal: 'bg-blue-500/20 text-blue-400',
  high: 'bg-amber-500/20 text-amber-400',
  critical: 'bg-red-500/20 text-red-400',
}

export default function IntentProcessor() {
  const queryClient = useQueryClient()
  const [query, setQuery] = useState('')
  const [priority, setPriority] = useState<'low' | 'normal' | 'high' | 'critical'>('normal')

  const { data: intents = [], isLoading } = useQuery({
    queryKey: ['intents'],
    queryFn: fetchIntents,
    refetchInterval: 10000,
  })

  const submitMutation = useMutation({
    mutationFn: async () => {
      await apiClient.post(apiPath('intents'), { query, priority })
    },
    onSuccess: () => {
      toast.success('Intent submitted')
      setQuery('')
      queryClient.invalidateQueries({ queryKey: ['intents'] })
    },
    onError: () => toast.error('Failed to submit intent'),
  })

  if (isLoading) {
    return (
      <div className="px-4 py-6 sm:px-0">
        <div className="glass-card flex h-72 items-center justify-center">
          <div className="h-12 w-12 animate-spin rounded-full border-2 border-white/30 border-t-white" />
        </div>
      </div>
    )
  }

  return (
    <div className="px-4 py-6 sm:px-0 space-y-8 text-slate-100">
      {/* Header */}
      <section className="glass-card relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/20 via-purple-500/10 to-pink-500/10" />
        <div className="relative">
          <p className="eyebrow-text flex items-center gap-2">
            <Zap className="w-4 h-4" />
            AI-Driven Orchestration
          </p>
          <h1 className="mt-2 text-3xl font-semibold text-white">Intent Processor</h1>
          <p className="mt-3 max-w-2xl text-sm text-slate-300">
            Submit natural language intents and let the AI decompose them into executable steps 
            across drivers. Track progress and view reasoning traces in real-time.
          </p>
        </div>
      </section>

      {/* Submit Intent */}
      <section className="glass-card">
        <div className="flex items-center gap-3 mb-4">
          <Send className="w-5 h-5 text-indigo-400" />
          <h2 className="text-xl font-semibold text-white">Submit Intent</h2>
        </div>
        <div className="flex flex-col sm:flex-row gap-4">
          <input
            type="text"
            placeholder="Describe what you want to accomplish..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="flex-1 px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder-slate-400 focus:outline-none focus:border-white/30"
          />
          <select
            value={priority}
            onChange={(e) => setPriority(e.target.value as typeof priority)}
            className="px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white"
          >
            <option value="low">Low</option>
            <option value="normal">Normal</option>
            <option value="high">High</option>
            <option value="critical">Critical</option>
          </select>
          <button
            onClick={() => submitMutation.mutate()}
            disabled={!query.trim() || submitMutation.isPending}
            className="btn-tonal flex items-center gap-2 px-6"
          >
            <Play className="w-4 h-4" />
            Execute
          </button>
        </div>
      </section>

      {/* Stats */}
      <div className="grid gap-4 sm:grid-cols-4">
        <div className="glass-card text-center">
          <p className="text-3xl font-bold text-white">{intents.length}</p>
          <p className="text-sm text-slate-400">Total Intents</p>
        </div>
        <div className="glass-card text-center">
          <p className="text-3xl font-bold text-white">
            {intents.filter((i) => i.status === 'executing').length}
          </p>
          <p className="text-sm text-slate-400">In Progress</p>
        </div>
        <div className="glass-card text-center">
          <p className="text-3xl font-bold text-white">
            {intents.filter((i) => i.status === 'completed').length}
          </p>
          <p className="text-sm text-slate-400">Completed</p>
        </div>
        <div className="glass-card text-center">
          <p className="text-3xl font-bold text-emerald-400">
            {intents.length > 0 
              ? `${((intents.filter((i) => i.status === 'completed').length / intents.length) * 100).toFixed(0)}%`
              : '0%'}
          </p>
          <p className="text-sm text-slate-400">Success Rate</p>
        </div>
      </div>

      {/* Intent Queue */}
      <section className="glass-card">
        <div className="flex items-center gap-3 mb-6">
          <Layers className="w-5 h-5 text-indigo-400" />
          <h2 className="text-xl font-semibold text-white">Intent Queue</h2>
        </div>
        <div className="space-y-4">
          {intents.map((intent) => (
            <div key={intent.id} className="p-4 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 transition-colors">
              <div className="flex items-start justify-between gap-4">
                <div className="flex items-start gap-4">
                  <div className={`p-2 rounded-lg ${statusStyles[intent.status].bg}`}>
                    {statusStyles[intent.status].icon}
                  </div>
                  <div>
                    <p className="text-white font-medium">{intent.query}</p>
                    <div className="flex items-center gap-3 mt-2 text-xs text-slate-400">
                      <span className={`px-2 py-0.5 rounded ${priorityStyles[intent.priority]}`}>
                        {intent.priority}
                      </span>
                      <span className="flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {new Date(intent.created_at).toLocaleTimeString()}
                      </span>
                      {intent.steps_total > 0 && (
                        <span className="flex items-center gap-1">
                          <Target className="w-3 h-3" />
                          {intent.steps_completed}/{intent.steps_total} steps
                        </span>
                      )}
                    </div>
                    {intent.final_result && (
                      <p className="mt-2 text-sm text-emerald-400 flex items-center gap-2">
                        <ArrowRight className="w-3 h-3" />
                        {intent.final_result}
                      </p>
                    )}
                  </div>
                </div>
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${statusStyles[intent.status].bg} ${statusStyles[intent.status].text}`}>
                  {intent.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* v1000 Banner */}
      <section className="glass-card border border-dashed border-indigo-500/30 bg-gradient-to-r from-indigo-500/10 via-purple-500/10 to-pink-500/10">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
            <Sparkles className="w-6 h-6 text-white" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-white">Version 1000 Intent Processing</h3>
            <p className="text-sm text-slate-300">
              Coming soon: Multi-step reasoning visualization, constraint-based planning,
              and federated driver execution across distributed nodes.
            </p>
          </div>
        </div>
      </section>
    </div>
  )
}






