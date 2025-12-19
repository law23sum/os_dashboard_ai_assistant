import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Send,
  MessageSquare,
  Paperclip,
  Bot,
  User,
  FileText,
  Copy,
  Check,
  ChevronDown,
  ChevronUp,
  X,
} from 'lucide-react'
import { useState, useEffect, useRef, useCallback } from 'react'
import { toast } from '../utils/toast'
import apiClient, { apiPath } from '../lib/apiClient'
import { extractArray } from '../lib/responseHelpers'
import { ChatMessage } from '../types'
import UnifiedDocumentViewer from '../components/UnifiedDocumentViewer'
import DocumentPanel from '../components/DocumentPanel'
import ChangeMonitor from '../components/ChangeMonitor'
import type { ChatDocument } from '../types/documents'

const fetchChatHistory = async (persona?: string): Promise<ChatMessage[]> => {
  const params = persona ? { persona } : undefined
  const { data } = await apiClient.get(apiPath('chat/'), { params })
  return extractArray<ChatMessage>(data, ['messages', 'items'])
}

const sendMessage = async (message: {
  persona: string
  content: string
  attachments?: string[]
}): Promise<{ user_message: ChatMessage; ai_reply: ChatMessage }> => {
  const payload = {
    persona: message.persona,
    role: 'user',
    kind: 'chat',
    content: message.content,
    attachments: message.attachments ?? undefined,
  }
  const { data } = await apiClient.post(apiPath('chat/'), payload)
  
  // Handle new response format with both user_message and ai_reply
  if (data && typeof data === 'object') {
    if ('user_message' in data && 'ai_reply' in data) {
      return {
        user_message: data.user_message as ChatMessage,
        ai_reply: data.ai_reply as ChatMessage,
      }
    }
    // Fallback for old format (single message)
    if ('message' in data && data.message) {
      return {
        user_message: data.message as ChatMessage,
        ai_reply: data.message as ChatMessage, // Temporary fallback
      }
    }
    // If data is a single ChatMessage (legacy)
    if ('id' in data && 'content' in data) {
      return {
        user_message: data as ChatMessage,
        ai_reply: data as ChatMessage, // Temporary fallback
      }
    }
  }
  
  throw new Error('Invalid response format from chat API')
}

const PERSONAS = [
  { id: 'Chris', label: 'Chris', role: 'User', color: 'from-violet-500 to-purple-600' },
  { id: 'AIC', label: 'AIC', role: 'AI Copilot', color: 'from-emerald-500 to-teal-600' },
  { id: 'Aria', label: 'Aria', role: 'Research AI', color: 'from-pink-500 to-rose-600' },
  { id: 'Sora', label: 'Sora', role: 'Creative AI', color: 'from-amber-500 to-orange-600' },
]

