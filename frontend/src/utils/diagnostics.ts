/**
 * Diagnostic utility to check app initialization
 * Run this in browser console to diagnose issues
 */

export function runDiagnostics() {
  const results: Record<string, any> = {}

  // Check if React is loaded
  try {
    // @ts-ignore
    results.react = typeof React !== 'undefined' ? 'loaded' : 'missing'
  } catch {
    results.react = 'error'
  }

  // Check if root element exists
  results.rootElement = document.getElementById('root') ? 'exists' : 'missing'

  // Check localStorage
  try {
    localStorage.setItem('__test__', 'test')
    localStorage.removeItem('__test__')
    results.localStorage = 'working'
  } catch {
    results.localStorage = 'blocked'
  }

  // Check if modules are loading
  try {
    // @ts-ignore
    results.vite = typeof import.meta !== 'undefined' && import.meta.env ? 'loaded' : 'missing'
  } catch {
    results.vite = 'error'
  }

  // Check for common errors
  const errors: string[] = []
  if (results.rootElement === 'missing') {
    errors.push('Root element #root not found in DOM')
  }
  if (results.localStorage === 'blocked') {
    errors.push('LocalStorage is blocked')
  }

  results.errors = errors
  results.timestamp = new Date().toISOString()

  console.log('=== App Diagnostics ===')
  console.table(results)
  if (errors.length > 0) {
    console.error('Errors found:', errors)
  }

  return results
}

// Auto-run on import
if (typeof window !== 'undefined') {
  // @ts-ignore
  window.runAppDiagnostics = runDiagnostics
  console.log('Diagnostics available: run runAppDiagnostics() in console')
}



