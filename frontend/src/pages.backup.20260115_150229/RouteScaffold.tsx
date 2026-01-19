import { useIARouteContext } from '../navigation/iaContext'
import { useActor } from '../contexts/ActorContext'
import { getCategories, getFeatures, getPlatforms } from '../data/iaManifest'
import { CategoryHomeTemplate } from '../components/templates/CategoryHomeTemplate'
import { FeaturePageTemplate } from '../components/templates/FeaturePageTemplate'
import { PlatformLandingTemplate } from '../components/templates/PlatformLandingTemplate'
import IARouteFallback from './IARouteFallback'

export default function RouteScaffold() {
  const routeContext = useIARouteContext()
  const { currentActor } = useActor()

  const allowedPlatforms = getPlatforms(currentActor)
  const activePlatform = routeContext.platform
    ? allowedPlatforms.find((platform) => platform.id === routeContext.platform?.id)
    : undefined

  if (routeContext.isPlatformLanding && activePlatform) {
    const categories = getCategories(activePlatform.id, currentActor)
    return (
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
    if (!activeCategory) {
      return <IARouteFallback />
    }

    const features = activeCategory.features ?? []
    return (
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

  if (routeContext.feature && routeContext.category && activePlatform) {
    const allowedCategories = getCategories(activePlatform.id, currentActor)
    const activeCategory = allowedCategories.find((category) => category.id === routeContext.category?.id)
    if (!activeCategory) {
      return <IARouteFallback />
    }

    const allowedFeatures = getFeatures(activePlatform.id, activeCategory.id, currentActor)
    const activeFeature = allowedFeatures.find((feature) => feature.route === routeContext.feature?.route)
    if (!activeFeature) {
      return <IARouteFallback />
    }

    return (
      <FeaturePageTemplate
        platform={activePlatform}
        category={activeCategory}
        feature={activeFeature}
      />
    )
  }

  return <IARouteFallback />
}
