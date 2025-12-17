/**
 * React Query hooks for Auto-Fix & Self-Healing System (v1000)
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { API } from '../api'
import type { AutoFixIssue, AutoFixReport, AutoFixConfiguration } from '../types'

const QUERY_KEYS = {
  status: ['autofix', 'status'] as const,
  config: ['autofix', 'config'] as const,
  issues: (status?: string) => ['autofix', 'issues', status] as const,
  reports: (limit: number) => ['autofix', 'reports', limit] as const,
  report: (id: string) => ['autofix', 'report', id] as const,
}

export function useAutoFixStatus() {
  return useQuery<{ enabled: boolean; last_scan: string; issues_pending: number }>({
    queryKey: QUERY_KEYS.status,
    queryFn: () => API.autoFix.status(),
    refetchInterval: 30000,
  })
}

export function useAutoFixConfig() {
  return useQuery<AutoFixConfiguration>({
    queryKey: QUERY_KEYS.config,
    queryFn: () => API.autoFix.config(),
  })
}

export function useUpdateAutoFixConfig() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (config: Partial<AutoFixConfiguration>) => API.autoFix.updateConfig(config),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: QUERY_KEYS.config }),
  })
}

export function useAutoFixIssues(status?: string) {
  return useQuery<AutoFixIssue[]>({
    queryKey: QUERY_KEYS.issues(status),
    queryFn: () => API.autoFix.issues(status),
    refetchInterval: 15000,
  })
}

export function useAutoFixReports(limit = 10) {
  return useQuery<AutoFixReport[]>({
    queryKey: QUERY_KEYS.reports(limit),
    queryFn: () => API.autoFix.reports(limit),
    staleTime: 60000,
  })
}

export function useAutoFixReport(id: string) {
  return useQuery<AutoFixReport>({
    queryKey: QUERY_KEYS.report(id),
    queryFn: () => API.autoFix.report(id),
    enabled: !!id,
  })
}

export function useTriggerAutoFixScan() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: () => API.autoFix.scan(),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['autofix'] }),
  })
}

export function useApplyAutoFix() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (issueId: string) => API.autoFix.applyFix(issueId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['autofix', 'issues'] })
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.status })
    },
  })
}

export function useSkipAutoFixIssue() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (issueId: string) => API.autoFix.skipIssue(issueId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['autofix', 'issues'] })
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.status })
    },
  })
}

export function getIssueTypeColor(type: string): string {
  const colors: Record<string, string> = {
    error: 'text-red-600 bg-red-100 dark:text-red-400 dark:bg-red-900/30',
    warning: 'text-amber-600 bg-amber-100 dark:text-amber-400 dark:bg-amber-900/30',
    lint: 'text-blue-600 bg-blue-100 dark:text-blue-400 dark:bg-blue-900/30',
    security: 'text-purple-600 bg-purple-100 dark:text-purple-400 dark:bg-purple-900/30',
    performance: 'text-cyan-600 bg-cyan-100 dark:text-cyan-400 dark:bg-cyan-900/30',
  }
  return colors[type] ?? colors.warning
}

export function getAutoFixStatusColor(status: string): string {
  const colors: Record<string, string> = {
    pending: 'text-gray-600 bg-gray-100 dark:text-gray-400 dark:bg-gray-700/50',
    analyzing: 'text-blue-600 bg-blue-100 dark:text-blue-400 dark:bg-blue-900/30',
    fixing: 'text-amber-600 bg-amber-100 dark:text-amber-400 dark:bg-amber-900/30',
    applied: 'text-emerald-600 bg-emerald-100 dark:text-emerald-400 dark:bg-emerald-900/30',
    failed: 'text-red-600 bg-red-100 dark:text-red-400 dark:bg-red-900/30',
    skipped: 'text-gray-500 bg-gray-100 dark:text-gray-500 dark:bg-gray-700/30',
  }
  return colors[status] ?? colors.pending
}

export function formatConfidence(confidence: number): string {
  if (confidence >= 0.9) return 'Very High'
  if (confidence >= 0.7) return 'High'
  if (confidence >= 0.5) return 'Medium'
  if (confidence >= 0.3) return 'Low'
  return 'Very Low'
}






