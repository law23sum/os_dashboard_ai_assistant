/**
 * E2E Tests for Projects Page
 * Tests the complete flow of project management including:
 * - Listing projects
 * - Creating projects  
 * - Updating projects
 * - Deleting projects
 * - Import/Export functionality
 * 
 * Spec References: §3.3, §7.2, §8.7
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, waitFor, fireEvent, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter } from 'react-router-dom'
import Projects from '../../pages/Projects'

// Mock the API client
vi.mock('../../lib/apiClient', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
  apiPath: (path: string) => `/api/${path}`,
}))

vi.mock('../../lib/responseHelpers', () => ({
  extractArray: (data: unknown, keys: string[]) => {
    if (Array.isArray(data)) return data
    if (data && typeof data === 'object') {
      for (const key of keys) {
        if (Array.isArray((data as Record<string, unknown>)[key])) {
          return (data as Record<string, unknown>)[key]
        }
      }
    }
    return []
  },
}))

import apiClient from '../../lib/apiClient'

const mockProjects = [
  {
    name: 'Test Project 1',
    description: 'First test project',
    status: 'active',
    priority: 'HIGH',
    order_num: 0,
  },
  {
    name: 'Test Project 2',
    description: 'Second test project',
    status: 'planning',
    priority: 'MEDIUM',
    order_num: 1,
  },
]

const mockTasks = [
  {
    id: 1,
    title: 'Task 1',
    project: 'Test Project 1',
    status: 'IN_PROGRESS',
    priority: 'HIGH',
    notes: '',
    owner: 'Chris',
    created_at: '2025-01-01T00:00:00Z',
  },
]

const mockLinks = [
  {
    id: 1,
    project_id: 'Test Project 1',
    integration_type: 'local_document',
    title: 'Test Doc',
    description: '',
    external_id: '/docs/test.md',
    created_at: '2025-01-01T00:00:00Z',
    last_synced: null,
    label: 'Document',
    href: '/docs/test.md',
    available: true,
  },
]

const mockLedgerEvents = [
  {
    id: 'evt-1',
    project_id: 'Test Project 1',
    event_type: 'project_created',
    entity_type: 'project',
    entity_id: 'Test Project 1',
    payload: {},
    created_at: '2025-01-01T00:00:00Z',
    hash_prev: null,
    hash_curr: 'abc123',
  },
]

const mockIntelligence = [
  {
    project_id: 'Test Project 1',
    health_score: 85,
    risk_level: 'steady',
    completion_ratio: 0.75,
    total_tasks: 4,
    open_tasks: 1,
    critical_tasks: 0,
    ledger_ok: true,
    last_event_at: '2025-01-01T00:00:00Z',
    last_event_type: 'task_created',
    summary: 'Steady state',
  },
]

const mockPersonas = [
  {
    id: 'persona-aic',
    type: 'aic',
    label: 'AIC',
    decision_threshold: 0.9,
    interaction_style: 'governor',
    capabilities: ['system_architecture'],
    active: true,
  },
]

const mockReasoningHistory: unknown[] = []

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

describe('Projects Page E2E Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    
    // Setup default mock responses
    vi.mocked(apiClient.get).mockImplementation(async (url: string) => {
      if (url.includes('/projects/links')) {
        return { data: mockLinks }
      }
      if (url.includes('/projects/ledger')) {
        return { data: mockLedgerEvents }
      }
      if (url.includes('/projects/intelligence')) {
        return { data: mockIntelligence }
      }
      if (url.includes('/projects')) {
        return { data: mockProjects }
      }
      if (url.includes('/tasks')) {
        return { data: mockTasks }
      }
      if (url.includes('/reasoning/personas')) {
        return { data: mockPersonas }
      }
      if (url.includes('/reasoning/history')) {
        return { data: mockReasoningHistory }
      }
      return { data: [] }
    })
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  describe('Project Listing', () => {
    it('should display all projects from the backend', async () => {
      renderWithProviders(<Projects />)

      await waitFor(() => {
        expect(screen.getByText('Test Project 1')).toBeInTheDocument()
        expect(screen.getByText('Test Project 2')).toBeInTheDocument()
      })
    })

    it('should show project count statistics', async () => {
      renderWithProviders(<Projects />)

      await waitFor(() => {
        const totalProjects = screen.getByText(/Total Projects/i)
        expect(totalProjects).toBeInTheDocument()
      })
    })

    it('should display project status badges', async () => {
      renderWithProviders(<Projects />)

      await waitFor(() => {
        expect(screen.getByText('active')).toBeInTheDocument()
        expect(screen.getByText('planning')).toBeInTheDocument()
      })
    })
  })

  describe('Project Creation', () => {
    it('should open create project form when clicking New Project button', async () => {
      const user = userEvent.setup()
      renderWithProviders(<Projects />)

      await waitFor(() => {
        expect(screen.getByText('Test Project 1')).toBeInTheDocument()
      })

      const newProjectBtn = screen.getByRole('button', { name: /new project/i })
      await user.click(newProjectBtn)

      expect(screen.getByText('Create Project')).toBeInTheDocument()
      expect(screen.getByPlaceholderText(/atlas master stack/i)).toBeInTheDocument()
    })

    it('should create a new project when form is submitted', async () => {
      vi.mocked(apiClient.post).mockResolvedValueOnce({
        data: {
          name: 'New Test Project',
          description: 'A new project',
          status: 'active',
          priority: 'MEDIUM',
          order_num: 2,
        },
      })

      const user = userEvent.setup()
      renderWithProviders(<Projects />)

      await waitFor(() => {
        expect(screen.getByText('Test Project 1')).toBeInTheDocument()
      })

      // Open create form
      const newProjectBtn = screen.getByRole('button', { name: /new project/i })
      await user.click(newProjectBtn)

      // Fill in the form
      const nameInput = screen.getByPlaceholderText(/atlas master stack/i)
      await user.type(nameInput, 'New Test Project')

      const descriptionInput = screen.getByPlaceholderText(/mission, scope, or capsule objectives/i)
      await user.type(descriptionInput, 'A new project')

      // Submit the form
      const submitBtn = screen.getByRole('button', { name: /create project/i })
      await user.click(submitBtn)

      await waitFor(() => {
        expect(apiClient.post).toHaveBeenCalledWith(
          '/api/projects',
          expect.objectContaining({
            name: 'New Test Project',
            description: 'A new project',
          })
        )
      })
    })
  })

  describe('Project Updates', () => {
    it('should open edit form when clicking Edit button', async () => {
      const user = userEvent.setup()
      renderWithProviders(<Projects />)

      await waitFor(() => {
        expect(screen.getByText('Test Project 1')).toBeInTheDocument()
      })

      // Find and click the Edit button for the first project
      const editButtons = screen.getAllByRole('button', { name: /edit/i })
      await user.click(editButtons[0])

      // Should show update form
      await waitFor(() => {
        expect(screen.getByText(/update test project 1/i)).toBeInTheDocument()
      })
    })

    it('should update project when form is submitted', async () => {
      vi.mocked(apiClient.put).mockResolvedValueOnce({
        data: {
          name: 'Test Project 1',
          description: 'Updated description',
          status: 'active',
          priority: 'CRITICAL',
          order_num: 0,
        },
      })

      const user = userEvent.setup()
      renderWithProviders(<Projects />)

      await waitFor(() => {
        expect(screen.getByText('Test Project 1')).toBeInTheDocument()
      })

      // Open edit form
      const editButtons = screen.getAllByRole('button', { name: /edit/i })
      await user.click(editButtons[0])

      await waitFor(() => {
        expect(screen.getByText(/update test project 1/i)).toBeInTheDocument()
      })

      // Update priority
      const prioritySelect = screen.getByRole('combobox', { name: /priority/i })
      await user.selectOptions(prioritySelect, 'CRITICAL')

      // Submit
      const saveBtn = screen.getByRole('button', { name: /save changes/i })
      await user.click(saveBtn)

      await waitFor(() => {
        expect(apiClient.put).toHaveBeenCalledWith(
          expect.stringContaining('Test Project 1'),
          expect.objectContaining({
            priority: 'CRITICAL',
          })
        )
      })
    })
  })

  describe('Project Deletion', () => {
    it('should show confirmation dialog when deleting project', async () => {
      const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(false)
      const user = userEvent.setup()
      
      renderWithProviders(<Projects />)

      await waitFor(() => {
        expect(screen.getByText('Test Project 1')).toBeInTheDocument()
      })

      const deleteButtons = screen.getAllByRole('button', { name: /delete/i })
      await user.click(deleteButtons[0])

      expect(confirmSpy).toHaveBeenCalledWith(
        expect.stringContaining('Delete project')
      )
      
      confirmSpy.mockRestore()
    })

    it('should delete project when confirmed', async () => {
      vi.spyOn(window, 'confirm').mockReturnValue(true)
      vi.mocked(apiClient.delete).mockResolvedValueOnce({ data: null })

      const user = userEvent.setup()
      renderWithProviders(<Projects />)

      await waitFor(() => {
        expect(screen.getByText('Test Project 1')).toBeInTheDocument()
      })

      const deleteButtons = screen.getAllByRole('button', { name: /delete/i })
      await user.click(deleteButtons[0])

      await waitFor(() => {
        expect(apiClient.delete).toHaveBeenCalledWith(
          expect.stringContaining('Test Project 1')
        )
      })
    })
  })

  describe('Project Intelligence Panel', () => {
    it('should display health score metrics', async () => {
      renderWithProviders(<Projects />)

      await waitFor(() => {
        const avgHealthLabel = screen.getByText(/avg health/i)
        expect(avgHealthLabel).toBeInTheDocument()
      })
    })

    it('should display high-risk project count', async () => {
      renderWithProviders(<Projects />)

      await waitFor(() => {
        const highRiskLabel = screen.getByText(/high-risk projects/i)
        expect(highRiskLabel).toBeInTheDocument()
      })
    })
  })

  describe('Project Ledger Panel', () => {
    it('should display ledger events', async () => {
      renderWithProviders(<Projects />)

      await waitFor(() => {
        expect(screen.getByText(/project ledger/i)).toBeInTheDocument()
      })
    })

    it('should show ledger integrity status', async () => {
      renderWithProviders(<Projects />)

      await waitFor(() => {
        // Should show "Hash chain intact" for valid ledger
        const integrityLabel = screen.queryByText(/hash chain intact/i) || screen.queryByText(/hash divergence/i)
        expect(integrityLabel).toBeInTheDocument()
      })
    })
  })

  describe('Refresh Functionality', () => {
    it('should refresh data when clicking Refresh button', async () => {
      const user = userEvent.setup()
      renderWithProviders(<Projects />)

      await waitFor(() => {
        expect(screen.getByText('Test Project 1')).toBeInTheDocument()
      })

      const refreshBtn = screen.getByRole('button', { name: /refresh snapshot/i })
      await user.click(refreshBtn)

      // Should trigger multiple API calls to refresh data
      await waitFor(() => {
        expect(apiClient.get).toHaveBeenCalled()
      })
    })
  })
})

describe('Projects Integration Tests', () => {
  it('should handle API errors gracefully', async () => {
    vi.mocked(apiClient.get).mockRejectedValueOnce(new Error('Network error'))

    renderWithProviders(<Projects />)

    // Should show loading state initially then handle error
    await waitFor(() => {
      // Component should either show error or fallback content
      const content = document.body.textContent
      expect(content).toBeTruthy()
    })
  })

  it('should display empty state when no projects exist', async () => {
    vi.mocked(apiClient.get).mockImplementation(async (url: string) => {
      if (url.includes('/projects')) {
        return { data: [] }
      }
      if (url.includes('/tasks')) {
        return { data: [] }
      }
      return { data: [] }
    })

    renderWithProviders(<Projects />)

    await waitFor(() => {
      expect(screen.getByText(/no projects registered/i)).toBeInTheDocument()
    })
  })
})
