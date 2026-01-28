import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, RefreshCw, Trash2 } from 'lucide-react'
import { useMemo, useState } from 'react'
import { toast } from '../utils/toast'
import apiClient, { apiPath } from '../lib/apiClient'
import { extractArray } from '../lib/responseHelpers'
import { Task } from '../types'

const fetchTasks = async (): Promise<Task[]> => {
  const { data } = await apiClient.get(apiPath('tasks'))
  return extractArray<Task>(data, ['tasks', 'items'])
}

const createTask = async (task: Partial<Task>): Promise<Task> => {
  const { data } = await apiClient.post(apiPath('tasks'), task)
  if (data && typeof data === 'object' && 'task' in data && data.task) {
    return data.task as Task
  }
  return data as Task
}

const updateTask = async (id: number, task: Partial<Task>): Promise<Task> => {
  const { data } = await apiClient.put(apiPath(`tasks/${id}`), task)
  if (data && typeof data === 'object' && 'task' in data && data.task) {
    return data.task as Task
  }
  return data as Task
}

const deleteTask = async (id: number): Promise<void> => {
  await apiClient.delete(apiPath(`tasks/${id}`))
}

export default function Tasks() {
  const [isCreating, setIsCreating] = useState(false)
  const [showCompleted, setShowCompleted] = useState(true)
  const [newTask, setNewTask] = useState({
    title: '',
    project: 'General',
    status: 'TODO',
    priority: 'MEDIUM',
  })

  const queryClient = useQueryClient()
  const { data: tasks, isLoading, refetch } = useQuery({
    queryKey: ['tasks'],
    queryFn: fetchTasks,
  })

  const createMutation = useMutation({
    mutationFn: createTask,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
      toast.success('Task created successfully')
      setIsCreating(false)
      setNewTask({ title: '', project: 'General', status: 'TODO', priority: 'MEDIUM' })
    },
    onError: (error) => {
      toast.error(`Failed to create task: ${error instanceof Error ? error.message : 'Unknown error'}`)
    },
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, task }: { id: number; task: Partial<Task> }) => updateTask(id, task),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
      toast.success('Task updated successfully')
    },
    onError: (error) => {
      toast.error(`Failed to update task: ${error instanceof Error ? error.message : 'Unknown error'}`)
    },
  })

  const deleteMutation = useMutation({
    mutationFn: deleteTask,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
      toast.success('Task deleted successfully')
    },
    onError: (error) => {
      toast.error(`Failed to delete task: ${error instanceof Error ? error.message : 'Unknown error'}`)
    },
  })

  const filteredTasks = useMemo(() => {
    if (!tasks) return []
    return tasks.filter((task) => (showCompleted ? true : task.status !== 'DONE'))
  }, [tasks, showCompleted])

  const statusCounts = useMemo(() => {
    const counts: Record<string, number> = { TODO: 0, IN_PROGRESS: 0, BLOCKED: 0, DONE: 0 }
    filteredTasks.forEach((task) => {
      counts[task.status] = (counts[task.status] || 0) + 1
    })
    return counts
  }, [filteredTasks])

  const priorityCounts = useMemo(() => {
    const counts: Record<string, number> = { LOW: 0, MEDIUM: 0, HIGH: 0, CRITICAL: 0 }
    filteredTasks.forEach((task) => {
      counts[task.priority] = (counts[task.priority] || 0) + 1
    })
    return counts
  }, [filteredTasks])

  const handleStatusChange = (task: Task, newStatus: string) => {
    updateMutation.mutate({ id: task.id, task: { status: newStatus } })
  }

  const handlePriorityChange = (task: Task, newPriority: string) => {
    updateMutation.mutate({ id: task.id, task: { priority: newPriority } })
  }

  const handleCreate = () => {
    if (!newTask.title.trim()) {
      toast.error('Task title is required')
      return
    }
    createMutation.mutate(newTask)
  }

  const priorityColors: Record<string, string> = {
    LOW: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
    MEDIUM: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
    HIGH: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200',
    CRITICAL: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
  }

  const statusColors: Record<string, string> = {
    TODO: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200',
    IN_PROGRESS: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
    BLOCKED: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
    DONE: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
  }

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center h-64 gap-4">
        <div className="animate-spin rounded-full h-12 w-12 border-2 border-white/30 border-t-primary-500"></div>
        <p className="text-sm text-slate-400">Loading tasks...</p>
      </div>
    )
  }

  return (
    <div id="overview" className="px-4 py-6 sm:px-0">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
        <div>
          <h2 className="text-2xl font-bold text-[color:var(--osd-text)]">Tasks</h2>
          <p className="text-sm text-[color:var(--osd-muted)] mt-1">Manage your tasks and to-dos</p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => refetch()}
            className="inline-flex items-center px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md text-sm font-medium text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </button>
          <button
            onClick={() => setIsCreating(!isCreating)}
            className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700"
          >
            <Plus className="w-5 h-5 mr-2" />
            New Task
          </button>
        </div>
      </div>

      {isCreating && (
        <div id="create" className="bg-white dark:bg-gray-800 shadow rounded-lg p-6 mb-6">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Create New Task</h3>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Title *
              </label>
              <input
                type="text"
                value={newTask.title}
                onChange={(e) => setNewTask({ ...newTask, title: e.target.value })}
                className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                placeholder="Enter task title"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Project
              </label>
              <input
                type="text"
                value={newTask.project}
                onChange={(e) => setNewTask({ ...newTask, project: e.target.value })}
                className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Status
              </label>
              <select
                value={newTask.status}
                onChange={(e) => setNewTask({ ...newTask, status: e.target.value })}
                className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              >
                <option value="TODO">TODO</option>
                <option value="IN_PROGRESS">IN_PROGRESS</option>
                <option value="BLOCKED">BLOCKED</option>
                <option value="DONE">DONE</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Priority
              </label>
              <select
                value={newTask.priority}
                onChange={(e) => setNewTask({ ...newTask, priority: e.target.value })}
                className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              >
                <option value="LOW">LOW</option>
                <option value="MEDIUM">MEDIUM</option>
                <option value="HIGH">HIGH</option>
                <option value="CRITICAL">CRITICAL</option>
              </select>
            </div>
          </div>
          <div className="mt-4 flex justify-end space-x-3">
            <button
              onClick={() => setIsCreating(false)}
              className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-600"
            >
              Cancel
            </button>
            <button
              onClick={handleCreate}
              disabled={createMutation.isPending}
              className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 disabled:opacity-50"
            >
              {createMutation.isPending ? 'Creating...' : 'Create Task'}
            </button>
          </div>
        </div>
      )}

      <div
        id="filters"
        className="flex flex-col md:flex-row md:items-center md:justify-between bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4 mb-6 gap-3"
      >
        <div className="flex items-center gap-3 text-sm text-gray-700 dark:text-gray-300">
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={showCompleted}
              onChange={(e) => setShowCompleted(e.target.checked)}
              className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
            />
            <span>Show Completed Tasks</span>
          </label>
          <span className="text-gray-400 dark:text-gray-500">|</span>
          <span>
            {filteredTasks.length} visible / {tasks?.length ?? 0} total
          </span>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm w-full md:w-auto">
          {Object.entries(statusCounts).map(([status, count]) => (
            <div
              key={status}
              className="rounded-lg border border-gray-200 dark:border-gray-700 px-3 py-2 bg-gray-50 dark:bg-gray-900/40"
            >
              <p className="text-xs uppercase tracking-wide text-gray-500 dark:text-gray-400">
                {status.replace('_', ' ')}
              </p>
              <p className="text-lg font-semibold text-gray-900 dark:text-white">{count}</p>
            </div>
          ))}
        </div>
      </div>

      <div id="list" className="bg-white dark:bg-gray-800 shadow rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Title
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Project
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Priority
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Owner
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              {filteredTasks.map((task) => (
                <tr key={task.id}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900 dark:text-white">{task.title}</div>
                    {task.notes && (
                      <div className="text-sm text-gray-500 dark:text-gray-400">{task.notes}</div>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900 dark:text-white">{task.project}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <select
                      value={task.status}
                      onChange={(e) => handleStatusChange(task, e.target.value)}
                      className={`text-xs font-medium px-2 py-1 rounded-full ${statusColors[task.status] || statusColors.TODO}`}
                    >
                      <option value="TODO">TODO</option>
                      <option value="IN_PROGRESS">IN_PROGRESS</option>
                      <option value="BLOCKED">BLOCKED</option>
                      <option value="DONE">DONE</option>
                    </select>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <select
                      value={task.priority}
                      onChange={(e) => handlePriorityChange(task, e.target.value)}
                      className={`text-xs font-medium px-2 py-1 rounded-full ${priorityColors[task.priority] || priorityColors.MEDIUM}`}
                    >
                      <option value="LOW">LOW</option>
                      <option value="MEDIUM">MEDIUM</option>
                      <option value="HIGH">HIGH</option>
                      <option value="CRITICAL">CRITICAL</option>
                    </select>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900 dark:text-white">{task.owner}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button
                      onClick={() => deleteMutation.mutate(task.id)}
                      className="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300 ml-4"
                    >
                      <Trash2 className="w-5 h-5" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {filteredTasks.length === 0 && (
            <div className="text-center py-12">
              <p className="text-gray-500 dark:text-gray-400">
                {tasks && tasks.length > 0
                  ? 'No tasks match the current filters.'
                  : 'No tasks found. Create your first task!'}
              </p>
            </div>
          )}
        </div>
      </div>

      <div id="summary" className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Summary</h3>
        <div className="grid gap-4 md:grid-cols-2">
          <div>
            <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Status Counts</p>
            <ul className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
              {Object.entries(statusCounts).map(([status, count]) => (
                <li key={status}>
                  • {status.replace('_', ' ')}:{' '}
                  <span className="font-semibold text-gray-900 dark:text-white">{count}</span>
                </li>
              ))}
            </ul>
          </div>
          <div>
            <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Priority Counts</p>
            <ul className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
              {Object.entries(priorityCounts).map(([priority, count]) => (
                <li key={priority}>
                  • {priority}:{' '}
                  <span className="font-semibold text-gray-900 dark:text-white">{count}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}
