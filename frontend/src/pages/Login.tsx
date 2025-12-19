import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Shield, User, Lock, AlertCircle, LogIn } from 'lucide-react'
import { LogIn, Lock, User, Shield, AlertCircle } from 'lucide-react'

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
import { useState, FormEvent } from 'react'
import { useNavigate, Link, useLocation } from 'react-router-dom'
import { Shield, Lock, User, AlertCircle, LogIn } from 'lucide-react'
import apiClient, { apiPath } from '../lib/apiClient'
import { toast } from '../utils/toast'

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
  const from = (location.state as any)?.from?.pathname || '/'

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

      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || 'Login failed')
      }

      const data = await response.json()
      localStorage.setItem('access_token', data.access_token)
      if (data.refresh_token) {
        localStorage.setItem('refresh_token', data.refresh_token)
      }
      localStorage.setItem('user', JSON.stringify(data.user))

      navigate('/')
    } catch (err: any) {
      setError(err.message || 'Login failed')
    } finally {
      setLoading(false)
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
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Background decoration */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-violet-500/10 rounded-full blur-3xl" />
      </div>

      <div className="relative w-full max-w-md px-6">
        {/* Logo and Title */}
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-4">
      <div className="relative w-full max-w-md">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-indigo-500/20 to-violet-500/20 border border-indigo-500/30 mb-4">
            <Shield className="w-8 h-8 text-indigo-400" />
          </div>
          <h1 className="text-3xl font-bold text-white mb-2">OS Dashboard AI</h1>
          <p className="text-slate-400">Sign in to your account</p>
        </div>

        {/* Login Form */}
        <div className="bg-slate-800/50 backdrop-blur-xl border border-slate-700/50 rounded-2xl p-8">
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
                  className="w-full pl-11 pr-4 py-3 bg-slate-900/50 border border-slate-700/60 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500/50 transition-all"
                  placeholder="Enter your username"
                  disabled={loading}
                  autoComplete="username"
                  className="w-full pl-11 pr-4 py-3 bg-slate-800/50 border border-slate-700/60 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500/50 transition-all"
                  placeholder="Enter your username"
                  disabled={loading}
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-[color:var(--osd-background)] to-[color:var(--osd-surface)] p-4">
      <div className="w-full max-w-md">
        <div className="glass-content p-8 rounded-2xl shadow-2xl">
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-[color:var(--osd-accent)] to-[color:var(--osd-accentPurple)] mb-4 shadow-lg">
              <Shield className="w-8 h-8 text-white" />
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-[color:var(--osd-accent)]/20 to-[color:var(--osd-accentPurple)]/20 border border-[color:var(--osd-accent)]/30 mb-4">
              <Shield className="w-8 h-8 text-[color:var(--osd-accent)]" />
            </div>
            <h1 className="text-3xl font-bold mb-2">OS Dashboard</h1>
            <p className="text-[color:var(--osd-muted)]">Sign in to your account</p>
          </div>

          {error && (
            <div className="mb-4 p-3 bg-red-500/20 border border-red-500/50 rounded-lg text-red-400 text-sm flex items-start gap-2">
              <AlertCircle className="w-5 h-5 flex-shrink-0" />
              <span>{error}</span>
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
                  className="w-full pl-10 pr-4 py-2 bg-[color:var(--osd-surface)] border border-[color:var(--osd-border)] rounded-lg focus:outline-none focus:ring-2 focus:ring-[color:var(--osd-accent)]"
                  placeholder="Enter your username"
                  className="w-full pl-10 pr-4 py-2 bg-[color:var(--osd-surface)] border border-[color:var(--osd-border)] rounded-lg focus:outline-none focus:ring-2 focus:ring-[color:var(--osd-accent)] text-[color:var(--osd-text)]"
                  required
                  autoFocus
                  disabled={isLoading}
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
                  className="w-full pl-11 pr-4 py-3 bg-slate-900/50 border border-slate-700/60 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500/50 transition-all"
                  placeholder="Enter your password"
                  disabled={loading}
                  autoComplete="current-password"
                  className="w-full pl-11 pr-4 py-3 bg-slate-800/50 border border-slate-700/60 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500/50 transition-all"
                  placeholder="Enter your password"
                  disabled={loading}
              <label className="block text-sm font-medium mb-2">Password</label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-[color:var(--osd-muted)]" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 bg-[color:var(--osd-surface)] border border-[color:var(--osd-border)] rounded-lg focus:outline-none focus:ring-2 focus:ring-[color:var(--osd-accent)]"
                  placeholder="Enter your password"
                  className="w-full pl-10 pr-4 py-2 bg-[color:var(--osd-surface)] border border-[color:var(--osd-border)] rounded-lg focus:outline-none focus:ring-2 focus:ring-[color:var(--osd-accent)] text-[color:var(--osd-text)]"
                  required
                  disabled={isLoading}
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-3 bg-gradient-to-r from-[color:var(--osd-accent)] to-[color:var(--osd-accentPurple)] text-white rounded-lg font-medium hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 shadow-lg"
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-gradient-to-r from-indigo-500 to-indigo-600 hover:from-indigo-600 hover:to-indigo-700 text-white font-medium rounded-xl shadow-lg shadow-indigo-500/20 hover:shadow-xl hover:shadow-indigo-500/30 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
              className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-gradient-to-r from-primary-500 to-primary-600 hover:from-primary-600 hover:to-primary-700 text-white font-medium rounded-xl shadow-lg shadow-primary-500/20 hover:shadow-xl hover:shadow-primary-500/30 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
              disabled={isLoading}
              className="w-full py-3 bg-gradient-to-r from-[color:var(--osd-accent)] to-[color:var(--osd-accentPurple)] text-white rounded-lg font-medium hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Signing in...
                </>
              ) : (
                <>
                  <LogIn className="w-5 h-5" />
                  <span>Sign In</span>
                  Sign In
                </>
              )}
            </button>
          </form>

          <div className="mt-6 pt-6 border-t border-[color:var(--osd-border)]">
            <p className="text-center text-sm text-[color:var(--osd-muted)]">
              Don't have an account?{' '}
              <Link to="/signup" className="text-[color:var(--osd-accent)] hover:underline font-medium">
              <Link
                to="/signup"
                className="text-indigo-400 hover:text-indigo-300 font-medium transition-colors"
              >
              <Link to="/signup" className="text-primary-400 hover:text-primary-300 font-medium transition-colors">
                Create one
              </Link>
            </p>
          </div>

          {/* Demo Credentials Hint */}
          <div className="mt-6 p-4 bg-[color:var(--osd-surface)]/50 border border-[color:var(--osd-border)] rounded-xl">
            <p className="text-xs font-semibold text-[color:var(--osd-text)] mb-2">Demo Credentials:</p>
            <div className="space-y-1 text-xs text-[color:var(--osd-muted)]">
          {/* Demo Credentials */}
          <div className="mt-6 p-4 bg-slate-900/30 border border-slate-700/50 rounded-xl">
          <div className="mt-6 p-4 bg-slate-800/30 border border-slate-700/50 rounded-xl">
            <p className="text-xs font-semibold text-slate-300 mb-2">Demo Credentials:</p>
            <div className="space-y-1 text-xs text-slate-400">
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