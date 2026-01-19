import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  Book, FileText, Code, Terminal, Zap, Settings, Shield, Database,
  Search, ChevronRight, ExternalLink, BookOpen, Layers
} from 'lucide-react'
import apiClient, { apiPath } from '../lib/apiClient'

type DocSection = 'getting-started' | 'api' | 'guides' | 'reference'

interface DocItem {
  id: string
  title: string
  description: string
  category: string
  path: string
}

export default function Docs() {
  const [activeSection, setActiveSection] = useState<DocSection>('getting-started')
  const [searchQuery, setSearchQuery] = useState('')

  const { data: docs } = useQuery({
    queryKey: ['documentation'],
    queryFn: async () => {
      try {
        const { data } = await apiClient.get<DocItem[]>(apiPath('docs'))
        return data
      } catch {
        return null
      }
    },
  })

  const sections = [
    { id: 'getting-started' as DocSection, label: 'Getting Started', icon: Zap },
    { id: 'api' as DocSection, label: 'API Reference', icon: Code },
    { id: 'guides' as DocSection, label: 'Guides', icon: BookOpen },
    { id: 'reference' as DocSection, label: 'Reference', icon: Layers },
  ]

  const gettingStartedDocs = [
    { title: 'Quick Start', description: 'Get up and running in 5 minutes', icon: Zap, path: '/docs/quickstart' },
    { title: 'Installation', description: 'Install and configure the platform', icon: Terminal, path: '/docs/installation' },
    { title: 'Configuration', description: 'Configure your environment', icon: Settings, path: '/docs/config' },
    { title: 'First Project', description: 'Create your first project', icon: FileText, path: '/docs/first-project' },
  ]

  const apiDocs = [
    { title: 'Authentication', description: 'API authentication and tokens', icon: Shield, path: '/docs/api/auth' },
    { title: 'Projects API', description: 'Manage projects programmatically', icon: FileText, path: '/docs/api/projects' },
    { title: 'Tasks API', description: 'Task management endpoints', icon: Code, path: '/docs/api/tasks' },
    { title: 'AI Services', description: 'AI and ML API endpoints', icon: Zap, path: '/docs/api/ai' },
    { title: 'Webhooks', description: 'Event-driven integrations', icon: Database, path: '/docs/api/webhooks' },
  ]

  const guides = [
    { title: 'AI Copilot Setup', description: 'Configure and use AI assistance', icon: Zap, path: '/docs/guides/ai-copilot' },
    { title: 'Team Collaboration', description: 'Set up team workflows', icon: BookOpen, path: '/docs/guides/collaboration' },
    { title: 'Automation Rules', description: 'Create automated workflows', icon: Settings, path: '/docs/guides/automation' },
    { title: 'Security Best Practices', description: 'Secure your deployment', icon: Shield, path: '/docs/guides/security' },
  ]

  const reference = [
    { title: 'Architecture Overview', description: 'System architecture and design', icon: Layers, path: '/docs/ref/architecture' },
    { title: 'Data Models', description: 'Database schemas and models', icon: Database, path: '/docs/ref/models' },
    { title: 'Error Codes', description: 'API error codes reference', icon: Code, path: '/docs/ref/errors' },
    { title: 'Changelog', description: 'Release notes and changes', icon: FileText, path: '/docs/ref/changelog' },
  ]

  const getCurrentDocs = () => {
    switch (activeSection) {
      case 'getting-started': return gettingStartedDocs
      case 'api': return apiDocs
      case 'guides': return guides
      case 'reference': return reference
      default: return gettingStartedDocs
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white flex items-center gap-3">
            <Book className="w-8 h-8 text-indigo-400" />
            Documentation
          </h1>
          <p className="text-slate-400 mt-1">Learn how to use and integrate with the platform</p>
        </div>

        {/* Search */}
        <div className="relative mb-8">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
          <input
            type="text"
            placeholder="Search documentation..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-12 pr-4 py-3 bg-slate-800/50 border border-slate-700/50 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Sidebar */}
          <div className="lg:col-span-1">
            <nav className="space-y-1">
              {sections.map((section) => (
                <button
                  key={section.id}
                  onClick={() => setActiveSection(section.id)}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                    activeSection === section.id
                      ? 'bg-indigo-500/20 text-indigo-400 border border-indigo-500/30'
                      : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
                  }`}
                >
                  <section.icon className="w-5 h-5" />
                  {section.label}
                </button>
              ))}
            </nav>

            {/* Quick Links */}
            <div className="mt-8 p-4 bg-slate-800/30 border border-slate-700/50 rounded-xl">
              <h3 className="text-white font-medium mb-3">Quick Links</h3>
              <div className="space-y-2">
                <a href="#" className="flex items-center gap-2 text-slate-400 hover:text-indigo-400 text-sm">
                  <ExternalLink className="w-4 h-4" />
                  GitHub Repository
                </a>
                <a href="#" className="flex items-center gap-2 text-slate-400 hover:text-indigo-400 text-sm">
                  <ExternalLink className="w-4 h-4" />
                  API Status
                </a>
                <a href="#" className="flex items-center gap-2 text-slate-400 hover:text-indigo-400 text-sm">
                  <ExternalLink className="w-4 h-4" />
                  Community Forum
                </a>
              </div>
            </div>
          </div>

          {/* Content */}
          <div className="lg:col-span-3">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {getCurrentDocs().map((doc, i) => (
                <a
                  key={i}
                  href={doc.path}
                  className="group bg-slate-800/50 border border-slate-700/50 rounded-xl p-5 hover:border-indigo-500/50 hover:bg-slate-800/70 transition-all"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-3 mb-3">
                      <div className="p-2 bg-indigo-500/10 rounded-lg">
                        <doc.icon className="w-5 h-5 text-indigo-400" />
                      </div>
                      <h3 className="text-white font-medium group-hover:text-indigo-400 transition-colors">
                        {doc.title}
                      </h3>
                    </div>
                    <ChevronRight className="w-5 h-5 text-slate-500 group-hover:text-indigo-400 group-hover:translate-x-1 transition-all" />
                  </div>
                  <p className="text-slate-400 text-sm">{doc.description}</p>
                </a>
              ))}
            </div>

            {/* Featured Section */}
            <div className="mt-8 p-6 bg-gradient-to-r from-indigo-500/10 to-violet-500/10 border border-indigo-500/20 rounded-xl">
              <div className="flex items-center gap-3 mb-3">
                <Zap className="w-6 h-6 text-indigo-400" />
                <h3 className="text-xl font-semibold text-white">New to the Platform?</h3>
              </div>
              <p className="text-slate-300 mb-4">
                Start with our interactive tutorial to learn the basics and get your first project running in minutes.
              </p>
              <button className="px-4 py-2 bg-indigo-500 hover:bg-indigo-600 text-white rounded-lg transition-colors">
                Start Tutorial
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
