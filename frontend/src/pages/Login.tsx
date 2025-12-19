import { FormEvent, useMemo, useState } from 'react'
import { Link, Navigate, useLocation, useNavigate } from 'react-router-dom'
import { AlertCircle, LogIn, Lock, Shield, User } from 'lucide-react'

type LocationState = { from?: string }

type MeResponse = {
  id: number
  username: string
  email: string
  full_name?: string | null
  role?: string
  is_admin?: boolean
}

export default function Login() {
  const navigate = useNavigate()
  const location = useLocation()
  const state = (location.state || {}) as LocationState

  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const alreadyAuthed = useMemo(() => {
    if (typeof window === 'undefined') return false
    return !!window.localStorage.getItem('access_token')
  }, [])

  if (alreadyAuthed) {
    return <Navigate to={state.from || '/'} replace />
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError(null)
    setLoading(true)

    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      })

      const data = await res.json().catch(() => ({}))
      if (!res.ok) throw new Error(data.detail || 'Login failed')

      const access = data.access_token
      const refresh = data.refresh_token
      if (!access) throw new Error('Missing access token')

      localStorage.setItem('access_token', access)
      if (refresh) localStorage.setItem('refresh_token', refresh)

      const meRes = await fetch('/api/auth/me', {
        headers: { Authorization: `Bearer ${access}` },
      })
      const meData = (await meRes.json().catch(() => null)) as MeResponse | null
      if (meRes.ok && meData) {
        localStorage.setItem('user', JSON.stringify(meData))
      }

      navigate(state.from || '/', { replace: true })
    } catch (err: any) {
      setError(err?.message || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-4">
      <div className="relative w-full max-w-md">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-primary-500/20 to-violet-500/20 border border-primary-500/30 mb-4">
            <Shield className="w-8 h-8 text-primary-400" />
          </div>
          <h1 className="text-3xl font-bold text-white mb-2">OS Dashboard AI</h1>
          <p className="text-slate-400">Sign in to your account</p>
        </div>

        <div className="glass-card p-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            {error ? (
              <div className="flex items-start gap-3 p-4 bg-red-500/10 border border-red-500/30 rounded-xl">
                <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                <p className="text-sm text-red-200">{error}</p>
              </div>
            ) : null}

            <div>
              <label htmlFor="username" className="block text-sm font-medium text-slate-300 mb-2">
                Username
              </label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                <input
                  id="username"
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                  autoComplete="username"
                  className="w-full pl-11 pr-4 py-3 bg-slate-800/50 border border-slate-700/60 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500/50 transition-all"
                  placeholder="Enter your username"
                  disabled={loading}
                />
              </div>
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-slate-300 mb-2">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                <input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  autoComplete="current-password"
                  className="w-full pl-11 pr-4 py-3 bg-slate-800/50 border border-slate-700/60 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500/50 transition-all"
                  placeholder="Enter your password"
                  disabled={loading}
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-gradient-to-r from-primary-500 to-primary-600 hover:from-primary-600 hover:to-primary-700 text-white font-medium rounded-xl shadow-lg shadow-primary-500/20 hover:shadow-xl hover:shadow-primary-500/30 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              {loading ? (
                <>
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  <span>Signing in...</span>
                </>
              ) : (
                <>
                  <LogIn className="w-5 h-5" />
                  <span>Sign In</span>
                </>
              )}
            </button>
          </form>

          <div className="mt-6 pt-6 border-t border-slate-700/50">
            <p className="text-center text-sm text-slate-400">
              Don't have an account?{' '}
              <Link to="/signup" className="text-primary-400 hover:text-primary-300 font-medium transition-colors">
                Create one
              </Link>
            </p>
          </div>

          <div className="mt-6 p-4 bg-slate-800/30 border border-slate-700/50 rounded-xl">
            <p className="text-xs font-semibold text-slate-300 mb-2">Demo Credentials:</p>
            <div className="space-y-1 text-xs text-slate-400">
              <p>
                <span className="font-mono">admin</span> / <span className="font-mono">admin123</span>{' '}
                <span className="text-amber-400">(Admin)</span>
              </p>
              <p>
                <span className="font-mono">alice</span> / <span className="font-mono">password123</span>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
