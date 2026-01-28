import { Link } from 'react-router-dom'
import {
  ArrowRight,
  Bell,
  Camera,
  Cloud,
  MessageSquare,
  Mic,
  Smartphone,
  Sparkles,
  Touch,
  Zap,
} from 'lucide-react'
import { usePlatform } from '../../hooks/usePlatform'

export default function MobileHome() {
  const { platformName } = usePlatform()

  const mobileFeatures = [
    {
      icon: Touch,
      title: 'Touch-Optimized',
      description: 'Designed for touch interactions',
      color: 'from-blue-500/20 to-cyan-500/10',
    },
    {
      icon: Cloud,
      title: 'Offline Support',
      description: 'Works without internet connection',
      color: 'from-purple-500/20 to-pink-500/10',
    },
    {
      icon: Bell,
      title: 'Push Notifications',
      description: 'Stay updated with real-time alerts',
      color: 'from-emerald-500/20 to-teal-500/10',
    },
    {
      icon: Camera,
      title: 'Camera Integration',
      description: 'Capture and process images',
      color: 'from-amber-500/20 to-yellow-500/10',
    },
  ]

  const quickActions = [
    {
      icon: MessageSquare,
      title: 'Chat',
      link: '/chat',
      color: 'from-blue-500 to-cyan-500',
    },
    {
      icon: Sparkles,
      title: 'AI Assistant',
      link: '/ai-os',
      color: 'from-purple-500 to-pink-500',
    },
    {
      icon: Cloud,
      title: 'Projects',
      link: '/projects',
      color: 'from-emerald-500 to-teal-500',
    },
    {
      icon: Bell,
      title: 'Notifications',
      link: '/monitoring',
      color: 'from-amber-500 to-orange-500',
    },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900/20 to-slate-900 pb-20">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="absolute inset-0 bg-grid-white/[0.02] bg-[size:20px_20px]" />
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-12 pb-8">
          <div className="text-center">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-purple-500/10 border border-purple-500/20 text-purple-300 text-sm mb-6">
              <Smartphone className="w-4 h-4" />
              <span>Mobile App - {platformName}</span>
            </div>
            <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
              OS Dashboard
              <span className="block bg-gradient-to-r from-purple-400 via-pink-400 to-rose-400 bg-clip-text text-transparent">
                Mobile
              </span>
            </h1>
            <p className="text-lg text-slate-300 max-w-xl mx-auto mb-6">
              Take your productivity on the go with our mobile-optimized experience
            </p>
            <Link
              to="/dashboard"
              className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-xl font-medium hover:from-purple-600 hover:to-pink-600 transition-all shadow-lg shadow-purple-500/25"
            >
              Get Started
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </div>

      {/* Quick Actions Grid */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-2 gap-4">
          {quickActions.map((action, idx) => (
            <Link
              key={idx}
              to={action.link}
              className="group glass-card p-6 rounded-2xl border border-slate-700/50 hover:border-purple-500/50 transition-all active:scale-95"
            >
              <div className={`w-14 h-14 rounded-xl bg-gradient-to-br ${action.color} flex items-center justify-center mb-4 shadow-lg`}>
                <action.icon className="w-7 h-7 text-white" />
              </div>
              <h3 className="text-lg font-semibold text-white">{action.title}</h3>
            </Link>
          ))}
        </div>
      </div>

      {/* Mobile Features */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h2 className="text-2xl font-bold text-white mb-6 text-center">Mobile Features</h2>
        <div className="grid grid-cols-2 gap-4">
          {mobileFeatures.map((feature, idx) => (
            <div
              key={idx}
              className="glass-card p-5 rounded-xl border border-slate-700/50"
            >
              <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${feature.color} flex items-center justify-center mb-3`}>
                <feature.icon className="w-5 h-5 text-white" />
              </div>
              <h3 className="text-base font-semibold text-white mb-1">{feature.title}</h3>
              <p className="text-xs text-slate-400">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Mobile-Specific Info */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="glass-card p-6 rounded-2xl border border-slate-700/50">
          <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <Zap className="w-5 h-5 text-yellow-400" />
            Optimized for Mobile
          </h2>
          <div className="space-y-3 text-slate-300 text-sm">
            <div className="flex items-start gap-3">
              <Touch className="w-5 h-5 text-purple-400 mt-0.5 flex-shrink-0" />
              <div>
                <div className="font-semibold text-white">Touch Gestures</div>
                <div className="text-slate-400">Swipe, pinch, and tap interactions</div>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <Cloud className="w-5 h-5 text-blue-400 mt-0.5 flex-shrink-0" />
              <div>
                <div className="font-semibold text-white">Offline Mode</div>
                <div className="text-slate-400">Continue working without internet</div>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <Mic className="w-5 h-5 text-green-400 mt-0.5 flex-shrink-0" />
              <div>
                <div className="font-semibold text-white">Voice Input</div>
                <div className="text-slate-400">Use voice commands for quick actions</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
