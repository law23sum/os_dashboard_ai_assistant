const fs = require('fs')
const path = require('path')
const vm = require('vm')
const { execFileSync } = require('child_process')

const REPO_ROOT = path.resolve(__dirname, '..')
const MANIFEST_PATH = path.join(REPO_ROOT, 'frontend', 'src', 'data', 'iaManifest.complete.ts')

const COMMITS = {
  stable: '3a154a6e6305fe9f3a760f44b1b10d73e1ed3256',
  increments: '58cfc345630f68bf10909538aba48c12f87ce9df',
  backup: '4acea80190121b8ab79d8cd1367166bcfead8bde',
}

const FALLBACK_ORDER = ['stable', 'increments', 'backup']

const extractArrayLiteral = (source, marker) => {
  const markerIndex = source.indexOf(marker)
  if (markerIndex === -1) {
    throw new Error(`Marker not found: ${marker}`)
  }
  const equalsIndex = source.indexOf('=', markerIndex)
  if (equalsIndex === -1) {
    throw new Error(`Assignment not found after marker: ${marker}`)
  }
  const start = source.indexOf('[', equalsIndex)
  if (start === -1) {
    throw new Error(`Array start not found after marker: ${marker}`)
  }

  let depth = 0
  let inSingle = false
  let inDouble = false
  let inTemplate = false
  let escape = false

  for (let i = start; i < source.length; i += 1) {
    const ch = source[i]

    if (escape) {
      escape = false
      continue
    }
    if (ch === '\\\\') {
      escape = true
      continue
    }

    if (inSingle) {
      if (ch === "'") inSingle = false
      continue
    }
    if (inDouble) {
      if (ch === '"') inDouble = false
      continue
    }
    if (inTemplate) {
      if (ch === '`') inTemplate = false
      continue
    }

    if (ch === "'") {
      inSingle = true
      continue
    }
    if (ch === '"') {
      inDouble = true
      continue
    }
    if (ch === '`') {
      inTemplate = true
      continue
    }

    if (ch === '[') {
      depth += 1
      continue
    }
    if (ch === ']') {
      depth -= 1
      if (depth === 0) {
        return source.slice(start, i + 1)
      }
    }
  }

  throw new Error('Array literal not closed')
}

const loadManifest = () => {
  const source = fs.readFileSync(MANIFEST_PATH, 'utf8')
  const arrayText = extractArrayLiteral(source, 'export const iaManifest')
  return vm.runInNewContext(arrayText)
}

const toTitleFromRoute = (route) => {
  if (!route) return 'Feature'
  const cleaned = route.replace(/\/+$/, '').split('/').filter(Boolean).pop() || 'Feature'
  return cleaned
    .split('-')
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(' ')
}

const getComponentName = (componentPath) => {
  const base = path.basename(componentPath, path.extname(componentPath))
  const cleaned = base.replace(/[^A-Za-z0-9_]/g, '')
  return cleaned || 'RestoredPage'
}

const ensureDir = (filePath) => {
  fs.mkdirSync(path.dirname(filePath), { recursive: true })
}

const readFromCommit = (sha, componentPath) => {
  try {
    return execFileSync('git', ['show', `${sha}:${componentPath}`], {
      cwd: REPO_ROOT,
      encoding: 'utf8',
      stdio: ['ignore', 'pipe', 'ignore'],
    })
  } catch (error) {
    return null
  }
}

const writeStubFeature = (entry, targetPath) => {
  const componentName = getComponentName(entry.componentPath)
  const title = entry.label || toTitleFromRoute(entry.route)
  const description = `Feature page for ${title}.`
  const content = [
    "import { FeaturePageTemplate } from '@/components/templates/FeaturePageTemplate'",
    '',
    `/**`,
    ` * ${title} Page`,
    ` * Route: ${entry.route}`,
    ` */`,
    `export default function ${componentName}() {`,
    `  return (`,
    `    <FeaturePageTemplate`,
    `      title=${JSON.stringify(title)}`,
    `      description=${JSON.stringify(description)}`,
    `    />`,
    `  )`,
    `}`,
    '',
  ].join('\n')
  ensureDir(targetPath)
  fs.writeFileSync(targetPath, content, 'utf8')
}

