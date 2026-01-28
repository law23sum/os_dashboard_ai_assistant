import { useState, useRef, useCallback, useEffect, useMemo } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import {
  Upload,
  FileText,
  FileSpreadsheet,
  Presentation,
  Mail,
  FileJson,
  File,
  RefreshCw,
  Sparkles,
  Trash2,
  Loader2,
  BookOpen,
  Clock,
  FileType,
  Code,
  Target,
  Search,
  Filter,
  Download,
  RotateCcw,
} from 'lucide-react'
import { toast } from '../utils/toast'
import { apiPath } from '../lib/apiClient'
import type { ChatDocument } from '../types/documents'
import {
  listChatDocuments,
  uploadChatDocument,
  modifyChatDocument,
  deleteChatDocument,
  fetchChatDocumentContent,
  type DocumentModifyResponse,
  type DocumentContentResponse,
} from '../api/documents'
import { QUICK_ACTIONS } from '../constants/documentActions'

const getCategoryIcon = (category: string) => {
  switch (category) {
    case 'word':
    case 'text':
    case 'markdown':
    case 'richtext':
      return FileText
    case 'excel':
    case 'csv':
      return FileSpreadsheet
    case 'powerpoint':
      return Presentation
    case 'email':
      return Mail
    case 'json':
    case 'xml':
      return FileJson
    case 'pdf':
      return FileType
    case 'html':
      return Code
    case 'onenote':
      return BookOpen
    default:
      return File
  }
}

const getCategoryColor = (category: string) => {
  switch (category) {
    case 'word':
      return 'text-blue-400 bg-blue-500/10'
    case 'excel':
    case 'csv':
      return 'text-emerald-400 bg-emerald-500/10'
    case 'powerpoint':
      return 'text-orange-400 bg-orange-500/10'
    case 'pdf':
      return 'text-rose-400 bg-rose-500/10'
    case 'email':
      return 'text-purple-400 bg-purple-500/10'
    case 'json':
    case 'xml':
      return 'text-amber-400 bg-amber-500/10'
    case 'onenote':
      return 'text-violet-400 bg-violet-500/10'
    case 'markdown':
    case 'text':
      return 'text-slate-300 bg-slate-500/10'
    default:
      return 'text-slate-400 bg-slate-500/10'
  }
}

