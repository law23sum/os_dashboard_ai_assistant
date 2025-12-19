import { useState, FormEvent } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Shield, Mail, Lock, User, AlertCircle, LogIn } from 'lucide-react'
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
import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { LogIn, Mail, Lock, User } from 'lucide-react'

export default function Login() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      })

      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || 'Login failed')
      }

      const data = await response.json()
      localStorage.setItem('access_token', data.access_token)
      localStorage.setItem('user', JSON.stringify(data.user))
      
      navigate('/dashboard')
    } catch (err: any) {
      setError(err.message || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Background decoration */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary-500/10 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-violet-500/10 rounded-full blur-3xl" />
      </div>

      <div className="relative w-full max-w-md px-6">
        {/* Logo and Title */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-primary-500/20 to-violet-500/20 border border-primary-500/30 mb-4">
            <Shield className="w-8 h-8 text-primary-400" />
          </div>
          <h1 className="text-3xl font-bold text-white mb-2">OS Dashboard AI</h1>
          <p className="text-slate-400">Sign in to your account</p>
        </div>

        {/* Login Form */}
        <div className="glass-card p-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            {error && (
              <div className="flex items-start gap-3 p-4 bg-red-500/10 border border-red-500/30 rounded-xl">
                <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                <p className="text-sm text-red-200">{error}</p>
              </div>
            )}

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
                  className="w-full pl-11 pr-4 py-3 bg-slate-800/50 border border-slate-700/60 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500/50 transition-all"
                  placeholder="Enter your username"
                  disabled={isLoading}
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-[color:var(--osd-background)] to-[color:var(--osd-surface)] p-4">
      <div className="w-full max-w-md">
        <div className="glass-content p-8 rounded-2xl shadow-2xl">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold mb-2">OS Dashboard</h1>
            <p className="text-[color:var(--osd-muted)]">Sign in to your account</p>
          </div>

          {error && (
            <div className="mb-4 p-3 bg-red-500/20 border border-red-500/50 rounded-lg text-red-400 text-sm">
              {error}
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
                  required
                  autoFocus
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
                  className="w-full pl-11 pr-4 py-3 bg-slate-800/50 border border-slate-700/60 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500/50 transition-all"
                  placeholder="Enter your password"
                  disabled={isLoading}
              <label className="block text-sm font-medium mb-2">Password</label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-[color:var(--osd-muted)]" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 bg-[color:var(--osd-surface)] border border-[color:var(--osd-border)] rounded-lg focus:outline-none focus:ring-2 focus:ring-[color:var(--osd-accent)]"
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-gradient-to-r from-primary-500 to-primary-600 hover:from-primary-600 hover:to-primary-700 text-white font-medium rounded-xl shadow-lg shadow-primary-500/20 hover:shadow-xl hover:shadow-primary-500/30 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
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
              disabled={loading}
              className="w-full py-3 bg-gradient-to-r from-[color:var(--osd-accent)] to-[color:var(--osd-accentPurple)] text-white rounded-lg font-medium hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {loading ? (
                <>Loading...</>
              ) : (
                <>
                  <LogIn className="w-5 h-5" />
                  Sign In
                </>
              )}
            </button>
          </form>

          <div className="mt-6 pt-6 border-t border-slate-700/50">
            <p className="text-center text-sm text-slate-400">
              Don't have an account?{' '}
              <Link
                to="/signup"
                className="text-primary-400 hover:text-primary-300 font-medium transition-colors"
              >
                Create one
              </Link>
            </p>
          </div>

          {/* Demo Credentials */}
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
