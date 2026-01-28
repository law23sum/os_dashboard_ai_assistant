import { Link } from 'react-router-dom'
import {
  ArrowRight,
  Chrome,
  Globe,
  Link as LinkIcon,
  Puzzle,
  Search,
  Shield,
  Sparkles,
  Zap,
} from 'lucide-react'
import { usePlatform } from '../../hooks/usePlatform'

export default function ExtensionHome() {
  const { platformName } = usePlatform()

  const extensionFeatures = [
    {
      icon: Search,
      title: 'Quick Search',
      description: 'Search across all your data instantly',
      color: 'from-blue-500/20 to-cyan-500/10',
      link: '/search',
    },
    {
      icon: LinkIcon,
      title: 'Page Capture',
      description: 'Save and organize web content',
      color: 'from-purple-500/20 to-pink-500/10',
      link: '/projects',
    },
    {
      icon: Sparkles,
      title: 'AI Assistant',
      description: 'Get AI help on any webpage',
      color: 'from-emerald-500/20 to-teal-500/10',
      link: '/chat',
    },
    {
      icon: Shield,
      title: 'Security Check',
      description: 'Verify page security and compliance',
      color: 'from-red-500/20 to-orange-500/10',
      link: '/audit',
    },
  ]

  const browserInfo = [
    { label: 'Browser', value: 'Chrome', icon: Chrome },
    { label: 'Version', value: 'Manifest V3', icon: Puzzle },
    { label: 'Status', value: 'Active', icon: Shield },
    { label: 'Sync', value: 'Enabled', icon: Globe },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-cyan-900/20 to-slate-900">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="absolute inset-0 bg-grid-white/[0.02] bg-[size:20px_20px]" />
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-16 pb-12">
          <div className="text-center">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-300 text-sm mb-6">
              <Puzzle className="w-4 h-4" />
              <span>Browser Extension - {platformName}</span>
            </div>
            <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
              OS Dashboard
              <span className="block bg-gradient-to-r from-cyan-400 via-blue-400 to-indigo-400 bg-clip-text text-transparent">
                Browser Extension
              </span>
            </h1>
            <p className="text-lg text-slate-300 max-w-xl mx-auto mb-6">
              Access your dashboard and AI assistant directly from your browser.
              Work seamlessly across the web.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/dashboard"
                className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-cyan-500 to-blue-500 text-white rounded-lg font-medium hover:from-cyan-600 hover:to-blue-600 transition-all shadow-lg shadow-cyan-500/25"
              >
                Open Dashboard
                <ArrowRight className="w-4 h-4" />
              </Link>
              <button
                onClick={() => {
                  // Extension-specific action
                  if (window.chrome?.action) {
                    window.chrome.action.openPopup()
                  }
                }}
                className="inline-flex items-center gap-2 px-6 py-3 bg-slate-800/50 border border-slate-700 text-slate-200 rounded-lg font-medium hover:bg-slate-800 transition-all"
              >
                Open Popup
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Browser Info */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {browserInfo.map((info, idx) => (
            <div
              key={idx}
              className="glass-card p-5 rounded-xl border border-slate-700/50"
            >
              <info.icon className="w-6 h-6 text-cyan-400 mb-2" />
              <div className="text-lg font-semibold text-white mb-1">{info.value}</div>
              <div className="text-xs text-slate-400">{info.label}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Extension Features */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center mb-8">
          <h2 className="text-2xl font-bold text-white mb-3">Extension Features</h2>
          <p className="text-slate-400 text-sm">
            Powerful tools available right in your browser
          </p>
        </div>
        <div className="grid md:grid-cols-2 gap-4">
          {extensionFeatures.map((feature, idx) => (
            <Link
              key={idx}
              to={feature.link}
              className="group glass-card p-6 rounded-xl border border-slate-700/50 hover:border-cyan-500/50 transition-all hover:scale-105"
            >
              <div className={`w-12 h-12 rounded-lg bg-gradient-to-br ${feature.color} flex items-center justify-center mb-4`}>
                <feature.icon className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-lg font-semibold text-white mb-2 group-hover:text-cyan-400 transition-colors">
                {feature.title}
              </h3>
              <p className="text-slate-400 text-sm">{feature.description}</p>
              <div className="mt-4 flex items-center text-cyan-400 text-sm font-medium opacity-0 group-hover:opacity-100 transition-opacity">
                Try it <ArrowRight className="w-4 h-4 ml-1" />
              </div>
            </Link>
          ))}
        </div>
      </div>

      {/* Extension Capabilities */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="glass-card p-6 rounded-2xl border border-slate-700/50">
          <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <Zap className="w-5 h-5 text-yellow-400" />
            Extension Capabilities
          </h2>
          <div className="grid md:grid-cols-2 gap-4 text-sm">
            <div>
              <h3 className="text-base font-semibold text-white mb-2">Content Scripts</h3>
              <ul className="space-y-1 text-slate-300">
                <li>• Inject UI on any webpage</li>
                <li>• Extract page content</li>
                <li>• Modify page behavior</li>
              </ul>
            </div>
            <div>
              <h3 className="text-base font-semibold text-white mb-2">Background Service</h3>
              <ul className="space-y-1 text-slate-300">
                <li>• Run tasks in background</li>
                <li>• Sync data across devices</li>
                <li>• Process notifications</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
