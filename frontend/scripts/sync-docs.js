#!/usr/bin/env node
/**
 * Copies the canonical HTML/markdown docs into frontend/public/docs so
 * every route (docs/*.html and docs/*.md) has an asset during dev/build.
 */
import fs from 'fs/promises'
import path from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const repoRoot = path.resolve(__dirname, '..', '..')

const mergeSources = [path.join(repoRoot, 'docs')]

const documentationFiles = [
  'README.md',
  'commands.md',
  'IMPLEMENTATION_SUMMARY.md',
  'IMPLEMENTATION_ROADMAP.md',
  'NEW_FEATURES_ADDED.md',
  'CANONICAL_INTERNAL_REPRESENTATION.md',
  'DAEMON_FRAMEWORK_ARCHITECTURE.md',
  'COGNITIVE_DAEMON_SYSTEM.md',
  'ARCHITECTURE_IMPLEMENTATION.md',
  'OS_DASHBOARD_CANON_SYSTEM_SPEC.md',
  'AI_OFFICE_AGENT_REALTIME.md',
  'DOCUMENT_UPLOAD_DESIGN.md',
  'DOCUMENT_UPLOAD_DAEMON_INTEGRATION.md',
  'DOCUMENT_UPLOAD_IMPLEMENTATION.md',
  'DOCUMENT_TEMPLATES_AND_AUTOMATION.md',
  'AUTOMATION_ORCHESTRATION_INTEGRATION.md',
  'FILE_TASK_EXTRACTION_FEATURE.md',
  'ONEDRIVE_INTEGRATION.md',
  'OS_DASHBOARD_ENTERPRISE.md',
  'THIRD_PARTY_CREDENTIALS_SETUP.md',
  'AWS_COST_ESTIMATE.md',
  'CONVERSATION_AI_INTEGRATION.md',
  'GLOBAL_IMPACT_WHITE_PAPER.md',
  'SALVAGED_CODE_SUMMARY.md',
  'VISION.md',
  'VISION_IMPLEMENTATION.md',
  'FUTURE_FEATURE_PORTFOLIO.md',
  'DEPLOYMENT.md',
  'FEATURE_OPPORTUNITIES.md',
  'MISSING_FEATURES_SUMMARY.md',
  'LOW_HANGING_FRUIT_FEATURES.md',
]

const copySources = [
  ...documentationFiles.map((file) => path.join(repoRoot, 'documentation', file)),
  path.join(repoRoot, 'project_directory_structure'),
  path.join(repoRoot, 'table_of_content_os_dashboard_ai_assistant.pdf'),
  path.join(repoRoot, 'CyberChef_v10.19.4'),
]
const targetRoot = path.join(repoRoot, 'frontend', 'public', 'docs')

const skipNames = new Set(['.DS_Store'])

async function pathExists(target) {
  try {
    await fs.access(target)
    return true
  } catch {
    return false
  }
}

async function copyRecursive(src, dest) {
  const stats = await fs.stat(src)
  if (stats.isDirectory()) {
    await fs.mkdir(dest, { recursive: true })
    const entries = await fs.readdir(src)
    for (const entry of entries) {
      if (entry.startsWith('.') || skipNames.has(entry)) continue
      const from = path.join(src, entry)
      const to = path.join(dest, entry)
      await copyRecursive(from, to)
    }
    return
  }
  await fs.mkdir(path.dirname(dest), { recursive: true })
  await fs.copyFile(src, dest)
}

async function main() {
  await fs.mkdir(targetRoot, { recursive: true })
  const synced = []
  for (const source of mergeSources) {
    if (!(await pathExists(source))) continue
    await copyRecursive(source, targetRoot)
    synced.push(path.relative(repoRoot, source))
  }
  for (const source of copySources) {
    if (!(await pathExists(source))) continue
    const dest = path.join(targetRoot, path.basename(source))
    await copyRecursive(source, dest)
    synced.push(path.relative(repoRoot, source))
  }
  if (!synced.length) {
    console.warn('sync-docs: no sources found, skipping copy')
    return
  }
  console.log(
    `sync-docs: copied ${synced.join(', ')} -> ${path.relative(repoRoot, targetRoot)}`,
  )
}

main().catch((error) => {
  console.error('sync-docs: failed to copy docs', error)
  process.exit(1)
})
