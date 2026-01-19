/**
 * End-to-End Test Configuration
 * 
 * Environments: local/dev/preview/staging, prod/release
 * Test Types: regression, sanity, functional
 */

export interface TestEnvironment {
  name: string
  apiBase: string
  frontendUrl: string
  database?: string
  description: string
}

export const environments: Record<string, TestEnvironment> = {
  local: {
    name: 'local',
    apiBase: 'http://localhost:8000/api',
    frontendUrl: 'http://localhost:5173',
    database: 'assistant_hub_gui/assistant_hub/assistant_hub.db',
    description: 'Local development environment (unit testing)',
  },
  dev: {
    name: 'dev',
    apiBase: process.env.VITE_API_BASE || 'http://localhost:8000/api',
    frontendUrl: process.env.VITE_FRONTEND_URL || 'http://localhost:5173',
    database: 'assistant_hub_gui/assistant_hub/assistant_hub.db',
    description: 'Development environment (interchangeable with local)',
  },
  preview: {
    name: 'preview',
    apiBase: process.env.PREVIEW_API_BASE || 'https://preview.osdashboard.ai/api',
    frontendUrl: process.env.PREVIEW_FRONTEND_URL || 'https://preview.osdashboard.ai',
    description: 'Preview environment (per-PR or ephemeral)',
  },
  staging: {
    name: 'staging',
    apiBase: process.env.STAGING_API_BASE || 'https://staging.osdashboard.ai/api',
    frontendUrl: process.env.STAGING_FRONTEND_URL || 'https://staging.osdashboard.ai',
    description: 'Staging environment (release candidate)',
  },
  alpha: {
    name: 'alpha',
    apiBase: process.env.ALPHA_API_BASE || 'https://staging.osdashboard.ai/api',
    frontendUrl: process.env.ALPHA_FRONTEND_URL || 'https://staging.osdashboard.ai',
    description: 'Legacy alpha cohort (defaults to staging host)',
  },
  beta: {
    name: 'beta',
    apiBase: process.env.BETA_API_BASE || 'https://staging.osdashboard.ai/api',
    frontendUrl: process.env.BETA_FRONTEND_URL || 'https://staging.osdashboard.ai',
    description: 'Legacy beta cohort (defaults to staging host)',
  },
  prod: {
    name: 'prod',
    apiBase: process.env.PROD_API_BASE || 'https://app.osdashboard.ai/api',
    frontendUrl: process.env.PROD_FRONTEND_URL || 'https://app.osdashboard.ai',
    description: 'Production environment (real user data testing)',
  },
  release: {
    name: 'release',
    apiBase: process.env.RELEASE_API_BASE || 'https://app.osdashboard.ai/api',
    frontendUrl: process.env.RELEASE_FRONTEND_URL || 'https://app.osdashboard.ai',
    description: 'Release environment (real user data testing)',
  },
}

export function getEnvironment(envName: string = 'local'): TestEnvironment {
  const env = environments[envName]
  if (!env) {
    throw new Error(`Unknown environment: ${envName}. Available: ${Object.keys(environments).join(', ')}`)
  }
  return env
}

export interface TestSuite {
  name: string
  description: string
  type: 'regression' | 'sanity' | 'functional'
  tests: TestCase[]
}

export interface TestCase {
  id: string
  name: string
  description: string
  category: string
  priority: 'critical' | 'high' | 'medium' | 'low'
  steps: TestStep[]
  expectedResult: string
  specRef?: string
}

export interface TestStep {
  action: string
  expected?: string
}
