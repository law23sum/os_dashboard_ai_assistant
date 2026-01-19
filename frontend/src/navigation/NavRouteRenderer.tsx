import { Component, Suspense, lazy, useMemo } from 'react'
import type { ReactNode } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useIARouteContext } from './iaContext'
import { useActor } from '../contexts/ActorContext'
import { getCategories, getFeatures, getPlatforms } from '../data/iaManifest'
import { CategoryHomeTemplate } from '../components/templates/CategoryHomeTemplate'
import { FeaturePageTemplate } from '../components/templates/FeaturePageTemplate'
import { PlatformLandingTemplate } from '../components/templates/PlatformLandingTemplate'
import PolicySimulator from '../pages/governance/policy/PolicySimulator'
import { routeComponentMap, routeComponentRoutes } from './routeComponentMap'
import { routeUsesFeatureTemplate } from './routeComponentMeta'

const pageModules = import.meta.glob([
  '/src/pages/**/*.tsx',
  '!/src/pages/**/__tests__/**',
  '!/src/pages/Login.tsx',
  '!/src/pages/Signup.tsx',
  '!/src/pages/Admin.tsx',
  '!/src/pages/Documentation.tsx',
  '!/src/pages/ResponsesChat.tsx',
  '!/src/pages/FutureDeck.tsx',
  '!/src/pages/pms/PmsProjectDetail.tsx',
  '!/src/pages/governance/policy/PolicySimulator.tsx',
])

const normalizeRoute = (route: string) => (route === '/' ? '/' : route.replace(/\/+$/, ''))

const toModulePath = (componentPath: string) => componentPath.replace(/^frontend\/src/, '/src')

const resolveComponentPathForRoute = (route: string) => {
  const normalized = normalizeRoute(route)
  const direct = routeComponentMap[normalized]
  if (direct) return direct
  for (const candidate of routeComponentRoutes) {
    if (normalized === candidate || normalized.startsWith(`${candidate}/`)) {
      return routeComponentMap[candidate]
    }
  }
  return undefined
}

type RouteComponentBoundaryProps = {
  fallback: ReactNode
  children: ReactNode
}

class RouteComponentBoundary extends Component<RouteComponentBoundaryProps, { hasError: boolean }> {
  state = { hasError: false }

  static getDerivedStateFromError() {
    return { hasError: true }
  }

  componentDidCatch(error: Error) {
    console.warn('Route component failed to render:', error)
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback
    }
    return this.props.children
  }
}

