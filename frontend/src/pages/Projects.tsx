import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Plus,
  RefreshCw,
  ExternalLink,
  FileText,
  PenSquare,
  Trash2,
  ArrowUpNarrowWide,
  ArrowDownNarrowWide,
  BookOpen,
  Hash,
  Clock,
  Shield,
  AlertTriangle,
  Sparkles,
  X,
  Brain,
  History,
  Loader2,
  Cpu,
  Activity,
  Zap,
} from 'lucide-react'
import { useEffect, useMemo, useState } from 'react'
import type React from 'react'
import { toast } from '../utils/toast'
import apiClient, { apiPath } from '../lib/apiClient'
import { extractArray } from '../lib/responseHelpers'
import type {
  Project,
  Task,
  ProjectLink,
  ProjectLedgerEvent,
  ProjectIntelligence,
  ProjectInsightResponse,
  ReasoningTrace,
  ReasoningPersona,
  ProjectTRFResponse,
} from '../types'

type StorageStatus = {
  data_dir: string
  db_path: string
  db_exists: boolean
  db_size_bytes: number
  db_last_modified?: string | null
  project_count: number
  task_count: number
}

const fetchProjects = async (): Promise<Project[]> => {
  const { data } = await apiClient.get(apiPath('projects'))
  return extractArray<Project>(data, ['projects', 'items'])
}

const fetchStorageStatus = async (): Promise<StorageStatus> => {
  const { data } = await apiClient.get<StorageStatus>(apiPath('settings/storage'))
  return data
}

const fetchTasks = async (): Promise<Task[]> => {
  const { data } = await apiClient.get(apiPath('tasks'))
  return extractArray<Task>(data, ['tasks', 'items'])
}

const fetchProjectLinks = async (): Promise<ProjectLink[]> => {
  const { data } = await apiClient.get<ProjectLink[]>(apiPath('projects/links'))
  return data
}

const fetchProjectLedger = async (project?: string, limit = 120): Promise<ProjectLedgerEvent[]> => {
  const params: Record<string, string | number> = { limit }
  if (project) {
    params.project = project
  }
  const { data } = await apiClient.get<ProjectLedgerEvent[]>(apiPath('projects/ledger'), {
    params,
  })
  return data
}

const fetchProjectIntelligence = async (): Promise<ProjectIntelligence[]> => {
  const { data } = await apiClient.get<ProjectIntelligence[]>(apiPath('projects/intelligence'))
  return data
}

const fetchProjectInsights = async (projectName: string): Promise<ProjectInsightResponse> => {
  const { data } = await apiClient.get<ProjectInsightResponse>(
    apiPath(`projects/${encodeURIComponent(projectName)}/insights`),
  )
  return data
}

const fetchProjectTrf = async (projectName: string): Promise<ProjectTRFResponse> => {
  const { data } = await apiClient.get<ProjectTRFResponse>(
    apiPath(`projects/${encodeURIComponent(projectName)}/trf`),
  )
  return data
}

const fetchReasoningHistory = async (limit = 5): Promise<ReasoningTrace[]> => {
  const { data } = await apiClient.get<ReasoningTrace[]>(apiPath('reasoning/history'), {
    params: { limit },
  })
  return data
}

const fetchReasoningPersonas = async (): Promise<ReasoningPersona[]> => {
  const { data } = await apiClient.get<ReasoningPersona[]>(apiPath('reasoning/personas'))
  return data
}

const runReasoningQuery = async (payload: { query: string; persona?: string }): Promise<ReasoningTrace> => {
  const { data } = await apiClient.post<ReasoningTrace>(apiPath('reasoning/query'), payload)
  return data
}

const createProject = async (project: Partial<Project>): Promise<Project> => {
  const { data } = await apiClient.post<Project>(apiPath('projects'), project)
  return data
}

const updateProject = async (name: string, patch: Partial<Project>): Promise<Project> => {
  const { data } = await apiClient.put<Project>(apiPath(`projects/${encodeURIComponent(name)}`), patch)
  return data
}

const deleteProject = async (name: string): Promise<void> => {
  await apiClient.delete(apiPath(`projects/${encodeURIComponent(name)}`))
}

  type EnrichedProject = Project & {
    tasks: Task[]
    links: ProjectLink[]
    ledger: ProjectLedgerEvent[]
    intelligence?: ProjectIntelligence
  }

const statusGradients: Record<string, string> = {
  active: 'from-emerald-400/90 via-teal-400/80 to-sky-400/80',
  paused: 'from-amber-400/80 via-orange-500/80 to-rose-500/80',
  planning: 'from-indigo-400/80 via-purple-500/70 to-pink-500/70',
}

const priorityPills: Record<string, string> = {
  CRITICAL: 'bg-rose-500/15 text-rose-200 border border-rose-400/30',
  HIGH: 'bg-amber-500/15 text-amber-100 border border-amber-400/30',
  MEDIUM: 'bg-sky-500/15 text-sky-100 border border-sky-400/30',
  LOW: 'bg-slate-500/15 text-slate-200 border border-slate-400/30',
}

const riskLevelOrder: Record<string, number> = {
  steady: 0,
  guarded: 1,
  high: 2,
  critical: 3,
}

const riskBadgeTone: Record<string, string> = {
  steady: 'border-emerald-500/30 bg-emerald-500/10 text-emerald-100',
  guarded: 'border-sky-500/30 bg-sky-500/10 text-sky-100',
  high: 'border-amber-500/30 bg-amber-500/10 text-amber-100',
  critical: 'border-rose-500/30 bg-rose-500/10 text-rose-100',
}

const riskLabel: Record<string, string> = {
  steady: 'Steady',
  guarded: 'Guarded',
  high: 'High Risk',
  critical: 'Critical',
}

const getPayloadTitle = (payload?: Record<string, unknown>) =>
  typeof payload?.title === 'string' ? (payload.title as string) : undefined

const defaultForm = {
  name: '',
  description: '',
  priority: 'MEDIUM',
  status: 'active',
}

