import apiClient, { apiPath } from '../lib/apiClient'

export interface VectorStore {
  id: string
  name: string
  created_at?: number
  file_counts?: {
    in_progress?: number
    completed?: number
    failed?: number
    cancelled?: number
    total?: number
  }
  usage_bytes?: number
  expires_after?: {
    anchor: string
    days: number
  }
}

export interface FileUploadResponse {
  file_id: string
  filename: string
  purpose: string
  bytes: number
}

export interface VectorStoreFile {
  id: string
  file_id: string
  created_at?: number
  status?: string
}

export interface SearchResult {
  file_id: string
  score?: number
  content?: string
}

export interface SearchResponse {
  results: SearchResult[]
}

export interface BatchUploadRequest {
  file_ids?: string[]
  files?: Array<{
    file_id: string
    attributes?: Record<string, any>
    chunking_strategy?: {
      type: string
      max_chunk_size_tokens: number
      chunk_overlap_tokens: number
    }
  }>
  chunking_strategy?: {
    type: string
    max_chunk_size_tokens: number
    chunk_overlap_tokens: number
  }
}

export interface BatchUploadResponse {
  id: string
  vector_store_id: string
  status: string
  file_counts?: Record<string, number>
  created_at?: number
  expires_at?: number
}

// Upload a file to OpenAI
export const uploadFile = async (file: File, purpose: string = 'assistants'): Promise<FileUploadResponse> => {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('purpose', purpose)
  
  const { data } = await apiClient.post<FileUploadResponse>(
    apiPath('vector-stores/upload'),
    formData,
    {
      headers: { 'Content-Type': 'multipart/form-data' },
    }
  )
  return data
}

// Create a new vector store
export const createVectorStore = async (params: {
  name: string
  file_ids?: string[]
  expires_after_days?: number
}): Promise<VectorStore> => {
  const { data } = await apiClient.post<VectorStore>(
    apiPath('vector-stores/'),
    params
  )
  return data
}

// List all vector stores
export const listVectorStores = async (params?: {
  limit?: number
  order?: 'asc' | 'desc'
}): Promise<VectorStore[]> => {
  const queryParams = new URLSearchParams()
  if (params?.limit) queryParams.append('limit', params.limit.toString())
  if (params?.order) queryParams.append('order', params.order)
  
  const { data } = await apiClient.get<VectorStore[]>(
    apiPath(`vector-stores/?${queryParams.toString()}`)
  )
  return data
}

// Get vector store details
export const getVectorStore = async (vectorStoreId: string): Promise<VectorStore> => {
  const { data } = await apiClient.get<VectorStore>(
    apiPath(`vector-stores/${vectorStoreId}`)
  )
  return data
}

// Update vector store
export const updateVectorStore = async (
  vectorStoreId: string,
  params: {
    name?: string
    expires_after_days?: number
  }
): Promise<VectorStore> => {
  const { data } = await apiClient.put<VectorStore>(
    apiPath(`vector-stores/${vectorStoreId}`),
    params
  )
  return data
}

// Delete vector store
export const deleteVectorStore = async (vectorStoreId: string): Promise<void> => {
  await apiClient.delete(apiPath(`vector-stores/${vectorStoreId}`))
}

// Add files to vector store
export const addFilesToVectorStore = async (
  vectorStoreId: string,
  params: {
    file_ids: string[]
    max_chunk_size?: number
    chunk_overlap?: number
  }
): Promise<{ results: VectorStoreFile[]; count: number }> => {
  const { data } = await apiClient.post<{ results: VectorStoreFile[]; count: number }>(
    apiPath(`vector-stores/${vectorStoreId}/files`),
    params
  )
  return data
}

// Batch add files to vector store
export const batchAddFiles = async (
  vectorStoreId: string,
  request: BatchUploadRequest
): Promise<BatchUploadResponse> => {
  const { data } = await apiClient.post<BatchUploadResponse>(
    apiPath(`vector-stores/${vectorStoreId}/files/batch`),
    request
  )
  return data
}

// List files in vector store
export const listVectorStoreFiles = async (
  vectorStoreId: string,
  params?: {
    limit?: number
    order?: 'asc' | 'desc'
  }
): Promise<VectorStoreFile[]> => {
  const queryParams = new URLSearchParams()
  if (params?.limit) queryParams.append('limit', params.limit.toString())
  if (params?.order) queryParams.append('order', params.order)
  
  const { data } = await apiClient.get<VectorStoreFile[]>(
    apiPath(`vector-stores/${vectorStoreId}/files?${queryParams.toString()}`)
  )
  return data
}

// Get file details in vector store
export const getVectorStoreFile = async (
  vectorStoreId: string,
  fileId: string
): Promise<VectorStoreFile> => {
  const { data } = await apiClient.get<VectorStoreFile>(
    apiPath(`vector-stores/${vectorStoreId}/files/${fileId}`)
  )
  return data
}

// Delete file from vector store
export const deleteVectorStoreFile = async (
  vectorStoreId: string,
  fileId: string
): Promise<void> => {
  await apiClient.delete(apiPath(`vector-stores/${vectorStoreId}/files/${fileId}`))
}

// Search vector store
export const searchVectorStore = async (
  vectorStoreId: string,
  query: string,
  limit: number = 10
): Promise<SearchResponse> => {
  const { data } = await apiClient.post<SearchResponse>(
    apiPath(`vector-stores/${vectorStoreId}/search`),
    { query, limit }
  )
  return data
}

// Get batch status
export const getFileBatch = async (
  vectorStoreId: string,
  batchId: string
): Promise<BatchUploadResponse> => {
  const { data } = await apiClient.get<BatchUploadResponse>(
    apiPath(`vector-stores/${vectorStoreId}/batches/${batchId}`)
  )
  return data
}

