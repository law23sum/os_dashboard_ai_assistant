/**
 * Canonical IA Manifest (computed)
 *
 * The repo historically used "legacy" routes like `/projects`, `/ai/os`, etc.
 * The IA invariants for this restoration require:
 * - Category home: /{platform}/{category}
 * - Feature:       /{platform}/{category}/{feature}
 *
 * We keep legacy paths for redirects/backwards-compat, but the navigation UI
 * and route generation must only use canonical paths.
 */

import {
  iaManifest as legacyManifest,
  type IAPlatform,
  type IACategory,
  type IAFeature,
} from './iaManifest'

// Log initialization
console.log('[iaCanonical] Starting initialization...')
console.log('[iaCanonical] legacyManifest type:', typeof legacyManifest)
console.log('[iaCanonical] legacyManifest is array:', Array.isArray(legacyManifest))
console.log('[iaCanonical] legacyManifest length:', legacyManifest?.length ?? 'undefined')

export type ActorScope = 'personal' | 'business' | 'enterprise'
type ItemScope = ActorScope | 'both' | undefined

const allowsActorScope = (itemScope: ItemScope, actorScope: ActorScope) => {
  if (!itemScope) return true
  if (itemScope === 'both' || itemScope === actorScope) return true
  if (actorScope === 'enterprise' && (itemScope === 'personal' || itemScope === 'business')) return true
  if (actorScope === 'business' && itemScope === 'personal') return true
  return false
}

export interface CanonicalIAFeature extends Omit<IAFeature, 'route'> {
  /** Canonical route: /{platform}/{category}/{feature} */
  route: string
  /** Legacy route (pre-IA): e.g. /projects */
  legacyRoute: string
  platformId: string
  categoryId: string
}

export interface CanonicalIACategory extends Omit<IACategory, 'homeRoute' | 'features'> {
  /** Canonical category home route: /{platform}/{category} */
  homeRoute: string
  /** Legacy category home route (pre-IA): often the first feature route */
  legacyHomeRoute: string
  platformId: string
  features: CanonicalIAFeature[]
}

export interface CanonicalIAPlatform extends Omit<IAPlatform, 'path' | 'categories'> {
  /** Canonical platform route prefix: /{platform} */
  path: string
  categories: CanonicalIACategory[]
}

export function canonicalPlatformPath(platformId: string) {
  return `/${platformId}`
}

export function canonicalCategoryPath(platformId: string, categoryId: string) {
  return `/${platformId}/${categoryId}`
}

export function canonicalFeaturePath(platformId: string, categoryId: string, featureId: string) {
  return `/${platformId}/${categoryId}/${featureId}`
}

let canonicalIaManifest: CanonicalIAPlatform[]
try {
  console.log('[iaCanonical] Checking legacyManifest...')
  if (!legacyManifest || !Array.isArray(legacyManifest) || legacyManifest.length === 0) {
    console.error('[iaCanonical] legacyManifest is empty or invalid:', legacyManifest)
    canonicalIaManifest = []
  } else {
    console.log('[iaCanonical] Processing', legacyManifest.length, 'platforms...')
    canonicalIaManifest = legacyManifest.map((platform) => {
    const platformId = platform.id
    return {
      ...platform,
      path: canonicalPlatformPath(platformId),
      categories: platform.categories.map((category) => {
        const categoryId = category.id
        const legacyHomeRoute = category.homeRoute
        return {
          ...category,
          platformId,
          homeRoute: canonicalCategoryPath(platformId, categoryId),
          legacyHomeRoute,
          features: category.features.map((feature) => ({
            ...feature,
            platformId,
            categoryId,
            route: canonicalFeaturePath(platformId, categoryId, feature.id),
            legacyRoute: feature.route,
          })),
        }
      }),
    }
    })
    console.log('[iaCanonical] Successfully initialized', canonicalIaManifest.length, 'platforms')
  }
} catch (error) {
  console.error('[iaCanonical] Failed to initialize canonicalIaManifest:', error)
  console.error('[iaCanonical] Error details:', error instanceof Error ? error.stack : error)
  canonicalIaManifest = []
}

console.log('[iaCanonical] Final canonicalIaManifest length:', canonicalIaManifest?.length ?? 'undefined')

export { canonicalIaManifest }

export function getPlatforms(actorScope: ActorScope): CanonicalIAPlatform[] {
  return canonicalIaManifest.filter((p) => allowsActorScope(p.actorScope, actorScope))
}

export function getCategories(platformId: string, actorScope: ActorScope): CanonicalIACategory[] {
  const platform = canonicalIaManifest.find((p) => p.id === platformId)
  if (!platform) return []
  if (!allowsActorScope(platform.actorScope, actorScope)) return []
  return platform.categories.filter((c) => allowsActorScope(c.actorScope, actorScope))
}

export function getFeatures(platformId: string, categoryId: string, actorScope: ActorScope): CanonicalIAFeature[] {
  const platform = canonicalIaManifest.find((p) => p.id === platformId)
  if (!platform) return []
  const category = platform.categories.find((c) => c.id === categoryId)
  if (!category) return []
  if (!allowsActorScope(category.actorScope, actorScope)) return []
  return category.features.filter((f) => allowsActorScope(f.actorScope, actorScope))
}

export function findCanonicalRouteContext(pathname: string): {
  platform?: CanonicalIAPlatform
  category?: CanonicalIACategory
  feature?: CanonicalIAFeature
  isCategoryHome: boolean
} {
  const normalized = pathname === '/' ? '/' : pathname.replace(/\/+$/, '')

  const parts = normalized.split('/').filter(Boolean)
  if (parts.length < 1) return { isCategoryHome: false }

  const [platformId, categoryId, featureId] = parts
  const platform = canonicalIaManifest.find((p) => p.id === platformId)
  if (!platform) return { isCategoryHome: false }

  if (!categoryId) {
    return { platform, isCategoryHome: false }
  }

  const category = platform.categories.find((c) => c.id === categoryId)
  if (!category) return { platform, isCategoryHome: false }

  if (!featureId) {
    return { platform, category, isCategoryHome: true }
  }

  const feature = category.features.find((f) => f.id === featureId)
  if (!feature) return { platform, category, isCategoryHome: false }

  return { platform, category, feature, isCategoryHome: false }
}

/**
 * Legacy → canonical redirects.
 *
 * IMPORTANT: These redirects are NOT used for nav generation.
 * They exist solely to preserve deep links that used legacy paths.
 */
export function buildLegacyRedirectMap(): Map<string, string> {
  const redirects = new Map<string, string>()

  // Root dashboard historically lived at `/` and `/dashboard`.
  // Canonically we land users on the first category home of Mission Control (or first platform).
  const firstPlatform = canonicalIaManifest[0]
  const firstCategory = firstPlatform?.categories?.[0]
  if (firstPlatform && firstCategory) {
    redirects.set('/', canonicalCategoryPath(firstPlatform.id, firstCategory.id))
    redirects.set('/dashboard', canonicalCategoryPath(firstPlatform.id, firstCategory.id))
  }

  for (const platform of canonicalIaManifest) {
    for (const category of platform.categories) {
      // Legacy category home route should land on the canonical category home
      if (category.legacyHomeRoute) {
        redirects.set(category.legacyHomeRoute, category.homeRoute)
      }
      // Feature legacy routes redirect to canonical feature routes
      for (const feature of category.features) {
        if (feature.legacyRoute) {
          redirects.set(feature.legacyRoute, feature.route)
        }
      }
    }
  }

  return redirects
}

