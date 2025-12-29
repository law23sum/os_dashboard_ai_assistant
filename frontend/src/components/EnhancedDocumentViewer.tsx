import { useState } from 'react'
import {
  FileText,
  Code,
  Hexagon,
  Image as ImageIcon,
  FileJson,
  FileSpreadsheet,
  FileType,
  Binary,
  Eye,
  GitBranch,
  ChevronDown,
  ChevronUp,
} from 'lucide-react'
import type { ChatDocument } from '../types/documents'

type ViewFormat = 
  | 'raw'
  | 'hex'
  | 'binary'
  | 'image'
  | 'pdf'
  | 'excel'
  | 'powerpoint'
  | 'json'
  | 'csv'
  | 'markdown'
  | 'code'

interface EnhancedDocumentViewerProps {
  document: ChatDocument | null
  onDocumentUpdate?: (doc: ChatDocument) => void
}

export default function EnhancedDocumentViewer({ document, onDocumentUpdate }: EnhancedDocumentViewerProps) {
  const [viewFormat, setViewFormat] = useState<ViewFormat>('raw')
  const [showVersionControl, setShowVersionControl] = useState(false)
  const [selectedVersions, setSelectedVersions] = useState<string[]>([])
  
  if (!document) {
    return (
      <div className="flex items-center justify-center h-full text-slate-400">
        <div className="text-center">
          <FileText className="w-12 h-12 mx-auto mb-3 opacity-50" />
          <p>No document selected</p>
        </div>
      </div>
    )
  }

  const viewFormats: Array<{ format: ViewFormat; icon: any; label: string }> = [
    { format: 'raw', icon: FileText, label: 'Raw Text' },
    { format: 'hex', icon: Hexagon, label: 'Hexadecimal' },
    { format: 'binary', icon: Binary, label: 'Binary' },
    { format: 'image', icon: ImageIcon, label: 'Image' },
    { format: 'pdf', icon: FileType, label: 'PDF' },
    { format: 'excel', icon: FileSpreadsheet, label: 'Excel' },
    { format: 'powerpoint', icon: FileType, label: 'PowerPoint' },
    { format: 'json', icon: FileJson, label: 'JSON' },
    { format: 'csv', icon: FileSpreadsheet, label: 'CSV' },
    { format: 'markdown', icon: FileText, label: 'Markdown' },
    { format: 'code', icon: Code, label: 'Code' },
  ]

  // Mock versions - in real implementation, fetch from backend
  const versions = [
    { id: 'v1', timestamp: '2025-12-19 10:30', author: 'Alice', changes: '+15 -3' },
    { id: 'v2', timestamp: '2025-12-19 11:45', author: 'Bob', changes: '+8 -12' },
    { id: 'v3', timestamp: '2025-12-19 14:20', author: 'Charlie', changes: '+25 -7' },
  ]

  const toggleVersionSelection = (versionId: string) => {
    setSelectedVersions(prev => {
      if (prev.includes(versionId)) {
        return prev.filter(id => id !== versionId)
      }
      if (prev.length < 3) {
        return [...prev, versionId]
      }
      return prev
    })
  }

  return (
    <div className="h-full flex flex-col bg-slate-900/50">
      {/* Header with Format Tabs */}
      <div className="border-b border-slate-700/50 bg-slate-800/30">
        <div className="px-4 py-3">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold text-white">{document.original_name}</h3>
            <button
              onClick={() => setShowVersionControl(!showVersionControl)}
              className="flex items-center gap-2 px-3 py-1.5 bg-slate-800/80 hover:bg-slate-700 border border-slate-700/60 rounded-lg transition-colors text-xs text-slate-300"
            >
              <GitBranch className="w-3.5 h-3.5" />
              <span>Version Control</span>
              {showVersionControl ? (
                <ChevronUp className="w-3.5 h-3.5" />
              ) : (
                <ChevronDown className="w-3.5 h-3.5" />
              )}
            </button>
          </div>

          {/* Format Tabs */}
          <div className="flex gap-1 overflow-x-auto pb-1">
            {viewFormats.map(({ format, icon: Icon, label }) => (
              <button
                key={format}
                onClick={() => setViewFormat(format)}
                className={`
                  flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition-all
                  ${viewFormat === format
                    ? 'bg-primary-500/20 text-primary-300 border border-primary-500/30'
                    : 'text-slate-400 hover:text-slate-300 hover:bg-slate-800/50'
                  }
                `}
              >
                <Icon className="w-3.5 h-3.5" />
                {label}
              </button>
            ))}
          </div>
        </div>

        {/* Version Control Panel (Collapsible) */}
        {showVersionControl && (
          <div className="px-4 pb-3 border-t border-slate-700/50 pt-3">
            <div className="flex items-center justify-between mb-2">
              <p className="text-xs font-semibold text-slate-300">
                Select up to 3 versions to compare
              </p>
              {selectedVersions.length > 0 && (
                <button
                  onClick={() => setSelectedVersions([])}
                  className="text-xs text-primary-400 hover:text-primary-300"
                >
                  Clear selection
                </button>
              )}
            </div>
            <div className="grid gap-2 max-h-48 overflow-y-auto">
              {versions.map((version) => (
                <button
                  key={version.id}
                  onClick={() => toggleVersionSelection(version.id)}
                  className={`
                    flex items-center justify-between p-2.5 rounded-lg text-left transition-all
                    ${selectedVersions.includes(version.id)
                      ? 'bg-primary-500/20 border border-primary-500/30'
                      : 'bg-slate-800/50 border border-slate-700/50 hover:border-slate-600'
                    }
                  `}
                >
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs text-primary-400">{version.id}</span>
                      <span className="text-xs text-slate-400">{version.timestamp}</span>
                    </div>
                    <p className="text-xs text-slate-300 mt-0.5">
                      by {version.author} • {version.changes}
                    </p>
                  </div>
                  {selectedVersions.includes(version.id) && (
                    <div className="ml-2 flex items-center justify-center w-5 h-5 bg-primary-500 rounded-full">
                      <span className="text-xs font-bold text-white">
                        {selectedVersions.indexOf(version.id) + 1}
                      </span>
                    </div>
                  )}
                </button>
              ))}
            </div>
            {selectedVersions.length > 1 && (
              <div className="mt-3 flex gap-2">
                <button className="flex-1 px-3 py-2 bg-primary-500/20 hover:bg-primary-500/30 border border-primary-500/30 rounded-lg text-xs font-medium text-primary-300 transition-colors">
                  Compare Selected ({selectedVersions.length})
                </button>
                <button className="px-3 py-2 bg-slate-800/80 hover:bg-slate-700 border border-slate-700/60 rounded-lg text-xs font-medium text-slate-300 transition-colors">
                  Merge Info
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-auto p-4">
        {renderContent(viewFormat, document, selectedVersions)}
      </div>
    </div>
  )
}

function renderContent(format: ViewFormat, document: ChatDocument, selectedVersions: string[]) {
  // If comparing versions, show diff view
  if (selectedVersions.length > 1) {
    return (
      <div className="space-y-4">
        <div className="flex items-center gap-2 px-4 py-2 bg-primary-500/10 border border-primary-500/30 rounded-xl">
          <Eye className="w-4 h-4 text-primary-400" />
          <span className="text-sm font-medium text-primary-300">
            Comparing {selectedVersions.length} versions
          </span>
        </div>
        <div className="grid gap-4" style={{ gridTemplateColumns: `repeat(${selectedVersions.length}, 1fr)` }}>
          {selectedVersions.map((versionId, index) => (
            <div key={versionId} className="border border-slate-700/50 rounded-xl overflow-hidden">
              <div className="px-3 py-2 bg-slate-800/50 border-b border-slate-700/50">
                <p className="text-xs font-semibold text-white">Version {versionId}</p>
              </div>
              <div className="p-3 bg-slate-800/20 font-mono text-xs text-slate-300">
                <pre className="whitespace-pre-wrap">
                  {`// Content for ${versionId}\n// Line 1: ${document.original_name}\n// Line 2: Sample diff content ${index + 1}\n// Line 3: More changes here...`}
                </pre>
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  // Single document view based on format
  switch (format) {
    case 'hex':
      return <HexView document={document} />
    case 'binary':
      return <BinaryView document={document} />
    case 'image':
      return <ImageView document={document} />
    case 'json':
      return <JsonView document={document} />
    case 'csv':
      return <CsvView document={document} />
    case 'markdown':
      return <MarkdownView document={document} />
    case 'code':
      return <CodeView document={document} />
    default:
      return <RawView document={document} />
  }
}

function HexView({ document }: { document: ChatDocument }) {
  // Mock hex dump
  const hexContent = Array.from({ length: 16 }, (_, i) => {
    const offset = (i * 16).toString(16).padStart(8, '0')
    const hex = Array.from({ length: 16 }, (_, j) => 
      ((i * 16 + j) % 256).toString(16).padStart(2, '0')
    ).join(' ')
    const ascii = Array.from({ length: 16 }, () => '.')
    return `${offset}  ${hex}  ${ascii.join('')}`
  }).join('\n')

  return (
    <div className="p-4 bg-slate-900/80 border border-slate-700/50 rounded-xl">
      <pre className="font-mono text-xs text-green-400">
        {hexContent}
      </pre>
    </div>
  )
}

function BinaryView({ document }: { document: ChatDocument }) {
  return (
    <div className="p-4 bg-slate-900/80 border border-slate-700/50 rounded-xl">
      <p className="text-sm text-slate-400 mb-3">Binary representation:</p>
      <pre className="font-mono text-xs text-cyan-400 overflow-x-auto">
        {Array.from({ length: 8 }, () => 
          Array.from({ length: 8 }, () => Math.random() > 0.5 ? '1' : '0').join('')
        ).join(' ')}
      </pre>
    </div>
  )
}

function ImageView({ document }: { document: ChatDocument }) {
  return (
    <div className="flex items-center justify-center h-full">
      <div className="text-center">
        <ImageIcon className="w-16 h-16 mx-auto mb-4 text-slate-500" />
        <p className="text-sm text-slate-400">Image preview for: {document.original_name}</p>
        <p className="text-xs text-slate-500 mt-1">Image rendering would appear here</p>
      </div>
    </div>
  )
}

function JsonView({ document }: { document: ChatDocument }) {
  const mockJson = {
    document_name: document.original_name,
    type: 'json',
    created_at: new Date().toISOString(),
    metadata: {
      version: '1.0',
      author: 'System',
    },
  }

  return (
    <div className="p-4 bg-slate-900/80 border border-slate-700/50 rounded-xl">
      <pre className="font-mono text-xs text-slate-300">
        {JSON.stringify(mockJson, null, 2)}
      </pre>
    </div>
  )
}

function CsvView({ document }: { document: ChatDocument }) {
  const mockData = [
    ['Name', 'Age', 'Role', 'Department'],
    ['Alice', '28', 'Engineer', 'Development'],
    ['Bob', '34', 'Designer', 'Product'],
    ['Charlie', '31', 'Manager', 'Operations'],
  ]

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm border-collapse">
        <thead>
          <tr className="bg-slate-800/50">
            {mockData[0].map((header, i) => (
              <th key={i} className="px-4 py-2 text-left text-slate-300 font-semibold border-b border-slate-700/50">
                {header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {mockData.slice(1).map((row, i) => (
            <tr key={i} className="hover:bg-slate-800/30">
              {row.map((cell, j) => (
                <td key={j} className="px-4 py-2 text-slate-300 border-b border-slate-700/30">
                  {cell}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function MarkdownView({ document }: { document: ChatDocument }) {
  return (
    <div className="prose prose-invert max-w-none">
      <h1>Document: {document.original_name}</h1>
      <p>This is a markdown preview of the document.</p>
      <h2>Features</h2>
      <ul>
        <li>Support for headings</li>
        <li>Lists and formatting</li>
        <li>Code blocks</li>
      </ul>
    </div>
  )
}

function CodeView({ document }: { document: ChatDocument }) {
  const mockCode = `// Example code view for ${document.original_name}
function processDocument(doc) {
  const result = parseContent(doc);
  return formatOutput(result);
}

export default processDocument;`

  return (
    <div className="p-4 bg-slate-900/80 border border-slate-700/50 rounded-xl">
      <pre className="font-mono text-sm text-slate-300">
        {mockCode}
      </pre>
    </div>
  )
}

function RawView({ document }: { document: ChatDocument }) {
  return (
    <div className="p-4 bg-slate-900/80 border border-slate-700/50 rounded-xl">
      <pre className="font-mono text-sm text-slate-300 whitespace-pre-wrap">
        {`Raw content of ${document.original_name}\n\nThis would contain the actual file content in raw text format.`}
      </pre>
    </div>
  )
}
