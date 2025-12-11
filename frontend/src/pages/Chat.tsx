import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Send, MessageSquare } from 'lucide-react'
import { useState, useEffect, useRef } from 'react'
import { toast } from '../utils/toast'
import apiClient, { apiPath } from '../lib/apiClient'
import { extractArray } from '../lib/responseHelpers'
import { ChatMessage } from '../types'

const fetchChatHistory = async (persona?: string): Promise<ChatMessage[]> => {
  const params = persona ? { persona } : undefined
  const { data } = await apiClient.get(apiPath('chat/'), { params })
  return extractArray<ChatMessage>(data, ['messages', 'items'])
}

const sendMessage = async (message: { persona: string; content: string }): Promise<ChatMessage> => {
  const payload = {
    persona: message.persona,
    role: 'user',
    kind: 'chat',
    content: message.content,
  }
  const { data } = await apiClient.post(apiPath('chat/'), payload)
  if (data && typeof data === 'object' && 'message' in data && data.message) {
    return data.message as ChatMessage
  }
  return data as ChatMessage
}

export default function Chat() {
  const [message, setMessage] = useState('')
  const [persona, setPersona] = useState('Chris')
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const queryClient = useQueryClient()
  const { data: messages = [] } = useQuery({
    queryKey: ['chat', persona],
    queryFn: () => fetchChatHistory(persona),
  })

  const sendMutation = useMutation({
    mutationFn: sendMessage,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['chat', persona] })
      setMessage('')
    },
    onError: (error) => {
      toast.error(`Failed to send message: ${error instanceof Error ? error.message : 'Unknown error'}`)
    },
  })

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!message.trim()) return
    sendMutation.mutate({ persona, content: message })
  }

  return (
    <div className="px-4 py-6 sm:px-0 h-[calc(100vh-8rem)] flex flex-col">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Chat</h2>
        <p className="text-gray-600 dark:text-gray-400">Chat with your AI assistants</p>
      </div>

      <div className="flex-1 bg-white dark:bg-gray-800 shadow rounded-lg flex flex-col">
        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.length === 0 && (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <MessageSquare className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500 dark:text-gray-400">No messages yet. Start a conversation!</p>
              </div>
            </div>
          )}
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                  msg.role === 'user'
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-200 text-gray-900 dark:bg-gray-700 dark:text-white'
                }`}
              >
                <div className="text-sm font-medium mb-1">{msg.persona}</div>
                <div className="text-sm">{msg.content}</div>
                <div className="text-xs opacity-75 mt-1">
                  {new Date(msg.created_at).toLocaleTimeString()}
                </div>
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="border-t border-gray-200 dark:border-gray-700 p-4">
          <form onSubmit={handleSubmit} className="flex space-x-4">
            <select
              value={persona}
              onChange={(e) => setPersona(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            >
              <option value="Chris">Chris</option>
              <option value="AIC">AIC</option>
              <option value="Aria">Aria</option>
              <option value="Sora">Sora</option>
            </select>
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Type your message..."
              className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            />
            <button
              type="submit"
              disabled={sendMutation.isPending || !message.trim()}
              className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
            >
              <Send className="w-5 h-5" />
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}
