/**
 * Comprehensive API Service Layer
 * Centralized API client with error handling, retry logic, and type safety
 */

import apiClient, { apiPath } from '../lib/apiClient'
import { extractArray } from '../lib/responseHelpers'
import type { Task, Project, ChatMessage, DashboardStats } from '../types'

// ============================================================================
// Types
// ============================================================================

export interface ApiResponse<T> {
  data: T
  error?: string
  requestId?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  pageSize: number
}

export interface CookbookToolExample {
  prompt: string
  tool_name: string
}

export interface CookbookToolExamplesResponse {
  tools: Record<string, unknown>[]
  examples: CookbookToolExample[]
  openapi_hint: string
}

export interface CookbookTriageRequest {
  prompt: string
  mode?: 'auto' | 'heuristic' | 'llm'
  max_agents?: number
  model?: string
}

export interface CookbookTriageResponse {
  agents: string[]
  rationale: string
  confidence: number
  mode: string
}

export interface CookbookGuardrailsRequest {
  response_text: string
  blocked_phrases?: string[]
  max_response_chars?: number
  require_safe_language?: boolean
}

export interface CookbookGuardrailsResponse {
  allowed: boolean
  score: number
  violations: { rule: string; detail: string }[]
  notes: string[]
}

export interface CookbookFileSearchRequest {
  query: string
  vector_store_ids: string[]
  max_num_results?: number
  ranking_options?: Record<string, unknown>
  model?: string
}

export interface CookbookFileSearchResponse {
  response: string
  results: Record<string, unknown>[]
  tool_calls: Record<string, unknown>[]
}

// ============================================================================
// Tasks API
// ============================================================================

export const tasksApi = {
  list: async (): Promise<Task[]> => {
    const { data } = await apiClient.get(apiPath('tasks'))
    return extractArray<Task>(data, ['tasks', 'items'])
  },

  get: async (id: number): Promise<Task> => {
    const { data } = await apiClient.get(apiPath(`tasks/${id}`))
    return data.task || data
  },

  create: async (task: Partial<Task>): Promise<Task> => {
    const { data } = await apiClient.post(apiPath('tasks'), task)
    return data.task || data
  },

  update: async (id: number, task: Partial<Task>): Promise<Task> => {
    const { data } = await apiClient.put(apiPath(`tasks/${id}`), task)
    return data.task || data
  },

  delete: async (id: number): Promise<void> => {
    await apiClient.delete(apiPath(`tasks/${id}`))
  },
}

// ============================================================================
// Projects API
// ============================================================================

export const projectsApi = {
  list: async (): Promise<Project[]> => {
    const { data } = await apiClient.get(apiPath('projects'))
    return extractArray<Project>(data, ['projects', 'items'])
  },

  get: async (name: string): Promise<Project> => {
    const { data } = await apiClient.get(apiPath(`projects/${encodeURIComponent(name)}`))
    return data.project || data
  },

  create: async (project: Partial<Project>): Promise<Project> => {
    const { data } = await apiClient.post(apiPath('projects'), project)
    return data.project || data
  },

  update: async (name: string, project: Partial<Project>): Promise<Project> => {
    const { data } = await apiClient.put(apiPath(`projects/${encodeURIComponent(name)}`), project)
    return data.project || data
  },

  delete: async (name: string): Promise<void> => {
    await apiClient.delete(apiPath(`projects/${encodeURIComponent(name)}`))
  },
}

// ============================================================================
// Chat API
// ============================================================================

export const chatApi = {
  list: async (persona?: string): Promise<ChatMessage[]> => {
    const params = persona ? { persona } : undefined
    const { data } = await apiClient.get(apiPath('chat/'), { params })
    return extractArray<ChatMessage>(data, ['messages', 'items'])
  },

  send: async (message: {
    persona: string
    model_provider: string
    content: string
    attachments?: string[]
  }): Promise<{ user_message: ChatMessage; ai_reply: ChatMessage }> => {
    const payload = {
      persona: message.persona,
      model_provider: message.model_provider,
      role: 'user',
      kind: 'chat',
      content: message.content,
      attachments: message.attachments ?? undefined,
    }
    const { data } = await apiClient.post(apiPath('chat/'), payload)
    
    if (data && typeof data === 'object') {
      if ('user_message' in data && 'ai_reply' in data) {
        return {
          user_message: data.user_message as ChatMessage,
          ai_reply: data.ai_reply as ChatMessage,
        }
      }
      if ('message' in data && data.message) {
        return {
          user_message: data.message as ChatMessage,
          ai_reply: data.message as ChatMessage,
        }
      }
      if ('id' in data && 'content' in data) {
        return {
          user_message: data as ChatMessage,
          ai_reply: data as ChatMessage,
        }
      }
    }
    
    throw new Error('Invalid response format from chat API')
  },

  clear: async (): Promise<void> => {
    await apiClient.delete(apiPath('chat/'))
  },
}

// ============================================================================
// Dashboard API
// ============================================================================

export const dashboardApi = {
  getStats: async (): Promise<DashboardStats> => {
    const { data } = await apiClient.get(apiPath('dashboard/stats'))
    return data
  },

  getSystemStatus: async () => {
    const { data } = await apiClient.get('/system')
    return data
  },

  getPlanesStatus: async () => {
    const { data } = await apiClient.get('/planes/status')
    return data
  },
}

