import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { type ChangeEvent, useMemo, useState } from 'react'
import { FileText, Layers, ListChecks, Plus, Trash2, Save, X, Play, Sparkles, Search } from 'lucide-react'
import apiClient, { apiPath } from '../lib/apiClient'
import { toast } from '../utils/toast'

interface TaskTemplate {
  id: string
  name: string
  title: string
  project: string
  priority: string
  notes: string
  time_estimated: number | null
  created_at: string
}

interface TemplateSampleFile {
  extension: string
  filename: string
  description: string
}

interface DocumentTemplateProfile {
  name: string
  purpose: string
  governance: string[]
  toolchain_alignment: string[]
  daemon_support: string[]
  sample_files: TemplateSampleFile[]
}

interface DocumentPlaceholderEntry {
  id: string
  name: string
  category: string
  placeholder_count: number
  placeholders: string[]
  preview: string
}

interface DocumentTemplatesSnapshot {
  catalog: DocumentTemplateProfile[]
  placeholder_matrix: DocumentPlaceholderEntry[]
}

const fetchTemplates = async (): Promise<TaskTemplate[]> => {
  const { data } = await apiClient.get<{ templates: TaskTemplate[] }>(apiPath('templates'))
  return data.templates
}

const fetchDocumentTemplates = async (): Promise<DocumentTemplatesSnapshot> => {
  const { data } = await apiClient.get<DocumentTemplatesSnapshot>(apiPath('templates/documents'))
  return data
}

