import { useState, useEffect, useRef, useMemo } from 'react'
import { useMutation, useQuery, useQueryClient, useQueries } from '@tanstack/react-query'
import {
  FileText,
  Save,
  RotateCcw,
  GitBranch,
  Check,
  X,
  GitMerge,
  Sparkles,
  RefreshCw,
  Clock,
  User,
  Bot,
  Download,
  Edit3,
  Eye,
  History,
  Loader2,
  FileSpreadsheet,
  Presentation,
  Mail,
  FileJson,
  File,
  BookOpen,
  FileType,
  Code,
  Type,
  FileCode,
  Search,
  Hexagon,
  Image as ImageIcon,
  Video,
  Music,
  Archive,
} from 'lucide-react'
import { toast } from '../utils/toast'
import type { ChatDocument } from '../types/documents'
import {
  fetchChatDocumentContent,
  modifyChatDocument,
  type DocumentContentResponse,
  type DocumentModifyResponse,
} from '../api/documents'
import apiClient, { apiPath } from '../lib/apiClient'
import { QUICK_ACTIONS } from '../constants/documentActions'

type ViewType =
  | 'raw'
  | 'formatted'
  | 'preview'
  | 'markdown'
  | 'code'
  | 'hex'
  | 'pdf'
  | 'image'
  | 'json'
  | 'csv'
type FileSource = 'chat' | 'local' | 'server'

interface UnifiedDocumentViewerProps {
  document?: ChatDocument | null
  persona: string
  onDocumentUpdate?: (updatedDoc: ChatDocument) => void
  onDocumentSelect?: (doc: ChatDocument | null) => void
  className?: string
}

interface FileContentResponse {
  content: string
  path: string
  mtime?: string
}

interface DocumentVersionRow {
  id: string
  version_number: number
  created_at: string
  created_by: string
  change_summary: string
  is_ai_generated: boolean
  confidence_score?: number | null
}

interface DiffResponse {
  from_id: string
  to_id: string
  diff: string
  format: string
}

const fetchFileContent = async (filePath: string): Promise<FileContentResponse> => {
  const { data } = await apiClient.get<FileContentResponse>(
    apiPath(`files/preview?path=${encodeURIComponent(filePath)}`)
  )
  return data
}

const fetchVersions = async (documentId: string): Promise<DocumentVersionRow[]> => {
  const { data } = await apiClient.get<DocumentVersionRow[]>(apiPath(`documents/${documentId}/versions`))
  return data || []
}

const fetchDiff = async (documentId: string, fromId: string, toId: string): Promise<DiffResponse> => {
  const { data } = await apiClient.get<DiffResponse>(
    apiPath(`documents/${documentId}/diff?from_id=${encodeURIComponent(fromId)}&to_id=${encodeURIComponent(toId)}`)
  )
  return data
}

const mergeVersions = async (documentId: string, versionIds: string[], persona: string) => {
  const { data } = await apiClient.post(apiPath(`documents/${documentId}/versions/merge`), {
    version_ids: versionIds,
    persona,
  })
  return data
}

const getFileType = (filename: string, content?: string): 'text' | 'binary' | 'image' | 'video' | 'audio' | 'archive' => {
  const ext = filename.split('.').pop()?.toLowerCase() || ''
  const textExtensions = ['txt', 'md', 'json', 'xml', 'html', 'css', 'js', 'ts', 'tsx', 'jsx', 'py', 'java', 'c', 'cpp', 'h', 'hpp', 'sh', 'yaml', 'yml', 'csv', 'log']
  const imageExtensions = ['jpg', 'jpeg', 'png', 'gif', 'svg', 'webp', 'bmp', 'ico']
  const videoExtensions = ['mp4', 'avi', 'mov', 'wmv', 'flv', 'webm', 'mkv']
  const audioExtensions = ['mp3', 'wav', 'ogg', 'flac', 'aac', 'm4a']
  const archiveExtensions = ['zip', 'tar', 'gz', 'rar', '7z', 'bz2']
  
  if (imageExtensions.includes(ext)) return 'image'
  if (videoExtensions.includes(ext)) return 'video'
  if (audioExtensions.includes(ext)) return 'audio'
  if (archiveExtensions.includes(ext)) return 'archive'
  if (textExtensions.includes(ext)) return 'text'
  
  // Check if content is binary (contains null bytes or high percentage of non-printable chars)
  if (content) {
    const nullBytes = (content.match(/\0/g) || []).length
    const nonPrintable = (content.match(/[\x00-\x08\x0E-\x1F\x7F-\x9F]/g) || []).length
    const total = content.length
    if (nullBytes > 0 || (nonPrintable / total) > 0.1) {
      return 'binary'
    }
  }
  
  return 'text'
}

