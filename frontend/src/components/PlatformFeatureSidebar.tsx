import { useEffect, useMemo } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { getPlatformFeatures } from '../data/platformFeatures'

export default function PlatformFeatureSidebar() {
  const location = useLocation()
  const features = useMemo(() => getPlatformFeatures(location.pathname), [location.pathname])
  const activeHash = location.hash || '#overview'

  useEffect(() => {
    const id = (location.hash || '').replace(/^#/, '')
    if (!id) return
    const el = document.getElementById(id)
    if (!el) return
    // Let the current render commit before scrolling.
    requestAnimationFrame(() => {
      el.scrollIntoView({ behavior: 'smooth', block: 'start' })
    })
  }, [location.hash, location.pathname])

  if (!features || features.length === 0) {
    return null
  }

  return (
    <aside className="hidden lg:block w-72 shrink-0">
      <div className="sticky top-[5.75rem] rounded-3xl border border-[color:var(--osd-border)] bg-[color:var(--osd-surfaceAlt)] p-4">
        <p className="text-xs uppercase tracking-[0.35em] text-[color:var(--osd-muted)]">Platform features</p>
        <p className="mt-1 text-sm font-semibold text-[color:var(--osd-text)]">Quick navigation</p>
        <div className="mt-4 max-h-[calc(100vh-9.5rem)] overflow-y-auto pr-1 space-y-1">
          {features.map((feature) => {
            const targetHash = feature.href.startsWith('#') ? feature.href : ''
            const isActive = targetHash ? activeHash === targetHash : false
            const to = feature.href.startsWith('#')
              ? { pathname: location.pathname, hash: feature.href }
              : feature.href
            return (
              <Link
                key={feature.id}
                to={to}
                className={`block rounded-2xl px-3 py-2 text-sm transition ${
                  isActive
                    ? 'border border-[color:var(--osd-accent)] bg-[color:var(--osd-accent)]/10 text-[color:var(--osd-text)]'
                    : 'border border-transparent text-[color:var(--osd-muted)] hover:border-[color:var(--osd-border)] hover:text-[color:var(--osd-text)]'
                }`}
                title={feature.description}
              >
                <div className="font-medium">{feature.label}</div>
                {feature.description ? (
                  <div className="text-xs text-[color:var(--osd-muted)]">{feature.description}</div>
                ) : null}
              </Link>
            )
          })}
        </div>
      </div>
    </aside>
  )
}

