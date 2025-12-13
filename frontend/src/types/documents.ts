export interface ChatDocument {
  id: string
  filename: string
  original_name: string
  file_type: string
  category: string
  size_bytes: number
  preview_type: string
  uploaded_at: string
  content_preview?: string
  metadata: Record<string, any>
}
