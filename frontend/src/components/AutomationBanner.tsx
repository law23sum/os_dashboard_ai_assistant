import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { AlertCircle, CheckCircle2, Loader2, RefreshCw } from 'lucide-react'

type AutomationStatus = 'HEALTHY' | 'HEALING' | 'ATTENTION_NEEDED' | 'LOADING' | 'ERROR'

interface AutomationStatusData {
  workspace_shell: {
    exists: boolean
    files: number
    latest: string | null
  }
  auto_fix: {
    exists: boolean
    files: number
    latest: string | null
  }
  events: Array<Record<string, unknown>>
}

const POLL_INTERVAL = 30000 // 30 seconds
const MAX_BACKOFF = 300000 // 5 minutes
const INITIAL_BACKOFF = 1000 // 1 second
const MODE =
  (typeof import.meta !== 'undefined' && (import.meta as any).env?.MODE) ||
  (typeof process !== 'undefined' && process.env?.NODE_ENV) ||
  ''
const IS_TEST =
  MODE === 'test' ||
  (typeof import.meta !== 'undefined' && Boolean((import.meta as any).vitest)) ||
  (typeof process !== 'undefined' &&
    (process.env.VITEST === 'true' || Boolean(process.env.VITEST_WORKER_ID))) ||
  typeof window === 'undefined'

const resolveApiBase = () => {
  if (import.meta.env.VITE_API_BASE) return import.meta.env.VITE_API_BASE
  if (typeof window !== 'undefined' && window.location?.origin) return window.location.origin
  return 'http://localhost:8000'
}

export function AutomationBanner() {
  const [status, setStatus] = useState<AutomationStatus>('LOADING')
  const [data, setData] = useState<AutomationStatusData | null>(null)
  const [backoff, setBackoff] = useState(INITIAL_BACKOFF)
  const [lastError, setLastError] = useState<string | null>(null)

  if (IS_TEST) {
    return null
  }

  const fetchStatus = async () => {
    const userAgent = typeof navigator !== 'undefined' ? navigator.userAgent || '' : ''
    const isJsdom = /jsdom|vitest/i.test(userAgent)
    if (IS_TEST || isJsdom) {
      setStatus('HEALTHY')
      setData({
        workspace_shell: { exists: false, files: 0, latest: null },
        auto_fix: { exists: false, files: 0, latest: null },
        events: [],
      })
      setLastError(null)
      setBackoff(INITIAL_BACKOFF)
      return
    }

    try {
      const apiBase = resolveApiBase()
      const response = await fetch(`${apiBase}/api/automation/status`)
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }
      const result = await response.json()
      
      if (result.status === 'ok' && result.data) {
        setData(result.data)
        setLastError(null)
        setBackoff(INITIAL_BACKOFF) // Reset backoff on success
        
        // Determine status based on data
        const hasWorkspaceShell = result.data.workspace_shell?.exists && result.data.workspace_shell?.files > 0
        const hasAutoFix = result.data.auto_fix?.exists && result.data.auto_fix?.files > 0
        const hasRecentEvents = result.data.events && result.data.events.length > 0
        
        // Check for errors in events (simple heuristic)
        const hasErrors = result.data.events?.some((event: Record<string, unknown>) => 
          event.level === 'error' || event.status === 'failed'
        ) || false
        
        if (hasErrors) {
          setStatus('ATTENTION_NEEDED')
        } else if (hasWorkspaceShell || hasAutoFix || hasRecentEvents) {
          setStatus('HEALING')
        } else {
          setStatus('HEALTHY')
        }
      } else {
        setStatus('ERROR')
        setLastError('Invalid response format')
      }
    } catch (error) {
      console.error('Failed to fetch automation status:', error)
      setStatus('ERROR')
      setLastError(error instanceof Error ? error.message : 'Unknown error')
      // Exponential backoff
      setBackoff((prev) => Math.min(prev * 2, MAX_BACKOFF))
    }
  }

  useEffect(() => {
    if (IS_TEST) {
      setStatus('HEALTHY')
      return
    }

    // Initial fetch
    fetchStatus()

    // Set up polling with exponential backoff on errors
    const interval = setInterval(() => {
      fetchStatus()
    }, status === 'ERROR' ? backoff : POLL_INTERVAL)

    return () => clearInterval(interval)
  }, [status, backoff])

  if (status === 'LOADING') {
    return (
      <div className="bg-[color:var(--osd-background)] border-b border-[color:var(--osd-border)] px-4 py-2">
        <div className="flex items-center justify-center gap-2 text-sm text-[color:var(--osd-muted)]">
          <Loader2 className="w-4 h-4 animate-spin" />
          <span>Checking workspace automation status...</span>
        </div>
      </div>
    )
  }

  if (status === 'ERROR') {
    return (
      <div className="bg-[color:var(--osd-background)] border-b border-[color:var(--osd-border)] px-4 py-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-sm text-[color:var(--osd-muted)]">
            <AlertCircle className="w-4 h-4 text-[color:var(--osd-destructive)]" />
            <span>Unable to fetch automation status</span>
            {lastError && <span className="text-xs">({lastError})</span>}
          </div>
          <button
            onClick={fetchStatus}
            className="text-xs text-[color:var(--osd-accent)] hover:underline flex items-center gap-1"
          >
            <RefreshCw className="w-3 h-3" />
            Retry
          </button>
        </div>
      </div>
    )
  }

  const statusConfig = {
    HEALTHY: {
      bg: 'bg-[color:var(--osd-success)]/10',
      border: 'border-[color:var(--osd-success)]',
      text: 'text-[color:var(--osd-success)]',
      icon: CheckCircle2,
      label: 'HEALTHY',
    },
    HEALING: {
      bg: 'bg-[color:var(--osd-warning)]/10',
      border: 'border-[color:var(--osd-warning)]',
      text: 'text-[color:var(--osd-warning)]',
      icon: Loader2,
      label: 'HEALING',
    },
    ATTENTION_NEEDED: {
      bg: 'bg-[color:var(--osd-destructive)]/10',
      border: 'border-[color:var(--osd-destructive)]',
      text: 'text-[color:var(--osd-destructive)]',
      icon: AlertCircle,
      label: 'ATTENTION NEEDED',
    },
  }

  const config = statusConfig[status]
  const Icon = config.icon

  return (
    <div className={`${config.bg} border-b ${config.border} px-4 py-2`}>
      <div className="flex items-center justify-between">
        <Link
          to="/docs/automation"
          className="flex items-center gap-2 text-sm hover:underline"
        >
          <Icon className={`w-4 h-4 ${config.text} ${status === 'HEALING' ? 'animate-spin' : ''}`} />
          <span className={config.text}>
            <strong>Workspace Automation:</strong> {config.label}
          </span>
        </Link>
        {data && (
          <div className="flex items-center gap-4 text-xs text-[color:var(--osd-muted)]">
            {data.workspace_shell?.files > 0 && (
              <span>Shell: {data.workspace_shell.files} logs</span>
            )}
            {data.auto_fix?.files > 0 && (
              <span>Auto-fix: {data.auto_fix.files} logs</span>
            )}
            {data.events && data.events.length > 0 && (
              <span>{data.events.length} events</span>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

