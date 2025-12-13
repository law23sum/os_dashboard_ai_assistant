/**
 * React Query hooks for Observability & Runtime Diagnostics (v1000)
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { API } from '../api'
import type { ObservabilitySnapshot, RuntimeDiagnosticEvent, AIRemediationSuggestion, ObservabilityMetrics } from '../types'

const QUERY_KEYS = {
  snapshot: ['observability', 'snapshot'] as const,
  events: (limit: number, severity?: string) => ['observability', 'events', { limit, severity }] as const,
  suggestions: ['observability', 'suggestions'] as const,
  metrics: ['observability', 'metrics'] as const,
  health: ['observability', 'health'] as const,
}

export function useObservabilitySnapshot() {
  return useQuery<ObservabilitySnapshot>({
    queryKey: QUERY_KEYS.snapshot,
    queryFn: () => API.observability.snapshot(),
    refetchInterval: 15000,
    staleTime: 10000,
  })
}

export function useObservabilityEvents(limit = 100, severity?: string) {
  return useQuery<RuntimeDiagnosticEvent[]>({
    queryKey: QUERY_KEYS.events(limit, severity),
    queryFn: () => API.observability.events(limit, severity),
    refetchInterval: 10000,
  })
}

export function useObservabilitySuggestions() {
  return useQuery<AIRemediationSuggestion[]>({
    queryKey: QUERY_KEYS.suggestions,
    queryFn: () => API.observability.suggestions(),
    refetchInterval: 30000,
  })
}

export function useObservabilityMetrics() {
  return useQuery<ObservabilityMetrics>({
    queryKey: QUERY_KEYS.metrics,
    queryFn: () => API.observability.metrics(),
    refetchInterval: 5000,
  })
}

export function useApplySuggestion() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (suggestionId: string) => API.observability.applySuggestion(suggestionId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['observability'] }),
  })
}

export function useDismissSuggestion() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (suggestionId: string) => API.observability.dismissSuggestion(suggestionId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: QUERY_KEYS.suggestions }),
  })
}

export function getSeverityColor(severity: string): string {
  const colors: Record<string, string> = {
    critical: 'text-red-600 bg-red-100 dark:text-red-400 dark:bg-red-900/30',
    error: 'text-orange-600 bg-orange-100 dark:text-orange-400 dark:bg-orange-900/30',
    warning: 'text-yellow-600 bg-yellow-100 dark:text-yellow-400 dark:bg-yellow-900/30',
    info: 'text-blue-600 bg-blue-100 dark:text-blue-400 dark:bg-blue-900/30',
    debug: 'text-gray-600 bg-gray-100 dark:text-gray-400 dark:bg-gray-700/50',
  }
  return colors[severity] ?? colors.info
}

export function formatEventTime(timestamp: string): string {
  const date = new Date(timestamp)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  if (diffMins < 1) return 'just now'
  if (diffMins < 60) return `${diffMins}m ago`
  const diffHours = Math.floor(diffMins / 60)
  if (diffHours < 24) return `${diffHours}h ago`
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