export default function Templates() {
  const queryClient = useQueryClient()
  const [selectedTemplate, setSelectedTemplate] = useState<TaskTemplate | null>(null)
  const [isEditing, setIsEditing] = useState(false)
  const [search, setSearch] = useState('')
  const [docCategoryFilter, setDocCategoryFilter] = useState('all')
  const [formData, setFormData] = useState<Partial<TaskTemplate>>({
    name: '',
    title: '',
    project: 'General',
    priority: 'MEDIUM',
    notes: '',
    time_estimated: null,
  })

  const { data: templates, isLoading } = useQuery({
    queryKey: ['templates'],
    queryFn: fetchTemplates,
  })

  const { data: documentSnapshot, isLoading: isDocLoading } = useQuery({
    queryKey: ['document-templates'],
    queryFn: fetchDocumentTemplates,
  })

  const createMutation = useMutation({
    mutationFn: async (template: Partial<TaskTemplate>) => {
      const { data } = await apiClient.post(apiPath('templates'), template)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['templates'] })
      toast.success('Template saved successfully')
      resetForm()
    },
    onError: (error) => {
      toast.error(`Failed to save template: ${error instanceof Error ? error.message : 'Unknown error'}`)
    },
  })

  const updateMutation = useMutation({
    mutationFn: async ({ id, ...template }: TaskTemplate) => {
      const { data } = await apiClient.put(apiPath(`templates/${id}`), template)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['templates'] })
      toast.success('Template updated successfully')
      resetForm()
    },
    onError: (error) => {
      toast.error(`Failed to update template: ${error instanceof Error ? error.message : 'Unknown error'}`)
    },
  })

  const deleteMutation = useMutation({
    mutationFn: async (id: string) => {
      const { data } = await apiClient.delete(apiPath(`templates/${id}`))
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['templates'] })
      toast.success('Template deleted successfully')
      if (selectedTemplate) {
        setSelectedTemplate(null)
        resetForm()
      }
    },
    onError: (error) => {
      toast.error(`Failed to delete template: ${error instanceof Error ? error.message : 'Unknown error'}`)
    },
  })

  const createTaskMutation = useMutation({
    mutationFn: async (templateId: string) => {
      const { data } = await apiClient.post(apiPath('templates/create-task'), {
        template_id: templateId,
        owner: 'User',
      })
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
      toast.success('Task created from template')
    },
    onError: (error) => {
      toast.error(`Failed to create task: ${error instanceof Error ? error.message : 'Unknown error'}`)
    },
  })

  const resetForm = () => {
    setFormData({
      name: '',
      title: '',
      project: 'General',
      priority: 'MEDIUM',
      notes: '',
      time_estimated: null,
    })
    setSelectedTemplate(null)
    setIsEditing(false)
  }

  const handleSelectTemplate = (template: TaskTemplate) => {
    setSelectedTemplate(template)
    setFormData({
      name: template.name,
      title: template.title,
      project: template.project,
      priority: template.priority,
      notes: template.notes,
      time_estimated: template.time_estimated,
    })
    setIsEditing(false)
  }

  const handleNewTemplate = () => {
    resetForm()
    setIsEditing(true)
  }

  const handleSave = () => {
    if (!formData.name?.trim()) {
      toast.error('Template name is required')
      return
    }

    if (selectedTemplate) {
      updateMutation.mutate({ ...selectedTemplate, ...formData } as TaskTemplate)
    } else {
      createMutation.mutate(formData)
    }
  }

  const handleDelete = (id: string) => {
    if (confirm('Are you sure you want to delete this template?')) {
      deleteMutation.mutate(id)
    }
  }

  const handleCreateTask = (templateId: string) => {
    createTaskMutation.mutate(templateId)
  }

  const templateStats = useMemo(() => {
    const total = templates?.length ?? 0
    const urgent = templates ? templates.filter((template) => template.priority === 'URGENT').length : 0
    const sla =
      templates && templates.length > 0
        ? Math.round(
            templates.reduce((sum, template) => sum + (template.time_estimated || 0), 0) /
              templates.length,
          )
        : 0
    const projects = templates ? new Set(templates.map((template) => template.project)).size : 0
    return { total, urgent, sla, projects }
  }, [templates])

  const filteredTemplates = useMemo(() => {
    const list = templates || []
    const trimmed = search.trim().toLowerCase()
    if (!trimmed) return list
    return list.filter((template) =>
      [template.name, template.title, template.project, template.priority]
        .filter(Boolean)
        .some((value) => value!.toLowerCase().includes(trimmed)),
    )
  }, [templates, search])

  const documentCatalog = documentSnapshot?.catalog ?? []
  const placeholderMatrix = documentSnapshot?.placeholder_matrix ?? []

  const documentCategories = useMemo(() => {
    const set = new Set<string>(['all'])
    documentCatalog.forEach((profile) => set.add(profile.name))
    return Array.from(set)
  }, [documentCatalog])

  const filteredDocumentCatalog = useMemo(() => {
    if (docCategoryFilter === 'all') {
      return documentCatalog
    }
    return documentCatalog.filter((profile) => profile.name === docCategoryFilter)
  }, [documentCatalog, docCategoryFilter])

  const formatCategoryLabel = (label: string) =>
    label
      .replace(/_/g, ' ')
      .replace(/\b\w/g, (char) => char.toUpperCase())

  if (isLoading) {
    return (
      <div className="px-4 py-6 sm:px-0">
        <div className="glass-card flex h-72 items-center justify-center text-slate-300">
          <div className="h-12 w-12 animate-spin rounded-full border-2 border-white/30 border-t-white" />
        </div>
      </div>
    )
  }

  return (
    <div className="px-4 py-6 sm:px-0 space-y-8 text-slate-100">
      <section className="glass-card relative overflow-hidden">
        <div className="pointer-events-none absolute inset-0 bg-gradient-to-br from-indigo-500/20 via-transparent to-purple-500/10" />
        <div className="relative flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <p className="eyebrow-text">Workflows</p>
            <h1 className="mt-2 text-3xl font-semibold text-white">Task Template Library</h1>
            <p className="mt-3 text-sm text-slate-300 max-w-2xl">
              Shared between the web browser, Electron shell, and legacy Tkinter tabs via the same FastAPI
              routes. Build once, reuse everywhere.
            </p>
          </div>
          <button
            onClick={handleNewTemplate}
            className="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-blue-500 to-indigo-500 px-5 py-3 text-sm font-semibold shadow-lg shadow-blue-500/20"
          >
            <Sparkles className="h-4 w-4" />
            New Template
          </button>
        </div>
        <div className="relative mt-6 grid gap-4 text-center text-sm sm:grid-cols-2 lg:grid-cols-4">
          <SummaryStat label="Templates" value={templateStats.total} sublabel="Ready to deploy" />
          <SummaryStat label="Urgent" value={templateStats.urgent} sublabel="High-impact playbooks" />
          <SummaryStat
            label="Avg Duration"
            value={templateStats.sla > 0 ? `${templateStats.sla}m` : '—'}
            sublabel="Time estimate"
          />
          <SummaryStat label="Projects" value={templateStats.projects} sublabel="Teams using templates" />
        </div>
      </section>

      <div className="grid gap-6 lg:grid-cols-[320px,minmax(0,1fr)]">
        <div className="space-y-6">
          <section className="glass-card space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="eyebrow-text">Template Library</p>
                <h3 className="text-lg font-semibold text-white">Reusable routines</h3>
              </div>
              <button className="btn-tonal text-xs" onClick={handleNewTemplate}>
                <Plus className="h-4 w-4" />
                New
              </button>
            </div>
            <div className="relative">
              <Search className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
              <input
                type="search"
                value={search}
                onChange={(event) => setSearch(event.target.value)}
                placeholder="Filter by name, project, or priority..."
                className="w-full rounded-2xl border border-white/10 bg-white/5 py-2.5 pl-11 pr-4 text-sm text-white placeholder:text-slate-400 focus:border-primary-500 focus:outline-none"
              />
            </div>
            <div className="max-h-[580px] space-y-3 overflow-y-auto pr-1">
              {filteredTemplates.length > 0 ? (
                filteredTemplates.map((template) => (
                  <button
                    key={template.id}
                    onClick={() => handleSelectTemplate(template)}
                    className={`w-full rounded-2xl border p-4 text-left transition ${
                      selectedTemplate?.id === template.id
                        ? 'border-white/40 bg-white/5 shadow-lg shadow-blue-500/10'
                        : 'border-white/5 bg-transparent hover:border-white/20 hover:bg-white/5'
                    }`}
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <p className="text-base font-semibold text-white">{template.name}</p>
                        <p className="text-sm text-slate-300">{template.title}</p>
                        <div className="mt-3 flex flex-wrap gap-2 text-xs font-semibold uppercase tracking-wider">
                          <span className="rounded-full border border-white/10 bg-white/5 px-2 py-1 text-slate-200">
                            {template.project}
                          </span>
                          <span className="rounded-full border border-white/10 bg-white/5 px-2 py-1 text-slate-200">
                            {template.priority}
                          </span>
                          {template.time_estimated ? (
                            <span className="rounded-full border border-white/10 bg-white/5 px-2 py-1 text-slate-200">
                              ~{template.time_estimated}m
                            </span>
                          ) : null}
                        </div>
                      </div>
                      <button
                        className="btn-tonal p-2 text-xs text-red-300"
                        onClick={(event) => {
                          event.stopPropagation()
                          handleDelete(template.id)
                        }}
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </button>
                ))
              ) : (
                <div className="rounded-2xl border border-white/10 bg-white/5 p-6 text-center text-sm text-slate-300">
                  <FileText className="mb-3 h-10 w-10 opacity-60 mx-auto" />
                  No templates match “{search || '—'}”.
                </div>
              )}
            </div>
          </section>

          <section className="glass-card text-sm text-slate-300">
            Templates live in `assistant_hub.tasks_workspace` so Tkinter, FastAPI, and React reference the
            exact same SQLite rows. Any edits you make here instantly flow to the desktop Electron build
            and the preserved Tkinter tab for parity.
          </section>
        </div>

        <section className="glass-card">
          {selectedTemplate || isEditing ? (
            <>
              <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
                <div>
                  <p className="eyebrow-text">{selectedTemplate ? 'Edit Template' : 'New Template'}</p>
                  <h3 className="text-2xl font-semibold text-white">
                    {selectedTemplate?.name || formData.name || 'Untitled'}
                  </h3>
                </div>
                <div className="flex flex-wrap gap-3">
                  {selectedTemplate && (
                    <button
                      onClick={() => handleCreateTask(selectedTemplate.id)}
                      disabled={createTaskMutation.isPending}
                      className="btn-tonal"
                    >
                      <Play className="h-4 w-4" />
                      Create Task
                    </button>
                  )}
                  <button className="btn-tonal" onClick={resetForm}>
                    <X className="h-4 w-4" />
                    Cancel
                  </button>
                  <button
                    onClick={handleSave}
                    disabled={createMutation.isPending || updateMutation.isPending}
                    className="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-blue-500 to-indigo-500 px-5 py-2 text-sm font-semibold shadow-lg shadow-blue-500/20 disabled:opacity-60"
                  >
                    <Save className="h-4 w-4" />
                    Save
                  </button>
                </div>
              </div>
              <div className="mt-6 space-y-5">
                <Field
                  label="Template Name *"
                  value={formData.name || ''}
                  onChange={(value) => setFormData({ ...formData, name: value })}
                  placeholder="e.g., Daily Standup"
                />
                <Field
                  label="Task Title"
                  value={formData.title || ''}
                  onChange={(value) => setFormData({ ...formData, title: value })}
                  placeholder="Review and update project status"
                />
                <div className="grid gap-4 md:grid-cols-2">
                  <Field
                    label="Project"
                    value={formData.project || ''}
                    onChange={(value) => setFormData({ ...formData, project: value })}
                    placeholder="General"
                  />
                  <div>
                    <label className="text-sm text-slate-200">Priority</label>
                    <select
                      value={formData.priority || 'MEDIUM'}
                      onChange={(event) => setFormData({ ...formData, priority: event.target.value })}
                      className="mt-2 w-full rounded-2xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white focus:border-primary-500 focus:outline-none"
                    >
                      <option value="LOW">Low</option>
                      <option value="MEDIUM">Medium</option>
                      <option value="HIGH">High</option>
                      <option value="URGENT">Urgent</option>
                    </select>
                  </div>
                </div>
                <Field
                  label="Time Estimated (minutes)"
                  type="number"
                  value={formData.time_estimated?.toString() || ''}
                  onChange={(value) =>
                    setFormData({
                      ...formData,
                      time_estimated: value ? parseInt(value, 10) : null,
                    })
                  }
                  placeholder="30"
                />
                <Field
                  label="Notes"
                  as="textarea"
                  rows={6}
                  value={formData.notes || ''}
                  onChange={(value) => setFormData({ ...formData, notes: value })}
                  placeholder="Additional notes or instructions..."
                />
              </div>
            </>
          ) : (
            <div className="flex h-full flex-col items-center justify-center gap-4 text-center text-slate-300">
              <div className="rounded-3xl border border-dashed border-white/20 p-8">
                <FileText className="h-14 w-14 text-white" />
              </div>
              <div>
                <h3 className="text-xl font-semibold text-white">Select a template to begin</h3>
                <p className="text-sm">
                  Templates sync between Tkinter and React, so edits are instantly reflected across every surface.
                </p>
              </div>
              <button
                onClick={handleNewTemplate}
                className="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-blue-500 to-indigo-500 px-5 py-3 text-sm font-semibold shadow-lg shadow-blue-500/20"
              >
                <Plus className="h-4 w-4" />
                Create New Template
              </button>
            </div>
          )}
        </section>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <section className="glass-card space-y-5">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <p className="eyebrow-text">Document Templates</p>
              <h3 className="text-2xl font-semibold text-white">Governed catalog</h3>
              <p className="text-sm text-slate-300">
                These profiles mirror the Tkinter catalog and power both the desktop executable and browser
                build. Pick a capsule to explore governance, toolchain alignment, and sample files.
              </p>
            </div>
            <div className="flex flex-col gap-2 text-sm text-white">
              <label htmlFor="doc-category" className="text-xs uppercase tracking-[0.35em] text-slate-400">
                Category
              </label>
              <select
                id="doc-category"
                value={docCategoryFilter}
                onChange={(event) => setDocCategoryFilter(event.target.value)}
                className="rounded-2xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white focus:border-primary-500 focus:outline-none"
              >
                {documentCategories.map((category) => (
                  <option key={category} value={category}>
                    {category === 'all' ? 'All' : formatCategoryLabel(category)}
                  </option>
                ))}
              </select>
            </div>
          </div>
          {isDocLoading ? (
            <div className="flex h-64 items-center justify-center text-slate-300">
              <div className="h-10 w-10 animate-spin rounded-full border-2 border-white/30 border-t-white" />
            </div>
          ) : (
            <div className="grid gap-4 md:grid-cols-2">
              {filteredDocumentCatalog.map((profile) => (
                <article
                  key={profile.name}
                  className="rounded-3xl border border-white/10 bg-gradient-to-br from-indigo-500/10 via-purple-500/10 to-pink-500/10 p-5 text-white shadow-lg shadow-indigo-500/20"
                >
                  <div className="flex items-center gap-3">
                    <div className="rounded-2xl bg-white/10 p-2">
                      <Layers className="h-5 w-5" />
                    </div>
                    <div>
                      <p className="text-sm uppercase tracking-[0.35em] text-slate-200/80">
                        {formatCategoryLabel(profile.name)}
                      </p>
                      <p className="text-xs text-slate-200/70">Samples: {profile.sample_files.length}</p>
                    </div>
                  </div>
                  <p className="mt-3 text-sm text-slate-100/90">{profile.purpose}</p>
                  <div className="mt-4 space-y-2 text-xs text-slate-200/80">
                    <p>
                      <span className="font-semibold text-white">Governance:</span> {profile.governance[0]}
                    </p>
                    <p>
                      <span className="font-semibold text-white">Toolchain:</span> {profile.toolchain_alignment[0]}
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {profile.sample_files.slice(0, 3).map((sample) => (
                        <span
                          key={`${profile.name}-${sample.extension}`}
                          className="rounded-full border border-white/20 px-2 py-1 text-[0.7rem]"
                        >
                          .{sample.extension}
                        </span>
                      ))}
                      {profile.sample_files.length > 3 ? (
                        <span className="rounded-full border border-white/20 px-2 py-1 text-[0.7rem]">
                          +{profile.sample_files.length - 3} more
                        </span>
                      ) : null}
                    </div>
                  </div>
                </article>
              ))}
              {filteredDocumentCatalog.length === 0 && (
                <div className="col-span-2 rounded-2xl border border-dashed border-white/20 p-6 text-center text-slate-300">
                  Nothing in this category yet.
                </div>
              )}
            </div>
          )}
        </section>

        <section className="glass-card space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="eyebrow-text">Placeholder Matrix</p>
              <h3 className="text-xl font-semibold text-white">Token map for governed docs</h3>
              <p className="text-sm text-slate-300">
                React + Tk both reference this matrix to ensure placeholder coverage remains identical.
              </p>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/5 px-3 py-2 text-center text-sm text-white">
              <p className="text-xs uppercase tracking-[0.35em] text-slate-300">Tokens</p>
              <p className="text-lg font-semibold">
                {placeholderMatrix.reduce((sum, entry) => sum + entry.placeholder_count, 0)}
              </p>
            </div>
          </div>
          <div className="max-h-[360px] space-y-3 overflow-y-auto pr-1">
            {placeholderMatrix.map((entry) => {
              const visible = entry.placeholders.slice(0, 8)
              const hidden = entry.placeholder_count - visible.length
              return (
                <div
                  key={entry.id}
                  className="rounded-2xl border border-white/10 bg-gradient-to-r from-slate-900/40 via-indigo-900/30 to-purple-900/30 p-4 text-white"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="text-base font-semibold">{entry.name}</p>
                      <p className="text-xs text-slate-300">{formatCategoryLabel(entry.category)}</p>
                    </div>
                    <div className="flex items-center gap-1 text-xs text-slate-200">
                      <ListChecks className="h-4 w-4" />
                      {entry.placeholder_count} tokens
                    </div>
                  </div>
                  <p className="mt-2 text-xs text-slate-200/80">
                    {entry.preview.length > 160 ? `${entry.preview.slice(0, 160)}…` : entry.preview}
                  </p>
                  <div className="mt-3 flex flex-wrap gap-2 text-[0.65rem] uppercase tracking-wide text-slate-100/80">
                    {visible.map((token) => (
                      <span key={`${entry.id}-${token}`} className="rounded-full border border-white/20 px-2 py-1">
                        {token}
                      </span>
                    ))}
                    {hidden > 0 && (
                      <span className="rounded-full border border-white/20 px-2 py-1">+{hidden} more</span>
                    )}
                  </div>
                </div>
              )
            })}
            {placeholderMatrix.length === 0 && !isDocLoading && (
              <div className="rounded-2xl border border-dashed border-white/20 p-6 text-center text-slate-300">
                Placeholder catalog will appear once the backend snapshot is ready.
              </div>
            )}
          </div>
        </section>
      </div>
    </div>
  )
}

function SummaryStat({ label, value, sublabel }: { label: string; value: number | string; sublabel: string }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white">
      <p className="text-xs uppercase tracking-[0.3em] text-slate-400">{label}</p>
      <p className="mt-2 text-2xl font-semibold">{value}</p>
      <p className="text-xs text-slate-300">{sublabel}</p>
    </div>
  )
}

interface FieldProps {
  label: string
  value: string
  onChange: (value: string) => void
  placeholder?: string
  type?: string
  as?: 'input' | 'textarea'
  rows?: number
}

function Field({
  label,
  value,
  onChange,
  placeholder,
  type = 'text',
  as = 'input',
  rows = 4,
}: FieldProps) {
  const InputComponent = as === 'textarea' ? 'textarea' : 'input'
  return (
    <label className="block text-sm text-slate-200">
      {label}
      <InputComponent
        value={value}
        placeholder={placeholder}
        rows={as === 'textarea' ? rows : undefined}
        type={as === 'textarea' ? undefined : type}
        onChange={(event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) =>
          onChange(event.target.value)
        }
        className="mt-2 w-full rounded-2xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white placeholder:text-slate-400 focus:border-primary-500 focus:outline-none"
      />
    </label>
  )
}
