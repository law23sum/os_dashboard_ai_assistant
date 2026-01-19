import { useState, useRef, useCallback, useEffect } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import {
  Database,
  Upload,
  Search,
  Trash2,
  Edit,
  Plus,
  FileText,
  Settings,
  CheckCircle,
  XCircle,
  Clock,
  Loader2,
  AlertCircle,
  Info,
  RefreshCw,
  FileCheck,
  Sliders,
} from 'lucide-react'
import { toast } from '../utils/toast'
import {
  VectorStore,
  listVectorStores,
  createVectorStore,
  getVectorStore,
  updateVectorStore,
  deleteVectorStore,
  uploadFile,
  listVectorStoreFiles,
  addFilesToVectorStore,
  batchAddFiles,
  deleteVectorStoreFile,
  searchVectorStore,
  type FileUploadResponse,
  type VectorStoreFile,
} from '../api/vectorStores'

export default function VectorStores() {
  const queryClient = useQueryClient()
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [selectedStoreId, setSelectedStoreId] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [isDragging, setIsDragging] = useState(false)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showSettingsModal, setShowSettingsModal] = useState(false)
  const [newStoreName, setNewStoreName] = useState('')
  const [expirationDays, setExpirationDays] = useState<number | undefined>(undefined)
  const [selectedFiles, setSelectedFiles] = useState<File[]>([])

  // Fetch vector stores
  const { data: stores = [], isLoading, refetch } = useQuery({
    queryKey: ['vector-stores'],
    queryFn: () => listVectorStores({ limit: 100, order: 'desc' }),
  })

  const selectedStore = selectedStoreId
    ? stores.find((s) => s.id === selectedStoreId)
    : null

  // Fetch files in selected store
  const { data: storeFiles = [], refetch: refetchFiles } = useQuery({
    queryKey: ['vector-store-files', selectedStoreId],
    queryFn: () => listVectorStoreFiles(selectedStoreId!),
    enabled: !!selectedStoreId,
  })

  // Create vector store mutation
  const createMutation = useMutation({
    mutationFn: (name: string) =>
      createVectorStore({
        name,
        expires_after_days: expirationDays || undefined,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['vector-stores'] })
      setShowCreateModal(false)
      setNewStoreName('')
      setExpirationDays(undefined)
      toast.success('Vector store created successfully')
    },
    onError: (error: any) => {
      toast.error(error?.message || 'Failed to create vector store')
    },
  })

  // Upload file mutation
  const uploadMutation = useMutation({
    mutationFn: async (file: File): Promise<FileUploadResponse> => {
      return uploadFile(file, 'assistants')
    },
    onError: (error: any) => {
      toast.error(error?.message || 'Failed to upload file')
    },
  })

  // Add files to store mutation
  const addFilesMutation = useMutation({
    mutationFn: async ({ storeId, fileIds }: { storeId: string; fileIds: string[] }) => {
      return addFilesToVectorStore(storeId, { file_ids: fileIds })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['vector-store-files', selectedStoreId] })
      toast.success('Files added to vector store')
      setSelectedFiles([])
    },
    onError: (error: any) => {
      toast.error(error?.message || 'Failed to add files')
    },
  })

  // Delete store mutation
  const deleteMutation = useMutation({
    mutationFn: deleteVectorStore,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['vector-stores'] })
      if (selectedStoreId) setSelectedStoreId(null)
      toast.success('Vector store deleted')
    },
    onError: (error: any) => {
      toast.error(error?.message || 'Failed to delete vector store')
    },
  })

  const deleteFileMutation = useMutation({
    mutationFn: ({ storeId, fileId }: { storeId: string; fileId: string }) =>
      deleteVectorStoreFile(storeId, fileId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['vector-store-files', selectedStoreId] })
      toast.success('File removed from vector store')
    },
    onError: (error: any) => {
      toast.error(error?.message || 'Failed to remove file')
    },
  })

  // Search mutation
  const searchMutation = useMutation({
    mutationFn: ({ storeId, query }: { storeId: string; query: string }) =>
      searchVectorStore(storeId, query, 10),
    onError: (error: any) => {
      toast.error(error?.message || 'Search failed')
    },
  })

  // Handle file selection
  const handleFileSelect = useCallback(async (files: FileList | null) => {
    if (!files || files.length === 0 || !selectedStoreId) return

    const fileArray = Array.from(files)
    setSelectedFiles(fileArray)

    try {
      // Upload all files first
      const uploadPromises = fileArray.map((file) => uploadMutation.mutateAsync(file))
      const uploadedFiles = await Promise.all(uploadPromises)

      // Add to vector store
      const fileIds = uploadedFiles.map((f) => f.file_id)
      await addFilesMutation.mutateAsync({ storeId: selectedStoreId, fileIds })
    } catch (error) {
      console.error('File upload/add error:', error)
    }
  }, [selectedStoreId, uploadMutation, addFilesMutation])

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = () => {
    setIsDragging(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    handleFileSelect(e.dataTransfer.files)
  }

  const handleDeleteStore = (storeId: string) => {
    if (confirm('Are you sure you want to delete this vector store?')) {
      deleteMutation.mutate(storeId)
    }
  }

  const handleSearch = () => {
    if (!selectedStoreId || !searchQuery.trim()) return
    searchMutation.mutate({ storeId: selectedStoreId, query: searchQuery })
  }

  const formatBytes = (bytes?: number) => {
    if (!bytes) return 'N/A'
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
  }

  const formatDate = (timestamp?: number) => {
    if (!timestamp) return 'N/A'
    return new Date(timestamp * 1000).toLocaleDateString()
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Loader2 className="w-8 h-8 text-primary-400 animate-spin" />
      </div>
    )
  }

  return (
    <div className="h-screen flex flex-col bg-slate-900 text-white">
      {/* Header */}
      <div className="border-b border-slate-700 bg-slate-800/50 backdrop-blur-sm px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Database className="w-6 h-6 text-primary-400" />
            <h1 className="text-2xl font-bold">Vector Stores</h1>
            <span className="text-sm text-slate-400">({stores.length} stores)</span>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => refetch()}
              className="px-3 py-2 text-sm bg-slate-700 hover:bg-slate-600 rounded-lg transition-colors flex items-center gap-2"
            >
              <RefreshCw className="w-4 h-4" />
              Refresh
            </button>
            <button
              onClick={() => setShowCreateModal(true)}
              className="px-4 py-2 bg-primary-600 hover:bg-primary-700 rounded-lg transition-colors flex items-center gap-2"
            >
              <Plus className="w-4 h-4" />
              New Store
            </button>
          </div>
        </div>
      </div>

      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar - Store List */}
        <div className="w-80 border-r border-slate-700 bg-slate-800/30 overflow-y-auto">
          <div className="p-4 space-y-2">
            {stores.map((store) => (
              <button
                key={store.id}
                onClick={() => setSelectedStoreId(store.id)}
                className={`w-full text-left p-3 rounded-lg transition-all ${
                  selectedStoreId === store.id
                    ? 'bg-primary-600/20 border border-primary-500/50'
                    : 'bg-slate-700/50 hover:bg-slate-700 border border-transparent'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="font-medium text-sm truncate">{store.name}</div>
                    <div className="text-xs text-slate-400 mt-1">
                      {store.file_counts?.total || 0} files
                    </div>
                    {store.expires_after && (
                      <div className="text-xs text-amber-400 mt-1 flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        Expires: {store.expires_after.days}d
                      </div>
                    )}
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      handleDeleteStore(store.id)
                    }}
                    className="ml-2 p-1 hover:bg-red-600/20 rounded text-red-400 hover:text-red-300"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </button>
            ))}
            {stores.length === 0 && (
              <div className="text-center py-8 text-slate-400">
                <Database className="w-12 h-12 mx-auto mb-2 opacity-50" />
                <p>No vector stores yet</p>
                <button
                  onClick={() => setShowCreateModal(true)}
                  className="mt-4 text-primary-400 hover:text-primary-300"
                >
                  Create your first store
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {selectedStore ? (
            <>
              {/* Store Header */}
              <div className="border-b border-slate-700 bg-slate-800/50 px-6 py-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-xl font-semibold">{selectedStore.name}</h2>
                    <div className="flex items-center gap-4 mt-1 text-sm text-slate-400">
                      <span>
                        {selectedStore.file_counts?.total || 0} files
                        {selectedStore.file_counts?.in_progress
                          ? ` (${selectedStore.file_counts.in_progress} processing)`
                          : ''}
                      </span>
                      <span>{formatBytes(selectedStore.usage_bytes)}</span>
                      <span>Created: {formatDate(selectedStore.created_at)}</span>
                    </div>
                  </div>
                  <button
                    onClick={() => setShowSettingsModal(true)}
                    className="px-3 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg transition-colors"
                  >
                    <Settings className="w-4 h-4" />
                  </button>
                </div>
              </div>

              {/* Search Bar */}
              <div className="px-6 py-4 border-b border-slate-700">
                <div className="flex gap-2">
                  <div className="flex-1 relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-400" />
                    <input
                      type="text"
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                      placeholder="Search vector store..."
                      className="w-full pl-10 pr-4 py-2 bg-slate-800 border border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    />
                  </div>
                  <button
                    onClick={handleSearch}
                    disabled={!searchQuery.trim() || searchMutation.isPending}
                    className="px-4 py-2 bg-primary-600 hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg transition-colors"
                  >
                    {searchMutation.isPending ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <Search className="w-4 h-4" />
                    )}
                  </button>
                </div>

                {/* Search Results */}
                {searchMutation.data && (
                  <div className="mt-4 p-4 bg-slate-800/50 rounded-lg">
                    <div className="text-sm font-medium mb-2">
                      Found {searchMutation.data.results.length} results
                    </div>
                    <div className="space-y-2">
                      {searchMutation.data.results.map((result, idx) => (
                        <div key={idx} className="p-3 bg-slate-700/50 rounded text-sm">
                          <div className="flex items-center justify-between mb-1">
                            <span className="font-mono text-xs text-slate-400">
                              {result.file_id}
                            </span>
                            {result.score !== undefined && (
                              <span className="text-xs text-primary-400">
                                Score: {result.score.toFixed(3)}
                              </span>
                            )}
                          </div>
                          {result.content && (
                            <div className="text-slate-300 mt-1 line-clamp-2">
                              {result.content}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* File Upload Area */}
              <div className="px-6 py-4 border-b border-slate-700">
                <div
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                  onDrop={handleDrop}
                  onClick={() => fileInputRef.current?.click()}
                  className={`
                    relative cursor-pointer border-2 border-dashed rounded-xl p-8 transition-all
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
                    onChange={(e) => handleFileSelect(e.target.files)}
                    className="hidden"
                    accept=".pdf,.docx,.doc,.txt,.md,.json,.csv,.html,.py,.js,.ts"
                  />
                  <div className="flex flex-col items-center text-center">
                    <Upload
                      className={`w-10 h-10 mb-3 transition-colors ${
                        isDragging ? 'text-primary-400' : 'text-slate-500'
                      }`}
                    />
                    <p className="text-sm text-slate-300 mb-1">
                      Drop files or <span className="text-primary-400 font-medium">browse</span>
                    </p>
                    <p className="text-xs text-slate-500">
                      PDF · DOCX · Text · Code · JSON · CSV
                    </p>
                  </div>
                  {(uploadMutation.isPending || addFilesMutation.isPending) && (
                    <div className="absolute inset-0 bg-slate-900/80 flex items-center justify-center rounded-xl">
                      <div className="flex flex-col items-center">
                        <Loader2 className="w-6 h-6 text-primary-400 animate-spin" />
                        <span className="text-xs text-primary-400 mt-2">Processing...</span>
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Files List */}
              <div className="flex-1 overflow-y-auto px-6 py-4">
                <div className="space-y-2">
                  {storeFiles.map((file) => (
                    <div
                      key={file.id}
                      className="p-3 bg-slate-800/50 rounded-lg border border-slate-700 flex items-center justify-between hover:bg-slate-800 transition-colors"
                    >
                      <div className="flex items-center gap-3 flex-1 min-w-0">
                        <FileText className="w-5 h-5 text-slate-400 flex-shrink-0" />
                        <div className="flex-1 min-w-0">
                          <div className="font-mono text-xs text-slate-300 truncate">
                            {file.file_id}
                          </div>
                          {file.status && (
                            <div className="text-xs text-slate-500 mt-1 flex items-center gap-1">
                              {file.status === 'completed' ? (
                                <>
                                  <CheckCircle className="w-3 h-3 text-green-400" />
                                  <span className="text-green-400">Ready</span>
                                </>
                              ) : file.status === 'in_progress' ? (
                                <>
                                  <Clock className="w-3 h-3 text-amber-400" />
                                  <span className="text-amber-400">Processing</span>
                                </>
                              ) : (
                                <>
                                  <XCircle className="w-3 h-3 text-red-400" />
                                  <span className="text-red-400">Failed</span>
                                </>
                              )}
                            </div>
                          )}
                        </div>
                      </div>
                      <button
                        onClick={() => {
                          if (!selectedStoreId) return
                          if (confirm('Remove this file from the vector store?')) {
                            deleteFileMutation.mutate({
                              storeId: selectedStoreId,
                              fileId: file.id,
                            })
                          }
                        }}
                        disabled={deleteFileMutation.isPending}
                        className="p-2 hover:bg-red-600/20 rounded text-red-400 hover:text-red-300"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  ))}
                  {storeFiles.length === 0 && (
                    <div className="text-center py-12 text-slate-400">
                      <FileCheck className="w-12 h-12 mx-auto mb-2 opacity-50" />
                      <p>No files in this vector store</p>
                      <p className="text-xs mt-1">Upload files above to get started</p>
                    </div>
                  )}
                </div>
              </div>
            </>
          ) : (
            <div className="flex-1 flex items-center justify-center text-slate-400">
              <div className="text-center">
                <Database className="w-16 h-16 mx-auto mb-4 opacity-50" />
                <p>Select a vector store to view details</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Create Store Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-slate-800 rounded-xl p-6 w-full max-w-md border border-slate-700">
            <h3 className="text-xl font-semibold mb-4">Create Vector Store</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Name</label>
                <input
                  type="text"
                  value={newStoreName}
                  onChange={(e) => setNewStoreName(e.target.value)}
                  placeholder="My Knowledge Base"
                  className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">
                  Expiration (days, optional)
                </label>
                <input
                  type="number"
                  value={expirationDays || ''}
                  onChange={(e) =>
                    setExpirationDays(e.target.value ? parseInt(e.target.value) : undefined)
                  }
                  placeholder="7 (default: no expiration)"
                  className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
                <p className="text-xs text-slate-400 mt-1">
                  Store will expire after this many days of inactivity
                </p>
              </div>
            </div>
            <div className="flex gap-2 mt-6">
              <button
                onClick={() => {
                  setShowCreateModal(false)
                  setNewStoreName('')
                  setExpirationDays(undefined)
                }}
                className="flex-1 px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  if (newStoreName.trim()) {
                    createMutation.mutate(newStoreName.trim())
                  }
                }}
                disabled={!newStoreName.trim() || createMutation.isPending}
                className="flex-1 px-4 py-2 bg-primary-600 hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg transition-colors"
              >
                {createMutation.isPending ? (
                  <Loader2 className="w-4 h-4 animate-spin mx-auto" />
                ) : (
                  'Create'
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}