const formatFileSize = (bytes: number): string => {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

const formatTimestamp = (isoString: string): string => {
  const date = new Date(isoString)
  return date.toLocaleString(undefined, {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

interface DocumentPanelProps {
  persona: string
  onDocumentSelect?: (doc: ChatDocument | null) => void
  selectedDocumentId?: string | null
}

export default function DocumentPanel({
  persona,
  onDocumentSelect,
  selectedDocumentId,
}: DocumentPanelProps) {
  const queryClient = useQueryClient()
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [isDragging, setIsDragging] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [categoryFilter, setCategoryFilter] = useState('all')
  const [selectedDocId, setSelectedDocId] = useState<string | null>(null)
  const [selectedAction, setSelectedAction] = useState<string | null>(null)
  const [previewContent, setPreviewContent] = useState('')
  const [binaryPreview, setBinaryPreview] = useState<{ type: 'pdf' | 'image' | 'other'; url: string } | null>(null)
  const [previewError, setPreviewError] = useState<string | null>(null)
  const [isPreviewLoading, setIsPreviewLoading] = useState(false)
  const [previewVersion, setPreviewVersion] = useState(0)

  const { data: documents = [], isLoading, refetch } = useQuery({
    queryKey: ['chat-documents'],
    queryFn: listChatDocuments,
    refetchInterval: 5000,
  })

  const isControlled = selectedDocumentId !== undefined
  const activeDocId = isControlled ? selectedDocumentId : selectedDocId
  const selectedDoc =
    typeof activeDocId === 'string' && activeDocId.length > 0
      ? documents.find((doc) => doc.id === activeDocId) ?? null
      : null

  useEffect(() => {
    if (!documents.length) {
      if (!isControlled) {
        setSelectedDocId(null)
      }
      onDocumentSelect?.(null)
      return
    }
    if (isControlled) {
      return
    }
    if (!selectedDocId) {
      const initial = documents[0]
      setSelectedDocId(initial.id)
      onDocumentSelect?.(initial)
    }
  }, [documents, selectedDocId, onDocumentSelect, isControlled])

  const uploadMutation = useMutation({
    mutationFn: (file: File) => uploadChatDocument(file, persona),
    onSuccess: (doc) => {
      toast.success(`Uploaded: ${doc.original_name}`)
      queryClient.invalidateQueries({ queryKey: ['chat-documents'] })
      if (!isControlled) {
        setSelectedDocId(doc.id)
      }
      onDocumentSelect?.(doc)
      setPreviewVersion((prev) => prev + 1)
    },
    onError: (error) => {
      toast.error(error instanceof Error ? error.message : 'Upload failed')
    },
  })

  const actionMutation = useMutation({
    mutationFn: modifyChatDocument,
    onSuccess: (result, variables) => {
      if (result.success) {
        toast.success(result.changes_summary)
        queryClient.invalidateQueries({ queryKey: ['chat-documents'] })
        if (selectedDoc && variables.documentId === selectedDoc.id) {
          setPreviewVersion((prev) => prev + 1)
        }
      } else {
        toast.error(result.changes_summary)
      }
      setSelectedAction(null)
    },
    onError: (error) => {
      toast.error(error instanceof Error ? error.message : 'Action failed')
      setSelectedAction(null)
    },
  })

  const deleteMutation = useMutation({
    mutationFn: deleteChatDocument,
    onSuccess: (_, deletedId) => {
      toast.success('Document deleted')
      queryClient.invalidateQueries({ queryKey: ['chat-documents'] })
      if (!isControlled && selectedDocId === deletedId) {
        setSelectedDocId(null)
      }
      if (activeDocId === deletedId) {
        onDocumentSelect?.(null)
      }
    },
    onError: (error) => {
      toast.error(error instanceof Error ? error.message : 'Delete failed')
    },
  })

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      setIsDragging(false)
      const files = Array.from(e.dataTransfer.files)
      files.forEach((file) => uploadMutation.mutate(file))
    },
    [uploadMutation]
  )

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (files) {
      Array.from(files).forEach((file) => uploadMutation.mutate(file))
    }
    e.target.value = ''
  }

  const handleDocSelect = (doc: ChatDocument) => {
    if (!isControlled) {
      setSelectedDocId(doc.id)
    }
    onDocumentSelect?.(doc)
  }

  const handleQuickAction = (action: QuickAction) => {
    if (!selectedDoc) {
      toast.error('Select a document first')
      return
    }
    if (selectedDoc.preview_type !== 'text') {
      toast.error('Binary files cannot be auto-modified. Download and edit locally.')
      return
    }
    setSelectedAction(action.id)
    actionMutation.mutate({
      documentId: selectedDoc.id,
      prompt: action.prompt,
      persona,
    })
  }

  const totalSize = useMemo(() => documents.reduce((acc, doc) => acc + doc.size_bytes, 0), [documents])
  const canModifySelectedDoc = selectedDoc?.preview_type === 'text'

  const lastUploaded = useMemo(() => {
    if (!documents.length) return null
    return documents.reduce((latest, doc) =>
      new Date(doc.uploaded_at) > new Date(latest.uploaded_at) ? doc : latest
    )
  }, [documents])

  const categoryCounts = useMemo(() => {
    const counts: Record<string, number> = {}
    documents.forEach((doc) => {
      counts[doc.category] = (counts[doc.category] || 0) + 1
    })
    return counts
  }, [documents])

  const filteredDocuments = useMemo(() => {
    const term = searchQuery.trim().toLowerCase()
    return documents
      .filter((doc) => {
        if (categoryFilter !== 'all' && doc.category !== categoryFilter) return false
        if (!term) return true
        return (
          doc.original_name.toLowerCase().includes(term) ||
          doc.metadata?.persona?.toLowerCase().includes(term) ||
          doc.category.toLowerCase().includes(term)
        )
      })
      .sort((a, b) => new Date(b.uploaded_at).getTime() - new Date(a.uploaded_at).getTime())
  }, [documents, categoryFilter, searchQuery])

  useEffect(() => {
    setPreviewContent('')
    setPreviewError(null)
    setBinaryPreview(null)

    if (!selectedDoc) {
      setIsPreviewLoading(false)
      return
    }

    let cancelled = false
    setIsPreviewLoading(true)

    const loadPreview = async () => {
      try {
        const response = await fetchChatDocumentContent(selectedDoc.id)
        if (cancelled) return

        if (selectedDoc.preview_type === 'text' || response.encoding === 'utf-8') {
          setPreviewContent(response.content)
          return
        }

        if (response.encoding === 'base64') {
          const dataUrl = `data:${response.content_type};base64,${response.content}`
          if (response.content_type === 'application/pdf') {
            setBinaryPreview({ type: 'pdf', url: dataUrl })
            return
          }
          if (response.content_type.startsWith('image/')) {
            setBinaryPreview({ type: 'image', url: dataUrl })
            return
          }
          setBinaryPreview({ type: 'other', url: dataUrl })
          setPreviewError('Preview limited. Use the download option for full fidelity.')
          return
        }

        setPreviewError('Preview not available for this file type.')
      } catch (error) {
        if (!cancelled) {
          setPreviewContent('')
          setPreviewError(error instanceof Error ? error.message : 'Failed to load preview.')
        }
      } finally {
        if (!cancelled) {
          setIsPreviewLoading(false)
        }
      }
    }

    loadPreview()

    return () => {
      cancelled = true
    }
  }, [selectedDoc?.id, selectedDoc?.preview_type, previewVersion])

  return (
    <div className="h-full flex flex-col bg-slate-900/50 border-l border-slate-700/50">
      <div className="p-4 border-b border-slate-700/50 space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider flex items-center gap-2">
            <FileText className="w-4 h-4 text-primary-400" />
            Document Workspace
          </h3>
          <button
            onClick={() => refetch()}
            className="p-1.5 hover:bg-slate-700/50 rounded-lg transition-colors"
            title="Refresh"
          >
            <RefreshCw className={`w-4 h-4 text-slate-400 ${isLoading ? 'animate-spin' : ''}`} />
          </button>
        </div>

        <div className="grid grid-cols-3 gap-3">
          <div className="rounded-xl border border-slate-700/50 bg-slate-900/40 p-3">
            <p className="text-[10px] uppercase text-slate-500">Documents</p>
            <p className="text-xl font-semibold text-slate-100">{documents.length}</p>
          </div>
          <div className="rounded-xl border border-slate-700/50 bg-slate-900/40 p-3">
            <p className="text-[10px] uppercase text-slate-500">Storage footprint</p>
            <p className="text-xl font-semibold text-slate-100">{formatFileSize(totalSize)}</p>
          </div>
          <div className="rounded-xl border border-slate-700/50 bg-slate-900/40 p-3">
            <p className="text-[10px] uppercase text-slate-500">Last upload</p>
            <p className="text-sm font-semibold text-slate-100">
              {lastUploaded ? formatTimestamp(lastUploaded.uploaded_at) : '—'}
            </p>
          </div>
        </div>

        <div className="flex flex-col gap-3">
          <div className="flex items-center gap-2 bg-slate-900/60 border border-slate-700/60 rounded-lg px-3 py-2">
            <Search className="w-4 h-4 text-slate-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by title, persona, or type..."
              className="bg-transparent text-sm flex-1 text-slate-100 placeholder:text-slate-500 focus:outline-none"
            />
          </div>
          <div className="flex flex-wrap items-center gap-2 text-xs text-slate-400">
            <Filter className="w-4 h-4" />
            <div className="flex flex-wrap gap-2">
              {['all', ...Object.keys(categoryCounts)].map((category) => (
                <button
                  key={category}
                  onClick={() => setCategoryFilter(category)}
                  className={`px-3 py-1 rounded-full border transition text-[11px] ${
                    categoryFilter === category
                      ? 'border-primary-500/70 bg-primary-500/10 text-primary-100'
                      : 'border-slate-700 text-slate-300 hover:border-primary-500/40'
                  }`}
                >
                  {category === 'all'
                    ? 'All documents'
                    : category.charAt(0).toUpperCase() + category.slice(1)}
                  {category !== 'all' && (
                    <span className="ml-1 text-[9px] text-primary-300">
                      {categoryCounts[category] || 0}
                    </span>
                  )}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`
            relative cursor-pointer border-2 border-dashed rounded-xl p-4 transition-all
            ${
              isDragging
                ? 'border-primary-400 bg-primary-500/10 scale-[1.02]'
                : 'border-slate-600 hover:border-primary-500/50 hover:bg-slate-800/30'
            }
          `}
        >
          <input
            ref={fileInputRef}
            type="file"
            multiple
            onChange={handleFileSelect}
            className="hidden"
            accept=".docx,.doc,.xlsx,.xls,.pptx,.ppt,.pdf,.json,.csv,.txt,.md,.eml,.msg,.xml,.html,.rtf,.one"
          />
          <div className="flex flex-col items-center text-center">
            <Upload
              className={`w-8 h-8 mb-2 transition-colors ${isDragging ? 'text-primary-400' : 'text-slate-500'}`}
            />
            <p className="text-xs text-slate-400">
              Drop files or <span className="text-primary-400 font-medium">browse</span>
            </p>
            <p className="text-[10px] text-slate-500 mt-1">Office · PDF · Email · JSON · CSV</p>
          </div>
          {uploadMutation.isPending && (
            <div className="absolute inset-0 bg-slate-900/80 flex items-center justify-center rounded-xl">
              <div className="flex flex-col items-center">
                <Loader2 className="w-6 h-6 text-primary-400 animate-spin" />
                <span className="text-xs text-primary-400 mt-2">Uploading...</span>
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-3 space-y-4">
        <div className="space-y-2">
          {isLoading ? (
            <div className="flex items-center justify-center h-20">
              <Loader2 className="w-6 h-6 text-primary-400 animate-spin" />
            </div>
          ) : documents.length === 0 ? (
            <div className="text-center py-8 text-slate-500">
              <File className="w-10 h-10 mx-auto mb-2 opacity-30" />
              <p className="text-xs">No documents uploaded</p>
              <p className="text-[10px] text-slate-600 mt-1">
                Upload documents to analyze or modify with AI
              </p>
            </div>
          ) : filteredDocuments.length === 0 ? (
            <div className="text-center py-6 text-slate-500 border border-dashed border-slate-700 rounded-xl">
              <p className="text-sm">No documents match your filters.</p>
              <p className="text-[11px] text-slate-500 mt-1">Try adjusting search or type filters.</p>
            </div>
          ) : (
            filteredDocuments.map((doc) => {
              const Icon = getCategoryIcon(doc.category)
              const colorClass = getCategoryColor(doc.category)
              const isActive = doc.id === activeDocId
              const snippet = doc.content_preview
                ? doc.content_preview.slice(0, 90).trim() + (doc.content_preview.length > 90 ? '…' : '')
                : 'No preview yet'

              return (
                <button
                  key={doc.id}
                  onClick={() => handleDocSelect(doc)}
                  className={`
                    w-full text-left rounded-xl border transition-all p-3 flex flex-col gap-3
                    ${
                      isActive
                        ? 'border-primary-500/70 bg-primary-500/10 shadow-lg shadow-primary-500/5'
                        : 'border-slate-700/50 bg-slate-800/30 hover:bg-slate-800/50 hover:border-slate-600'
                    }
                  `}
                >
                  <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-lg ${colorClass}`}>
                      <Icon className="w-4 h-4" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-slate-200 truncate">
                        {doc.original_name}
                      </p>
                      <div className="flex items-center gap-2 mt-1 text-[10px] text-slate-500">
                        <span className="uppercase font-medium">{doc.category}</span>
                        <span>•</span>
                        <span>{formatFileSize(doc.size_bytes)}</span>
                        <span>•</span>
                        <span>{formatTimestamp(doc.uploaded_at)}</span>
                      </div>
                    </div>
                    {doc.metadata?.persona && (
                      <span className="px-2 py-1 text-[10px] rounded-full border border-slate-600 text-slate-300">
                        {doc.metadata.persona}
                      </span>
                    )}
                  </div>
                  <p className="text-[11px] text-slate-400 line-clamp-2">{snippet}</p>
                </button>
              )
            })
          )}
        </div>

        <div className="rounded-xl border border-slate-700/50 bg-slate-800/30">
          {selectedDoc ? (
            <>
              <div className="p-4 border-b border-slate-700/50 flex flex-col gap-3">
                <div className="flex items-start gap-3">
                  <div className={`p-2 rounded-lg ${getCategoryColor(selectedDoc.category)}`}>
                    {(() => {
                      const Icon = getCategoryIcon(selectedDoc.category)
                      return <Icon className="w-5 h-5" />
                    })()}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-semibold text-slate-100">{selectedDoc.original_name}</p>
                    <div className="text-[11px] text-slate-400 flex flex-wrap gap-3 mt-1">
                      <span className="flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {formatTimestamp(selectedDoc.uploaded_at)}
                      </span>
                      <span>{formatFileSize(selectedDoc.size_bytes)}</span>
                      {selectedDoc.metadata?.persona && (
                        <span className="uppercase text-primary-300">{selectedDoc.metadata.persona}</span>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <a
                      href={apiPath(`documents/${selectedDoc.id}/content`)}
                      download={selectedDoc.original_name}
                      className="p-2 bg-slate-700/50 text-slate-200 rounded-lg hover:bg-slate-700 transition-colors"
                      title="Download"
                    >
                      <Download className="w-4 h-4" />
                    </a>
                    <button
                      onClick={() => deleteMutation.mutate(selectedDoc.id)}
                      className="p-2 bg-rose-500/10 text-rose-300 rounded-lg hover:bg-rose-500/20 transition-colors"
                      title="Delete document"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
                <div className="flex items-center justify-between text-[10px] text-slate-500">
                  <span>Live preview</span>
                  {selectedDoc.preview_type === 'text' && (
                    <button
                      onClick={() => setPreviewVersion((prev) => prev + 1)}
                      className="flex items-center gap-1 px-2 py-1 rounded-md border border-slate-700/70 text-slate-300 hover:bg-slate-800/70"
                    >
                      <RotateCcw className="w-3 h-3" />
                      Refresh
                    </button>
                  )}
                </div>
                <div className="bg-slate-900/60 border border-slate-700/60 rounded-lg p-3 text-[12px] text-slate-300 min-h-[100px] whitespace-pre-wrap">
                  {isPreviewLoading ? (
                    <div className="flex items-center gap-2 text-slate-400 text-xs">
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Loading preview...
                    </div>
                  ) : binaryPreview ? (
                    <div className="w-full">
                      {binaryPreview.type === 'pdf' ? (
                        <iframe
                          src={binaryPreview.url}
                          title="Document preview"
                          className="w-full h-64 rounded-lg border border-slate-800"
                        />
                      ) : binaryPreview.type === 'image' ? (
                        <img
                          src={binaryPreview.url}
                          alt={selectedDoc.original_name}
                          className="w-full max-h-64 object-contain rounded-lg border border-slate-800 bg-slate-900"
                        />
                      ) : (
                        <div className="text-xs text-slate-400">
                          Preview limited for this file type. Use the download button above to open it
                          in a native viewer.
                        </div>
                      )}
                    </div>
                  ) : previewError ? (
                    <div className="text-center py-6 space-y-2">
                      <p className="text-xs text-slate-400">{previewError}</p>
                      {selectedDoc && (
                        <a
                          href={apiPath(`documents/${selectedDoc.id}/content`)}
                          download={selectedDoc.original_name}
                          className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-slate-700/50 hover:bg-slate-700 border border-slate-600 rounded-lg text-[11px] text-slate-300 transition-colors"
                        >
                          <Download className="w-3 h-3" />
                          Download
                        </a>
                      )}
                    </div>
                  ) : previewContent ? (
                    previewContent
                  ) : (
                    <div className="text-center py-6 space-y-2">
                      <p className="text-xs text-slate-500">Preview not available for this file type.</p>
                      {selectedDoc && (
                        <a
                          href={apiPath(`documents/${selectedDoc.id}/content`)}
                          download={selectedDoc.original_name}
                          className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-slate-700/50 hover:bg-slate-700 border border-slate-600 rounded-lg text-[11px] text-slate-300 transition-colors"
                        >
                          <Download className="w-3 h-3" />
                          Download to View
                        </a>
                      )}
                    </div>
                  )}
                </div>
              </div>

              <div className="p-4 border-b border-slate-700/50 grid grid-cols-3 gap-3 text-[11px] text-slate-400">
                <div>
                  <p className="uppercase text-[9px] text-slate-500">Category</p>
                  <p className="text-slate-200">{selectedDoc.category}</p>
                </div>
                <div>
                  <p className="uppercase text-[9px] text-slate-500">Persona</p>
                  <p className="text-slate-200">{selectedDoc.metadata?.persona ?? '—'}</p>
                </div>
                <div>
                  <p className="uppercase text-[9px] text-slate-500">Type</p>
                  <p className="text-slate-200">{selectedDoc.file_type || '—'}</p>
                </div>
              </div>

              <div className="p-4">
                <p className="text-xs text-slate-400 mb-3">AI quick actions</p>
                {selectedDoc && !canModifySelectedDoc && (
                  <div className="text-[11px] text-rose-200 bg-rose-500/5 border border-rose-500/30 rounded-lg p-3 mb-3">
                    Binary files cannot be auto-modified. Download and edit locally.
                  </div>
                )}
                <div className="grid gap-2">
                  {QUICK_ACTIONS.map((action) => {
                    const Icon = action.icon
                    const isRunning = actionMutation.isPending && selectedAction === action.id
                    return (
                      <button
                        key={action.id}
                        onClick={() => handleQuickAction(action)}
                        className={`w-full flex items-center gap-3 p-3 rounded-lg border text-left transition-colors ${
                          isRunning || !canModifySelectedDoc
                            ? 'border-slate-800 bg-slate-900/30 text-slate-500 cursor-not-allowed'
                            : 'border-slate-700/60 bg-slate-900/40 hover:border-primary-500/60 hover:bg-slate-900/70'
                        }`}
                        disabled={isRunning || !canModifySelectedDoc}
                        title={
                          canModifySelectedDoc
                            ? action.description
                            : 'Binary files must be edited outside the AI workspace.'
                        }
                      >
                        <div className="p-2 bg-slate-800 rounded-lg text-primary-300">
                          {isRunning ? (
                            <Loader2 className="w-4 h-4 animate-spin" />
                          ) : (
                            <Icon className="w-4 h-4" />
                          )}
                        </div>
                        <div className="flex-1">
                          <p className="text-sm font-medium text-slate-200">{action.label}</p>
                          <p className="text-[11px] text-slate-400">{action.description}</p>
                        </div>
                        <Target className="w-4 h-4 text-slate-500" />
                      </button>
                    )
                  })}
                </div>
              </div>
            </>
          ) : (
            <div className="p-6 text-center text-slate-500 flex flex-col items-center gap-2">
              <Sparkles className="w-5 h-5 text-primary-400" />
              <p className="text-sm">Select a document to unlock quick AI options.</p>
              <p className="text-[11px] text-slate-500">
                The assistant can summarize, extract actions, surface metrics, or draft a brief—no
                prompt writing required.
              </p>
            </div>
          )}
        </div>
      </div>

      <div className="p-3 border-t border-slate-700/50 bg-slate-900/30">
        <div className="flex items-center justify-between text-[10px] text-slate-500">
          <span className="flex items-center gap-1">
            <FileText className="w-3 h-3" />
            {documents.length} document(s)
          </span>
          <span>{formatFileSize(totalSize)} total</span>
        </div>
      </div>
    </div>
  )
}
