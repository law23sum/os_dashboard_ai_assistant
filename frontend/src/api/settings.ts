import apiClient, { apiPath } from '../lib/apiClient'
import type { Settings } from '../types'

export type StorageStatus = {
  data_dir: string
  db_path: string
  db_exists: boolean
  db_size_bytes: number
  db_last_modified?: string | null
  project_count: number
  task_count: number
}

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

export const fetchStorageStatus = async (): Promise<StorageStatus> => {
  const { data } = await apiClient.get<StorageStatus>(apiPath('settings/storage'))
  return data
}
