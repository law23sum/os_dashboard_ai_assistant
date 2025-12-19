import { BrowserRouter, HashRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useEffect } from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from './utils/toast'
import Layout from './components/Layout'
import Login from './pages/Login'
import Signup from './pages/Signup'
import Admin from './pages/Admin'
import Research from './pages/Research'
import Dashboard from './pages/Dashboard'
import Tasks from './pages/Tasks'
import Projects from './pages/Projects'
import Chat from './pages/Chat'
import Integrations from './pages/Integrations'
import Settings from './pages/Settings'
import AIOps from './pages/AIOps'
import Analytics from './pages/Analytics'
import MLOps from './pages/MLOps'
import Personalization from './pages/Personalization'
import Collaboration from './pages/Collaboration'
import Monitoring from './pages/Monitoring'
import Docs from './pages/Docs'
import Documentation from './pages/Documentation'
import Templates from './pages/Templates'
import Writer from './pages/Writer'
import SpecSheet from './pages/SpecSheet'
import APIConnectors from './pages/APIConnectors'
import AICopilot from './pages/AICopilot'
import OfficeRealtime from './pages/OfficeRealtime'
import AIOS from './pages/AIOS'
import AdvancedAI from './pages/AdvancedAI'
import Audit from './pages/Audit'
import SearchEngine from './pages/SearchEngine'
import ComputerVision from './pages/ComputerVision'
import Tools from './pages/Tools'
import { applyTheme, defaultTheme } from './theme'
import Security from './pages/Security'
import NetworkMonitoring from './pages/NetworkMonitoring'
import EdgeComputing from './pages/EdgeComputing'
import Workflows from './pages/Workflows'
import NAS from './pages/NAS'
import AdvancedSystems from './pages/AdvancedSystems'
import Billing from './pages/Billing'
import FutureDeck from './pages/FutureDeck'
import NeuralArchitectureSearch from './pages/NeuralArchitectureSearch'
import VisionDeck from './pages/VisionDeck'
import Observability from './pages/Observability'
import CapsuleMarketplace from './pages/CapsuleMarketplace'
import AutoFix from './pages/AutoFix'
import IntentProcessor from './pages/IntentProcessor'
import WorkspaceHealth from './pages/WorkspaceHealth'
import Login from './pages/Login'
import Signup from './pages/Signup'
import Admin from './pages/Admin'
import ProjectOrchestrator from './pages/ProjectOrchestrator'
import { AppErrorBoundary } from './components/AppErrorBoundary'
import { AuthProvider } from './auth/AuthContext'
import { RequireAuth } from './auth/RequireAuth'
import { RequireAdmin } from './auth/RequireAdmin'
import ProtectedRoute from './components/ProtectedRoute'

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
    if (baseHref) {
      return normalizeBasePath(baseHref)
    }
  }
  const envBase = import.meta.env.BASE_URL || '/'
  return normalizeBasePath(envBase)
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

const shouldUseHashRouter = (): boolean => {
  if (typeof window === 'undefined') return false
  // When the Electron shell loads a local bundle via `loadFile`, `file://` URLs
  // include the full filesystem pathname (e.g. `/.../index.html`) which breaks
  // BrowserRouter route matching and can render a blank window.
  return window.location.protocol === 'file:'
}

