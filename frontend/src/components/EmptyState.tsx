import { LucideIcon } from 'lucide-react'
import { ReactNode } from 'react'

interface EmptyStateProps {
  icon: LucideIcon
  title: string
  description: string
  action?: ReactNode
  gradient?: string
}

export default function EmptyState({
  icon: Icon,
  title,
  description,
  action,
  gradient = 'from-slate-800/50 to-slate-900/50',
}: EmptyStateProps) {
  return (
    <div className={`flex flex-col items-center justify-center py-16 px-6 rounded-2xl border border-slate-700/50 bg-gradient-to-br ${gradient}`}>
      <div className="p-4 rounded-2xl bg-slate-800/50 border border-slate-700/50 mb-4">
        <Icon className="w-12 h-12 text-slate-500" />
      </div>
      <h3 className="text-lg font-semibold text-white mb-2">{title}</h3>
      <p className="text-sm text-slate-400 text-center max-w-md mb-6">{description}</p>
      {action && <div>{action}</div>}
    </div>
  )
}






