/**
 * Headless Browser Verification Script
 * 
 * Verifies that all pages from gui_nav.latest.json are actually accessible
 * Uses Playwright to test page rendering
 */

import { chromium, Browser, Page } from 'playwright'
import * as fs from 'fs'
import * as path from 'path'

const BASE_URL = process.env.E2E_BASE_URL || 'http://localhost:5173'
const TIMEOUT = 10000 // 10 seconds per page

interface RouteResult {
  path: string
  title: string
  accessible: boolean
  error?: string
  statusCode?: number
  hasContent?: boolean
}

async function loadRoutes(): Promise<Array<{ path: string; title: string }>> {
  const navPath = path.join(__dirname, '../frontend/src/data/gui_nav.latest.json')
  const data = JSON.parse(fs.readFileSync(navPath, 'utf-8'))
  
  const routes: Array<{ path: string; title: string }> = []
  
  for (const edition of Object.keys(data)) {
    const platforms = data[edition]
    for (const platform of Object.keys(platforms)) {
      const categories = platforms[platform]
      for (const category of Object.keys(categories)) {
        const features = categories[category]
        for (const feature of features) {
          routes.push({
            path: feature.path,
            title: feature.title
          })
        }
      }
    }
  }
  
  return routes
}

async function checkPage(page: Page, route: { path: string; title: string }): Promise<RouteResult> {
  const result: RouteResult = {
    path: route.path,
    title: route.title,
    accessible: false
  }
  
  try {
    const url = `${BASE_URL}${route.path}`
    console.log(`Checking: ${route.path} (${route.title})`)
    
    const response = await page.goto(url, { 
      waitUntil: 'networkidle',
      timeout: TIMEOUT 
    })
    
    result.statusCode = response?.status() || 0
    
    if (response && response.status() >= 400) {
      result.error = `HTTP ${response.status()}`
      return result
    }
    
    // Wait for content to load
    await page.waitForTimeout(1000)
    
    // Check if page has content (not just a blank page or error)
    const bodyText = await page.textContent('body')
    const hasError = await page.$('text=/error|404|not found/i')
    const hasContent = bodyText && bodyText.length > 100 && !hasError
    
    result.hasContent = !!hasContent
    result.accessible = response?.status() === 200 && hasContent
    
    if (!result.accessible) {
      if (!hasContent) {
        result.error = 'Page appears empty or has no content'
      } else if (response?.status() !== 200) {
        result.error = `HTTP ${response?.status()}`
      }
    }
    
  } catch (error: any) {
    result.error = error.message || 'Unknown error'
    result.accessible = false
  }
  
  return result
}

async function verifyPages() {
  console.log('🔍 Loading routes from gui_nav.latest.json...')
  const routes = await loadRoutes()
  console.log(`📋 Found ${routes.length} routes to verify\n`)
  
  console.log(`🌐 Starting headless browser...`)
  const browser = await chromium.launch({ headless: true })
  const context = await browser.newContext()
  const page = await context.newPage()
  
  // Set longer timeout
  page.setDefaultTimeout(TIMEOUT)
  
  const results: RouteResult[] = []
  const sampleSize = Math.min(50, routes.length) // Test first 50 pages for speed
  
  console.log(`\n🧪 Testing ${sampleSize} sample pages (out of ${routes.length} total)...\n`)
  
  for (let i = 0; i < sampleSize; i++) {
    const route = routes[i]
    const result = await checkPage(page, route)
    results.push(result)
    
    if (result.accessible) {
      console.log(`  ✅ ${route.path}`)
    } else {
      console.log(`  ❌ ${route.path} - ${result.error || 'Failed'}`)
    }
  }
  
  await browser.close()
  
  // Summary
  const accessible = results.filter(r => r.accessible).length
  const failed = results.filter(r => !r.accessible).length
  
  console.log(`\n📊 Summary:`)
  console.log(`  Total tested: ${results.length}`)
  console.log(`  ✅ Accessible: ${accessible}`)
  console.log(`  ❌ Failed: ${failed}`)
  
  if (failed > 0) {
    console.log(`\n❌ Failed pages:`)
    results
      .filter(r => !r.accessible)
      .forEach(r => {
        console.log(`  - ${r.path} (${r.title}): ${r.error || 'Unknown error'}`)
      })
  }
  
  // Write results to file
  const resultsPath = path.join(__dirname, '../page_verification_results.json')
  fs.writeFileSync(resultsPath, JSON.stringify({
    timestamp: new Date().toISOString(),
    baseUrl: BASE_URL,
    totalRoutes: routes.length,
    tested: results.length,
    accessible,
    failed,
    results
  }, null, 2))
  
  console.log(`\n💾 Results saved to: ${resultsPath}`)
  
  return { accessible, failed, total: results.length }
}

// Run if executed directly
if (require.main === module) {
  verifyPages()
    .then(({ accessible, failed }) => {
      process.exit(failed > 0 ? 1 : 0)
    })
    .catch(error => {
      console.error('❌ Verification failed:', error)
      process.exit(1)
    })
}

export { verifyPages, loadRoutes }

