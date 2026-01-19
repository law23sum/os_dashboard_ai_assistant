import apiClient, { apiPath } from '../lib/apiClient'

export type AgentJournalStats = {
  agents: Record<string, { total: number; last_timestamp?: string | null }>
  team?: { total?: number; last_timestamp?: string | null }
  totals?: { team_interactions?: number }
}

export type AgentJournalEvent = {
  entry_hash?: string
  agent_id?: string
  event_type: string
  summary?: string
  timestamp_utc?: string
}

export type AgentJournalEventParams = {
  agent_id?: string
  event_type?: string
  limit?: number
  include_sensitive?: boolean
}

export type AgentJournalTeamParams = {
  event_type?: string
  limit?: number
  include_sensitive?: boolean
}

export const agentJournalApi = {
  getStats: async (include_sensitive?: boolean): Promise<AgentJournalStats> => {
    const { data } = await apiClient.get<AgentJournalStats>(apiPath('agent-journal/stats'), {
      params: include_sensitive ? { include_sensitive } : undefined,
    })
    return data
  },
  listEvents: async (params: AgentJournalEventParams): Promise<AgentJournalEvent[]> => {
    const { data } = await apiClient.get<AgentJournalEvent[]>(apiPath('agent-journal/events'), { params })
    return data
  },
  listTeamEvents: async (params: AgentJournalTeamParams): Promise<AgentJournalEvent[]> => {
    const { data } = await apiClient.get<AgentJournalEvent[]>(apiPath('agent-journal/team'), { params })
    return data
  },
}
