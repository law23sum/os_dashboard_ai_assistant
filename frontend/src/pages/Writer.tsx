import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useState, useMemo, ReactNode } from 'react'
import { Plus, FileEdit, BookOpen, Wand2, Save, Loader2, MonitorSmartphone } from 'lucide-react'
import apiClient, { apiPath } from '../lib/apiClient'
import {
  WriterSnapshot,
  WriterDocument,
  WriterStats,
  WriterSuggestion,
  WriterPipelineEntry,
  WriterCanonEntry,
} from '../types'

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

const generateNarrative = async (payload: {
  doc_type: string
  theme: string
  genre: string
  title: string
}): Promise<string> => {
  const { data } = await apiClient.post<{ content: string }>(apiPath('writer/generate'), payload)
  return data.content
}

export default function Writer() {
  const [title, setTitle] = useState('')
  const [theme, setTheme] = useState('')
  const [docType, setDocType] = useState('Article')
  const [genre, setGenre] = useState('Professional')
  const [assistance, setAssistance] = useState('Minimal')
  const [length, setLength] = useState('Short (500-1000 words)')
  const [editorContent, setEditorContent] = useState('')
  const [activeDoc, setActiveDoc] = useState<WriterDocument | null>(null)

  const queryClient = useQueryClient()
  const snapshotQuery = useQuery({
    queryKey: ['writer-snapshot'],
    queryFn: fetchSnapshot,
    refetchInterval: 30000,
    onSuccess: (snapshot) => {
      if (!activeDoc && snapshot.documents.length) {
        setActiveDoc(snapshot.documents[0])
        setEditorContent(snapshot.documents[0].content ?? '')
        setTitle(snapshot.documents[0].title)
        setTheme(snapshot.documents[0].theme)
        setDocType(snapshot.documents[0].type)
      }
    },
  })

  const createMutation = useMutation({
    mutationFn: createDocument,
    onSuccess: (doc) => {
      queryClient.invalidateQueries({ queryKey: ['writer-snapshot'] })
      setActiveDoc(doc)
      setEditorContent('')
    },
  })

  const saveMutation = useMutation({
    mutationFn: saveDocument,
    onSuccess: (doc) => {
      setActiveDoc(doc)
      queryClient.invalidateQueries({ queryKey: ['writer-snapshot'] })
    },
  })

  const loadMutation = useMutation({
    mutationFn: loadDocument,
    onSuccess: (doc) => {
      setActiveDoc(doc)
      setEditorContent(doc.content ?? '')
      setTitle(doc.title)
      setDocType(doc.type)
      setTheme(doc.theme)
    },
  })

  const generateMutation = useMutation({
    mutationFn: generateNarrative,
    onSuccess: (content) => {
      setEditorContent(content)
    },
  })

  const snapshot = snapshotQuery.data

  const stats: WriterStats | undefined = snapshot?.stats
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
    if (!activeDoc) return
    saveMutation.mutate({ id: activeDoc.id, content: editorContent })
  }

  const handleGenerate = () => {
    generateMutation.mutate({
      doc_type: docType,
      theme: theme || 'adventure',
      genre,
      title: title || 'Untitled Narrative',
    })
  }

  const handleSelectDocument = (doc: WriterDocument) => {
    loadMutation.mutate(doc.id)
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
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Writer Workspace</h2>
          <p className="text-gray-600 dark:text-gray-400">
            Shared writing environment with AI assistance for both desktop and web.
          </p>
        </div>
        <div className="flex gap-3">
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
            disabled={generateMutation.isPending}
            className="inline-flex items-center px-4 py-2 rounded-md border border-transparent text-sm font-medium bg-gray-900 text-white hover:bg-gray-800"
          >
            {generateMutation.isPending ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Wand2 className="w-4 h-4 mr-2" />}
            Generate Narrative
          </button>
        </div>
      </div>

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
          <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
            <textarea
              value={editorContent}
              onChange={(e) => setEditorContent(e.target.value)}
              rows={16}
              className="w-full p-4 rounded-lg bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-gray-100 focus:ring-primary-500 focus:border-primary-500"
              placeholder="Start writing your ideas, or generate a narrative to begin..."
            />
          </div>

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
              <button
                key={doc.id}
                onClick={() => handleSelectDocument(doc)}
                className={`w-full text-left p-4 hover:bg-gray-50 dark:hover:bg-gray-700 ${
                  activeDoc?.id === doc.id ? 'bg-primary-50 dark:bg-primary-900/20' : ''
                }`}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">{doc.title}</p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">{doc.summary}</p>
                  </div>
                  <span className="text-xs px-2 py-1 rounded-full bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-200">
                    {doc.status}
                  </span>
                </div>
              </button>
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
