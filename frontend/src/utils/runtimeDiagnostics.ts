import apiClient, { apiPath } from '../lib/apiClient'

export interface ClientDiagnosticPayload {
  source: string
  message: string
  stack?: string | null
  severity?: 'error' | 'warning' | 'info'
  context?: Record<string, unknown>
}

const ENDPOINT = apiPath('runtime/diagnostics')

const serializePayload = (payload: ClientDiagnosticPayload) => ({
  source: payload.source,
  message: payload.message,
  stack: payload.stack ?? null,
  severity: payload.severity ?? 'error',
  context: {
    ...payload.context,
    userAgent: typeof navigator !== 'undefined' ? navigator.userAgent : 'unknown',
    url: typeof window !== 'undefined' ? window.location.href : 'unknown',
  },
})

export function reportClientError(payload: ClientDiagnosticPayload): void {
  const body = JSON.stringify(serializePayload(payload))
  if (typeof navigator !== 'undefined' && navigator.sendBeacon) {
    const blob = new Blob([body], { type: 'application/json' })
    const url =
      ENDPOINT.startsWith('http://') || ENDPOINT.startsWith('https://')
        ? ENDPOINT
        : ENDPOINT.startsWith('/')
          ? ENDPOINT
          : `/${ENDPOINT}`
    const sent = navigator.sendBeacon(url, blob)
    if (sent) {
      return
    }
  }
  apiClient
    .post(ENDPOINT, JSON.parse(body))
    .catch((error) => console.error('[RuntimeDiagnostics] Failed to report error', error))
}

let diagnosticsAttached = false

export function attachRuntimeDiagnostics() {
  if (diagnosticsAttached || typeof window === 'undefined') {
    return
  }
  diagnosticsAttached = true

  window.addEventListener('error', (event) => {
    if (!event.error) {
      return
    }
    reportClientError({
      source: 'window.error',
      message: event.error.message,
      stack: event.error.stack ?? null,
    })
  })

  window.addEventListener('unhandledrejection', (event) => {
    const reason =
      event.reason instanceof Error ? event.reason : new Error(typeof event.reason === 'string' ? event.reason : 'Promise rejection')
    reportClientError({
      source: 'window.unhandledrejection',
      message: reason.message,
      stack: reason.stack ?? null,
      context: { reason: event.reason },
    })
  })
}

export function recordRuntimeDiagnostic(message: string, source: string, context?: Record<string, unknown>) {
  reportClientError({
    source,
    message,
    context,
    severity: 'info',
  })
}
