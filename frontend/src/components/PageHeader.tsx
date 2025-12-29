import { ReactNode } from 'react'
import { LucideIcon } from 'lucide-react'

interface PageHeaderProps {
  title: string
  description?: string
  icon?: LucideIcon
  action?: ReactNode
  actions?: ReactNode
  badge?: string | number
  gradient?: string
  eyebrow?: string
  className?: string
}

export default function PageHeader({
  title,
  description,
  icon: Icon,
  action,
  actions,
  badge,
  gradient = 'from-primary-500/10 via-violet-500/5 to-transparent',
  eyebrow,
  className = '',
}: PageHeaderProps) {
  const headerActions = actions || action

  return (
    <div className={`page-header ${className}`}>
      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
        <div className="flex-1 min-w-0">
          {eyebrow && (
            <div className="page-header__eyebrow mb-2">{eyebrow}</div>
          )}
          <div className="flex items-center gap-3 mb-2">
            {Icon && (
              <div className="p-2 rounded-xl bg-[color:var(--osd-accentSoft)]">
                <Icon className="w-6 h-6 text-[color:var(--osd-accent)]" />
              </div>
            )}
            <h1 className="page-header__title">{title}</h1>
            {badge !== undefined && (
              <span className="px-2.5 py-0.5 text-xs font-semibold bg-primary-500/20 text-primary-300 rounded-full border border-primary-500/30">
                {badge}
              </span>
            )}
          </div>
          {description && (
            <p className="page-header__description">{description}</p>
          )}
        </div>
        {headerActions && (
          <div className="page-header__actions flex-shrink-0">
            {headerActions}
          </div>
        )}
      </div>
    </div>
  )
}
