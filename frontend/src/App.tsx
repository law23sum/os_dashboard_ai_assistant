import { useEffect, useMemo, useState } from 'react'
import { BrowserRouter, HashRouter, Routes, Route, Outlet } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

import Layout from './components/Layout'
import { AppErrorBoundary } from './components/AppErrorBoundary'
import { Toaster } from './utils/toast'
import { applyTheme, defaultTheme } from './theme'

// Pages
import Login from './pages/Login'
import Signup from './pages/Signup'
import Admin from './pages/Admin'
import Documentation from './pages/Documentation'
import ResponsesChat from './pages/ResponsesChat'
import FutureDeck from './pages/FutureDeck'
import PmsProjectDetail from './pages/pms/PmsProjectDetail'

// Auth
import { AuthProvider } from './auth/AuthContext'
import { RequireAuth } from './auth/RequireAuth'
import { RequireAdmin } from './auth/RequireAdmin'
import { IANavigationProvider } from './navigation/iaContext'
import NavRouteRenderer from './navigation/NavRouteRenderer'

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
    if (typeof window.history === 'undefined' || typeof window.history.pushState === 'undefined') {
      return true
    }
    if (
      window.location.protocol === 'http:' &&
      window.location.hostname !== 'localhost' &&
      window.location.hostname !== '127.0.0.1'
    ) {
      return false
    }
  } catch (e) {
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

function SafeRouter({ children, useHashRouter, basePath }: {
  children: React.ReactNode
  useHashRouter: boolean
  basePath: string
}) {
  const [shouldUseHash, setShouldUseHash] = useState(useHashRouter)

  useEffect(() => {
    if (!useHashRouter && typeof window !== 'undefined') {
      try {
        const testState = { test: true }
        window.history.replaceState(testState, '', window.location.href)
        setShouldUseHash(false)
      } catch (error) {
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

function LayoutWrapper() {
  return (
    <IANavigationProvider>
      <Layout>
        <Outlet />
      </Layout>
    </IANavigationProvider>
  )
}

function App() {
  useEffect(() => {
    applyTheme(defaultTheme)
  }, [])

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
                <Route
                  path="/admin"
                  element={
                    <RequireAdmin>
                      <Admin />
                    </RequireAdmin>
                  }
                />
                <Route path="/chat/responses" element={<ResponsesChat />} />
                <Route path="/pms/projects/:projectId" element={<PmsProjectDetail />} />
                <Route path="/future/:slug" element={<FutureDeck />} />
                <Route path="/docs/:page" element={<Documentation />} />
                <Route path="/docs/index.html" element={<Documentation page="index" />} />
                <Route path="/docs/dashboard.html" element={<Documentation page="dashboard" />} />
                <Route path="/docs/projects.html" element={<Documentation page="projects" />} />
                <Route path="/docs/settings.html" element={<Documentation page="settings" />} />
                <Route path="/docs/billing.html" element={<Documentation page="billing" />} />
                <Route path="/docs/ai_capabilities.html" element={<Documentation page="ai_capabilities" />} />

                {/* IA-driven routes (platform/category/feature resolution) */}
                <Route path="*" element={<NavRouteRenderer />} />
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
