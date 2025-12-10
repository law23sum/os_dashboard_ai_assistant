import apiClient, { apiPath } from '../lib/apiClient'
import type { Settings } from '../types'

export const fetchSettings = async (): Promise<Settings> => {
  const { data } = await apiClient.get<Settings>(apiPath('settings'))
  return data
}

export const updateSettings = async (
  payload: Partial<Settings>,
): Promise<Settings> => {
  const { data } = await apiClient.put<Settings>(apiPath('settings'), payload)
  return data
}
