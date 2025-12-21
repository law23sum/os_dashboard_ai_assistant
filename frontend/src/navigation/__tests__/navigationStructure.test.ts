/**
 * Navigation Structure Tests
 * Tests for Platform → Category → Feature relationships
 */

import { describe, it, expect } from '@jest/globals'
import navConfig from '../../public/gui_nav.latest.json'

describe('Navigation Structure', () => {
  it('should have correct Platform → Category relationship (one-to-many)', () => {
    const platforms = new Map()
    
    for (const [edition, editionData] of Object.entries(navConfig)) {
      for (const [platform, platformData] of Object.entries(editionData)) {
        if (!platforms.has(platform)) {
          platforms.set(platform, [])
        }
        const categories = Object.keys(platformData)
        platforms.get(platform).push(...categories)
      }
    }
    
    // Each platform should have at least one category
    for (const [platform, categories] of platforms.entries()) {
      expect(categories.length).toBeGreaterThan(0)
    }
  })

  it('should have correct Category → Feature relationship (one-to-many)', () => {
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

  it('should have correct Category → Platform relationship (one-to-one within edition)', () => {
    const categoryPlatforms = new Map()
    
    for (const [edition, editionData] of Object.entries(navConfig)) {
      for (const [platform, platformData] of Object.entries(editionData)) {
        for (const category of Object.keys(platformData)) {
          const key = `${edition}:${category}`
          if (!categoryPlatforms.has(key)) {
            categoryPlatforms.set(key, platform)
          } else {
            // Within same edition, category should belong to one platform
            expect(categoryPlatforms.get(key)).toBe(platform)
          }
        }
      }
    }
  })

  it('should have correct Feature → Category relationship (one-to-one)', () => {
    const featureCategories = new Map()
    
    for (const [edition, editionData] of Object.entries(navConfig)) {
      for (const [platform, platformData] of Object.entries(editionData)) {
        for (const [category, features] of Object.entries(platformData)) {
          if (Array.isArray(features)) {
            for (const feature of features) {
              if (feature.path) {
                const key = `${edition}:${feature.path}`
                if (!featureCategories.has(key)) {
                  featureCategories.set(key, { platform, category })
                } else {
                  // Feature should belong to one category
                  const existing = featureCategories.get(key)
                  expect(existing.category).toBe(category)
                }
              }
            }
          }
        }
      }
    }
  })

  it('should not have duplicate routes', () => {
    const routes = new Set()
    const duplicates = []
    
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
    
    expect(duplicates.length).toBe(0)
  })
})
