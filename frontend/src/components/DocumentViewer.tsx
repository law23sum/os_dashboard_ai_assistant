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
                </div>
              </div>
            )}
            
            {activeView === 'hex' && (
              <div className="space-y-2">
                <div className="text-sm text-[color:var(--osd-muted)]">
                  Offset: {content.offset}, Length: {content.length} / {content.total_size}
                </div>
                <pre className="bg-[color:var(--osd-surface)] p-4 rounded-lg overflow-auto max-h-96 font-mono text-xs">
                  {content.hex_dump?.join('\n') || content.hex || 'No hex data available'}
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
                  Pages: {content.num_pages || 'N/A'}
                </div>
                {content.base64_data && (
                  <iframe src={content.base64_data} className="w-full h-96 rounded-lg" title="PDF Viewer" />
                )}
              </div>
            )}
            
            {activeView === 'json' && (
              <pre className="bg-[color:var(--osd-surface)] p-4 rounded-lg overflow-auto max-h-96 font-mono text-xs">
                {JSON.stringify(content.content || content, null, 2)}
              </pre>
            )}
          </div>
        ) : (
          <div className="text-center py-12 text-[color:var(--osd-muted)]">
            Select a view type to load content
          </div>
        )}
      </div>
    </div>
  )
}
