import { describe, expect, it } from 'vitest'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter, Route, Routes, useLocation } from 'react-router-dom'
import Layout from '../Layout'

function LocationEcho() {
  const location = useLocation()
  return <div data-testid="location">{location.pathname}</div>
}

describe('Layout navigation hierarchy', () => {
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

  it('opens and closes a platform dropdown (not sticky)', async () => {
    renderLayoutAt('/tasks')

    const button = screen.getAllByRole('button', { name: 'Mission Control' })[0]
    fireEvent.click(button)

    await waitFor(() => {
      expect(document.body.querySelector('.osd-dropdown')).toBeTruthy()
    })

    // Click again to close
    fireEvent.click(button)
    await waitFor(() => {
      expect(document.body.querySelector('.osd-dropdown')).toBeFalsy()
    })
  })

  it('closes on Escape', async () => {
    renderLayoutAt('/')

    const button = screen.getAllByRole('button', { name: 'Mission Control' })[0]
    fireEvent.click(button)

    await waitFor(() => {
      expect(document.body.querySelector('.osd-dropdown')).toBeTruthy()
    })

    fireEvent.keyDown(document, { key: 'Escape' })

    await waitFor(() => {
      expect(document.body.querySelector('.osd-dropdown')).toBeFalsy()
    })
  })

  it('navigates when selecting a dropdown category and closes', async () => {
    renderLayoutAt('/')

    const button = screen.getAllByRole('button', { name: 'Mission Control' })[0]
    fireEvent.click(button)

    await waitFor(() => {
      expect(document.body.querySelector('.osd-dropdown')).toBeTruthy()
    })

    // Select a category (group) whose first page is /chat
    fireEvent.click(screen.getByText('Engagement & Persona Surfaces'))

    await waitFor(() => {
      expect(document.body.querySelector('.osd-dropdown')).toBeFalsy()
      expect(screen.getByTestId('location').textContent).toBe('/chat')
    })
  })
})
