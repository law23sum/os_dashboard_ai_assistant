import { useState, FormEvent } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Shield, User, Lock, AlertCircle, LogIn } from 'lucide-react'
import apiClient, { apiPath } from '../lib/apiClient'
import { toast } from '../utils/toast'

export default function Login() {
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

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

      localStorage.setItem('user', JSON.stringify(userResponse.data))

      toast.success('Login successful!')
      navigate('/')
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
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-[color:var(--osd-accent)] to-[color:var(--osd-accentPurple)] mb-4 shadow-lg">
              <Shield className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-3xl font-bold mb-2">OS Dashboard</h1>
            <p className="text-[color:var(--osd-muted)]">Sign in to your account</p>
          </div>

          {error && (
            <div className="mb-4 p-3 bg-red-500/20 border border-red-500/50 rounded-lg text-red-400 text-sm flex items-start gap-2">
              <AlertCircle className="w-5 h-5 flex-shrink-0" />
              <span>{error}</span>
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
                  className="w-full pl-10 pr-4 py-2 bg-[color:var(--osd-surface)] border border-[color:var(--osd-border)] rounded-lg focus:outline-none focus:ring-2 focus:ring-[color:var(--osd-accent)]"
                  placeholder="Enter your username"
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
                  className="w-full pl-10 pr-4 py-2 bg-[color:var(--osd-surface)] border border-[color:var(--osd-border)] rounded-lg focus:outline-none focus:ring-2 focus:ring-[color:var(--osd-accent)]"
                  placeholder="Enter your password"
                  required
                  disabled={isLoading}
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-3 bg-gradient-to-r from-[color:var(--osd-accent)] to-[color:var(--osd-accentPurple)] text-white rounded-lg font-medium hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 shadow-lg"
            >
              {isLoading ? (
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

          <div className="mt-6 pt-6 border-t border-[color:var(--osd-border)]">
            <p className="text-center text-sm text-[color:var(--osd-muted)]">
              Don't have an account?{' '}
              <Link to="/signup" className="text-[color:var(--osd-accent)] hover:underline font-medium">
                Create one
              </Link>
            </p>
          </div>

          {/* Demo Credentials Hint */}
          <div className="mt-6 p-4 bg-[color:var(--osd-surface)]/50 border border-[color:var(--osd-border)] rounded-xl">
            <p className="text-xs font-semibold text-[color:var(--osd-text)] mb-2">Demo Credentials:</p>
            <div className="space-y-1 text-xs text-[color:var(--osd-muted)]">
              <p>
                <span className="font-mono text-[color:var(--osd-accent)]">admin</span> / <span className="font-mono">admin123</span>{' '}
                <span className="text-[color:var(--osd-warning)]">(Admin)</span>
              </p>
              <p>
                <span className="font-mono text-[color:var(--osd-accent)]">alice</span> / <span className="font-mono">password123</span>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