function App() {
  useEffect(() => {
    applyTheme(defaultTheme)
  }, [])
  const basePath = resolveRouterBasePath()
  const useHashRouter = shouldUseHashRouter()
  const Router = useHashRouter ? HashRouter : BrowserRouter

  return (
    <QueryClientProvider client={queryClient}>
      <Router basename={useHashRouter ? undefined : basePath}>
        <AppErrorBoundary>
          <Routes>
            {/* Public Routes (No Layout) */}
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />

            {/* Protected Routes (With Layout) */}
            <Route element={<ProtectedRoute><Layout /></ProtectedRoute>}>
              {/* Root & Core Pages */}
              <Route path="/" element={<Dashboard />} />
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

            {/* Root & Core Pages */}
            <Route path="/" element={<Dashboard />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/tasks" element={<Tasks />} />
            <Route path="/projects" element={<Projects />} />
            <Route path="/chat" element={<Chat />} />
            <Route path="/research" element={<Research />} />
      <AuthProvider>
        <Router basename={useHashRouter ? undefined : basePath}>
          <AppErrorBoundary>
            <Routes>
              {/* Public */}
              <Route path="/login" element={<Login />} />
              <Route path="/signup" element={<Signup />} />

              {/* Protected app */}
              <Route element={<RequireAuth><Layout /></RequireAuth>}>
                {/* Root & Core Pages */}
                <Route path="/" element={<Dashboard />} />
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/tasks" element={<Tasks />} />
                <Route path="/projects" element={<Projects />} />
                <Route path="/chat" element={<Chat />} />
                <Route path="/research" element={<Research />} />

            {/* Work & Writing Hierarchy: /work/* */}
            <Route path="/work" element={<Navigate to="/work/templates" replace />} />
            <Route path="/work/templates" element={<Templates />} />
            <Route path="/work/writer" element={<Writer />} />
            <Route path="/work/tools" element={<Tools />} />
            {/* Legacy redirects for backward compatibility */}
            <Route path="/templates" element={<Navigate to="/work/templates" replace />} />
            <Route path="/writer" element={<Navigate to="/work/writer" replace />} />
            <Route path="/tools" element={<Navigate to="/work/tools" replace />} />

            {/* AI Hierarchy: /ai/* */}
            <Route path="/ai" element={<Navigate to="/ai/operations" replace />} />
            <Route path="/ai/operations" element={<AIOps />} />
            <Route path="/ai/os" element={<AIOS />} />
            <Route path="/ai/advanced" element={<AdvancedAI />} />
            <Route path="/ai/systems" element={<AdvancedSystems />} />
            <Route path="/ai/mlops" element={<MLOps />} />
            <Route path="/ai/copilot" element={<AICopilot />} />
            <Route path="/ai/nas" element={<NeuralArchitectureSearch />} />
            <Route path="/ai/nas/experiments" element={<NeuralArchitectureSearch />} />
            <Route path="/ai/nas/simulator" element={<NAS />} />
            <Route path="/ai/security" element={<Security />} />
            <Route path="/ai/edge" element={<EdgeComputing />} />
            <Route path="/ai/edge-computing" element={<EdgeComputing />} />
            <Route path="/ai/workflows" element={<Workflows />} />
            <Route path="/ai/vision" element={<ComputerVision />} />
            <Route path="/ai/capsules" element={<CapsuleMarketplace />} />
            <Route path="/ai/autofix" element={<AutoFix />} />
            <Route path="/ai/intents" element={<IntentProcessor />} />
            {/* Legacy redirects for backward compatibility */}
            <Route path="/ai-ops" element={<Navigate to="/ai/operations" replace />} />
            <Route path="/ai-os" element={<Navigate to="/ai/os" replace />} />
            <Route path="/advanced-ai" element={<Navigate to="/ai/advanced" replace />} />
            <Route path="/ai-systems" element={<Navigate to="/ai/systems" replace />} />
            <Route path="/mlops" element={<Navigate to="/ai/mlops" replace />} />
            <Route path="/nas" element={<Navigate to="/ai/nas" replace />} />
            <Route path="/nas/experiments" element={<Navigate to="/ai/nas" replace />} />
            <Route path="/nas/simulator" element={<Navigate to="/ai/nas/simulator" replace />} />
            <Route path="/neural-architecture" element={<Navigate to="/ai/nas" replace />} />
            <Route path="/security" element={<Navigate to="/ai/security" replace />} />
            <Route path="/edge-computing" element={<Navigate to="/ai/edge-computing" replace />} />
            <Route path="/workflows" element={<Navigate to="/ai/workflows" replace />} />
            <Route path="/computer-vision" element={<ComputerVision />} />

            {/* Integrations Hierarchy: /integrations/* */}
            <Route path="/integrations" element={<Integrations />} />
            <Route path="/integrations/api-connectors" element={<APIConnectors />} />
            <Route path="/integrations/office" element={<OfficeRealtime />} />
            <Route path="/integrations/office-realtime" element={<OfficeRealtime />} />
            {/* Legacy redirect for backward compatibility */}
            <Route path="/api-connectors" element={<Navigate to="/integrations/api-connectors" replace />} />

            {/* Observability (v1000) */}
            <Route path="/observability" element={<Observability />} />
            <Route path="/workspace/health" element={<WorkspaceHealth />} />
            <Route path="/workspace/orchestrator" element={<ProjectOrchestrator />} />
            <Route path="/projects/orchestrator" element={<ProjectOrchestrator />} />

            {/* Analytics & Monitoring Hierarchy: /monitoring/* */}
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/billing" element={<Billing />} />
            <Route path="/monitoring" element={<Monitoring />} />

            {/* Search & Discovery */}
            <Route path="/search" element={<SearchEngine />} />
            <Route path="/search-engine" element={<SearchEngine />} />

            {/* Audit & Compliance */}
            <Route path="/audit" element={<Audit />} />

            {/* Collaboration & Personalization */}
            <Route path="/collaboration" element={<Collaboration />} />
            <Route path="/personalization" element={<Personalization />} />

            {/* Documentation Hierarchy: /docs/* */}
            <Route path="/docs" element={<Docs />} />
            <Route path="/docs/spec-sheet" element={<SpecSheet />} />
            <Route path="/docs/:page" element={<Documentation />} />
            {/* Direct HTML page routes for backward compatibility */}
            <Route path="/docs/index.html" element={<Documentation page="index" />} />
            <Route path="/docs/dashboard.html" element={<Documentation page="dashboard" />} />
            <Route path="/docs/projects.html" element={<Documentation page="projects" />} />
            <Route path="/docs/settings.html" element={<Documentation page="settings" />} />
            <Route path="/docs/billing.html" element={<Documentation page="billing" />} />
            <Route path="/docs/ai_capabilities.html" element={<Documentation page="ai_capabilities" />} />

            {/* Systems */}
            <Route path="/systems/security" element={<Security />} />
            <Route path="/systems/network" element={<NetworkMonitoring />} />
            <Route path="/network" element={<NetworkMonitoring />} />
            <Route path="/systems/edge" element={<EdgeComputing />} />
            <Route path="/systems/workflows" element={<Workflows />} />
            <Route path="/systems/nas" element={<NAS />} />
            <Route path="/vision" element={<VisionDeck />} />
            <Route path="/vision-deck" element={<Navigate to="/vision" replace />} />
            <Route path="/future" element={<Navigate to="/vision" replace />} />
            <Route path="/future/:slug" element={<FutureDeck />} />

            {/* Roadmap & Risks Hierarchy: /roadmap/* */}
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

            {/* Settings */}
            <Route path="/settings" element={<Settings />} />

                {/* Admin */}
                <Route
                  path="/admin"
                  element={
                    <RequireAdmin>
                      <Admin />
                    </RequireAdmin>
                  }
                />

                {/* Catch-all */}
                <Route path="*" element={<Navigate to="/" replace />} />
              </Route>
            </Routes>
          </AppErrorBoundary>
        </Router>
      </AuthProvider>
            {/* Admin Panel - Requires admin role */}
            <Route path="/admin" element={<ProtectedRoute requireAdmin><Admin /></ProtectedRoute>} />

            {/* Catch-all */}
            <Route path="*" element={<Navigate to="/" replace />} />
            </Route>
          </Routes>
        </AppErrorBoundary>
      </Router>
      <Toaster position="top-right" />
    </QueryClientProvider>
  )
}

export default App