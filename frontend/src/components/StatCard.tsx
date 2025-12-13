import { LucideIcon, TrendingUp, TrendingDown } from 'lucide-react'
import { ReactNode } from 'react'

interface StatCardProps {
  title: string
  value: string | number
  icon?: LucideIcon
  trend?: {
    value: number
    label: string
  }
  description?: string
  gradient?: string
  action?: ReactNode
}

export default function StatCard({
  title,
  value,
  icon: Icon,
  trend,
  description,
  gradient = 'from-slate-800/50 to-slate-900/50',
  action,
}: StatCardProps) {
  const TrendIcon = trend && trend.value > 0 ? TrendingUp : TrendingDown
  const trendColor = trend && trend.value > 0 ? 'text-emerald-400' : 'text-red-400'

  return (
    <div className={`relative overflow-hidden rounded-xl border border-slate-700/50 bg-gradient-to-br ${gradient} p-5 hover:border-slate-600/50 transition-all group`}>
      <div className="relative z-10">
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-2">
            {Icon && (
              <div className="p-2 rounded-lg bg-white/5 border border-white/10">
                <Icon className="w-4 h-4 text-slate-400" />
              </div>
            )}
            <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">{title}</p>
          </div>
          {action}
        </div>
        <div className="mb-2">
          <p className="text-2xl font-bold text-white">{value}</p>
        </div>
        {description && (
          <p className="text-xs text-slate-500 mb-2">{description}</p>
        )}
        {trend && (
          <div className={`flex items-center gap-1 text-xs font-medium ${trendColor}`}>
            <TrendIcon className="w-3.5 h-3.5" />
            <span>{Math.abs(trend.value)}%</span>
            <span className="text-slate-500">{trend.label}</span>
          </div>
        )}
      </div>
    </div>
  )
}

