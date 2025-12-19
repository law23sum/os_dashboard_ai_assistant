import { useState, FormEvent } from 'react'
import { useNavigate, Link, useLocation } from 'react-router-dom'
import { Shield, Lock, User, AlertCircle, LogIn } from 'lucide-react'
import apiClient, { apiPath } from '../lib/apiClient'
import { toast } from '../utils/toast'

export default function Login() {
  const navigate = useNavigate()
  const location = useLocation()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const from = (location.state as any)?.from?.pathname || '/'

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError(null)
    setIsLoading(true)

    try {
      const response = await apiClient.post(apiPath('auth/login'), {
        username,
        password,
      })

      const { access_token, refresh_token } = response.data

      // Store tokens
      localStorage.setItem('access_token', access_token)
      localStorage.setItem('refresh_token', refresh_token)

      // Get user info
      const userResponse = await apiClient.get(apiPath('auth/me'), {
        headers: { Authorization: `Bearer ${access_token}` },
      })

      const userData = userResponse.data
      localStorage.setItem('user', JSON.stringify(userData))

      toast.success('Login successful!')
      navigate(from, { replace: true })
    } catch (err: any) {
      const message = err.response?.data?.detail || 'Login failed. Please try again.'
      setError(message)
      toast.error(message)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-[color:var(--osd-background)] to-[color:var(--osd-surface)] p-4">
      <div className="w-full max-w-md">
        <div className="glass-content p-8 rounded-2xl shadow-2xl">
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-[color:var(--osd-accent)]/20 to-[color:var(--osd-accentPurple)]/20 border border-[color:var(--osd-accent)]/30 mb-4">
              <Shield className="w-8 h-8 text-[color:var(--osd-accent)]" />
            </div>
            <h1 className="text-3xl font-bold mb-2">OS Dashboard</h1>
            <p className="text-[color:var(--osd-muted)]">Sign in to your account</p>
          </div>

          {error && (
            <div className="mb-4 p-3 bg-red-500/20 border border-red-500/50 rounded-lg text-red-400 text-sm flex items-start gap-2">
              <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
              <p>{error}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Username</label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-[color:var(--osd-muted)]" />
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 bg-[color:var(--osd-surface)] border border-[color:var(--osd-border)] rounded-lg focus:outline-none focus:ring-2 focus:ring-[color:var(--osd-accent)] text-[color:var(--osd-text)]"
                  required
                  autoFocus
                  disabled={isLoading}
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Password</label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-[color:var(--osd-muted)]" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 bg-[color:var(--osd-surface)] border border-[color:var(--osd-border)] rounded-lg focus:outline-none focus:ring-2 focus:ring-[color:var(--osd-accent)] text-[color:var(--osd-text)]"
                  required
                  disabled={isLoading}
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-3 bg-gradient-to-r from-[color:var(--osd-accent)] to-[color:var(--osd-accentPurple)] text-white rounded-lg font-medium hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <>
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Signing in...
                </>
              ) : (
                <>
                  <LogIn className="w-5 h-5" />
                  Sign In
                </>
              )}
            </button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-sm text-[color:var(--osd-muted)]">
              Don't have an account?{' '}
              <Link to="/signup" className="text-[color:var(--osd-accent)] hover:underline">
                Sign up
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
