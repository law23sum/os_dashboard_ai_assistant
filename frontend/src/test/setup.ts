import React from 'react'
import { expect, afterEach, vi } from 'vitest'
import { cleanup } from '@testing-library/react'
import * as matchers from '@testing-library/jest-dom/matchers'

const routerFutureFlags = {
  v7_startTransition: true,
  v7_relativeSplatPath: true,
}

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual<typeof import('react-router-dom')>('react-router-dom')

  const BrowserRouter = (props: React.ComponentProps<typeof actual.BrowserRouter>) => {
    const { future, ...rest } = props
    return React.createElement(actual.BrowserRouter, {
      ...rest,
      future: { ...routerFutureFlags, ...future },
    })
  }

  const MemoryRouter = (props: React.ComponentProps<typeof actual.MemoryRouter>) => {
    const { future, ...rest } = props
    return React.createElement(actual.MemoryRouter, {
      ...rest,
      future: { ...routerFutureFlags, ...future },
    })
  }

  return { ...actual, BrowserRouter, MemoryRouter }
})

vi.mock('react-router', async () => {
  const actual = await vi.importActual<typeof import('react-router')>('react-router')

  const MemoryRouter = (props: React.ComponentProps<typeof actual.MemoryRouter>) => {
    const { future, ...rest } = props
    return React.createElement(actual.MemoryRouter, {
      ...rest,
      future: { ...routerFutureFlags, ...future },
    })
  }

  return { ...actual, MemoryRouter }
})

vi.mock('../auth/AuthContext', async () => {
  const actual = await vi.importActual<typeof import('../auth/AuthContext')>('../auth/AuthContext')
  return {
    ...actual,
    useAuth: vi.fn(() => ({
      state: { status: 'authenticated', user: { is_admin: true } },
      refresh: vi.fn(),
      logout: vi.fn(),
    })),
  }
})

vi.mock('../contexts/ActorContext', async () => {
  const actual = await vi.importActual<typeof import('../contexts/ActorContext')>('../contexts/ActorContext')
  return {
    ...actual,
    useActor: vi.fn(() => ({
      currentActor: 'personal',
      setCurrentActor: vi.fn(),
      isPersonal: true,
      isEnterprise: false,
    })),
  }
})

const originalConsoleError = console.error
console.error = (...args) => {
  const message = args.map(String).join(' ')
  if (message.includes('not wrapped in act')) {
    return
  }
  originalConsoleError(...args)
}

const originalEmitWarning = process.emitWarning.bind(process)
process.emitWarning = ((warning, ...args) => {
  const message = typeof warning === 'string' ? warning : warning?.message
  if (message && message.includes('--localstorage-file')) {
    return
  }
  return originalEmitWarning(warning as Parameters<typeof originalEmitWarning>[0], ...args)
}) as typeof process.emitWarning

if (!globalThis.localStorage || typeof globalThis.localStorage.clear !== 'function') {
  const store = new Map<string, string>()
  const localStorageMock = {
    getItem: (key: string) => (store.has(key) ? store.get(key)! : null),
    setItem: (key: string, value: string) => {
      store.set(key, value)
    },
    removeItem: (key: string) => {
      store.delete(key)
    },
    clear: () => {
      store.clear()
    },
    key: (index: number) => Array.from(store.keys())[index] ?? null,
    get length() {
      return store.size
    },
  }

  globalThis.localStorage = localStorageMock as Storage
  if (globalThis.window) {
    globalThis.window.localStorage = localStorageMock as Storage
  }
}

// Extend Vitest's expect with jest-dom matchers
expect.extend(matchers)

// Cleanup after each test
afterEach(() => {
  cleanup()
})






