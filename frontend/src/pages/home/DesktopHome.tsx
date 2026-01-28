import { Link } from 'react-router-dom'
import {
  Activity,
  ArrowRight,
  Cpu,
  HardDrive,
  Monitor,
  Power,
  Settings,
  Sparkles,
  Terminal,
  Zap,
} from 'lucide-react'
import { usePlatform } from '../../hooks/usePlatform'

export default function DesktopHome() {
  const { platformName, isMac, isWindows, isLinux } = usePlatform()

  const quickActions = [
    {
      icon: Terminal,
      title: 'Terminal Access',
      description: 'Run commands and scripts',
      link: '/tools',
      color: 'from-green-500/20 to-emerald-500/10',
    },
    {
      icon: Settings,
      title: 'System Settings',
      description: 'Configure your environment',
      link: '/settings',
      color: 'from-blue-500/20 to-cyan-500/10',
    },
    {
      icon: Activity,
      title: 'System Monitor',
      description: 'Track performance metrics',
      link: '/monitoring',
      color: 'from-purple-500/20 to-pink-500/10',
    },
    {
      icon: Sparkles,
      title: 'AI Assistant',
      description: 'Get help from your AI',
      link: '/chat',
      color: 'from-amber-500/20 to-yellow-500/10',
    },
  ]

  const systemInfo = [
    { label: 'Platform', value: platformName, icon: Monitor },
    { label: 'CPU Usage', value: '45%', icon: Cpu },
    { label: 'Memory', value: '8.2 GB / 16 GB', icon: HardDrive },
    { label: 'Status', value: 'Online', icon: Power },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-indigo-900/20 to-slate-900">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="absolute inset-0 bg-grid-white/[0.02] bg-[size:20px_20px]" />
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16">
          <div className="text-center">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-sm mb-8">
              <Monitor className="w-4 h-4" />
              <span>Desktop Application - {platformName}</span>
            </div>
            <h1 className="text-5xl md:text-6xl font-bold text-white mb-6">
              OS Dashboard
              <span className="block bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
                Desktop Edition
              </span>
            </h1>
            <p className="text-xl text-slate-300 max-w-2xl mx-auto mb-8">
              Native desktop experience with full system integration, offline capabilities, and
              enhanced performance for power users.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/dashboard"
                className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-indigo-500 to-purple-500 text-white rounded-lg font-medium hover:from-indigo-600 hover:to-purple-600 transition-all shadow-lg shadow-indigo-500/25"
              >
                Open Dashboard
                <ArrowRight className="w-4 h-4" />
              </Link>
              <Link
                to="/settings"
                className="inline-flex items-center gap-2 px-6 py-3 bg-slate-800/50 border border-slate-700 text-slate-200 rounded-lg font-medium hover:bg-slate-800 transition-all"
              >
                Configure Settings
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* System Info */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {systemInfo.map((info, idx) => (
            <div
              key={idx}
              className="glass-card p-6 rounded-xl border border-slate-700/50 hover:border-indigo-500/50 transition-all"
            >
              <info.icon className="w-8 h-8 text-indigo-400 mb-3" />
              <div className="text-lg font-semibold text-white mb-1">{info.value}</div>
              <div className="text-sm text-slate-400">{info.label}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-white mb-4">Quick Actions</h2>
          <p className="text-slate-400 max-w-2xl mx-auto">
            Fast access to essential desktop features and system tools
          </p>
        </div>
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {quickActions.map((action, idx) => (
            <Link
              key={idx}
              to={action.link}
              className="group glass-card p-6 rounded-xl border border-slate-700/50 hover:border-indigo-500/50 transition-all hover:scale-105"
            >
              <div className={`w-12 h-12 rounded-lg bg-gradient-to-br ${action.color} flex items-center justify-center mb-4`}>
                <action.icon className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-2 group-hover:text-indigo-400 transition-colors">
                {action.title}
              </h3>
              <p className="text-slate-400 text-sm">{action.description}</p>
              <div className="mt-4 flex items-center text-indigo-400 text-sm font-medium opacity-0 group-hover:opacity-100 transition-opacity">
                Open <ArrowRight className="w-4 h-4 ml-1" />
              </div>
            </Link>
          ))}
        </div>
      </div>

      {/* Desktop Features */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="glass-card p-8 rounded-2xl border border-slate-700/50">
          <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
            <Zap className="w-6 h-6 text-yellow-400" />
            Desktop-Specific Features
          </h2>
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-lg font-semibold text-white mb-3">Native Integration</h3>
              <ul className="space-y-2 text-slate-300">
                <li>• File system access</li>
                <li>• System notifications</li>
                <li>• Native menus and dialogs</li>
                <li>• Auto-update mechanism</li>
              </ul>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-white mb-3">Performance</h3>
              <ul className="space-y-2 text-slate-300">
                <li>• Offline-first architecture</li>
                <li>• Local data caching</li>
                <li>• Hardware acceleration</li>
                <li>• Reduced network dependency</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