export default function Projects() {
  const [formMode, setFormMode] = useState<'create' | 'edit' | null>(null)
  const [form, setForm] = useState(defaultForm)
  const [editingProject, setEditingProject] = useState<EnrichedProject | null>(null)
  const [insightsProject, setInsightsProject] = useState<EnrichedProject | null>(null)
  const [trfProject, setTrfProject] = useState<EnrichedProject | null>(null)
  const [ledgerProjectFilter, setLedgerProjectFilter] = useState<string | null>(null)
  const [reasoningQueryText, setReasoningQueryText] = useState('')
  const [selectedPersona, setSelectedPersona] = useState('aic')
  const [activeTrace, setActiveTrace] = useState<ReasoningTrace | null>(null)

  const queryClient = useQueryClient()
  const projectsQuery = useQuery({ queryKey: ['projects'], queryFn: fetchProjects })
  const storageQuery = useQuery({ queryKey: ['settings-storage'], queryFn: fetchStorageStatus, staleTime: 30000 })
  const tasksQuery = useQuery({ queryKey: ['tasks'], queryFn: fetchTasks })
  const linksQuery = useQuery({ queryKey: ['project-links'], queryFn: fetchProjectLinks })
  const ledgerQuery = useQuery({
    queryKey: ['project-ledger', ledgerProjectFilter ?? 'all'],
    queryFn: () => fetchProjectLedger(ledgerProjectFilter ?? undefined, 120),
    enabled: !projectsQuery.isLoading,
    placeholderData: (previousData) => previousData ?? [],
    refetchInterval: 20000,
  })
  const intelligenceQuery = useQuery({
    queryKey: ['project-intelligence'],
    queryFn: fetchProjectIntelligence,
    enabled: !projectsQuery.isLoading,
    refetchInterval: 30000,
  })
  const projectInsightsQuery = useQuery({
    queryKey: ['project-insights', insightsProject?.name],
    queryFn: () => {
      if (!insightsProject) {
        throw new Error('No project selected')
      }
      return fetchProjectInsights(insightsProject.name)
    },
    enabled: Boolean(insightsProject),
    staleTime: 60000,
    refetchInterval: 60000,
  })
  const insightsProjectTrfQuery = useQuery({
    queryKey: ['project-trf', insightsProject?.name],
    queryFn: () => {
      if (!insightsProject) {
        throw new Error('No project selected')
      }
      return fetchProjectTrf(insightsProject.name)
    },
    enabled: Boolean(insightsProject),
    staleTime: 60000,
    refetchInterval: 60000,
  })
  const projectTrfQuery = useQuery({
    queryKey: ['project-trf', trfProject?.name],
    queryFn: () => {
      if (!trfProject) {
        throw new Error('No project selected')
      }
      return fetchProjectTrf(trfProject.name)
    },
    enabled: Boolean(trfProject),
    staleTime: 60000,
    refetchInterval: 60000,
  })
  const reasoningPersonasQuery = useQuery({
    queryKey: ['reasoning-personas'],
    queryFn: fetchReasoningPersonas,
    staleTime: 5 * 60 * 1000,
  })
  const reasoningHistoryQuery = useQuery({
    queryKey: ['reasoning-history'],
    queryFn: () => fetchReasoningHistory(),
    refetchInterval: 60000,
  })

  const createMutation = useMutation({
    mutationFn: createProject,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] })
      toast.success('Project created successfully')
      setFormMode(null)
      setForm(defaultForm)
    },
    onError: () => toast.error('Failed to create project'),
  })

  const updateMutation = useMutation({
    mutationFn: ({ name, patch }: { name: string; patch: Partial<Project> }) => updateProject(name, patch),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['projects'] })
      toast.success(`Updated ${variables.name}`)
      setFormMode(null)
      setEditingProject(null)
      setForm(defaultForm)
    },
    onError: (error) => {
      toast.error(`Failed to update project: ${error instanceof Error ? error.message : 'Unknown error'}`)
    },
  })

  const deleteMutation = useMutation({
    mutationFn: deleteProject,
    onSuccess: (_, name) => {
      queryClient.invalidateQueries({ queryKey: ['projects'] })
      toast.success(`Deleted ${name}`)
    },
    onError: (error) => {
      toast.error(`Failed to delete project: ${error instanceof Error ? error.message : 'Unknown error'}`)
    },
  })

  const reorderMutation = useMutation({
    mutationFn: async ({ source, target }: { source: EnrichedProject; target: EnrichedProject }) => {
      await updateProject(source.name, { order_num: target.order_num })
      await updateProject(target.name, { order_num: source.order_num })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] })
    },
    onError: (error) => {
      toast.error(`Failed to reorder projects: ${error instanceof Error ? error.message : 'Unknown error'}`)
    },
  })
  const reasoningMutation = useMutation({
    mutationFn: runReasoningQuery,
    onSuccess: (trace) => {
      setActiveTrace(trace)
      setReasoningQueryText(trace.query)
      toast.success('Reasoning trace generated')
      queryClient.invalidateQueries({ queryKey: ['reasoning-history'] })
    },
    onError: (error) => {
      toast.error(`Reasoning failed: ${error instanceof Error ? error.message : 'Unknown error'}`)
    },
  })

  const isLoading =
    projectsQuery.isLoading ||
    storageQuery.isLoading ||
    tasksQuery.isLoading ||
    linksQuery.isLoading ||
    ledgerQuery.isLoading ||
    intelligenceQuery.isLoading

  const tasksByProject = useMemo(() => {
    const grouped = new Map<string, Task[]>()
    ;(tasksQuery.data ?? []).forEach((task) => {
      const key = task.project || 'General'
      const list = grouped.get(key) ?? []
      list.push(task)
      grouped.set(key, list)
    })
    return grouped
  }, [tasksQuery.data])

  const linksByProject = useMemo(() => {
    const grouped = new Map<string, ProjectLink[]>()
    ;(linksQuery.data ?? []).forEach((link) => {
      const key = link.project_id || 'General'
      const list = grouped.get(key) ?? []
      list.push(link)
      grouped.set(key, list)
    })
    return grouped
  }, [linksQuery.data])

  const ledgerByProject = useMemo(() => {
    const grouped = new Map<string, ProjectLedgerEvent[]>()
    ;(ledgerQuery.data ?? []).forEach((event) => {
      const list = grouped.get(event.project_id) ?? []
      list.push(event)
      grouped.set(event.project_id, list)
    })
    return grouped
  }, [ledgerQuery.data])

  const intelligenceByProject = useMemo(() => {
    const grouped = new Map<string, ProjectIntelligence>()
    ;(intelligenceQuery.data ?? []).forEach((intel) => {
      grouped.set(intel.project_id, intel)
    })
    return grouped
  }, [intelligenceQuery.data])

  const intelligenceStats = useMemo(() => {
    const intel = intelligenceQuery.data ?? []
    if (!intel.length) {
      return {
        averageHealth: null,
        highRisk: 0,
        ledgerAlerts: 0,
      }
    }
    const averageHealth = Number(
      (intel.reduce((sum, item) => sum + item.health_score, 0) / intel.length).toFixed(1)
    )
    const highRisk = intel.filter((item) => riskLevelOrder[item.risk_level] >= riskLevelOrder.high).length
    const ledgerAlerts = intel.filter((item) => !item.ledger_ok).length
    return {
      averageHealth,
      highRisk,
      ledgerAlerts,
    }
  }, [intelligenceQuery.data])

  const highestRiskProjects = useMemo(() => {
    const intel = intelligenceQuery.data ?? []
    return [...intel]
      .sort((a, b) => {
        const orderDiff = riskLevelOrder[b.risk_level] - riskLevelOrder[a.risk_level]
        if (orderDiff !== 0) return orderDiff
        return b.health_score - a.health_score
      })
      .slice(0, 4)
  }, [intelligenceQuery.data])

  const enrichedProjects = useMemo<EnrichedProject[]>(() => {
    return (projectsQuery.data ?? []).map((project) => ({
      ...project,
      tasks: tasksByProject.get(project.name) ?? [],
      links: linksByProject.get(project.name) ?? [],
      ledger: ledgerByProject.get(project.name) ?? [],
      intelligence: intelligenceByProject.get(project.name),
    }))
  }, [projectsQuery.data, tasksByProject, linksByProject, ledgerByProject, intelligenceByProject])

  useEffect(() => {
    if (!insightsProject) return
    const updated = enrichedProjects.find((project) => project.name === insightsProject.name)
    if (updated && updated !== insightsProject) {
      setInsightsProject(updated)
    }
  }, [enrichedProjects, insightsProject])

  useEffect(() => {
    if (!activeTrace && reasoningHistoryQuery.data && reasoningHistoryQuery.data.length) {
      setActiveTrace(reasoningHistoryQuery.data[0])
    }
  }, [activeTrace, reasoningHistoryQuery.data])

  const latestLedgerEvents = ledgerQuery.data ?? []

  const aggregate = useMemo(() => {
    const totalTasks = (tasksQuery.data ?? []).length
    const activeProjects = enrichedProjects.filter((p) => p.status === 'active').length
    const criticalTasks = (tasksQuery.data ?? []).filter((task) => task.priority === 'CRITICAL').length
    return {
      totalProjects: enrichedProjects.length,
      activeProjects,
      totalTasks,
      criticalTasks,
    }
  }, [enrichedProjects, tasksQuery.data])

  const statusCounts = useMemo(() => {
    const counts: Record<string, number> = {}
    enrichedProjects.forEach((project) => {
      const key = (project.status || 'unknown').toUpperCase()
      counts[key] = (counts[key] || 0) + 1
    })
    return counts
  }, [enrichedProjects])

  const priorityCounts = useMemo(() => {
    const counts: Record<string, number> = {}
    enrichedProjects.forEach((project) => {
      const key = (project.priority || 'MEDIUM').toUpperCase()
      counts[key] = (counts[key] || 0) + 1
    })
    return counts
  }, [enrichedProjects])

  const headerStats = useMemo<Array<{ label: string; value: string | number; detail: string }>>(() => {
    const stats: Array<{ label: string; value: string | number; detail: string }> = [
      {
        label: 'Total Projects',
        value: aggregate.totalProjects,
        detail: 'Across all tenants',
      },
      {
        label: 'Active Projects',
        value: aggregate.activeProjects,
        detail: 'Status = active',
      },
      {
        label: 'Total Tasks',
        value: aggregate.totalTasks,
        detail: 'All workstreams',
      },
      {
        label: 'Critical Tasks',
        value: aggregate.criticalTasks,
        detail: 'Priority CRITICAL',
      },
    ]
    if (intelligenceStats.averageHealth !== null) {
      stats.push({
        label: 'Avg Health',
        value: `${intelligenceStats.averageHealth}%`,
        detail: 'Spec §4.5 Project Intelligence',
      })
    }
    stats.push({
      label: 'High-Risk Projects',
      value: intelligenceStats.highRisk,
      detail: 'Risk level ≥ High',
    })
    return stats
  }, [aggregate, intelligenceStats])

  const orderedProjects = useMemo(() => {
    return [...enrichedProjects].sort((a, b) => {
      const orderCompare = (a.order_num ?? 0) - (b.order_num ?? 0)
      if (orderCompare !== 0) return orderCompare
      return a.name.localeCompare(b.name)
    })
  }, [enrichedProjects])

  const ledgerProjectOptions = useMemo(
    () => orderedProjects.map((project) => project.name),
    [orderedProjects]
  )

  const personaOptions: ReasoningPersona[] = useMemo(() => {
    if (reasoningPersonasQuery.data && reasoningPersonasQuery.data.length) {
      return reasoningPersonasQuery.data
    }
    return [
      {
        id: 'fallback-aic',
        type: 'aic',
        label: 'AIC',
        decision_threshold: 0.9,
        interaction_style: 'governor',
        capabilities: ['system_architecture'],
        active: true,
      },
      {
        id: 'fallback-chris',
        type: 'chris',
        label: 'Chris',
        decision_threshold: 0.7,
        interaction_style: 'strategist',
        capabilities: ['project_management'],
        active: true,
      },
    ]
  }, [reasoningPersonasQuery.data])

  const reasoningHistory = reasoningHistoryQuery.data ?? []

  const ledgerIntegrityOk = useMemo(() => {
    if (latestLedgerEvents.length <= 1) {
      return true
    }
    for (let idx = 0; idx < latestLedgerEvents.length - 1; idx += 1) {
      const current = latestLedgerEvents[idx]
      const next = latestLedgerEvents[idx + 1]
      if (current.hash_prev && next.hash_curr && current.hash_prev !== next.hash_curr) {
        return false
      }
    }
    return true
  }, [latestLedgerEvents])

  const handleLedgerProjectChange = (projectName: string | null) => {
    setLedgerProjectFilter(projectName)
  }

  const handleHistorySelect = (trace: ReasoningTrace) => {
    setActiveTrace(trace)
    setReasoningQueryText(trace.query)
  }

  const handleReasoningRun = () => {
    const trimmed = reasoningQueryText.trim()
    if (!trimmed) {
      toast.error('Enter a reasoning query to engage the TRF.')
      return
    }
    reasoningMutation.mutate({ query: trimmed, persona: selectedPersona })
  }

  const openCreateForm = () => {
    setForm(defaultForm)
    setEditingProject(null)
    setFormMode('create')
  }

  const openEditForm = (project: EnrichedProject) => {
    setForm({
      name: project.name,
      description: project.description || '',
      priority: project.priority || 'MEDIUM',
      status: project.status || 'active',
    })
    setEditingProject(project)
    setFormMode('edit')
  }

  const openInsightsPanel = (project: EnrichedProject) => {
    setInsightsProject(project)
  }

  const openTrfPanel = (project: EnrichedProject) => {
    setTrfProject(project)
  }

  const closeForm = () => {
    setForm(defaultForm)
    setEditingProject(null)
    setFormMode(null)
  }

  const handleRefresh = () => {
    projectsQuery.refetch()
    tasksQuery.refetch()
    linksQuery.refetch()
    ledgerQuery.refetch()
    intelligenceQuery.refetch()
    if (insightsProject) {
      projectInsightsQuery.refetch()
    }
    if (trfProject) {
      projectTrfQuery.refetch()
    }
  }

  const handleFormSubmit = (event: React.FormEvent) => {
    event.preventDefault()
    if (!form.name.trim()) {
      toast.error('Project name is required')
      return
    }
    if (formMode === 'create') {
      createMutation.mutate({
        name: form.name.trim(),
        description: form.description.trim(),
        priority: form.priority,
        status: form.status,
      })
    } else if (formMode === 'edit' && editingProject) {
      updateMutation.mutate({
        name: editingProject.name,
        patch: {
          description: form.description.trim(),
          priority: form.priority,
          status: form.status,
        },
      })
    }
  }

  const handleDelete = (project: EnrichedProject) => {
    if (!window.confirm(`Delete project "${project.name}"? This action cannot be undone.`)) {
      return
    }
    if (insightsProject?.name === project.name) {
      setInsightsProject(null)
    }
    deleteMutation.mutate(project.name)
  }

  const handleMove = (project: EnrichedProject, direction: 'up' | 'down') => {
    const idx = orderedProjects.findIndex((p) => p.name === project.name)
    if (idx === -1) return
    const targetIndex = direction === 'up' ? idx - 1 : idx + 1
    if (targetIndex < 0 || targetIndex >= orderedProjects.length) return
    const neighbor = orderedProjects[targetIndex]
    reorderMutation.mutate({ source: project, target: neighbor })
  }

  if (isLoading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="h-12 w-12 animate-spin rounded-full border-b-2 border-[color:var(--osd-accent)]" />
      </div>
    )
  }

  const linkErrorMessage =
    linksQuery.isError && linksQuery.error instanceof Error ? linksQuery.error.message : undefined
  const ledgerErrorMessage =
    ledgerQuery.isError && ledgerQuery.error instanceof Error ? ledgerQuery.error.message : undefined
  const intelligenceErrorMessage =
    intelligenceQuery.isError && intelligenceQuery.error instanceof Error
      ? intelligenceQuery.error.message
      : undefined
  const reasoningHistoryErrorMessage =
    reasoningHistoryQuery.isError && reasoningHistoryQuery.error instanceof Error
      ? reasoningHistoryQuery.error.message
      : undefined
  const reasoningRunErrorMessage =
    reasoningMutation.isError && reasoningMutation.error instanceof Error
      ? reasoningMutation.error.message
      : undefined

  return (
    <div className="space-y-8 px-4 py-8 text-[color:var(--osd-text)]">
      <header
        id="overview"
        className="rounded-3xl bg-gradient-to-r from-[var(--osd-accentBlue)] via-[var(--osd-accent)] to-[var(--osd-accentPurple)] p-8 shadow-2xl shadow-slate-900/40"
      >
        <div className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.35em] text-white/70">Workspaces · Capsules · Ownership</p>
            <h1 className="mt-2 text-3xl font-bold">Master Stack · Projects & Workspaces</h1>
            <p className="mt-2 max-w-3xl text-sm text-white/85">
              Mirrors the Tkinter Projects pane — live snapshot of every workspace pulled from FastAPI, including task
              summaries and capsule readiness. Desktop + browser share the same React surface, so runbooks stay in sync.
            </p>
          </div>
          <div className="flex flex-wrap gap-3">
            <button
              onClick={handleRefresh}
              data-testid="projects-refresh"
              className="inline-flex items-center rounded-full bg-white/15 px-5 py-3 text-sm font-semibold text-white hover:bg-white/25"
            >
              <RefreshCw className="mr-2 h-4 w-4" />
              Refresh Snapshot
            </button>
            <button
              onClick={openCreateForm}
              data-testid="projects-new"
              className="inline-flex items-center rounded-full bg-white text-sm font-semibold text-[var(--osd-accent)] shadow-lg shadow-slate-900/30 px-5 py-3"
            >
              <Plus className="mr-2 h-4 w-4" />
              New Project
            </button>
          </div>
        </div>
        <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {headerStats.map((stat) => (
            <div key={stat.label} className="rounded-2xl bg-white/10 p-4">
              <p className="text-xs uppercase tracking-wide text-white/70">{stat.label}</p>
              <p className="mt-2 text-2xl font-bold">{stat.value}</p>
              <p className="text-xs text-white/80">{stat.detail}</p>
            </div>
          ))}
        </div>
        {storageQuery.data && (
          <div className="mt-6 rounded-2xl border border-white/15 bg-white/10 px-4 py-3 text-sm text-white/85">
            <p className="text-xs uppercase tracking-[0.35em] text-white/70">Persistence</p>
            <p className="mt-1">
              DB: <span className="font-mono text-white/90">{storageQuery.data.db_path}</span> · Projects:{' '}
              <strong>{storageQuery.data.project_count}</strong> · Tasks: <strong>{storageQuery.data.task_count}</strong>
            </p>
            {storageQuery.data.project_count < 10 && (
              <p className="mt-2 text-xs text-white/75">
                If you expected many more projects, your backend may be pointing at a new/empty SQLite file. Point
                <span className="font-mono"> ASSISTANT_HUB_DB</span> to your previous <span className="font-mono">assistant_hub.db</span>
                (or copy it into the configured data directory) and reload.
              </p>
            )}
          </div>
        )}
      </header>

      {linkErrorMessage && (
        <div className="rounded-2xl border border-amber-500/30 bg-amber-500/10 px-4 py-3 text-sm text-amber-100 shadow-inner shadow-amber-900/30">
          Linked documents are temporarily unavailable: {linkErrorMessage}
        </div>
      )}
      {ledgerErrorMessage && (
        <div className="rounded-2xl border border-rose-500/30 bg-rose-500/10 px-4 py-3 text-sm text-rose-100 shadow-inner shadow-rose-900/30">
          Ledger events failed to load: {ledgerErrorMessage}
        </div>
      )}
      {intelligenceErrorMessage && (
        <div className="rounded-2xl border border-amber-500/30 bg-amber-500/10 px-4 py-3 text-sm text-amber-100 shadow-inner shadow-amber-900/30">
          Project intelligence service unavailable: {intelligenceErrorMessage}
        </div>
      )}

      {formMode && (
        <form
          id="create"
          onSubmit={handleFormSubmit}
          className="glass-panel space-y-4 border border-[color:var(--osd-border)] p-6"
        >
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold">
              {formMode === 'edit' ? `Update ${editingProject?.name ?? 'Project'}` : 'Create Project'}
            </h2>
            <button
              type="button"
              onClick={closeForm}
              className="rounded-full border border-[color:var(--osd-border)] px-3 py-1 text-xs uppercase tracking-widest text-[color:var(--osd-muted)] hover:border-[color:var(--osd-accent)] hover:text-[color:var(--osd-accent)]"
            >
              Close
            </button>
          </div>
          <div className="grid gap-4 md:grid-cols-2">
            <label className="space-y-2 text-sm">
              <span>Name</span>
              <input
                type="text"
                value={form.name}
                disabled={formMode === 'edit'}
                onChange={(e) => setForm((prev) => ({ ...prev, name: e.target.value }))}
                data-testid="project-form-name"
                className="w-full rounded-xl border border-[color:var(--osd-border)] bg-[color:var(--osd-surfaceAlt)] px-3 py-2 disabled:opacity-60"
                placeholder="Atlas Master Stack"
                required
              />
            </label>
            <label className="space-y-2 text-sm">
              <span>Priority</span>
              <select
                value={form.priority}
                onChange={(e) => setForm((prev) => ({ ...prev, priority: e.target.value }))}
                data-testid="project-form-priority"
                className="w-full rounded-xl border border-[color:var(--osd-border)] bg-[color:var(--osd-surfaceAlt)] px-3 py-2"
              >
                {['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map((level) => (
                  <option key={level} value={level}>
                    {level}
                  </option>
                ))}
              </select>
            </label>
          </div>
          <label className="space-y-2 text-sm">
            <span>Status</span>
            <select
              value={form.status}
              onChange={(e) => setForm((prev) => ({ ...prev, status: e.target.value }))}
              data-testid="project-form-status"
              className="w-full rounded-xl border border-[color:var(--osd-border)] bg-[color:var(--osd-surfaceAlt)] px-3 py-2"
            >
              {['active', 'planning', 'paused', 'completed'].map((status) => (
                <option key={status} value={status}>
                  {status}
                </option>
              ))}
            </select>
          </label>
          <label className="space-y-2 text-sm">
            <span>Description</span>
            <textarea
              value={form.description}
              onChange={(e) => setForm((prev) => ({ ...prev, description: e.target.value }))}
              data-testid="project-form-description"
              className="w-full rounded-2xl border border-[color:var(--osd-border)] bg-[color:var(--osd-surfaceAlt)] px-3 py-2"
              rows={3}
              placeholder="Mission, scope, or capsule objectives"
            />
          </label>
          <div className="flex flex-wrap gap-3">
            <button
              type="submit"
              disabled={createMutation.isPending || updateMutation.isPending}
              data-testid="project-form-submit"
              className="rounded-full bg-[color:var(--osd-accent)] px-5 py-2 text-sm font-semibold text-white hover:bg-[color:var(--osd-accentHover)] disabled:opacity-50"
            >
              {formMode === 'edit'
                ? updateMutation.isPending
                  ? 'Saving…'
                  : 'Save Changes'
                : createMutation.isPending
                  ? 'Creating…'
                  : 'Create Project'}
            </button>
            <button
              type="button"
              onClick={closeForm}
              className="rounded-full border border-[color:var(--osd-border)] px-5 py-2 text-sm"
            >
              Cancel
            </button>
          </div>
        </form>
      )
}

      <section id="workspaces" className="grid gap-6 lg:grid-cols-2">
        {orderedProjects.map((project, index) => {
          const gradient = statusGradients[project.status?.toLowerCase() ?? ''] || 'from-slate-600/50 to-slate-800/70'
          const tasks = project.tasks ?? []
          const links = project.links ?? []
          const intelligence = project.intelligence
          const latestLedgerEvent = project.ledger?.[0]
          const canMoveUp = index > 0
          const canMoveDown = index < orderedProjects.length - 1
          const ledgerDate = latestLedgerEvent ? new Date(latestLedgerEvent.created_at) : null
          const ledgerTimestamp =
            ledgerDate && !Number.isNaN(ledgerDate.getTime())
              ? ledgerDate.toLocaleString()
              : latestLedgerEvent?.created_at
          const ledgerPayloadTitle = latestLedgerEvent ? getPayloadTitle(latestLedgerEvent.payload) : undefined
          return (
            <article key={project.name} className="glass-panel border border-[color:var(--osd-border)] p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs uppercase tracking-[0.3em] text-[color:var(--osd-muted)]">Workspace</p>
                  <h2 className="text-2xl font-semibold text-[color:var(--osd-text)]">{project.name}</h2>
                  <p className="mt-1 text-sm text-[color:var(--osd-muted)]">{project.description || 'No description provided.'}</p>
                </div>
                <div className={`rounded-2xl px-4 py-2 text-xs font-semibold text-white bg-gradient-to-r ${gradient}`}>
                  {project.status || 'planned'}
                </div>
              </div>
              <div className="mt-4 flex flex-wrap gap-3 text-xs">
                <span className={`rounded-full px-3 py-1 ${priorityPills[project.priority] || 'bg-slate-500/15 text-slate-200'}`}>
                  Priority · {project.priority}
                </span>
                <span className="rounded-full border border-[color:var(--osd-border)] px-3 py-1 text-[color:var(--osd-muted)]">
                  Owner · {(project as any).owner_id ?? 'OS Ops'}
                </span>
                <span className="rounded-full border border-[color:var(--osd-border)] px-3 py-1 text-[color:var(--osd-muted)]">
                  Tasks · {tasks.length}
                </span>
              </div>
              {intelligence && (
                <div className="mt-6 grid gap-3 sm:grid-cols-2">
                  <div className="rounded-2xl border border-[color:var(--osd-border)] bg-[color:var(--osd-surfaceAlt)] px-4 py-3">
                    <p className="text-xs uppercase tracking-[0.3em] text-[color:var(--osd-muted)]">Health Score</p>
                    <p className="mt-1 text-2xl font-bold text-[color:var(--osd-text)]">{intelligence.health_score}</p>
                    <p className="text-xs text-[color:var(--osd-muted)]">
                      Completion {(intelligence.completion_ratio * 100).toFixed(0)}% · {intelligence.open_tasks} open
                    </p>
                  </div>
                  <div
                    className={`rounded-2xl border px-4 py-3 text-sm ${riskBadgeTone[intelligence.risk_level] || riskBadgeTone.guarded}`}
                  >
                    <p className="text-xs uppercase tracking-[0.3em]">Risk</p>
                    <p className="text-lg font-semibold">{riskLabel[intelligence.risk_level] || intelligence.risk_level}</p>
                    <p className="text-xs">
                      {intelligence.summary}
                      {!intelligence.ledger_ok ? ' · Ledger integrity check required' : ''}
                    </p>
                  </div>
                </div>
              )}
              <div className="mt-4 flex flex-wrap gap-2 text-xs">
                <button
                  type="button"
                  onClick={() => canMoveUp && handleMove(project, 'up')}
                  disabled={!canMoveUp}
                  className="inline-flex items-center gap-2 rounded-full border border-[color:var(--osd-border)] px-3 py-1 text-[color:var(--osd-muted)] hover:border-[color:var(--osd-accent)] hover:text-[color:var(--osd-accent)] disabled:opacity-40"
                >
                  <ArrowUpNarrowWide className="h-3.5 w-3.5" />
                  Move Up
                </button>
                <button
                  type="button"
                  onClick={() => canMoveDown && handleMove(project, 'down')}
                  disabled={!canMoveDown}
                  className="inline-flex items-center gap-2 rounded-full border border-[color:var(--osd-border)] px-3 py-1 text-[color:var(--osd-muted)] hover:border-[color:var(--osd-accent)] hover:text-[color:var(--osd-accent)] disabled:opacity-40"
                >
                  <ArrowDownNarrowWide className="h-3.5 w-3.5" />
                  Move Down
                </button>
                <button
                  type="button"
                  onClick={() => openEditForm(project)}
                  className="inline-flex items-center gap-2 rounded-full border border-[color:var(--osd-border)] px-3 py-1 text-[color:var(--osd-muted)] hover:border-[color:var(--osd-accent)] hover:text-[color:var(--osd-accent)]"
                >
                  <PenSquare className="h-3.5 w-3.5" />
                  Edit
                </button>
                <button
                  type="button"
                  onClick={() => openInsightsPanel(project)}
                  className="inline-flex items-center gap-2 rounded-full border border-transparent bg-[color:var(--osd-accent)] px-3 py-1 text-white shadow-lg shadow-slate-900/20 hover:bg-[color:var(--osd-accentHover)]"
                >
                  <Sparkles className="h-3.5 w-3.5" />
                  Insights
                </button>
                <button
                  type="button"
                  onClick={() => openTrfPanel(project)}
                  className="inline-flex items-center gap-2 rounded-full border border-[color:var(--osd-border)] bg-[color:var(--osd-surfaceAlt)] px-3 py-1 text-[color:var(--osd-text)] hover:border-[color:var(--osd-accent)]"
                >
                  <Cpu className="h-3.5 w-3.5" />
                  TRF Trace
                </button>
                <button
                  type="button"
                  onClick={() => handleDelete(project)}
                  data-testid={`project-delete:${project.name}`}
                  className="inline-flex items-center gap-2 rounded-full border border-rose-500/60 px-3 py-1 text-rose-200 hover:bg-rose-500/10"
                >
                  <Trash2 className="h-3.5 w-3.5" />
                  Delete
                </button>
              </div>
              <div className="mt-6 grid gap-3">
                {tasks.slice(0, 4).map((task) => (
                  <div key={task.id} className="flex items-center justify-between rounded-2xl border border-[color:var(--osd-border)] bg-[color:var(--osd-surfaceAlt)] px-4 py-3 text-sm">
                    <div>
                      <p className="font-medium text-[color:var(--osd-text)]">{task.title}</p>
                      <p className="text-xs text-[color:var(--osd-muted)]">{task.status} · Priority {task.priority}</p>
                    </div>
                    <span className="text-xs text-[color:var(--osd-muted)]">{task.due_date ? `Due ${task.due_date}` : 'No due date'}</span>
                  </div>
                ))}
                {tasks.length === 0 && (
                  <p className="rounded-2xl border border-dashed border-[color:var(--osd-border)] px-4 py-6 text-center text-sm text-[color:var(--osd-muted)]">
                    No tasks yet. Capsules can auto-draft tasks once the workspace kicks off.
                  </p>
                )}
              </div>
              <div className="mt-6 border-t border-dashed border-[color:var(--osd-border)] pt-4">
                <p className="text-xs uppercase tracking-[0.3em] text-[color:var(--osd-muted)]">
                  Linked Docs & OneNote
                </p>
                <div className="mt-3 flex flex-wrap gap-2">
                  {links.map((link) => {
                    const badgeBase =
                      'inline-flex items-center gap-2 rounded-full border px-3 py-1 text-xs transition-colors'
                    const badgeState = link.href
                      ? 'border-[color:var(--osd-border)] text-[color:var(--osd-text)] hover:border-[color:var(--osd-accent)] hover:text-[color:var(--osd-accent)]'
                      : link.available
                        ? 'border border-dashed border-[color:var(--osd-border)] text-[color:var(--osd-muted)]'
                        : 'border border-dashed border-rose-500/40 text-rose-200/80'
                    const content = (
                      <>
                        <FileText className="h-3.5 w-3.5 opacity-70" />
                        <span>{link.label}</span>
                        {link.href && <ExternalLink className="h-3 w-3 opacity-60" />}
                      </>
                    )
                    return link.href ? (
                      <a
                        key={`${link.id}-${link.integration_type}`}
                        href={link.href}
                        target="_blank"
                        rel="noreferrer"
                        className={`${badgeBase} ${badgeState}`}
                        title={link.title}
                      >
                        {content}
                      </a>
                    ) : (
                      <span
                        key={`${link.id}-${link.integration_type}`}
                        className={`${badgeBase} ${badgeState}`}
                        title={link.title || link.description || link.integration_type}
                      >
                        {content}
                      </span>
                    )
                  })}
                  {links.length === 0 && (
                    <span className="rounded-full border border-dashed border-[color:var(--osd-border)] px-3 py-1 text-xs text-[color:var(--osd-muted)]">
                      No linked docs yet — add OneNote or uploads from the Tk cockpit.
                    </span>
                  )}
                </div>
              </div>
              <div className="mt-6 border-t border-dashed border-[color:var(--osd-border)] pt-4">
                <p className="text-xs uppercase tracking-[0.3em] text-[color:var(--osd-muted)]">Latest Ledger Event</p>
                {latestLedgerEvent ? (
                  <div className="mt-3 rounded-2xl border border-[color:var(--osd-border)] bg-[color:var(--osd-surfaceAlt)] px-4 py-3 text-sm">
                    <p className="font-medium text-[color:var(--osd-text)]">
                      {latestLedgerEvent.event_type.replace(/_/g, ' ')}
                    </p>
                    <p className="text-xs text-[color:var(--osd-muted)]">
                      {ledgerTimestamp ? `Recorded ${ledgerTimestamp}` : 'Recorded recently'}
                      {ledgerPayloadTitle ? ` · ${ledgerPayloadTitle}` : ''}
                    </p>
                  </div>
                ) : (
                  <p className="mt-3 rounded-2xl border border-dashed border-[color:var(--osd-border)] px-3 py-2 text-xs text-[color:var(--osd-muted)]">
                    No ledger activity yet.
                  </p>
                )}
              </div>
            </article>
          )
        })}
        {enrichedProjects.length === 0 && (
          <div className="glass-panel border border-[color:var(--osd-border)] p-10 text-center text-sm text-[color:var(--osd-muted)]">
            No projects registered. Import or create one to populate the Master Stack.
          </div>
        )}
      </section>

      <section id="links" className="rounded-3xl border border-[color:var(--osd-border)] bg-[color:var(--osd-surfaceAlt)] p-6">
        <div className="flex items-start justify-between gap-3">
          <div>
            <p className="text-xs uppercase tracking-[0.35em] text-[color:var(--osd-muted)]">Spec §6.2 · §7.2</p>
            <h3 className="text-lg font-semibold text-[color:var(--osd-text)]">Linked assets index</h3>
            <p className="text-sm text-[color:var(--osd-muted)]">
              Consolidated view of OneNote mirrors and document links tied to each project.
            </p>
          </div>
        </div>
        <div className="mt-4 space-y-3 max-h-72 overflow-y-auto pr-1">
          {orderedProjects.map((project) => {
            const links = linksByProject.get(project.name) ?? []
            return (
              <div
                key={`links-${project.name}`}
                className="rounded-2xl border border-[color:var(--osd-border)] bg-[color:var(--osd-background)] p-4"
              >
                <p className="text-sm font-semibold text-[color:var(--osd-text)]">{project.name}</p>
                <div className="mt-2 flex flex-wrap gap-2">
                  {links.length ? (
                    links.map((link) => (
                      <a
                        key={`link-${link.id}`}
                        href={link.href ?? '#'}
                        target={link.href ? '_blank' : undefined}
                        rel={link.href ? 'noreferrer' : undefined}
                        className="rounded-full border border-[color:var(--osd-border)] px-3 py-1 text-xs text-[color:var(--osd-text)] hover:border-[color:var(--osd-accent)]"
                        title={link.description || link.external_id}
                        onClick={(event) => {
                          if (!link.href) {
                            event.preventDefault()
                          }
                        }}
                      >
                        {link.label}
                      </a>
                    ))
                  ) : (
                    <span className="rounded-full border border-dashed border-[color:var(--osd-border)] px-3 py-1 text-xs text-[color:var(--osd-muted)]">
                      No linked assets
                    </span>
                  )}
                </div>
              </div>
            )
          })}
          {!orderedProjects.length && (
            <p className="rounded-2xl border border-dashed border-[color:var(--osd-border)] px-4 py-6 text-center text-sm text-[color:var(--osd-muted)]">
              Create a project to start attaching documents and OneNote mirrors.
            </p>
          )}
        </div>
      </section>

      <section id="trf" className="rounded-3xl border border-[color:var(--osd-border)] bg-[color:var(--osd-surfaceAlt)] p-6">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.35em] text-[color:var(--osd-muted)]">Spec §4.6–§4.8</p>
            <h3 className="text-lg font-semibold text-[color:var(--osd-text)]">TRF trace viewer</h3>
            <p className="text-sm text-[color:var(--osd-muted)]">
              Open a project’s Theoretical Reasoning Framework trace to review entropy, resonance, continuity, and audit gates.
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            {orderedProjects.slice(0, 6).map((project) => (
              <button
                key={`trf-open-${project.name}`}
                type="button"
                onClick={() => openTrfPanel(project)}
                className="rounded-full border border-[color:var(--osd-border)] bg-[color:var(--osd-background)] px-4 py-2 text-xs font-semibold text-[color:var(--osd-text)] hover:border-[color:var(--osd-accent)]"
              >
                Open · {project.name}
              </button>
            ))}
            {orderedProjects.length > 6 && (
              <span className="rounded-full border border-dashed border-[color:var(--osd-border)] px-4 py-2 text-xs text-[color:var(--osd-muted)]">
                More via each project card
              </span>
            )}
          </div>
        </div>
      </section>

      <section className="space-y-6">
        <div className="glass-panel border border-[color:var(--osd-border)] p-6">
          <div className="grid gap-6 lg:grid-cols-2">
            <div>
              <h3 className="text-lg font-semibold text-[color:var(--osd-text)]">Status Summary</h3>
              <p className="text-sm text-[color:var(--osd-muted)] mb-3">
                Mirrors the Tkinter summary widget so desktop + web stay in sync.
              </p>
              <ul className="space-y-2 text-sm text-[color:var(--osd-muted)]">
                {Object.entries(statusCounts).map(([status, count]) => (
                  <li
                    key={status}
                    className="flex justify-between rounded-xl border border-[color:var(--osd-border)] px-3 py-2"
                  >
                    <span className="uppercase tracking-wide">{status}</span>
                    <span className="font-semibold text-[color:var(--osd-text)]">{count}</span>
                  </li>
                ))}
                {Object.keys(statusCounts).length === 0 && <li>No status data yet.</li>}
              </ul>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-[color:var(--osd-text)]">Priority Summary</h3>
              <p className="text-sm text-[color:var(--osd-muted)] mb-3">Matches the Tkinter priority counts panel.</p>
              <ul className="space-y-2 text-sm text-[color:var(--osd-muted)]">
                {Object.entries(priorityCounts).map(([priority, count]) => (
                  <li
                    key={priority}
                    className="flex justify-between rounded-xl border border-[color:var(--osd-border)] px-3 py-2"
                  >
                    <span className="uppercase tracking-wide">{priority}</span>
                    <span className="font-semibold text-[color:var(--osd-text)]">{count}</span>
                  </li>
                ))}
                {Object.keys(priorityCounts).length === 0 && <li>No priority data yet.</li>}
              </ul>
            </div>
          </div>
        </div>
        <div id="intelligence">
          <ProjectIntelligencePanel
          highestRisk={highestRiskProjects}
          stats={intelligenceStats}
          isLoading={intelligenceQuery.isLoading}
          isFetching={intelligenceQuery.isFetching}
          error={intelligenceQuery.error}
          onRefresh={() => intelligenceQuery.refetch()}
          />
        </div>
        <div id="ledger">
          <ProjectLedgerPanel
          events={latestLedgerEvents}
          integrityOk={ledgerIntegrityOk}
          isLoading={ledgerQuery.isLoading}
          isFetching={ledgerQuery.isFetching}
          error={ledgerQuery.error}
          selectedFilter={ledgerProjectFilter}
          projectOptions={ledgerProjectOptions}
          onProjectChange={handleLedgerProjectChange}
          onRefresh={() => ledgerQuery.refetch()}
          />
        </div>
        <div id="reasoning">
          <ReasoningLabPanel
          personas={personaOptions}
          personasLoading={reasoningPersonasQuery.isLoading}
          history={reasoningHistory}
          historyLoading={reasoningHistoryQuery.isLoading}
          historyError={reasoningHistoryErrorMessage}
          onSelectPersona={setSelectedPersona}
          selectedPersona={selectedPersona}
          queryText={reasoningQueryText}
          onQueryChange={setReasoningQueryText}
          onRun={handleReasoningRun}
          isRunning={reasoningMutation.isPending}
          currentTrace={activeTrace}
          onSelectTrace={handleHistorySelect}
          runError={reasoningRunErrorMessage}
          />
        </div>
      </section>
      {insightsProject && (
      <ProjectInsightsDrawer
        project={insightsProject}
        insight={projectInsightsQuery.data}
        isLoading={projectInsightsQuery.isLoading}
        isFetching={projectInsightsQuery.isFetching}
        error={projectInsightsQuery.error}
        trf={insightsProjectTrfQuery.data}
        trfLoading={insightsProjectTrfQuery.isLoading}
        trfFetching={insightsProjectTrfQuery.isFetching}
        trfError={insightsProjectTrfQuery.error}
        onClose={() => setInsightsProject(null)}
        onRefresh={() => projectInsightsQuery.refetch()}
        onRefreshTrf={() => insightsProjectTrfQuery.refetch()}
      />
      )}
      {trfProject && (
        <ProjectTrfDrawer
          project={trfProject}
          snapshot={projectTrfQuery.data}
          isLoading={projectTrfQuery.isLoading}
          isFetching={projectTrfQuery.isFetching}
          error={projectTrfQuery.error}
          onClose={() => setTrfProject(null)}
          onRefresh={() => projectTrfQuery.refetch()}
        />
      )}
    </div>
  )
}

