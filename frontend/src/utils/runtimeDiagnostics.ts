interface RuntimeDiagnostic {
  id: string
  message: string
  stack?: string
  source: string
  timestamp: number
}

const MAX_DIAGNOSTIC_ENTRIES = 12
const diagnostics: RuntimeDiagnostic[] = []
let listenersAttached = false

const pushDiagnostic = (entry: RuntimeDiagnostic) => {
  diagnostics.push(entry)
  if (diagnostics.length > MAX_DIAGNOSTIC_ENTRIES) {
    diagnostics.shift()
  }
  if (typeof window !== 'undefined') {
    const win = window as Window & { __OSDASH_RUNTIME_ERRORS__?: RuntimeDiagnostic[] }
    win.__OSDASH_RUNTIME_ERRORS__ = [...diagnostics]
  }
}

const buildEntry = (message: string, source?: string, stack?: string): RuntimeDiagnostic => ({
  id: `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 7)}`,
  message: message || 'Unknown error',
  stack,
  source: source || 'runtime',
  timestamp: Date.now(),
})

export const recordRuntimeDiagnostic = (message: string, source?: string, stack?: string) => {
  pushDiagnostic(buildEntry(message, source, stack))
}

export const getRuntimeDiagnostics = (): RuntimeDiagnostic[] => {
  return [...diagnostics].reverse()
}

const safeStringify = (value: unknown): string => {
  if (typeof value === 'string') {
    return value
  }
  try {
    return JSON.stringify(value)
  } catch {
    return String(value)
  }
}

export const attachRuntimeDiagnostics = (): void => {
  if (listenersAttached || typeof window === 'undefined') {
    return
  }
  listenersAttached = true

  window.addEventListener('error', (event) => {
    const message = event.message || 'Unhandled error'
    const source = event.filename ? `${event.filename}:${event.lineno ?? 0}` : 'window.onerror'
    const stack = event.error instanceof Error ? event.error.stack : undefined
    recordRuntimeDiagnostic(message, source, stack)
  })

  window.addEventListener('unhandledrejection', (event) => {
    let message = 'Unhandled promise rejection'
    let stack: string | undefined
    if (event.reason instanceof Error) {
      message = event.reason.message
      stack = event.reason.stack
    } else if (event.reason) {
      message = safeStringify(event.reason)
    }
    recordRuntimeDiagnostic(message, 'unhandledrejection', stack)
  })
}

export type { RuntimeDiagnostic }
