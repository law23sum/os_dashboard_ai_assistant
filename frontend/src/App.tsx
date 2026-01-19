import { BrowserRouter, HashRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useEffect } from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from './utils/toast'
import { AuthProvider } from './auth/AuthContext'
import Layout from './components/Layout'
import { applyTheme, defaultTheme } from './theme'
import { AppErrorBoundary } from './components/AppErrorBoundary'

// Core Pages
import Dashboard from './pages/Dashboard'
import Projects from './pages/Projects'
import Tasks from './pages/Tasks'
import Chat from './pages/Chat'
import Settings from './pages/Settings'

// Auth Pages
import Login from './pages/Login'
import Signup from './pages/Signup'

// AI Pages
import AIOps from './pages/AIOps'
import AICopilot from './pages/AICopilot'
import AutoFix from './pages/AutoFix'
import CapsuleMarketplace from './pages/CapsuleMarketplace'

// Operations & Audit
import Operations from './pages/Operations'
import Audit from './pages/Audit'

// Research & Docs
import Research from './pages/Research'
import Integrations from './pages/Integrations'
import Docs from './pages/Docs'

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
      <AuthProvider>
        <Router basename={useHashRouter ? undefined : basePath}>
          <AppErrorBoundary>
            <Routes>
              {/* Auth Routes (No Layout) */}
              <Route path="/login" element={<Login />} />
              <Route path="/signup" element={<Signup />} />

              {/* All other routes with Layout */}
              <Route element={<Layout />}>
                {/* Core */}
                <Route path="/" element={<Dashboard />} />
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/projects" element={<Projects />} />
                <Route path="/tasks" element={<Tasks />} />
                <Route path="/chat" element={<Chat />} />

                {/* AI Hub */}
                <Route path="/ai" element={<Navigate to="/ai/ops" replace />} />
                <Route path="/ai/ops" element={<AIOps />} />
                <Route path="/ai/copilot" element={<AICopilot />} />
                <Route path="/ai/autofix" element={<AutoFix />} />
                <Route path="/ai/capsules" element={<CapsuleMarketplace />} />

                {/* Operations & Compliance */}
                <Route path="/operations" element={<Operations />} />
                <Route path="/monitoring" element={<Operations />} />
                <Route path="/analytics" element={<Operations />} />
                <Route path="/audit" element={<Audit />} />

                {/* Research & Content */}
                <Route path="/research" element={<Research />} />
                <Route path="/integrations" element={<Integrations />} />

                {/* Documentation */}
                <Route path="/docs" element={<Docs />} />
                <Route path="/docs/*" element={<Docs />} />

                {/* Settings */}
                <Route path="/settings" element={<Settings />} />

                {/* Legacy redirects */}
                <Route path="/ai-ops" element={<Navigate to="/ai/ops" replace />} />
                <Route path="/ai/operations" element={<Navigate to="/ai/ops" replace />} />
                <Route path="/mlops" element={<Navigate to="/ai/ops" replace />} />
                <Route path="/billing" element={<Navigate to="/settings" replace />} />
                <Route path="/security" element={<Navigate to="/settings" replace />} />

                {/* Catch-all */}
                <Route path="*" element={<Navigate to="/" replace />} />
              </Route>
            </Routes>
          </AppErrorBoundary>
        </Router>
        <Toaster position="top-right" />
      </AuthProvider>
    </QueryClientProvider>
  )
}

export default App
