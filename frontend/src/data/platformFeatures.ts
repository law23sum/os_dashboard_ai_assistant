export type PlatformFeature = {
  /** Stable id used for keys + hashes. */
  id: string
  /** Human label shown in left sidebar. */
  label: string
  /** Optional short description (tooltip / subtext). */
  description?: string
  /** Target hash (e.g. "#ledger") or full path (e.g. "/projects"). */
  href: string
}

/**
 * Hybrid topology map:
 * - Tree: the top navigation tabs (categories) live in `Layout.tsx`.
 * - Network: dropdown “platforms” live in those categories.
 * - For each platform route, this map defines the ordered feature list shown in
 *   the left sidebar (simple/common → advanced/specialized).
 */
export const PLATFORM_FEATURES_BY_ROUTE_PREFIX: Array<{
  routePrefix: string
  features: PlatformFeature[]
}> = [
  {
    routePrefix: '/',
    features: [
      { id: 'overview', label: 'Overview', href: '#overview' },
      { id: 'task-pulse', label: 'Task pulse', href: '#task-pulse' },
      { id: 'persona-focus', label: 'Persona focus', href: '#persona-focus' },
      { id: 'system-health', label: 'System health', href: '#system-health' },
      { id: 'project-pulse', label: 'Project pulse', href: '#project-pulse' },
      { id: 'search', label: 'Search', href: '#search' },
      { id: 'daemons', label: 'Daemons', href: '#daemons' },
      { id: 'operations', label: 'Operations & audit', href: '#operations' },
      { id: 'planes', label: 'Planes status', href: '#planes' },
    ],
  },
  {
    routePrefix: '/dashboard',
    features: [
      { id: 'overview', label: 'Overview', href: '#overview' },
      { id: 'task-pulse', label: 'Task pulse', href: '#task-pulse' },
      { id: 'persona-focus', label: 'Persona focus', href: '#persona-focus' },
      { id: 'system-health', label: 'System health', href: '#system-health' },
      { id: 'project-pulse', label: 'Project pulse', href: '#project-pulse' },
      { id: 'search', label: 'Search', href: '#search' },
      { id: 'daemons', label: 'Daemons', href: '#daemons' },
      { id: 'operations', label: 'Operations & audit', href: '#operations' },
      { id: 'planes', label: 'Planes status', href: '#planes' },
    ],
  },
  {
    routePrefix: '/projects',
    features: [
      { id: 'overview', label: 'Overview', href: '#overview' },
      { id: 'create', label: 'Create / update', href: '#create' },
      { id: 'workspaces', label: 'Workspaces list', href: '#workspaces' },
      { id: 'links', label: 'Linked docs', href: '#links' },
      { id: 'ledger', label: 'Ledger', href: '#ledger' },
      { id: 'intelligence', label: 'Intelligence', href: '#intelligence' },
      { id: 'trf', label: 'TRF traces', href: '#trf' },
      { id: 'reasoning', label: 'Reasoning lab', href: '#reasoning' },
    ],
  },
  {
    routePrefix: '/tasks',
    features: [
      { id: 'overview', label: 'Overview', href: '#overview' },
      { id: 'create', label: 'Create task', href: '#create' },
      { id: 'filters', label: 'Filters & counts', href: '#filters' },
      { id: 'list', label: 'Task list', href: '#list' },
      { id: 'summary', label: 'Summary', href: '#summary' },
    ],
  },
]

export function getPlatformFeatures(pathname: string): PlatformFeature[] | null {
  const match = PLATFORM_FEATURES_BY_ROUTE_PREFIX.find((entry) => {
    if (entry.routePrefix === '/') return pathname === '/'
    return pathname === entry.routePrefix || pathname.startsWith(`${entry.routePrefix}/`)
  })
  return match?.features ?? null
}

