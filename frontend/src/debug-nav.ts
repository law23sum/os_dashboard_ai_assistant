/**
 * Debug script to check navigation state
 * Run this in browser console to diagnose navigation issues
 */

export function debugNavigation() {
  console.log('=== Navigation Debug ===')
  
  // Check if manifest exists
  import('./data/iaManifest').then((module) => {
    console.log('✅ Manifest loaded')
    console.log('Platforms:', module.iaManifest.length)
    console.log('First platform:', module.iaManifest[0])
    
    // Test getPlatforms
    const personalPlatforms = module.getPlatforms('personal')
    const enterprisePlatforms = module.getPlatforms('enterprise')
    console.log('Personal platforms:', personalPlatforms.length)
    console.log('Enterprise platforms:', enterprisePlatforms.length)
    
    // Check route context
    const context = module.findRouteContext(window.location.pathname)
    console.log('Current route context:', context)
  }).catch((err) => {
    console.error('❌ Failed to load manifest:', err)
  })
}

// Auto-run if in browser
if (typeof window !== 'undefined') {
  (window as any).debugNavigation = debugNavigation
  console.log('Run debugNavigation() in console to check navigation state')
}

