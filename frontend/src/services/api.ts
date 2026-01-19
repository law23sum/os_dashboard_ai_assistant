/**
 * Comprehensive API Service Layer
 * Centralized API client with error handling, retry logic, and type safety
 */

import apiClient, { apiPath } from '../lib/apiClient'
import { extractArray } from '../lib/responseHelpers'
import type { Task, Project, ChatMessage, DashboardStats, ApiSessionCostResponse } from '../types'

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

export interface ToolingToolExample {
  prompt: string
  tool_name: string
}

export interface ToolingToolExamplesResponse {
  tools: Record<string, unknown>[]
  examples: ToolingToolExample[]
  openapi_hint: string
}

export interface ToolingTriageRequest {
  prompt: string
  mode?: 'auto' | 'heuristic' | 'llm'
  max_agents?: number
  model?: string
}

export interface ToolingTriageResponse {
  agents: string[]
  rationale: string
  confidence: number
  mode: string
}

export interface ToolingGuardrailsRequest {
  response_text: string
  blocked_phrases?: string[]
  max_response_chars?: number
  require_safe_language?: boolean
}

export interface ToolingGuardrailsResponse {
  allowed: boolean
  score: number
  violations: { rule: string; detail: string }[]
  notes: string[]
}

export interface ToolingFileSearchRequest {
  query: string
  vector_store_ids: string[]
  max_num_results?: number
  ranking_options?: Record<string, unknown>
  model?: string
}

export interface ToolingFileSearchResponse {
  response: string
  results: Record<string, unknown>[]
  tool_calls: Record<string, unknown>[]
}

export type CookbookToolExample = ToolingToolExample
export type CookbookToolExamplesResponse = ToolingToolExamplesResponse
export type CookbookTriageRequest = ToolingTriageRequest
export type CookbookTriageResponse = ToolingTriageResponse
export type CookbookGuardrailsRequest = ToolingGuardrailsRequest
export type CookbookGuardrailsResponse = ToolingGuardrailsResponse
export type CookbookFileSearchRequest = ToolingFileSearchRequest
export type CookbookFileSearchResponse = ToolingFileSearchResponse

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
// API Session Costs
// ============================================================================

export const apiSessionCostsApi = {
  get: async (): Promise<ApiSessionCostResponse> => {
    const { data } = await apiClient.get<ApiSessionCostResponse>(apiPath('api-session-costs'))
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
// Tooling Patterns API
// ============================================================================

export const toolingApi = {
  getToolExamples: async (): Promise<ToolingToolExamplesResponse> => {
    const { data } = await apiClient.get(apiPath('ai-tooling/tool-examples'))
    return data
  },

  triage: async (payload: ToolingTriageRequest): Promise<ToolingTriageResponse> => {
    const { data } = await apiClient.post(apiPath('ai-tooling/triage'), payload)
    return data
  },

  guardrails: async (payload: ToolingGuardrailsRequest): Promise<ToolingGuardrailsResponse> => {
    const { data } = await apiClient.post(apiPath('ai-tooling/guardrails'), payload)
    return data
  },

  fileSearch: async (payload: ToolingFileSearchRequest): Promise<ToolingFileSearchResponse> => {
    const { data } = await apiClient.post(apiPath('ai-tooling/file-search'), payload)
    return data
  },
}

export const cookbookApi = toolingApi

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
  tooling: toolingApi,
  cookbook: cookbookApi,
}

export default api
