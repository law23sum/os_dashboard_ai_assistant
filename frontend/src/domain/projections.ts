import apiClient, { apiPath } from '../lib/apiClient'

type ProjectionCallback = (data: unknown) => void

type EventPayload = {
  type: string
  payload: Record<string, unknown>
  correlationId: string
  timestamp: string
}

const projectionStore = new Map<string, unknown>()
const subscribers = new Map<string, Set<ProjectionCallback>>()
let eventSource: EventSource | null = null

const ledgerEventPath = () => apiPath('ledger/events')
const ledgerProjectionPath = () => apiPath('ledger/projections')
const ledgerStreamPath = () => apiPath('ledger/stream')

const safeParseJson = (value: string) => {
  try {
    return JSON.parse(value)
  } catch {
    return null
  }
}

const notifySubscribers = (key: string, data: unknown) => {
  const listeners = subscribers.get(key)
  if (!listeners) return
  listeners.forEach((listener) => listener(data))
}

export function buildProjectionKey(
  scope: string,
  featureKey: string,
  correlationId: string,
) {
  return `${scope}:${featureKey}:${correlationId}`
}

export function emitEvent(
  type: string,
  payload: Record<string, unknown>,
  correlationId: string,
): EventPayload {
  const eventPayload: EventPayload = {
    type,
    payload,
    correlationId,
    timestamp: new Date().toISOString(),
  }
  if (typeof window !== 'undefined') {
    window.dispatchEvent(new CustomEvent('osd:event', { detail: eventPayload }))
  }
  void apiClient
    .post(ledgerEventPath(), eventPayload)
    .catch(() => undefined)
  return eventPayload
}

export function publishProjectionUpdate(key: string, data: unknown) {
  projectionStore.set(key, data)
  notifySubscribers(key, data)
  void apiClient
    .post(ledgerProjectionPath(), { projection_key: key, data })
    .catch(() => undefined)
}

export function subscribeToProjection(key: string, callback: ProjectionCallback) {
  if (!subscribers.has(key)) {
    subscribers.set(key, new Set())
  }
  subscribers.get(key)?.add(callback)
  if (projectionStore.has(key)) {
    callback(projectionStore.get(key))
  }
  if (typeof window !== 'undefined' && typeof EventSource !== 'undefined' && !eventSource) {
    eventSource = new EventSource(ledgerStreamPath())
    eventSource.onmessage = (event) => {
      const payload = safeParseJson(event.data)
      if (!payload || payload.type !== 'projection_updated') return
      const projectionKey = payload.projection_key
      if (!projectionKey) return
      projectionStore.set(projectionKey, payload.data)
      notifySubscribers(projectionKey, payload.data)
    }
    eventSource.onerror = () => {
      // Keep local projections working even if the stream fails.
    }
  }
  return () => {
    subscribers.get(key)?.delete(callback)
    if (subscribers.get(key)?.size === 0) {
      subscribers.delete(key)
    }
    if (subscribers.size === 0 && eventSource) {
      eventSource.close()
      eventSource = null
    }
  }
}
