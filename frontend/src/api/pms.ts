import apiClient, { apiPath } from '../lib/apiClient'
import type {
  PmsAuditEvent,
  PmsCostRollup,
  PmsDocument,
  PmsDocumentRevision,
  PmsEpic,
  PmsExecutionRun,
  PmsExpenseEntry,
  PmsJournalBlock,
  PmsMeetingSession,
  PmsProject,
  PmsSchedulerIndex,
  PmsSearchResponse,
  PmsTask,
  PmsTimeEntry,
  PmsTranscriptSegment,
} from '../types/pms'
import type { ActorType } from '../types/actor'

type ScopeParams = {
  scope?: ActorType
  workspace_id?: string
}

const withScope = (scope?: ActorType, workspace_id?: string) => ({
  scope,
  workspace_id,
})

const scopeQuery = (scope?: ActorType, workspace_id?: string) => {
  const params = new URLSearchParams()
  if (scope) params.set('scope', scope)
  if (workspace_id) params.set('workspace_id', workspace_id)
  return params.toString()
}

export const pmsApi = {
  // Projects
  listProjects: async (scope?: ActorType) => {
    const { data } = await apiClient.get<PmsProject[]>(apiPath('pms/projects'), {
      params: withScope(scope),
    })
    return data
  },
  createProject: async (scope: ActorType, payload: Partial<PmsProject>) => {
    const { data } = await apiClient.post<PmsProject>(apiPath('pms/projects'), payload, {
      params: withScope(scope),
    })
    return data
  },
  getProject: async (projectId: string, scope?: ActorType) => {
    const { data } = await apiClient.get<PmsProject>(apiPath(`pms/projects/${projectId}`), {
      params: withScope(scope),
    })
    return data
  },
  updateProject: async (projectId: string, payload: Partial<PmsProject>, scope?: ActorType) => {
    const { data } = await apiClient.put<PmsProject>(apiPath(`pms/projects/${projectId}`), payload, {
      params: withScope(scope),
    })
    return data
  },

  // Epics
  listEpics: async (projectId: string, scope?: ActorType) => {
    const { data } = await apiClient.get<PmsEpic[]>(apiPath(`pms/projects/${projectId}/epics`), {
      params: withScope(scope),
    })
    return data
  },
  createEpic: async (projectId: string, payload: Partial<PmsEpic>, scope?: ActorType) => {
    const { data } = await apiClient.post<PmsEpic>(apiPath(`pms/projects/${projectId}/epics`), payload, {
      params: withScope(scope),
    })
    return data
  },
  updateEpic: async (projectId: string, epicId: string, payload: Partial<PmsEpic>, scope?: ActorType) => {
    const { data } = await apiClient.put<PmsEpic>(apiPath(`pms/projects/${projectId}/epics/${epicId}`), payload, {
      params: withScope(scope),
    })
    return data
  },
  archiveEpic: async (projectId: string, epicId: string, scope?: ActorType) => {
    const { data } = await apiClient.post<PmsEpic>(apiPath(`pms/projects/${projectId}/epics/${epicId}/archive`), {}, {
      params: withScope(scope),
    })
    return data
  },

  // Tasks & Todos
  listTasks: async (projectId: string, scope?: ActorType) => {
    const { data } = await apiClient.get<PmsTask[]>(apiPath(`pms/projects/${projectId}/tasks`), {
      params: withScope(scope),
    })
    return data
  },
  createTask: async (projectId: string, payload: Partial<PmsTask>, scope?: ActorType) => {
    const { data } = await apiClient.post<PmsTask>(apiPath(`pms/projects/${projectId}/tasks`), payload, {
      params: withScope(scope),
    })
    return data
  },
  getTask: async (projectId: string, taskId: string, scope?: ActorType) => {
    const { data } = await apiClient.get<PmsTask>(apiPath(`pms/projects/${projectId}/tasks/${taskId}`), {
      params: withScope(scope),
    })
    return data
  },
  updateTask: async (projectId: string, taskId: string, payload: Partial<PmsTask>, scope?: ActorType) => {
    const { data } = await apiClient.put<PmsTask>(apiPath(`pms/projects/${projectId}/tasks/${taskId}`), payload, {
      params: withScope(scope),
    })
    return data
  },
  archiveTask: async (projectId: string, taskId: string, scope?: ActorType) => {
    const { data } = await apiClient.post<PmsTask>(apiPath(`pms/projects/${projectId}/tasks/${taskId}/archive`), {}, {
      params: withScope(scope),
    })
    return data
  },
  listTodos: async (projectId: string, taskId: string, scope?: ActorType) => {
    const { data } = await apiClient.get(apiPath(`pms/projects/${projectId}/tasks/${taskId}/todos`), {
      params: withScope(scope),
    })
    return data
  },
  addTodo: async (projectId: string, taskId: string, payload: { text: string }, scope?: ActorType) => {
    const { data } = await apiClient.post(apiPath(`pms/projects/${projectId}/tasks/${taskId}/todos`), payload, {
      params: withScope(scope),
    })
    return data
  },
  insertTodo: async (
    projectId: string,
    taskId: string,
    payload: { text: string; index?: number; after_todo_id?: string },
    scope?: ActorType,
  ) => {
    const { data } = await apiClient.post(apiPath(`pms/projects/${projectId}/tasks/${taskId}/todos/insert`), payload, {
      params: withScope(scope),
    })
    return data
  },
  reorderTodos: async (
    projectId: string,
    taskId: string,
    payload: { todo_ids: string[] },
    scope?: ActorType,
  ) => {
    const { data } = await apiClient.post(apiPath(`pms/projects/${projectId}/tasks/${taskId}/todos/reorder`), payload, {
      params: withScope(scope),
    })
    return data
  },
  completeTodo: async (projectId: string, taskId: string, todoId: string, scope?: ActorType) => {
    const { data } = await apiClient.post(apiPath(`pms/projects/${projectId}/tasks/${taskId}/todos/${todoId}/complete`), {}, {
      params: withScope(scope),
    })
    return data
  },

  // Scheduler
  nextTask: async (projectId: string, mutate = true, scope?: ActorType) => {
    const { data } = await apiClient.post<PmsTask | null>(
      apiPath(`pms/projects/${projectId}/schedule/next`),
      { mutate },
      { params: withScope(scope) },
    )
    return data
  },
  peekTasks: async (projectId: string, count = 5, scope?: ActorType) => {
    const { data } = await apiClient.get<PmsTask[]>(apiPath(`pms/projects/${projectId}/schedule/peek`), {
      params: { ...withScope(scope), count },
    })
    return data
  },
  getSchedulerIndex: async (projectId: string, scope?: ActorType) => {
    const { data } = await apiClient.get<PmsSchedulerIndex>(apiPath(`pms/projects/${projectId}/schedule/index`), {
      params: withScope(scope),
    })
    return data
  },
  validateInvariants: async (projectId: string, scope?: ActorType) => {
    const { data } = await apiClient.post(apiPath(`pms/projects/${projectId}/schedule/validate`), {}, {
      params: withScope(scope),
    })
    return data
  },

  // Runs & Artifacts
  startRun: async (payload: Record<string, unknown>, scope?: ActorType) => {
    const { data } = await apiClient.post<PmsExecutionRun>(apiPath('pms/runs'), payload, {
      params: withScope(scope),
    })
    return data
  },
  completeRun: async (runId: string, payload: Record<string, unknown>, scope?: ActorType) => {
    const { data } = await apiClient.post<PmsExecutionRun>(apiPath(`pms/runs/${runId}/complete`), payload, {
      params: withScope(scope),
    })
    return data
  },
  attachArtifact: async (runId: string, payload: Record<string, unknown>, scope?: ActorType) => {
    const { data } = await apiClient.post(apiPath(`pms/runs/${runId}/artifacts`), payload, {
      params: withScope(scope),
    })
    return data
  },
  listRuns: async (params: Record<string, unknown> = {}, scope?: ActorType) => {
    const { data } = await apiClient.get<PmsExecutionRun[]>(apiPath('pms/runs'), {
      params: { ...params, ...withScope(scope) },
    })
    return data
  },
  listArtifacts: async (params: Record<string, unknown> = {}, scope?: ActorType) => {
    const { data } = await apiClient.get(apiPath('pms/artifacts'), {
      params: { ...params, ...withScope(scope) },
    })
    return data
  },
  downloadArtifactUrl: (artifactId: string, scope?: ActorType) => {
    const query = scopeQuery(scope)
    const suffix = query ? `?${query}` : ''
    return apiPath(`pms/artifacts/${artifactId}/download${suffix}`)
  },

  // Documents
  listDocuments: async (projectId?: string, scope?: ActorType) => {
    const { data } = await apiClient.get<PmsDocument[]>(apiPath('pms/documents'), {
      params: { ...withScope(scope), project_id: projectId },
    })
    return data
  },
  createDocument: async (payload: Partial<PmsDocument>, scope?: ActorType) => {
    const { data } = await apiClient.post<PmsDocument>(apiPath('pms/documents'), payload, {
      params: withScope(scope),
    })
    return data
  },
  addRevision: async (documentId: string, payload: { content: string; metadata?: Record<string, unknown> }, scope?: ActorType) => {
    const { data } = await apiClient.post<PmsDocumentRevision>(
      apiPath(`pms/documents/${documentId}/revisions`),
      payload,
      { params: withScope(scope) },
    )
    return data
  },
  publishRevision: async (documentId: string, revisionHash: string, scope?: ActorType) => {
    const { data } = await apiClient.post<PmsDocument>(apiPath(`pms/documents/${documentId}/publish`), {
      revision_hash: revisionHash,
    }, { params: withScope(scope) })
    return data
  },
  getDocument: async (documentId: string, view: 'published' | 'latest' | 'history' = 'published', scope?: ActorType) => {
    const { data } = await apiClient.get(apiPath(`pms/documents/${documentId}`), {
      params: { ...withScope(scope), view },
    })
    return data
  },

  // Meetings
  listMeetings: async (projectId?: string, scope?: ActorType) => {
    const { data } = await apiClient.get<PmsMeetingSession[]>(apiPath('pms/meetings'), {
      params: { ...withScope(scope), project_id: projectId },
    })
    return data
  },
  createMeeting: async (payload: Partial<PmsMeetingSession>, scope?: ActorType) => {
    const { data } = await apiClient.post<PmsMeetingSession>(apiPath('pms/meetings'), payload, {
      params: withScope(scope),
    })
    return data
  },
  getMeeting: async (meetingId: string, scope?: ActorType) => {
    const { data } = await apiClient.get<PmsMeetingSession>(apiPath(`pms/meetings/${meetingId}`), {
      params: withScope(scope),
    })
    return data
  },
  transcribeMeeting: async (meetingId: string, payload: Record<string, unknown>, scope?: ActorType) => {
    const { data } = await apiClient.post(apiPath(`pms/meetings/${meetingId}/transcribe`), payload, {
      params: withScope(scope),
    })
    return data
  },
  listTranscriptSegments: async (meetingId: string, scope?: ActorType) => {
    const { data } = await apiClient.get<PmsTranscriptSegment[]>(apiPath(`pms/meetings/${meetingId}/segments`), {
      params: withScope(scope),
    })
    return data
  },
  listJournalBlocks: async (meetingId: string, scope?: ActorType, sectionType?: string) => {
    const { data } = await apiClient.get<PmsJournalBlock[]>(apiPath(`pms/meetings/${meetingId}/journal`), {
      params: { ...withScope(scope), section_type: sectionType },
    })
    return data
  },
  updateSpeakerMapping: async (meetingId: string, payload: Record<string, unknown>, scope?: ActorType) => {
    const { data } = await apiClient.post<PmsMeetingSession>(apiPath(`pms/meetings/${meetingId}/speaker-mapping`), payload, {
      params: withScope(scope),
    })
    return data
  },
  exportMeetingPacketUrl: (meetingId: string, scope?: ActorType) => {
    const query = scopeQuery(scope)
    const suffix = query ? `?${query}` : ''
    return apiPath(`pms/meetings/${meetingId}/packet${suffix}`)
  },

  // Finance
  listExpenses: async (projectId?: string, scope?: ActorType) => {
    const { data } = await apiClient.get<PmsExpenseEntry[]>(apiPath('pms/expenses'), {
      params: { ...withScope(scope), project_id: projectId },
    })
    return data
  },
  addExpense: async (payload: Partial<PmsExpenseEntry>, scope?: ActorType) => {
    const { data } = await apiClient.post<PmsExpenseEntry>(apiPath('pms/expenses'), payload, {
      params: withScope(scope),
    })
    return data
  },
  listTimeEntries: async (projectId?: string, scope?: ActorType) => {
    const { data } = await apiClient.get<PmsTimeEntry[]>(apiPath('pms/time-entries'), {
      params: { ...withScope(scope), project_id: projectId },
    })
    return data
  },
  addTimeEntry: async (payload: Partial<PmsTimeEntry>, scope?: ActorType) => {
    const { data } = await apiClient.post<PmsTimeEntry>(apiPath('pms/time-entries'), payload, {
      params: withScope(scope),
    })
    return data
  },
  costRollup: async (projectId: string, scope?: ActorType) => {
    const { data } = await apiClient.get<PmsCostRollup>(apiPath(`pms/projects/${projectId}/rollup`), {
      params: withScope(scope),
    })
    return data
  },

  // Audit
  listAuditEvents: async (projectId?: string, scope?: ActorType) => {
    const { data } = await apiClient.get<PmsAuditEvent[]>(apiPath('pms/audit'), {
      params: { ...withScope(scope), project_id: projectId },
    })
    return data
  },

  // Search
  search: async (payload: { query: string; scope?: ActorType }) => {
    const { data } = await apiClient.get<PmsSearchResponse>(apiPath('pms/search'), {
      params: { q: payload.query, ...withScope(payload.scope) },
    })
    return data
  },
}
