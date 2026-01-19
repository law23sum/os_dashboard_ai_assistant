import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import PageHeader from '../PageHeader'

type QuickLink = {
  title: string
  path: string
  description?: string
}

type CategoryHomeTemplateProps = {
  title: string
  description: string
  features: QuickLink[]
}

const defaultChecklist = [
  'Review category overview',
  'Pick a quick action',
  'Run a sample workflow',
  'Validate recent activity',
]

export function CategoryHomeTemplate({ title, description, features }: CategoryHomeTemplateProps) {
  const [checked, setChecked] = useState<Record<string, boolean>>({})

  const quickLinks = useMemo(() => features.slice(0, 6), [features])

  const toggleChecklist = (item: string) => {
    setChecked((prev) => ({ ...prev, [item]: !prev[item] }))
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title={title}
        description={description}
        actions={(
          <div className="flex flex-wrap gap-2">
            <button type="button" className="btn-primary">Create New</button>
            <button type="button" className="btn-secondary">Run Workflow</button>
            <button type="button" className="btn-secondary">Import Data</button>
          </div>
        )}
      />

      <section className="glass-card p-6 space-y-3" data-page-section="overview">
        <h2 className="text-lg font-semibold text-[color:var(--osd-text)]">Overview</h2>
        <p className="text-sm text-[color:var(--osd-muted)]">{description}</p>
      </section>

      <section className="grid gap-4 lg:grid-cols-3">
        <div
          className="glass-card p-6 space-y-3 lg:col-span-2"
          data-page-section="quick-links"
        >
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-[color:var(--osd-text)]">Quick Links</h2>
            <span className="text-xs text-[color:var(--osd-muted)]">Top features</span>
          </div>
          <div className="grid gap-3 md:grid-cols-2">
            {quickLinks.map((link) => (
              <Link
                key={link.path}
                to={link.path}
                className="rounded-xl border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)]/40 p-4 hover:border-[color:var(--osd-accent)] transition-colors"
              >
                <div className="text-sm font-semibold text-[color:var(--osd-text)]">{link.title}</div>
                <p className="mt-1 text-xs text-[color:var(--osd-muted)]">
                  {link.description ?? `Open ${link.title} workflow.`}
                </p>
              </Link>
            ))}
          </div>
        </div>

        <div className="glass-card p-6 space-y-3" data-page-section="getting-started">
          <h2 className="text-lg font-semibold text-[color:var(--osd-text)]">Getting Started</h2>
          <ul className="space-y-2 text-sm">
            {defaultChecklist.map((item) => (
              <li key={item} className="flex items-center gap-2">
                <input
                  id={`check-${item}`}
                  type="checkbox"
                  checked={Boolean(checked[item])}
                  onChange={() => toggleChecklist(item)}
                  className="h-4 w-4 rounded border-[color:var(--osd-border)] bg-[color:var(--osd-surface)]"
                />
                <label htmlFor={`check-${item}`} className="text-[color:var(--osd-text)]">
                  {item}
                </label>
              </li>
            ))}
          </ul>
        </div>
      </section>

      <section className="glass-card p-6 space-y-4" data-page-section="recent-activity">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-[color:var(--osd-text)]">Recent Activity</h2>
          <button type="button" className="text-xs text-[color:var(--osd-muted)]">View all</button>
        </div>
        <div className="grid gap-3 md:grid-cols-3">
          {[
            { title: 'Latest run', detail: 'No runs yet. Launch a workflow to populate activity.' },
            { title: 'Most viewed', detail: quickLinks[0]?.title ?? 'No feature selected' },
            { title: 'Pending approvals', detail: '0 pending reviews' },
          ].map((item) => (
            <div
              key={item.title}
              className="rounded-xl border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)]/40 p-4"
            >
              <div className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">
                {item.title}
              </div>
              <div className="mt-2 text-sm text-[color:var(--osd-text)]">{item.detail}</div>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}
