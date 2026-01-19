#!/usr/bin/env node
const fs = require('fs')
const path = require('path')

const repoRoot = path.resolve(__dirname, '..')
const reportPath = path.join(repoRoot, 'incomplete_pages_report.json')
const scaffoldPath = path.join(repoRoot, 'frontend/src/pages/RouteScaffold.tsx')

const toPosix = (value) => value.split(path.sep).join('/')

const fileLooksLikeScaffold = (content) =>
  content.includes('page-container') &&
  content.includes('status-badge') &&
  content.includes('kpi-card')

const resolveReExportTarget = (filePath, content) => {
  const match = content.match(/export\s*\{\s*default\s*\}\s*from\s*['"](.+)['"]/)
  if (!match) return filePath
  const importPath = match[1]
  if (!importPath) return filePath
  if (importPath.includes('RouteScaffold')) return filePath

  const basePath = importPath.endsWith('.tsx') || importPath.endsWith('.ts')
    ? importPath
    : `${importPath}.tsx`

  return path.resolve(path.dirname(filePath), basePath)
}

if (!fs.existsSync(reportPath)) {
  console.error('Missing incomplete_pages_report.json. Run verify_all_page_components.py first.')
  process.exit(1)
}

if (!fs.existsSync(scaffoldPath)) {
  console.error('Missing RouteScaffold.tsx at frontend/src/pages/RouteScaffold.tsx.')
  process.exit(1)
}

const report = JSON.parse(fs.readFileSync(reportPath, 'utf8'))
const reportTargets = report
  .filter((entry) => Array.isArray(entry.issues) && entry.issues.includes('Contains stubs/TODOs'))
  .map((entry) => entry.path)

const pagesRoot = path.join(repoRoot, 'frontend/src/pages')
const scanTargets = []
const walk = (dir) => {
  const entries = fs.readdirSync(dir, { withFileTypes: true })
  entries.forEach((entry) => {
    const resolved = path.join(dir, entry.name)
    if (entry.isDirectory()) {
      walk(resolved)
      return
    }
    if (!entry.isFile() || !resolved.endsWith('.tsx')) {
      return
    }
    const content = fs.readFileSync(resolved, 'utf8')
    if (fileLooksLikeScaffold(content)) {
      scanTargets.push(resolved)
    }
  })
}

walk(pagesRoot)

const targets = Array.from(
  new Set(
    [...reportTargets, ...scanTargets].filter(Boolean).map((value) =>
      path.resolve(repoRoot, value),
    ),
  ),
)

let updated = 0
let skipped = 0
const changed = []

for (const fileEntry of targets) {
  if (!fileEntry) {
    skipped += 1
    continue
  }
  const filePath = path.resolve(repoRoot, fileEntry)
  if (!filePath.startsWith(repoRoot) || !fs.existsSync(filePath)) {
    skipped += 1
    continue
  }

  const content = fs.readFileSync(filePath, 'utf8')
  const targetPath = resolveReExportTarget(filePath, content)
  if (!fs.existsSync(targetPath)) {
    skipped += 1
    continue
  }

  const targetContent = fs.readFileSync(targetPath, 'utf8')
  if (!fileLooksLikeScaffold(targetContent)) {
    skipped += 1
    continue
  }

  let relImport = path.relative(path.dirname(targetPath), scaffoldPath)
  relImport = relImport.replace(/\\/g, '/').replace(/\.tsx$/, '')
  if (!relImport.startsWith('.')) {
    relImport = `./${relImport}`
  }

  const nextContent = `export { default } from '${relImport}'\n`

  if (targetContent.trim() === nextContent.trim()) {
    skipped += 1
    continue
  }

  fs.writeFileSync(targetPath, nextContent, 'utf8')
  updated += 1
  changed.push(toPosix(path.relative(repoRoot, targetPath)))
}

console.log(`Stub scaffold pages updated: ${updated}`)
console.log(`Skipped: ${skipped}`)
if (changed.length) {
  console.log('Updated files:')
  changed.forEach((file) => console.log(`- ${file}`))
}
