import { useEffect } from 'react'
import { BrowserRouter, HashRouter, Navigate, Route, Routes, useLocation } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

import Layout from './components/Layout'
import { AppErrorBoundary } from './components/AppErrorBoundary'
import { Toaster } from './utils/toast'
import { applyTheme, defaultTheme } from './theme'

import Dashboard from './pages/Dashboard'
import Tasks from './pages/Tasks'
import Projects from './pages/Projects'
import Chat from './pages/Chat'
import Collaboration from './pages/Collaboration'
import Personalization from './pages/Personalization'
import SearchEngine from './pages/SearchEngine'

import Research from './pages/Research'
import Templates from './pages/Templates'
import Writer from './pages/Writer'
import Tools from './pages/Tools'

import AIOps from './pages/AIOps'
import AIOS from './pages/AIOS'
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
import Admin from './pages/Admin'

import Login from './pages/Login'
import Signup from './pages/Signup'
import SpecPage from './pages/SpecPage'

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
  return window.location.protocol === 'file:'
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

function RequireAuth({ children }: { children: JSX.Element }) {
  const location = useLocation()
  const token = typeof window !== 'undefined' ? window.localStorage.getItem('access_token') : null
  if (!token) return <Navigate to="/login" replace state={{ from: location.pathname }} />
  return children
}

function RequireAdmin({ children }: { children: JSX.Element }) {
  const location = useLocation()
  const userRaw = typeof window !== 'undefined' ? window.localStorage.getItem('user') : null
  const user = userRaw ? JSON.parse(userRaw) : null
  const isAdmin = user?.role === 'admin' || user?.is_admin === true
  if (!isAdmin) return <Navigate to="/" replace state={{ from: location.pathname }} />
  return children
}

function AppRoutes() {
  return (
    <Routes>
      {/* Public */}
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<Signup />} />

      {/* Protected */}
      <Route
        element={
          <RequireAuth>
            <Layout />
          </RequireAuth>
        }
      >
        {/* Mission Control */}
        <Route path="/" element={<Dashboard />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/tasks" element={<Tasks />} />
        <Route path="/projects" element={<Projects />} />
        <Route path="/chat" element={<Chat />} />
        <Route path="/collaboration" element={<Collaboration />} />
        <Route path="/personalization" element={<Personalization />} />
        <Route path="/search" element={<SearchEngine />} />

        {/* Workspaces */}
        <Route path="/research" element={<Research />} />
        <Route path="/work" element={<Navigate to="/work/templates" replace />} />
        <Route path="/work/templates" element={<Templates />} />
        <Route path="/work/writer" element={<Writer />} />
        <Route path="/work/tools" element={<Tools />} />

        {/* AI Fabric */}
        <Route path="/ai" element={<Navigate to="/ai/operations" replace />} />
        <Route path="/ai/operations" element={<AIOps />} />
        <Route path="/ai/os" element={<AIOS />} />
        <Route path="/ai/advanced" element={<AdvancedAI />} />
        <Route path="/ai/systems" element={<AdvancedSystems />} />
        <Route path="/ai/mlops" element={<MLOps />} />
        <Route path="/ai/nas" element={<NeuralArchitectureSearch />} />
        <Route path="/ai/nas/experiments" element={<NeuralArchitectureSearch />} />
        <Route path="/ai/nas/simulator" element={<NAS />} />
        <Route path="/ai/vision" element={<ComputerVision />} />
        <Route path="/ai/edge" element={<EdgeComputing />} />
        <Route path="/ai/intents" element={<IntentProcessor />} />
        <Route path="/ai/capsules" element={<CapsuleMarketplace />} />
        <Route path="/ai/autofix" element={<AutoFix />} />
        <Route path="/ai/workflows" element={<Workflows />} />

        {/* Drivers & Integrations */}
        <Route path="/integrations" element={<Integrations />} />
        <Route path="/integrations/api-connectors" element={<APIConnectors />} />
        <Route path="/integrations/office" element={<OfficeRealtime />} />

        {/* Observability & Evidence */}
        <Route path="/analytics" element={<Analytics />} />
        <Route path="/monitoring" element={<Monitoring />} />
        <Route path="/observability" element={<Observability />} />
        <Route path="/audit" element={<Audit />} />
        <Route path="/billing" element={<Billing />} />

        {/* Operations */}
        <Route path="/systems/network" element={<NetworkMonitoring />} />
        <Route path="/systems/security" element={<Security />} />

        {/* Platform health */}
        <Route path="/workspace/health" element={<WorkspaceHealth />} />
        <Route path="/workspace/orchestrator" element={<ProjectOrchestrator />} />

        {/* Vision & Docs */}
        <Route path="/vision" element={<VisionDeck />} />
        <Route path="/future/:slug" element={<FutureDeck />} />
        <Route path="/docs" element={<Docs />} />
        <Route path="/docs/spec-sheet" element={<SpecSheet />} />
        <Route path="/docs/:page" element={<Documentation />} />

        {/* Settings & Admin */}
        <Route path="/settings" element={<Settings />} />
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
  )
}

export default function App() {
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
          <AppRoutes />
        </AppErrorBoundary>
      </Router>
      <Toaster position="top-right" />
    </QueryClientProvider>
  )
}
