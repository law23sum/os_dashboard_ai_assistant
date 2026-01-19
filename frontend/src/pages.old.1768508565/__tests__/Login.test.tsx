/**
 * Comprehensive tests for Login component
 * Tests authentication flow, error handling, and user interactions
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import React from 'react'
import Login from '../Login'
import * as apiClient from '../../lib/apiClient'
import { useAuth } from '../../auth/AuthContext'
import { toast } from '../../utils/toast'

// Mock dependencies
vi.mock('../../lib/apiClient', () => ({
  default: {
    post: vi.fn(),
    get: vi.fn(),
  },
  apiPath: vi.fn((path: string) => `/api/${path}`),
  setAccessToken: (token: string | null) => {
    if (token) {
      localStorage.setItem('access_token', token)
    } else {
      localStorage.removeItem('access_token')
    }
  },
}))

vi.mock('../../auth/AuthContext', () => ({
  useAuth: vi.fn(),
}))

vi.mock('../../utils/toast', () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
  },
}))

const mockNavigate = vi.fn()
const mockLocation = { state: null, pathname: '/login', search: '', hash: '' }
const routerFutureFlags = {
  v7_startTransition: true,
  v7_relativeSplatPath: true,
}

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  const BrowserRouter = (props: React.ComponentProps<typeof actual.BrowserRouter>) => {
    const { future, ...rest } = props
    return React.createElement(actual.BrowserRouter, {
      ...rest,
      future: { ...routerFutureFlags, ...future },
    })
  }
  return {
    ...actual,
    BrowserRouter,
    useNavigate: () => mockNavigate,
    useLocation: () => mockLocation,
  }
})

describe('Login Component', () => {
  const mockRefresh = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
    mockNavigate.mockClear()
    ;(useAuth as any).mockReturnValue({ refresh: mockRefresh })
  })

  it('should render login form with all required fields', () => {
    render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    )

    expect(screen.getByLabelText(/username/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument()
  })

  it('should show validation error when submitting empty form', async () => {
    render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    )

    const submitButton = screen.getByRole('button', { name: /sign in/i })
    fireEvent.click(submitButton)

    await waitFor(() => {
      const usernameInput = screen.getByLabelText(/username/i) as HTMLInputElement
      expect(usernameInput.validity.valueMissing).toBe(true)
    })
  })

  it('should successfully login with valid credentials', async () => {
    const mockAccessToken = 'mock-access-token'
    const mockRefreshToken = 'mock-refresh-token'

    ;(apiClient.default.post as any)
      .mockResolvedValueOnce({
        data: {
          access_token: mockAccessToken,
          refresh_token: mockRefreshToken,
        },
      })

    render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    )

    const usernameInput = screen.getByLabelText(/username/i)
    const passwordInput = screen.getByLabelText(/password/i)
    const submitButton = screen.getByRole('button', { name: /sign in/i })

    fireEvent.change(usernameInput, { target: { value: 'testuser' } })
    fireEvent.change(passwordInput, { target: { value: 'password123' } })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(apiClient.default.post).toHaveBeenCalledWith(
        '/api/auth/login',
        {
          username: 'testuser',
          password: 'password123',
        }
      )
    })

    await waitFor(() => {
      expect(localStorage.getItem('access_token')).toBe(mockAccessToken)
      expect(localStorage.getItem('refresh_token')).toBe(mockRefreshToken)
      expect(mockRefresh).toHaveBeenCalled()
      expect(toast.success).toHaveBeenCalledWith('Login successful!')
    })
  })

  it('should handle network errors gracefully', async () => {
    const networkError = {
      code: 'ERR_NETWORK',
      message: 'Network Error',
      request: {},
    }

    ;(apiClient.default.post as any).mockRejectedValue(networkError)

    render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    )

    const usernameInput = screen.getByLabelText(/username/i)
    const passwordInput = screen.getByLabelText(/password/i)
    const submitButton = screen.getByRole('button', { name: /sign in/i })

    fireEvent.change(usernameInput, { target: { value: 'testuser' } })
    fireEvent.change(passwordInput, { target: { value: 'password123' } })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/backend server is not running/i)).toBeInTheDocument()
      expect(toast.error).toHaveBeenCalled()
    })
  })

  it('should handle invalid credentials error', async () => {
    const errorResponse = {
      response: {
        status: 401,
        data: {
          detail: 'Invalid username or password',
        },
      },
    }

    ;(apiClient.default.post as any).mockRejectedValue(errorResponse)

    render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    )

    const usernameInput = screen.getByLabelText(/username/i)
    const passwordInput = screen.getByLabelText(/password/i)
    const submitButton = screen.getByRole('button', { name: /sign in/i })

    fireEvent.change(usernameInput, { target: { value: 'wronguser' } })
    fireEvent.change(passwordInput, { target: { value: 'wrongpass' } })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/invalid username or password/i)).toBeInTheDocument()
      expect(toast.error).toHaveBeenCalled()
    })
  })

  it('should handle validation errors with array format', async () => {
    const validationError = {
      response: {
        status: 422,
        data: {
          detail: [
            { msg: 'Username is required' },
            { msg: 'Password is required' },
          ],
        },
      },
    }

    ;(apiClient.default.post as any).mockRejectedValue(validationError)

    render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    )

    const usernameInput = screen.getByLabelText(/username/i)
    const passwordInput = screen.getByLabelText(/password/i)
    const submitButton = screen.getByRole('button', { name: /sign in/i })

    fireEvent.change(usernameInput, { target: { value: 'test' } })
    fireEvent.change(passwordInput, { target: { value: 'test' } })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/username is required.*password is required/i)).toBeInTheDocument()
    })
  })

  it('should redirect to signup page when clicking create account link', () => {
    render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    )

    const signupLink = screen.getByRole('link', { name: /create one/i })
    expect(signupLink).toHaveAttribute('href', '/signup')
  })

  it('should show loading state during login', async () => {
    ;(apiClient.default.post as any).mockImplementation(
      () => new Promise((resolve) => setTimeout(() => resolve({ data: {} }), 100))
    )

    render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    )

    const usernameInput = screen.getByLabelText(/username/i)
    const passwordInput = screen.getByLabelText(/password/i)
    const submitButton = screen.getByRole('button', { name: /sign in/i })

    fireEvent.change(usernameInput, { target: { value: 'testuser' } })
    fireEvent.change(passwordInput, { target: { value: 'password123' } })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/signing in/i)).toBeInTheDocument()
      expect(submitButton).toBeDisabled()
    })
  })

  it('should redirect if already authenticated', () => {
    localStorage.setItem('access_token', 'existing-token')

    render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    )

    // Should redirect, so form should not be visible
    expect(screen.queryByLabelText(/username/i)).not.toBeInTheDocument()
  })
})
