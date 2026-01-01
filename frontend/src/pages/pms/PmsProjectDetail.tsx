import { useEffect, useMemo, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Plus, Settings, Shield } from 'lucide-react'
import { useNavigate, useParams, useSearchParams } from 'react-router-dom'
import PageHeader from '@/components/PageHeader'
import { pmsApi } from '../../api/pms'
import { useActor } from '../../contexts/ActorContext'
import type { PmsTask, PmsTodo } from '@/types/pms'
import { formatCurrency, formatDate, formatDateTime, shortId } from './pmsUtils'

const tabs = [
  { id: 'overview', label: 'Overview' },
  { id: 'epics', label: 'Epics' },
  { id: 'tasks', label: 'Tasks' },
  { id: 'schedule', label: 'Schedule' },
  { id: 'runs', label: 'Runs & Artifacts' },
  { id: 'documents', label: 'Documents' },
  { id: 'journal', label: 'Journal' },
  { id: 'finance', label: 'Finance' },
  { id: 'audit', label: 'Audit' },
  { id: 'settings', label: 'Settings' },
]

export default function PmsProjectDetail() {
  const { projectId } = useParams<{ projectId: string }>()
  const { currentActor } = useActor()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [searchParams, setSearchParams] = useSearchParams()
  const activeTab = searchParams.get('tab') ?? 'overview'
  const focusTaskId = searchParams.get('focus')

  const [selectedEpicId, setSelectedEpicId] = useState<string | null>(null)
  const [selectedTaskId, setSelectedTaskId] = useState<string | null>(null)
  const [newEpicTitle, setNewEpicTitle] = useState('')
  const [newTaskTitle, setNewTaskTitle] = useState('')
  const [newTodoText, setNewTodoText] = useState('')

  const { data: project } = useQuery({
    queryKey: ['pms-project', projectId, currentActor],
    queryFn: () => pmsApi.getProject(projectId as string, currentActor),
    enabled: !!projectId,
  })

  const { data: epics = [] } = useQuery({
    queryKey: ['pms-epics', projectId, currentActor],
    queryFn: () => pmsApi.listEpics(projectId as string, currentActor),
    enabled: !!projectId,
  })

  const { data: tasks = [] } = useQuery({
    queryKey: ['pms-tasks', projectId, currentActor],
    queryFn: () => pmsApi.listTasks(projectId as string, currentActor),
    enabled: !!projectId,
  })

  const { data: runs = [] } = useQuery({
    queryKey: ['pms-runs', projectId, currentActor],
    queryFn: () => pmsApi.listRuns({ project_id: projectId }, currentActor),
    enabled: activeTab === 'runs' && !!projectId,
  })

  const { data: documents = [] } = useQuery({
    queryKey: ['pms-documents', projectId, currentActor],
    queryFn: () => pmsApi.listDocuments(projectId, currentActor),
    enabled: activeTab === 'documents' && !!projectId,
  })

  const { data: meetings = [] } = useQuery({
    queryKey: ['pms-meetings', projectId, currentActor],
    queryFn: () => pmsApi.listMeetings(projectId, currentActor),
    enabled: activeTab === 'journal' && !!projectId,
  })

  const { data: expenses = [] } = useQuery({
    queryKey: ['pms-expenses', projectId, currentActor],
    queryFn: () => pmsApi.listExpenses(projectId, currentActor),
    enabled: activeTab === 'finance' && !!projectId,
  })

  const { data: timeEntries = [] } = useQuery({
    queryKey: ['pms-time-entries', projectId, currentActor],
    queryFn: () => pmsApi.listTimeEntries(projectId, currentActor),
    enabled: activeTab === 'finance' && !!projectId,
  })

  const { data: costRollup } = useQuery({
    queryKey: ['pms-rollup', projectId, currentActor],
    queryFn: () => pmsApi.costRollup(projectId as string, currentActor),
    enabled: !!projectId,
  })

  const { data: auditEvents = [] } = useQuery({
    queryKey: ['pms-audit', projectId, currentActor],
    queryFn: () => pmsApi.listAuditEvents(projectId, currentActor),
    enabled: activeTab === 'audit' && !!projectId,
  })

  const { data: schedulerIndex } = useQuery({
    queryKey: ['pms-scheduler-index', projectId, currentActor],
    queryFn: () => pmsApi.getSchedulerIndex(projectId as string, currentActor),
    enabled: activeTab === 'schedule' && !!projectId,
  })

  const { data: nextTask } = useQuery({
    queryKey: ['pms-next-task', projectId, currentActor],
    queryFn: () => pmsApi.nextTask(projectId as string, false, currentActor),
    enabled: activeTab === 'schedule' && !!projectId,
  })

  useEffect(() => {
    if (focusTaskId) {
      setSelectedTaskId(focusTaskId)
    }
  }, [focusTaskId])

  const selectedEpic = useMemo(
    () => epics.find((epic) => epic.epic_id === selectedEpicId) || null,
    [epics, selectedEpicId],
  )

  const selectedTask = useMemo(
    () => tasks.find((task) => task.task_id === selectedTaskId) || null,
    [tasks, selectedTaskId],
  )

  const createEpic = useMutation({
    mutationFn: () =>
      pmsApi.createEpic(
        projectId as string,
        {
          title: newEpicTitle,
          description: '',
          acceptance_criteria: '',
          status: 'PLANNED',
        },
        currentActor,
      ),
    onSuccess: () => {
      setNewEpicTitle('')
      queryClient.invalidateQueries({ queryKey: ['pms-epics', projectId] })
    },
  })

  const createTask = useMutation({
    mutationFn: () =>
      pmsApi.createTask(
        projectId as string,
        {
          title: newTaskTitle,
          epic_id: selectedEpicId,
          priority: 'P1',
          category: 'General',
          task_type: 'General',
          status: 'TODO',
        },
        currentActor,
      ),
    onSuccess: () => {
      setNewTaskTitle('')
      queryClient.invalidateQueries({ queryKey: ['pms-tasks', projectId] })
    },
  })

  const updateTask = useMutation({
    mutationFn: (payload: Partial<PmsTask>) =>
      pmsApi.updateTask(projectId as string, selectedTaskId as string, payload, currentActor),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['pms-tasks', projectId] }),
  })

  const addTodo = useMutation({
    mutationFn: () =>
      pmsApi.addTodo(projectId as string, selectedTaskId as string, { text: newTodoText }, currentActor),
    onSuccess: () => {
      setNewTodoText('')
      queryClient.invalidateQueries({ queryKey: ['pms-tasks', projectId] })
    },
  })

  const completeTodo = useMutation({
    mutationFn: (todoId: string) =>
      pmsApi.completeTodo(projectId as string, selectedTaskId as string, todoId, currentActor),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['pms-tasks', projectId] }),
  })

  if (!projectId) {
    return null
  }

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="PMS"
        title={project?.name || 'Project'}
        description="Project overview across epics, tasks, runs, documents, finance, and audit."
        actions={
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => navigate(`/pms/projects/${projectId}?tab=settings`)}
            >
              <Settings className="w-4 h-4" />
              Settings
            </button>
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => setSearchParams({ tab: 'epics' })}
            >
              <Plus className="w-4 h-4" />
              New Epic
            </button>
            <a
              className="btn btn-secondary"
              href={pmsApi.evidencePackUrl(projectId, currentActor)}
              target="_blank"
              rel="noreferrer"
            >
              Export Evidence
            </a>
            <button type="button" className="btn btn-primary" onClick={() => setSearchParams({ tab: 'tasks' })}>
              <Plus className="w-4 h-4" />
              New Task
            </button>
          </div>
        }
      />

      <div className="flex flex-wrap gap-2">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            type="button"
            className={`px-4 py-2 rounded-full text-sm border transition-colors ${
              activeTab === tab.id
                ? 'border-[color:var(--osd-accent)] bg-[color:var(--osd-accentSoft)] text-[color:var(--osd-text)]'
                : 'border-[color:var(--osd-border)] text-[color:var(--osd-muted)] hover:text-[color:var(--osd-text)]'
            }`}
            onClick={() => setSearchParams({ tab: tab.id })}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {activeTab === 'overview' && (
        <div className="space-y-4">
          <div className="grid gap-4 md:grid-cols-3">
            <div className="glass-card p-4">
              <p className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Open tasks</p>
              <p className="text-2xl font-semibold">
                {tasks.filter((task) => task.status !== 'DONE').length}
              </p>
            </div>
            <div className="glass-card p-4">
              <p className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Active epics</p>
              <p className="text-2xl font-semibold">
                {epics.filter((epic) => epic.status !== 'DONE').length}
              </p>
            </div>
            <div className="glass-card p-4">
              <p className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Total spend</p>
              <p className="text-2xl font-semibold">
                {formatCurrency(costRollup?.combined_total ?? costRollup?.total ?? 0)}
              </p>
            </div>
          </div>

          <div className="glass-card p-5">
            <h3 className="text-sm font-semibold text-[color:var(--osd-text)] mb-3">Recent Activity</h3>
            <div className="space-y-2 text-sm">
              {auditEvents.slice(0, 6).map((event) => (
                <div key={event.event_id} className="flex items-center justify-between">
                  <span>{event.action}</span>
                  <span className="text-xs text-[color:var(--osd-muted)]">{formatDateTime(event.timestamp)}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {activeTab === 'epics' && (
        <div className="grid gap-4 lg:grid-cols-[1.2fr_1fr]">
          <div className="glass-card p-5 space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-semibold">Epics</h2>
              <div className="flex gap-2">
                <input
                  className="rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2 text-sm"
                  placeholder="New epic"
                  value={newEpicTitle}
                  onChange={(event) => setNewEpicTitle(event.target.value)}
                />
                <button
                  type="button"
                  className="btn btn-primary"
                  onClick={() => createEpic.mutate()}
                  disabled={!newEpicTitle}
                >
                  <Plus className="w-4 h-4" />
                  Add
                </button>
              </div>
            </div>
            <div className="space-y-2">
              {epics.map((epic) => (
                <button
                  key={epic.epic_id}
                  type="button"
                  onClick={() => setSelectedEpicId(epic.epic_id)}
                  className={`w-full text-left rounded-lg border px-3 py-2 ${
                    selectedEpicId === epic.epic_id
                      ? 'border-[color:var(--osd-accent)] bg-[color:var(--osd-accentSoft)]'
                      : 'border-[color:var(--osd-border)]'
                  }`}
                >
                  <div className="text-sm font-medium">{epic.title}</div>
                  <div className="text-xs text-[color:var(--osd-muted)]">{epic.status}</div>
                </button>
              ))}
            </div>
          </div>

          <div className="glass-card p-5 space-y-3">
            <h2 className="text-sm font-semibold">Epic Details</h2>
            {selectedEpic ? (
              <>
                <div className="text-base font-semibold">{selectedEpic.title}</div>
                <p className="text-sm text-[color:var(--osd-muted)]">{selectedEpic.description || '—'}</p>
                <div className="text-xs text-[color:var(--osd-muted)]">
                  Acceptance: {selectedEpic.acceptance_criteria || '—'}
                </div>
                <div className="text-xs text-[color:var(--osd-muted)]">
                  Tasks: {selectedEpic.rollup?.done_tasks ?? 0}/{selectedEpic.rollup?.total_tasks ?? 0}
                </div>
              </>
            ) : (
              <p className="text-sm text-[color:var(--osd-muted)]">Select an epic to view details.</p>
            )}
          </div>
        </div>
      )}

      {activeTab === 'tasks' && (
        <div className="grid gap-4 lg:grid-cols-[1.5fr_1fr]">
          <div className="glass-card p-5 space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-semibold">Tasks</h2>
              <div className="flex gap-2">
                <input
                  className="rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2 text-sm"
                  placeholder="New task"
                  value={newTaskTitle}
                  onChange={(event) => setNewTaskTitle(event.target.value)}
                />
                <button
                  type="button"
                  className="btn btn-primary"
                  onClick={() => createTask.mutate()}
                  disabled={!newTaskTitle}
                >
                  <Plus className="w-4 h-4" />
                  Add
                </button>
              </div>
            </div>
            <div className="space-y-2">
              {tasks.map((task) => (
                <button
                  key={task.task_id}
                  type="button"
                  onClick={() => setSelectedTaskId(task.task_id)}
                  className={`w-full text-left rounded-lg border px-3 py-2 ${
                    selectedTaskId === task.task_id
                      ? 'border-[color:var(--osd-accent)] bg-[color:var(--osd-accentSoft)]'
                      : 'border-[color:var(--osd-border)]'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="text-sm font-medium">{task.title}</div>
                    <span className="text-xs text-[color:var(--osd-muted)]">{task.priority}</span>
                  </div>
                  <div className="text-xs text-[color:var(--osd-muted)]">{task.status}</div>
                </button>
              ))}
            </div>
          </div>

          <div className="glass-card p-5 space-y-4">
            <h2 className="text-sm font-semibold">Task Details</h2>
            {selectedTask ? (
              <>
                <div>
                  <label className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Title</label>
                  <input
                    className="mt-2 w-full rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2 text-sm"
                    value={selectedTask.title}
                    onChange={(event) =>
                      updateTask.mutate({ title: event.target.value })
                    }
                  />
                </div>
                <div>
                  <label className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Status</label>
                  <select
                    className="mt-2 w-full rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2 text-sm"
                    value={selectedTask.status}
                    onChange={(event) => updateTask.mutate({ status: event.target.value as PmsTask['status'] })}
                  >
                    <option value="TODO">TODO</option>
                    <option value="IN_PROGRESS">IN PROGRESS</option>
                    <option value="BLOCKED">BLOCKED</option>
                    <option value="DONE">DONE</option>
                    <option value="ARCHIVED">ARCHIVED</option>
                  </select>
                </div>
                <div>
                  <label className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Todos</label>
                  <div className="mt-2 space-y-2">
                    {selectedTask.todos.map((todo: PmsTodo) => (
                      <div key={todo.todo_id} className="flex items-center justify-between text-sm">
                        <span className={todo.status === 'DONE' ? 'line-through text-[color:var(--osd-muted)]' : ''}>
                          {todo.text}
                        </span>
                        <button
                          type="button"
                          className="text-xs text-[color:var(--osd-muted)] hover:text-[color:var(--osd-text)]"
                          onClick={() => completeTodo.mutate(todo.todo_id)}
                        >
                          {todo.status === 'DONE' ? 'Done' : 'Complete'}
                        </button>
                      </div>
                    ))}
                    <div className="flex gap-2">
                      <input
                        className="flex-1 rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2 text-sm"
                        placeholder="Add todo"
                        value={newTodoText}
                        onChange={(event) => setNewTodoText(event.target.value)}
                      />
                      <button
                        type="button"
                        className="btn btn-secondary"
                        onClick={() => addTodo.mutate()}
                        disabled={!newTodoText}
                      >
                        Add
                      </button>
                    </div>
                  </div>
                </div>
              </>
            ) : (
              <p className="text-sm text-[color:var(--osd-muted)]">Select a task to edit details.</p>
            )}
          </div>
        </div>
      )}

      {activeTab === 'schedule' && (
        <div className="grid gap-4 lg:grid-cols-[1fr_2fr]">
          <div className="glass-card p-5 space-y-3">
            <h2 className="text-sm font-semibold">Next Task</h2>
            {nextTask ? (
              <div className="text-sm">
                <div className="font-medium">{nextTask.title}</div>
                <div className="text-xs text-[color:var(--osd-muted)]">{nextTask.priority}</div>
              </div>
            ) : (
              <p className="text-sm text-[color:var(--osd-muted)]">No eligible tasks.</p>
            )}
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => pmsApi.validateInvariants(projectId, currentActor)}
            >
              Validate Invariants
            </button>
          </div>
          <div className="glass-card p-5 space-y-4">
            <h2 className="text-sm font-semibold">Lane Board</h2>
            {schedulerIndex?.tiers.map((tier) => (
              <div key={tier.tier} className="space-y-2">
                <h3 className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">{tier.tier}</h3>
                <div className="grid gap-2 md:grid-cols-2">
                  {tier.lanes.map((lane) => (
                    <div key={lane.lane_key} className="rounded-lg border border-[color:var(--osd-border)] p-3">
                      <div className="text-xs text-[color:var(--osd-muted)]">{lane.lane_key}</div>
                      <ul className="mt-2 text-sm space-y-1">
                        {lane.task_ids.map((taskId) => (
                          <li key={taskId}>{shortId(taskId)}</li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'runs' && (
        <div className="glass-card p-5 space-y-3">
          <h2 className="text-sm font-semibold">Runs & Artifacts</h2>
          <div className="space-y-2 text-sm">
            {runs.map((run) => (
              <div key={run.run_id} className="flex items-center justify-between">
                <span>{shortId(run.run_id)} · {run.status}</span>
                <span className="text-xs text-[color:var(--osd-muted)]">{formatDateTime(run.started_at)}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'documents' && (
        <div className="glass-card p-5 space-y-3">
          <h2 className="text-sm font-semibold">Documents</h2>
          <div className="space-y-2 text-sm">
            {documents.map((doc) => (
              <div key={doc.document_id} className="flex items-center justify-between">
                <span>{doc.title}</span>
                <span className="text-xs text-[color:var(--osd-muted)]">{doc.kind}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'journal' && (
        <div className="glass-card p-5 space-y-3">
          <h2 className="text-sm font-semibold">Meeting Journal</h2>
          <div className="space-y-2 text-sm">
            {meetings.map((meeting) => (
              <div key={meeting.meeting_id} className="flex items-center justify-between">
                <span>{meeting.title}</span>
                <span className="text-xs text-[color:var(--osd-muted)]">{formatDate(meeting.started_at)}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'finance' && (
        <div className="grid gap-4 lg:grid-cols-2">
          <div className="glass-card p-5 space-y-3">
            <h2 className="text-sm font-semibold">Expenses</h2>
            {expenses.map((expense) => (
              <div key={expense.expense_id} className="flex items-center justify-between text-sm">
                <span>{expense.vendor}</span>
                <span>{formatCurrency(expense.amount, expense.currency)}</span>
              </div>
            ))}
          </div>
          <div className="glass-card p-5 space-y-3">
            <h2 className="text-sm font-semibold">Time Entries</h2>
            {timeEntries.map((entry) => (
              <div key={entry.time_entry_id} className="flex items-center justify-between text-sm">
                <span>{entry.role}</span>
                <span>{formatCurrency(entry.labor_cost ?? 0)}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'audit' && (
        <div className="glass-card p-5 space-y-3">
          <div className="flex items-center gap-2">
            <Shield className="w-4 h-4 text-[color:var(--osd-muted)]" />
            <h2 className="text-sm font-semibold">Audit Events</h2>
          </div>
          <div className="space-y-2 text-sm">
            {auditEvents.map((event) => (
              <div key={event.event_id} className="flex items-center justify-between">
                <span>{event.action}</span>
                <span className="text-xs text-[color:var(--osd-muted)]">{formatDateTime(event.timestamp)}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'settings' && (
        <div className="glass-card p-5 space-y-4">
          <div className="flex items-center gap-2">
            <Settings className="w-4 h-4 text-[color:var(--osd-muted)]" />
            <h2 className="text-sm font-semibold">Project Settings</h2>
          </div>
          <p className="text-sm text-[color:var(--osd-muted)]">
            Configure priority tiers, category vocabularies, and retention policies in the project config.
          </p>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={() => pmsApi.updateProject(projectId, { config: { priority_tiers: ['P0', 'P1', 'P2'] } }, currentActor)}
          >
            Save Scheduler Config
          </button>
        </div>
      )}
    </div>
  )
}
