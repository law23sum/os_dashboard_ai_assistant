export * from '../data/navigationStructure'

import { navigationStructure } from '../data/navigationStructure'

export type NavigationBreadcrumbItem = {
  label: string
  path?: string
}

const normalizePath = (path: string): string => {
  if (!path) return '/'
  const normalized = path.replace(/\/+$/, '')
  return normalized || '/'
}

const pathMatches = (current: string, candidate: string): boolean => {
  const normalizedCandidate = normalizePath(candidate)
  return current === normalizedCandidate || current.startsWith(`${normalizedCandidate}/`)
}

export function getPlatformBreadcrumb(path: string): NavigationBreadcrumbItem[] {
  const current = normalizePath(path)
  for (const category of navigationStructure) {
    for (const platform of category.platforms) {
      for (const feature of platform.features) {
        if (pathMatches(current, feature.path)) {
          return [
            { label: category.label },
            { label: platform.label, path: platform.path },
            { label: feature.label },
          ]
        }
      }
      if (pathMatches(current, platform.path)) {
        return [
          { label: category.label },
          { label: platform.label },
        ]
      }
    }
  }
  return []
}