const formatHex = (data: string): string => {
  const bytes = new Uint8Array(data.length)
  for (let i = 0; i < data.length; i++) {
    bytes[i] = data.charCodeAt(i)
  }
  
  let hex = ''
  for (let i = 0; i < bytes.length; i += 16) {
    const offset = i.toString(16).padStart(8, '0')
    const hexBytes = Array.from(bytes.slice(i, i + 16))
      .map(b => b.toString(16).padStart(2, '0'))
      .join(' ')
    const ascii = Array.from(bytes.slice(i, i + 16))
      .map(b => (b >= 32 && b < 127) ? String.fromCharCode(b) : '.')
      .join('')
    hex += `${offset}  ${hexBytes.padEnd(48, ' ')}  |${ascii}|\n`
  }
  return hex
}

export default function UnifiedDocumentViewer({
  document,
  persona,
  onDocumentUpdate,
  onDocumentSelect,
  className = '',
}: UnifiedDocumentViewerProps) {
  const queryClient = useQueryClient()
  const [viewMode, setViewMode] = useState<'view' | 'edit'>('view')
  const [viewType, setViewType] = useState<ViewType>('formatted')
  const [editedContent, setEditedContent] = useState('')
  const [fileSource, setFileSource] = useState<FileSource>('chat')
  const [localFilePath, setLocalFilePath] = useState<string | null>(null)
  const [localFileContent, setLocalFileContent] = useState<string | null>(null)
  const [serverFilePath, setServerFilePath] = useState<string | null>(null)
  const editorRef = useRef<HTMLTextAreaElement>(null)
  const [showVersions, setShowVersions] = useState(false)
  const [selectedVersionIds, setSelectedVersionIds] = useState<string[]>([])

  // Fetch chat document content
  const { data: currentContent, isLoading: isLoadingContent } = useQuery<DocumentContentResponse>({
    queryKey: ['document-content', document?.id],
    queryFn: () => fetchChatDocumentContent(document!.id),
    enabled: !!document && fileSource === 'chat',
  })

  const { data: versions = [] } = useQuery<DocumentVersionRow[]>({
    queryKey: ['document-versions', document?.id],
    queryFn: () => fetchVersions(document!.id),
    enabled: !!document && fileSource === 'chat',
  })

  // Fetch server file content
  const { data: serverFileContent, isLoading: isLoadingServerFile } = useQuery<FileContentResponse>({
    queryKey: ['file-preview', serverFilePath],
    queryFn: () => fetchFileContent(serverFilePath!),
    enabled: !!serverFilePath && fileSource === 'server',
    refetchInterval: 5000,
  })

  // Determine active file info
  const activeFile = useMemo(() => {
    if (fileSource === 'chat' && document) {
      return {
        name: document.original_name,
        content: currentContent?.content || '',
        type: document.preview_type || 'text',
        category: document.category,
        fileType: document.file_type,
      }
    }
    if (fileSource === 'local' && localFilePath) {
      return {
        name: localFilePath,
        content: localFileContent || '',
        type: getFileType(localFilePath, localFileContent || undefined),
        category: 'local',
        fileType: localFilePath.split('.').pop()?.toLowerCase() || '',
      }
    }
    if (fileSource === 'server' && serverFilePath && serverFileContent) {
      return {
        name: serverFilePath,
        content: serverFileContent.content || '',
        type: getFileType(serverFilePath, serverFileContent.content),
        category: 'server',
        fileType: serverFilePath.split('.').pop()?.toLowerCase() || '',
      }
    }
    return null
  }, [document, currentContent, localFilePath, localFileContent, serverFilePath, serverFileContent, fileSource])

  const isBinary = activeFile?.type === 'binary' || activeFile?.type === 'image' || activeFile?.type === 'video' || activeFile?.type === 'audio' || activeFile?.type === 'archive'
  const canEdit = !isBinary && fileSource === 'chat' && document

  // Update edited content when document changes
  useEffect(() => {
    if (activeFile && viewMode === 'view') {
      setEditedContent(activeFile.content)
    }
  }, [activeFile, viewMode])

  // Set view type based on file type
  useEffect(() => {
    if (activeFile) {
      if (isBinary) {
        if (currentContent?.content_type === 'application/pdf') {
          setViewType('pdf')
        } else if (currentContent?.content_type?.startsWith('image/')) {
          setViewType('image')
        } else {
          setViewType('hex')
        }
        setViewMode('view')
      } else if (activeFile.fileType === 'md' || activeFile.fileType === 'markdown') {
        setViewType('markdown')
      } else if (activeFile.fileType === 'json') {
        setViewType('json')
      } else if (activeFile.fileType === 'csv' || activeFile.fileType === 'tsv') {
        setViewType('csv')
      } else if (['js', 'ts', 'jsx', 'tsx', 'py', 'java', 'c', 'cpp', 'html', 'css', 'json', 'xml'].includes(activeFile.fileType)) {
        setViewType('code')
      } else {
        setViewType('formatted')
      }
    }
  }, [activeFile, isBinary, currentContent?.content_type])

  const handleChooseLocalFile = () => {
    const input = document.createElement('input')
    input.type = 'file'
    input.style.display = 'none'
    input.onchange = async (e) => {
      const file = (e.target as HTMLInputElement).files?.[0]
      if (!file) {
        document.body.removeChild(input)
        return
      }

      const reader = new FileReader()
      reader.onload = (event) => {
        const content = event.target?.result as string
        setLocalFilePath(file.name)
        setLocalFileContent(content)
        setFileSource('local')
        toast.info(`Loaded local file: ${file.name}`)
      }
      reader.onerror = () => {
        toast.error('Failed to read file')
        document.body.removeChild(input)
      }
      reader.readAsText(file)
    }
    document.body.appendChild(input)
    input.click()
  }

  const handleChooseServerFile = () => {
    const path = prompt('Enter file path to preview:')
    if (path) {
      setServerFilePath(path)
      setFileSource('server')
    }
  }

  const saveMutation = useMutation({
    mutationFn: async () => {
      if (!document || !canEdit) throw new Error('No editable document selected')
      const { data } = await apiClient.put(apiPath(`documents/${document.id}/content`), { content: editedContent, persona })
      return data as DocumentModifyResponse
    },
    onSuccess: (response: DocumentModifyResponse) => {
      toast.success('Document saved successfully')
      if (onDocumentUpdate && document) {
        onDocumentUpdate({ ...document, content_preview: response.modified_content ?? document.content_preview })
      }
      queryClient.invalidateQueries({ queryKey: ['document-content', document?.id] })
      queryClient.invalidateQueries({ queryKey: ['document-versions', document?.id] })
      queryClient.invalidateQueries({ queryKey: ['chat-documents'] })
      setViewMode('view')
    },
    onError: (error) => {
      toast.error(`Failed to save: ${error instanceof Error ? error.message : 'Unknown error'}`)
    },
  })

  const handleSave = () => {
    if (!document || !canEdit) return
    saveMutation.mutate()
  }

  const displayContent = viewMode === 'edit' ? editedContent : activeFile?.content || ''

  // View type options based on file type
  const viewTypeOptions = useMemo(() => {
    if (!activeFile) return []
    if (isBinary) {
      const options = [
        ...(currentContent?.content_type === 'application/pdf'
          ? [{ type: 'pdf' as ViewType, label: 'PDF', icon: FileType }]
          : []),
        ...(currentContent?.content_type?.startsWith('image/')
          ? [{ type: 'image' as ViewType, label: 'Image', icon: ImageIcon }]
          : []),
        { type: 'hex' as ViewType, label: 'Hex View', icon: Hexagon },
        { type: 'preview' as ViewType, label: 'Info', icon: Eye },
      ]
      return options
    }
    const options = [
      { type: 'formatted' as ViewType, label: 'Formatted', icon: Type },
      { type: 'raw' as ViewType, label: 'Raw', icon: FileCode },
    ]
    if (activeFile.fileType === 'md' || activeFile.fileType === 'markdown') {
      options.push({ type: 'markdown' as ViewType, label: 'Markdown', icon: FileText })
    }
    if (activeFile.fileType === 'json') {
      options.push({ type: 'json' as ViewType, label: 'JSON', icon: FileJson })
    }
    if (activeFile.fileType === 'csv' || activeFile.fileType === 'tsv') {
      options.push({ type: 'csv' as ViewType, label: activeFile.fileType.toUpperCase(), icon: FileSpreadsheet })
    }
    if (['js', 'ts', 'jsx', 'tsx', 'py', 'java', 'c', 'cpp', 'html', 'css', 'json', 'xml'].includes(activeFile.fileType)) {
      options.push({ type: 'code' as ViewType, label: 'Code', icon: Code })
    }
    return options
  }, [activeFile, isBinary, currentContent?.content_type])

  const diffs = useQueries({
    queries: (selectedVersionIds || []).map((fromId) => ({
      queryKey: ['document-diff', document?.id, fromId],
      queryFn: () => fetchDiff(document!.id, fromId, 'current'),
      enabled: !!document && fileSource === 'chat' && !!fromId,
      staleTime: 10_000,
    })),
  })

  const mergeMutation = useMutation({
    mutationFn: async () => {
      if (!document) throw new Error('No document selected')
      if (!selectedVersionIds.length) throw new Error('Select versions to merge')
      return mergeVersions(document.id, selectedVersionIds, persona)
    },
    onSuccess: async () => {
      toast.success('Merged into current')
      setSelectedVersionIds([])
      queryClient.invalidateQueries({ queryKey: ['document-content', document?.id] })
      queryClient.invalidateQueries({ queryKey: ['document-versions', document?.id] })
      queryClient.invalidateQueries({ queryKey: ['chat-documents'] })
    },
    onError: (err: any) => {
      toast.error(err?.response?.data?.detail || err?.message || 'Merge failed')
    },
  })

  if (!activeFile && !document) {
    return (
      <div className={`flex flex-col h-full bg-slate-900/50 ${className}`}>
        <div className="p-6 border-b border-slate-700/50">
          <div className="flex items-center gap-2.5 mb-3">
            <div className="p-1.5 rounded-lg bg-gradient-to-br from-primary-500/20 to-violet-500/20 border border-primary-500/30">
              <FileText className="w-4 h-4 text-primary-400" />
            </div>
            <div>
              <h4 className="text-sm font-semibold text-slate-200">Document Viewer</h4>
              <p className="text-xs text-slate-500">Select a document or file to view</p>
            </div>
          </div>
        </div>
        <div className="flex-1 flex items-center justify-center p-6">
          <div className="text-center max-w-sm">
            <div className="w-20 h-20 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-primary-500/20 to-violet-500/20 flex items-center justify-center border border-primary-500/30">
              <FileText className="w-10 h-10 text-primary-400" />
            </div>
            <h3 className="text-lg font-semibold text-white mb-2">No Document Selected</h3>
            <p className="text-sm text-slate-400 mb-6">
              Select a document from the workspace or choose a file to preview
            </p>
            <div className="flex gap-3 justify-center">
              <button
                onClick={handleChooseLocalFile}
                className="px-4 py-2 bg-slate-800/80 hover:bg-slate-700 border border-slate-700/60 rounded-lg text-sm text-slate-300 transition-colors"
              >
                <Search className="w-4 h-4 inline mr-2" />
                Choose Local File
              </button>
              <button
                onClick={handleChooseServerFile}
                className="px-4 py-2 bg-primary-500/20 hover:bg-primary-500/30 border border-primary-500/30 rounded-lg text-sm text-primary-300 transition-colors"
              >
                <FileText className="w-4 h-4 inline mr-2" />
                Choose Server File
              </button>
            </div>
          </div>
        </div>
      </div>
    )
  }

  const isLoading = isLoadingContent || isLoadingServerFile

  const binaryDataUrl =
    fileSource === 'chat' && currentContent?.encoding === 'base64'
      ? `data:${currentContent.content_type};base64,${currentContent.content}`
      : null

  const formattedJson = useMemo(() => {
    if (!activeFile || viewType !== 'json') return null
    try {
      return JSON.stringify(JSON.parse(activeFile.content || '{}'), null, 2)
    } catch {
      return activeFile.content
    }
  }, [activeFile, viewType])

  const csvTable = useMemo(() => {
    if (!activeFile || viewType !== 'csv') return null
    const sep = activeFile.fileType === 'tsv' ? '\t' : ','
    const lines = (activeFile.content || '').split(/\r?\n/).filter(Boolean)
    const rows = lines.slice(0, 200).map((l) => l.split(sep))
    const header = rows[0] || []
    const body = rows.slice(1)
    return { header, body }
  }, [activeFile, viewType])

  return (
    <div className={`flex flex-col h-full bg-slate-900/50 ${className}`}>
      {/* Header */}
      <div className="p-4 border-b border-slate-700/50 bg-gradient-to-r from-slate-900/95 to-slate-800/95 backdrop-blur-sm">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2.5 flex-1 min-w-0">
            <div className="p-1.5 rounded-lg bg-gradient-to-br from-primary-500/20 to-violet-500/20 border border-primary-500/30">
              <FileText className="w-4 h-4 text-primary-400" />
            </div>
            <div className="flex-1 min-w-0">
              <h4 className="text-sm font-semibold text-slate-200 truncate">
                {activeFile?.name || 'Document Viewer'}
              </h4>
              <div className="flex items-center gap-2 mt-0.5">
                <span className="text-[10px] text-slate-500">
                  {fileSource === 'chat' ? 'Chat Document' : fileSource === 'local' ? 'Local File' : 'Server File'}
                </span>
                {activeFile && (
                  <>
                    <span className="text-[10px] text-slate-600">•</span>
                    <span className="text-[10px] text-slate-500">{activeFile.fileType?.toUpperCase() || 'UNKNOWN'}</span>
                    {isBinary && (
                      <>
                        <span className="text-[10px] text-slate-600">•</span>
                        <span className="text-[10px] text-amber-500">Binary</span>
                      </>
                    )}
                  </>
                )}
              </div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {fileSource === 'chat' && document && (
              <>
                <button
                  onClick={() => setShowVersions((v) => !v)}
                  className={`p-2 rounded-lg transition-all ${
                    showVersions
                      ? 'bg-primary-500/20 text-primary-300 border border-primary-500/30'
                      : 'bg-slate-800/50 text-slate-400 hover:bg-slate-700/50'
                  }`}
                  title="Version control"
                >
                  <History className="w-4 h-4" />
                </button>
                <button
                  onClick={() => setViewMode('view')}
                  className={`p-2 rounded-lg transition-all ${
                    viewMode === 'view'
                      ? 'bg-primary-500/20 text-primary-300 border border-primary-500/30'
                      : 'bg-slate-800/50 text-slate-400 hover:bg-slate-700/50'
                  }`}
                  title="View mode"
                >
                  <Eye className="w-4 h-4" />
                </button>
                {canEdit && (
                  <button
                    onClick={() => {
                      setViewMode('edit')
                      setTimeout(() => editorRef.current?.focus(), 100)
                    }}
                    className={`p-2 rounded-lg transition-all ${
                      viewMode === 'edit'
                        ? 'bg-primary-500/20 text-primary-300 border border-primary-500/30'
                        : 'bg-slate-800/50 text-slate-400 hover:bg-slate-700/50'
                    }`}
                    title="Edit mode"
                  >
                    <Edit3 className="w-4 h-4" />
                  </button>
                )}
              </>
            )}
            {(fileSource === 'local' || fileSource === 'server') && (
              <button
                onClick={fileSource === 'local' ? handleChooseLocalFile : handleChooseServerFile}
                className="p-2 bg-slate-800/50 text-slate-400 hover:bg-slate-700/50 rounded-lg transition-all"
                title="Choose another file"
              >
                <Search className="w-4 h-4" />
              </button>
            )}
            {fileSource === 'server' && (
              <button
                onClick={() => {
                  // Refetch server file
                  window.location.reload()
                }}
                className="p-2 bg-slate-800/50 text-slate-400 hover:bg-slate-700/50 rounded-lg transition-all"
                title="Refresh"
              >
                <RefreshCw className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>

        {/* View Type Selector */}
        {viewMode === 'view' && viewTypeOptions.length > 0 && (
          <div className="flex items-center gap-2">
            {viewTypeOptions.map((option) => {
              const Icon = option.icon
              return (
                <button
                  key={option.type}
                  onClick={() => setViewType(option.type)}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                    viewType === option.type
                      ? 'bg-primary-500/20 text-primary-300 border border-primary-500/30'
                      : 'bg-slate-800/50 text-slate-400 hover:bg-slate-700/50 border border-transparent'
                  }`}
                >
                  <Icon className="w-3.5 h-3.5" />
                  {option.label}
                </button>
              )
            })}
          </div>
        )}

        {/* Save/Cancel buttons for edit mode */}
        {viewMode === 'edit' && canEdit && (
          <div className="flex items-center gap-2 mt-3">
            <button
              onClick={handleSave}
              disabled={saveMutation.isPending}
              className="flex items-center gap-2 px-4 py-2 bg-primary-500/20 hover:bg-primary-500/30 border border-primary-500/30 rounded-lg text-sm font-medium text-primary-300 transition-all disabled:opacity-50"
            >
              {saveMutation.isPending ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Save className="w-4 h-4" />
              )}
              Save
            </button>
            <button
              onClick={() => {
                setEditedContent(activeFile?.content || '')
                setViewMode('view')
              }}
              className="px-4 py-2 bg-slate-800/50 hover:bg-slate-700/50 border border-slate-700/50 rounded-lg text-sm font-medium text-slate-300 transition-all"
            >
              Cancel
            </button>
          </div>
        )}
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-y-auto p-6 relative">
        {isLoading ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <Loader2 className="w-8 h-8 text-primary-400 animate-spin mx-auto mb-3" />
              <p className="text-sm text-slate-400">Loading document...</p>
            </div>
          </div>
        ) : viewMode === 'edit' ? (
          <textarea
            ref={editorRef}
            value={editedContent}
            onChange={(e) => setEditedContent(e.target.value)}
            className="w-full h-full bg-slate-900/60 border border-slate-700/60 rounded-xl p-6 text-sm text-slate-100 font-mono resize-none focus:outline-none focus:ring-2 focus:ring-primary-500/50 leading-relaxed"
            placeholder="Start editing your document..."
          />
        ) : (
          <div className="max-w-4xl mx-auto">
            {viewType === 'raw' && (
              <div className="bg-slate-900/60 border border-slate-700/60 rounded-xl p-8 text-sm text-slate-200 whitespace-pre-wrap font-mono leading-relaxed overflow-x-auto">
                {displayContent || 'No content available'}
              </div>
            )}
            {viewType === 'json' && (
              <div className="bg-slate-900/60 border border-slate-700/60 rounded-xl p-8 text-sm text-slate-200 font-mono">
                <pre className="whitespace-pre-wrap leading-relaxed overflow-x-auto">
                  {formattedJson || 'No content available'}
                </pre>
              </div>
            )}
            {viewType === 'csv' && csvTable && (
              <div className="bg-slate-900/60 border border-slate-700/60 rounded-xl p-6 overflow-x-auto">
                <table className="min-w-full text-xs text-slate-200">
                  <thead className="text-slate-300">
                    <tr>
                      {csvTable.header.map((h, idx) => (
                        <th key={idx} className="text-left font-semibold pb-2 pr-4 whitespace-nowrap">
                          {h}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="text-slate-200">
                    {csvTable.body.map((row, rIdx) => (
                      <tr key={rIdx} className="border-t border-white/5">
                        {row.map((cell, cIdx) => (
                          <td key={cIdx} className="py-2 pr-4 whitespace-nowrap">
                            {cell}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
                <p className="mt-3 text-[11px] text-slate-500">Showing up to 200 rows.</p>
              </div>
            )}
            {viewType === 'formatted' && (
              <div className="bg-slate-900/60 border border-slate-700/60 rounded-xl p-8 text-base text-slate-100 leading-relaxed whitespace-pre-wrap">
                {displayContent || 'No content available'}
              </div>
            )}
            {viewType === 'markdown' && (
              <div className="bg-slate-900/60 border border-slate-700/60 rounded-xl p-8 prose prose-invert prose-slate max-w-none">
                <div className="markdown-content">
                  {displayContent.split('\n').map((line, idx) => {
                    const trimmed = line.trim()
                    if (trimmed.startsWith('# ')) {
                      return <h1 key={idx} className="text-3xl font-bold mt-6 mb-4 text-slate-100">{trimmed.slice(2)}</h1>
                    }
                    if (trimmed.startsWith('## ')) {
                      return <h2 key={idx} className="text-2xl font-bold mt-5 mb-3 text-slate-100">{trimmed.slice(3)}</h2>
                    }
                    if (trimmed.startsWith('### ')) {
                      return <h3 key={idx} className="text-xl font-semibold mt-4 mb-2 text-slate-200">{trimmed.slice(4)}</h3>
                    }
                    if (trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
                      return <li key={idx} className="ml-6 list-disc mb-1 text-slate-200">{trimmed.slice(2)}</li>
                    }
                    if (trimmed.startsWith('1. ') || /^\d+\.\s/.test(trimmed)) {
                      return <li key={idx} className="ml-6 list-decimal mb-1 text-slate-200">{trimmed.replace(/^\d+\.\s/, '')}</li>
                    }
                    if (trimmed === '') {
                      return <div key={idx} className="h-2" />
                    }
                    return <p key={idx} className="mb-3 text-slate-200 leading-relaxed">{line}</p>
                  })}
                </div>
              </div>
            )}
            {viewType === 'code' && (
              <div className="bg-slate-900/60 border border-slate-700/60 rounded-xl p-8 text-sm text-slate-200 font-mono">
                <pre className="whitespace-pre-wrap leading-relaxed overflow-x-auto">{displayContent || 'No content available'}</pre>
              </div>
            )}
            {viewType === 'hex' && isBinary && (
              <div className="bg-slate-900/60 border border-slate-700/60 rounded-xl p-8">
                <div className="mb-4 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Hexagon className="w-5 h-5 text-primary-400" />
                    <h3 className="text-sm font-semibold text-slate-200">Hexadecimal View</h3>
                  </div>
                  {fileSource === 'chat' && document && (
                    <a
                      href={apiPath(`documents/${document.id}/content`)}
                      download={document.original_name}
                      className="flex items-center gap-2 px-4 py-2 bg-primary-500/20 hover:bg-primary-500/30 border border-primary-500/30 rounded-lg text-sm text-primary-300 transition-colors"
                    >
                      <Download className="w-4 h-4" />
                      Download
                    </a>
                  )}
                </div>
                <div className="bg-slate-950/50 border border-slate-800/50 rounded-lg p-4 overflow-x-auto">
                  <pre className="text-xs text-slate-300 font-mono leading-relaxed">
                    {formatHex(displayContent)}
                  </pre>
                </div>
              </div>
            )}
            {viewType === 'pdf' && binaryDataUrl && (
              <div className="bg-slate-900/60 border border-slate-700/60 rounded-xl overflow-hidden">
                <iframe src={binaryDataUrl} title="PDF Viewer" className="w-full h-[70vh]" />
              </div>
            )}
            {viewType === 'image' && binaryDataUrl && (
              <div className="bg-slate-900/60 border border-slate-700/60 rounded-xl p-6">
                <img src={binaryDataUrl} alt={activeFile?.name || 'image'} className="w-full max-h-[70vh] object-contain" />
              </div>
            )}
            {viewType === 'preview' && isBinary && (
              <div className="bg-slate-900/60 border border-slate-700/60 rounded-xl p-8">
                <div className="text-center py-12 space-y-4">
                  <div className="w-16 h-16 mx-auto rounded-xl bg-slate-800/50 flex items-center justify-center">
                    {activeFile?.type === 'image' && <ImageIcon className="w-8 h-8 text-slate-500" />}
                    {activeFile?.type === 'video' && <Video className="w-8 h-8 text-slate-500" />}
                    {activeFile?.type === 'audio' && <Music className="w-8 h-8 text-slate-500" />}
                    {activeFile?.type === 'archive' && <Archive className="w-8 h-8 text-slate-500" />}
                    {!['image', 'video', 'audio', 'archive'].includes(activeFile?.type || '') && (
                      <FileType className="w-8 h-8 text-slate-500" />
                    )}
                  </div>
                  <div>
                    <p className="text-sm font-medium text-slate-300 mb-2">
                      {activeFile?.type === 'image' && 'Image File'}
                      {activeFile?.type === 'video' && 'Video File'}
                      {activeFile?.type === 'audio' && 'Audio File'}
                      {activeFile?.type === 'archive' && 'Archive File'}
                      {!['image', 'video', 'audio', 'archive'].includes(activeFile?.type || '') && 'Binary File'}
                    </p>
                    <p className="text-xs text-slate-500 mb-4">
                      This file type cannot be previewed in the browser.
                    </p>
                    {fileSource === 'chat' && document && (
                      <a
                        href={apiPath(`documents/${document.id}/content`)}
                        download={document.original_name}
                        className="inline-flex items-center gap-2 px-4 py-2 bg-primary-500/20 hover:bg-primary-500/30 border border-primary-500/30 rounded-lg text-sm text-primary-300 transition-colors"
                      >
                        <Download className="w-4 h-4" />
                        Download to View
                      </a>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Hidden version control drawer */}
        {showVersions && fileSource === 'chat' && document && (
          <div className="absolute inset-y-0 right-0 w-[420px] bg-slate-950/95 border-l border-slate-700/50 backdrop-blur-xl shadow-2xl overflow-hidden">
            <div className="p-4 border-b border-slate-700/50 flex items-center justify-between">
              <div>
                <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Version Control</p>
                <p className="text-sm text-slate-200">{versions.length} snapshot(s)</p>
              </div>
              <button
                onClick={() => setShowVersions(false)}
                className="p-2 rounded-lg bg-slate-800/50 text-slate-300 hover:bg-slate-700/50"
                title="Close"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="p-4 border-b border-slate-700/50">
              <button
                disabled={!selectedVersionIds.length || mergeMutation.isPending}
                onClick={() => mergeMutation.mutate()}
                className="w-full flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-violet-500/20 border border-violet-500/30 text-violet-200 disabled:opacity-50"
              >
                <GitMerge className="w-4 h-4" />
                {mergeMutation.isPending ? 'Merging…' : 'Merge selected into current'}
              </button>
              <p className="mt-2 text-[11px] text-slate-500">
                Select multiple versions to stack diffs and merge unique lines into the current document.
              </p>
            </div>

            <div className="p-4 overflow-y-auto h-full space-y-3">
              {versions.length === 0 ? (
                <div className="text-sm text-slate-400">No snapshots yet. Save or run an AI edit to create one.</div>
              ) : (
                versions.map((v) => {
                  const checked = selectedVersionIds.includes(v.id)
                  return (
                    <label
                      key={v.id}
                      className={`block rounded-xl border p-3 cursor-pointer transition ${
                        checked ? 'border-primary-500/60 bg-primary-500/10' : 'border-white/10 bg-white/5 hover:border-white/25'
                      }`}
                    >
                      <div className="flex items-start justify-between gap-3">
                        <div className="flex items-start gap-3">
                          <input
                            type="checkbox"
                            checked={checked}
                            onChange={() => {
                              setSelectedVersionIds((prev) =>
                                prev.includes(v.id) ? prev.filter((id) => id !== v.id) : [v.id, ...prev]
                              )
                            }}
                            className="mt-1"
                          />
                          <div>
                            <p className="text-sm font-semibold text-slate-100">v{v.version_number}</p>
                            <p className="text-xs text-slate-400">
                              {new Date(v.created_at).toLocaleString()} · {v.created_by}
                            </p>
                            <p className="text-xs text-slate-300 mt-1">{v.change_summary}</p>
                          </div>
                        </div>
                      </div>
                    </label>
                  )
                })
              )}

              {selectedVersionIds.length > 0 && (
                <div className="pt-2 space-y-3">
                  <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Stacked diffs</p>
                  {diffs.map((q, idx) => {
                    const fromId = selectedVersionIds[idx]
                    const diffText = (q.data as any)?.diff as string | undefined
                    return (
                      <div key={fromId} className="rounded-xl border border-white/10 bg-black/20 p-3">
                        <p className="text-xs text-slate-300 font-semibold mb-2">Diff: {fromId} → current</p>
                        {q.isLoading ? (
                          <div className="text-xs text-slate-400">Loading diff…</div>
                        ) : q.isError ? (
                          <div className="text-xs text-rose-300">Failed to load diff.</div>
                        ) : (
                          <pre className="text-[11px] text-slate-200 whitespace-pre-wrap font-mono max-h-64 overflow-y-auto">
                            {diffText || '(empty diff)'}
                          </pre>
                        )}
                      </div>
                    )
                  })}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}








