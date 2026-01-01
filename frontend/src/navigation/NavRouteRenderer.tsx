import { Navigate, useLocation } from 'react-router-dom'
import { useIARouteContext } from './iaContext'
import { CategoryHomeTemplate } from '../components/templates/CategoryHomeTemplate'

export default function NavRouteRenderer() {
  const location = useLocation()
  const routeContext = useIARouteContext()

  // If we have a category home, render the category home template
  if (routeContext.isCategoryHome && routeContext.category) {
    const features = routeContext.category.features ?? []
    return (
      <CategoryHomeTemplate
        title={routeContext.category.label}
        description={`Navigate to features in ${routeContext.category.label}.`}
        features={features.map((feature) => ({
          title: feature.label,
          path: feature.route,
        }))}
      />
    )
  }

  // If we have a feature, render a placeholder (can be enhanced later)
  if (routeContext.feature && routeContext.category) {
    const features = routeContext.category.features ?? []
    return (
      <CategoryHomeTemplate
        title={routeContext.feature.label}
        description={`Feature: ${routeContext.feature.label}`}
        features={features.map((feature) => ({
          title: feature.label,
          path: feature.route,
        }))}
      />
    )
  }

  // If we have a platform but no category/feature, redirect to first category or show 404
  if (routeContext.platform && routeContext.platform.categories.length > 0) {
    const firstCategory = routeContext.platform.categories[0]
    if (firstCategory?.homeRoute) {
      return <Navigate to={firstCategory.homeRoute} replace />
    }
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

