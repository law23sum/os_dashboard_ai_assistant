import apiClient, { apiPath } from '../lib/apiClient'

export type FilesystemPolicy = {
  allowed_roots: string[]
  mode: 'read_only' | 'read_write'
}

export type DirectoryItem = {
  path: string
  name: string
  type: 'file' | 'directory'
  size?: number | null
  modified?: string | null
  is_hidden?: boolean
}

export type DirectoryListing = {
  path: string
  items: DirectoryItem[]
  total_items: number
}

export type FilePreview = {
  path: string
  content: string
  truncated: boolean
}

export const getFilesystemPolicy = async (): Promise<FilesystemPolicy> => {
  const { data } = await apiClient.get<FilesystemPolicy>(apiPath('filesystem/policy'))
  return data
}

export const updateFilesystemPolicy = async (
  payload: Partial<FilesystemPolicy>,
): Promise<FilesystemPolicy> => {
  const { data } = await apiClient.put<FilesystemPolicy>(apiPath('filesystem/policy'), payload)
  return data
}

export const listDirectory = async (payload: {
  path: string
  show_hidden?: boolean
  include_metadata?: boolean
  max_items?: number
}): Promise<DirectoryListing> => {
  const { data } = await apiClient.post<DirectoryListing>(apiPath('filesystem/list'), payload)
  return data
}

export const getFileInfo = async (path: string): Promise<Record<string, unknown>> => {
  const { data } = await apiClient.get<Record<string, unknown>>(apiPath('filesystem/info'), {
    params: { path },
  })
  return data
}

export const readFile = async (path: string, maxBytes = 2048): Promise<FilePreview> => {
  const { data } = await apiClient.get<FilePreview>(apiPath('filesystem/read'), {
    params: { path, max_bytes: maxBytes },
  })
  return data
}
