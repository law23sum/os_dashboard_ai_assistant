import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useState, useMemo, ReactNode, useEffect, useRef } from 'react'
import { Plus, FileEdit, BookOpen, Wand2, Save, Loader2, MonitorSmartphone, X, Trash2, Settings } from 'lucide-react'
import apiClient, { apiPath } from '../lib/apiClient'
import {
  WriterSnapshot,
  WriterDocument,
  WriterStats,
  WriterSuggestion,
  WriterPipelineEntry,
  WriterCanonEntry,
} from '../types'
import AIPermissionModal, { AIPermissionSettings } from '../components/AIPermissionModal'
import AIChangePrompt from '../components/AIChangePrompt'

const fetchSnapshot = async (): Promise<WriterSnapshot> => {
  const { data } = await apiClient.get<WriterSnapshot>(apiPath('writer/snapshot'))
  return data
}

const createDocument = async (payload: {
  title: string
  doc_type: string
  summary?: string
  theme?: string
}): Promise<WriterDocument> => {
  const { data } = await apiClient.post<WriterDocument>(apiPath('writer/documents'), payload)
  return data
}

const saveDocument = async ({
  id,
  content,
}: {
  id: string
  content: string
}): Promise<WriterDocument> => {
  const { data } = await apiClient.put<WriterDocument>(apiPath(`writer/documents/${id}`), { content })
  return data
}

const loadDocument = async (id: string): Promise<WriterDocument> => {
  const { data } = await apiClient.get<WriterDocument>(apiPath(`writer/documents/${id}`))
  return data
}

const deleteDocument = async (id: string): Promise<void> => {
  await apiClient.delete(apiPath(`writer/documents/${id}`))
}

const generateNarrative = async (payload: {
  doc_type: string
  theme: string
  genre: string
  title: string
}): Promise<string> => {
  const { data } = await apiClient.post<{ content: string }>(apiPath('writer/generate'), payload)
  return data.content
}

interface OpenDocument {
  doc: WriterDocument
  content: string
  hasUnsavedChanges: boolean
}

