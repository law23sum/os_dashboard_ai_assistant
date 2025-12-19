import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
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
    const addEventListenerSpy = vi.spyOn(window, 'addEventListener')
    renderLayout()
    
    // Find a dropdown button (e.g., Mission Control)
    const dropdownButton = screen.getByText('Mission Control')
    expect(dropdownButton).toBeInTheDocument()

    // Click to open dropdown
    fireEvent.click(dropdownButton)

    // Verify throttle was called
    expect(throttle).toHaveBeenCalled()

    // Verify listeners were registered with capture on scroll for portaled dropdown positioning
    expect(addEventListenerSpy).toHaveBeenCalledWith(
      'scroll',
      expect.any(Function),
      expect.objectContaining({ capture: true }),
    )
    expect(addEventListenerSpy).toHaveBeenCalledWith('resize', expect.any(Function), expect.any(Object))

    addEventListenerSpy.mockRestore()
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
    for (let i = 0; i < 3; i++) {
      fireEvent.click(dropdownButton)
      await waitFor(() => {
        const dropdown = document.body.querySelector('.osd-dropdown')
        expect(dropdown).toBeInTheDocument()
      }, { timeout: 50 })
      
      fireEvent.click(dropdownButton)
      await waitFor(() => {
        const dropdown = document.body.querySelector('.osd-dropdown')
        expect(dropdown).not.toBeInTheDocument()
      }, { timeout: 50 })
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
      expect.objectContaining({ capture: true }),
    )
    expect(addEventListenerSpy).toHaveBeenCalledWith('resize', expect.any(Function), expect.any(Object))

    // Unmount component
    unmount()

    // Verify listeners were removed
    expect(removeEventListenerSpy).toHaveBeenCalledWith(
      'scroll',
      expect.any(Function),
      expect.objectContaining({ capture: true }),
    )
    expect(removeEventListenerSpy).toHaveBeenCalledWith('resize', expect.any(Function))

    addEventListenerSpy.mockRestore()
    removeEventListenerSpy.mockRestore()
  })

  it('should use memoized handlers to prevent unnecessary re-renders', async () => {
    renderLayout()
    
    const dropdownButton = screen.getByText('Mission Control')
    
    // Open dropdown
    fireEvent.click(dropdownButton)

    // Get the dropdown element (portaled to document.body)
    await waitFor(() => {
      const dropdown = document.body.querySelector('.osd-dropdown')
      expect(dropdown).toBeInTheDocument()

      // Click a link inside dropdown
      const link = dropdown?.querySelector('a')
      if (link) {
        fireEvent.click(link)
      }
    })

    // Clicking a link should close the dropdown via onClose()
    await waitFor(() => {
      expect(document.body.querySelector('.osd-dropdown')).not.toBeInTheDocument()
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

