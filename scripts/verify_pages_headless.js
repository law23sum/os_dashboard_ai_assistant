/**
 * Headless Browser Verification Script
 * 
 * Verifies that all pages from gui_nav.latest.json are actually accessible
 * Uses Playwright to test page rendering
 */

const { chromium } = require('playwright')
const fs = require('fs')
const path = require('path')

const BASE_URL = process.env.E2E_BASE_URL || 'http://localhost:5173'
const TIMEOUT = 15000 // 15 seconds per page

function loadRoutes() {
  const navPath = path.join(__dirname, '../frontend/src/data/gui_nav.latest.json')
  const data = JSON.parse(fs.readFileSync(navPath, 'utf-8'))
  
  const routes = []
  
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

async function checkPage(page, route) {
  const result = {
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
    await page.waitForTimeout(2000)
    
    // Check if page has content (not just a blank page or error)
    const bodyText = await page.textContent('body')
    const hasError = await page.$('text=/error|404|not found/i')
    const hasContent = bodyText && bodyText.length > 100 && !hasError
    
    // Check for React app mount
    const hasReactApp = await page.$('#root, [data-reactroot], [id^="root"]')
    
    result.hasContent = !!hasContent
    result.hasReactApp = !!hasReactApp
    result.accessible = response?.status() === 200 && (hasContent || hasReactApp)
    
    if (!result.accessible) {
      if (!hasContent && !hasReactApp) {
        result.error = 'Page appears empty or has no content'
      } else if (response?.status() !== 200) {
        result.error = `HTTP ${response?.status()}`
      } else {
        result.error = 'Page loaded but content check failed'
      }
    }
    
  } catch (error) {
    result.error = error.message || 'Unknown error'
    result.accessible = false
  }
  
  return result
}

async function verifyPages() {
  console.log('🔍 Loading routes from gui_nav.latest.json...')
  const routes = loadRoutes()
  console.log(`📋 Found ${routes.length} routes to verify\n`)
  
  console.log(`🌐 Starting headless browser...`)
  const browser = await chromium.launch({ headless: true })
  const context = await browser.newContext()
  const page = await context.newPage()
  
  // Set longer timeout
  page.setDefaultTimeout(TIMEOUT)
  
  const results = []
  // Test a sample of pages first, then all if requested
  const testAll = process.env.TEST_ALL === '1'
  const sampleSize = testAll ? routes.length : Math.min(30, routes.length)
  
  console.log(`\n🧪 Testing ${sampleSize} pages (out of ${routes.length} total)...\n`)
  console.log(`   (Set TEST_ALL=1 to test all pages)\n`)
  
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
  console.log(`  Success rate: ${((accessible / results.length) * 100).toFixed(1)}%`)
  
  if (failed > 0) {
    console.log(`\n❌ Failed pages:`)
    results
      .filter(r => !r.accessible)
      .slice(0, 20) // Show first 20 failures
      .forEach(r => {
        console.log(`  - ${r.path} (${r.title}): ${r.error || 'Unknown error'}`)
      })
    if (failed > 20) {
      console.log(`  ... and ${failed - 20} more`)
    }
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

module.exports = { verifyPages, loadRoutes }

