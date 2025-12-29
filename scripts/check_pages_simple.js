/**
 * Simple Page Verification
 * Checks route registration and provides summary
 */

const fs = require('fs')
const path = require('path')

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
            title: feature.title,
            platform,
            category
          })
        }
      }
    }
  }
  
  return routes
}

function checkRouteGeneration() {
  const runtimePath = path.join(__dirname, '../frontend/src/nav/runtime.ts')
  const routesPath = path.join(__dirname, '../frontend/src/routes.tsx')
  const appPath = path.join(__dirname, '../frontend/src/App.tsx')
  
  const checks = {
    runtimeExists: fs.existsSync(runtimePath),
    routesExists: fs.existsSync(routesPath),
    appExists: fs.existsSync(appPath),
    runtimeHasGetAllPaths: false,
    routesHasGenerateRoutes: false,
    appUsesGenerateRoutes: false
  }
  
  if (checks.runtimeExists) {
    const runtimeContent = fs.readFileSync(runtimePath, 'utf-8')
    checks.runtimeHasGetAllPaths = runtimeContent.includes('getAllConfiguredPaths')
  }
  
  if (checks.routesExists) {
    const routesContent = fs.readFileSync(routesPath, 'utf-8')
    checks.routesHasGenerateRoutes = routesContent.includes('generateRoutes')
  }
  
  if (checks.appExists) {
    const appContent = fs.readFileSync(appPath, 'utf-8')
    checks.appUsesGenerateRoutes = appContent.includes('generateRoutes()')
  }
  
  return checks
}

function main() {
  console.log('🔍 Checking Page Configuration...\n')
  
  const routes = loadRoutes()
  console.log(`📋 Total routes in gui_nav.latest.json: ${routes.length}\n`)
  
  const routeChecks = checkRouteGeneration()
  console.log('📝 Route Generation Status:')
  console.log(`  ✅ runtime.ts exists: ${routeChecks.runtimeExists}`)
  console.log(`  ✅ getAllConfiguredPaths() exists: ${routeChecks.runtimeHasGetAllPaths}`)
  console.log(`  ✅ routes.tsx exists: ${routeChecks.routesExists}`)
  console.log(`  ✅ generateRoutes() exists: ${routeChecks.routesHasGenerateRoutes}`)
  console.log(`  ✅ App.tsx uses generateRoutes(): ${routeChecks.appUsesGenerateRoutes}\n`)
  
  // Check RouteScaffold
  const scaffoldPath = path.join(__dirname, '../frontend/src/pages/RouteScaffold.tsx')
  const scaffoldExists = fs.existsSync(scaffoldPath)
  console.log(`📄 RouteScaffold.tsx exists: ${scaffoldExists}`)
  
  if (scaffoldExists) {
    const scaffoldContent = fs.readFileSync(scaffoldPath, 'utf-8')
    const hasFeatureTemplate = scaffoldContent.includes('FeaturePageTemplate')
    const hasCategoryTemplate = scaffoldContent.includes('CategoryHomeTemplate')
    console.log(`  ✅ Uses FeaturePageTemplate: ${hasFeatureTemplate}`)
    console.log(`  ✅ Uses CategoryHomeTemplate: ${hasCategoryTemplate}`)
  }
  
  // Sample routes
  console.log(`\n📋 Sample Routes (first 20):`)
  routes.slice(0, 20).forEach(r => {
    console.log(`  ${r.path} - ${r.title}`)
  })
  
  console.log(`\n💡 To verify pages are accessible:`)
  console.log(`  1. Ensure backend is running: python start_ui.py --mode web`)
  console.log(`  2. Open browser: http://localhost:5173`)
  console.log(`  3. Navigate to routes listed above`)
  console.log(`  4. Check browser console for errors`)
  
  console.log(`\n📊 Summary:`)
  console.log(`  Total routes configured: ${routes.length}`)
  console.log(`  Route generation: ${routeChecks.runtimeHasGetAllPaths && routeChecks.routesHasGenerateRoutes ? '✅ Configured' : '❌ Missing'}`)
  console.log(`  App integration: ${routeChecks.appUsesGenerateRoutes ? '✅ Integrated' : '❌ Not integrated'}`)
}

main()

