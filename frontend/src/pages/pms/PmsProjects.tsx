import { useMemo, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Filter, Plus, Search } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import PageHeader from '../../components/PageHeader'
import { pmsApi } from '../../api/pms'
import { useActor } from '../../contexts/ActorContext'
import { formatDate } from './pmsUtils'

const templatePacks = [
  { value: 'dev', label: 'Dev Pack' },
  { value: 'research', label: 'Research Pack' },
  { value: 'writing', label: 'Writer Pack' },
  { value: 'finance', label: 'Finance Pack' },
  { value: 'cyber', label: 'Cyber Pack' },
]

export default function PmsProjects() {
  const { currentActor } = useActor()
  const queryClient = useQueryClient()
  const navigate = useNavigate()
  const [search, setSearch] = useState('')
  const [modeFilter, setModeFilter] = useState<'all' | 'personal' | 'enterprise'>('all')
  const [sortBy, setSortBy] = useState<'recent' | 'alpha'>('recent')
  const [showCreate, setShowCreate] = useState(false)
  const [projectName, setProjectName] = useState('')
  const [templatePack, setTemplatePack] = useState('dev')

  const { data: projects = [] } = useQuery({
    queryKey: ['pms-projects', currentActor],
    queryFn: () => pmsApi.listProjects(currentActor),
  })

  const createProject = useMutation({
    mutationFn: () =>
      pmsApi.createProject(currentActor, {
        name: projectName,
        config: { template_pack: templatePack },
      }),
    onSuccess: () => {
      setProjectName('')
      setShowCreate(false)
      queryClient.invalidateQueries({ queryKey: ['pms-projects'] })
    },
  })

  const filteredProjects = useMemo(() => {
    const normalized = search.trim().toLowerCase()
    let items = projects
    if (modeFilter !== 'all') {
      items = items.filter((project) => project.mode === modeFilter)
    }
    if (normalized) {
      items = items.filter((project) => project.name.toLowerCase().includes(normalized))
    }
    if (sortBy === 'alpha') {
      items = [...items].sort((a, b) => a.name.localeCompare(b.name))
    } else {
      items = [...items].sort((a, b) => b.updated_at.localeCompare(a.updated_at))
    }
    return items
  }, [projects, search, modeFilter, sortBy])

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="PMS"
        title="Projects"
        description="Track outcomes across epics, tasks, runs, documents, and cost."
        actions={
          <button
            type="button"
            className="btn btn-primary"
            onClick={() => setShowCreate((prev) => !prev)}
          >
            <Plus className="w-4 h-4" />
            New Project
          </button>
        }
      />

      {showCreate && (
        <div className="glass-card p-4 flex flex-wrap gap-4 items-end">
          <div className="flex-1 min-w-[220px]">
            <label className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Project name</label>
            <input
              className="mt-2 w-full rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2"
              value={projectName}
              onChange={(event) => setProjectName(event.target.value)}
              placeholder="e.g. Q3 Launch Plan"
            />
          </div>
          <div className="min-w-[180px]">
            <label className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Template pack</label>
            <select
              className="mt-2 w-full rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2"
              value={templatePack}
              onChange={(event) => setTemplatePack(event.target.value)}
            >
              {templatePacks.map((pack) => (
                <option key={pack.value} value={pack.value}>
                  {pack.label}
                </option>
              ))}
            </select>
          </div>
          <button
            type="button"
            className="btn btn-primary"
            disabled={!projectName || createProject.isPending}
            onClick={() => createProject.mutate()}
          >
            Create Project
          </button>
        </div>
      )}

      <div className="glass-card p-4 flex flex-wrap gap-3 items-center">
        <div className="flex items-center gap-2 flex-1 min-w-[220px]">
          <Search className="w-4 h-4 text-[color:var(--osd-muted)]" />
          <input
            className="w-full bg-transparent text-sm text-[color:var(--osd-text)] focus:outline-none"
            placeholder="Search projects"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
        </div>
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-[color:var(--osd-muted)]" />
          <select
            className="rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2 text-sm"
            value={modeFilter}
            onChange={(event) => setModeFilter(event.target.value as typeof modeFilter)}
          >
            <option value="all">All modes</option>
            <option value="personal">Personal</option>
            <option value="enterprise">Enterprise</option>
          </select>
          <select
            className="rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2 text-sm"
            value={sortBy}
            onChange={(event) => setSortBy(event.target.value as typeof sortBy)}
          >
            <option value="recent">Most recent</option>
            <option value="alpha">Alphabetical</option>
          </select>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {filteredProjects.map((project) => (
          <div key={project.project_id} className="glass-card p-4 space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-base font-semibold">{project.name}</h3>
              <span className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">
                {project.mode}
              </span>
            </div>
            <div className="text-xs text-[color:var(--osd-muted)]">
              Updated {formatDate(project.updated_at)}
            </div>
            <button
              type="button"
              className="btn btn-secondary w-full"
              onClick={() => navigate(`/pms/projects/${project.project_id}`)}
            >
              Open Project
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}
