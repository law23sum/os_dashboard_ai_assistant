import { useMemo } from 'react'
import { useIARouteContext } from './iaContext'

export type NavigationBreadcrumb = {
  label: string
  path?: string
}

export type NavigationFeature = {
  title: string
}

export type NavigationState = {
  activeNav: {
    feature?: NavigationFeature
    breadcrumbs: NavigationBreadcrumb[]
  }
}

export function useNavigation(): NavigationState {
  const routeContext = useIARouteContext()

  const breadcrumbs = useMemo<NavigationBreadcrumb[]>(() => {
    const items: NavigationBreadcrumb[] = []
    if (routeContext.platform) {
      items.push({ label: routeContext.platform.label, path: routeContext.platform.path })
    }
    if (routeContext.category) {
      items.push({ label: routeContext.category.label, path: routeContext.category.homeRoute })
    }
    if (routeContext.feature) {
      items.push({ label: routeContext.feature.label, path: routeContext.feature.route })
    }
    return items
  }, [routeContext.platform, routeContext.category, routeContext.feature])

  const feature = routeContext.feature ? { title: routeContext.feature.label } : undefined

  return {
    activeNav: {
      feature,
      breadcrumbs,
    },
  }
}
