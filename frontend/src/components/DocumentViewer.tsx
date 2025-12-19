import { useState } from 'react'
import { FileText, Binary, Hex, Image, File, FileSpreadsheet, FileJson } from 'lucide-react'

interface DocumentViewerProps {
  documentId: string
  filename: string
  fileType: string
}

const VIEW_TYPES = [
  { id: 'text', label: 'Text', icon: FileText },
  { id: 'binary', label: 'Binary', icon: Binary },
  { id: 'hex', label: 'Hex', icon: Hex },
  { id: 'image', label: 'Image', icon: Image },
  { id: 'pdf', label: 'PDF', icon: File },
  { id: 'powerpoint', label: 'PowerPoint', icon: File },
  { id: 'excel', label: 'Excel', icon: FileSpreadsheet },
  { id: 'csv', label: 'CSV', icon: FileSpreadsheet },
  { id: 'json', label: 'JSON', icon: FileJson },
]

export default function DocumentViewer({ documentId, filename, fileType }: DocumentViewerProps) {
  const [activeView, setActiveView] = useState('text')
  const [content, setContent] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  const loadView = async (viewType: string) => {
    setLoading(true)
    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch(`/api/viewer/documents/${documentId}/view/${viewType}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })
      if (response.ok) {
        const data = await response.json()
        setContent(data.content)
        setActiveView(viewType)
      }
    } catch (error) {
      console.error('Failed to load view:', error)
    } finally {
      setLoading(false)
    }
  }

  // Determine available views based on file type
  const getAvailableViews = () => {
    const ext = filename.toLowerCase().split('.').pop() || ''
    const available = ['text', 'binary', 'hex'] // Always available
    
    if (['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'].includes(ext)) {
      available.push('image')
    }
    if (ext === 'pdf') {
      available.push('pdf')
    }
    if (['ppt', 'pptx'].includes(ext)) {
      available.push('powerpoint')
    }
    if (['xls', 'xlsx', 'xlsm'].includes(ext)) {
      available.push('excel')
    }
    if (ext === 'csv') {
      available.push('csv')
    }
    if (ext === 'json') {
      available.push('json')
    }
    
    return available
  }

  const availableViews = getAvailableViews()

  return (
    <div className="glass-content rounded-lg">
      {/* View Type Tabs */}
      <div className="border-b border-[color:var(--osd-border)] flex overflow-x-auto">
        {VIEW_TYPES.filter((view) => availableViews.includes(view.id)).map((view) => {
          const Icon = view.icon
          return (
            <button
              key={view.id}
              onClick={() => loadView(view.id)}
              className={`px-4 py-3 flex items-center gap-2 border-b-2 transition-colors ${
                activeView === view.id
                  ? 'border-[color:var(--osd-accent)] text-[color:var(--osd-accent)]'
                  : 'border-transparent text-[color:var(--osd-muted)] hover:text-[color:var(--osd-text)]'
              }`}
            >
              <Icon className="w-4 h-4" />
              {view.label}
            </button>
          )
        })}
      </div>

      {/* Content Area */}
      <div className="p-6">
        {loading ? (
          <div className="text-center py-12 text-[color:var(--osd-muted)]">Loading view...</div>
        ) : content ? (
          <div className="space-y-4">
            {activeView === 'text' && (
              <pre className="bg-[color:var(--osd-surface)] p-4 rounded-lg overflow-auto max-h-96 whitespace-pre-wrap">
                {content.content}
              </pre>
            )}
            
            {activeView === 'binary' && (
              <div className="space-y-2">
                <div className="text-sm text-[color:var(--osd-muted)]">
                  Size: {content.total_size} bytes
                </div>
                <div className="bg-[color:var(--osd-surface)] p-4 rounded-lg font-mono text-xs overflow-auto max-h-96">
                  {content.preview}
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
            )}
            
            {activeView === 'hex' && (
              <div className="space-y-2">
                <div className="text-sm text-[color:var(--osd-muted)]">
                  Offset: {content.offset}, Length: {content.length} / {content.total_size}
                </div>
                <pre className="bg-[color:var(--osd-surface)] p-4 rounded-lg overflow-auto max-h-96 font-mono text-xs">
                  {content.hex_dump.join('\n')}
                </pre>
              </div>
            )}
            
            {activeView === 'image' && content.base64_data && (
              <div className="flex justify-center">
                <img src={content.base64_data} alt={filename} className="max-w-full max-h-96 rounded-lg" />
              </div>
            )}
            
            {activeView === 'pdf' && (
              <div className="space-y-4">
                <div className="text-sm text-[color:var(--osd-muted)]">
                  Pages: {content.num_pages}
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
                {content.text_content?.map((page: any, idx: number) => (
                  <div key={idx} className="bg-[color:var(--osd-surface)] p-4 rounded-lg">
                    <h4 className="font-semibold mb-2">Page {page.page}</h4>
                    <pre className="text-sm whitespace-pre-wrap">{page.text}</pre>
                  </div>
                ))}
              </div>
            )}
            
            {activeView === 'excel' && (
              <div className="space-y-4">
                <div className="text-sm text-[color:var(--osd-muted)]">
                  Sheet: {content.current_sheet} ({content.num_rows} rows, {content.num_columns} columns)
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
                <div className="overflow-x-auto">
                  <table className="w-full text-sm border-collapse">
                    <thead>
                      <tr>
                        {content.columns?.map((col: string) => (
                          <th key={col} className="border border-[color:var(--osd-border)] px-2 py-1 bg-[color:var(--osd-surface)]">
                            {col}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {content.data?.map((row: any, idx: number) => (
                        <tr key={idx}>
                          {content.columns?.map((col: string) => (
                            <td key={col} className="border border-[color:var(--osd-border)] px-2 py-1">
                              {String(row[col] || '')}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
            
            {activeView === 'csv' && (
              <div className="space-y-4">
                <div className="text-sm text-[color:var(--osd-muted)]">
                  Delimiter: "{content.delimiter}" ({content.num_rows} rows, {content.num_columns} columns)
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm border-collapse">
                    <thead>
                      <tr>
                        {content.columns?.map((col: string) => (
                          <th key={col} className="border border-[color:var(--osd-border)] px-2 py-1 bg-[color:var(--osd-surface)]">
                            {col}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {content.data?.map((row: any, idx: number) => (
                        <tr key={idx}>
                          {content.columns?.map((col: string) => (
                            <td key={col} className="border border-[color:var(--osd-border)] px-2 py-1">
                              {String(row[col] || '')}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
            
            {activeView === 'json' && (
              <pre className="bg-[color:var(--osd-surface)] p-4 rounded-lg overflow-auto max-h-96 text-sm">
                {content.formatted}
              </pre>
            )}
          </div>
        ) : (
          <div className="text-center py-12 text-[color:var(--osd-muted)]">
            Select a view type to display the document
          </div>
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