const writeStubCategory = (entry, targetPath) => {
  const componentName = getComponentName(entry.componentPath)
  const title = entry.label || toTitleFromRoute(entry.route)
  const description = `Category home and dashboard for ${title}.`
  const features = Array.isArray(entry.features)
    ? entry.features.slice(0, 8).map((feature) => ({
        title: feature.label || toTitleFromRoute(feature.route),
        path: feature.route || '/',
      }))
    : []
  const content = [
    "import { CategoryHomeTemplate } from '@/components/templates/CategoryHomeTemplate'",
    '',
    `const features = ${JSON.stringify(features, null, 2)}`,
    '',
    `/**`,
    ` * ${title} Home`,
    ` * Route: ${entry.route}`,
    ` */`,
    `export default function ${componentName}() {`,
    `  return (`,
    `    <CategoryHomeTemplate`,
    `      title=${JSON.stringify(title)}`,
    `      description=${JSON.stringify(description)}`,
    `      features={features}`,
    `    />`,
    `  )`,
    `}`,
    '',
  ].join('\n')
  ensureDir(targetPath)
  fs.writeFileSync(targetPath, content, 'utf8')
}

const main = () => {
  const manifest = loadManifest()
  const entries = []

  for (const platform of manifest) {
    for (const category of platform.categories || []) {
      if (category.homeRoute && category.homeComponentPath) {
        entries.push({
          type: 'categoryHome',
          route: category.homeRoute,
          label: category.label,
          componentPath: category.homeComponentPath,
          bestCommit: category.homeBestCommit || 'stable',
          features: category.features || [],
        })
      }

      for (const feature of category.features || []) {
        if (!feature.route || !feature.componentPath) continue
        entries.push({
          type: 'feature',
          route: feature.route,
          label: feature.label,
          componentPath: feature.componentPath,
          bestCommit: feature.bestCommit || 'stable',
        })
      }
    }
  }

  const routeComponentMap = {}
  for (const entry of entries) {
    if (!entry.route || !entry.componentPath) continue
    if (!entry.componentPath.startsWith('frontend/src/pages/')) continue
    if (!routeComponentMap[entry.route]) {
      routeComponentMap[entry.route] = entry.componentPath
    }
  }

  const mapPath = path.join(REPO_ROOT, 'frontend', 'src', 'navigation', 'routeComponentMap.ts')
  const sortedRoutes = Object.keys(routeComponentMap).sort()
  const mapLines = [
    'export const routeComponentMap: Record<string, string> = {',
    ...sortedRoutes.map((route) => `  ${JSON.stringify(route)}: ${JSON.stringify(routeComponentMap[route])},`),
    '}',
    '',
    'export const routeComponentRoutes = Object.keys(routeComponentMap).sort(',
    '  (a, b) => b.length - a.length,',
    ')',
    '',
  ]
  ensureDir(mapPath)
  fs.writeFileSync(mapPath, mapLines.join('\n'), 'utf8')

  const processed = new Set()
  let restored = 0
  let generated = 0
  let skipped = 0
  let missingSource = 0

  for (const entry of entries) {
    if (!entry.componentPath || !entry.componentPath.startsWith('frontend/src/pages/')) {
      continue
    }
    if (processed.has(entry.componentPath)) {
      continue
    }
    processed.add(entry.componentPath)

    const targetPath = path.join(REPO_ROOT, entry.componentPath)
    if (fs.existsSync(targetPath)) {
      skipped += 1
      continue
    }

    const commitOrder = [entry.bestCommit, ...FALLBACK_ORDER].filter(
      (value, index, self) => value && self.indexOf(value) === index,
    )

    let content = null
    for (const commitName of commitOrder) {
      const sha = COMMITS[commitName]
      if (!sha) continue
      const result = readFromCommit(sha, entry.componentPath)
      if (result) {
        content = result
        break
      }
    }

    if (content) {
      ensureDir(targetPath)
      fs.writeFileSync(targetPath, content, 'utf8')
      restored += 1
      continue
    }

    missingSource += 1
    if (entry.type === 'categoryHome') {
      writeStubCategory(entry, targetPath)
    } else {
      writeStubFeature(entry, targetPath)
    }
    generated += 1
  }

  console.log('Restoration Summary')
  console.log(`  Restored: ${restored}`)
  console.log(`  Generated stubs: ${generated}`)
  console.log(`  Missing source: ${missingSource}`)
  console.log(`  Skipped (existing): ${skipped}`)
}

main()
