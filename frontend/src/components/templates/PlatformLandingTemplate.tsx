import { Link } from 'react-router-dom'
import PageHeader from '../PageHeader'

type PlatformCategoryCard = {
  id: string
  title: string
  path: string
  description?: string
  featureCount: number
  badge?: string
}

type PlatformLandingTemplateProps = {
  title: string
  description: string
  categories: PlatformCategoryCard[]
}

export function PlatformLandingTemplate({ title, description, categories }: PlatformLandingTemplateProps) {
  return (
    <div className="space-y-6">
      <PageHeader title={title} description={description} />

      <section
        className="grid gap-4 md:grid-cols-2 xl:grid-cols-3"
        data-page-section="category-grid"
      >
        {categories.map((category) => (
          <Link
            key={category.id}
            to={category.path}
            className="group glass-card p-6 border border-[color:var(--osd-border)]/60 hover:border-[color:var(--osd-accent)] transition-colors"
          >
            <div className="flex items-center justify-between gap-2">
              <h2 className="text-base font-semibold text-[color:var(--osd-text)]">
                {category.title}
              </h2>
              {category.badge ? (
                <span className="text-[0.55rem] uppercase tracking-wider px-2 py-0.5 rounded-full border border-emerald-400/40 text-emerald-300">
                  {category.badge}
                </span>
              ) : null}
            </div>
            <p className="mt-2 text-sm text-[color:var(--osd-muted)]">
              {category.description ?? `Jump into ${category.title} dashboards.`}
            </p>
            <div className="mt-4 text-xs text-[color:var(--osd-muted)]">
              {category.featureCount} features available
            </div>
          </Link>
        ))}
      </section>
    </div>
  )
}
