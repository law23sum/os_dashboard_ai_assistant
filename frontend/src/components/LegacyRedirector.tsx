import { Navigate, useLocation } from 'react-router-dom'
import { buildLegacyRedirectMap, getPlatforms, canonicalCategoryPath } from '../data/iaCanonical'
import { useIANavigation } from '../navigation/iaContext'

let LEGACY_REDIRECTS: Map<string, string>
try {
  LEGACY_REDIRECTS = buildLegacyRedirectMap()
} catch (error) {
  console.error('Failed to build legacy redirect map:', error)
  LEGACY_REDIRECTS = new Map()
}

function isCanonicalShape(pathname: string) {
  const parts = pathname.replace(/\/+$/, '').split('/').filter(Boolean)
  return parts.length === 2 || parts.length === 3
}

export function LegacyRedirector() {
  const location = useLocation()
  const { actorScope, routeContext } = useIANavigation()

  const normalizedPath = location.pathname === '/' ? '/' : location.pathname.replace(/\/+$/, '')

  // 1) Legacy path redirect
  const legacyTarget = LEGACY_REDIRECTS.get(normalizedPath)
  if (legacyTarget && legacyTarget !== normalizedPath) {
    return (
      <Navigate
        to={{ pathname: legacyTarget, search: location.search, hash: location.hash }}
        replace
      />
    )
  }

  // 2) Actor gating: if user lands on a canonical-shaped route that is not allowed,
  // routeContext will have no platform/category/feature (it gets filtered in iaContext).
  if (isCanonicalShape(normalizedPath) && !routeContext.platform) {
    try {
      const allowedPlatforms = getPlatforms(actorScope)
      const fallbackPlatform = allowedPlatforms?.[0]
      const fallbackCategory = fallbackPlatform?.categories?.[0]
      if (fallbackPlatform && fallbackCategory) {
        const fallback = canonicalCategoryPath(fallbackPlatform.id, fallbackCategory.id)
        return <Navigate to={fallback} replace />
      }
    } catch (error) {
      console.error('Error in actor gating redirect:', error)
    }
  }

  return null
}


