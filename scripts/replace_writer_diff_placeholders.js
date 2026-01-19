#!/usr/bin/env node
const fs = require('fs')
const path = require('path')

const repoRoot = path.resolve(__dirname, '..')
const pagesRoot = path.join(repoRoot, 'frontend', 'src', 'pages')

const pattern = /const handleViewAIChanges = \(\) => \{\s*\/\/ TODO: Implement diff view\s*alert\('Diff view coming soon!'\)\s*\}/g
const replacement = `const handleViewAIChanges = () => {\n    if (!pendingAIChange) return\n    const currentContent = openDocuments.get(pendingAIChange.documentId)?.content ?? ''\n    const proposedContent = pendingAIChange.newContent ?? ''\n    const preview = [\n      'Current draft:',\n      currentContent || '(empty)',\n      '',\n      'Proposed draft:',\n      proposedContent || '(empty)',\n    ].join('\\n')\n    alert(preview)\n  }`

const updated = []
const walk = (dir) => {
  const entries = fs.readdirSync(dir, { withFileTypes: true })
  entries.forEach((entry) => {
    const fullPath = path.join(dir, entry.name)
    if (entry.isDirectory()) {
      walk(fullPath)
      return
    }
    if (!entry.isFile() || !fullPath.endsWith('.tsx')) return

    const content = fs.readFileSync(fullPath, 'utf8')
    if (!content.includes('Diff view coming soon!')) return

    const next = content.replace(pattern, replacement)
    if (next !== content) {
      fs.writeFileSync(fullPath, next, 'utf8')
      updated.push(path.relative(repoRoot, fullPath))
    }
  })
}

walk(pagesRoot)

console.log(`Updated ${updated.length} writer diff placeholders`)
if (updated.length) {
  updated.forEach((file) => console.log(`- ${file}`))
}
