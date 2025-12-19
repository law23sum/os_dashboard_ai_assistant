/**
 * End-to-End Test Configuration
 * 
 * Environments: local/dev, alpha/beta, prod/release
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
  alpha: {
    name: 'alpha',
    apiBase: process.env.ALPHA_API_BASE || 'https://alpha-api.osdashboard.ai/api',
    frontendUrl: process.env.ALPHA_FRONTEND_URL || 'https://alpha.osdashboard.ai',
    description: 'Alpha environment (integrated testing)',
  },
  beta: {
    name: 'beta',
    apiBase: process.env.BETA_API_BASE || 'https://beta-api.osdashboard.ai/api',
    frontendUrl: process.env.BETA_FRONTEND_URL || 'https://beta.osdashboard.ai',
    description: 'Beta environment (integrated testing)',
  },
  prod: {
    name: 'prod',
    apiBase: process.env.PROD_API_BASE || 'https://api.osdashboard.ai/api',
    frontendUrl: process.env.PROD_FRONTEND_URL || 'https://osdashboard.ai',
    description: 'Production environment (real user data testing)',
  },
  release: {
    name: 'release',
    apiBase: process.env.RELEASE_API_BASE || 'https://api.osdashboard.ai/api',
    frontendUrl: process.env.RELEASE_FRONTEND_URL || 'https://osdashboard.ai',
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
