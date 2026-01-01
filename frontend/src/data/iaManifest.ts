/**
 * IA Manifest runtime adapter.
 * Sources navigation from gui_nav.latest.json and derives platform/category/feature roles.
 */

import rawNav from './gui_nav.latest.json'
import { legacyRedirects as legacyRedirectsFallback } from './iaManifest.from_json'

export type ActorScope = 'personal' | 'enterprise' | 'both'

export interface IAFeature {
  id: string
  label: string
  route: string
  componentPath: string
  bestCommit: 'stable' | 'increments' | 'backup'
  actorScope: ActorScope
  order: number
  isNew?: boolean
}

export interface IACategory {
  id: string
  label: string
  homeRoute: string
  homeComponentPath: string
  homeBestCommit: 'stable' | 'increments' | 'backup'
  features: IAFeature[]
  actorScope: ActorScope
  order: number
}

export interface IAPlatform {
  id: string
  label: string
  path: string
  categories: IACategory[]
  actorScope: ActorScope
  order: number
}

type RawFeature = {
  title?: string
  path?: string
  new?: boolean
}

type RawNav = Record<string, Record<string, Record<string, RawFeature[]>>>

const navConfig = rawNav as RawNav

const slugify = (value: string): string =>
  value
    .toLowerCase()
    .replace(/&/g, 'and')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')

const normalizePath = (value?: string): string => {
  if (!value) return '/'
  const trimmed = value.trim()
  if (!trimmed || trimmed === '/') return '/'
  const normalized = trimmed.startsWith('/') ? trimmed : `/${trimmed}`
  return normalized.replace(/\/+$/, '') || '/'
}

const mergeActorScope = (current: ActorScope, incoming: ActorScope): ActorScope => {
  if (current === incoming) return current
  if (current === 'both' || incoming === 'both') return 'both'
  return 'both'
}

const scoreCategoryHome = (feature: IAFeature, categoryLabel: string): number => {
  const labelLower = categoryLabel.toLowerCase()
  const titleLower = feature.label.toLowerCase()
  const segments = feature.route === '/' ? 0 : feature.route.split('/').filter(Boolean).length
  const isCoreRoot =
    feature.route === '/' && (labelLower.includes('flight deck') || labelLower.includes('mission control'))

  let score = -segments * 10
  if (titleLower === labelLower) score += 12
  if (titleLower.includes(labelLower)) score += 6
  if (titleLower.includes('overview')) score += 6
  if (titleLower.includes('dashboard') || titleLower.includes('home')) score += 5
  if (feature.route.endsWith(`/${slugify(categoryLabel)}`)) score += 3
  if (feature.route === '/' && !isCoreRoot) score -= 50
  return score
}

