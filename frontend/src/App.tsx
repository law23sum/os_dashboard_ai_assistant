import { useEffect, useMemo, useState } from 'react'
import { BrowserRouter, HashRouter, Routes, Route, Navigate, Outlet } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

import Layout from './components/Layout'
import { AppErrorBoundary } from './components/AppErrorBoundary'
import { Toaster } from './utils/toast'
import { applyTheme, defaultTheme } from './theme'

// Pages
import Login from './pages/Login'
import Signup from './pages/Signup'
import Admin from './pages/Admin'
import Research from './pages/Research'
import Dashboard from './pages/Dashboard'
import Tasks from './pages/Tasks'
import Projects from './pages/Projects'
import Chat from './pages/Chat'
import Collaboration from './pages/Collaboration'
import Personalization from './pages/Personalization'
import SearchEngine from './pages/SearchEngine'
import Templates from './pages/Templates'
import Writer from './pages/Writer'
import Tools from './pages/Tools'
import AIOps from './pages/AIOps'
import AIOS from './pages/AIOS'
import AICopilot from './pages/AICopilot'
import AdvancedAI from './pages/AdvancedAI'
import AdvancedSystems from './pages/AdvancedSystems'
import MLOps from './pages/MLOps'
import NeuralArchitectureSearch from './pages/NeuralArchitectureSearch'
import NAS from './pages/NAS'
import ComputerVision from './pages/ComputerVision'
import EdgeComputing from './pages/EdgeComputing'
import IntentProcessor from './pages/IntentProcessor'
import CapsuleMarketplace from './pages/CapsuleMarketplace'
import AutoFix from './pages/AutoFix'
import Workflows from './pages/Workflows'
import Integrations from './pages/Integrations'
import APIConnectors from './pages/APIConnectors'
import OfficeRealtime from './pages/OfficeRealtime'
import Analytics from './pages/Analytics'
import Monitoring from './pages/Monitoring'
import Observability from './pages/Observability'
import Audit from './pages/Audit'
import Billing from './pages/Billing'
import NetworkMonitoring from './pages/NetworkMonitoring'
import Security from './pages/Security'
import WorkspaceHealth from './pages/WorkspaceHealth'
import ProjectOrchestrator from './pages/ProjectOrchestrator'
import Docs from './pages/Docs'
import SpecSheet from './pages/SpecSheet'
import Documentation from './pages/Documentation'
import VisionDeck from './pages/VisionDeck'
import FutureDeck from './pages/FutureDeck'
import Settings from './pages/Settings'
import SpecPage from './pages/SpecPage'

// Auth
import { AuthProvider } from './auth/AuthContext'
import { RequireAuth } from './auth/RequireAuth'
import { RequireAdmin } from './auth/RequireAdmin'

const normalizeBasePath = (value?: string | null): string => {
  if (!value || value === '.' || value === './') return '/'
  try {
    const url = new URL(value, 'http://placeholder')
    let pathname = url.pathname || '/'
    pathname = pathname.replace(/\/+$/, '')
    return pathname || '/'
  } catch {
    if (value.startsWith('/')) {
      const trimmed = value.replace(/\/+$/, '')
      return trimmed || '/'
    }
    return '/'
  }
}

const resolveRouterBasePath = (): string => {
  if (typeof document !== 'undefined') {
    const baseHref = document.querySelector('base')?.getAttribute('href')
    if (baseHref) return normalizeBasePath(baseHref)
  }
  const envBase = import.meta.env.BASE_URL || '/'
  return normalizeBasePath(envBase)
}

const shouldUseHashRouter = (): boolean => {
  if (typeof window === 'undefined') return false
  
  // Electron `file://` URLs break BrowserRouter.
  if (window.location.protocol === 'file:') return true
  
  // Check if history API is available and secure
  try {
    // Test if we can safely use the history API
    if (typeof window.history === 'undefined' || typeof window.history.pushState === 'undefined') {
      return true
    }
    // Additional security check for mixed content or insecure contexts
    if (window.location.protocol === 'http:' && window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
      // Prefer HashRouter for non-localhost HTTP to avoid security issues
      return false // Keep BrowserRouter for HTTP, but this can be adjusted
    }
  } catch (e) {
    // If we can't access history API, fall back to HashRouter
    console.warn('History API not available, falling back to HashRouter:', e)
    return true
  }
  
  return false
}

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60 * 1000,
      gcTime: 5 * 60 * 1000,
      refetchOnWindowFocus: false,
      retry: 1,
    },
    mutations: {
      retry: 1,
    },
  },
})

