import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter, Route, Routes, useLocation } from 'react-router-dom'
import Layout from '../Layout'
import { getCategories, getPlatforms, legacyRedirects } from '../../data/iaManifest'

vi.mock('../UnifiedAIPanel', () => ({
  UnifiedAIPanel: () => <div data-testid="ai-panel">AI Panel</div>,
}))

vi.mock('../GlobalSearch', () => ({
  default: () => <div data-testid="global-search" />,
}))

vi.mock('../../hooks/useSettings', () => ({
  useAppSettings: () => ({
    data: { theme: 'default' },
  }),
}))

vi.mock('../../auth/AuthContext', () => ({
  useAuth: () => ({
    state: {
      status: 'authenticated',
      user: {
        id: 'demo',
        email: 'demo@osdash.local',
        display_name: 'Demo User',
        is_admin: false,
        environment: 'test',
      },
    },
    refresh: vi.fn(),
    logout: vi.fn(),
  }),
}))

const getNavDropdownButton = () => {
  const buttons = screen.getAllByRole('button')
  const navButtons = buttons.filter((btn) => btn.classList.contains('osd-nav-link'))
  return navButtons.length > 0 ? navButtons[0] : buttons[0]
}

function LocationEcho() {
  const location = useLocation()
  return <div data-testid="location">{location.pathname}</div>
}

const renderLayoutAt = (path = '/') => {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<LocationEcho />} />
          <Route path="/tasks" element={<LocationEcho />} />
          <Route path="/chat" element={<LocationEcho />} />
          <Route path="*" element={<LocationEcho />} />
        </Route>
      </Routes>
    </MemoryRouter>
  )
}

describe('Layout navigation hierarchy', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    globalThis.requestAnimationFrame = vi.fn((cb) => setTimeout(cb, 16)) as unknown as typeof requestAnimationFrame
    globalThis.cancelAnimationFrame = vi.fn()
  })

  afterEach(() => {
    vi.restoreAllMocks()
    cleanup()
  })

  it('should render layout with navigation', () => {
    renderLayoutAt('/')

    const platforms = getPlatforms('personal')
    const mission = platforms.find((platform) => platform.id === 'mission-control')
    const homePath = mission?.path ?? platforms[0]?.path ?? '/'
    const expectedPath = legacyRedirects['/'] ?? homePath

    expect(screen.getByText('AI OS Console')).toBeInTheDocument()
    expect(screen.getByTestId('location').textContent).toBe(expectedPath)
  })

  it('should open dropdown when nav button clicked', async () => {
    renderLayoutAt('/')

    const navButton = getNavDropdownButton()
    fireEvent.click(navButton)

    await waitFor(() => {
      const dropdown = document.body.querySelector('.osd-dropdown')
      expect(dropdown).toBeInTheDocument()
    })
  })

  it('should close dropdown when clicked again', async () => {
    renderLayoutAt('/')

    const navButton = getNavDropdownButton()
    fireEvent.click(navButton)

    await waitFor(() => {
      expect(document.body.querySelector('.osd-dropdown')).toBeInTheDocument()
    })

    fireEvent.click(navButton)

    await waitFor(() => {
      expect(document.body.querySelector('.osd-dropdown')).not.toBeInTheDocument()
    })
  })

  it('should cleanup on unmount', () => {
    const removeEventListenerSpy = vi.spyOn(document, 'removeEventListener')

    const { unmount } = renderLayoutAt('/')

    const navButton = getNavDropdownButton()
    fireEvent.click(navButton)

    unmount()

    expect(removeEventListenerSpy).toHaveBeenCalled()
    removeEventListenerSpy.mockRestore()
  })

  it('should close dropdown when clicking a link', async () => {
    renderLayoutAt('/')

    const navButton = getNavDropdownButton()
    fireEvent.click(navButton)

    await waitFor(() => {
      expect(document.body.querySelector('.osd-dropdown')).toBeInTheDocument()
    })

    const menuItems = screen.getAllByRole('menuitem')
    fireEvent.click(menuItems[0])

    await waitFor(() => {
      expect(document.body.querySelector('.osd-dropdown')).not.toBeInTheDocument()
    })
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

    renderLayoutAt('/')

    const navButton = getNavDropdownButton()
    fireEvent.click(navButton)

    await waitFor(() => {
      expect(document.body.querySelector('.osd-dropdown')).toBeInTheDocument()
    })

    expect(getBoundingClientRectSpy).toHaveBeenCalled()
    getBoundingClientRectSpy.mockRestore()
  })

  it('closes on Escape', async () => {
    renderLayoutAt('/')

    const navButton = getNavDropdownButton()
    fireEvent.click(navButton)

    await waitFor(() => {
      expect(document.body.querySelector('.osd-dropdown')).toBeInTheDocument()
    })

    fireEvent.keyDown(document, { key: 'Escape' })

    await waitFor(() => {
      expect(document.body.querySelector('.osd-dropdown')).not.toBeInTheDocument()
    })
  })

  it('navigates when selecting a dropdown category and closes', async () => {
    renderLayoutAt('/')

    const navButton = getNavDropdownButton()
    fireEvent.click(navButton)

    await waitFor(() => {
      expect(document.body.querySelector('.osd-dropdown')).toBeInTheDocument()
    })

    const platforms = getPlatforms('personal')
    const mission = platforms.find((platform) => platform.id === 'mission-control') ?? platforms[0]
    const categories = getCategories(mission.id, 'personal')
    const targetCategory = categories.find((category) => category.label === 'Engagement & Persona Surfaces')

    expect(targetCategory).toBeTruthy()
    fireEvent.click(screen.getByText(targetCategory?.label ?? 'Engagement & Persona Surfaces'))

    await waitFor(() => {
      expect(document.body.querySelector('.osd-dropdown')).not.toBeInTheDocument()
      expect(screen.getByTestId('location').textContent).toBe(targetCategory?.homeRoute)
    })
  })
})