type ProjectIntelligencePanelProps = {
  highestRisk: ProjectIntelligence[]
  stats: {
    averageHealth: number | null
    highRisk: number
    ledgerAlerts: number
  }
  isLoading: boolean
  isFetching: boolean
  error: unknown
  onRefresh: () => void
}

type ProjectInsightsDrawerProps = {
  project: EnrichedProject
  insight?: ProjectInsightResponse
  isLoading: boolean
  isFetching: boolean
  error: unknown
  trf?: ProjectTRFResponse
  trfLoading: boolean
  trfFetching: boolean
  trfError: unknown
  onClose: () => void
  onRefresh: () => void
  onRefreshTrf: () => void
}

type ProjectTrfDrawerProps = {
  project: EnrichedProject
  snapshot?: ProjectTRFResponse
  isLoading: boolean
  isFetching: boolean
  error: unknown
  onClose: () => void
  onRefresh: () => void
}

type ProjectLedgerPanelProps = {
  events: ProjectLedgerEvent[]
  integrityOk: boolean
  isLoading: boolean
  isFetching: boolean
  error: unknown
  selectedFilter: string | null
  projectOptions: string[]
  onProjectChange: (projectName: string | null) => void
  onRefresh: () => void
}

type ReasoningLabPanelProps = {
  personas: ReasoningPersona[]
  personasLoading: boolean
  history: ReasoningTrace[]
  historyLoading: boolean
  historyError?: string
  selectedPersona: string
  onSelectPersona: (persona: string) => void
  queryText: string
  onQueryChange: (value: string) => void
  onRun: () => void
  isRunning: boolean
  currentTrace: ReasoningTrace | null
  onSelectTrace: (trace: ReasoningTrace) => void
  runError?: string
}

