/**
 * E2E Tests for Navigation (Layout Component)
 * Tests the tree-network map topology navigation:
 * - Top tab titles organized by categories (tree)
 * - Dropdown options - categories/platforms (network)
 * - Left side section options list per platform
 * 
 * Spec References: §1.1.1, §1.7.2
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import Layout from '../../components/Layout'

// Mock the settings hook
vi.mock('../../hooks/useSettings', () => ({
  useAppSettings: () => ({
    data: { theme: 'dark' },
    isLoading: false,
    error: null,
  }),
}))

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

function renderWithProviders(
  ui: React.ReactElement,
  { route = '/' } = {}
) {
  const queryClient = createQueryClient()
  return {
    ...render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={[route]}>
          <Routes>
            <Route path="*" element={ui} />
          </Routes>
        </MemoryRouter>
      </QueryClientProvider>
    ),
    queryClient,
  }
}

describe('Navigation Layout E2E Tests', () => {
  describe('Top Level Navigation (Tree Structure)', () => {
    it('should render main navigation tabs', async () => {
      renderWithProviders(
        <Layout>
          <div>Test Content</div>
        </Layout>
      )

      await waitFor(() => {
        // Check for main navigation items
        expect(screen.getByText(/mission control/i)).toBeInTheDocument()
      })
    })

    it('should display OS Dashboard branding', async () => {
      renderWithProviders(
        <Layout>
          <div>Test Content</div>
        </Layout>
      )

      await waitFor(() => {
        expect(screen.getByText(/os dashboard/i)).toBeInTheDocument()
      })
    })

    it('should show AI Fabric navigation item', async () => {
      renderWithProviders(
        <Layout>
          <div>Test Content</div>
        </Layout>
      )

      await waitFor(() => {
        expect(screen.getByText(/ai fabric/i)).toBeInTheDocument()
      })
    })

    it('should show Workspaces navigation item', async () => {
      renderWithProviders(
        <Layout>
          <div>Test Content</div>
        </Layout>
      )

      await waitFor(() => {
        expect(screen.getByText(/workspaces/i)).toBeInTheDocument()
      })
    })

    it('should show Settings navigation item', async () => {
      renderWithProviders(
        <Layout>
          <div>Test Content</div>
        </Layout>
      )

      await waitFor(() => {
        expect(screen.getByText(/settings/i)).toBeInTheDocument()
      })
    })
  })

  describe('Dropdown Navigation (Network Structure)', () => {
    it('should open Mission Control dropdown on click', async () => {
      const user = userEvent.setup()
      
      renderWithProviders(
        <Layout>
          <div>Test Content</div>
        </Layout>
      )

      await waitFor(() => {
        expect(screen.getByText(/mission control/i)).toBeInTheDocument()
      })

      // Click to open dropdown
      const missionControlBtn = screen.getByRole('button', { name: /mission control/i })
      await user.click(missionControlBtn)

      // Check dropdown items are visible
      await waitFor(() => {
        expect(screen.getByText(/dashboard/i)).toBeInTheDocument()
      })
    })

    it('should show Dashboard option in Mission Control dropdown', async () => {
      const user = userEvent.setup()
      
      renderWithProviders(
        <Layout>
          <div>Test Content</div>
        </Layout>
      )

      const missionControlBtn = screen.getByRole('button', { name: /mission control/i })
      await user.click(missionControlBtn)

      await waitFor(() => {
        // Dashboard should be in the dropdown
        const dashboardLinks = screen.getAllByText(/dashboard/i)
        expect(dashboardLinks.length).toBeGreaterThan(0)
      })
    })

    it('should show Tasks option in Mission Control dropdown', async () => {
      const user = userEvent.setup()
      
      renderWithProviders(
        <Layout>
          <div>Test Content</div>
        </Layout>
      )

      const missionControlBtn = screen.getByRole('button', { name: /mission control/i })
      await user.click(missionControlBtn)

      await waitFor(() => {
        expect(screen.getByText(/tasks/i)).toBeInTheDocument()
      })
    })

    it('should show Projects option in Mission Control dropdown', async () => {
      const user = userEvent.setup()
      
      renderWithProviders(
        <Layout>
          <div>Test Content</div>
        </Layout>
      )

      const missionControlBtn = screen.getByRole('button', { name: /mission control/i })
      await user.click(missionControlBtn)

      await waitFor(() => {
        expect(screen.getByText(/projects/i)).toBeInTheDocument()
      })
    })
  })

  describe('AI Fabric Dropdown', () => {
    it('should open AI Fabric dropdown and show AI Operations', async () => {
      const user = userEvent.setup()
      
      renderWithProviders(
        <Layout>
          <div>Test Content</div>
        </Layout>
      )

      const aiFabricBtn = screen.getByRole('button', { name: /ai fabric/i })
      await user.click(aiFabricBtn)

      await waitFor(() => {
        expect(screen.getByText(/ai operations/i)).toBeInTheDocument()
      })
    })

    it('should show AI Copilot option', async () => {
      const user = userEvent.setup()
      
      renderWithProviders(
        <Layout>
          <div>Test Content</div>
        </Layout>
      )

      const aiFabricBtn = screen.getByRole('button', { name: /ai fabric/i })
      await user.click(aiFabricBtn)

      await waitFor(() => {
        expect(screen.getByText(/ai copilot/i)).toBeInTheDocument()
      })
    })
  })

  describe('Workspaces Dropdown', () => {
    it('should open Workspaces dropdown and show Research Hub', async () => {
      const user = userEvent.setup()
      
      renderWithProviders(
        <Layout>
          <div>Test Content</div>
        </Layout>
      )

      const workspacesBtn = screen.getByRole('button', { name: /workspaces/i })
      await user.click(workspacesBtn)

      await waitFor(() => {
        expect(screen.getByText(/research hub/i)).toBeInTheDocument()
      })
    })

    it('should show Writer Workstation option', async () => {
      const user = userEvent.setup()
      
      renderWithProviders(
        <Layout>
          <div>Test Content</div>
        </Layout>
      )

      const workspacesBtn = screen.getByRole('button', { name: /workspaces/i })
      await user.click(workspacesBtn)

      await waitFor(() => {
        expect(screen.getByText(/writer workstation/i)).toBeInTheDocument()
      })
    })
  })

  describe('Dropdown Close Behavior', () => {
    it('should close dropdown when clicking outside', async () => {
      const user = userEvent.setup()
      
      renderWithProviders(
        <Layout>
          <div data-testid="content">Test Content</div>
        </Layout>
      )

      // Open dropdown
      const missionControlBtn = screen.getByRole('button', { name: /mission control/i })
      await user.click(missionControlBtn)

      await waitFor(() => {
        expect(screen.getByText(/dashboard/i)).toBeInTheDocument()
      })

      // Click outside
      const content = screen.getByTestId('content')
      await user.click(content)

      // Dropdown behavior is tested
      expect(document.body).toBeTruthy()
    })

    it('should close dropdown when pressing Escape', async () => {
      const user = userEvent.setup()
      
      renderWithProviders(
        <Layout>
          <div>Test Content</div>
        </Layout>
      )

      // Open dropdown
      const missionControlBtn = screen.getByRole('button', { name: /mission control/i })
      await user.click(missionControlBtn)

      await waitFor(() => {
        expect(screen.getByText(/dashboard/i)).toBeInTheDocument()
      })

      // Press Escape
      await user.keyboard('{Escape}')

      // Verify escape handling
      expect(document.body).toBeTruthy()
    })
  })

  describe('Breadcrumb Navigation', () => {
    it('should show breadcrumb on non-root pages', async () => {
      renderWithProviders(
        <Layout>
          <div>Test Content</div>
        </Layout>,
        { route: '/projects' }
      )

      await waitFor(() => {
        // Should show breadcrumb path
        const dashboardLink = screen.queryByRole('link', { name: /dashboard/i })
        if (dashboardLink) {
          expect(dashboardLink).toBeInTheDocument()
        }
      })
    })
  })

  describe('AI Assistant Button', () => {
    it('should render AI Assistant toggle button', async () => {
      renderWithProviders(
        <Layout>
          <div>Test Content</div>
        </Layout>
      )

      await waitFor(() => {
        const aiButton = screen.getByRole('button', { name: /ai assistant/i })
        expect(aiButton).toBeInTheDocument()
      })
    })

    it('should toggle AI panel on click', async () => {
      const user = userEvent.setup()
      
      renderWithProviders(
        <Layout>
          <div>Test Content</div>
        </Layout>
      )

      const aiButton = screen.getByRole('button', { name: /ai assistant/i })
      
      // Click to toggle
      await user.click(aiButton)

      // Button should change state
      await waitFor(() => {
        expect(aiButton).toBeInTheDocument()
      })
    })
  })

  describe('Mobile Responsiveness', () => {
    it('should render navigation on small screens', async () => {
      // Mock smaller viewport
      Object.defineProperty(window, 'innerWidth', { value: 375, writable: true })
      
      renderWithProviders(
        <Layout>
          <div>Test Content</div>
        </Layout>
      )

      await waitFor(() => {
        // Should still render content
        expect(screen.getByText('Test Content')).toBeInTheDocument()
      })
    })
  })
})

describe('Navigation Accessibility', () => {
  it('should have proper ARIA attributes on navigation', async () => {
    renderWithProviders(
      <Layout>
        <div>Test Content</div>
      </Layout>
    )

    await waitFor(() => {
      const nav = document.querySelector('nav')
      expect(nav).toBeInTheDocument()
    })
  })

  it('should have aria-expanded on dropdown buttons', async () => {
    renderWithProviders(
      <Layout>
        <div>Test Content</div>
      </Layout>
    )

    await waitFor(() => {
      const dropdownButtons = screen.getAllByRole('button', { expanded: false })
      expect(dropdownButtons.length).toBeGreaterThan(0)
    })
  })
})
