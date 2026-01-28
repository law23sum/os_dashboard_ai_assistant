import { Component, ErrorInfo, ReactNode } from 'react'
import { reportClientError } from '../utils/runtimeDiagnostics'

interface AppErrorBoundaryProps {
  children: ReactNode
}

interface AppErrorBoundaryState {
  hasError: boolean
}

export class AppErrorBoundary extends Component<AppErrorBoundaryProps, AppErrorBoundaryState> {
  constructor(props: AppErrorBoundaryProps) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError() {
    return { hasError: true }
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    reportClientError({
      source: 'AppErrorBoundary',
      message: error.message,
      stack: error.stack ?? info.componentStack,
    })
  }

  handleReload = () => {
    this.setState({ hasError: false })
    window.location.reload()
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-[#050914] text-white flex flex-col items-center justify-center px-6 text-center">
          <h1 className="text-3xl font-semibold mb-4">Something unexpected happened</h1>
          <p className="text-slate-300 max-w-xl">
            We captured the error for the diagnostics service. Refresh or return home to continue working.
          </p>
          <div className="mt-6 flex flex-col sm:flex-row gap-3">
            <button
              type="button"
              className="rounded-full bg-white/10 px-6 py-2 text-sm font-semibold hover:bg-white/20 transition"
              onClick={this.handleReload}
            >
              Reload
            </button>
            <a
              className="rounded-full border border-white/30 px-6 py-2 text-sm font-semibold hover:bg-white/10 transition"
              href="/"
            >
              Return Home
            </a>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}
