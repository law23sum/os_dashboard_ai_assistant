import { Link } from 'react-router-dom'
import {
  Activity,
  ArrowRight,
  CheckCircle,
  Cloud,
  Cpu,
  Database,
  Globe,
  Layers,
  MessageSquare,
  Rocket,
  Search,
  Shield,
  Sparkles,
  TrendingUp,
  Zap,
} from 'lucide-react'
import { usePlatform } from '../../hooks/usePlatform'

export default function WebHome() {
  const { platformName } = usePlatform()

  const features = [
    {
      icon: Rocket,
      title: 'AI-Powered Workflows',
      description: 'Automate complex tasks with intelligent orchestration',
      color: 'from-blue-500/20 to-cyan-500/10',
      link: '/ai-os',
    },
    {
      icon: Search,
      title: 'Semantic Search',
      description: 'Find information instantly with AI-powered search',
      color: 'from-purple-500/20 to-pink-500/10',
      link: '/search',
    },
    {
      icon: Database,
      title: 'Data Management',
      description: 'Organize and manage your projects and tasks',
      color: 'from-emerald-500/20 to-teal-500/10',
      link: '/projects',
    },
    {
      icon: Shield,
      title: 'Security & Compliance',
      description: 'Enterprise-grade security and audit capabilities',
      color: 'from-red-500/20 to-orange-500/10',
      link: '/audit',
    },
    {
      icon: MessageSquare,
      title: 'AI Assistant',
      description: 'Get help from your AI assistant anytime',
      color: 'from-indigo-500/20 to-blue-500/10',
      link: '/chat',
    },
    {
      icon: TrendingUp,
      title: 'Analytics & Insights',
      description: 'Track performance and gain actionable insights',
      color: 'from-amber-500/20 to-yellow-500/10',
      link: '/analytics',
    },
  ]

  const stats = [
    { label: 'Active Projects', value: '12', icon: Layers },
    { label: 'Tasks Completed', value: '1,234', icon: CheckCircle },
    { label: 'AI Interactions', value: '5,678', icon: Sparkles },
    { label: 'System Uptime', value: '99.9%', icon: Activity },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900/20 to-slate-900">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="absolute inset-0 bg-grid-white/[0.02] bg-[size:20px_20px]" />
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16">
          <div className="text-center">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-300 text-sm mb-8">
              <Globe className="w-4 h-4" />
              <span>Web Platform - {platformName}</span>
            </div>
            <h1 className="text-5xl md:text-6xl font-bold text-white mb-6">
              OS Dashboard
              <span className="block bg-gradient-to-r from-blue-400 via-cyan-400 to-teal-400 bg-clip-text text-transparent">
                AI Assistant
              </span>
            </h1>
            <p className="text-xl text-slate-300 max-w-2xl mx-auto mb-8">
              Unified platform for AI-powered workflows, project management, and intelligent automation.
              Built for the modern web with cutting-edge technology.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/dashboard"
                className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-500 to-cyan-500 text-white rounded-lg font-medium hover:from-blue-600 hover:to-cyan-600 transition-all shadow-lg shadow-blue-500/25"
              >
                Get Started
                <ArrowRight className="w-4 h-4" />
              </Link>
              <Link
                to="/docs"
                className="inline-flex items-center gap-2 px-6 py-3 bg-slate-800/50 border border-slate-700 text-slate-200 rounded-lg font-medium hover:bg-slate-800 transition-all"
              >
                View Documentation
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {stats.map((stat, idx) => (
            <div
              key={idx}
              className="glass-card p-6 rounded-xl border border-slate-700/50 hover:border-blue-500/50 transition-all"
            >
              <stat.icon className="w-8 h-8 text-blue-400 mb-3" />
              <div className="text-3xl font-bold text-white mb-1">{stat.value}</div>
              <div className="text-sm text-slate-400">{stat.label}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Features Grid */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-white mb-4">Core Features</h2>
          <p className="text-slate-400 max-w-2xl mx-auto">
            Everything you need to manage projects, automate workflows, and leverage AI capabilities
          </p>
        </div>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, idx) => (
            <Link
              key={idx}
              to={feature.link}
              className="group glass-card p-6 rounded-xl border border-slate-700/50 hover:border-blue-500/50 transition-all hover:scale-105"
            >
              <div className={`w-12 h-12 rounded-lg bg-gradient-to-br ${feature.color} flex items-center justify-center mb-4`}>
                <feature.icon className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-2 group-hover:text-blue-400 transition-colors">
                {feature.title}
              </h3>
              <p className="text-slate-400 text-sm">{feature.description}</p>
              <div className="mt-4 flex items-center text-blue-400 text-sm font-medium opacity-0 group-hover:opacity-100 transition-opacity">
                Explore <ArrowRight className="w-4 h-4 ml-1" />
              </div>
            </Link>
          ))}
        </div>
      </div>

      {/* Tech Stack Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="glass-card p-8 rounded-2xl border border-slate-700/50">
          <h2 className="text-2xl font-bold text-white mb-6">Built with Modern Technology</h2>
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                <Zap className="w-5 h-5 text-yellow-400" />
                Frontend Stack
              </h3>
              <ul className="space-y-2 text-slate-300">
                <li>• React 18 + TypeScript</li>
                <li>• Tailwind CSS + shadcn/ui</li>
                <li>• Zustand for state management</li>
                <li>• React Query for data fetching</li>
              </ul>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                <Cloud className="w-5 h-5 text-blue-400" />
                Backend Services
              </h3>
              <ul className="space-y-2 text-slate-300">
                <li>• Temporal for workflows</li>
                <li>• PostgreSQL + CockroachDB</li>
                <li>• OpenSearch for search</li>
                <li>• Kafka for messaging</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
