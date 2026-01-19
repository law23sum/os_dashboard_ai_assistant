#!/usr/bin/env node
/* eslint-disable no-console */
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const REPO_ROOT = path.resolve(__dirname, '..');
const PRODUCT_DATA_PATH = path.join(REPO_ROOT, 'docs', 'scripts', 'product-data.js');

const DEPRECATED_PUBLIC_NAMES = [
  'OS Dashboard AI Assistant Platform',
  'Overall OS Dashboard AI Assistant Platform',
  'Overall OS Dashboard AI Assistant Platform Envelope',
  'Advanced Research, Simulation & Digital Twin Platform Envelope',
  'Project Management System (PMS)',
  'Project Management System',
  'Master Stack & Project Management Engine',
];

const ALLOWED_TIERS = new Set([
  'Product',
  'Capability',
  'System',
  'Platform',
  'Service',
  'Module',
  'Feature',
  'Process',
  'Pipeline',
]);

const SCAN_DIRS = [
  path.join(REPO_ROOT, 'docs'),
  path.join(REPO_ROOT, 'frontend', 'src'),
  path.join(REPO_ROOT, 'frontend', 'public', 'docs'),
  path.join(REPO_ROOT, 'frontend', 'public', 'gui_nav.latest.json'),
  path.join(REPO_ROOT, 'frontend', 'src', 'data'),
  path.join(REPO_ROOT, 'frontend', 'src', 'domain'),
  path.join(REPO_ROOT, 'ui'),
  path.join(REPO_ROOT, 'README.md'),
];

const IGNORE_DIRS = new Set([
  'node_modules',
  'dist',
  'build',
  'coverage',
  'documentation',
  'worktrees',
  'agent_exports',
  'nav_exports',
  'reference',
]);

const IGNORE_FILES = new Set([
  path.join(REPO_ROOT, 'docs', 'architecture', 'renaming-map.md'),
  path.join(REPO_ROOT, 'MIGRATION.md'),
]);

const TEXT_EXTENSIONS = new Set(['.md', '.html', '.js', '.ts', '.tsx', '.json', '.txt']);

function collectFiles(target) {
  const files = [];
  if (!fs.existsSync(target)) return files;
  const stat = fs.statSync(target);
  if (stat.isFile()) {
    files.push(target);
    return files;
  }
  const queue = [target];
  while (queue.length) {
    const current = queue.pop();
    const entries = fs.readdirSync(current, { withFileTypes: true });
    for (const entry of entries) {
      if (entry.isDirectory()) {
        if (IGNORE_DIRS.has(entry.name)) continue;
        queue.push(path.join(current, entry.name));
      } else if (entry.isFile()) {
        const filePath = path.join(current, entry.name);
        if (IGNORE_FILES.has(filePath)) continue;
        if (TEXT_EXTENSIONS.has(path.extname(entry.name))) {
          files.push(filePath);
        }
      }
    }
  }
  return files;
}

function checkDeprecatedNames(files) {
  const violations = [];
  for (const filePath of files) {
    let content;
    try {
      content = fs.readFileSync(filePath, 'utf8');
    } catch {
      continue;
    }
    for (const needle of DEPRECATED_PUBLIC_NAMES) {
      if (content.includes(needle)) {
        violations.push({ filePath, needle });
      }
    }
  }
  return violations;
}

function loadProductCatalog() {
  if (!fs.existsSync(PRODUCT_DATA_PATH)) {
    throw new Error(`Missing product data: ${PRODUCT_DATA_PATH}`);
  }
  const code = fs.readFileSync(PRODUCT_DATA_PATH, 'utf8');
  const sandbox = { window: {} };
  vm.createContext(sandbox);
  vm.runInContext(code, sandbox, { filename: PRODUCT_DATA_PATH });
  const data = sandbox.window.osProductData;
  if (!Array.isArray(data)) {
    throw new Error('window.osProductData is not an array in product-data.js');
  }
  return data;
}

function checkCatalogMetadata(entries) {
  const errors = [];
  entries.forEach((entry, index) => {
    const label = entry.name || entry.id || `index ${index}`;
    if (!entry.artifact_type) {
      errors.push(`${label}: missing artifact_type`);
    }
    if (!entry.tier) {
      errors.push(`${label}: missing tier`);
    } else if (!ALLOWED_TIERS.has(entry.tier)) {
      errors.push(`${label}: invalid tier "${entry.tier}"`);
    }
    if (entry.artifact_type === 'Capability' && !entry.capability_layer) {
      errors.push(`${label}: capability_layer required for Capability artifacts`);
    }
  });
  return errors;
}

function main() {
  const files = SCAN_DIRS.flatMap(collectFiles);
  const deprecatedViolations = checkDeprecatedNames(files);
  const catalog = loadProductCatalog();
  const catalogErrors = checkCatalogMetadata(catalog);

  if (deprecatedViolations.length || catalogErrors.length) {
    console.error('Naming drift check failed.');
    if (deprecatedViolations.length) {
      console.error('\\nDeprecated name occurrences:');
      for (const violation of deprecatedViolations) {
        const rel = path.relative(REPO_ROOT, violation.filePath);
        console.error(`- ${rel}: "${violation.needle}"`);
      }
    }
    if (catalogErrors.length) {
      console.error('\\nCatalog metadata errors:');
      for (const err of catalogErrors) {
        console.error(`- ${err}`);
      }
    }
    process.exit(1);
  }

  console.log('Naming drift check passed.');
}

main();
