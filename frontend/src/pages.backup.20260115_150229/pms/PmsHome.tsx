import { useEffect, useMemo, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { ArrowRight, ListChecks, Play, Plus } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import PageHeader from '@/components/PageHeader'
import { useActor } from '../../contexts/ActorContext'
import { ipmApi } from '../../api/ipm'
import type { PmsTask } from '@/types/pms'
import { formatDate, formatCurrency } from './pmsUtils'

export default function PmsHome() {
  const { currentActor } = useActor()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [selectedProjectId, setSelectedProjectId] = useState<string | null>(null)
  const [showTaskForm, setShowTaskForm] = useState(false)
  const [newTaskTitle, setNewTaskTitle] = useState('')
  const [newTaskProject, setNewTaskProject] = useState('')

  const { data: projects = [], isLoading: loadingProjects } = useQuery({
    queryKey: ['pms-projects', currentActor],
    queryFn: () => ipmApi.listProjects(currentActor),
  })

  useEffect(() => {
    if (!selectedProjectId && projects.length > 0) {
      setSelectedProjectId(projects[0].project_id)
    }
    if (!newTaskProject && projects.length > 0) {
      setNewTaskProject(projects[0].project_id)
    }
  }, [projects, selectedProjectId, newTaskProject])

  const selectedProject = useMemo(
    () => projects.find((project) => project.project_id === selectedProjectId) || null,
    [projects, selectedProjectId],
  )

  const { data: nextTask } = useQuery({
    queryKey: ['pms-next-task', selectedProjectId, currentActor],
    queryFn: () => ipmApi.nextTask(selectedProjectId as string, false, currentActor),
    enabled: !!selectedProjectId,
  })

  const { data: peekTasks = [] } = useQuery({
    queryKey: ['pms-peek-tasks', selectedProjectId, currentActor],
    queryFn: () => ipmApi.peekTasks(selectedProjectId as string, 5, currentActor),
    enabled: !!selectedProjectId,
  })

  const { data: recentRuns = [] } = useQuery({
    queryKey: ['pms-runs', selectedProjectId, currentActor],
    queryFn: () => ipmApi.listRuns({ project_id: selectedProjectId, limit: 5 }, currentActor),
    enabled: !!selectedProjectId,
  })

  const { data: meetings = [] } = useQuery({
    queryKey: ['pms-meetings', selectedProjectId, currentActor],
    queryFn: () => ipmApi.listMeetings(selectedProjectId as string, currentActor),
    enabled: !!selectedProjectId,
  })

  const { data: costRollup } = useQuery({
    queryKey: ['pms-rollup', selectedProjectId, currentActor],
    queryFn: () => ipmApi.costRollup(selectedProjectId as string, currentActor),
    enabled: !!selectedProjectId,
  })

  const { data: projectStats = [] } = useQuery({
    queryKey: ['pms-project-stats', currentActor, projects.map((project) => project.project_id)],
    queryFn: async () => {
      const limited = projects.slice(0, 5)
      const results = await Promise.all(
        limited.map(async (project) => {
          const tasks = await ipmApi.listTasks(project.project_id, currentActor)
          const total = tasks.length
          const done = tasks.filter((task) => task.status === 'DONE').length
          return {
            project,
            total,
            done,
          }
        }),
      )
      return results
    },
    enabled: projects.length > 0,
  })

  const startRun = useMutation({
    mutationFn: (task: PmsTask) =>
      ipmApi.startRun(
        {
          project_id: task.project_id,
          task_id: task.task_id,
          input_params: {},
        },
        currentActor,
      ),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pms-runs'] })
    },
  })

  const createTask = useMutation({
    mutationFn: () =>
      ipmApi.createTask(
        newTaskProject,
        {
          title: newTaskTitle,
          priority: 'P1',
          category: 'General',
          task_type: 'General',
        },
        currentActor,
      ),
    onSuccess: () => {
      setNewTaskTitle('')
      setShowTaskForm(false)
      queryClient.invalidateQueries({ queryKey: ['pms-projects'] })
      if (selectedProjectId) {
        queryClient.invalidateQueries({ queryKey: ['pms-next-task', selectedProjectId] })
        queryClient.invalidateQueries({ queryKey: ['pms-peek-tasks', selectedProjectId] })
      }
    },
  })

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="IPM"
        title="Home"
        description="What’s next across your projects, runs, journals, and finance signals."
        actions={
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              className="btn btn-primary"
              onClick={() => setShowTaskForm((prev) => !prev)}
            >
              <Plus className="w-4 h-4" />
              New Task
            </button>
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => navigate('/ipm/projects')}
            >
              New Project
            </button>
          </div>
        }
      />

      {showTaskForm && (
        <div className="glass-card p-4 flex flex-wrap items-end gap-4">
          <div className="flex-1 min-w-[220px]">
            <label className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Project</label>
            <select
              className="mt-2 w-full rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2"
              value={newTaskProject}
              onChange={(event) => setNewTaskProject(event.target.value)}
            >
              {projects.map((project) => (
                <option key={project.project_id} value={project.project_id}>
                  {project.name}
                </option>
              ))}
            </select>
          </div>
          <div className="flex-[2] min-w-[220px]">
            <label className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Task title</label>
            <input
              className="mt-2 w-full rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2"
              placeholder="Define the deliverable"
              value={newTaskTitle}
              onChange={(event) => setNewTaskTitle(event.target.value)}
            />
          </div>
          <button
            type="button"
            className="btn btn-primary"
            disabled={!newTaskTitle || !newTaskProject || createTask.isPending}
            onClick={() => createTask.mutate()}
          >
            Create Task
          </button>
        </div>
      )}

      <div className="grid gap-4 lg:grid-cols-2">
        <section className="glass-card p-5 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Next Up</p>
              <h2 className="text-lg font-semibold">{selectedProject?.name || 'Select a project'}</h2>
            </div>
            <select
              className="rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2 text-sm"
              value={selectedProjectId || ''}
              onChange={(event) => setSelectedProjectId(event.target.value)}
            >
              {projects.map((project) => (
                <option key={project.project_id} value={project.project_id}>
                  {project.name}
                </option>
              ))}
            </select>
          </div>

          {nextTask ? (
            <div className="rounded-xl border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)]/40 p-4">
              <div className="flex items-center justify-between">
                <div>
                  <div className="flex items-center gap-2 text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">
                    <span>{nextTask.priority}</span>
                    <span>·</span>
                    <span>{nextTask.category}</span>
                    <span>·</span>
                    <span>{nextTask.task_type}</span>
                  </div>
                  <h3 className="mt-2 text-base font-semibold text-[color:var(--osd-text)]">
                    {nextTask.title}
                  </h3>
                  <p className="mt-1 text-xs text-[color:var(--osd-muted)]">
                    Created {formatDate(nextTask.created_at)}
                  </p>
                </div>
                <div className="flex gap-2">
                  <button
                    type="button"
                    className="btn btn-secondary"
                    onClick={() => navigate(`/ipm/projects/${nextTask.project_id}?tab=tasks&focus=${nextTask.task_id}`)}
                  >
                    Open Task
                  </button>
                  <button
                    type="button"
                    className="btn btn-primary"
                    onClick={() => startRun.mutate(nextTask)}
                  >
                    <Play className="w-4 h-4" />
                    Start Run
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <div className="rounded-xl border border-dashed border-[color:var(--osd-border)] p-4 text-sm text-[color:var(--osd-muted)]">
              {selectedProjectId ? 'No queued tasks found.' : 'Pick a project to see next tasks.'}
            </div>
          )}

          <div className="space-y-3">
            {peekTasks.map((task: PmsTask) => (
              <div key={task.task_id} className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-2">
                  <span className="text-xs px-2 py-1 rounded-full border border-[color:var(--osd-border)]">
                    {task.priority}
                  </span>
                  <span>{task.title}</span>
                </div>
                <button
                  type="button"
                  className="text-xs text-[color:var(--osd-muted)] hover:text-[color:var(--osd-text)]"
                  onClick={() => navigate(`/ipm/projects/${task.project_id}?tab=tasks&focus=${task.task_id}`)}
                >
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        </section>

        <section className="glass-card p-5 space-y-4">
          <div className="flex items-center gap-2">
            <ListChecks className="w-4 h-4 text-[color:var(--osd-muted)]" />
            <h2 className="text-sm font-semibold text-[color:var(--osd-text)]">My Active Projects</h2>
          </div>
          {loadingProjects ? (
            <p className="text-sm text-[color:var(--osd-muted)]">Loading projects...</p>
          ) : (
            <div className="space-y-3">
              {projectStats.map(({ project, total, done }) => {
                const progress = total === 0 ? 0 : Math.round((done / total) * 100)
                return (
                  <div key={project.project_id} className="rounded-xl border border-[color:var(--osd-border)] p-3">
                    <div className="flex items-center justify-between text-sm">
                      <span className="font-medium">{project.name}</span>
                      <span className="text-xs text-[color:var(--osd-muted)]">{progress}%</span>
                    </div>
                    <div className="mt-2 h-2 rounded-full bg-[color:var(--osd-border)]">
                      <div
                        className="h-full rounded-full bg-[color:var(--osd-accent)]"
                        style={{ width: `${progress}%` }}
                      />
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </section>
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <section className="glass-card p-5 lg:col-span-2">
          <h2 className="text-sm font-semibold text-[color:var(--osd-text)] mb-3">Recent Runs</h2>
          <div className="space-y-2 text-sm">
            {recentRuns.map((run) => (
              <div key={run.run_id} className="flex items-center justify-between">
                <span className="font-medium">{run.status}</span>
                <span className="text-xs text-[color:var(--osd-muted)]">{formatDate(run.started_at)}</span>
              </div>
            ))}
          </div>
        </section>

        <section className="glass-card p-5 space-y-3">
          <h2 className="text-sm font-semibold text-[color:var(--osd-text)]">Cost Snapshot</h2>
          <div className="text-xs text-[color:var(--osd-muted)]">This month</div>
          <div className="text-lg font-semibold">
            {formatCurrency(costRollup?.combined_total ?? costRollup?.total ?? 0)}
          </div>
          <div className="text-xs text-[color:var(--osd-muted)]">
            Labor {formatCurrency(costRollup?.labor_total ?? 0)} · Expenses {formatCurrency(costRollup?.expense_total ?? 0)}
          </div>
        </section>
      </div>

      <section className="glass-card p-5">
        <h2 className="text-sm font-semibold text-[color:var(--osd-text)] mb-3">Recent Meetings / Journals</h2>
        <div className="space-y-2 text-sm">
          {meetings.slice(0, 6).map((meeting) => (
            <div key={meeting.meeting_id} className="flex items-center justify-between">
              <span>{meeting.title}</span>
              <button
                type="button"
                className="text-xs text-[color:var(--osd-muted)] hover:text-[color:var(--osd-text)]"
                onClick={() => navigate(`/ipm/journal?meeting=${meeting.meeting_id}`)}
              >
                Open Journal
              </button>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}
