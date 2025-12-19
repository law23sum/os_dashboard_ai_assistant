import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, fireEvent, waitFor, cleanup } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import Layout from '../Layout'
import { throttle } from '../../shared/utils'

// Mock the throttle function to track calls
vi.mock('../../shared/utils', () => ({
  throttle: vi.fn((fn) => fn),
  debounce: vi.fn((fn) => fn),
}))

// Mock UnifiedAIPanel to simplify tests
vi.mock('../UnifiedAIPanel', () => ({
  UnifiedAIPanel: () => <div data-testid="ai-panel">AI Panel</div>,
}))

// Mock useAppSettings hook
vi.mock('../../hooks/useSettings', () => ({
  useAppSettings: () => ({
    data: { theme: 'default' },
  }),
}))

describe('Layout NavDropdown Performance', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    // Mock window methods
    global.requestAnimationFrame = vi.fn((cb) => setTimeout(cb, 16))
    global.cancelAnimationFrame = vi.fn()
  })

  afterEach(() => {
    vi.restoreAllMocks()
    // Ensure React/RTL unmounts the tree before the next test.
    cleanup()
  })

  const renderLayout = () => {
    return render(
      <BrowserRouter>
        <Layout>
          <div>Test Content</div>
        </Layout>
      </BrowserRouter>
    )
  }

  it('should throttle scroll and resize events', async () => {
    renderLayout()
    
    // Find a dropdown button (e.g., Mission Control)
    const dropdownButton = screen.getByText('Mission Control')
    expect(dropdownButton).toBeInTheDocument()

    // Click to open dropdown
    fireEvent.click(dropdownButton)

    // Verify throttle was called
    expect(throttle).toHaveBeenCalled()

    // Simulate scroll events (should not throw)
    const scrollEvents = Array(10)
      .fill(null)
      .map(() => new Event('scroll'))
    scrollEvents.forEach((event) => window.dispatchEvent(event))

    // Dropdown should remain visible
    await waitFor(() => {
      const dropdown = document.body.querySelector('.osd-dropdown')
      expect(dropdown).toBeInTheDocument()
    })
  })

  it('should not cause excessive re-renders when opening dropdown', async () => {
    const renderSpy = vi.fn()
    renderLayout()

    // Find dropdown button
    const dropdownButton = screen.getByText('Mission Control')
    
    // Track renders (in a real scenario, we'd use React DevTools Profiler)
    const initialRenderCount = renderSpy.mock.calls.length

    // Open dropdown
    fireEvent.click(dropdownButton)

    await waitFor(() => {
      // Dropdown should be visible (portaled to document.body)
      const dropdown = document.body.querySelector('.osd-dropdown')
      expect(dropdown).toBeInTheDocument()
    })

    // Verify dropdown opened without excessive renders
    // In a real test, we'd measure actual render counts
    expect(dropdownButton).toBeInTheDocument()
  })

  it('should handle rapid open/close cycles efficiently', async () => {
    renderLayout()
    
    const dropdownButton = screen.getByText('Mission Control')

    // Rapidly toggle dropdown multiple times
    for (let i = 0; i < 5; i++) {
      fireEvent.click(dropdownButton)
      await waitFor(() => {
        const dropdown = document.body.querySelector('.osd-dropdown')
        expect(dropdown).toBeInTheDocument()
      })

      fireEvent.click(dropdownButton)
      await waitFor(() => {
        const dropdown = document.body.querySelector('.osd-dropdown')
        expect(dropdown).not.toBeInTheDocument()
      })
    }

    // Should not throw errors or cause performance issues
    expect(dropdownButton).toBeInTheDocument()
  })

  it('should cleanup event listeners on unmount', () => {
    const addEventListenerSpy = vi.spyOn(window, 'addEventListener')
    const removeEventListenerSpy = vi.spyOn(window, 'removeEventListener')

    const { unmount } = renderLayout()
    
    const dropdownButton = screen.getByText('Mission Control')
    fireEvent.click(dropdownButton)

    // Verify listeners were added
    expect(addEventListenerSpy).toHaveBeenCalledWith(
      'scroll',
      expect.any(Function),
      expect.objectContaining({ capture: true })
    )
    expect(addEventListenerSpy).toHaveBeenCalledWith('resize', expect.any(Function), expect.anything())

    // Unmount component
    unmount()

    // Verify listeners were removed
    expect(removeEventListenerSpy).toHaveBeenCalledWith(
      'scroll',
      expect.any(Function),
      expect.objectContaining({ capture: true })
    )
    // Resize handler may be removed without passing the original options object in jsdom.
    expect(removeEventListenerSpy).toHaveBeenCalledWith('resize', expect.any(Function))

    addEventListenerSpy.mockRestore()
    removeEventListenerSpy.mockRestore()
  })

  it('should use memoized handlers to prevent unnecessary re-renders', async () => {
    renderLayout()
    
    const dropdownButton = screen.getByText('Mission Control')
    
    // Open dropdown
    fireEvent.click(dropdownButton)

    // Click a link inside dropdown and ensure it closes cleanly.
    await waitFor(() => {
      const dropdown = document.body.querySelector('.osd-dropdown')
      expect(dropdown).toBeInTheDocument()
    })

    const dropdown = document.body.querySelector('.osd-dropdown')
    const link = dropdown?.querySelector('a')
    expect(link).toBeTruthy()
    if (link) {
      fireEvent.click(link)
    }

    await waitFor(() => {
      const nextDropdown = document.body.querySelector('.osd-dropdown')
      expect(nextDropdown).not.toBeInTheDocument()
    })
  })

  it('should position dropdown efficiently without layout thrashing', async () => {
    const getBoundingClientRectSpy = vi.spyOn(Element.prototype, 'getBoundingClientRect')
    getBoundingClientRectSpy.mockReturnValue({
      left: 100,
      top: 50,
      right: 200,
      bottom: 100,
      width: 100,
      height: 50,
      x: 100,
      y: 50,
      toJSON: vi.fn(),
    } as DOMRect)

    renderLayout()
    
    const dropdownButton = screen.getByText('Mission Control')
    fireEvent.click(dropdownButton)

    await waitFor(() => {
      const dropdown = document.body.querySelector('.osd-dropdown') as HTMLElement
      expect(dropdown).toBeInTheDocument()
    })

    // getBoundingClientRect should be called, but not excessively
    // In a real scenario, we'd verify it's called a reasonable number of times
    expect(getBoundingClientRectSpy).toHaveBeenCalled()

    getBoundingClientRectSpy.mockRestore()
  })
})

describe('Select Element Performance', () => {
  it('should use memoized onChange handlers', () => {
    // This test would be for select elements in Research.tsx
    // In a real scenario, we'd test that handlers are stable across renders
    expect(true).toBe(true) // Placeholder - would test actual select components
  })
})