// ============================================================================
// Documents API
// ============================================================================

export const documentsApi = {
  list: async (): Promise<any[]> => {
    const { data } = await apiClient.get(apiPath('documents'))
    return extractArray(data, ['documents', 'items'])
  },

  get: async (id: string): Promise<any> => {
    const { data } = await apiClient.get(apiPath(`documents/${id}`))
    return data.document || data
  },

  create: async (document: any): Promise<any> => {
    const { data } = await apiClient.post(apiPath('documents'), document)
    return data.document || data
  },

  update: async (id: string, document: any): Promise<any> => {
    const { data } = await apiClient.put(apiPath(`documents/${id}`), document)
    return data.document || data
  },

  delete: async (id: string): Promise<void> => {
    await apiClient.delete(apiPath(`documents/${id}`))
  },
}

// ============================================================================
// Settings API
// ============================================================================

export const settingsApi = {
  get: async (): Promise<any> => {
    const { data } = await apiClient.get(apiPath('settings'))
    return data
  },

  update: async (settings: any): Promise<any> => {
    const { data } = await apiClient.put(apiPath('settings'), settings)
    return data
  },
}

// ============================================================================
// Integrations API
// ============================================================================

export const integrationsApi = {
  list: async (): Promise<any[]> => {
    const { data } = await apiClient.get(apiPath('integrations'))
    return extractArray(data, ['integrations', 'items'])
  },

  connect: async (service: string): Promise<any> => {
    const { data } = await apiClient.post(apiPath(`integrations/${service}/connect`))
    return data
  },

  disconnect: async (service: string): Promise<void> => {
    await apiClient.post(apiPath(`integrations/${service}/disconnect`))
  },
}

// ============================================================================
// Analytics API
// ============================================================================

export const analyticsApi = {
  getMetrics: async (): Promise<any> => {
    const { data } = await apiClient.get(apiPath('analytics/metrics'))
    return data
  },

  getReports: async (): Promise<any[]> => {
    const { data } = await apiClient.get(apiPath('analytics/reports'))
    return extractArray(data, ['reports', 'items'])
  },
}

// ============================================================================
// Search API
// ============================================================================

export const searchApi = {
  search: async (query: string): Promise<any[]> => {
    const { data } = await apiClient.get(apiPath(`search?q=${encodeURIComponent(query)}`))
    return extractArray(data, ['results', 'items'])
  },
}

// ============================================================================
// Workspace API
// ============================================================================

export const workspaceApi = {
  getHealth: async (): Promise<any> => {
    const { data } = await apiClient.get(apiPath('workspace/health'))
    return data
  },

  getProjects: async (): Promise<any[]> => {
    const { data } = await apiClient.get(apiPath('workspace/projects'))
    return extractArray(data, ['projects', 'items'])
  },

  scan: async (): Promise<any> => {
    const { data } = await apiClient.post(apiPath('workspace/scan'))
    return data
  },
}

// ============================================================================
// Terminal API
// ============================================================================

export const terminalApi = {
  execute: async (command: string, cwd?: string): Promise<any> => {
    const { data } = await apiClient.post(apiPath('terminal'), { command, cwd })
    return data
  },

  getCommands: async (): Promise<string[]> => {
    const { data } = await apiClient.get(apiPath('terminal/commands'))
    return extractArray(data, ['commands', 'items'])
  },
}

// ============================================================================
// Cookbook Patterns API
// ============================================================================

export const cookbookApi = {
  getToolExamples: async (): Promise<CookbookToolExamplesResponse> => {
    const { data } = await apiClient.get(apiPath('cookbook/tool-examples'))
    return data
  },

  triage: async (payload: CookbookTriageRequest): Promise<CookbookTriageResponse> => {
    const { data } = await apiClient.post(apiPath('cookbook/triage'), payload)
    return data
  },

  guardrails: async (payload: CookbookGuardrailsRequest): Promise<CookbookGuardrailsResponse> => {
    const { data } = await apiClient.post(apiPath('cookbook/guardrails'), payload)
    return data
  },

  fileSearch: async (payload: CookbookFileSearchRequest): Promise<CookbookFileSearchResponse> => {
    const { data } = await apiClient.post(apiPath('cookbook/file-search'), payload)
    return data
  },
}

// ============================================================================
// AI Systems API
// ============================================================================

export const aiSystemsApi = {
  ask: async (prompt: string): Promise<string> => {
    const { data } = await apiClient.post(apiPath('ai/ask'), { prompt })
    return data.response || data.message || data
  },

  getPersonas: async (): Promise<any> => {
    const { data } = await apiClient.get(apiPath('personas'))
    return data
  },
}

// ============================================================================
// Unified API Export
// ============================================================================

export const api = {
  tasks: tasksApi,
  projects: projectsApi,
  chat: chatApi,
  dashboard: dashboardApi,
  documents: documentsApi,
  settings: settingsApi,
  integrations: integrationsApi,
  analytics: analyticsApi,
  search: searchApi,
  workspace: workspaceApi,
  terminal: terminalApi,
  ai: aiSystemsApi,
  cookbook: cookbookApi,
}

export default api
