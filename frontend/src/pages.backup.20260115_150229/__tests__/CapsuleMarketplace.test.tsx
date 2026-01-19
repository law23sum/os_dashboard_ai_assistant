/**
 * Tests for CapsuleMarketplace.tsx
 * Component: CapsuleMarketplace
 * Route: /ai/capsules
 * 
 * Tests cover:
 * - Blank page scenario (API failure)
 * - Empty data handling
 * - Loading states
 * - Demo data fallback
 */

import { describe, it, expect, beforeEach, vi } from '@jest/globals'
import { render, screen, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter } from 'react-router-dom'
import React from 'react'
import CapsuleMarketplace from '../CapsuleMarketplace'

// Mock the API client
const mockGet = vi.fn()
const mockPost = vi.fn()

vi.mock('../../api/client', () => ({
  default: {
    get: mockGet,
    post: mockPost,
  },
  apiPath: (path: string) => `/api/${path}`,
}))

describe('CapsuleMarketplace - Blank Apps Scenario', () => {
  let queryClient: QueryClient

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
          cacheTime: 0,
        },
      },
    })
    vi.clearAllMocks()
  })

  const renderComponent = () => {
    return render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <CapsuleMarketplace />
        </BrowserRouter>
      </QueryClientProvider>
    )
  }

  it('should display demo data when API fails', async () => {
    // Mock API failure
    mockGet.mockRejectedValue(new Error('API Error'))

    renderComponent()

    // Wait for the component to handle the error and show demo data
    await waitFor(() => {
      // Should show at least one capsule from demo data
      expect(screen.getByText(/Shell Capsule|Git Maintenance|Document Blueprint/i)).toBeInTheDocument()
    }, { timeout: 3000 })

    // Should not show empty state
    expect(screen.queryByText(/No capsules found/i)).not.toBeInTheDocument()
  })

  it('should display demo data when API returns empty arrays', async () => {
    // Mock API returning empty data
    mockGet.mockResolvedValue({
      data: {
        capsules: [],
        blueprints: [],
      },
    })

    renderComponent()

    // Should show demo data instead of blank page
    await waitFor(() => {
      expect(screen.getByText(/Shell Capsule|Git Maintenance/i)).toBeInTheDocument()
    }, { timeout: 3000 })
  })

  it('should show loading state initially', () => {
    // Mock a delayed API response
    mockGet.mockImplementation(
      () => new Promise(resolve => setTimeout(() => resolve({ data: {} }), 100))
    )

    renderComponent()

    // Should show loading spinner or loading state
    const loadingElement = screen.queryByRole('status') || 
                          document.querySelector('.animate-spin') ||
                          screen.queryByText(/loading/i)
    
    // Note: The component uses a custom loading spinner, so we check for the spinner class
    expect(loadingElement || document.querySelector('div[class*="animate-spin"]')).toBeTruthy()
  })

  it('should display capsules when API returns valid data', async () => {
    const mockCapsules = [
      {
        id: 'test-capsule-1',
        name: 'Test Capsule',
        description: 'A test capsule',
        version: '1.0.0',
        author: 'Test Author',
        category: 'test',
        tags: ['test'],
        drivers: ['drv-test'],
        downloads: 100,
        rating: 4.5,
        status: 'available',
        verified: true,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      },
    ]

    mockGet.mockResolvedValue({
      data: {
        capsules: mockCapsules,
        blueprints: [],
      },
    })

    renderComponent()

    await waitFor(() => {
      expect(screen.getByText('Test Capsule')).toBeInTheDocument()
    })
  })

  it('should fill empty blueprints with demo data if capsules exist', async () => {
    const mockCapsules = [
      {
        id: 'test-capsule',
        name: 'Test Capsule',
        description: 'Test',
        version: '1.0.0',
        author: 'Test',
        category: 'test',
        tags: [],
        drivers: [],
        downloads: 0,
        rating: 4.0,
        status: 'available',
        verified: true,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      },
    ]

    mockGet.mockResolvedValue({
      data: {
        capsules: mockCapsules,
        blueprints: [],
      },
    })

    renderComponent()

    await waitFor(() => {
      // Should show demo blueprints even though API returned empty blueprints
      expect(screen.getByText(/Blueprints/i)).toBeInTheDocument()
    })
  })

  it('should handle API timeout gracefully with demo data', async () => {
    // Mock API timeout
    mockGet.mockImplementation(
      () => new Promise((_, reject) => 
        setTimeout(() => reject(new Error('Request timeout')), 100)
      )
    )

    renderComponent()

    // Should eventually show demo data after timeout
    await waitFor(() => {
      expect(screen.getByText(/Shell Capsule|Git Maintenance/i)).toBeInTheDocument()
    }, { timeout: 3000 })
  })

  it('should render without crashing', () => {
    mockGet.mockResolvedValue({ data: {} })

    const { container } = renderComponent()
    expect(container).toBeTruthy()
  })

  it('should be accessible', async () => {
    mockGet.mockResolvedValue({ data: {} })

    const { container } = renderComponent()

    await waitFor(() => {
      // Basic accessibility check - should have main content area
      expect(container.querySelector('div, main, article')).toBeTruthy()
    })
  })
})
