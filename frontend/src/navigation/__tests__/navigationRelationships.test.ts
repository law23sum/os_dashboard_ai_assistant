/**
 * Navigation Relationships Tests
 * Tests for Platform → Category → Feature relationships
 * 
 * Relationships:
 * - Platform → Category: ONE-TO-MANY (one platform has many categories)
 * - Category → Feature: ONE-TO-MANY (one category has many features)
 * - Category → Platform: ONE-TO-ONE (within same edition)
 * - Feature → Category: ONE-TO-ONE (each feature belongs to exactly one category)
 */

import { describe, it, expect } from 'vitest'
import navConfig from '../../../public/gui_nav.latest.json'

describe('Navigation Relationships', () => {
  describe('Platform → Category (ONE-TO-MANY)', () => {
    it('should have each platform with multiple categories', () => {
      const platformCategoryCounts = new Map<string, number>()
      
      for (const [edition, editionData] of Object.entries(navConfig)) {
        for (const [platform, platformData] of Object.entries(editionData)) {
          const key = `${edition}:${platform}`
          const categoryCount = Object.keys(platformData).length
          
          if (!platformCategoryCounts.has(key)) {
            platformCategoryCounts.set(key, categoryCount)
          } else {
            platformCategoryCounts.set(key, platformCategoryCounts.get(key)! + categoryCount)
          }
        }
      }
      
      // Each platform should have at least one category
      for (const [platform, count] of platformCategoryCounts.entries()) {
        expect(count).toBeGreaterThan(0)
      }
    })
  })

  describe('Category → Feature (ONE-TO-MANY)', () => {
    it('should have each category with multiple features', () => {
      for (const [edition, editionData] of Object.entries(navConfig)) {
        for (const [platform, platformData] of Object.entries(editionData)) {
          for (const [category, features] of Object.entries(platformData)) {
            if (Array.isArray(features)) {
              // Each category should have at least one feature
              expect(features.length).toBeGreaterThan(0)
            }
          }
        }
      }
    })
  })

  describe('Category → Platform (ONE-TO-ONE within edition)', () => {
    it('should have each category belong to exactly one platform within same edition', () => {
      const categoryPlatforms = new Map<string, string>()
      
      for (const [edition, editionData] of Object.entries(navConfig)) {
        for (const [platform, platformData] of Object.entries(editionData)) {
          for (const category of Object.keys(platformData)) {
            const key = `${edition}:${category}`
            
            if (!categoryPlatforms.has(key)) {
              categoryPlatforms.set(key, platform)
            } else {
              // Within same edition, category should belong to one platform
              const existingPlatform = categoryPlatforms.get(key)
              // Allow cross-edition (Personal vs Business/Team vs Enterprise) but not within same edition
              if (existingPlatform !== platform) {
                // This is valid if it's cross-edition, but we check the key includes edition
                // So if key matches, it's same edition - should be same platform
                expect(existingPlatform).toBe(platform)
              }
            }
          }
        }
      }
    })
  })

  describe('Feature → Category (ONE-TO-ONE)', () => {
    it('should have each feature belong to exactly one category', () => {
      const featureCategories = new Map<string, { platform: string; category: string; edition: string }>()
      const duplicates: string[] = []
      
      for (const [edition, editionData] of Object.entries(navConfig)) {
        for (const [platform, platformData] of Object.entries(editionData)) {
          for (const [category, features] of Object.entries(platformData)) {
            if (Array.isArray(features)) {
              for (const feature of features) {
                if (feature.path) {
                  const key = feature.path
                  
                  if (!featureCategories.has(key)) {
                    featureCategories.set(key, { platform, category, edition })
                  } else {
                    // Feature should belong to one category
                    const existing = featureCategories.get(key)!
                    if (existing.category !== category || existing.platform !== platform) {
                      duplicates.push(key)
                    }
                  }
                }
              }
            }
          }
        }
      }
      
      expect(duplicates.length).toBe(0)
    })
  })

  describe('IA Compliance', () => {
    it('should not have features in platform dropdowns', () => {
      // This is enforced by the navigation parser
      // Platform dropdowns should only show categories
      for (const [edition, editionData] of Object.entries(navConfig)) {
        for (const [platform, platformData] of Object.entries(editionData)) {
          // Platform data should be an object with categories as keys
          expect(typeof platformData).toBe('object')
          expect(Array.isArray(platformData)).toBe(false)
          
          // Each category should have an array of features
          for (const [category, features] of Object.entries(platformData)) {
            expect(Array.isArray(features)).toBe(true)
          }
        }
      }
    })

    it('should not have duplicate routes', () => {
      const routes = new Set<string>()
      const duplicates: string[] = []
      
      for (const [edition, editionData] of Object.entries(navConfig)) {
        for (const [platform, platformData] of Object.entries(editionData)) {
          for (const [category, features] of Object.entries(platformData)) {
            if (Array.isArray(features)) {
              for (const feature of features) {
                if (feature.path) {
                  if (routes.has(feature.path)) {
                    duplicates.push(feature.path)
                  }
                  routes.add(feature.path)
                }
              }
            }
          }
        }
      }
      
      if (duplicates.length > 0) {
        console.warn('Duplicate routes found:', duplicates.slice(0, 10))
      }
      expect(duplicates.length).toBe(0)
    })
  })
})

