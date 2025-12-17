import { useState, useEffect, useRef, useCallback, useMemo } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
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

const formatFileSize = (bytes: number): string => {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

interface DocumentVersion {
  id: string
  version_number: number
  content: string
  created_at: string
  created_by: string
  change_summary: string
  is_ai_generated: boolean
  confidence_score?: number
}

interface PendingAIChange {
  id: string
  documentId: string
  proposedContent: string
  changeSummary: string
  confidence: number
  timestamp: string
  persona: string
}

interface DocumentViewerProps {
  document: ChatDocument | null
  persona: string
  onDocumentUpdate?: (document: ChatDocument) => void
  onDocumentSelect?: (document: ChatDocument | null) => void
}

// Mock API functions - these should be implemented in the backend
const fetchDocumentVersions = async (documentId: string): Promise<DocumentVersion[]> => {
  try {
    const { data } = await apiClient.get<DocumentVersion[]>(apiPath(`documents/${documentId}/versions`))
    return data || []
  } catch (error) {
    // If endpoint doesn't exist, return empty array
    return []
  }
}

const acceptVersion = async (documentId: string, versionId: string): Promise<boolean> => {
  try {
    await apiClient.post(apiPath(`documents/${documentId}/versions/${versionId}/accept`))
    return true
  } catch (error) {
    toast.error('Failed to accept version')
    return false
  }
}

const rejectVersion = async (documentId: string, versionId: string): Promise<boolean> => {
  try {
    await apiClient.post(apiPath(`documents/${documentId}/versions/${versionId}/reject`))
    return true
  } catch (error) {
    toast.error('Failed to reject version')
    return false
  }
}

const mergeVersions = async (
  documentId: string,
  baseVersionId: string,
  mergeVersionId: string
): Promise<DocumentVersion | null> => {
  try {
    const { data } = await apiClient.post<DocumentVersion>(
      apiPath(`documents/${documentId}/versions/merge`),
      { base_version_id: baseVersionId, merge_version_id: mergeVersionId }
    )
    return data
  } catch (error) {
    toast.error('Failed to merge versions')
    return null
  }
}

const proposeAIContent = async (
  documentId: string,
  prompt: string,
  persona: string
): Promise<PendingAIChange | null> => {
  try {
    const { data } = await apiClient.post<PendingAIChange>(
      apiPath(`documents/${documentId}/propose`),
      { prompt, persona }
    )
    return data
  } catch (error) {
    // Fallback to modify endpoint
    const result = await modifyChatDocument({ documentId, prompt, persona })
    if (result.success && result.modified_content) {
      return {
        id: `pending-${Date.now()}`,
        documentId,
        proposedContent: result.modified_content,
        changeSummary: result.changes_summary,
        confidence: 0.85,
        timestamp: new Date().toISOString(),
        persona,
      }
    }
    return null
  }
}

type ViewType = 'raw' | 'formatted' | 'preview' | 'markdown' | 'code'

export default function DocumentViewer({
  document,
  persona,
  onDocumentUpdate,
  onDocumentSelect,
}: DocumentViewerProps) {
  const queryClient = useQueryClient()
  const [viewMode, setViewMode] = useState<'view' | 'edit'>('view')
  const [viewType, setViewType] = useState<ViewType>('formatted')
  const [editedContent, setEditedContent] = useState('')
  const [pendingChanges, setPendingChanges] = useState<PendingAIChange[]>([])
  const [selectedVersion, setSelectedVersion] = useState<string | null>(null)
  const [showVersionHistory, setShowVersionHistory] = useState(false)
  const [isRealTimeUpdating, setIsRealTimeUpdating] = useState(false)
  const [selectedAction, setSelectedAction] = useState<string | null>(null)
  const editorRef = useRef<HTMLTextAreaElement>(null)

  const quickActionMutation = useMutation({
    mutationFn: modifyChatDocument,
    onSuccess: (result) => {
      if (result.success) {
        toast.success(result.changes_summary)
        queryClient.invalidateQueries({ queryKey: ['document-content', document?.id] })
        queryClient.invalidateQueries({ queryKey: ['chat-documents'] })
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

  const handleQuickAction = (action: typeof QUICK_ACTIONS[0]) => {
    if (!document) {
      toast.error('Select a document first')
      return
    }
    if (document.preview_type !== 'text') {
      toast.error('Binary files cannot be auto-modified. Download and edit locally.')
      return
    }
    setSelectedAction(action.id)
    quickActionMutation.mutate({
      documentId: document.id,
      prompt: action.prompt,
      persona,
    })
  }

  const { data: currentContent, isLoading: isLoadingContent } = useQuery({
    queryKey: ['document-content', document?.id],
    queryFn: () => fetchChatDocumentContent(document!.id),
    enabled: !!document,
    refetchInterval: 5000, // Poll for updates
  })

  const { data: versions = [], refetch: refetchVersions } = useQuery({
    queryKey: ['document-versions', document?.id],
    queryFn: () => fetchDocumentVersions(document!.id),
    enabled: !!document,
  })

  const saveMutation = useMutation({
    mutationFn: async (content: string) => {
      if (!document) throw new Error('No document selected')
      const { data } = await apiClient.put(apiPath(`documents/${document.id}/content`), { content })
      return data
    },
    onSuccess: () => {
      toast.success('Document saved')
      queryClient.invalidateQueries({ queryKey: ['document-content', document?.id] })
      refetchVersions()
      setViewMode('view')
    },
    onError: (error) => {
      toast.error(`Failed to save: ${error instanceof Error ? error.message : 'Unknown error'}`)
    },
  })

  const proposeMutation = useMutation({
    mutationFn: ({ prompt }: { prompt: string }) => proposeAIContent(document!.id, prompt, persona),
    onSuccess: (proposal) => {
      if (proposal) {
        setPendingChanges((prev) => [proposal, ...prev])
        toast.info('AI proposal generated')
      } else {
        toast.error('Failed to generate proposal')
      }
    },
  })

  const acceptChangeMutation = useMutation({
    mutationFn: (changeId: string) => {
      const change = pendingChanges.find((c) => c.id === changeId)
      if (!change || !document) throw new Error('Change not found')
      return saveMutation.mutateAsync(change.proposedContent)
    },
    onSuccess: (_, changeId) => {
      setPendingChanges((prev) => prev.filter((c) => c.id !== changeId))
      toast.success('Change accepted and saved')
    },
  })

  const rejectChangeMutation = useMutation({
    mutationFn: (changeId: string) => {
      setPendingChanges((prev) => prev.filter((c) => c.id !== changeId))
      return Promise.resolve()
    },
    onSuccess: () => {
      toast.info('Change rejected')
    },
  })

  const acceptVersionMutation = useMutation({
    mutationFn: (versionId: string) => acceptVersion(document!.id, versionId),
    onSuccess: () => {
      toast.success('Version accepted')
      refetchVersions()
      queryClient.invalidateQueries({ queryKey: ['document-content', document?.id] })
    },
  })

  const rejectVersionMutation = useMutation({
    mutationFn: (versionId: string) => rejectVersion(document!.id, versionId),
    onSuccess: () => {
      toast.info('Version rejected')
      refetchVersions()
    },
  })

  const mergeMutation = useMutation({
    mutationFn: ({ baseId, mergeId }: { baseId: string; mergeId: string }) =>
      mergeVersions(document!.id, baseId, mergeId),
    onSuccess: (mergedVersion) => {
      if (mergedVersion) {
        toast.success('Versions merged successfully')
        refetchVersions()
        queryClient.invalidateQueries({ queryKey: ['document-content', document?.id] })
      }
    },
  })

  // Initialize edited content when document changes
  useEffect(() => {
    if (currentContent?.content) {
      if (viewMode === 'edit') {
        setEditedContent(currentContent.content)
        setTimeout(() => {
          if (editorRef.current) {
            editorRef.current.style.height = 'auto'
            editorRef.current.style.height = `${editorRef.current.scrollHeight}px`
          }
        }, 0)
      }
    }
  }, [currentContent, viewMode])

  // Real-time AI updates monitoring
  useEffect(() => {
    if (!document || !currentContent) return

    const checkForUpdates = async () => {
      if (pendingChanges.length > 0 || versions.length > 0) {
        setIsRealTimeUpdating(true)
        setTimeout(() => setIsRealTimeUpdating(false), 1500)
      }
    }

    const interval = setInterval(checkForUpdates, 5000)
    return () => clearInterval(interval)
  }, [document, currentContent, pendingChanges.length, versions.length])

  const handleSave = () => {
    if (editedContent.trim()) {
      saveMutation.mutate(editedContent)
    }
  }

  const handleProposeChange = () => {
    const userPrompt = window.prompt('Enter a prompt for AI to propose changes:')
    if (userPrompt && userPrompt.trim()) {
      proposeMutation.mutate({ prompt: userPrompt })
    }
  }

  const displayContent = viewMode === 'edit' ? editedContent : currentContent?.content || ''

  if (!document) {
    return (
      <div className="h-full flex items-center justify-center bg-gradient-to-br from-slate-900/50 to-slate-800/30">
        <div className="text-center max-w-md px-6">
          <div className="w-20 h-20 mx-auto mb-6 rounded-2xl bg-gradient-to-br from-primary-500/20 to-violet-500/20 flex items-center justify-center backdrop-blur-sm">
            <FileText className="w-10 h-10 text-primary-400" />
          </div>
          <h3 className="text-xl font-semibold text-slate-200 mb-2">No Document Selected</h3>
          <p className="text-sm text-slate-400 leading-relaxed">
            Select a document from the chat to view, edit, and manage versions here.
          </p>
        </div>
      </div>
    )
  }

  const selectedVersionData = versions.find((v) => v.id === selectedVersion)
  const displayVersions = selectedVersionData
    ? [{ ...selectedVersionData, is_selected: true }, ...versions.filter((v) => v.id !== selectedVersion)]
    : versions

  // Determine available view types based on document
  const availableViewTypes: { type: ViewType; label: string; icon: typeof FileText }[] = [
    { type: 'raw', label: 'Raw', icon: FileCode },
    { type: 'formatted', label: 'Formatted', icon: Type },
  ]

  if (document.category === 'markdown' || document.category === 'text') {
    availableViewTypes.push({ type: 'markdown', label: 'Markdown', icon: FileText })
  }
  if (document.category === 'json' || document.category === 'xml' || document.category === 'html') {
    availableViewTypes.push({ type: 'code', label: 'Code', icon: Code })
  }
  if (document.preview_type !== 'text') {
    availableViewTypes.push({ type: 'preview', label: 'Preview', icon: Eye })
  }

  return (
    <div className="h-full flex flex-col bg-gradient-to-br from-slate-900/50 via-slate-900/40 to-slate-800/30">
      {/* Header - Cleaner Design */}
      <div className="px-6 py-4 border-b border-slate-700/30 bg-slate-900/60 backdrop-blur-sm">
        <div className="flex items-center justify-between mb-4">
          {/* Document Info */}
          <div className="flex items-center gap-4 flex-1 min-w-0">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500/20 to-violet-500/20 flex items-center justify-center flex-shrink-0">
              <FileText className="w-5 h-5 text-primary-400" />
            </div>
            <div className="flex-1 min-w-0">
              <h2 className="text-base font-semibold text-slate-100 truncate mb-0.5">
                {document.original_name}
              </h2>
              <div className="flex items-center gap-3 text-xs text-slate-400">
                <span className="capitalize">{document.category}</span>
                <span>•</span>
                <span>{formatFileSize(document.size_bytes)}</span>
                <span>•</span>
                <span className="flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  {new Date(document.uploaded_at).toLocaleDateString()}
                </span>
              </div>
            </div>
          </div>

          {/* Action Buttons - Grouped */}
          <div className="flex items-center gap-2">
            {isRealTimeUpdating && (
              <div className="flex items-center gap-2 px-3 py-1.5 bg-primary-500/20 border border-primary-500/30 rounded-lg">
                <Loader2 className="w-3.5 h-3.5 text-primary-400 animate-spin" />
                <span className="text-xs text-primary-300 font-medium">AI updating...</span>
              </div>
            )}
            
            {document && (
              <>
                <button
                  onClick={() => setShowVersionHistory(!showVersionHistory)}
                  className={`p-2 rounded-md transition-all relative ${
                    showVersionHistory
                      ? 'bg-primary-500/20 text-primary-400'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-700/50'
                  }`}
                  title="Version History"
                >
                  <History className="w-4 h-4" />
                  {versions.length > 0 && !showVersionHistory && (
                    <span className="absolute -top-0.5 -right-0.5 w-4 h-4 bg-primary-500 text-white text-[9px] rounded-full flex items-center justify-center font-semibold">
                      {versions.length}
                    </span>
                  )}
                </button>
                
                <a
                  href={apiPath(`documents/${document.id}/content`)}
                  download={document.original_name}
                  className="p-2 text-slate-400 rounded-md hover:text-slate-200 hover:bg-slate-700/50 transition-all"
                  title="Download"
                >
                  <Download className="w-4 h-4" />
                </a>
              </>
            )}
          </div>
        </div>

        {/* Mode Toggle and View Type Tabs - Improved Design */}
        <div className="flex items-center justify-between gap-4">
          {/* View/Edit Mode Toggle */}
          <div className="flex items-center gap-1 p-1 bg-slate-800/50 rounded-lg border border-slate-700/50">
            <button
              onClick={() => setViewMode('view')}
              className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all ${
                viewMode === 'view'
                  ? 'bg-primary-500/20 text-primary-300 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Eye className="w-4 h-4" />
              View
            </button>
            <button
              onClick={() => {
                setViewMode('edit')
                setEditedContent(currentContent?.content || '')
              }}
              className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all ${
                viewMode === 'edit'
                  ? 'bg-primary-500/20 text-primary-300 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Edit3 className="w-4 h-4" />
              Edit
            </button>
          </div>

          {/* View Type Tabs - Only in view mode */}
          {viewMode === 'view' && (
            <div className="flex items-center gap-1">
              {availableViewTypes.map(({ type, label, icon: Icon }) => (
                <button
                  key={type}
                  onClick={() => setViewType(type)}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                    viewType === type
                      ? 'bg-slate-700 text-slate-100 shadow-sm'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                  }`}
                  title={`${label} view`}
                >
                  <Icon className="w-3.5 h-3.5" />
                  {label}
                </button>
              ))}
            </div>
          )}

          {/* Edit Mode Actions */}
          {viewMode === 'edit' && (
            <div className="flex items-center gap-2">
              <button
                onClick={handleSave}
                disabled={saveMutation.isPending}
                className="flex items-center gap-2 px-4 py-2 bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 rounded-md text-sm font-medium hover:bg-emerald-500/30 disabled:opacity-50 transition-all"
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
                  setEditedContent(currentContent?.content || '')
                  setViewMode('view')
                }}
                className="flex items-center gap-2 px-4 py-2 bg-slate-800 text-slate-400 border border-slate-700 rounded-md text-sm font-medium hover:bg-slate-700 hover:text-slate-200 transition-all"
              >
                <X className="w-4 h-4" />
                Cancel
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
          {/* Pending AI Changes */}
          {pendingChanges.length > 0 && (
            <div className="p-4 border-b border-slate-700/30 bg-amber-500/5">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-amber-400" />
                  <span className="text-sm font-semibold text-amber-300">
                    {pendingChanges.length} Pending AI Proposal{pendingChanges.length > 1 ? 's' : ''}
                  </span>
                </div>
              </div>
              <div className="space-y-2">
                {pendingChanges.map((change) => (
                  <div
                    key={change.id}
                    className="bg-slate-800/50 border border-amber-500/30 rounded-lg p-3"
                  >
                    <div className="flex items-start justify-between gap-3 mb-2">
                      <div className="flex-1">
                        <p className="text-sm text-amber-200 font-medium mb-1">{change.changeSummary}</p>
                        <div className="flex items-center gap-2 text-xs text-slate-400">
                          <Bot className="w-3 h-3" />
                          <span>{change.persona}</span>
                          <span>•</span>
                          <span>Confidence: {Math.round(change.confidence * 100)}%</span>
                          <span>•</span>
                          <span>{new Date(change.timestamp).toLocaleTimeString()}</span>
                        </div>
                      </div>
                      <div className="flex items-center gap-1">
                        <button
                          onClick={() => acceptChangeMutation.mutate(change.id)}
                          disabled={acceptChangeMutation.isPending}
                          className="p-2 bg-emerald-500/20 text-emerald-400 rounded-lg hover:bg-emerald-500/30 disabled:opacity-50 transition-all"
                          title="Accept"
                        >
                          <Check className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => rejectChangeMutation.mutate(change.id)}
                          className="p-2 bg-rose-500/20 text-rose-400 rounded-lg hover:bg-rose-500/30 transition-all"
                          title="Reject"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Document Content Editor/Viewer - Improved Typography */}
          <div className="flex-1 overflow-y-auto">
            {isLoadingContent ? (
              <div className="flex items-center justify-center h-full">
                <div className="text-center">
                  <Loader2 className="w-8 h-8 text-primary-400 animate-spin mx-auto mb-3" />
                  <p className="text-sm text-slate-400">Loading document...</p>
                </div>
              </div>
            ) : viewMode === 'edit' ? (
              <div className="h-full p-6">
                <textarea
                  ref={editorRef}
                  value={editedContent}
                  onChange={(e) => {
                    setEditedContent(e.target.value)
                    const textarea = e.target
                    textarea.style.height = 'auto'
                    textarea.style.height = `${textarea.scrollHeight}px`
                  }}
                  className="w-full h-full bg-slate-900/60 border border-slate-700/60 rounded-xl p-6 text-sm text-slate-100 font-mono resize-none focus:outline-none focus:ring-2 focus:ring-primary-500/50 leading-relaxed"
                  placeholder="Start editing your document..."
                />
              </div>
            ) : (
              <div className="h-full p-6">
                <div className="max-w-4xl mx-auto">
                  {viewType === 'raw' && (
                    <div className="bg-slate-900/60 border border-slate-700/60 rounded-xl p-8 text-sm text-slate-200 whitespace-pre-wrap font-mono leading-relaxed">
                      {displayContent || 'No content available'}
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
                          // Safe markdown rendering without dangerouslySetInnerHTML
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
                          if (trimmed.startsWith('```')) {
                            return <div key={idx} className="bg-slate-800/50 rounded p-2 my-2 font-mono text-xs text-slate-300" />
                          }
                          return <p key={idx} className="mb-3 text-slate-200 leading-relaxed">{line}</p>
                        })}
                      </div>
                    </div>
                  )}
                  {viewType === 'code' && (
                    <div className="bg-slate-900/60 border border-slate-700/60 rounded-xl p-8 text-sm text-slate-200 font-mono">
                      <pre className="whitespace-pre-wrap leading-relaxed">{displayContent || 'No content available'}</pre>
                    </div>
                  )}
                  {viewType === 'preview' && currentContent && (
                    <div className="bg-slate-900/60 border border-slate-700/60 rounded-xl p-8">
                      {document.preview_type === 'text' ? (
                        <div className="text-base text-slate-100 whitespace-pre-wrap leading-relaxed">{displayContent}</div>
                      ) : (
                        <div className="text-center py-12 space-y-4">
                          <div className="w-16 h-16 mx-auto rounded-xl bg-slate-800/50 flex items-center justify-center">
                            <FileType className="w-8 h-8 text-slate-500" />
                          </div>
                          <div>
                            <p className="text-sm font-medium text-slate-300 mb-2">Binary File Preview</p>
                            <p className="text-xs text-slate-500 mb-4">
                              This file type cannot be previewed in the browser.
                            </p>
                            <a
                              href={apiPath(`documents/${document.id}/content`)}
                              download={document.original_name}
                              className="inline-flex items-center gap-2 px-4 py-2 bg-primary-500/20 hover:bg-primary-500/30 border border-primary-500/30 rounded-lg text-sm text-primary-300 transition-colors"
                            >
                              <Download className="w-4 h-4" />
                              Download to View
                            </a>
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* AI Proposal Button */}
          {viewMode === 'view' && (
            <div className="p-4 border-t border-slate-700/30 bg-slate-900/40">
              <button
                onClick={handleProposeChange}
                disabled={proposeMutation.isPending}
                className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-gradient-to-r from-primary-500/20 to-violet-500/20 border border-primary-500/30 rounded-lg text-sm font-medium text-primary-300 hover:from-primary-500/30 hover:to-violet-500/30 disabled:opacity-50 transition-all"
              >
                {proposeMutation.isPending ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Generating proposal...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
                    <span>Propose AI Changes</span>
                  </>
                )}
              </button>
            </div>
          )}
        </div>

      {/* Version Control - Bottom Right Floating Panel */}
      {showVersionHistory && (
        <div className="fixed bottom-6 right-6 w-[420px] h-[560px] bg-slate-900/98 backdrop-blur-xl border border-slate-700/50 rounded-2xl shadow-2xl flex flex-col overflow-hidden z-50 animate-in slide-in-from-bottom-4 fade-in duration-300">
          <div className="p-4 border-b border-slate-700/50 bg-gradient-to-r from-slate-800/50 to-slate-900/50">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-primary-500/20 flex items-center justify-center">
                  <GitBranch className="w-4 h-4 text-primary-400" />
                </div>
                <div>
                  <h4 className="text-sm font-semibold text-slate-100">Version History</h4>
                  {versions.length > 0 && (
                    <p className="text-xs text-slate-400">{versions.length} version{versions.length !== 1 ? 's' : ''}</p>
                  )}
                </div>
              </div>
              <button
                onClick={() => setShowVersionHistory(false)}
                className="p-1.5 text-slate-400 hover:text-slate-200 hover:bg-slate-700/50 rounded-lg transition-all"
                title="Hide version control"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            <button
              onClick={handleProposeChange}
              disabled={proposeMutation.isPending}
              className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-primary-500/20 border border-primary-500/30 rounded-lg text-sm font-medium text-primary-300 hover:bg-primary-500/30 disabled:opacity-50 transition-all"
            >
              <Sparkles className="w-4 h-4" />
              AI Propose New Content
            </button>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-3">
            {versions.length === 0 ? (
              <div className="text-center py-12 text-slate-500">
                <GitBranch className="w-12 h-12 mx-auto mb-3 opacity-30" />
                <p className="text-sm font-medium mb-1">No version history yet</p>
                <p className="text-xs text-slate-600">Versions will appear here after changes</p>
              </div>
            ) : (
              versions.map((version, index) => {
                const isSelected = version.id === selectedVersion
                const isCurrent = index === 0
                return (
                  <div
                    key={version.id}
                    className={`p-4 rounded-xl border transition-all ${
                      isSelected
                        ? 'border-primary-500/50 bg-primary-500/10'
                        : 'border-slate-700/50 bg-slate-800/30 hover:bg-slate-800/50'
                    }`}
                  >
                    <div className="flex items-start justify-between gap-3 mb-3">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <span className="text-sm font-semibold text-slate-200">
                            v{version.version_number}
                          </span>
                          {isCurrent && (
                            <span className="px-2 py-0.5 bg-emerald-500/20 text-emerald-400 text-xs rounded-md border border-emerald-500/30">
                              Current
                            </span>
                          )}
                          {version.is_ai_generated && (
                            <span className="px-2 py-0.5 bg-primary-500/20 text-primary-400 text-xs rounded-md border border-primary-500/30">
                              AI
                            </span>
                          )}
                        </div>
                        <p className="text-sm text-slate-300 leading-relaxed mb-2">
                          {version.change_summary}
                        </p>
                        <div className="flex items-center gap-2 text-xs text-slate-500">
                          {version.is_ai_generated ? (
                            <Bot className="w-3.5 h-3.5" />
                          ) : (
                            <User className="w-3.5 h-3.5" />
                          )}
                          <span>{version.created_by}</span>
                          <span>•</span>
                          <span>{new Date(version.created_at).toLocaleString()}</span>
                          {version.confidence_score && (
                            <>
                              <span>•</span>
                              <span>{Math.round(version.confidence_score * 100)}% confidence</span>
                            </>
                          )}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2 mt-3">
                      <button
                        onClick={() => setSelectedVersion(isSelected ? null : version.id)}
                        className="flex-1 px-3 py-2 bg-slate-700/50 text-slate-300 text-xs font-medium rounded-lg hover:bg-slate-700 transition-colors"
                      >
                        {isSelected ? 'Deselect' : 'Select'}
                      </button>
                      {!isCurrent && (
                        <>
                          <button
                            onClick={() => acceptVersionMutation.mutate(version.id)}
                            disabled={acceptVersionMutation.isPending}
                            className="px-3 py-2 bg-emerald-500/20 text-emerald-400 text-xs font-medium rounded-lg hover:bg-emerald-500/30 disabled:opacity-50 transition-all"
                            title="Accept this version"
                          >
                            <Check className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => rejectVersionMutation.mutate(version.id)}
                            className="px-3 py-2 bg-rose-500/20 text-rose-400 text-xs font-medium rounded-lg hover:bg-rose-500/30 transition-all"
                            title="Reject this version"
                          >
                            <X className="w-4 h-4" />
                          </button>
                        </>
                      )}
                    </div>
                    {selectedVersion && selectedVersion === version.id && index > 0 && (
                      <button
                        onClick={() =>
                          mergeMutation.mutate({
                            baseId: versions[0].id,
                            mergeId: version.id,
                          })
                        }
                        disabled={mergeMutation.isPending}
                        className="w-full mt-2 flex items-center justify-center gap-2 px-3 py-2 bg-violet-500/20 text-violet-400 text-xs font-medium rounded-lg border border-violet-500/30 hover:bg-violet-500/30 disabled:opacity-50 transition-all"
                      >
                        <GitMerge className="w-4 h-4" />
                        Merge with Current
                      </button>
                    )}
                  </div>
                )
              })
            )}
          </div>
        </div>
      )}
    </div>
  )
}