function ProjectIntelligencePanel({
  highestRisk,
  stats,
  isLoading,
  isFetching,
  error,
  onRefresh,
}: ProjectIntelligencePanelProps) {
  const avgHealth = stats.averageHealth !== null ? `${stats.averageHealth}%` : '—'
  const errorMessage = error instanceof Error ? error.message : 'Unable to load intelligence metrics.'
  return (
    <div className="rounded-3xl border border-[color:var(--osd-border)] bg-[color:var(--osd-surfaceAlt)] p-6 space-y-5">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.35em] text-[color:var(--osd-muted)]">Spec §4.5 · §4.8</p>
          <h3 className="text-lg font-semibold text-[color:var(--osd-text)] flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-[color:var(--osd-accent)]" />
            Project Intelligence
          </h3>
          <p className="text-sm text-[color:var(--osd-muted)] max-w-3xl">
            AIC’s quick health heuristic for every workspace, derived from tasks, ledger events, and TRF governance cues.
          </p>
        </div>
        <button
          type="button"
          onClick={onRefresh}
          disabled={isFetching}
          className="inline-flex items-center gap-2 rounded-full border border-[color:var(--osd-border)] px-4 py-2 text-xs font-semibold text-[color:var(--osd-text)] hover:border-[color:var(--osd-accent)] disabled:opacity-60"
        >
          <RefreshCw className="h-4 w-4" />
          {isFetching ? 'Recomputing…' : 'Refresh Intelligence'}
        </button>
      </div>
      <div className="grid gap-3 sm:grid-cols-3">
        <div className="rounded-2xl border border-[color:var(--osd-border)] p-3 text-xs text-[color:var(--osd-muted)]">
          <div className="flex items-center gap-2 text-sm text-[color:var(--osd-text)]">
            <ArrowUpNarrowWide className="h-4 w-4" />
            Avg health
          </div>
          <p className="mt-1 text-2xl font-semibold text-[color:var(--osd-text)]">{avgHealth}</p>
        </div>
        <div className="rounded-2xl border border-[color:var(--osd-border)] p-3 text-xs text-[color:var(--osd-muted)]">
          <div className="flex items-center gap-2 text-sm text-[color:var(--osd-text)]">
            <AlertTriangle className="h-4 w-4 text-amber-400" />
            High-risk projects
          </div>
          <p className="mt-1 text-2xl font-semibold text-[color:var(--osd-text)]">{stats.highRisk}</p>
        </div>
        <div className="rounded-2xl border border-[color:var(--osd-border)] p-3 text-xs text-[color:var(--osd-muted)]">
          <div className="flex items-center gap-2 text-sm text-[color:var(--osd-text)]">
            <Shield className="h-4 w-4" />
            Ledger alerts
          </div>
          <p className="mt-1 text-2xl font-semibold text-[color:var(--osd-text)]">{stats.ledgerAlerts}</p>
        </div>
      </div>
      {Boolean(error) && (
        <div className="rounded-2xl border border-rose-500/60 bg-rose-500/10 px-4 py-3 text-sm text-rose-100">
          <strong>Intelligence unavailable.</strong> {errorMessage}
        </div>
      )}
      {isLoading ? (
        <div className="flex h-48 items-center justify-center">
          <div className="h-10 w-10 animate-spin rounded-full border-b-2 border-[color:var(--osd-accent)]" />
        </div>
      ) : (
        <div className="space-y-3">
          {highestRisk.length ? (
            highestRisk.map((intel) => (
              <article
                key={`${intel.project_id}-${intel.risk_level}`}
                className="rounded-2xl border border-[color:var(--osd-border)] bg-[color:var(--osd-background)] p-4 text-sm text-[color:var(--osd-muted)]"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-[color:var(--osd-text)] font-semibold">{intel.project_id}</p>
                    <p className="text-xs uppercase tracking-[0.4em]">
                      {riskLabel[intel.risk_level] || intel.risk_level}
                    </p>
                  </div>
                  <div className={`rounded-full px-3 py-1 text-xs ${riskBadgeTone[intel.risk_level] || riskBadgeTone.guarded}`}>
                    {intel.summary}
                  </div>
                </div>
                <div className="mt-2 text-xs text-[color:var(--osd-muted)]">
                  Health {intel.health_score} · {intel.open_tasks} open ·{' '}
                  {intel.critical_tasks} critical · Ledger {intel.ledger_ok ? 'verified' : 'alert'}
                </div>
              </article>
            ))
          ) : (
            <p className="rounded-2xl border border-dashed border-[color:var(--osd-border)] px-4 py-6 text-center text-sm text-[color:var(--osd-muted)]">
              Intelligence snapshots will populate once ledger + task data are available.
            </p>
          )}
        </div>
      )}
      <div className="flex items-center justify-between text-xs text-[color:var(--osd-muted)]">
        <span>Derived from Project Intelligence subsystem in the canon spec.</span>
        <a
          className="inline-flex items-center gap-1 text-[color:var(--osd-accent)]"
          href="/docs/dashboard.html"
          target="_blank"
          rel="noreferrer"
        >
          <ExternalLink className="h-3 w-3" />
          Read spec
        </a>
      </div>
    </div>
  )
}