const buildManifest = (): IAPlatform[] => {
  const platforms = new Map<string, IAPlatform>()
  let platformOrder = 1

  for (const [editionName, editionPlatforms] of Object.entries(navConfig)) {
    const editionScope: ActorScope = editionName.toLowerCase().includes('enterprise')
      ? 'enterprise'
      : 'personal'

    for (const [platformName, categories] of Object.entries(editionPlatforms)) {
      const platformId = slugify(platformName)
      let platform = platforms.get(platformId)
      if (!platform) {
        platform = {
          id: platformId,
          label: platformName,
          path: `/${platformId}`,
          categories: [],
          actorScope: editionScope,
          order: platformOrder++,
        }
        platforms.set(platformId, platform)
      } else {
        platform.actorScope = mergeActorScope(platform.actorScope, editionScope)
      }

      for (const [categoryName, featureList] of Object.entries(categories)) {
        const categoryId = slugify(categoryName)
        let category = platform.categories.find((item) => item.id === categoryId)
        if (!category) {
          category = {
            id: categoryId,
            label: categoryName,
            homeRoute: '/',
            homeComponentPath: 'frontend/src/components/templates/CategoryHomeTemplate.tsx',
            homeBestCommit: 'stable',
            features: [],
            actorScope: editionScope,
            order: platform.categories.length + 1,
          }
          platform.categories.push(category)
        } else {
          category.actorScope = mergeActorScope(category.actorScope, editionScope)
        }

        const parsedFeatures: IAFeature[] = (Array.isArray(featureList) ? featureList : [])
          .filter((item) => item && typeof item === 'object')
          .map((item, index) => ({
            id: slugify(item.title || `feature-${index + 1}`) || `feature-${index + 1}`,
            label: item.title || `Feature ${index + 1}`,
            route: normalizePath(item.path),
            componentPath: 'frontend/src/components/templates/FeaturePageTemplate.tsx',
            bestCommit: 'stable',
            actorScope: editionScope,
            order: index + 1,
            isNew: Boolean(item.new),
          }))

        if (parsedFeatures.length > 0) {
          let bestIndex = 0
          let bestScore = Number.NEGATIVE_INFINITY
          parsedFeatures.forEach((feature, index) => {
            const score = scoreCategoryHome(feature, categoryName)
            if (score > bestScore) {
              bestScore = score
              bestIndex = index
            }
          })

          const homeCandidate = parsedFeatures[bestIndex]
          if (!category.homeRoute || category.homeRoute === '/') {
            category.homeRoute = homeCandidate.route
          }

          const existingRoutes = new Set(category.features.map((feature) => feature.route))
          let orderOffset = category.features.length
          parsedFeatures.forEach((feature, index) => {
            if (index === bestIndex) return
            if (existingRoutes.has(feature.route)) return
            orderOffset += 1
            category.features.push({
              ...feature,
              order: orderOffset,
              actorScope: mergeActorScope(feature.actorScope, category!.actorScope),
            })
          })
        }
      }
    }
  }

  return Array.from(platforms.values())
}

export const iaManifest = buildManifest()

export type Platform = IAPlatform
export type Category = IACategory
export type NavItem = IAFeature

export const legacyRedirects = legacyRedirectsFallback

export const isScopeAllowed = (itemScope: ActorScope | undefined, actorScope: ActorScope) => {
  if (!itemScope) return true
  if (itemScope === 'both' || itemScope === actorScope) return true
  if (actorScope === 'enterprise' && itemScope === 'personal') return true
  return false
}

export function getPlatforms(actorScope: ActorScope): IAPlatform[] {
  return iaManifest.filter((platform) => isScopeAllowed(platform.actorScope, actorScope))
}

export function getCategories(platformId: string, actorScope: ActorScope): IACategory[] {
  const platform = iaManifest.find((item) => item.id === platformId)
  if (!platform) return []
  if (!isScopeAllowed(platform.actorScope, actorScope)) return []
  return platform.categories.filter((category) => isScopeAllowed(category.actorScope, actorScope))
}

export function getFeatures(platformId: string, categoryId: string, actorScope: ActorScope): IAFeature[] {
  const platform = iaManifest.find((item) => item.id === platformId)
  if (!platform) return []
  const category = platform.categories.find((item) => item.id === categoryId)
  if (!category) return []
  if (!isScopeAllowed(category.actorScope, actorScope)) return []
  return category.features.filter((feature) => isScopeAllowed(feature.actorScope, actorScope))
}

export function findRouteContext(route: string): {
  platform?: IAPlatform
  category?: IACategory
  feature?: IAFeature
  isCategoryHome: boolean
} {
  const normalized = route === '/' ? '/' : route.replace(/\/+$/, '')

  for (const platform of iaManifest) {
    if (platform.path === normalized) {
      return { platform, isCategoryHome: false }
    }
    for (const category of platform.categories) {
      if (category.homeRoute === normalized) {
        return { platform, category, isCategoryHome: true }
      }
      for (const feature of category.features) {
        if (normalized === feature.route || normalized.startsWith(feature.route + '/')) {
          return { platform, category, feature, isCategoryHome: false }
        }
      }
    }
  }

  return { isCategoryHome: false }
}
