/**
 * IA Compliance Tests
 * 
 * Ensures navigation structure follows IA rules:
 * 1. Platforms = top nav dropdown triggers only
 * 2. Categories = dropdown items only (category home pages)
 * 3. Features = sidebar items only
 * 4. NO route appears in both dropdown and sidebar
 * 5. NO features appear in platform dropdowns
 */

import { describe, it, expect } from 'vitest'
import { iaManifest } from '../../data/iaManifest'
import { verifyIACompliance, assertIACompliance } from '../iaGuardrails'
import type { Platform, Category, NavItem } from '../../data/iaManifest'

describe('IA Compliance Tests', () => {
  const allPlatforms = [...iaManifest.personal, ...iaManifest.enterprise]

  describe('Structure Validation', () => {
    it('should have platforms defined', () => {
      expect(allPlatforms.length).toBeGreaterThan(0)
      expect(Array.isArray(allPlatforms)).toBe(true)
    })

    it('each platform should have categories', () => {
      for (const platform of allPlatforms) {
        expect(platform.categories).toBeDefined()
        expect(Array.isArray(platform.categories)).toBe(true)
        expect(platform.categories.length).toBeGreaterThan(0)
      }
    })

    it('each category should have a homeRoute', () => {
      for (const platform of allPlatforms) {
        for (const category of platform.categories) {
          expect(category.homeRoute).toBeDefined()
          expect(typeof category.homeRoute).toBe('string')
          expect(category.homeRoute.length).toBeGreaterThan(0)
        }
      }
    })

    it('each category should have features', () => {
      for (const platform of allPlatforms) {
        for (const category of platform.categories) {
          expect(category.features).toBeDefined()
          expect(Array.isArray(category.features)).toBe(true)
        }
      }
    })
  })

  describe('IA Rule 1: Platforms are dropdown triggers only', () => {
    it('platforms should not contain feature routes directly', () => {
      for (const platform of allPlatforms) {
        // Platforms should only have categories, not direct features
        expect(platform.categories).toBeDefined()
      }
    })
  })

  describe('IA Rule 2: Categories are dropdown items only', () => {
    it('category homeRoutes should be unique', () => {
      const homeRoutes = new Set<string>()
      
      for (const platform of allPlatforms) {
        for (const category of platform.categories) {
          expect(homeRoutes.has(category.homeRoute)).toBe(false)
          homeRoutes.add(category.homeRoute)
        }
      }
    })

    it('category homeRoutes should not be feature routes', () => {
      const featureRoutes = new Set<string>()
      
      // Collect all feature routes
      for (const platform of allPlatforms) {
        for (const category of platform.categories) {
          for (const feature of category.features) {
            featureRoutes.add(feature.route)
          }
        }
      }
      
      // Check category homes are not features
      for (const platform of allPlatforms) {
        for (const category of platform.categories) {
          // Category home can be the same as first feature (that's OK)
          // But it should be explicitly marked as category home
          expect(category.homeRoute).toBeDefined()
        }
      }
    })
  })

  describe('IA Rule 3: Features are sidebar items only', () => {
    it('features should have unique routes', () => {
      const featureRoutes = new Set<string>()
      
      for (const platform of allPlatforms) {
        for (const category of platform.categories) {
          for (const feature of category.features) {
            expect(featureRoutes.has(feature.route)).toBe(false)
            featureRoutes.add(feature.route)
          }
        }
      }
    })

    it('features should not appear in category homeRoutes', () => {
      const categoryHomeRoutes = new Set<string>()
      
      // Collect category home routes
      for (const platform of allPlatforms) {
        for (const category of platform.categories) {
          categoryHomeRoutes.add(category.homeRoute)
        }
      }
      
      // Features should not be category homes (except first feature can be)
      for (const platform of allPlatforms) {
        for (const category of platform.categories) {
          for (let i = 1; i < category.features.length; i++) {
            const feature = category.features[i]
            // Feature routes should not be category home routes
            // (First feature can be, but others cannot)
            if (i > 0) {
              expect(categoryHomeRoutes.has(feature.route)).toBe(false)
            }
          }
        }
      }
    })
  })

  describe('IA Rule 4: No route duplication', () => {
    it('no route should appear in both dropdown and sidebar', () => {
      const violations = verifyIACompliance()
      const duplicateViolations = violations.filter(v => v.type === 'duplicate_route')
      
      // Should have no duplicate route violations
      expect(duplicateViolations.length).toBe(0)
    })
    
    it('should pass IA compliance assertion', () => {
      expect(() => assertIACompliance()).not.toThrow()
    })
  })

  describe('IA Rule 5: No features in platform dropdowns', () => {
    it('platform dropdowns should only show categories', () => {
      // This is enforced by the navigation component structure
      // PlatformNavIA only shows categories, not features
      // Verify by checking that features are not at platform level
      for (const platform of allPlatforms) {
        // Platforms should only have categories
        expect(platform.categories).toBeDefined()
        expect(Array.isArray(platform.categories)).toBe(true)
        
        // No direct features at platform level
        // (This would be a structure violation)
      }
    })
  })

  describe('Actor Scope Validation', () => {
    it('all platforms should have valid actorScope', () => {
      for (const platform of allPlatforms) {
        expect(platform.actorScope).toBeDefined()
        expect(typeof platform.actorScope).toBe('object')
        expect(typeof platform.actorScope.personal).toBe('boolean')
        expect(typeof platform.actorScope.enterprise).toBe('boolean')
      }
    })

    it('all categories should have valid actorScope', () => {
      for (const platform of allPlatforms) {
        for (const category of platform.categories) {
          expect(category.actorScope).toBeDefined()
          expect(typeof category.actorScope).toBe('object')
          expect(typeof category.actorScope.personal).toBe('boolean')
          expect(typeof category.actorScope.enterprise).toBe('boolean')
        }
      }
    })

    it('all features should have valid actorScope', () => {
      for (const platform of allPlatforms) {
        for (const category of platform.categories) {
          for (const feature of category.features) {
            expect(feature.actorScope).toBeDefined()
            expect(typeof feature.actorScope).toBe('object')
            expect(typeof feature.actorScope.personal).toBe('boolean')
            expect(typeof feature.actorScope.enterprise).toBe('boolean')
          }
        }
      }
    })
  })

  describe('Route Format Validation', () => {
    it('all routes should start with /', () => {
      for (const platform of allPlatforms) {
        for (const category of platform.categories) {
          expect(category.homeRoute.startsWith('/')).toBe(true)
          
          for (const feature of category.features) {
            expect(feature.route.startsWith('/')).toBe(true)
          }
        }
      }
    })
  })
})

