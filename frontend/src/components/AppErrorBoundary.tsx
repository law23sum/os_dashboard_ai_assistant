import { Component, ErrorInfo, ReactNode } from 'react'
import { getRuntimeDiagnostics, recordRuntimeDiagnostic } from '../utils/runtimeDiagnostics'

interface AppErrorBoundaryProps {
  children: ReactNode
}

interface AppErrorBoundaryState {
  error: Error | null
}

export default class AppErrorBoundary extends Component<AppErrorBoundaryProps, AppErrorBoundaryState> {
  state: AppErrorBoundaryState = {
    error: null,
  }

  static getDerivedStateFromError(error: Error): AppErrorBoundaryState {
    return { error }
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    recordRuntimeDiagnostic(error.message, 'AppErrorBoundary', info?.componentStack)
    console.error('OS Dashboard UI crashed', error, info)
  }

  private handleReload = () => {
    if (typeof window !== 'undefined') {
      window.location.reload()
    }
  }

  private handleCopyDiagnostics = () => {
    if (typeof navigator === 'undefined' || !navigator.clipboard) return
    const diagnostics = getRuntimeDiagnostics()
    const payload = diagnostics
      .map((entry) => {
        const timestamp = new Date(entry.timestamp).toISOString()
        return `[${timestamp}] ${entry.source}: ${entry.message}${entry.stack ? `\n${entry.stack}` : ''}`
      })
      .join('\n\n')
    navigator.clipboard.writeText(payload).catch(() => {
      /* no-op */
    })
  }

  render(): ReactNode {
    const { error } = this.state
    if (error) {
      const diagnostics = getRuntimeDiagnostics()
      return (
        <div className="min-h-screen bg-slate-950 text-slate-100 flex items-center justify-center px-4">
          <div className="max-w-3xl space-y-4">
            <div>
              <p className="text-xs uppercase tracking-[0.4em] text-slate-400">Runtime Error</p>
              <h1 className="text-2xl font-semibold">We could not render the dashboard shell.</h1>
              <p className="text-sm text-slate-300">
                The UI surfaced a fatal error before it could paint. Reload the page, or collect the diagnostics below
                and share them with the engineering team. Desktop users can also check the Electron console (View →
                Toggle Developer Tools).
              </p>
            </div>
            <div className="rounded-xl border border-white/10 bg-black/40 p-4 text-sm">
              <p className="font-semibold text-white">Error</p>
              <p className="mt-1 font-mono text-red-300">{error.message}</p>
              {error.stack && (
                <pre className="mt-3 max-h-60 overflow-auto rounded-lg bg-black/30 p-3 text-xs text-slate-300">
                  {error.stack}
                </pre>
              )}
            </div>
            {diagnostics.length > 0 && (
              <div className="rounded-xl border border-white/10 bg-black/40 p-4 text-sm">
                <div className="flex items-center justify-between">
                  <p className="font-semibold text-white">Recent runtime diagnostics</p>
                  <button
                    type="button"
                    className="text-xs font-semibold text-primary-300 hover:text-primary-200"
                    onClick={this.handleCopyDiagnostics}
                  >
                    Copy log
                  </button>
                </div>
                <ul className="mt-3 space-y-2 text-xs">
                  {diagnostics.slice(0, 5).map((entry) => (
                    <li key={entry.id} className="rounded-lg border border-white/5 bg-white/5 p-3">
                      <p className="font-mono text-[0.7rem] text-slate-400">
                        {new Date(entry.timestamp).toLocaleTimeString()} · {entry.source}
                      </p>
                      <p className="text-slate-100">{entry.message}</p>
                      {entry.stack && (
                        <pre className="mt-2 max-h-32 overflow-auto text-[0.65rem] text-slate-300">{entry.stack}</pre>
                      )}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            <div className="flex flex-wrap gap-3">
              <button
                type="button"
                onClick={this.handleReload}
                className="rounded-lg bg-primary-600 px-4 py-2 text-sm font-semibold text-white hover:bg-primary-500"
              >
                Reload interface
              </button>
              <a
                href="/docs/index.html"
                target="_blank"
                rel="noreferrer"
                className="rounded-lg border border-white/20 px-4 py-2 text-sm font-semibold text-white/80 hover:border-white/40"
              >
                Legacy docs snapshot
              </a>
            </div>
          </div>
        </div>
      )
    }
    return this.props.children
  }
}