export default function Chat() {
  const [message, setMessage] = useState('')
  const [persona, setPersona] = useState('Chris')
  const [selectedDoc, setSelectedDoc] = useState<ChatDocument | null>(null)
  const [copiedId, setCopiedId] = useState<number | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)
  
  // Panel state management
  const [documentPanelHeight, setDocumentPanelHeight] = useState(400) // Default height in pixels
  const [changeMonitorHeight, setChangeMonitorHeight] = useState(256) // Default height in pixels
  const [isDocumentPanelCollapsed, setIsDocumentPanelCollapsed] = useState(false)
  const [isChangeMonitorCollapsed, setIsChangeMonitorCollapsed] = useState(false)
  const [isResizing, setIsResizing] = useState(false)
  const resizeRef = useRef<{ type: 'document' | 'change'; startY: number; startHeight: number } | null>(null)

  // Auto-resize textarea
  useEffect(() => {
    const textarea = inputRef.current
    if (textarea) {
      textarea.style.height = '48px'
      const scrollHeight = textarea.scrollHeight
      if (scrollHeight > 48) {
        textarea.style.height = `${Math.min(scrollHeight, 120)}px`
      }
    }
  }, [message])

  // Handle panel resizing
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!resizeRef.current) return
      
      const deltaY = e.clientY - resizeRef.current.startY
      if (resizeRef.current.type === 'document') {
        const newHeight = Math.max(200, Math.min(600, resizeRef.current.startHeight + deltaY))
        setDocumentPanelHeight(newHeight)
      } else if (resizeRef.current.type === 'change') {
        const newHeight = Math.max(150, Math.min(500, resizeRef.current.startHeight + deltaY))
        setChangeMonitorHeight(newHeight)
      }
    }

    const handleMouseUp = () => {
      resizeRef.current = null
      setIsResizing(false)
    }

    if (isResizing) {
      document.addEventListener('mousemove', handleMouseMove)
      document.addEventListener('mouseup', handleMouseUp)
      return () => {
        document.removeEventListener('mousemove', handleMouseMove)
        document.removeEventListener('mouseup', handleMouseUp)
      }
    }
  }, [isResizing])

  const queryClient = useQueryClient()
  const { data: messages = [] } = useQuery({
    queryKey: ['chat', persona],
    queryFn: () => fetchChatHistory(persona),
  })

  const sendMutation = useMutation({
    mutationFn: sendMessage,
    onSuccess: (response) => {
      // Optimistically update the cache with both messages
      queryClient.setQueryData<ChatMessage[]>(['chat', persona], (old = []) => {
        // Add both user message and AI reply to the cache
        const newMessages = [...old, response.user_message, response.ai_reply]
        // Remove duplicates by id
        const seen = new Set<number>()
        return newMessages.filter(msg => {
          if (seen.has(msg.id)) return false
          seen.add(msg.id)
          return true
        })
      })
      // Also invalidate to ensure we get the latest from server
      queryClient.invalidateQueries({ queryKey: ['chat', persona] })
      setMessage('')
      // Reset textarea height
      if (inputRef.current) {
        inputRef.current.style.height = '48px'
      }
      // Focus back on input
      setTimeout(() => inputRef.current?.focus(), 100)
    },
    onError: (error) => {
      toast.error(`Failed to send message: ${error instanceof Error ? error.message : 'Unknown error'}`)
    },
  })

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [])

  useEffect(() => {
    scrollToBottom()
  }, [messages, scrollToBottom])

  // Focus input on mount and after sending
  useEffect(() => {
    if (inputRef.current && messages.length > 0) {
      // Small delay to ensure DOM is ready
      setTimeout(() => inputRef.current?.focus(), 100)
    }
  }, [])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (!message.trim() || sendMutation.isPending) return

    // Include document context if selected
    let finalMessage = message.trim()
    if (selectedDoc) {
      finalMessage = `[Attached: ${selectedDoc.original_name}]\n\n${finalMessage}`
    }

    sendMutation.mutate({
      persona,
      content: finalMessage,
      attachments: selectedDoc ? [selectedDoc.id] : undefined,
    })
    // Don't clear selectedDoc - let user keep it attached for multiple messages
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
    // Cmd/Ctrl + K to focus input
    if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
      e.preventDefault()
      inputRef.current?.focus()
    }
  }

  const handleCopy = async (text: string, id: number) => {
    await navigator.clipboard.writeText(text)
    setCopiedId(id)
    setTimeout(() => setCopiedId(null), 2000)
  }

  const handleDocumentSelect = (doc: ChatDocument | null) => {
    if (!doc) {
      setSelectedDoc(null)
      return
    }
    setSelectedDoc(doc)
    toast.info(`Document attached: ${doc.original_name}`)
  }

  const currentPersona = PERSONAS.find((p) => p.id === persona) || PERSONAS[0]

  return (
    <div className="h-[calc(100vh-4rem)] flex flex-col bg-slate-900">
      {/* Header */}
      <div className="px-6 py-4 border-b border-slate-700/50 bg-gradient-to-r from-slate-900/95 to-slate-800/95 backdrop-blur-sm">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="p-2 rounded-xl bg-gradient-to-br from-primary-500/20 to-violet-500/20 border border-primary-500/30">
              <MessageSquare className="w-5 h-5 text-primary-400" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">Chat</h2>
              <p className="text-sm text-slate-400 mt-0.5">
                {messages.length > 0 
                  ? `${messages.length} message${messages.length !== 1 ? 's' : ''} • ${persona}`
                  : 'Chat with your AI assistants'
                }
              </p>
            </div>
          </div>
          {messages.length > 0 && (
            <div className="flex items-center gap-2 text-xs text-slate-500">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              <span>Active</span>
            </div>
          )}
        </div>
      </div>

      {/* Main Content - Split Layout */}
      <div className="flex-1 flex flex-col overflow-hidden bg-slate-900/30">
        <div className="flex-1 flex overflow-hidden">
          {/* Left: Chat Area */}
          <div className="w-1/2 flex flex-col min-w-0 border-r border-slate-700/50 bg-slate-900/50 backdrop-blur-sm">
            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6 scroll-smooth">
            {messages.length === 0 && (
              <div className="flex items-center justify-center h-full">
                <div className="text-center max-w-lg px-4">
                  <div className="w-20 h-20 mx-auto mb-6 rounded-2xl bg-gradient-to-br from-primary-500/20 to-violet-500/20 flex items-center justify-center border border-primary-500/30">
                    <Bot className="w-10 h-10 text-primary-400" />
                  </div>
                  <h3 className="text-xl font-semibold text-white mb-3">Start a Conversation</h3>
                  <p className="text-slate-400 text-sm mb-6 leading-relaxed">
                    Send a message to begin. You can upload documents using the panel on the right
                    and ask the AI to analyze or modify them.
                  </p>
                </div>
              </div>
            )}

            {messages.map((msg, index) => {
              const isUser = msg.role === 'user'
              const msgPersona = PERSONAS.find((p) => p.id === msg.persona)
              const showAvatar = index === 0 || messages[index - 1].persona !== msg.persona || messages[index - 1].role !== msg.role

              return (
                <div
                  key={msg.id}
                  className={`flex gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'} ${!showAvatar ? 'mt-1' : ''}`}
                >
                  {/* Avatar - Only show when persona changes */}
                  <div className={`flex-shrink-0 ${showAvatar ? 'w-9' : 'w-9'}`}>
                    {showAvatar ? (
                      <div
                        className={`
                          w-9 h-9 rounded-xl flex items-center justify-center
                          bg-gradient-to-br ${msgPersona?.color || 'from-slate-500 to-slate-600'}
                          shadow-lg shadow-black/20 border border-white/10
                        `}
                      >
                        {isUser ? (
                          <User className="w-4 h-4 text-white" />
                        ) : (
                          <Bot className="w-4 h-4 text-white" />
                        )}
                      </div>
                    ) : (
                      <div className="w-9" />
                    )}
                  </div>

                  {/* Message Content */}
                  <div
                    className={`
                      group relative max-w-[75%] rounded-2xl px-5 py-3.5
                      transition-all duration-200
                      ${
                        isUser
                          ? 'bg-gradient-to-br from-primary-600 to-primary-700 text-white shadow-lg shadow-primary-500/20'
                          : 'bg-slate-800/80 text-slate-200 border border-slate-700/60 shadow-md backdrop-blur-sm'
                      }
                      hover:shadow-xl
                    `}
                  >
                    {/* Persona Label */}
                    {showAvatar && (
                      <div
                        className={`text-xs font-semibold mb-2 ${isUser ? 'text-primary-100' : 'text-slate-300'}`}
                      >
                        {msg.persona}
                        {msgPersona && (
                          <span className="ml-1.5 opacity-70 font-normal">• {msgPersona.role}</span>
                        )}
                      </div>
                    )}

                    {/* Message Text */}
                    <div className="text-sm whitespace-pre-wrap leading-relaxed break-words">
                      {msg.content}
                    </div>

                    {/* Timestamp & Actions */}
                    <div
                      className={`
                        flex items-center justify-between mt-3 pt-2 border-t
                        ${isUser ? 'border-primary-500/30 text-primary-100/80' : 'border-slate-700/50 text-slate-500'}
                      `}
                    >
                      <span className="text-[10px] font-medium">
                        {new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </span>
                      <button
                        onClick={() => handleCopy(msg.content, msg.id)}
                        className={`
                          opacity-0 group-hover:opacity-100 transition-all duration-200 p-1.5 rounded-lg
                          ${isUser 
                            ? 'hover:bg-primary-500/30 text-primary-100' 
                            : 'hover:bg-slate-700/70 text-slate-400'
                          }
                        `}
                        title="Copy message"
                        aria-label="Copy message"
                      >
                        {copiedId === msg.id ? (
                          <Check className="w-3.5 h-3.5" />
                        ) : (
                          <Copy className="w-3.5 h-3.5" />
                        )}
                      </button>
                    </div>
                  </div>
                </div>
              )
            })}

            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="p-4 border-t border-slate-700/50 bg-gradient-to-t from-slate-900/95 to-slate-800/95 backdrop-blur-sm">
            {/* Selected Document Indicator */}
            {selectedDoc && (
              <div className="mb-3 flex items-center gap-2 px-4 py-2.5 bg-gradient-to-r from-primary-500/10 to-primary-600/10 border border-primary-500/30 rounded-xl">
                <div className="p-1.5 rounded-lg bg-primary-500/20">
                  <FileText className="w-4 h-4 text-primary-400" />
                </div>
                <span className="text-sm font-medium text-primary-200 flex-1 truncate">
                  {selectedDoc.original_name}
                </span>
                <button
                  onClick={() => setSelectedDoc(null)}
                  className="p-1.5 hover:bg-primary-500/20 rounded-lg transition-colors"
                  title="Remove attachment"
                  aria-label="Remove attachment"
                >
                  <X className="w-4 h-4 text-primary-400" />
                </button>
              </div>
            )}

            <form onSubmit={handleSubmit} className="flex items-end gap-3">
              {/* Persona Selector */}
              <div className="relative">
                <select
                  value={persona}
                  onChange={(e) => {
                    e.stopPropagation()
                    setPersona(e.target.value)
                  }}
                  className="appearance-none px-4 py-3 pr-10 bg-slate-800/80 border border-slate-700/60 rounded-xl text-sm font-medium text-white focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500/50 cursor-pointer transition-all hover:bg-slate-800 hover:border-slate-600 active:scale-[0.98]"
                  style={{ 
                    WebkitAppearance: 'none',
                    MozAppearance: 'none',
                    cursor: 'pointer',
                  }}
                >
                  {PERSONAS.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.label}
                    </option>
                  ))}
                </select>
                <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none">
                  <div
                    className={`w-2.5 h-2.5 rounded-full bg-gradient-to-br ${currentPersona.color} shadow-sm`}
                  />
                </div>
              </div>

              {/* Message Input */}
              <div className="flex-1 relative">
                <textarea
                  ref={inputRef}
                  value={message}
                  onChange={(e) => {
                    setMessage(e.target.value)
                    const textarea = e.target
                    textarea.style.height = '48px'
                    const scrollHeight = textarea.scrollHeight
                    if (scrollHeight > 48) {
                      textarea.style.height = `${Math.min(scrollHeight, 120)}px`
                    }
                  }}
                  onKeyDown={handleKeyDown}
                  placeholder="Type your message... (Shift+Enter for new line, Enter to send)"
                  rows={1}
                  className="w-full px-4 py-3 bg-slate-800/80 border border-slate-700/60 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500/50 resize-none overflow-y-auto transition-all duration-200 hover:border-slate-600"
                  style={{ minHeight: '48px', maxHeight: '120px' }}
                />
              </div>

              {/* Attach Document Button */}
              <button
                type="button"
                onClick={() => {
                  toast.info(selectedDoc ? `Document attached: ${selectedDoc.original_name}` : 'Select a document from the right panel')
                }}
                className={`
                  p-3 rounded-xl transition-all relative
                  ${selectedDoc 
                    ? 'bg-gradient-to-br from-primary-500/20 to-primary-600/20 text-primary-400 border border-primary-500/30' 
                    : 'bg-slate-800/80 text-slate-400 hover:bg-slate-700 hover:text-slate-300 border border-slate-700/60'
                  }
                `}
                title={selectedDoc ? `Document attached: ${selectedDoc.original_name}` : 'Select a document from the right panel'}
                aria-label="Attach document"
              >
                <Paperclip className="w-5 h-5" />
                {selectedDoc && (
                  <span className="absolute -top-1 -right-1 w-3 h-3 bg-primary-500 rounded-full border-2 border-slate-900" />
                )}
              </button>

              {/* Send Button */}
              <button
                type="submit"
                disabled={sendMutation.isPending || !message.trim()}
                className="p-3 bg-gradient-to-br from-primary-500 to-primary-600 text-white rounded-xl hover:from-primary-600 hover:to-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center gap-2 shadow-lg shadow-primary-500/20 hover:shadow-xl hover:shadow-primary-500/30 disabled:shadow-none"
                aria-label="Send message"
              >
                {sendMutation.isPending ? (
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                ) : (
                  <Send className="w-5 h-5" />
                )}
              </button>
            </form>
          </div>
        </div>

          {/* Right: Multi-panel layout */}
          <div className="w-1/2 flex flex-col min-w-0">
            {/* Top: Document Panel - Resizable */}
            <div className="relative border-b border-slate-700/50 overflow-hidden bg-slate-900/50 backdrop-blur-sm">
              {/* Resize Handle */}
              <div
                className={`absolute top-0 left-0 right-0 h-1 cursor-ns-resize hover:bg-primary-500/50 transition-colors z-10 ${
                  isResizing ? 'bg-primary-500/70' : 'bg-transparent'
                }`}
                onMouseDown={(e) => {
                  setIsResizing(true)
                  resizeRef.current = {
                    type: 'document',
                    startY: e.clientY,
                    startHeight: documentPanelHeight,
                  }
                }}
              />
              
              {/* Collapse Button */}
              <button
                onClick={() => setIsDocumentPanelCollapsed(!isDocumentPanelCollapsed)}
                className="absolute top-2 right-2 z-20 p-1.5 bg-slate-800/80 hover:bg-slate-700 rounded-lg transition-colors border border-slate-700/50"
                title={isDocumentPanelCollapsed ? 'Expand document panel' : 'Collapse document panel'}
              >
                {isDocumentPanelCollapsed ? (
                  <ChevronDown className="w-4 h-4 text-slate-400" />
                ) : (
                  <ChevronUp className="w-4 h-4 text-slate-400" />
                )}
              </button>

              <div
                className="overflow-hidden transition-all duration-300"
                style={{
                  height: isDocumentPanelCollapsed ? '40px' : `${documentPanelHeight}px`,
                }}
              >
                <DocumentPanel
                  persona={persona}
                  onDocumentSelect={handleDocumentSelect}
                  selectedDocumentId={selectedDoc?.id}
                />
              </div>
            </div>
            
            {/* Middle: Unified Document Viewer */}
            <div className="flex-1 flex overflow-hidden">
              <UnifiedDocumentViewer
                document={selectedDoc}
                persona={persona}
                onDocumentUpdate={(updatedDoc) => {
                  setSelectedDoc(updatedDoc)
                }}
                onDocumentSelect={handleDocumentSelect}
              />
            </div>
          </div>
        </div>

        {/* Bottom: Change Monitor - Resizable */}
        <div className="relative border-t border-slate-700/50 overflow-hidden bg-slate-900/50 backdrop-blur-sm">
          {/* Resize Handle */}
          <div
            className={`absolute top-0 left-0 right-0 h-1 cursor-ns-resize hover:bg-primary-500/50 transition-colors z-10 ${
              isResizing ? 'bg-primary-500/70' : 'bg-transparent'
            }`}
            onMouseDown={(e) => {
              setIsResizing(true)
              resizeRef.current = {
                type: 'change',
                startY: e.clientY,
                startHeight: changeMonitorHeight,
              }
            }}
          />
          
          {/* Collapse Button */}
          <button
            onClick={() => setIsChangeMonitorCollapsed(!isChangeMonitorCollapsed)}
            className="absolute top-2 right-2 z-20 p-1.5 bg-slate-800/80 hover:bg-slate-700 rounded-lg transition-colors border border-slate-700/50"
            title={isChangeMonitorCollapsed ? 'Expand change monitor' : 'Collapse change monitor'}
          >
            {isChangeMonitorCollapsed ? (
              <ChevronUp className="w-4 h-4 text-slate-400" />
            ) : (
              <ChevronDown className="w-4 h-4 text-slate-400" />
            )}
          </button>

          <div
            className="overflow-hidden transition-all duration-300"
            style={{
              height: isChangeMonitorCollapsed ? '40px' : `${changeMonitorHeight}px`,
            }}
          >
            <ChangeMonitor chatMessages={messages} />
          </div>
        </div>
      </div>
    </div>
  )
}
