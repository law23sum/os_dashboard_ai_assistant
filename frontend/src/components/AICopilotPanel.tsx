import { X, Sparkles, MessageSquare, Bot, FileText, Wand2, Brain, Cpu, Activity, Zap, Target, TrendingUp, Clock, CheckCircle2, AlertCircle, Loader2, ChevronRight } from 'lucide-react'
import { Link, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import apiClient, { apiPath } from '../lib/apiClient'
import type { PersonasResponse } from '../types'
import { useState, useMemo, useEffect } from 'react'
import { toast } from '../utils/toast'

interface AICopilotPanelProps {
  currentPath: string
  open: boolean
  onToggle: (open: boolean) => void
}

const PERSONA_ROLES: Record<string, { role: string; description: string; color: string; icon: typeof Bot; gradient: string }> = {
  Chris: {
    role: 'Human Owner',
    description: 'Executive decisions and system authority',
    color: 'from-rose-500 to-orange-500',
    gradient: 'bg-gradient-to-br from-rose-500/20 via-orange-500/10 to-transparent',
    icon: Bot,
  },
  AIC: {
    role: 'Meta-Governor',
    description: 'Cross-project coherence, quality assurance, architecture integrity',
    color: 'from-indigo-500 to-blue-500',
    gradient: 'bg-gradient-to-br from-indigo-500/20 via-blue-500/10 to-transparent',
    icon: Brain,
  },
  Aria: {
    role: 'Emotional Muse',
    description: 'Tone, resonance, emotional coherence, narrative explanation',
    color: 'from-emerald-500 to-teal-500',
    gradient: 'bg-gradient-to-br from-emerald-500/20 via-teal-500/10 to-transparent',
    icon: Sparkles,
  },
  Sora: {
    role: 'Strategic Architect',
    description: 'Structure, dependencies, sequencing, execution order',
    color: 'from-cyan-500 to-sky-500',
    gradient: 'bg-gradient-to-br from-cyan-500/20 via-sky-500/10 to-transparent',
    icon: Target,
  },
}

const fetchPersonas = async (): Promise<PersonasResponse> => {
  const { data } = await apiClient.get<PersonasResponse>(apiPath('personas'))
  return data
}

// Context-aware suggestions based on current page
const getContextSuggestions = (path: string) => {
  const suggestions: Array<{ icon: typeof MessageSquare; label: string; action: string; path?: string; priority?: 'high' | 'medium' | 'low' }> = []

  if (path.startsWith('/chat')) {
    suggestions.push(
      { icon: FileText, label: 'Upload document', action: 'Upload a document to analyze', path: '/chat', priority: 'high' },
      { icon: Wand2, label: 'Generate summary', action: 'Summarize recent conversations', priority: 'medium' },
      { icon: Brain, label: 'Switch persona', action: 'Change AI assistant personality', priority: 'low' }
    )
  } else if (path.startsWith('/work/writer')) {
    suggestions.push(
      { icon: FileText, label: 'New document', action: 'Create a new document', path: '/work/writer', priority: 'high' },
      { icon: Wand2, label: 'Generate content', action: 'AI-powered content generation', priority: 'high' },
      { icon: TrendingUp, label: 'Review drafts', action: 'Review and refine documents', priority: 'medium' }
    )
  } else if (path.startsWith('/research')) {
    suggestions.push(
      { icon: Brain, label: 'New experiment', action: 'Start a research experiment', priority: 'high' },
      { icon: FileText, label: 'Literature review', action: 'Search and analyze papers', priority: 'medium' },
      { icon: Zap, label: 'Run simulation', action: 'Execute simulation models', priority: 'medium' }
    )
  } else if (path.startsWith('/projects')) {
    suggestions.push(
      { icon: Target, label: 'Project insights', action: 'Get AI analysis of project status', priority: 'high' },
      { icon: Activity, label: 'Risk assessment', action: 'Evaluate project risks', priority: 'high' },
      { icon: TrendingUp, label: 'Timeline forecast', action: 'Predict completion timeline', priority: 'medium' }
    )
  } else if (path.startsWith('/ai/copilot')) {
    suggestions.push(
      { icon: Cpu, label: 'AI Operations', action: 'Monitor AI system status', priority: 'medium' },
      { icon: Brain, label: 'Reasoning traces', action: 'View AI reasoning history', priority: 'medium' },
      { icon: Zap, label: 'Driver metrics', action: 'Check driver performance', priority: 'low' }
    )
  } else {
    // Default suggestions
    suggestions.push(
      { icon: MessageSquare, label: 'Start chat', action: 'Begin a conversation', path: '/chat', priority: 'high' },
      { icon: FileText, label: 'Create document', action: 'Generate new content', path: '/work/writer', priority: 'high' },
      { icon: Brain, label: 'AI insights', action: 'Get AI-powered recommendations', priority: 'medium' }
    )
  }

  return suggestions
}

export function AICopilotPanel({ currentPath, open, onToggle }: AICopilotPanelProps) {
  const navigate = useNavigate()
  const { data: personasData, isLoading: personasLoading } = useQuery({ queryKey: ['personas'], queryFn: fetchPersonas })
  const [selectedPersona, setSelectedPersona] = useState<string>('AIC')
  const [isChangingPersona, setIsChangingPersona] = useState(false)
  const [panelMounted, setPanelMounted] = useState(false)

  const activePersona = personasData?.active || selectedPersona
  const personas = personasData?.personas || []

  const contextSuggestions = useMemo(() => getContextSuggestions(currentPath), [currentPath])

  // Smooth panel entrance animation
  useEffect(() => {
    if (open) {
      setPanelMounted(true)
    } else {
      // Delay unmount for exit animation
      const timer = setTimeout(() => setPanelMounted(false), 300)
      return () => clearTimeout(timer)
    }
  }, [open])

  const quickActions = [
    {
      icon: MessageSquare,
      label: 'Chat',
      path: '/chat',
      description: 'Start a conversation',
    },
    {
      icon: Bot,
      label: 'AI Copilot',
      path: '/ai/copilot',
      description: 'Full copilot console',
    },
    {
      icon: FileText,
      label: 'Writer',
      path: '/work/writer',
      description: 'Document generation',
    },
    {
      icon: Wand2,
      label: 'Research',
      path: '/research',
      description: 'Research hub',
    },
  ]

  const handlePersonaChange = async (persona: string) => {
    if (persona === activePersona || isChangingPersona) return
    
    setIsChangingPersona(true)
    setSelectedPersona(persona)
    try {
      await apiClient.post(apiPath('personas'), { persona })
      toast.success(`Switched to ${persona}`)
    } catch (error) {
      console.error('Failed to update persona:', error)
      toast.error('Failed to switch persona')
      setSelectedPersona(activePersona) // Revert on error
    } finally {
      setIsChangingPersona(false)
    }
  }

  if (!open && !panelMounted) return null

  const currentPersonaInfo = PERSONA_ROLES[activePersona] || PERSONA_ROLES['AIC']
  const PersonaIcon = currentPersonaInfo.icon

  return (
    <>
      {/* Backdrop overlay */}
      {open && (
        <div
          className="fixed inset-0 bg-black/20 backdrop-blur-sm z-40 transition-opacity duration-300"
          onClick={() => onToggle(false)}
          aria-hidden="true"
        />
      )}
      
      {/* Panel */}
      <div
        className={`
          fixed right-0 top-0 bottom-0 w-96 bg-slate-900/98 backdrop-blur-xl border-l border-slate-700/50 shadow-2xl z-50 flex flex-col
          transform transition-transform duration-300 ease-out
          ${open ? 'translate-x-0' : 'translate-x-full'}
        `}
      >
        {/* Header */}
        <div className={`p-5 border-b border-slate-700/50 ${currentPersonaInfo.gradient} transition-all duration-300`}>
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className={`p-2.5 rounded-xl bg-gradient-to-br ${currentPersonaInfo.color}/30 shadow-lg shadow-${currentPersonaInfo.color.split('-')[1]}-500/20`}>
                <PersonaIcon className="w-5 h-5 text-white" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-white tracking-tight">AI Copilot</h3>
                <p className="text-xs text-slate-300/80 font-medium">Context-aware assistant</p>
              </div>
            </div>
            <button
              onClick={() => onToggle(false)}
              className="p-2 hover:bg-slate-800/60 rounded-lg transition-all text-slate-400 hover:text-white hover:rotate-90 active:scale-95"
              aria-label="Close panel"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Persona Selector */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <p className="text-xs uppercase tracking-wider text-slate-400 font-semibold">Active Persona</p>
              {isChangingPersona && (
                <Loader2 className="w-3.5 h-3.5 text-primary-400 animate-spin" />
              )}
            </div>
            <div className="grid grid-cols-2 gap-2">
              {Object.entries(PERSONA_ROLES).map(([name, info]) => {
                const Icon = info.icon
                const isActive = activePersona === name
                return (
                  <button
                    key={name}
                    onClick={() => handlePersonaChange(name)}
                    disabled={isChangingPersona}
                    className={`
                      flex items-center gap-2.5 p-2.5 rounded-xl border-2 transition-all text-left
                      transform hover:scale-[1.02] active:scale-[0.98]
                      focus:outline-none focus:ring-2 focus:ring-primary-500/50
                      ${
                        isActive
                          ? `border-primary-500/70 bg-gradient-to-br ${info.color}/20 shadow-lg shadow-${info.color.split('-')[1]}-500/10 text-white`
                          : 'border-slate-700/50 bg-slate-800/40 hover:bg-slate-800/60 hover:border-slate-600/70 text-slate-200 disabled:opacity-50 disabled:cursor-not-allowed'
                      }
                    `}
                  >
                    <div className={`p-1.5 rounded-lg transition-all ${
                      isActive 
                        ? `bg-gradient-to-br ${info.color}/40 shadow-md` 
                        : 'bg-slate-700/50'
                    }`}>
                      <Icon className="w-3.5 h-3.5" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-xs font-semibold truncate">{name}</p>
                      <p className="text-[10px] text-slate-400 truncate leading-tight">{info.role}</p>
                    </div>
                    {isActive && (
                      <CheckCircle2 className="w-3.5 h-3.5 text-primary-400 flex-shrink-0 animate-in fade-in zoom-in duration-200" />
                    )}
                  </button>
                )
              })}
            </div>
            {currentPersonaInfo && (
              <div className="mt-3 p-3 rounded-xl bg-slate-800/60 border border-slate-700/50 backdrop-blur-sm">
                <p className="text-[11px] text-slate-300 leading-relaxed">{currentPersonaInfo.description}</p>
              </div>
            )}
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-5 space-y-5 scrollbar-thin scrollbar-thumb-slate-700 scrollbar-track-transparent">
          {/* Context-Aware Suggestions */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-primary-400" />
                <p className="text-xs uppercase tracking-wider text-slate-400 font-semibold">Smart Suggestions</p>
              </div>
              <span className="text-[10px] text-slate-500 bg-slate-800/50 px-2 py-0.5 rounded-full">
                {contextSuggestions.length}
              </span>
            </div>
            <div className="space-y-2">
              {contextSuggestions.length === 0 ? (
                <div className="p-4 rounded-xl border border-slate-700/50 bg-slate-800/30 text-center">
                  <p className="text-xs text-slate-400">No suggestions available</p>
                </div>
              ) : (
                contextSuggestions.map((suggestion, idx) => {
                  const Icon = suggestion.icon
                  const priorityColor = 
                    suggestion.priority === 'high' ? 'border-primary-500/40 bg-primary-500/5' :
                    suggestion.priority === 'medium' ? 'border-slate-600/40 bg-slate-800/30' :
                    'border-slate-700/30 bg-slate-800/20'
                  
                  return (
                    <button
                      key={idx}
                      onClick={() => {
                        if (suggestion.path) {
                          navigate(suggestion.path)
                          onToggle(false)
                        }
                      }}
                      className={`
                        w-full flex items-center gap-3 p-3.5 rounded-xl border-2 transition-all text-left group
                        hover:scale-[1.02] active:scale-[0.98] focus:outline-none focus:ring-2 focus:ring-primary-500/50
                        ${priorityColor} hover:border-primary-500/60 hover:bg-primary-500/10
                      `}
                    >
                      <div className="p-2 rounded-lg bg-primary-500/10 group-hover:bg-primary-500/20 transition-colors group-hover:scale-110">
                        <Icon className="w-4 h-4 text-primary-400" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-semibold text-slate-200 group-hover:text-white transition-colors">
                          {suggestion.label}
                        </p>
                        <p className="text-xs text-slate-400 truncate mt-0.5">{suggestion.action}</p>
                      </div>
                      {suggestion.path && (
                        <ChevronRight className="w-4 h-4 text-slate-500 group-hover:text-primary-400 transition-colors opacity-0 group-hover:opacity-100" />
                      )}
                    </button>
                  )
                })
              )}
            </div>
          </div>

          {/* Quick Actions */}
          <div className="space-y-3">
            <p className="text-xs uppercase tracking-wider text-slate-400 font-semibold">Quick Actions</p>
            <div className="grid grid-cols-2 gap-2.5">
              {quickActions.map((action) => {
                const Icon = action.icon
                const isActive = currentPath === action.path || currentPath.startsWith(action.path + '/')
                return (
                  <Link
                    key={action.path}
                    to={action.path}
                    onClick={() => onToggle(false)}
                    className={`
                      flex flex-col items-center gap-2.5 p-3.5 rounded-xl border-2 transition-all
                      transform hover:scale-105 active:scale-95 focus:outline-none focus:ring-2 focus:ring-primary-500/50
                      ${
                        isActive
                          ? 'border-primary-500/70 bg-primary-500/10 text-white shadow-lg shadow-primary-500/10'
                          : 'border-slate-700/50 bg-slate-800/30 hover:bg-slate-800/50 hover:border-slate-600 text-slate-200'
                      }
                    `}
                  >
                    <div
                      className={`p-2.5 rounded-xl transition-all ${
                        isActive 
                          ? 'bg-primary-500/20 shadow-md' 
                          : 'bg-slate-700/50 group-hover:bg-slate-700/70'
                      }`}
                    >
                      <Icon className="w-4 h-4" />
                    </div>
                    <div className="text-center">
                      <p className="text-xs font-semibold">{action.label}</p>
                      <p className="text-[10px] text-slate-400 mt-0.5 leading-tight">{action.description}</p>
                    </div>
                  </Link>
                )
              })}
            </div>
          </div>

          {/* Status Indicators */}
          <div className="space-y-3 pt-3 border-t border-slate-700/50">
            <p className="text-xs uppercase tracking-wider text-slate-400 font-semibold">System Status</p>
            <div className="space-y-2">
              <div className="flex items-center justify-between p-3 rounded-xl bg-slate-800/40 border border-slate-700/50 hover:bg-slate-800/60 transition-colors">
                <div className="flex items-center gap-2.5">
                  <div className="relative">
                    <div className="w-2.5 h-2.5 rounded-full bg-emerald-400" />
                    <div className="absolute inset-0 w-2.5 h-2.5 rounded-full bg-emerald-400 animate-ping opacity-75" />
                  </div>
                  <span className="text-xs font-medium text-slate-300">AI Services</span>
                </div>
                <span className="text-[10px] text-emerald-400 font-medium bg-emerald-400/10 px-2 py-0.5 rounded-full">
                  Active
                </span>
              </div>
              <div className="flex items-center justify-between p-3 rounded-xl bg-slate-800/40 border border-slate-700/50 hover:bg-slate-800/60 transition-colors">
                <div className="flex items-center gap-2.5">
                  <Cpu className="w-3.5 h-3.5 text-primary-400" />
                  <span className="text-xs font-medium text-slate-300">Processing</span>
                </div>
                <span className="text-[10px] text-slate-400 font-medium">Ready</span>
              </div>
            </div>
          </div>

          {/* Current Context */}
          <div className="pt-3 border-t border-slate-700/50">
            <p className="text-xs uppercase tracking-wider text-slate-400 font-semibold mb-2.5">Current Context</p>
            <div className="p-3.5 rounded-xl border border-slate-700/50 bg-slate-800/30 backdrop-blur-sm">
              <p className="text-xs text-slate-300 font-mono break-all leading-relaxed">{currentPath}</p>
              <div className="mt-2.5 flex items-center gap-2 text-[10px] text-slate-500">
                <Clock className="w-3 h-3" />
                <span>Context-aware suggestions enabled</span>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-5 border-t border-slate-700/50 space-y-3 bg-slate-900/50 backdrop-blur-sm">
          <Link
            to="/ai/copilot"
            onClick={() => onToggle(false)}
            className="w-full flex items-center justify-center gap-2.5 px-5 py-3 bg-gradient-to-r from-primary-500 to-primary-600 text-white rounded-xl hover:from-primary-600 hover:to-primary-700 transition-all text-sm font-semibold shadow-lg shadow-primary-500/30 hover:shadow-xl hover:shadow-primary-500/40 transform hover:scale-[1.02] active:scale-[0.98] focus:outline-none focus:ring-2 focus:ring-primary-500/50"
          >
            <Sparkles className="w-4 h-4" />
            Open Full Console
          </Link>
          <div className="flex items-center justify-center gap-1.5 text-[10px] text-slate-500">
            <Brain className="w-3 h-3" />
            <span className="font-medium">Powered by AI OS</span>
          </div>
        </div>
      </div>
    </>
  )
}
