import { useMemo } from 'react'
import { useActor } from '../contexts/ActorContext'
import { findRouteContext, getCategories, getFeatures, getPlatforms } from '../data/iaManifest'
import { CategoryHomeTemplate } from './templates/CategoryHomeTemplate'
import { FeaturePageTemplate } from './templates/FeaturePageTemplate'
import { PlatformLandingTemplate } from './templates/PlatformLandingTemplate'

interface MvpScaffoldProps {
  title: string
  description?: string
  route?: string
  todo?: string[]
}

export default function MvpScaffold({ title, description, route, todo }: MvpScaffoldProps) {
  const { currentActor } = useActor()
  const routeContext = useMemo(() => (route ? findRouteContext(route) : undefined), [route])
  const todoItems = (todo ?? []).filter((item) => item.trim().length > 0)
  let content: JSX.Element | null = null

  if (route && routeContext?.platform) {
    const allowedPlatforms = getPlatforms(currentActor)
    const activePlatform = allowedPlatforms.find((platform) => platform.id === routeContext.platform?.id)

    if (routeContext.isPlatformLanding && activePlatform) {
      const categories = getCategories(activePlatform.id, currentActor)
      content = (
        <PlatformLandingTemplate
          title={activePlatform.label}
          description={`Browse ${activePlatform.label} categories and dashboards.`}
          categories={categories.map((category) => ({
            id: category.id,
            title: category.label,
            path: category.homeRoute,
            description: `Dashboards, workflows, and tooling for ${category.label}.`,
            featureCount: category.features.length,
          }))}
        />
      )
    }

    if (routeContext.isCategoryHome && routeContext.category && activePlatform) {
      const allowedCategories = getCategories(activePlatform.id, currentActor)
      const activeCategory = allowedCategories.find((category) => category.id === routeContext.category?.id)
      if (activeCategory) {
        const features = activeCategory.features ?? []
        content = (
          <CategoryHomeTemplate
            title={activeCategory.label}
            description={`Navigate to features in ${activeCategory.label}.`}
            features={features.map((feature) => ({
              title: feature.label,
              path: feature.route,
            }))}
          />
        )
      }
    }

    if (routeContext.feature && routeContext.category && activePlatform) {
      const allowedCategories = getCategories(activePlatform.id, currentActor)
      const activeCategory = allowedCategories.find((category) => category.id === routeContext.category?.id)
      if (activeCategory) {
        const allowedFeatures = getFeatures(activePlatform.id, activeCategory.id, currentActor)
        const activeFeature = allowedFeatures.find((feature) => feature.route === routeContext.feature?.route)
        if (activeFeature) {
          content = (
            <FeaturePageTemplate
              platform={activePlatform}
              category={activeCategory}
              feature={activeFeature}
            />
          )
        }
      }
    }
  }

  if (!content) {
    const fallbackDescription = description ?? `Configure and execute ${title}.`
    content = <FeaturePageTemplate title={title} description={fallbackDescription} />
  }

  if (todoItems.length === 0) {
    return content
  }

  return (
    <div className="space-y-6">
      {content}
      <section className="glass-card p-6">
        <h2 className="text-lg font-semibold text-[color:var(--osd-text)]">Next steps</h2>
        <ul className="mt-3 space-y-2 text-sm text-[color:var(--osd-muted)]">
          {todoItems.map((item) => (
            <li key={item} className="flex items-start gap-2">
              <span className="mt-1 h-2 w-2 rounded-full bg-[color:var(--osd-accent)]" />
              <span>{item}</span>
            </li>
          ))}
        </ul>
      </section>
    </div>
  )
}