// Safe Router wrapper that falls back to HashRouter if BrowserRouter initialization fails
function SafeRouter({ children, useHashRouter, basePath }: { 
  children: React.ReactNode
  useHashRouter: boolean
  basePath: string
}) {
  const [shouldUseHash, setShouldUseHash] = useState(useHashRouter)
  
  useEffect(() => {
    // Test if BrowserRouter can be safely used
    if (!useHashRouter && typeof window !== 'undefined') {
      try {
        // Test history API access
        const testState = { test: true }
        window.history.replaceState(testState, '', window.location.href)
        // If we get here, history API works
        setShouldUseHash(false)
      } catch (error) {
        // History API not available or insecure, fall back to HashRouter
        console.warn('BrowserRouter not available, falling back to HashRouter:', error)
        setShouldUseHash(true)
      }
    } else {
      setShouldUseHash(useHashRouter)
    }
  }, [useHashRouter])

  const Router = shouldUseHash ? HashRouter : BrowserRouter
  
  return (
    <Router basename={shouldUseHash ? undefined : basePath}>
      {children}
    </Router>
  )
}

// Layout wrapper component for protected routes
function LayoutWrapper() {
  return (
    <Layout>
      <Outlet />
    </Layout>
  )
}

function App() {
  useEffect(() => {
    applyTheme(defaultTheme)
  }, [])

  // Memoize router configuration to prevent recreation on every render
  const { basePath, useHashRouter } = useMemo(() => {
    const base = resolveRouterBasePath()
    const useHash = shouldUseHashRouter()
    return {
      basePath: base,
      useHashRouter: useHash,
    }
  }, [])

  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <SafeRouter useHashRouter={useHashRouter} basePath={basePath}>
          <AppErrorBoundary>
            <Routes>
              {/* Public Routes */}
              <Route path="/login" element={<Login />} />
              <Route path="/signup" element={<Signup />} />

              {/* Protected Routes */}
              <Route element={<RequireAuth><LayoutWrapper /></RequireAuth>}>
                {/* Root & Core Pages */}
                <Route path="/" element={<Dashboard />} />
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/tasks" element={<Tasks />} />
                <Route path="/projects" element={<Projects />} />
                <Route path="/chat" element={<Chat />} />
                <Route path="/research" element={<Research />} />
                <Route path="/collaboration" element={<Collaboration />} />
                <Route path="/personalization" element={<Personalization />} />
                <Route path="/search" element={<SearchEngine />} />

                {/* Work & Writing Hierarchy: /work/* */}
                <Route path="/work" element={<Navigate to="/work/templates" replace />} />
                <Route path="/work/templates" element={<Templates />} />
                <Route path="/work/writer" element={<Writer />} />
                <Route path="/work/tools" element={<Tools />} />
                <Route path="/templates" element={<Navigate to="/work/templates" replace />} />
                <Route path="/writer" element={<Navigate to="/work/writer" replace />} />
                <Route path="/tools" element={<Navigate to="/work/tools" replace />} />

                {/* Mission & Architecture Hierarchy: /mission/* */}
                <Route path="/mission" element={<Navigate to="/mission/overview" replace />} />
                <Route path="/mission/overview" element={<Dashboard />} />
                <Route path="/mission/modes" element={<Dashboard />} />
                <Route path="/mission/identity" element={<Settings />} />
                <Route path="/mission/daemons" element={<AIOps />} />
                <Route path="/mission/ai-stack" element={<AIOS />} />
                <Route path="/mission/models" element={<AdvancedAI />} />
                <Route path="/mission/architecture" element={<AdvancedSystems />} />
                <Route path="/mission/components" element={<AdvancedSystems />} />
                <Route path="/mission/principles" element={<AdvancedSystems />} />
                <Route path="/mission/mapping" element={<AdvancedSystems />} />
                <Route path="/mission/orchestrator" element={<AIOps />} />
                <Route path="/mission/planes/data" element={<Dashboard />} />
                <Route path="/mission/planes/control" element={<AIOps />} />
                <Route path="/mission/planes/governance" element={<Security />} />
                <Route path="/mission/planes/cross-plane" element={<AdvancedSystems />} />

                {/* Workspaces Hierarchy */}
                <Route path="/workspaces" element={<Navigate to="/workspaces/dev" replace />} />
                <Route path="/workspaces/dev" element={<Tools />} />
                <Route path="/workspaces/dev/merge-advisor" element={<Tools />} />
                <Route path="/workspaces/dev/commit-tasks" element={<Tasks />} />
                <Route path="/workspaces/dev/cicd" element={<Workflows />} />
                <Route path="/workspaces/research/lab" element={<Research />} />
                <Route path="/workspaces/research/simulation" element={<Research />} />
                <Route path="/workspaces/research/experiments" element={<NeuralArchitectureSearch />} />
                <Route path="/workspaces/research/validation" element={<NeuralArchitectureSearch />} />
                <Route path="/workspaces/research/digital-twins" element={<Research />} />
                <Route path="/workspaces/research/hpc" element={<Research />} />
                <Route path="/workspaces/writer/canon" element={<Writer />} />
                <Route path="/workspaces/writer/narrative" element={<Writer />} />
                <Route path="/workspaces/writer/qa" element={<Writer />} />
                <Route path="/workspaces/cyber/threat-modeling" element={<Security />} />
                <Route path="/workspaces/cyber/auto-remediation" element={<AutoFix />} />
                <Route path="/workspaces/finance" element={<Billing />} />
                <Route path="/workspaces/finance/scenarios" element={<Billing />} />
                <Route path="/workspaces/sre" element={<Monitoring />} />
                <Route path="/workspaces/sre/health" element={<Monitoring />} />
                <Route path="/workspaces/sre/sandbox" element={<Monitoring />} />
                <Route path="/workspaces/sre/reliability" element={<Monitoring />} />
                <Route path="/workspaces/archive" element={<Docs />} />
                <Route path="/workspaces/archive/time-travel" element={<Docs />} />
                <Route path="/workspaces/auditor" element={<Audit />} />
                <Route path="/workspaces/auditor/evidence" element={<Audit />} />
                <Route path="/workspaces/auditor/regulator" element={<Audit />} />
                <Route path="/workspaces/twins" element={<Research />} />
                <Route path="/workspaces/twins/enterprise" element={<Research />} />
                <Route path="/workspaces/twins/reality-mesh" element={<Research />} />

                {/* AI Hierarchy: /ai/* */}
                <Route path="/ai" element={<Navigate to="/ai/operations" replace />} />
                <Route path="/ai/operations" element={<AIOps />} />
                <Route path="/ai/os" element={<AIOS />} />
                <Route path="/ai/advanced" element={<AdvancedAI />} />
                <Route path="/ai/systems" element={<AdvancedSystems />} />
                <Route path="/ai/mlops" element={<MLOps />} />
                <Route path="/ai/copilot" element={<AICopilot />} />
                <Route path="/ai/personas" element={<AICopilot />} />
                <Route path="/ai/daemons" element={<AIOps />} />
                <Route path="/ai/trf" element={<AdvancedAI />} />
                <Route path="/ai/project-intelligence" element={<AdvancedAI />} />
                <Route path="/ai/drivers" element={<Integrations />} />
                <Route path="/ai/drivers/os" element={<AIOS />} />
                <Route path="/ai/drivers/package" element={<Integrations />} />
                <Route path="/ai/drivers/hardware" element={<AIOS />} />
                <Route path="/ai/drivers/software" element={<Integrations />} />
                <Route path="/ai/drivers/data" element={<Integrations />} />
                <Route path="/ai/drivers/research" element={<Research />} />
                <Route path="/ai/drivers/sandbox" element={<AIOS />} />
                <Route path="/ai/nas" element={<NeuralArchitectureSearch />} />
                <Route path="/ai/nas/experiments" element={<NeuralArchitectureSearch />} />
                <Route path="/ai/nas/simulator" element={<NAS />} />
                <Route path="/ai/security" element={<Security />} />
                <Route path="/ai/edge" element={<EdgeComputing />} />
                <Route path="/ai/workflows" element={<Workflows />} />
                <Route path="/ai/vision" element={<ComputerVision />} />
                <Route path="/ai/capsules" element={<CapsuleMarketplace />} />
                <Route path="/ai/capsules/ledger" element={<Audit />} />
                <Route path="/ai/capsules/lineage" element={<Audit />} />
                <Route path="/ai/capsules/operator-studio" element={<Workflows />} />
                <Route path="/ai/capsules/templates" element={<CapsuleMarketplace />} />
                <Route path="/ai/capsules/my-stack" element={<CapsuleMarketplace />} />
                <Route path="/ai/autofix" element={<AutoFix />} />
                <Route path="/ai/intents" element={<IntentProcessor />} />

                {/* Drivers & Integrations Hierarchy */}
                <Route path="/drivers" element={<Navigate to="/drivers/registry" replace />} />
                <Route path="/drivers/registry" element={<Integrations />} />
                <Route path="/drivers/sdk" element={<Integrations />} />
                <Route path="/drivers/publishing" element={<Integrations />} />
                <Route path="/drivers/integrations/productivity" element={<Integrations />} />
                <Route path="/drivers/integrations/code" element={<Integrations />} />
                <Route path="/drivers/integrations/finance" element={<Billing />} />
                <Route path="/drivers/integrations/research" element={<Research />} />
                <Route path="/drivers/integrations/legacy" element={<Tools />} />
                <Route path="/drivers/integrations/cloud" element={<Integrations />} />
                <Route path="/drivers/marketplace" element={<CapsuleMarketplace />} />
                <Route path="/drivers/packs" element={<Integrations />} />
                <Route path="/drivers/vertical-editions" element={<Integrations />} />
                <Route path="/drivers/enterprise-store" element={<CapsuleMarketplace />} />
                <Route path="/drivers/risk" element={<Security />} />

                {/* Integrations Hierarchy: /integrations/* */}
                <Route path="/integrations" element={<Integrations />} />
                <Route path="/integrations/api-connectors" element={<APIConnectors />} />
                <Route path="/integrations/office" element={<OfficeRealtime />} />
                <Route path="/integrations/microsoft" element={<OfficeRealtime />} />
                <Route path="/integrations/google" element={<OfficeRealtime />} />
                <Route path="/integrations/github" element={<Integrations />} />
                <Route path="/integrations/gitlab" element={<Integrations />} />
                <Route path="/integrations/cicd" element={<Workflows />} />

                {/* Data & Knowledge Hierarchy */}
                <Route path="/data" element={<Navigate to="/data/cir" replace />} />
                <Route path="/data/cir" element={<Docs />} />
                <Route path="/data/ledger" element={<Audit />} />
                <Route path="/data/capsules" element={<CapsuleMarketplace />} />
                <Route path="/data/artifacts" element={<CapsuleMarketplace />} />
                <Route path="/data/indices" element={<SearchEngine />} />
                <Route path="/data/indices/fulltext" element={<SearchEngine />} />
                <Route path="/data/indices/semantic" element={<SearchEngine />} />
                <Route path="/data/indices/graph" element={<SearchEngine />} />
                <Route path="/data/metrics" element={<Analytics />} />
                <Route path="/data/logs" element={<Analytics />} />
                <Route path="/data/traces" element={<Monitoring />} />
                <Route path="/data/archive" element={<Docs />} />
                <Route path="/data/backup" element={<Docs />} />
                <Route path="/data/legal-hold" element={<Audit />} />
                <Route path="/data/encryption" element={<Security />} />
                <Route path="/data/integrity" element={<Security />} />
                <Route path="/data/replication" element={<Monitoring />} />
                <Route path="/data/consistency" element={<Monitoring />} />

                {/* Governance & Security Hierarchy */}
                <Route path="/governance" element={<Navigate to="/governance/policy" replace />} />
                <Route path="/governance/policy" element={<Security />} />
                <Route path="/governance/policy/dsl" element={<Security />} />
                <Route path="/governance/policy/safety" element={<Security />} />
                <Route path="/governance/policy/simulator" element={<Security />} />
                <Route path="/governance/compliance" element={<Audit />} />
                <Route path="/governance/regulator" element={<Audit />} />
                <Route path="/governance/regulator/tenancy" element={<Audit />} />
                <Route path="/governance/regulator/evidence" element={<Audit />} />
                <Route path="/governance/identity" element={<Settings />} />
                <Route path="/governance/identity/auth" element={<Settings />} />
                <Route path="/governance/identity/rbac" element={<Settings />} />
                <Route path="/governance/data-protection" element={<Security />} />
                <Route path="/governance/data-protection/classification" element={<Security />} />
                <Route path="/governance/data-protection/residency" element={<Security />} />
                <Route path="/governance/data-protection/masking" element={<Security />} />
                <Route path="/governance/security/monitoring" element={<Security />} />
                <Route path="/governance/security/risk" element={<Security />} />
                <Route path="/governance/security/alignment" element={<Security />} />
                <Route path="/governance/security/incidents" element={<Security />} />
                <Route path="/governance/billing/usage" element={<Billing />} />
                <Route path="/governance/billing/budgets" element={<Billing />} />
                <Route path="/governance/billing/guardrails" element={<Billing />} />
                <Route path="/governance/billing/optimizer" element={<Billing />} />
                <Route path="/governance/billing/multi-tenant" element={<Billing />} />

                {/* Observability & Evidence */}
                <Route path="/observability" element={<Observability />} />
                <Route path="/observability/metrics" element={<Analytics />} />
                <Route path="/observability/slis" element={<Analytics />} />
                <Route path="/observability/logging" element={<Analytics />} />
                <Route path="/observability/tracing" element={<Monitoring />} />
                <Route path="/observability/record-auditor" element={<Audit />} />
                <Route path="/observability/evidence" element={<Audit />} />
                <Route path="/observability/audit-logs" element={<Audit />} />
                <Route path="/observability/retention" element={<Audit />} />
                <Route path="/observability/health" element={<Monitoring />} />
                <Route path="/observability/self-healing" element={<AutoFix />} />
                <Route path="/observability/runbooks" element={<Workflows />} />
                <Route path="/observability/dashboards" element={<Dashboard />} />
                <Route path="/observability/alerting" element={<Analytics />} />
                <Route path="/observability/replay" element={<Monitoring />} />
                <Route path="/observability/backtesting" element={<Monitoring />} />
                <Route path="/observability/events" element={<Observability />} />
                <Route path="/observability/suggestions" element={<Observability />} />

                {/* Operations & Infrastructure */}
                <Route path="/operations" element={<Navigate to="/operations/performance" replace />} />
                <Route path="/operations/performance" element={<Analytics />} />
                <Route path="/operations/scaling" element={<Monitoring />} />
                <Route path="/operations/driver-performance" element={<Monitoring />} />
                <Route path="/operations/backpressure" element={<Monitoring />} />
                <Route path="/operations/reliability" element={<Monitoring />} />
                <Route path="/operations/capacity" element={<Analytics />} />
                <Route path="/operations/deployment" element={<Monitoring />} />
                <Route path="/operations/deployment/local" element={<Monitoring />} />
                <Route path="/operations/deployment/cloud" element={<Monitoring />} />
                <Route path="/operations/deployment/hybrid" element={<EdgeComputing />} />
                <Route path="/operations/topology" element={<NetworkMonitoring />} />
                <Route path="/operations/storage" element={<Monitoring />} />
                <Route path="/operations/queues" element={<Monitoring />} />
                <Route path="/operations/hpc" element={<Research />} />
                <Route path="/operations/config" element={<Settings />} />
                <Route path="/operations/multi-region" element={<Monitoring />} />
                <Route path="/operations/upgrades" element={<Monitoring />} />
                <Route path="/operations/migration" element={<Monitoring />} />
                <Route path="/operations/rollback" element={<Monitoring />} />
                <Route path="/operations/failure" element={<Monitoring />} />
                <Route path="/operations/detection" element={<Monitoring />} />
                <Route path="/operations/recovery" element={<AutoFix />} />
                <Route path="/operations/data-protection" element={<Security />} />
                <Route path="/operations/security-incidents" element={<Security />} />
                <Route path="/operations/bc-dr" element={<Monitoring />} />

                {/* Analytics & Monitoring */}
                <Route path="/analytics" element={<Analytics />} />
                <Route path="/billing" element={<Billing />} />
                <Route path="/monitoring" element={<Monitoring />} />
                <Route path="/monitoring/metrics" element={<Analytics />} />
                <Route path="/monitoring/sli-slo" element={<Analytics />} />
                <Route path="/monitoring/tracing" element={<Monitoring />} />
                <Route path="/monitoring/health" element={<Monitoring />} />
                <Route path="/workspace/health" element={<WorkspaceHealth />} />
                <Route path="/workspace/orchestrator" element={<ProjectOrchestrator />} />
                <Route path="/projects/orchestrator" element={<ProjectOrchestrator />} />

                {/* Systems */}
                <Route path="/systems/security" element={<Security />} />
                <Route path="/systems/network" element={<NetworkMonitoring />} />
                <Route path="/network" element={<NetworkMonitoring />} />
                <Route path="/systems/edge" element={<EdgeComputing />} />
                <Route path="/systems/workflows" element={<Workflows />} />
                <Route path="/systems/nas" element={<NAS />} />

                {/* Search & Discovery */}
                <Route path="/search" element={<SearchEngine />} />

                {/* Audit & Compliance */}
                <Route path="/audit" element={<Audit />} />
                <Route path="/audit/logs" element={<Audit />} />
                <Route path="/audit/events" element={<Audit />} />
                <Route path="/audit/evidence-packs" element={<Audit />} />
                <Route path="/audit/retention" element={<Audit />} />

                {/* Vision Deck */}
                <Route path="/vision" element={<VisionDeck />} />
                <Route path="/future" element={<Navigate to="/vision" replace />} />
                <Route path="/future/:slug" element={<FutureDeck />} />

                {/* Roadmap & Risks Hierarchy */}
                <Route path="/roadmap" element={<Navigate to="/roadmap/overview" replace />} />
                <Route path="/roadmap/overview" element={<Docs />} />
                <Route path="/roadmap/phases" element={<Docs />} />
                <Route path="/roadmap/milestones" element={<Docs />} />
                <Route path="/roadmap/future" element={<FutureDeck />} />
                <Route path="/roadmap/risks" element={<Docs />} />
                <Route path="/roadmap/decisions" element={<Docs />} />
                <Route path="/roadmap/gaps" element={<Docs />} />
                <Route path="/roadmap/questions" element={<Docs />} />
                <Route path="/roadmap/spec" element={<SpecSheet />} />
                <Route path="/roadmap/future-capabilities" element={<FutureDeck />} />

                {/* Documentation Hierarchy: /docs/* */}
                <Route path="/docs" element={<Docs />} />
                <Route path="/docs/spec-sheet" element={<SpecSheet />} />
                <Route path="/docs/reference/capsules" element={<Docs />} />
                <Route path="/docs/reference/drivers" element={<Docs />} />
                <Route path="/docs/reference/policies" element={<Docs />} />
                <Route path="/docs/reference/evidence" element={<Docs />} />
                <Route path="/docs/api" element={<Docs />} />
                <Route path="/docs/:page" element={<Documentation />} />
                <Route path="/docs/index.html" element={<Documentation page="index" />} />
                <Route path="/docs/dashboard.html" element={<Documentation page="dashboard" />} />
                <Route path="/docs/projects.html" element={<Documentation page="projects" />} />
                <Route path="/docs/settings.html" element={<Documentation page="settings" />} />
                <Route path="/docs/billing.html" element={<Documentation page="billing" />} />
                <Route path="/docs/ai_capabilities.html" element={<Documentation page="ai_capabilities" />} />

                {/* Settings */}
                <Route path="/settings" element={<Settings />} />

                {/* Admin Panel - Requires admin role */}
                <Route
                  path="/admin"
                  element={
                    <RequireAdmin>
                      <Admin />
                    </RequireAdmin>
                  }
                />

                {/* Spec-driven pages (fills in blank/new routes) */}
                <Route path="*" element={<SpecPage />} />
              </Route>
            </Routes>
          </AppErrorBoundary>
        </SafeRouter>
      </AuthProvider>
      <Toaster position="top-right" />
    </QueryClientProvider>
  )
}

export default App
