/**
 * Headless Browser Verification Script
 * Verifies that all pages from gui_nav.latest.json are actually accessible
 */

const { chromium } = require('@playwright/test')
const fs = require('fs')
const path = require('path')

const BASE_URL = process.env.E2E_BASE_URL || 'http://localhost:5173'
const TIMEOUT = 15000

function loadRoutes() {
  const navPath = path.join(__dirname, 'src/data/gui_nav.latest.json')
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
    
    const response = await page.goto(url, { 
      waitUntil: 'domcontentloaded',
      timeout: TIMEOUT 
    })
    
    result.statusCode = response?.status() || 0
    
    if (response && response.status() >= 400) {
      result.error = `HTTP ${response.status()}`
      return result
    }
    
    // Wait a bit for React to render
    await page.waitForTimeout(2000)
    
    // Check if page has content
    const bodyText = await page.textContent('body') || ''
    const hasError = await page.$('text=/error|404|not found/i')
    const hasReactRoot = await page.$('#root, [data-reactroot]')
    const hasMainContent = await page.$('main, [role="main"], .page-container')
    
    result.hasContent = bodyText.length > 100
    result.hasReactApp = !!hasReactRoot
    result.hasMainContent = !!hasMainContent
    result.accessible = response?.status() === 200 && !hasError && (hasReactRoot || hasMainContent)
    
    if (!result.accessible) {
      if (!hasReactRoot && !hasMainContent) {
        result.error = 'No React app or main content found'
      } else if (hasError) {
        result.error = 'Error message detected on page'
      } else if (response?.status() !== 200) {
        result.error = `HTTP ${response?.status()}`
      } else {
        result.error = 'Content check failed'
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
  console.log(`   Base URL: ${BASE_URL}\n`)
  
  const browser = await chromium.launch({ headless: true })
  const context = await browser.newContext()
  const page = await context.newPage()
  
  page.setDefaultTimeout(TIMEOUT)
  
  const results = []
  const testAll = process.env.TEST_ALL === '1'
  const sampleSize = testAll ? routes.length : Math.min(50, routes.length)
  
  console.log(`🧪 Testing ${sampleSize} pages (out of ${routes.length} total)...`)
  if (!testAll) {
    console.log(`   (Set TEST_ALL=1 to test all pages)\n`)
  } else {
    console.log()
  }
  
  for (let i = 0; i < sampleSize; i++) {
    const route = routes[i]
    process.stdout.write(`  [${i + 1}/${sampleSize}] ${route.path}... `)
    const result = await checkPage(page, route)
    results.push(result)
    
    if (result.accessible) {
      console.log('✅')
    } else {
      console.log(`❌ (${result.error})`)
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
    console.log(`\n❌ Failed pages (first 20):`)
    results
      .filter(r => !r.accessible)
      .slice(0, 20)
      .forEach(r => {
        console.log(`  - ${r.path} (${r.title}): ${r.error || 'Unknown error'}`)
      })
    if (failed > 20) {
      console.log(`  ... and ${failed - 20} more`)
    }
  }
  
  // Write results
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
  
  console.log(`\n💾 Results saved to: page_verification_results.json`)
  
  return { accessible, failed, total: results.length }
}

if (require.main === module) {
  verifyPages()
    .then(({ accessible, failed }) => {
      process.exit(failed > accessible ? 1 : 0)
    })
    .catch(error => {
      console.error('❌ Verification failed:', error)
      process.exit(1)
    })
}

module.exports = { verifyPages, loadRoutes }

