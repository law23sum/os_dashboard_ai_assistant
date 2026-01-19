import apiClient, { apiPath } from '../lib/apiClient'
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

export const conceptsApi = {
  // Models
  listModels: async (scope?: ActorType) => {
    const { data } = await apiClient.get(apiPath('concepts/models'), {
      params: withScope(scope),
    })
    return data
  },
  createModel: async (payload: Record<string, unknown>, scope?: ActorType) => {
    const { data } = await apiClient.post(apiPath('concepts/models'), payload, {
      params: withScope(scope),
    })
    return data
  },

  // Versions
  listVersions: async (modelId: string, scope?: ActorType) => {
    const { data } = await apiClient.get(apiPath(`concepts/models/${modelId}/versions`), {
      params: withScope(scope),
    })
    return data
  },
  createVersion: async (modelId: string, payload: Record<string, unknown>, scope?: ActorType) => {
    const { data } = await apiClient.post(apiPath(`concepts/models/${modelId}/versions`), payload, {
      params: withScope(scope),
    })
    return data
  },
  updateVersion: async (versionId: string, payload: Record<string, unknown>, scope?: ActorType) => {
    const { data } = await apiClient.put(apiPath(`concepts/versions/${versionId}`), payload, {
      params: withScope(scope),
    })
    return data
  },
  getBundle: async (versionId: string, scope?: ActorType) => {
    const { data } = await apiClient.get(apiPath(`concepts/versions/${versionId}/bundle`), {
      params: withScope(scope),
    })
    return data
  },
  getAnalysis: async (versionId: string, scope?: ActorType) => {
    const { data } = await apiClient.get(apiPath(`concepts/versions/${versionId}/analysis`), {
      params: withScope(scope),
    })
    return data
  },
  exportVersion: async (versionId: string, format: string, scope?: ActorType) => {
    const { data } = await apiClient.get(apiPath(`concepts/versions/${versionId}/export`), {
      params: { ...withScope(scope), format },
    })
    return data
  },

  // Nodes
  createNode: async (versionId: string, payload: Record<string, unknown>, scope?: ActorType) => {
    const { data } = await apiClient.post(apiPath(`concepts/versions/${versionId}/nodes`), payload, {
      params: withScope(scope),
    })
    return data
  },
  updateNode: async (versionId: string, nodeId: string, patch: Record<string, unknown>, scope?: ActorType) => {
    const { data } = await apiClient.patch(apiPath(`concepts/versions/${versionId}/nodes/${nodeId}`), patch, {
      params: withScope(scope),
    })
    return data
  },

  // Edges
  createEdge: async (versionId: string, payload: Record<string, unknown>, scope?: ActorType) => {
    const { data } = await apiClient.post(apiPath(`concepts/versions/${versionId}/edges`), payload, {
      params: withScope(scope),
    })
    return data
  },
  updateEdge: async (versionId: string, edgeId: string, patch: Record<string, unknown>, scope?: ActorType) => {
    const { data } = await apiClient.patch(apiPath(`concepts/versions/${versionId}/edges/${edgeId}`), patch, {
      params: withScope(scope),
    })
    return data
  },

  // Transitions
  upsertTransition: async (versionId: string, payload: Record<string, unknown>, scope?: ActorType) => {
    const { data } = await apiClient.post(apiPath(`concepts/versions/${versionId}/transitions`), payload, {
      params: withScope(scope),
    })
    return data
  },

  // IPM Integration (legacy /pms-links endpoints)
  listPmsLinks: async (params: { project_id?: string; epic_id?: string }, scope?: ActorType) => {
    const { data } = await apiClient.get(apiPath('concepts/pms-links'), {
      params: { ...params, ...withScope(scope) },
    })
    return data
  },
  createPmsLink: async (versionId: string, payload: Record<string, unknown>, scope?: ActorType) => {
    const { data } = await apiClient.post(apiPath(`concepts/versions/${versionId}/pms-links`), payload, {
      params: withScope(scope),
    })
    return data
  },
  getCoverage: async (versionId: string, projectId: string, epicId?: string, scope?: ActorType) => {
    const { data } = await apiClient.get(apiPath(`concepts/versions/${versionId}/coverage`), {
      params: { project_id: projectId, epic_id: epicId, ...withScope(scope) },
    })
    return data
  },
  generateBacklog: async (versionId: string, payload: Record<string, unknown>, scope?: ActorType) => {
    const { data } = await apiClient.post(apiPath(`concepts/versions/${versionId}/backlog/generate`), payload, {
      params: withScope(scope),
    })
    return data
  },
  getBacklogDelta: async (versionId: string, payload: Record<string, unknown>, scope?: ActorType) => {
    const { data } = await apiClient.post(apiPath(`concepts/versions/${versionId}/backlog/delta`), payload, {
      params: withScope(scope),
    })
    return data
  },

  // Runtime & Events
  listEvents: async (versionId: string, params: { limit?: number }, scope?: ActorType) => {
    const { data } = await apiClient.get(apiPath(`concepts/versions/${versionId}/events`), {
      params: { ...params, ...withScope(scope) },
    })
    return data
  },
  createEvent: async (versionId: string, payload: Record<string, unknown>, scope?: ActorType) => {
    const { data } = await apiClient.post(apiPath(`concepts/versions/${versionId}/events`), payload, {
      params: withScope(scope),
    })
    return data
  },

  // Queue
  listQueue: async (versionId: string, params: { status?: string; limit?: number }, scope?: ActorType) => {
    const { data } = await apiClient.get(apiPath(`concepts/versions/${versionId}/queue`), {
      params: { ...params, ...withScope(scope) },
    })
    return data
  },
  processQueue: async (versionId: string, params: { limit?: number }, scope?: ActorType) => {
    const { data } = await apiClient.post(apiPath(`concepts/versions/${versionId}/queue/process`), {}, {
      params: { ...params, ...withScope(scope) },
    })
    return data
  },

  // Object States
  listObjectStates: async (versionId: string, params: { limit?: number }, scope?: ActorType) => {
    const { data } = await apiClient.get(apiPath(`concepts/versions/${versionId}/object-states`), {
      params: { ...params, ...withScope(scope) },
    })
    return data
  },

  // Simulation
  simulateSequence: async (versionId: string, payload: Record<string, unknown>, scope?: ActorType) => {
    const { data } = await apiClient.post(apiPath(`concepts/versions/${versionId}/simulate`), payload, {
      params: withScope(scope),
    })
    return data
  },
}




