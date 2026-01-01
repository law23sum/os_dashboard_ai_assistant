/**
 * Comprehensive tests for Signup component
 * Tests registration flow, validation, error handling, and user interactions
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import React from 'react'
import Signup from '../Signup'
import * as authApi from '../../api/auth'
import { useAuth } from '../../auth/AuthContext'
import { toast } from '../../utils/toast'

// Mock dependencies
vi.mock('../../api/auth', () => ({
  signup: vi.fn(),
}))

vi.mock('../../lib/apiClient', () => ({
  default: {
    post: vi.fn(),
    get: vi.fn(),
  },
  apiPath: vi.fn((path: string) => `/api/${path}`),
  setAccessToken: vi.fn(),
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

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  }
})

describe('Signup Component', () => {
  const mockRefresh = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
    mockNavigate.mockClear()
    ;(useAuth as any).mockReturnValue({ refresh: mockRefresh })
  })

  it('should render signup form with all required fields', () => {
    render(
      <BrowserRouter>
        <Signup />
      </BrowserRouter>
    )

    expect(screen.getByLabelText(/full name/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/username/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/^password/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/confirm password/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /create account/i })).toBeInTheDocument()
  })

  it('should show error when passwords do not match', async () => {
    render(
      <BrowserRouter>
        <Signup />
      </BrowserRouter>
    )

    const passwordInput = screen.getByLabelText(/^password/i)
    const confirmPasswordInput = screen.getByLabelText(/confirm password/i)
    const submitButton = screen.getByRole('button', { name: /create account/i })

    fireEvent.change(passwordInput, { target: { value: 'password123' } })
    fireEvent.change(confirmPasswordInput, { target: { value: 'different123' } })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/passwords do not match/i)).toBeInTheDocument()
      expect(toast.error).toHaveBeenCalledWith('Passwords do not match')
    })
  })

  it('should show error when password is too short', async () => {
    render(
      <BrowserRouter>
        <Signup />
      </BrowserRouter>
    )

    const passwordInput = screen.getByLabelText(/^password/i)
    const confirmPasswordInput = screen.getByLabelText(/confirm password/i)
    const usernameInput = screen.getByLabelText(/username/i)
    const emailInput = screen.getByLabelText(/email/i)
    const submitButton = screen.getByRole('button', { name: /create account/i })

    fireEvent.change(usernameInput, { target: { value: 'testuser' } })
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } })
    fireEvent.change(passwordInput, { target: { value: 'short' } })
    fireEvent.change(confirmPasswordInput, { target: { value: 'short' } })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/password must be at least 6 characters/i)).toBeInTheDocument()
      expect(toast.error).toHaveBeenCalledWith('Password must be at least 6 characters')
    })
  })

  it('should successfully signup and auto-login with valid data', async () => {
    const mockAccessToken = 'mock-access-token'
    const mockUser = {
      id: '1',
      email: 'newuser@example.com',
      display_name: 'New User',
      is_admin: false,
      environment: 'demo',
    }

    // Mock signup response
    ;(authApi.signup as any).mockResolvedValueOnce({
      access_token: mockAccessToken,
      token_type: 'bearer',
      user: mockUser,
    })

    render(
        <BrowserRouter>
        <Signup />
        </BrowserRouter>
      )

    const fullNameInput = screen.getByLabelText(/full name/i)
    const usernameInput = screen.getByLabelText(/username/i)
    const emailInput = screen.getByLabelText(/email/i)
    const passwordInput = screen.getByLabelText(/^password/i)
    const confirmPasswordInput = screen.getByLabelText(/confirm password/i)
    const submitButton = screen.getByRole('button', { name: /create account/i })

    fireEvent.change(fullNameInput, { target: { value: 'New User' } })
    fireEvent.change(usernameInput, { target: { value: 'newuser' } })
    fireEvent.change(emailInput, { target: { value: 'newuser@example.com' } })
    fireEvent.change(passwordInput, { target: { value: 'password123' } })
    fireEvent.change(confirmPasswordInput, { target: { value: 'password123' } })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(authApi.signup).toHaveBeenCalledWith(
        'newuser@example.com',
        'password123',
        'New User', // fullName is used as display_name
        'demo'
      )
    })

    await waitFor(() => {
      expect(localStorage.getItem('access_token')).toBe(mockAccessToken)
      expect(toast.success).toHaveBeenCalledWith('Account created successfully!')
      expect(mockNavigate).toHaveBeenCalledWith('/dashboard', { replace: true })
    })
  })

  it('should handle network errors gracefully', async () => {
    const networkError = {
      code: 'ERR_NETWORK',
      message: 'Network Error',
      request: {},
    }

    ;(authApi.signup as any).mockRejectedValue(networkError)

    render(
      <BrowserRouter>
        <Signup />
      </BrowserRouter>
    )

    const usernameInput = screen.getByLabelText(/username/i)
    const emailInput = screen.getByLabelText(/email/i)
    const passwordInput = screen.getByLabelText(/^password/i)
    const confirmPasswordInput = screen.getByLabelText(/confirm password/i)
    const submitButton = screen.getByRole('button', { name: /create account/i })

    fireEvent.change(usernameInput, { target: { value: 'testuser' } })
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } })
    fireEvent.change(passwordInput, { target: { value: 'password123' } })
    fireEvent.change(confirmPasswordInput, { target: { value: 'password123' } })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/backend server is not running/i)).toBeInTheDocument()
      expect(toast.error).toHaveBeenCalled()
    })
  })

  it('should handle duplicate email/username error', async () => {
    const duplicateError = {
      response: {
        status: 400,
        data: {
          detail: 'Username or email already registered',
        },
      },
    }

    ;(authApi.signup as any).mockRejectedValue(duplicateError)

    render(
      <BrowserRouter>
        <Signup />
      </BrowserRouter>
    )

    const usernameInput = screen.getByLabelText(/username/i)
    const emailInput = screen.getByLabelText(/email/i)
    const passwordInput = screen.getByLabelText(/^password/i)
    const confirmPasswordInput = screen.getByLabelText(/confirm password/i)
    const submitButton = screen.getByRole('button', { name: /create account/i })

    fireEvent.change(usernameInput, { target: { value: 'existinguser' } })
    fireEvent.change(emailInput, { target: { value: 'existing@example.com' } })
    fireEvent.change(passwordInput, { target: { value: 'password123' } })
    fireEvent.change(confirmPasswordInput, { target: { value: 'password123' } })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/username or email already registered/i)).toBeInTheDocument()
      expect(toast.error).toHaveBeenCalled()
    })
  })

  it('should handle validation errors with array format', async () => {
    const validationError = {
      response: {
        status: 422,
        data: {
          detail: [
            { msg: 'Email is required' },
            { msg: 'Username must be at least 3 characters' },
          ],
        },
      },
    }

    ;(authApi.signup as any).mockRejectedValue(validationError)

    render(
      <BrowserRouter>
        <Signup />
      </BrowserRouter>
    )

    const usernameInput = screen.getByLabelText(/username/i)
    const emailInput = screen.getByLabelText(/email/i)
    const passwordInput = screen.getByLabelText(/^password/i)
    const confirmPasswordInput = screen.getByLabelText(/confirm password/i)
    const submitButton = screen.getByRole('button', { name: /create account/i })

    fireEvent.change(usernameInput, { target: { value: 'ab' } })
    fireEvent.change(emailInput, { target: { value: 'invalid' } })
    fireEvent.change(passwordInput, { target: { value: 'password123' } })
    fireEvent.change(confirmPasswordInput, { target: { value: 'password123' } })
    fireEvent.click(submitButton)

    await waitFor(() => {
      const errorText = screen.getByText(/email is required.*username must be at least 3 characters/i)
      expect(errorText).toBeInTheDocument()
    })
  })

  it('should redirect to login page when clicking sign in link', () => {
    render(
      <BrowserRouter>
        <Signup />
      </BrowserRouter>
    )

    const loginLink = screen.getByRole('link', { name: /sign in/i })
    expect(loginLink).toHaveAttribute('href', '/login')
  })

  it('should show loading state during signup', async () => {
    ;(authApi.signup as any).mockImplementation(
      () => new Promise((resolve) => setTimeout(() => resolve({ 
        access_token: 'token',
        token_type: 'bearer',
        user: { id: '1', email: 'test@example.com', display_name: 'Test', is_admin: false, environment: 'demo' }
      }), 100))
    )

    render(
        <BrowserRouter>
        <Signup />
        </BrowserRouter>
      )

    const usernameInput = screen.getByLabelText(/username/i)
    const emailInput = screen.getByLabelText(/email/i)
    const passwordInput = screen.getByLabelText(/^password/i)
    const confirmPasswordInput = screen.getByLabelText(/confirm password/i)
    const submitButton = screen.getByRole('button', { name: /create account/i })

    fireEvent.change(usernameInput, { target: { value: 'testuser' } })
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } })
    fireEvent.change(passwordInput, { target: { value: 'password123' } })
    fireEvent.change(confirmPasswordInput, { target: { value: 'password123' } })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/creating account/i)).toBeInTheDocument()
      expect(submitButton).toBeDisabled()
    })
  })

  it('should allow optional full name field', async () => {
    const mockAccessToken = 'mock-access-token'
    const mockUser = {
      id: '1',
      email: 'newuser@example.com',
      display_name: 'newuser', // When fullName is empty, username is used
      is_admin: false,
      environment: 'demo',
    }

    ;(authApi.signup as any).mockResolvedValueOnce({
      access_token: mockAccessToken,
      token_type: 'bearer',
      user: mockUser,
    })

    render(
      <BrowserRouter>
        <Signup />
      </BrowserRouter>
    )

    const usernameInput = screen.getByLabelText(/username/i)
    const emailInput = screen.getByLabelText(/email/i)
    const passwordInput = screen.getByLabelText(/^password/i)
    const confirmPasswordInput = screen.getByLabelText(/confirm password/i)
    const submitButton = screen.getByRole('button', { name: /create account/i })

    // Don't fill in full name
    fireEvent.change(usernameInput, { target: { value: 'newuser' } })
    fireEvent.change(emailInput, { target: { value: 'newuser@example.com' } })
    fireEvent.change(passwordInput, { target: { value: 'password123' } })
    fireEvent.change(confirmPasswordInput, { target: { value: 'password123' } })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(authApi.signup).toHaveBeenCalledWith(
        'newuser@example.com',
        'password123',
        'newuser', // When fullName is empty, username is used as display_name
        'demo'
      )
    })
  })
})