export default function NavRouteRenderer() {
  const location = useLocation()
  const routeContext = useIARouteContext()
  const { currentActor } = useActor()

  const allowedPlatforms = getPlatforms(currentActor)
  const fallbackCategory = allowedPlatforms[0]?.categories?.[0]
  const fallbackPath = fallbackCategory?.homeRoute ?? allowedPlatforms[0]?.path ?? '/'

  const activePlatform = routeContext.platform
    ? allowedPlatforms.find((platform) => platform.id === routeContext.platform?.id)
    : undefined

  const normalizedPath = normalizeRoute(location.pathname)
  const hasRenderableRoute = routeContext.isCategoryHome || Boolean(routeContext.feature)
  const componentPath = useMemo(() => {
    if (!hasRenderableRoute) return undefined
    return resolveComponentPathForRoute(normalizedPath)
  }, [hasRenderableRoute, normalizedPath])
  const usesFeatureTemplate = Boolean(routeUsesFeatureTemplate[normalizedPath])
  const modulePath = componentPath ? toModulePath(componentPath) : undefined
  const moduleLoader = modulePath ? pageModules[modulePath] : undefined
  const LazyComponent = useMemo(() => {
    if (!moduleLoader) return null
    return lazy(async () => {
      const mod = await moduleLoader()
      const resolved = mod.default ?? mod[Object.keys(mod)[0]]
      if (!resolved) {
        throw new Error(`No export found for ${modulePath}`)
      }
      return { default: resolved }
    })
  }, [moduleLoader, modulePath])

  if (routeContext.platform && !activePlatform) {
    return <Navigate to={fallbackPath} replace />
  }

  if (routeContext.isPlatformLanding && activePlatform) {
    const categories = getCategories(activePlatform.id, currentActor)
    return (
      <PlatformLandingTemplate
        title={activePlatform.label}
        description={`Browse ${activePlatform.label} categories and dashboards.`}
        categories={categories.map((category) => {
          const newCount = category.features.filter((feature) => feature.isNew).length
          return {
            id: category.id,
            title: category.label,
            path: category.homeRoute,
            description: `Dashboards, workflows, and tooling for ${category.label}.`,
            featureCount: category.features.length,
            badge: newCount > 0 ? 'New' : undefined,
          }
        })}
      />
    )
  }

  // If we have a category home, render the category home template
  if (routeContext.isCategoryHome && routeContext.category && activePlatform) {
    const allowedCategories = getCategories(activePlatform.id, currentActor)
    const activeCategory = allowedCategories.find((category) => category.id === routeContext.category?.id)
    if (!activeCategory) {
      return <Navigate to={fallbackPath} replace />
    }

    const features = activeCategory.features ?? []
    const fallbackElement = (
      <CategoryHomeTemplate
        title={activeCategory.label}
        description={`Navigate to features in ${activeCategory.label}.`}
        features={features.map((feature) => ({
          title: feature.label,
          path: feature.route,
        }))}
      />
    )

    if (LazyComponent) {
      if (!usesFeatureTemplate) {
        return (
          <RouteComponentBoundary fallback={fallbackElement}>
            <Suspense fallback={<div className="p-6 text-sm text-[color:var(--osd-muted)]">Loading…</div>}>
              <FeaturePageTemplate
                platform={activePlatform}
                category={activeCategory}
                feature={undefined}
              >
                <LazyComponent />
              </FeaturePageTemplate>
            </Suspense>
          </RouteComponentBoundary>
        )
      }
      return (
        <RouteComponentBoundary fallback={fallbackElement}>
          <Suspense fallback={<div className="p-6 text-sm text-[color:var(--osd-muted)]">Loading…</div>}>
            <LazyComponent />
          </Suspense>
        </RouteComponentBoundary>
      )
    }

    return fallbackElement
  }

  // If we have a feature, render a placeholder (can be enhanced later)
  if (routeContext.feature && routeContext.category && activePlatform) {
    const allowedCategories = getCategories(activePlatform.id, currentActor)
    const activeCategory = allowedCategories.find((category) => category.id === routeContext.category?.id)
    if (!activeCategory) {
      return <Navigate to={fallbackPath} replace />
    }

    const allowedFeatures = getFeatures(activePlatform.id, activeCategory.id, currentActor)
    const activeFeature = allowedFeatures.find((feature) => feature.route === routeContext.feature?.route)
    if (!activeFeature) {
      return <Navigate to={activeCategory.homeRoute} replace />
    }

    if (activeFeature.route === '/governance/policy/simulator') {
      return <PolicySimulator />
    }

    const fallbackElement = (
      <FeaturePageTemplate
        platform={activePlatform}
        category={activeCategory}
        feature={activeFeature}
      />
    )

    if (LazyComponent) {
      return (
        <RouteComponentBoundary fallback={fallbackElement}>
          <Suspense fallback={<div className="p-6 text-sm text-[color:var(--osd-muted)]">Loading…</div>}>
            <LazyComponent />
          </Suspense>
        </RouteComponentBoundary>
      )
    }

    return fallbackElement
  }

  if (routeContext.platform && fallbackPath && location.pathname !== fallbackPath) {
    return <Navigate to={fallbackPath} replace />
  }

  // No matching route found - show 404
  return (
    <div className="flex items-center justify-center min-h-[400px]">
      <div className="text-center">
        <h1 className="text-2xl font-bold text-[color:var(--osd-text)] mb-2">404</h1>
        <p className="text-[color:var(--osd-muted)]">Page not found: {location.pathname}</p>
      </div>
    </div>
  )
}