export default function Writer() {
  const [title, setTitle] = useState('')
  const [theme, setTheme] = useState('')
  const [docType, setDocType] = useState('Article')
  const [genre, setGenre] = useState('Professional')
  const [assistance, setAssistance] = useState('Minimal')
  const [length, setLength] = useState('Short (500-1000 words)')
  
  // Tabbed document management
  const [openDocuments, setOpenDocuments] = useState<Map<string, OpenDocument>>(new Map())
  const [activeDocId, setActiveDocId] = useState<string | null>(null)
  
  // AI Permission settings
  const [permissionSettings, setPermissionSettings] = useState<AIPermissionSettings | null>(null)
  const [showPermissionModal, setShowPermissionModal] = useState(false)
  const [showChangePrompt, setShowChangePrompt] = useState(false)
  const [pendingAIChange, setPendingAIChange] = useState<{
    documentId: string
    changeSummary: string
    confidence: number
    newContent: string
  } | null>(null)
  
  // Track AI changes for real-time switching
  const aiChangeQueueRef = useRef<Array<{
    documentId: string
    changeSummary: string
    confidence: number
    newContent: string
  }>>([])

  const queryClient = useQueryClient()
  const snapshotQuery = useQuery({
    queryKey: ['writer-snapshot'],
    queryFn: fetchSnapshot,
    refetchInterval: 5000, // Poll for AI changes
  })

  // Load permission settings from localStorage on mount
  useEffect(() => {
    const stored = localStorage.getItem('aiPermissionSettings')
    if (stored) {
      try {
        setPermissionSettings(JSON.parse(stored))
      } catch {
        // Invalid stored data, show modal
        setShowPermissionModal(true)
      }
    } else {
      // First time, show modal
      setShowPermissionModal(true)
    }
  }, [])

  // Check for AI changes in snapshot and queue them
  useEffect(() => {
    if (!snapshotQuery.data || !permissionSettings) return

    const snapshot = snapshotQuery.data
    snapshot.documents.forEach((doc) => {
      const openDoc = openDocuments.get(doc.id)
      if (openDoc && doc.content !== openDoc.content) {
        // Document was changed externally (likely by AI)
        const confidence = Math.floor(Math.random() * 30) + 70 // Simulate confidence 70-100%
        const changeSummary = `AI updated "${doc.title}" with new content`
        
        // Check if we should auto-apply or prompt
        if (permissionSettings.mode === 'auto' && confidence >= permissionSettings.confidenceThreshold) {
          // Auto-apply
          setOpenDocuments((prev) => {
            const updated = new Map(prev)
            const existing = updated.get(doc.id)
            if (existing) {
              updated.set(doc.id, {
                ...existing,
                content: doc.content,
              })
            }
            return updated
          })
          // Switch to this document if not already active
          if (activeDocId !== doc.id) {
            setActiveDocId(doc.id)
          }
        } else {
          // Queue for permission
          aiChangeQueueRef.current.push({
            documentId: doc.id,
            changeSummary,
            confidence,
            newContent: doc.content,
          })
          processAIChangeQueue()
        }
      }
    })
  }, [snapshotQuery.data, permissionSettings, openDocuments, activeDocId])

  const processAIChangeQueue = () => {
    if (aiChangeQueueRef.current.length === 0 || showChangePrompt) return

    const nextChange = aiChangeQueueRef.current.shift()
    if (nextChange) {
      setPendingAIChange(nextChange)
      setShowChangePrompt(true)
      // Switch to the document being changed
      setActiveDocId(nextChange.documentId)
    }
  }

  // Process queue when prompt closes
  useEffect(() => {
    if (!showChangePrompt && aiChangeQueueRef.current.length > 0) {
      setTimeout(processAIChangeQueue, 500)
    }
  }, [showChangePrompt])

  const createMutation = useMutation({
    mutationFn: createDocument,
    onSuccess: (doc) => {
      queryClient.invalidateQueries({ queryKey: ['writer-snapshot'] })
      // Open new document in a tab
      setOpenDocuments((prev) => {
        const updated = new Map(prev)
        updated.set(doc.id, {
          doc,
          content: doc.content ?? '',
          hasUnsavedChanges: false,
        })
        return updated
      })
      setActiveDocId(doc.id)
      setTitle(doc.title)
      setTheme(doc.theme)
      setDocType(doc.type)
    },
  })

  const saveMutation = useMutation({
    mutationFn: saveDocument,
    onSuccess: (doc) => {
      queryClient.invalidateQueries({ queryKey: ['writer-snapshot'] })
      setOpenDocuments((prev) => {
        const updated = new Map(prev)
        const existing = updated.get(doc.id)
        if (existing) {
          updated.set(doc.id, {
            ...existing,
            content: doc.content ?? '',
            hasUnsavedChanges: false,
          })
        }
        return updated
      })
    },
  })

  const loadMutation = useMutation({
    mutationFn: loadDocument,
    onSuccess: (doc) => {
      // Open document in a tab if not already open
      setOpenDocuments((prev) => {
        const updated = new Map(prev)
        if (!updated.has(doc.id)) {
          updated.set(doc.id, {
            doc,
            content: doc.content ?? '',
            hasUnsavedChanges: false,
          })
        }
        return updated
      })
      setActiveDocId(doc.id)
      setTitle(doc.title)
      setTheme(doc.theme)
      setDocType(doc.type)
    },
  })

  const deleteMutation = useMutation({
    mutationFn: deleteDocument,
    onSuccess: (_, docId) => {
      queryClient.invalidateQueries({ queryKey: ['writer-snapshot'] })
      // Close tab if open
      setOpenDocuments((prev) => {
        const updated = new Map(prev)
        updated.delete(docId)
        return updated
      })
      // Switch to another tab if this was active
      if (activeDocId === docId) {
        const remaining = Array.from(openDocuments.keys()).filter(id => id !== docId)
        setActiveDocId(remaining[0] || null)
      }
    },
  })

  const generateMutation = useMutation({
    mutationFn: generateNarrative,
    onSuccess: (content) => {
      if (activeDocId) {
        setOpenDocuments((prev) => {
          const updated = new Map(prev)
          const existing = updated.get(activeDocId)
          if (existing) {
            updated.set(activeDocId, {
              ...existing,
              content,
              hasUnsavedChanges: true,
            })
          }
          return updated
        })
      }
    },
  })

  const snapshot = snapshotQuery.data
  const stats: WriterStats | undefined = snapshot?.stats

  const activeDoc = activeDocId ? openDocuments.get(activeDocId) : null
  const editorContent = activeDoc?.content ?? ''
  const wordCount = useMemo(() => editorContent.trim().split(/\s+/).filter(Boolean).length, [editorContent])

  const handleCreateDocument = () => {
    createMutation.mutate({
      title: title || 'Untitled Document',
      doc_type: docType,
      summary: theme,
      theme,
    })
  }

  const handleSave = () => {
    if (!activeDocId || !activeDoc) return
    saveMutation.mutate({ id: activeDocId, content: activeDoc.content })
  }

  const handleGenerate = () => {
    if (!activeDocId) return
    generateMutation.mutate({
      doc_type: docType,
      theme: theme || 'adventure',
      genre,
      title: title || 'Untitled Narrative',
    })
  }

  const handleSelectDocument = (doc: WriterDocument) => {
    if (openDocuments.has(doc.id)) {
      setActiveDocId(doc.id)
    } else {
      loadMutation.mutate(doc.id)
    }
  }

  const handleCloseTab = (docId: string, e: React.MouseEvent) => {
    e.stopPropagation()
    setOpenDocuments((prev) => {
      const updated = new Map(prev)
      updated.delete(docId)
      return updated
    })
    if (activeDocId === docId) {
      const remaining = Array.from(openDocuments.keys()).filter(id => id !== docId)
      setActiveDocId(remaining[0] || null)
    }
  }

  const handleDeleteDocument = (docId: string, e: React.MouseEvent) => {
    e.stopPropagation()
    if (confirm('Are you sure you want to delete this document? This action cannot be undone.')) {
      deleteMutation.mutate(docId)
    }
  }

  const handleContentChange = (newContent: string) => {
    if (!activeDocId) return
    setOpenDocuments((prev) => {
      const updated = new Map(prev)
      const existing = updated.get(activeDocId)
      if (existing) {
        updated.set(activeDocId, {
          ...existing,
          content: newContent,
          hasUnsavedChanges: true,
        })
      }
      return updated
    })
  }

  const handleAcceptAIChange = () => {
    if (!pendingAIChange) return
    setOpenDocuments((prev) => {
      const updated = new Map(prev)
      const existing = updated.get(pendingAIChange.documentId)
      if (existing) {
        updated.set(pendingAIChange.documentId, {
          ...existing,
          content: pendingAIChange.newContent,
          hasUnsavedChanges: true,
        })
      }
      return updated
    })
    setPendingAIChange(null)
    setShowChangePrompt(false)
  }

  const handleRejectAIChange = () => {
    setPendingAIChange(null)
    setShowChangePrompt(false)
  }

  const handleViewAIChanges = () => {
    // TODO: Implement diff view
    alert('Diff view coming soon!')
  }

  const handleSavePermissionSettings = (settings: AIPermissionSettings) => {
    setPermissionSettings(settings)
    localStorage.setItem('aiPermissionSettings', JSON.stringify(settings))
  }

  if (snapshotQuery.isLoading || !snapshot) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
      </div>
    )
  }

  return (
    <div className="px-4 py-6 sm:px-0 space-y-6">
      <AIPermissionModal
        isOpen={showPermissionModal}
        onClose={() => setShowPermissionModal(false)}
        onSave={handleSavePermissionSettings}
        initialSettings={permissionSettings || undefined}
      />

      {pendingAIChange && (
        <AIChangePrompt
          isOpen={showChangePrompt}
          documentTitle={openDocuments.get(pendingAIChange.documentId)?.doc.title || 'Unknown'}
          changeSummary={pendingAIChange.changeSummary}
          confidence={pendingAIChange.confidence}
          onAccept={handleAcceptAIChange}
          onReject={handleRejectAIChange}
          onViewChanges={handleViewAIChanges}
        />
      )}

      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Writer Workspace</h2>
          <p className="text-gray-600 dark:text-gray-400">
            Shared writing environment with AI assistance for both desktop and web.
          </p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={() => setShowPermissionModal(true)}
            className="inline-flex items-center px-4 py-2 rounded-md border border-gray-300 dark:border-gray-600 text-sm font-medium text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700"
            title="AI Permission Settings"
          >
            <Settings className="w-4 h-4 mr-2" />
            AI Settings
          </button>
          <button
            onClick={handleCreateDocument}
            className="inline-flex items-center px-4 py-2 rounded-md bg-primary-600 text-white text-sm font-medium hover:bg-primary-700"
            disabled={createMutation.isPending}
          >
            {createMutation.isPending ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Plus className="w-4 h-4 mr-2" />}
            New Document
          </button>
          <button
            onClick={handleSave}
            disabled={saveMutation.isPending || !activeDoc}
            className="inline-flex items-center px-4 py-2 rounded-md border border-gray-300 dark:border-gray-600 text-sm font-medium text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-60"
          >
            {saveMutation.isPending ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Save className="w-4 h-4 mr-2" />}
            Save Draft
          </button>
          <button
            onClick={handleGenerate}
            disabled={generateMutation.isPending || !activeDocId}
            className="inline-flex items-center px-4 py-2 rounded-md border border-transparent text-sm font-medium bg-gray-900 text-white hover:bg-gray-800"
          >
            {generateMutation.isPending ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Wand2 className="w-4 h-4 mr-2" />}
            Generate Narrative
          </button>
        </div>
      </div>

      {/* Document Tabs */}
      {openDocuments.size > 0 && (
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
          <div className="flex items-center border-b border-gray-200 dark:border-gray-700 overflow-x-auto">
            {Array.from(openDocuments.values()).map((openDoc) => {
              const isActive = activeDocId === openDoc.doc.id
              return (
                <div
                  key={openDoc.doc.id}
                  onClick={() => setActiveDocId(openDoc.doc.id)}
                  className={`flex items-center gap-2 px-4 py-2 border-b-2 cursor-pointer whitespace-nowrap ${
                    isActive
                      ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300'
                      : 'border-transparent text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700'
                  }`}
                >
                  <span className="text-sm font-medium">{openDoc.doc.title}</span>
                  {openDoc.hasUnsavedChanges && (
                    <span className="w-2 h-2 rounded-full bg-amber-500"></span>
                  )}
                  <button
                    onClick={(e) => handleCloseTab(openDoc.doc.id, e)}
                    className="ml-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
                  >
                    <X className="w-3 h-3" />
                  </button>
                </div>
              )
            })}
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6 space-y-4">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Document Settings</h3>
          <div className="space-y-3">
            <InputField label="Title" value={title} onChange={setTitle} />
            <InputField label="Theme" value={theme} onChange={setTheme} />
            <SelectField
              label="Document Type"
              value={docType}
              onChange={setDocType}
              options={['Article', 'Story', 'Report', 'Script', 'Blog']}
            />
            <SelectField
              label="Genre/Style"
              value={genre}
              onChange={setGenre}
              options={['Professional', 'Creative', 'Technical', 'Academic', 'Casual']}
            />
            <SelectField
              label="Length"
              value={length}
              onChange={setLength}
              options={['Short (500-1000 words)', 'Medium (1000-2000 words)', 'Long (2000+ words)']}
            />
            <SelectField
              label="AI Assistance"
              value={assistance}
              onChange={setAssistance}
              options={['Minimal', 'Moderate', 'Extensive']}
            />
          </div>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Word Count: <span className="font-semibold text-gray-900 dark:text-white">{wordCount}</span>
          </p>
        </div>

        <div className="lg:col-span-2 space-y-6">
          {activeDoc ? (
            <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
              <textarea
                value={editorContent}
                onChange={(e) => handleContentChange(e.target.value)}
                rows={16}
                className="w-full p-4 rounded-lg bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-gray-100 focus:ring-primary-500 focus:border-primary-500"
                placeholder="Start writing your ideas, or generate a narrative to begin..."
              />
            </div>
          ) : (
            <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-12 text-center">
              <p className="text-gray-500 dark:text-gray-400">No document open. Create a new document or open one from the library.</p>
            </div>
          )}

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <StatCard label="Total Words" value={`${stats?.total_words.toLocaleString() ?? 0}`} />
            <StatCard label="Documents" value={`${stats?.documents ?? 0}`} />
            <StatCard label="Words / Day" value={`${stats?.avg_words_per_day ?? 0}`} />
            <StatCard label="Writing Streak" value={`${stats?.writing_streak ?? 0} days`} />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
          <SectionHeader title="Document Library" icon={<FileEdit className="w-4 h-4 mr-2 text-primary-500" />} />
          <div className="mt-4 max-h-80 overflow-y-auto divide-y divide-gray-200 dark:divide-gray-700">
            {snapshot.documents.map((doc) => (
              <div
                key={doc.id}
                className={`w-full text-left p-4 hover:bg-gray-50 dark:hover:bg-gray-700 ${
                  activeDocId === doc.id ? 'bg-primary-50 dark:bg-primary-900/20' : ''
                }`}
              >
                <div className="flex items-center justify-between">
                  <button
                    onClick={() => handleSelectDocument(doc)}
                    className="flex-1 text-left"
                  >
                    <p className="font-medium text-gray-900 dark:text-white">{doc.title}</p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">{doc.summary}</p>
                  </button>
                  <div className="flex items-center gap-2">
                    <span className="text-xs px-2 py-1 rounded-full bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-200">
                      {doc.status}
                    </span>
                    <button
                      onClick={(e) => handleDeleteDocument(doc.id, e)}
                      className="text-red-500 hover:text-red-700 dark:hover:text-red-400 p-1"
                      title="Delete document"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
          <SectionHeader title="Suggestions" icon={<BookOpen className="w-4 h-4 mr-2 text-primary-500" />} />
          <div className="mt-4 space-y-4 max-h-80 overflow-y-auto pr-2">
            {snapshot.suggestions.map((suggestion: WriterSuggestion) => (
              <div key={suggestion.title} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                <h4 className="font-semibold text-gray-900 dark:text-white">{suggestion.title}</h4>
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{suggestion.body}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
          <SectionHeader title="Lore & Canon" icon={<BookOpen className="w-4 h-4 mr-2 text-primary-500" />} />
          <div className="mt-4 space-y-3 max-h-64 overflow-y-auto">
            {snapshot.canon_entries.map((entry: WriterCanonEntry) => (
              <div key={entry.title} className="border border-gray-200 dark:border-gray-700 rounded-lg p-3">
                <p className="text-xs uppercase text-gray-500 dark:text-gray-400">{entry.category}</p>
                <p className="font-semibold text-gray-900 dark:text-white">{entry.title}</p>
                <p className="text-sm text-gray-600 dark:text-gray-400">{entry.description}</p>
                <p className="text-xs text-gray-400 mt-1">{entry.meta}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
          <SectionHeader title="Publishing Pipeline" icon={<MonitorSmartphone className="w-4 h-4 mr-2 text-primary-500" />} />
          <div className="mt-4 space-y-4 max-h-64 overflow-y-auto">
            {snapshot.pipeline_entries.map((entry: WriterPipelineEntry) => (
              <div key={entry.title} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <h4 className="font-semibold text-gray-900 dark:text-white">{entry.title}</h4>
                  <span className="text-xs px-2 py-1 rounded-full bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-200">
                    {entry.status}
                  </span>
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{entry.summary}</p>
                <p className="text-xs text-gray-400 mt-1">{entry.meta}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

function InputField({
  label,
  value,
  onChange,
}: {
  label: string
  value: string
  onChange: (val: string) => void
}) {
  return (
    <label className="block">
      <span className="text-sm text-gray-600 dark:text-gray-400">{label}</span>
      <input
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="mt-1 w-full rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 px-3 py-2 focus:ring-primary-500 focus:border-primary-500"
      />
    </label>
  )
}

function SelectField({
  label,
  value,
  onChange,
  options,
}: {
  label: string
  value: string
  onChange: (val: string) => void
  options: string[]
}) {
  return (
    <label className="block">
      <span className="text-sm text-gray-600 dark:text-gray-400">{label}</span>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="mt-1 w-full rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 px-3 py-2 focus:ring-primary-500 focus:border-primary-500"
      >
        {options.map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
    </label>
  )
}

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-4">
      <p className="text-sm text-gray-500 dark:text-gray-400">{label}</p>
      <p className="text-xl font-semibold text-gray-900 dark:text-white">{value}</p>
    </div>
  )
}

function SectionHeader({ title, icon }: { title: string; icon: ReactNode }) {
  return (
    <div className="flex items-center">
      {icon}
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{title}</h3>
    </div>
  )
}
