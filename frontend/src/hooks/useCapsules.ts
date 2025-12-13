/**
 * React Query hooks for Capsule Marketplace & Blueprints (v1000)
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { API } from '../api'
import type { CapsuleSpec, BlueprintSpec, CapsuleRunLog, CapsuleMarketplaceResponse, CapsuleMarketplaceFilter } from '../types'

const QUERY_KEYS = {
  capsules: (filters?: CapsuleMarketplaceFilter) => ['capsules', 'list', filters] as const,
  capsule: (id: string) => ['capsules', 'detail', id] as const,
  capsuleLogs: (id: string) => ['capsules', 'logs', id] as const,
  featured: ['capsules', 'featured'] as const,
  categories: ['capsules', 'categories'] as const,
  blueprints: ['blueprints', 'list'] as const,
  blueprint: (id: string) => ['blueprints', 'detail', id] as const,
}

export function useCapsuleMarketplace(filters?: CapsuleMarketplaceFilter) {
  return useQuery<CapsuleMarketplaceResponse>({
    queryKey: QUERY_KEYS.capsules(filters),
    queryFn: () => API.capsules.list(filters),
    staleTime: 60000,
  })
}

export function useCapsule(id: string) {
  return useQuery<CapsuleSpec>({
    queryKey: QUERY_KEYS.capsule(id),
    queryFn: () => API.capsules.get(id),
    enabled: !!id,
  })
}

export function useCapsuleLogs(id: string, limit = 20) {
  return useQuery<CapsuleRunLog[]>({
    queryKey: QUERY_KEYS.capsuleLogs(id),
    queryFn: () => API.capsules.logs(id, limit),
    enabled: !!id,
    refetchInterval: 10000,
  })
}

export function useFeaturedCapsules() {
  return useQuery<CapsuleSpec[]>({
    queryKey: QUERY_KEYS.featured,
    queryFn: () => API.capsules.featured(),
    staleTime: 300000,
  })
}

export function useCapsuleCategories() {
  return useQuery<string[]>({
    queryKey: QUERY_KEYS.categories,
    queryFn: () => API.capsules.categories(),
    staleTime: 600000,
  })
}

export function useBlueprints() {
  return useQuery<BlueprintSpec[]>({
    queryKey: QUERY_KEYS.blueprints,
    queryFn: () => API.blueprints.list(),
    staleTime: 60000,
  })
}

export function useBlueprint(id: string) {
  return useQuery<BlueprintSpec>({
    queryKey: QUERY_KEYS.blueprint(id),
    queryFn: () => API.blueprints.get(id),
    enabled: !!id,
  })
}

export function useRunCapsule() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, params }: { id: string; params?: Record<string, unknown> }) =>
      API.capsules.run(id, params),
    onSuccess: (_, variables) =>
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.capsuleLogs(variables.id) }),
  })
}

export function useExecuteBlueprint() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, params }: { id: string; params?: Record<string, unknown> }) =>
      API.blueprints.execute(id, params),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['capsules', 'logs'] }),
  })
}

export function getCapsuleStatusColor(status: string): string {
  const colors: Record<string, string> = {
    active: 'text-emerald-600 bg-emerald-100 dark:text-emerald-400 dark:bg-emerald-900/30',
    draft: 'text-amber-600 bg-amber-100 dark:text-amber-400 dark:bg-amber-900/30',
    deprecated: 'text-orange-600 bg-orange-100 dark:text-orange-400 dark:bg-orange-900/30',
    archived: 'text-gray-600 bg-gray-100 dark:text-gray-400 dark:bg-gray-700/50',
  }
  return colors[status] ?? colors.draft
}

export function formatSuccessRate(rate: number): string {
  return `${(rate * 100).toFixed(1)}%`
}

export function formatDuration(ms: number): string {
  if (ms < 1000) return `${ms}ms`
  if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`
  return `${(ms / 60000).toFixed(1)}m`
}

