/**
 * Responses API Chat Page
 * Modern chat interface using the Responses API with improved UX/UI
 */
import { useState, useEffect, useRef } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import {
  Send,
  Bot,
  User,
  Sparkles,
  Code,
  FileSearch,
  Settings,
  Loader2,
  Copy,
  Check,
  X,
  MessageSquare,
  Zap,
} from 'lucide-react'
import { toast } from '../utils/toast'
import apiClient, { apiPath } from '../lib/apiClient'
import PageHeader from '../components/PageHeader'

interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: Date
  toolCalls?: Array<{
    id: string
    type: string
    name?: string
    input?: string
  }>
}

interface Conversation {
  id: string
  metadata?: Record<string, any>
}

export default function ResponsesChat() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [conversationId, setConversationId] = useState<string | null>(null)
  const [isStreaming, setIsStreaming] = useState(false)
  const [selectedTools, setSelectedTools] = useState({
    codeInterpreter: true,
    fileSearch: true,
    functionCalling: true,
  })
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const [copiedId, setCopiedId] = useState<string | null>(null)

  // Create conversation
  const createConversation = useMutation({
    mutationFn: async () => {
      const { data } = await apiClient.post(apiPath('responses/conversations'), {
        metadata: { created_at: new Date().toISOString() },
      })
      return data
    },
    onSuccess: (data: Conversation) => {
      setConversationId(data.id)
      toast.success('Conversation created')
    },
    onError: (error: Error) => {
      toast.error(`Failed to create conversation: ${error.message}`)
    },
  })

  // Send message
  const sendMessage = useMutation({
    mutationFn: async (content: string) => {
      if (!conversationId) {
        await createConversation.mutateAsync()
        // Wait a bit for conversation to be created
        await new Promise((resolve) => setTimeout(resolve, 100))
      }

      const tools = []
      if (selectedTools.codeInterpreter) {
        tools.push({ type: 'code_interpreter' })
      }
      if (selectedTools.fileSearch) {
        tools.push({ type: 'file_search' })
      }
      if (selectedTools.functionCalling) {
        tools.push({
          type: 'function',
          function: {
            name: 'get_weather',
            description: 'Determine weather in my location',
            parameters: {
              type: 'object',
              properties: {
                location: {
                  type: 'string',
                  description: 'The city and state e.g. San Francisco, CA',
                },
                unit: {
                  type: 'string',
                  enum: ['c', 'f'],
                },
              },
              required: ['location'],
            },
          },
        })
      }

      const payload = {
        model: 'gpt-4o',
        input: [
          {
            role: 'user',
            content: [
              {
                type: 'input_text',
                text: content,
              },
            ],
          },
        ],
        conversation: conversationId,
        store: true,
        stream: true,
        tools: tools.length > 0 ? tools : undefined,
        tool_choice: 'auto',
        instructions: 'You are a helpful assistant.',
      }

      const response = await fetch(apiPath('responses/responses'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      return response
    },
    onSuccess: async (response) => {
      // Add user message
      const userMessage: Message = {
        id: `user-${Date.now()}`,
        role: 'user',
        content: input,
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, userMessage])
      setInput('')
      setIsStreaming(true)

      // Stream response
      const reader = response.body?.getReader()
      const decoder = new TextDecoder()
      let buffer = ''
      let assistantMessage: Message = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: '',
        timestamp: new Date(),
        toolCalls: [],
      }

      setMessages((prev) => [...prev, assistantMessage])

      if (!reader) {
        setIsStreaming(false)
        return
      }

      try {
        while (true) {
          const { done, value } = await reader.read()
          if (done) break

          buffer += decoder.decode(value, { stream: true })
          const lines = buffer.split('\n')
          buffer = lines.pop() || ''

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6))

                if (data.type === 'response.output_item.delta' && data.delta?.type === 'message.delta') {
                  const content = data.delta.content
                  if (content) {
                    for (const item of content) {
                      if (item.type === 'output_text' && item.text) {
                        setMessages((prev) => {
                          const last = prev[prev.length - 1]
                          if (last.role === 'assistant') {
                            return [
                              ...prev.slice(0, -1),
                              { ...last, content: last.content + item.text },
                            ]
                          }
                          return prev
                        })
                      }
                    }
                  }
                }

                if (data.type === 'response.output_item.added' && data.item?.type === 'code_interpreter_tool_call') {
                  setMessages((prev) => {
                    const last = prev[prev.length - 1]
                    if (last.role === 'assistant') {
                      return [
                        ...prev.slice(0, -1),
                        {
                          ...last,
                          toolCalls: [
                            ...(last.toolCalls || []),
                            {
                              id: data.item.id,
                              type: 'code_interpreter',
                              input: data.item.input || '',
                            },
                          ],
                        },
                      ]
                    }
                    return prev
                  })
                }

                if (data.type === 'response.output_item.added' && data.item?.type === 'function_tool_call') {
                  setMessages((prev) => {
                    const last = prev[prev.length - 1]
                    if (last.role === 'assistant') {
                      return [
                        ...prev.slice(0, -1),
                        {
                          ...last,
                          toolCalls: [
                            ...(last.toolCalls || []),
                            {
                              id: data.item.id,
                              type: 'function',
                              name: data.item.name,
                            },
                          ],
                        },
                      ]
                    }
                    return prev
                  })
                }

                if (data.type === 'response.done') {
                  setIsStreaming(false)
                }

                if (data.type === 'error') {
                  toast.error(`Stream error: ${data.error}`)
                  setIsStreaming(false)
                }
              } catch (e) {
                // Skip invalid JSON
              }
            }
          }
        }
      } catch (error) {
        toast.error(`Streaming error: ${error}`)
        setIsStreaming(false)
      }
    },
    onError: (error: Error) => {
      toast.error(`Failed to send message: ${error.message}`)
      setIsStreaming(false)
    },
  })

  // Initialize conversation on mount
  useEffect(() => {
    if (!conversationId) {
      createConversation.mutate()
    }
  }, [])

  // Scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isStreaming) return
    sendMessage.mutate(input)
  }

  const copyToClipboard = (text: string, id: string) => {
    navigator.clipboard.writeText(text)
    setCopiedId(id)
    setTimeout(() => setCopiedId(null), 2000)
    toast.success('Copied to clipboard')
  }

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900">
      <PageHeader
        title="Responses API Chat"
        description="Modern chat interface powered by OpenAI Responses API"
        icon={Sparkles}
      />

      {/* Tool Settings Bar */}
      <div className="border-b border-slate-200 dark:border-slate-700 bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <label className="flex items-center gap-2 text-sm font-medium text-slate-700 dark:text-slate-300 cursor-pointer">
              <input
                type="checkbox"
                checked={selectedTools.codeInterpreter}
                onChange={(e) =>
                  setSelectedTools((prev) => ({
                    ...prev,
                    codeInterpreter: e.target.checked,
                  }))
                }
                className="rounded"
              />
              <Code className="w-4 h-4" />
              <span>Code Interpreter</span>
            </label>
            <label className="flex items-center gap-2 text-sm font-medium text-slate-700 dark:text-slate-300 cursor-pointer">
              <input
                type="checkbox"
                checked={selectedTools.fileSearch}
                onChange={(e) =>
                  setSelectedTools((prev) => ({
                    ...prev,
                    fileSearch: e.target.checked,
                  }))
                }
                className="rounded"
              />
              <FileSearch className="w-4 h-4" />
              <span>File Search</span>
            </label>
            <label className="flex items-center gap-2 text-sm font-medium text-slate-700 dark:text-slate-300 cursor-pointer">
              <input
                type="checkbox"
                checked={selectedTools.functionCalling}
                onChange={(e) =>
                  setSelectedTools((prev) => ({
                    ...prev,
                    functionCalling: e.target.checked,
                  }))
                }
                className="rounded"
              />
              <Zap className="w-4 h-4" />
              <span>Functions</span>
            </label>
          </div>
          {conversationId && (
            <div className="flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400">
              <span>Conversation:</span>
              <code className="px-2 py-1 bg-slate-100 dark:bg-slate-700 rounded">
                {conversationId.slice(0, 8)}...
              </code>
              <button
                onClick={() => copyToClipboard(conversationId, 'conv')}
                className="p-1 hover:bg-slate-200 dark:hover:bg-slate-600 rounded"
              >
                {copiedId === 'conv' ? (
                  <Check className="w-3 h-3" />
                ) : (
                  <Copy className="w-3 h-3" />
                )}
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto px-4 py-6">
        <div className="max-w-4xl mx-auto space-y-6">
          {messages.length === 0 && (
            <div className="text-center py-12">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 mb-4">
                <Sparkles className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-slate-900 dark:text-white mb-2">
                Start a conversation
              </h3>
              <p className="text-slate-600 dark:text-slate-400">
                Ask questions, write code, or search files. The AI assistant is ready to help.
              </p>
            </div>
          )}

          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex gap-4 ${
                message.role === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              {message.role === 'assistant' && (
                <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center">
                  <Bot className="w-5 h-5 text-white" />
                </div>
              )}

              <div
                className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                  message.role === 'user'
                    ? 'bg-gradient-to-br from-blue-500 to-indigo-600 text-white'
                    : 'bg-white dark:bg-slate-800 text-slate-900 dark:text-white shadow-lg border border-slate-200 dark:border-slate-700'
                }`}
              >
                {message.role === 'user' ? (
                  <div className="flex items-center gap-2">
                    <User className="w-4 h-4" />
                    <p className="whitespace-pre-wrap">{message.content}</p>
                  </div>
                ) : (
                  <div className="space-y-2">
                    <p className="whitespace-pre-wrap">{message.content}</p>
                    {message.toolCalls && message.toolCalls.length > 0 && (
                      <div className="mt-3 pt-3 border-t border-slate-200 dark:border-slate-700 space-y-2">
                        {message.toolCalls.map((toolCall) => (
                          <div
                            key={toolCall.id}
                            className="text-xs bg-slate-100 dark:bg-slate-700 rounded p-2"
                          >
                            {toolCall.type === 'code_interpreter' && (
                              <div className="flex items-center gap-2">
                                <Code className="w-3 h-3" />
                                <span className="font-mono">{toolCall.input}</span>
                              </div>
                            )}
                            {toolCall.type === 'function' && (
                              <div className="flex items-center gap-2">
                                <Zap className="w-3 h-3" />
                                <span>Function: {toolCall.name}</span>
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
                <div className="mt-2 flex items-center justify-end gap-2">
                  <button
                    onClick={() => copyToClipboard(message.content, message.id)}
                    className="text-xs opacity-70 hover:opacity-100 transition-opacity"
                  >
                    {copiedId === message.id ? (
                      <Check className="w-3 h-3" />
                    ) : (
                      <Copy className="w-3 h-3" />
                    )}
                  </button>
                </div>
              </div>

              {message.role === 'user' && (
                <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-br from-slate-400 to-slate-600 flex items-center justify-center">
                  <User className="w-5 h-5 text-white" />
                </div>
              )}
            </div>
          ))}

          {isStreaming && (
            <div className="flex gap-4 justify-start">
              <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center">
                <Bot className="w-5 h-5 text-white" />
              </div>
              <div className="bg-white dark:bg-slate-800 rounded-2xl px-4 py-3 shadow-lg border border-slate-200 dark:border-slate-700">
                <Loader2 className="w-4 h-4 animate-spin text-blue-500" />
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <div className="border-t border-slate-200 dark:border-slate-700 bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <form onSubmit={handleSubmit} className="flex gap-3">
            <div className="flex-1 relative">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault()
                    handleSubmit(e)
                  }
                }}
                placeholder="Type your message... (Shift+Enter for new line)"
                className="w-full px-4 py-3 pr-12 rounded-xl border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-900 dark:text-white placeholder-slate-500 dark:placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                rows={1}
                disabled={isStreaming}
              />
            </div>
            <button
              type="submit"
              disabled={!input.trim() || isStreaming}
              className="px-6 py-3 bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-xl font-medium hover:from-blue-600 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg hover:shadow-xl flex items-center gap-2"
            >
              {isStreaming ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Sending...</span>
                </>
              ) : (
                <>
                  <Send className="w-4 h-4" />
                  <span>Send</span>
                </>
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}


