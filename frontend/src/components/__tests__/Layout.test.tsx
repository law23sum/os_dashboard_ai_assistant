import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, fireEvent, waitFor, cleanup } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import Layout from '../Layout'

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

// Helper to get the first nav dropdown button
const getNavDropdownButton = () => {
  // Get all buttons and find the first one that looks like a nav dropdown
  const buttons = screen.getAllByRole('button')
  const navButtons = buttons.filter(btn => btn.classList.contains('osd-nav-link'))
  return navButtons.length > 0 ? navButtons[0] : buttons[0]
}

describe('Layout NavDropdown Performance', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    global.requestAnimationFrame = vi.fn((cb) => setTimeout(cb, 16))
    global.cancelAnimationFrame = vi.fn()
  })

  afterEach(() => {
    vi.restoreAllMocks()
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

  it('should render layout with navigation', async () => {
    renderLayout()
    
    // Check that layout rendered with content
    expect(screen.getByText('Test Content')).toBeInTheDocument()
    
    // Check for navigation elements
    expect(screen.getByText('OS Dashboard · AI Assistant')).toBeInTheDocument()
  })

  it('should open dropdown when nav button clicked', async () => {
    renderLayout()
    
    const navButton = getNavDropdownButton()
    if (navButton) {
      fireEvent.click(navButton)

      // Dropdown should be visible (portaled to document.body)
      await waitFor(() => {
        const dropdown = document.body.querySelector('.osd-dropdown')
        expect(dropdown).toBeInTheDocument()
      }, { timeout: 500 })
    }
  })

  it('should close dropdown when clicked again', async () => {
    renderLayout()
    
    const navButton = getNavDropdownButton()
    if (!navButton) return
    
    // Open dropdown
    fireEvent.click(navButton)
    await waitFor(() => {
      const dropdown = document.body.querySelector('.osd-dropdown')
      expect(dropdown).toBeInTheDocument()
    }, { timeout: 500 })

    // Close dropdown
    fireEvent.click(navButton)
    await waitFor(() => {
      const dropdown = document.body.querySelector('.osd-dropdown')
      expect(dropdown).not.toBeInTheDocument()
    }, { timeout: 500 })
  })

  it('should cleanup on unmount', () => {
    const removeEventListenerSpy = vi.spyOn(document, 'removeEventListener')

    const { unmount } = renderLayout()
    
    const navButton = getNavDropdownButton()
    if (navButton) {
      fireEvent.click(navButton)
    }

    unmount()

    // Verify cleanup happened
    expect(removeEventListenerSpy).toHaveBeenCalled()
    removeEventListenerSpy.mockRestore()
  })

  it('should close dropdown when clicking a link', async () => {
    renderLayout()
    
    const navButton = getNavDropdownButton()
    if (!navButton) return
    
    // Open dropdown
    fireEvent.click(navButton)
    await waitFor(() => {
      const dropdown = document.body.querySelector('.osd-dropdown')
      expect(dropdown).toBeInTheDocument()
    }, { timeout: 500 })

    // Click a link inside dropdown
    const dropdown = document.body.querySelector('.osd-dropdown')
    const link = dropdown?.querySelector('a')
    if (link) {
      fireEvent.click(link)
    }

    // Dropdown should close after clicking link
    await waitFor(() => {
      expect(document.body.querySelector('.osd-dropdown')).not.toBeInTheDocument()
    }, { timeout: 500 })
  })

  it('should position dropdown correctly', async () => {
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
    
    const navButton = getNavDropdownButton()
    if (navButton) {
      fireEvent.click(navButton)

      await waitFor(() => {
        const dropdown = document.body.querySelector('.osd-dropdown') as HTMLElement
        expect(dropdown).toBeInTheDocument()
      }, { timeout: 500 })

      expect(getBoundingClientRectSpy).toHaveBeenCalled()
    }

    getBoundingClientRectSpy.mockRestore()
  })
})
