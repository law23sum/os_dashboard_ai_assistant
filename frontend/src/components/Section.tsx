import { ReactNode } from 'react'
import { LucideIcon } from 'lucide-react'

interface SectionProps {
  title?: string
  description?: string
  icon?: LucideIcon
  children: ReactNode
  action?: ReactNode
  className?: string
}

export default function Section({
  title,
  description,
  icon: Icon,
  children,
  action,
  className = '',
}: SectionProps) {
  return (
    <section className={`space-y-4 ${className}`}>
      {(title || description || action) && (
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-start gap-3 flex-1">
            {Icon && (
              <div className="p-2 rounded-lg bg-primary-500/10 border border-primary-500/20">
                <Icon className="w-4 h-4 text-primary-400" />
              </div>
            )}
            <div className="flex-1 min-w-0">
              {title && (
                <h2 className="text-lg font-semibold text-white mb-1">{title}</h2>
              )}
              {description && (
                <p className="text-sm text-slate-400">{description}</p>
              )}
            </div>
          </div>
          {action && <div className="flex-shrink-0">{action}</div>}
        </div>
      )}
      <div>{children}</div>
    </section>
  )
}

