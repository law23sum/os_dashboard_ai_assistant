/**
 * IA Manifest wrapper.
 * Keep this file lightweight: re-export the JSON-derived manifest and helpers.
 */

import {
  iaManifest as derivedManifest,
  type IAPlatform,
  type IACategory,
  type IAFeature,
  type ActorScope,
  getPlatforms,
  getCategories,
  getFeatures,
  findRouteContext,
} from './iaManifest.from_json'

export const iaManifest = derivedManifest

export type Platform = IAPlatform
export type Category = IACategory
export type NavItem = IAFeature
export type { ActorScope }

export { getPlatforms, getCategories, getFeatures, findRouteContext }
