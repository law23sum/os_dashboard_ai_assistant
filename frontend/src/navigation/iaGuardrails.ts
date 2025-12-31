/**
 * IA Guardrails - Runtime checks to prevent IA violations
 * 
 * These functions can be called at runtime to verify IA compliance
 * and prevent navigation structure violations.
 */

import { iaManifest } from '../data/iaManifest'
import type { Platform, Category, NavItem } from '../data/iaManifest'

export interface IAViolation {
  type: 'duplicate_route' | 'feature_in_dropdown' | 'missing_category_home' | 'invalid_structure'
  message: string
  route?: string
  platform?: string
  category?: string
  feature?: string
}

/**
 * Verify IA compliance and return violations
 */
export function verifyIACompliance(): IAViolation[] {
  const violations: IAViolation[] = []
  const categoryHomeRoutes = new Set<string>()
  const featureRoutes = new Set<string>()
  
  const allPlatforms = iaManifest
  
  for (const platform of allPlatforms) {
    for (const category of platform.categories) {
      // Check category home
      if (categoryHomeRoutes.has(category.homeRoute)) {
        violations.push({
          type: 'duplicate_route',
          message: `Duplicate category home route: ${category.homeRoute}`,
          route: category.homeRoute,
          platform: platform.id,
          category: category.id
        })
      }
      categoryHomeRoutes.add(category.homeRoute)
      
      // Check features
      for (const feature of category.features) {
        if (featureRoutes.has(feature.route)) {
          violations.push({
            type: 'duplicate_route',
            message: `Duplicate feature route: ${feature.route}`,
            route: feature.route,
            platform: platform.id,
            category: category.id,
            feature: feature.id
          })
        }
        featureRoutes.add(feature.route)
        
        // Check if feature route matches category home (violation)
        if (feature.route === category.homeRoute && category.features.indexOf(feature) > 0) {
          violations.push({
            type: 'duplicate_route',
            message: `Feature route matches category home: ${feature.route}`,
            route: feature.route,
            platform: platform.id,
            category: category.id,
            feature: feature.id
          })
        }
      }
    }
  }
  
  // Check for routes in both sets (violation)
  const duplicates = Array.from(categoryHomeRoutes).filter(route => featureRoutes.has(route))
  for (const route of duplicates) {
    violations.push({
      type: 'duplicate_route',
      message: `Route appears in both dropdown and sidebar: ${route}`,
      route
    })
  }
  
  return violations
}

/**
 * Assert IA compliance - throws if violations found
 */
export function assertIACompliance(): void {
  const violations = verifyIACompliance()
  if (violations.length > 0) {
    const messages = violations.map(v => v.message).join('\n')
    throw new Error(`IA Compliance Violations:\n${messages}`)
  }
}

/**
 * Check if a route is a category home
 */
export function isCategoryHome(route: string): boolean {
  const allPlatforms = iaManifest
  for (const platform of allPlatforms) {
    for (const category of platform.categories) {
      if (category.homeRoute === route) {
        return true
      }
    }
  }
  return false
}

/**
 * Check if a route is a feature
 */
export function isFeature(route: string): boolean {
  const allPlatforms = iaManifest
  for (const platform of allPlatforms) {
    for (const category of platform.categories) {
      for (const feature of category.features) {
        if (feature.route === route) {
          return true
        }
      }
    }
  }
  return false
}

/**
 * Get platform for a route
 */
export function getPlatformForRoute(route: string): Platform | null {
  const allPlatforms = iaManifest
  for (const platform of allPlatforms) {
    for (const category of platform.categories) {
      if (category.homeRoute === route) {
        return platform
      }
      for (const feature of category.features) {
        if (feature.route === route) {
          return platform
        }
      }
    }
  }
  return null
}

/**
 * Validate that navigation component structure follows IA rules
 */
export function validateNavigationStructure(): {
  valid: boolean
  violations: IAViolation[]
} {
  const violations = verifyIACompliance()
  
  return {
    valid: violations.length === 0,
    violations
  }
}

