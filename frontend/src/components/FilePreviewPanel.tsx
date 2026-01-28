import { useState, useEffect } from 'react'
import { Search, RefreshCw, FileText, Loader2 } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import apiClient, { apiPath } from '../lib/apiClient'
import { toast } from '../utils/toast'

interface FilePreviewPanelProps {
  className?: string
}

interface FileContentResponse {
  content: string
  path: string
  mtime?: string
}

const fetchFileContent = async (filePath: string): Promise<FileContentResponse> => {
  const { data } = await apiClient.get<FileContentResponse>(
    apiPath(`files/preview?path=${encodeURIComponent(filePath)}`)
  )
  return data
}

export default function FilePreviewPanel({ className = '' }: FilePreviewPanelProps) {
  const [activeFilePath, setActiveFilePath] = useState<string | null>(null)
  const [localFileContent, setLocalFileContent] = useState<string | null>(null)
  const [isLocalFile, setIsLocalFile] = useState(false)

  const { data: fileContent, isLoading, refetch } = useQuery({
    queryKey: ['file-preview', activeFilePath],
    queryFn: () => fetchFileContent(activeFilePath!),
    enabled: !!activeFilePath && !isLocalFile,
    refetchInterval: 5000, // Refresh every 5 seconds to watch for changes
  })

  const handleChooseFile = () => {
    // Create a file input element
    const input = document.createElement('input')
    input.type = 'file'
    input.style.display = 'none'
    input.onchange = async (e) => {
      const file = (e.target as HTMLInputElement).files?.[0]
      if (!file) {
        document.body.removeChild(input)
        return
      }

      // Read the file content directly for local preview
      const reader = new FileReader()
      reader.onload = (event) => {
        const content = event.target?.result as string
        setActiveFilePath(file.name)
        setLocalFileContent(content)
        setIsLocalFile(true)
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

  return (
    <div className={`flex flex-col h-full bg-slate-900/50 border-l border-slate-700/50 ${className}`}>
      {/* Header - Enhanced */}
      <div className="p-4 border-b border-slate-700/50 bg-gradient-to-r from-slate-900/95 to-slate-800/95 backdrop-blur-sm">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2.5">
            <div className="p-1.5 rounded-lg bg-gradient-to-br from-primary-500/20 to-violet-500/20 border border-primary-500/30">
              <FileText className="w-4 h-4 text-primary-400" />
            </div>
            <div>
              <h4 className="text-xs font-semibold text-slate-200 uppercase tracking-wider">File Preview</h4>
              <p className="text-[10px] text-slate-500 mt-0.5">Watch files for changes</p>
            </div>
          </div>
        </div>

        {/* Status */}
        <div className="mb-3">
          {activeFilePath ? (
            <div className="flex items-center gap-2 px-2 py-1.5 bg-primary-500/10 border border-primary-500/30 rounded-lg">
              <div className="flex-1 min-w-0">
                <p className="text-[10px] text-slate-400 mb-0.5">Active File</p>
                <p className="text-xs text-primary-300 font-medium truncate" title={activeFilePath}>
                  {activeFilePath}
                </p>
              </div>
              {isLocalFile && (
                <span className="px-1.5 py-0.5 text-[9px] bg-slate-700/50 text-slate-300 rounded border border-slate-600">
                  Local
                </span>
              )}
            </div>
          ) : (
            <div className="px-2 py-1.5 bg-slate-800/50 border border-slate-700/50 rounded-lg">
              <p className="text-[10px] text-slate-500">No file selected</p>
            </div>
          )}
        </div>

        {/* Buttons - Enhanced */}
        <div className="flex gap-2">
          <button
            onClick={handleChooseFile}
            className="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 bg-slate-800/80 text-slate-300 rounded-lg hover:bg-slate-700 hover:text-slate-200 transition-all text-[11px] font-medium border border-slate-700/60 hover:border-slate-600"
          >
            <Search className="w-3.5 h-3.5" />
            Choose File
          </button>
          <button
            onClick={() => refetch()}
            disabled={!activeFilePath || isLoading}
            className="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 bg-slate-800/80 text-slate-300 rounded-lg hover:bg-slate-700 hover:text-slate-200 transition-all text-[11px] font-medium disabled:opacity-50 disabled:cursor-not-allowed border border-slate-700/60 hover:border-slate-600"
            title={activeFilePath ? 'Refresh file content' : 'Select a file first'}
          >
            {isLoading ? (
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
            ) : (
              <RefreshCw className="w-3.5 h-3.5" />
            )}
            Refresh
          </button>
        </div>
      </div>

      {/* File Content */}
      <div className="flex-1 overflow-y-auto p-4">
        {!activeFilePath ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center max-w-sm px-4">
              <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-primary-500/20 to-violet-500/20 flex items-center justify-center">
                <FileText className="w-8 h-8 text-primary-400" />
              </div>
              <p className="text-sm font-medium text-slate-300 mb-2">No file selected</p>
              <p className="text-xs text-slate-500 mb-4">
                Choose a file to preview and share with the AI assistant
              </p>
              <button
                onClick={handleChooseFile}
                className="px-4 py-2 bg-primary-500/20 hover:bg-primary-500/30 border border-primary-500/30 rounded-lg text-sm text-primary-300 transition-colors"
              >
                Choose File
              </button>
            </div>
          </div>
        ) : isLoading ? (
          <div className="flex flex-col items-center justify-center h-full">
            <Loader2 className="w-8 h-8 text-primary-400 animate-spin mb-3" />
            <p className="text-xs text-slate-400">Loading file content...</p>
          </div>
        ) : (fileContent || localFileContent) ? (
          <div className="h-full flex flex-col">
            <div className="mb-2 flex items-center justify-between text-[10px] text-slate-500">
              <span>File content preview</span>
              {fileContent?.mtime && (
                <span>Last modified: {new Date(fileContent.mtime).toLocaleString()}</span>
              )}
            </div>
            <div className="flex-1 overflow-y-auto bg-slate-900/60 border border-slate-700/60 rounded-lg p-4 text-xs text-slate-200 whitespace-pre-wrap font-mono leading-relaxed scroll-smooth">
              {fileContent?.content || localFileContent || 'File is empty'}
            </div>
            {activeFilePath && !isLocalFile && (
              <div className="mt-2 text-[9px] text-slate-500 flex items-center gap-1.5">
                <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                <span>Auto-refreshing every 5 seconds</span>
              </div>
            )}
          </div>
        ) : (
          <div className="flex items-center justify-center h-full">
            <div className="text-center max-w-sm px-4">
              <div className="w-12 h-12 mx-auto mb-3 rounded-xl bg-rose-500/10 flex items-center justify-center">
                <FileText className="w-6 h-6 text-rose-400" />
              </div>
              <p className="text-sm font-medium text-slate-300 mb-1">Unable to load file</p>
              <p className="text-xs text-slate-500 mb-3">
                The file may not be accessible or the preview API is unavailable
              </p>
              <button
                onClick={handleChooseFile}
                className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-lg text-xs text-slate-300 transition-colors"
              >
                Try Another File
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

