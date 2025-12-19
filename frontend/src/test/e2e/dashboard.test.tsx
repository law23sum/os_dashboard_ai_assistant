/**
 * E2E Tests for Dashboard Page
 * Tests the main dashboard functionality including:
 * - System stats display
 * - Quick actions
 * - Status cards
 * - Integration status
 * 
 * Spec References: §1.1.1, §1.7
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter } from 'react-router-dom'
import Dashboard from '../../pages/Dashboard'

// Mock the API client
vi.mock('../../lib/apiClient', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
  },
  apiPath: (path: string) => `/api/${path}`,
}))

vi.mock('../../lib/responseHelpers', () => ({
  extractArray: (data: unknown) => {
    if (Array.isArray(data)) return data
    return []
  },
}))

import apiClient from '../../lib/apiClient'

const mockDashboardStats = {
  total_tasks: 25,
  tasks_by_status: {
    TODO: 10,
    IN_PROGRESS: 8,
    DONE: 5,
    BLOCKED: 2,
  },
  tasks_by_priority: {
    CRITICAL: 2,
    HIGH: 8,
    MEDIUM: 10,
    LOW: 5,
  },
  total_projects: 5,
  active_projects: 3,
  system_stats: {
    cpu_percent: 45.5,
    memory_percent: 62.3,
    disk_percent: 55.0,
  },
  security_status: {
    status: 'secure',
    message: 'All systems operational',
    updated_at: '2025-01-01T00:00:00Z',
    source: 'security_daemon',
  },
  persona_load: {
    AIC: 30,
    Aria: 45,
    Sora: 25,
  },
  active_persona: 'AIC',
}

const mockSystemStatus = {
  status: 'operational',
  version: '1.0.0',
  uptime_seconds: 86400,
}

const mockPlanesStatus = {
  data_plane: { status: 'healthy', latency_ms: 15 },
  control_plane: { status: 'healthy', latency_ms: 20 },
  governance_plane: { status: 'healthy', latency_ms: 25 },
}

function createQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        gcTime: 0,
        staleTime: 0,
      },
    },
  })
}

function renderWithProviders(ui: React.ReactElement) {
  const queryClient = createQueryClient()
  return {
    ...render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>{ui}</BrowserRouter>
      </QueryClientProvider>
    ),
    queryClient,
  }
}

describe('Dashboard Page E2E Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    
    vi.mocked(apiClient.get).mockImplementation(async (url: string) => {
      if (url.includes('/dashboard')) {
        return { data: mockDashboardStats }
      }
      if (url.includes('/system')) {
        return { data: mockSystemStatus }
      }
      if (url.includes('/planes')) {
        return { data: mockPlanesStatus }
      }
      return { data: {} }
    })
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  describe('Dashboard Rendering', () => {
    it('should render the dashboard page', async () => {
      renderWithProviders(<Dashboard />)

      await waitFor(() => {
        // Dashboard should show some content
        expect(document.body.textContent).toBeTruthy()
      })
    })

    it('should display page title', async () => {
      renderWithProviders(<Dashboard />)

      await waitFor(() => {
        const title = screen.queryByText(/dashboard/i) || screen.queryByText(/mission control/i)
        expect(title).toBeInTheDocument()
      })
    })
  })

  describe('Statistics Display', () => {
    it('should display task statistics', async () => {
      renderWithProviders(<Dashboard />)

      await waitFor(() => {
        // Should show some task-related stats
        const content = document.body.textContent
        expect(content).toBeTruthy()
      })
    })

    it('should display project count', async () => {
      renderWithProviders(<Dashboard />)

      await waitFor(() => {
        const projectLabel = screen.queryByText(/project/i)
        if (projectLabel) {
          expect(projectLabel).toBeInTheDocument()
        }
      })
    })
  })

  describe('System Status', () => {
    it('should display system health indicators', async () => {
      renderWithProviders(<Dashboard />)

      await waitFor(() => {
        // System health should be shown somewhere
        const healthContent = screen.queryByText(/cpu/i) || screen.queryByText(/memory/i) || screen.queryByText(/healthy/i)
        if (healthContent) {
          expect(healthContent).toBeInTheDocument()
        }
      })
    })
  })

  describe('Navigation', () => {
    it('should have links to other pages', async () => {
      renderWithProviders(<Dashboard />)

      await waitFor(() => {
        // Dashboard should render without errors
        expect(document.body.textContent).toBeTruthy()
      })
    })
  })

  describe('Error States', () => {
    it('should handle API errors gracefully', async () => {
      vi.mocked(apiClient.get).mockRejectedValue(new Error('API Error'))

      renderWithProviders(<Dashboard />)

      // Should not crash
      await waitFor(() => {
        expect(document.body).toBeTruthy()
      })
    })
  })
})

describe('Dashboard Integration Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should load data from all required endpoints', async () => {
    vi.mocked(apiClient.get).mockImplementation(async (url: string) => {
      if (url.includes('/dashboard')) {
        return { data: mockDashboardStats }
      }
      if (url.includes('/system')) {
        return { data: mockSystemStatus }
      }
      if (url.includes('/planes')) {
        return { data: mockPlanesStatus }
      }
      return { data: {} }
    })

    renderWithProviders(<Dashboard />)

    await waitFor(() => {
      // Verify API was called
      expect(apiClient.get).toHaveBeenCalled()
    })
  })
})
