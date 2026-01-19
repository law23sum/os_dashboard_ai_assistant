import { useMemo } from 'react'
import contracts from './page-contracts.json'

export type PageContract = {
  route: string
  role: 'category_home' | 'feature'
  entities: string[]
  projections: string[]
  emits_events?: string[]
  params: string[]
  configs: string[]
  dimensions: string[]
  compute_class: 'fast' | 'standard' | 'heavy'
  summary?: string
}

const contractMap = new Map<string, PageContract>(
  (contracts as PageContract[]).map((contract) => [contract.route, contract]),
)

export function getPageContract(route: string): PageContract | undefined {
  const normalized = route === '/' ? '/' : route.replace(/\/+$/, '')
  return contractMap.get(normalized)
}

export function usePageContract(route: string): PageContract | undefined {
  return useMemo(() => getPageContract(route), [route])
}
