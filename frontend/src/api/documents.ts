import type { ChatDocument } from '../types/documents'
import apiClient, { apiPath } from '../lib/apiClient'

export interface DocumentModifyResponse {
  document_id: string
  success: boolean
  modified_content?: string
  changes_summary: string
  new_version_id?: string
}

export interface DocumentContentResponse {
  document_id: string
  filename: string
  content_type: string
  content: string
  encoding: string
}

export const listChatDocuments = async (): Promise<ChatDocument[]> => {
  const { data } = await apiClient.get<ChatDocument[]>(apiPath('documents/'))
  return data
}

export const uploadChatDocument = async (file: File, persona: string): Promise<ChatDocument> => {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('persona', persona)
  const { data } = await apiClient.post<ChatDocument>(apiPath('documents/upload'), formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}

export const modifyChatDocument = async (params: {
  documentId: string
  prompt: string
  persona: string
}): Promise<DocumentModifyResponse> => {
  const { data } = await apiClient.post<DocumentModifyResponse>(
    apiPath(`documents/${params.documentId}/modify`),
    { document_id: params.documentId, prompt: params.prompt, persona: params.persona }
  )
  return data
}

export const deleteChatDocument = async (documentId: string): Promise<void> => {
  await apiClient.delete(apiPath(`documents/${documentId}`))
}

export const fetchChatDocumentContent = async (
  documentId: string
): Promise<DocumentContentResponse> => {
  const { data } = await apiClient.get<DocumentContentResponse>(
    apiPath(`documents/${documentId}/content`)
  )
  return data
}