function ProjectInsightsDrawer({
  project,
  insight,
  isLoading,
  isFetching,
  error,
  trf,
  trfLoading,
  trfFetching,
  trfError,
  onClose,
  onRefresh,
  onRefreshTrf,
}: ProjectInsightsDrawerProps) {
  const severityTone: Record<string, string> = {
    low: 'text-emerald-300',
    medium: 'text-amber-300',
    high: 'text-rose-300',
    critical: 'text-rose-400',
  }
  const riskScore = insight?.risk.risk_score ?? 0
  const severity = insight?.risk.severity ?? 'unknown'
  const risks = insight?.risk.risks ?? []
  const recommendations = insight?.risk.recommendations ?? 'No recommendations yet.'
  const forecast = insight?.forecast
  const errorMessage = error instanceof Error ? error.message : 'Unable to load insights.'
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 px-4 py-6">
      <div className="relative w-full max-w-3xl rounded-3xl border border-[color:var(--osd-border)] bg-[color:var(--osd-background)] p-6 shadow-2xl shadow-slate-900/50">
        <div className="flex items-start justify-between gap-3">
          <div>
            <p className="text-xs uppercase tracking-[0.35em] text-[color:var(--osd-muted)]">Spec §4.5 · §4.8 · §6.2</p>
            <h3 className="text-2xl font-semibold text-[color:var(--osd-text)] flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-[color:var(--osd-accent)]" />
              Project Intelligence · {project.name}
            </h3>
            <p className="text-sm text-[color:var(--osd-muted)]">
              Mirrors the Tkinter insight flyout — shared FastAPI snapshot powering both desktop and browser shells.
            </p>
            <p className="text-xs text-[color:var(--osd-muted)] mt-1">
              Generated {insight ? formatTimestamp(insight.generated_at) : '—'}
            </p>
          </div>
          <div className="flex gap-2">
            <button
              type="button"
              onClick={onRefresh}
              disabled={isFetching}
              className="inline-flex items-center gap-2 rounded-full border border-[color:var(--osd-border)] px-4 py-2 text-xs font-semibold text-[color:var(--osd-text)] hover:border-[color:var(--osd-accent)] disabled:opacity-60"
            >
              <RefreshCw className="h-4 w-4" />
              {isFetching ? 'Refreshing…' : 'Refresh'}
            </button>
            <button
              type="button"
              onClick={onClose}
              className="inline-flex items-center gap-2 rounded-full border border-[color:var(--osd-border)] px-4 py-2 text-xs font-semibold text-[color:var(--osd-text)] hover:border-[color:var(--osd-accent)]"
            >
              <X className="h-4 w-4" />
              Close
            </button>
          </div>
        </div>
        {Boolean(error) && (
          <div className="mt-4 rounded-2xl border border-rose-500/60 bg-rose-500/10 px-4 py-3 text-sm text-rose-100">
            <strong>Insights unavailable.</strong> {errorMessage}
          </div>
        )}
        {isLoading ? (
          <div className="flex h-64 items-center justify-center">
            <div className="h-12 w-12 animate-spin rounded-full border-b-2 border-[color:var(--osd-accent)]" />
          </div>
        ) : (
          <div className="mt-6 space-y-6">
            <div className="rounded-2xl border border-[color:var(--osd-border)] p-5">
              <div className="flex flex-wrap items-center justify-between gap-4">
                <div>
                  <p className="text-xs uppercase tracking-[0.4em] text-[color:var(--osd-muted)]">Risk Score</p>
                  <p className="text-4xl font-bold text-[color:var(--osd-text)]">{riskScore}</p>
                </div>
                <div className={`text-sm font-semibold ${severityTone[severity] ?? 'text-[color:var(--osd-muted)]'}`}>
                  Severity · {severity.toUpperCase()}
                </div>
              </div>
              <div className="mt-4 h-3 w-full overflow-hidden rounded-full border border-[color:var(--osd-border)] bg-[color:var(--osd-surfaceAlt)]">
                <div
                  className="h-full rounded-full bg-gradient-to-r from-rose-400 via-amber-400 to-emerald-400"
                  style={{ width: `${Math.min(100, Math.max(0, riskScore))}%` }}
                />
              </div>
              <p className="mt-2 text-xs text-[color:var(--osd-muted)]">
                {insight?.risk.completed_tasks ?? 0} completed · {insight?.risk.total_tasks ?? 0} total ·{' '}
                {((insight?.risk.completion_rate ?? 0) * 100).toFixed(0)}% complete
              </p>
            </div>
            <div className="rounded-2xl border border-[color:var(--osd-border)] p-5">
              <p className="text-xs uppercase tracking-[0.35em] text-[color:var(--osd-muted)]">Risks</p>
              {risks.length === 0 ? (
                <p className="mt-3 text-sm text-[color:var(--osd-muted)]">
                  No active risks detected for this workspace.
                </p>
              ) : (
                <ul className="mt-3 space-y-2 text-sm text-[color:var(--osd-muted)]">
                  {risks.map((item, idx) => (
                    <li
                      key={`${item.type}-${idx}`}
                      className="rounded-2xl border border-[color:var(--osd-border)] bg-[color:var(--osd-surfaceAlt)] px-4 py-3"
                    >
                      <p className="font-semibold text-[color:var(--osd-text)]">
                        {item.message}
                        {item.count ? ` · ${item.count}` : ''}
                      </p>
                      <p className="text-xs uppercase tracking-[0.35em]">
                        {item.type.replace(/_/g, ' ')} · {item.severity}
                      </p>
                    </li>
                  ))}
                </ul>
              )}
            </div>
            <div className="rounded-2xl border border-[color:var(--osd-border)] p-5 space-y-3">
              <p className="text-xs uppercase tracking-[0.35em] text-[color:var(--osd-muted)]">Recommendations</p>
              <p className="whitespace-pre-line text-sm text-[color:var(--osd-text)]">{recommendations}</p>
            </div>
            <div className="rounded-2xl border border-[color:var(--osd-border)] p-5">
              <p className="text-xs uppercase tracking-[0.35em] text-[color:var(--osd-muted)]">
                Forecast &amp; Continuity
              </p>
              {forecast ? (
                <div className="mt-3 space-y-2 text-sm text-[color:var(--osd-muted)]">
                  <p className="text-lg font-semibold text-[color:var(--osd-text)]">
                    Target completion: {forecast.predicted_date ?? 'TBD'} ({forecast.confidence} confidence)
                  </p>
                  <p>{forecast.reasoning}</p>
                  <p>
                    Estimated days remaining: {forecast.estimated_days ?? '—'} · Pending tasks:{' '}
                    {forecast.pending_task_count}
                  </p>
                </div>
              ) : (
                <p className="mt-3 text-sm text-[color:var(--osd-muted)]">
                  Forecast unavailable until more task data is recorded.
                </p>
              )}
            </div>
            <div className="rounded-2xl border border-[color:var(--osd-border)] p-5 space-y-4">
              <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <p className="text-xs uppercase tracking-[0.35em] text-[color:var(--osd-muted)]">
                    TRF Snapshot · Spec §4.6–§4.8
                  </p>
                  <p className="text-sm text-[color:var(--osd-muted)]">
                    Inline slice of the Theoretical Reasoning Framework so auditors can see entropy/resonance without leaving this drawer.
                  </p>
                </div>
                <button
                  type="button"
                  onClick={onRefreshTrf}
                  disabled={trfFetching}
                  className="inline-flex items-center gap-2 rounded-full border border-[color:var(--osd-border)] px-4 py-2 text-xs font-semibold text-[color:var(--osd-text)] hover:border-[color:var(--osd-accent)] disabled:opacity-60"
                >
                  <RefreshCw className="h-4 w-4" />
                  {trfFetching ? 'Refreshing…' : 'Refresh TRF'}
                </button>
              </div>
              {Boolean(trfError) ? (
                <div className="rounded-2xl border border-rose-500/60 bg-rose-500/10 px-4 py-3 text-sm text-rose-100">
                  <strong>TRF stream unavailable.</strong>{' '}
                  {trfError instanceof Error ? trfError.message : 'Unable to load TRF snapshot.'}
                </div>
              ) : trfLoading ? (
                <div className="flex h-32 items-center justify-center">
                  <Loader2 className="h-8 w-8 animate-spin text-[color:var(--osd-accent)]" />
                </div>
              ) : trf ? (
                <div className="space-y-4">
                  <div className="grid gap-3 sm:grid-cols-3">
                    {[
                      { label: 'Entropy', value: `${Math.round(trf.entropy * 100)}%` },
                      { label: 'Resonance', value: `${Math.round(trf.resonance * 100)}%` },
                      { label: 'Continuity', value: `${Math.round(trf.continuity * 100)}%` },
                    ].map((metric) => (
                      <div
                        key={metric.label}
                        className="rounded-2xl border border-[color:var(--osd-border)] bg-[color:var(--osd-surfaceAlt)] p-4"
                      >
                        <p className="text-xs uppercase tracking-[0.3em] text-[color:var(--osd-muted)]">{metric.label}</p>
                        <p className="mt-2 text-2xl font-semibold text-[color:var(--osd-text)]">{metric.value}</p>
                      </div>
                    ))}
                  </div>
                  <div className="grid gap-4 lg:grid-cols-2">
                    <div className="rounded-2xl border border-[color:var(--osd-border)] bg-[color:var(--osd-surfaceAlt)] p-4">
                      <h4 className="text-sm font-semibold text-[color:var(--osd-text)] uppercase tracking-[0.3em]">
                        Latest Traces
                      </h4>
                      <div className="mt-3 space-y-3 max-h-48 overflow-y-auto pr-1">
                        {trf.traces.slice(0, 3).map((trace) => (
                          <div key={trace.trace_id} className="rounded-xl border border-[color:var(--osd-border)] p-3">
                            <p className="text-xs uppercase tracking-[0.3em] text-[color:var(--osd-muted)]">
                              {trace.persona} · {trace.operator}
                            </p>
                            <p className="text-sm text-[color:var(--osd-text)]">{trace.premise}</p>
                            <p className="text-xs text-[color:var(--osd-muted)]">
                              {trace.conclusion} · {Math.round(trace.confidence * 100)}% confidence
                            </p>
                          </div>
                        ))}
                        {!trf.traces.length && (
                          <p className="text-xs text-[color:var(--osd-muted)]">No TRF traces recorded yet.</p>
                        )}
                      </div>
                    </div>
                    <div className="rounded-2xl border border-[color:var(--osd-border)] bg-[color:var(--osd-surfaceAlt)] p-4">
                      <h4 className="text-sm font-semibold text-[color:var(--osd-text)] uppercase tracking-[0.3em]">
                        Personas
                      </h4>
                      <div className="mt-3 space-y-2">
                        {trf.personas.slice(0, 3).map((persona) => (
                          <div key={persona.persona} className="rounded-xl border border-[color:var(--osd-border)] p-3 text-sm">
                            <p className="font-semibold text-[color:var(--osd-text)]">
                              {persona.persona}{' '}
                              <span className="text-xs uppercase tracking-[0.3em] text-[color:var(--osd-muted)]">{persona.status}</span>
                            </p>
                            <p className="text-xs text-[color:var(--osd-muted)]">
                              {persona.role} · {persona.utilization}% utilization
                            </p>
                          </div>
                        ))}
                        {!trf.personas.length && (
                          <p className="text-xs text-[color:var(--osd-muted)]">No persona telemetry available.</p>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <p className="text-sm text-[color:var(--osd-muted)]">
                  Request a TRF snapshot to populate entropy, resonance, and continuity metrics.
                </p>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

function ProjectTrfDrawer({
  project,
  snapshot,
  isLoading,
  isFetching,
  error,
  onClose,
  onRefresh,
}: ProjectTrfDrawerProps) {
  const metrics = [
    { label: 'Entropy', value: snapshot ? `${Math.round(snapshot.entropy * 100)}%` : '—', description: 'Intent flux' },
    { label: 'Resonance', value: snapshot ? `${Math.round(snapshot.resonance * 100)}%` : '—', description: 'Persona alignment' },
    { label: 'Continuity', value: snapshot ? `${Math.round(snapshot.continuity * 100)}%` : '—', description: 'Governance hooks' },
  ]
  const traces = snapshot?.traces ?? []
  const personas = snapshot?.personas ?? []
  const heuristics = snapshot?.heuristics ?? []
  const errorMessage = error instanceof Error ? error.message : 'Unable to load TRF snapshot.'

  return (
    <div className="fixed inset-0 z-40 flex items-end justify-center bg-black/60 px-4 pb-8 pt-10 sm:items-center sm:px-6 lg:px-8">
      <div className="relative w-full max-w-4xl rounded-3xl border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-6 pb-8 pt-6 shadow-2xl">
        <header className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.35em] text-[color:var(--osd-muted)]">TRF · Spec §4.5–§4.8</p>
            <h3 className="text-2xl font-semibold text-[color:var(--osd-text)]">
              {project.name} · Theoretical Reasoning Framework
            </h3>
            <p className="text-sm text-[color:var(--osd-muted)]">
              Energy heuristics, persona load, and reasoning traces mirrored from the Tkinter console.
            </p>
          </div>
          <div className="flex gap-2">
            <button
              type="button"
              onClick={onRefresh}
              disabled={isFetching}
              className="inline-flex items-center gap-2 rounded-full border border-[color:var(--osd-border)] px-4 py-2 text-xs font-semibold text-[color:var(--osd-text)] hover:border-[color:var(--osd-accent)] disabled:opacity-60"
            >
              <RefreshCw className="h-4 w-4" />
              {isFetching ? 'Refreshing…' : 'Refresh'}
            </button>
            <button
              type="button"
              onClick={onClose}
              className="inline-flex items-center rounded-full border border-[color:var(--osd-border)] px-3 py-1 text-[color:var(--osd-muted)] hover:border-[color:var(--osd-accent)] hover:text-[color:var(--osd-accent)]"
            >
              <X className="h-4 w-4" />
              Close
            </button>
          </div>
        </header>
        {error ? (
          <div className="mt-6 rounded-2xl border border-rose-500/40 bg-rose-500/10 px-4 py-3 text-sm text-rose-50">
            <strong>TRF snapshot unavailable.</strong> {errorMessage}
          </div>
        ) : isLoading ? (
          <div className="mt-10 flex min-h-[240px] items-center justify-center">
            <Loader2 className="h-10 w-10 animate-spin text-[color:var(--osd-accent)]" />
          </div>
        ) : (
          <div className="mt-6 space-y-6">
            <div className="grid gap-3 sm:grid-cols-3">
              {metrics.map((metric) => (
                <div
                  key={metric.label}
                  className="rounded-2xl border border-[color:var(--osd-border)] bg-[color:var(--osd-surfaceAlt)] p-4"
                >
                  <div className="flex items-center gap-2 text-xs uppercase tracking-[0.3em] text-[color:var(--osd-muted)]">
                    <Activity className="h-3.5 w-3.5" />
                    {metric.label}
                  </div>
                  <p className="mt-2 text-2xl font-semibold text-[color:var(--osd-text)]">{metric.value}</p>
                  <p className="text-xs text-[color:var(--osd-muted)]">{metric.description}</p>
                </div>
              ))}
            </div>
            <div className="grid gap-4 lg:grid-cols-[1.3fr,1fr]">
              <div className="rounded-2xl border border-[color:var(--osd-border)] bg-[color:var(--osd-surfaceAlt)] p-5">
                <div className="flex items-center justify-between">
                  <h4 className="text-lg font-semibold text-[color:var(--osd-text)]">Reasoning Traces</h4>
                  <span className="text-xs uppercase tracking-[0.35em] text-[color:var(--osd-muted)]">
                    {traces.length} entries
                  </span>
                </div>
                <div className="mt-4 space-y-3 max-h-72 overflow-y-auto pr-1">
                  {traces.length === 0 && (
                    <p className="rounded-xl border border-dashed border-[color:var(--osd-border)] px-4 py-6 text-center text-sm text-[color:var(--osd-muted)]">
                      No TRF traces yet. Ledger events will populate this stream.
                    </p>
                  )}
                  {traces.map((trace) => (
                    <article
                      key={trace.trace_id}
                      className="rounded-2xl border border-[color:var(--osd-border)] bg-[color:var(--osd-background)] p-4"
                    >
                      <div className="flex items-center justify-between text-xs text-[color:var(--osd-muted)]">
                        <span className="font-mono uppercase tracking-[0.25em] text-[color:var(--osd-accent)]">
                          {trace.operator}
                        </span>
                        <span>{new Date(trace.created_at).toLocaleString()}</span>
                      </div>
                      <p className="mt-2 text-sm font-semibold text-[color:var(--osd-text)]">
                        {trace.persona} · {trace.compliance_gate}
                      </p>
                      <p className="text-sm text-[color:var(--osd-muted)]">
                        {trace.premise} → {trace.conclusion}
                      </p>
                      <p className="mt-1 text-xs text-[color:var(--osd-muted)]">
                        {trace.evidence} · Confidence {Math.round(trace.confidence * 100)}%
                      </p>
                    </article>
                  ))}
                </div>
              </div>
              <div className="space-y-4">
                <div className="rounded-2xl border border-[color:var(--osd-border)] bg-[color:var(--osd-surfaceAlt)] p-4">
                  <h4 className="text-sm font-semibold text-[color:var(--osd-text)] uppercase tracking-[0.3em]">
                    Persona Load
                  </h4>
                  <div className="mt-3 space-y-3">
                    {personas.length === 0 && (
                      <p className="text-xs text-[color:var(--osd-muted)]">No persona telemetry yet.</p>
                    )}
                    {personas.map((persona) => (
                      <div key={persona.persona} className="rounded-xl border border-[color:var(--osd-border)] p-3">
                        <div className="flex items-center justify-between text-sm text-[color:var(--osd-text)]">
                          <span>
                            {persona.persona} · <span className="text-[color:var(--osd-muted)]">{persona.role}</span>
                          </span>
                          <span className="text-xs uppercase tracking-[0.3em]">{persona.status}</span>
                        </div>
                        <div className="mt-2 flex items-center justify-between text-xs text-[color:var(--osd-muted)]">
                          <span>{persona.context}</span>
                          <span>{persona.utilization}%</span>
                        </div>
                        <div className="mt-1 h-1.5 rounded-full bg-[color:var(--osd-border)]">
                          <div
                            className="h-1.5 rounded-full bg-gradient-to-r from-indigo-500 to-purple-500"
                            style={{ width: `${persona.utilization}%` }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
                <div className="rounded-2xl border border-[color:var(--osd-border)] bg-[color:var(--osd-surfaceAlt)] p-4">
                  <h4 className="text-sm font-semibold text-[color:var(--osd-text)] uppercase tracking-[0.3em]">
                    Heuristics
                  </h4>
                  <div className="mt-3 space-y-2">
                    {heuristics.map((heuristic) => (
                      <div key={heuristic.label} className="flex items-start gap-3 rounded-xl border border-[color:var(--osd-border)] p-3">
                        <div className="rounded-full bg-[color:var(--osd-border)]/50 p-2">
                          <Zap className="h-4 w-4 text-[color:var(--osd-accent)]" />
                        </div>
                        <div>
                          <p className="text-sm font-semibold text-[color:var(--osd-text)]">
                            {heuristic.label}{' '}
                            <span className="text-xs uppercase tracking-[0.3em] text-[color:var(--osd-muted)]">
                              {heuristic.status}
                            </span>
                          </p>
                          <p className="text-xs text-[color:var(--osd-muted)]">{heuristic.detail}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
            {snapshot?.spec_refs?.length && (
              <p className="text-xs text-[color:var(--osd-muted)]">
                Spec references: {snapshot.spec_refs.join(', ')}
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

function ProjectLedgerPanel({
  events,
  integrityOk,
  isLoading,
  isFetching,
  error,
  selectedFilter,
  projectOptions,
  onProjectChange,
  onRefresh,
}: ProjectLedgerPanelProps) {
  const eventCount = events.length
  const latestTimestamp = formatTimestamp(events[0]?.created_at)
  const integrityTone = integrityOk
    ? 'border-emerald-500/30 bg-emerald-500/10 text-emerald-200'
    : 'border-amber-500/30 bg-amber-500/10 text-amber-100'

  const handleSelectChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    onProjectChange(event.target.value || null)
  }

  const errorMessage = error instanceof Error ? error.message : 'Unable to load ledger events.'

  return (
    <div className="rounded-3xl border border-[color:var(--osd-border)] bg-[color:var(--osd-surfaceAlt)] p-6 space-y-5">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.35em] text-[color:var(--osd-muted)]">Spec §3.7 · §6.3 · §8.7</p>
          <h3 className="text-lg font-semibold text-[color:var(--osd-text)] flex items-center gap-2">
            <BookOpen className="h-5 w-5 text-[color:var(--osd-accent)]" />
            Project Ledger
          </h3>
          <p className="text-sm text-[color:var(--osd-muted)] max-w-3xl">
            Hash-chained audit trail shared between Tkinter and React so the desktop + browser surfaces stay aligned.
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <label className="flex items-center gap-2 text-xs uppercase tracking-[0.4em] text-[color:var(--osd-muted)]">
            Scope
            <select
              value={selectedFilter ?? ''}
              onChange={handleSelectChange}
              className="h-10 rounded-xl border border-[color:var(--osd-border)] bg-[color:var(--osd-background)] px-3 text-[color:var(--osd-text)] focus:border-[color:var(--osd-accent)] focus:outline-none"
            >
              <option value="">All Projects</option>
              {projectOptions.map((name) => (
                <option key={name} value={name}>
                  {name}
                </option>
              ))}
            </select>
          </label>
          <button
            type="button"
            onClick={onRefresh}
            disabled={isFetching}
            className="inline-flex items-center gap-2 rounded-full border border-[color:var(--osd-border)] px-4 py-2 text-xs font-semibold text-[color:var(--osd-text)] hover:border-[color:var(--osd-accent)] disabled:opacity-60"
          >
            <RefreshCw className="h-4 w-4" />
            {isFetching ? 'Refreshing…' : 'Refresh Ledger'}
          </button>
        </div>
      </div>
      <div className="grid gap-3 sm:grid-cols-3">
        <div className="rounded-2xl border border-[color:var(--osd-border)] p-3 text-xs text-[color:var(--osd-muted)]">
          <div className="flex items-center gap-2 text-sm text-[color:var(--osd-text)]">
            <Hash className="h-4 w-4" />
            Events tracked
          </div>
          <p className="mt-1 text-2xl font-semibold text-[color:var(--osd-text)]">{eventCount}</p>
        </div>
        <div className="rounded-2xl border border-[color:var(--osd-border)] p-3 text-xs text-[color:var(--osd-muted)]">
          <div className="flex items-center gap-2 text-sm text-[color:var(--osd-text)]">
            <Clock className="h-4 w-4" />
            Latest event
          </div>
          <p className="mt-1 text-sm text-[color:var(--osd-text)]">{latestTimestamp}</p>
        </div>
        <div className={`rounded-2xl border px-3 py-2 text-xs ${integrityTone} flex items-center gap-2`}>
          <Hash className="h-4 w-4" />
          <span className="font-semibold">{integrityOk ? 'Hash chain intact' : 'Hash divergence detected'}</span>
        </div>
      </div>
      {Boolean(error) && (
        <div className="rounded-2xl border border-rose-500/60 bg-rose-500/10 px-4 py-3 text-sm text-rose-100">
          <strong>Ledger unavailable.</strong> {errorMessage}
        </div>
      )}
      {isLoading ? (
        <div className="flex h-48 items-center justify-center">
          <div className="h-10 w-10 animate-spin rounded-full border-b-2 border-[color:var(--osd-accent)]" />
        </div>
      ) : (
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {events.length ? (
            events.slice(0, 12).map((event) => (
              <article
                key={event.id}
                className="rounded-2xl border border-[color:var(--osd-border)] bg-[color:var(--osd-background)] p-4 text-sm text-[color:var(--osd-muted)]"
              >
                <div className="flex items-center justify-between text-[color:var(--osd-text)]">
                  <span className="font-semibold">{event.event_type.replace(/_/g, ' ')}</span>
                  <span className="text-xs text-[color:var(--osd-muted)]">{formatTimestamp(event.created_at)}</span>
                </div>
                <p className="mt-1 text-xs uppercase tracking-[0.4em]">{describeEntity(event)}</p>
                <p className="mt-2 text-sm text-[color:var(--osd-muted)]">{summarizePayload(event.payload)}</p>
                <div className="mt-3 flex items-center justify-between text-[color:var(--osd-muted)] text-xs">
                  <span className="flex items-center gap-1 font-mono">
                    <Hash className="h-3.5 w-3.5" />
                    {event.hash_curr.slice(0, 8)}
                  </span>
                  <span>{event.project_id}</span>
                </div>
              </article>
            ))
          ) : (
            <p className="rounded-2xl border border-dashed border-[color:var(--osd-border)] px-4 py-6 text-center text-sm text-[color:var(--osd-muted)]">
              Ledger events will populate this space as automation runs, approvals complete, or governance hooks fire.
            </p>
          )}
        </div>
      )}
      <div className="flex items-center justify-between text-xs text-[color:var(--osd-muted)]">
        <span>Details live in the canonical spec for governance, capsules, and auditing.</span>
        <a
          className="inline-flex items-center gap-1 text-[color:var(--osd-accent)]"
          href="/docs/projects.html"
          target="_blank"
          rel="noreferrer"
        >
          <ExternalLink className="h-3 w-3" />
          Open doc
        </a>
      </div>
    </div>
  )
}

function ReasoningLabPanel({
  personas,
  personasLoading,
  history,
  historyLoading,
  historyError,
  selectedPersona,
  onSelectPersona,
  queryText,
  onQueryChange,
  onRun,
  isRunning,
  currentTrace,
  onSelectTrace,
  runError,
}: ReasoningLabPanelProps) {
  const traceSteps = currentTrace?.steps ?? []
  return (
    <div className="rounded-3xl border border-[color:var(--osd-border)] bg-[color:var(--osd-surfaceAlt)] p-6 space-y-6">
      <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.35em] text-[color:var(--osd-muted)]">Spec §4.6 · §4.7 · §4.8</p>
          <h3 className="text-lg font-semibold text-[color:var(--osd-text)] flex items-center gap-2">
            <Brain className="h-5 w-5 text-[color:var(--osd-accent)]" />
            TRF Reasoning Lab
          </h3>
          <p className="text-sm text-[color:var(--osd-muted)] max-w-3xl">
            Mirrors the Tkinter reasoning pane — select a persona, run a query, and inspect the structured reasoning trace.
          </p>
        </div>
        <button
          type="button"
          onClick={onRun}
          disabled={isRunning || !queryText.trim()}
          className="inline-flex items-center gap-2 rounded-full border border-[color:var(--osd-border)] px-4 py-2 text-xs font-semibold text-[color:var(--osd-text)] hover:border-[color:var(--osd-accent)] disabled:opacity-60"
        >
          {isRunning ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}
          {isRunning ? 'Reasoning…' : 'Generate Trace'}
        </button>
      </div>

      <div className="grid gap-6 lg:grid-cols-[2fr,1fr]">
        <div className="space-y-4">
          <div>
            <p className="text-xs uppercase tracking-[0.3em] text-[color:var(--osd-muted)]">Persona</p>
            <div className="mt-2 flex flex-wrap gap-2">
              {personas.map((persona) => {
                const isActive = persona.type === selectedPersona
                return (
                  <button
                    key={persona.id}
                    type="button"
                    onClick={() => onSelectPersona(persona.type)}
                    className={`rounded-full border px-3 py-1 text-xs font-semibold transition ${
                      isActive
                        ? 'border-[color:var(--osd-accent)] text-[color:var(--osd-accent)]'
                        : 'border-[color:var(--osd-border)] text-[color:var(--osd-muted)] hover:border-[color:var(--osd-accent)] hover:text-[color:var(--osd-accent)]'
                    }`}
                  >
                    {persona.label}
                  </button>
                )
              })}
              {personasLoading && <span className="text-xs text-[color:var(--osd-muted)]">Loading personas…</span>}
            </div>
          </div>
          <label className="space-y-2 text-sm">
            <span>Reasoning Query</span>
            <textarea
              value={queryText}
              onChange={(event) => onQueryChange(event.target.value)}
              rows={4}
              className="w-full rounded-2xl border border-[color:var(--osd-border)] bg-[color:var(--osd-background)] px-3 py-2 text-sm text-[color:var(--osd-text)]"
              placeholder="Explain how the ledger integrity impacts TRF output…"
            />
          </label>
          {runError && (
            <div className="rounded-2xl border border-rose-500/60 bg-rose-500/10 px-4 py-3 text-xs text-rose-100">
              {runError}
            </div>
          )}
        </div>
        <div className="rounded-2xl border border-[color:var(--osd-border)] bg-[color:var(--osd-background)] p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs uppercase tracking-[0.3em] text-[color:var(--osd-muted)] flex items-center gap-2">
                <History className="h-4 w-4" />
                Recent Traces
              </p>
              <p className="text-xs text-[color:var(--osd-muted)]">Select a trace to review past reasoning.</p>
            </div>
            {historyLoading && <Loader2 className="h-4 w-4 animate-spin text-[color:var(--osd-muted)]" />}
          </div>
          <div className="mt-4 space-y-2">
            {history.map((trace) => {
              const isActive = currentTrace?.id === trace.id
              return (
                <button
                  key={trace.id}
                  type="button"
                  onClick={() => onSelectTrace(trace)}
                  className={`w-full rounded-xl border px-3 py-2 text-left text-xs transition ${
                    isActive
                      ? 'border-[color:var(--osd-accent)] bg-[color:var(--osd-accent)]/10 text-[color:var(--osd-text)]'
                      : 'border-[color:var(--osd-border)] text-[color:var(--osd-muted)] hover:border-[color:var(--osd-accent)] hover:text-[color:var(--osd-accent)]'
                  }`}
                >
                  <p className="font-semibold line-clamp-2">{trace.query}</p>
                  <p className="text-[color:var(--osd-muted)]">{formatTimestamp(trace.created_at)}</p>
                </button>
              )
            })}
            {!history.length && !historyLoading && (
              <p className="text-xs text-[color:var(--osd-muted)]">No reasoning history yet.</p>
            )}
            {historyError && (
              <div className="rounded-xl border border-rose-500/40 bg-rose-500/10 px-3 py-2 text-xs text-rose-100">
                {historyError}
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="rounded-2xl border border-[color:var(--osd-border)] bg-[color:var(--osd-background)] p-5">
        {currentTrace ? (
          <>
            <div className="flex flex-col gap-2 md:flex-row md:items-start md:justify-between">
              <div>
                <p className="text-xs uppercase tracking-[0.3em] text-[color:var(--osd-muted)]">Conclusion</p>
                <h4 className="text-xl font-semibold text-[color:var(--osd-text)]">
                  {currentTrace.final_conclusion || 'Conclusion pending'}
                </h4>
                <p className="text-xs text-[color:var(--osd-muted)]">
                  Confidence {(currentTrace.overall_confidence * 100).toFixed(1)}% ·{' '}
                  {currentTrace.persona_label || currentTrace.persona_id || 'Persona'}
                </p>
              </div>
              <p className="text-xs text-[color:var(--osd-muted)]">
                Generated {formatTimestamp(currentTrace.created_at)}
              </p>
            </div>
            <div className="mt-4 space-y-3">
              {traceSteps.map((step) => (
                <article key={step.id} className="rounded-2xl border border-[color:var(--osd-border)] bg-[color:var(--osd-surfaceAlt)] p-4">
                  <div className="flex items-center justify-between text-xs">
                    <span className="uppercase tracking-[0.3em] text-[color:var(--osd-muted)]">
                      {step.operator.replace(/_/g, ' ')}
                    </span>
                    <span className="text-[color:var(--osd-text)] font-semibold">
                      {(step.confidence * 100).toFixed(0)}%
                    </span>
                  </div>
                  <p className="mt-2 text-sm text-[color:var(--osd-text)]">{step.conclusion}</p>
                  {step.premises.length > 0 && (
                    <p className="mt-1 text-xs text-[color:var(--osd-muted)]">
                      Premises: {step.premises.join(' · ')}
                    </p>
                  )}
                </article>
              ))}
              {!traceSteps.length && (
                <p className="rounded-2xl border border-dashed border-[color:var(--osd-border)] px-4 py-6 text-center text-sm text-[color:var(--osd-muted)]">
                  No reasoning steps recorded for this query.
                </p>
              )}
            </div>
          </>
        ) : (
          <p className="text-sm text-[color:var(--osd-muted)]">
            Run a reasoning query to populate the TRF trace view.
          </p>
        )}
      </div>
    </div>
  )
}

function formatTimestamp(value?: string) {
  if (!value) {
    return 'Timestamp unavailable'
  }
  const parsed = new Date(value)
  if (Number.isNaN(parsed.getTime())) {
    return value
  }
  return parsed.toLocaleString()
}

function summarizePayload(payload: Record<string, unknown>) {
  if (!payload || Object.keys(payload).length === 0) {
    return 'No additional details'
  }
  const priorityKeys = ['message', 'summary', 'note', 'details', 'description', 'title']
  for (const key of priorityKeys) {
    const candidate = payload[key]
    if (typeof candidate === 'string' && candidate.trim()) {
      return candidate
    }
  }
  try {
    return JSON.stringify(payload, null, 2)
  } catch {
    return 'Payload available'
  }
}

function describeEntity(event: ProjectLedgerEvent) {
  const parts = []
  if (event.entity_type) {
    parts.push(event.entity_type)
  }
  if (event.entity_id) {
    parts.push(event.entity_id)
  }
  if (parts.length === 0) {
    return 'System event'
  }
  return parts.join(' · ')
}
