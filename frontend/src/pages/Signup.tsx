import { FormEvent, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { AlertCircle, Mail, Shield, User, UserPlus, Lock } from 'lucide-react'

export default function Signup() {
  const navigate = useNavigate()

  const [form, setForm] = useState({
import { useState, FormEvent } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Shield, Mail, Lock, User, AlertCircle, UserPlus, UserCircle } from 'lucide-react'
import apiClient, { apiPath } from '../lib/apiClient'
import { toast } from '../utils/toast'

export default function Signup() {
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    fullName: '',
    password: '',
    confirmPassword: '',
  })

  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError(null)

    if (form.password !== form.confirmPassword) {
      setError('Passwords do not match')
      return
    }
    if (form.password.length < 8) {
      setError('Password must be at least 8 characters')
      return
    }

    setLoading(true)
    try {
      const res = await fetch('/api/auth/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: form.username,
          email: form.email,
          password: form.password,
          full_name: form.fullName || null,
        }),
      })

      const data = await res.json().catch(() => ({}))
      if (!res.ok) throw new Error(data.detail || 'Signup failed')

      // Auto-login
      const loginRes = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: form.username, password: form.password }),
      })
      const loginData = await loginRes.json().catch(() => ({}))
      if (loginRes.ok && loginData.access_token) {
        localStorage.setItem('access_token', loginData.access_token)
        if (loginData.refresh_token) localStorage.setItem('refresh_token', loginData.refresh_token)
        navigate('/', { replace: true })
      } else {
        navigate('/login', { replace: true })
      }
    } catch (err: any) {
      setError(err?.message || 'Signup failed')
    } finally {
      setLoading(false)
    setIsLoading(true)

    try {
      // Create account
      await apiClient.post(apiPath('auth/signup'), {
        username: formData.username,
        email: formData.email,
        password: formData.password,
        full_name: formData.fullName || null,
      })

      toast.success('Account created successfully!')

      // Auto-login after signup
      const loginResponse = await apiClient.post(apiPath('auth/login'), {
        username: formData.username,
        password: formData.password,
      })

      const { access_token, refresh_token } = loginResponse.data

      // Store tokens
      localStorage.setItem('access_token', access_token)
      localStorage.setItem('refresh_token', refresh_token)

      // Get user info
      const userResponse = await apiClient.get(apiPath('auth/me'), {
        headers: { Authorization: `Bearer ${access_token}` },
      })

      localStorage.setItem('user', JSON.stringify(userResponse.data))

      navigate('/')
    } catch (err: any) {
      const message = err.response?.data?.detail || 'Signup failed. Please try again.'
      setError(message)
      toast.error(message)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-4">
      <div className="relative w-full max-w-md">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-primary-500/20 to-violet-500/20 border border-primary-500/30 mb-4">
            <Shield className="w-8 h-8 text-primary-400" />
          </div>
          <h1 className="text-3xl font-bold text-white mb-2">Create Account</h1>
          <p className="text-slate-400">Join OS Dashboard AI today</p>
        </div>

        <div className="glass-card p-8">
          <form onSubmit={handleSubmit} className="space-y-5">
            {error ? (
              <div className="flex items-start gap-3 p-4 bg-red-500/10 border border-red-500/30 rounded-xl">
                <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                <p className="text-sm text-red-200">{error}</p>
              </div>
            ) : null}

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Username *</label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                <input
                  type="text"
                  value={form.username}
                  onChange={(e) => setForm((f) => ({ ...f, username: e.target.value }))}
                  required
                  className="w-full pl-11 pr-4 py-3 bg-slate-800/50 border border-slate-700/60 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500/50 transition-all"
                  placeholder="Choose a username"
                  disabled={loading}
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Email *</label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                <input
                  type="email"
                  value={form.email}
                  onChange={(e) => setForm((f) => ({ ...f, email: e.target.value }))}
                  required
                  className="w-full pl-11 pr-4 py-3 bg-slate-800/50 border border-slate-700/60 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500/50 transition-all"
                  placeholder="your@email.com"
                  disabled={loading}
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-[color:var(--osd-background)] to-[color:var(--osd-surface)] p-4">
      <div className="w-full max-w-md">
        <div className="glass-content p-8 rounded-2xl shadow-2xl">
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-[color:var(--osd-accent)]/20 to-[color:var(--osd-accentPurple)]/20 border border-[color:var(--osd-accent)]/30 mb-4">
              <Shield className="w-8 h-8 text-[color:var(--osd-accent)]" />
            </div>
            <h1 className="text-3xl font-bold mb-2">Create Account</h1>
            <p className="text-[color:var(--osd-muted)]">Sign up for OS Dashboard</p>
          </div>

          {error && (
            <div className="mb-4 p-3 bg-red-500/20 border border-red-500/50 rounded-lg text-red-400 text-sm flex items-start gap-2">
              <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
              <p>{error}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Full Name (Optional)</label>
              <div className="relative">
                <UserCircle className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-[color:var(--osd-muted)]" />
                <input
                  type="text"
                  value={formData.fullName}
                  onChange={(e) => handleChange('fullName', e.target.value)}
                  className="w-full pl-10 pr-4 py-2 bg-[color:var(--osd-surface)] border border-[color:var(--osd-border)] rounded-lg focus:outline-none focus:ring-2 focus:ring-[color:var(--osd-accent)] text-[color:var(--osd-text)]"
                  placeholder="John Doe"
                  disabled={isLoading}
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Full Name <span className="text-slate-500">(optional)</span>
              </label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                <input
                  type="text"
                  value={form.fullName}
                  onChange={(e) => setForm((f) => ({ ...f, fullName: e.target.value }))}
                  className="w-full pl-11 pr-4 py-3 bg-slate-800/50 border border-slate-700/60 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500/50 transition-all"
                  placeholder="John Doe"
                  disabled={loading}
              <label className="block text-sm font-medium mb-2">Username</label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-[color:var(--osd-muted)]" />
                <input
                  type="text"
                  value={formData.username}
                  onChange={(e) => handleChange('username', e.target.value)}
                  className="w-full pl-10 pr-4 py-2 bg-[color:var(--osd-surface)] border border-[color:var(--osd-border)] rounded-lg focus:outline-none focus:ring-2 focus:ring-[color:var(--osd-accent)] text-[color:var(--osd-text)]"
                  required
                  autoFocus
                  disabled={isLoading}
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Password *</label>
              <label className="block text-sm font-medium mb-2">Email</label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-[color:var(--osd-muted)]" />
                <input
                  type="password"
                  value={form.password}
                  onChange={(e) => setForm((f) => ({ ...f, password: e.target.value }))}
                  required
                  minLength={8}
                  className="w-full pl-11 pr-4 py-3 bg-slate-800/50 border border-slate-700/60 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500/50 transition-all"
                  placeholder="Create a strong password"
                  disabled={loading}
                  type="email"
                  value={formData.email}
                  onChange={(e) => handleChange('email', e.target.value)}
                  className="w-full pl-10 pr-4 py-2 bg-[color:var(--osd-surface)] border border-[color:var(--osd-border)] rounded-lg focus:outline-none focus:ring-2 focus:ring-[color:var(--osd-accent)] text-[color:var(--osd-text)]"
                  required
                  disabled={isLoading}
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Confirm Password *</label>
              <label className="block text-sm font-medium mb-2">Password</label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-[color:var(--osd-muted)]" />
                <input
                  type="password"
                  value={form.confirmPassword}
                  onChange={(e) => setForm((f) => ({ ...f, confirmPassword: e.target.value }))}
                  required
                  className="w-full pl-11 pr-4 py-3 bg-slate-800/50 border border-slate-700/60 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500/50 transition-all"
                  placeholder="Confirm your password"
                  disabled={loading}
                  value={formData.password}
                  onChange={(e) => handleChange('password', e.target.value)}
                  className="w-full pl-10 pr-4 py-2 bg-[color:var(--osd-surface)] border border-[color:var(--osd-border)] rounded-lg focus:outline-none focus:ring-2 focus:ring-[color:var(--osd-accent)] text-[color:var(--osd-text)]"
                  required
                  minLength={8}
                  disabled={isLoading}
                />
              </div>
              <p className="text-xs text-[color:var(--osd-muted)] mt-1">Must be at least 8 characters</p>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Confirm Password</label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-[color:var(--osd-muted)]" />
                <input
                  type="password"
                  value={formData.confirmPassword}
                  onChange={(e) => handleChange('confirmPassword', e.target.value)}
                  className="w-full pl-10 pr-4 py-2 bg-[color:var(--osd-surface)] border border-[color:var(--osd-border)] rounded-lg focus:outline-none focus:ring-2 focus:ring-[color:var(--osd-accent)] text-[color:var(--osd-text)]"
                  required
                  disabled={isLoading}
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-gradient-to-r from-primary-500 to-primary-600 hover:from-primary-600 hover:to-primary-700 text-white font-medium rounded-xl shadow-lg shadow-primary-500/20 hover:shadow-xl hover:shadow-primary-500/30 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
              disabled={isLoading}
              className="w-full py-3 bg-gradient-to-r from-[color:var(--osd-accent)] to-[color:var(--osd-accentPurple)] text-white rounded-lg font-medium hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Creating account...
                </>
              ) : (
                <>
                  <UserPlus className="w-5 h-5" />
                  <span>Create Account</span>
                  Sign Up
                </>
              )}
            </button>
          </form>

          <div className="mt-6 pt-6 border-t border-slate-700/50">
            <p className="text-center text-sm text-slate-400">
              Already have an account?{' '}
              <Link to="/login" className="text-primary-400 hover:text-primary-300 font-medium transition-colors">
          <div className="mt-6 text-center">
            <p className="text-sm text-[color:var(--osd-muted)]">
              Already have an account?{' '}
              <Link to="/login" className="text-[color:var(--osd-accent)] hover:underline">
                Sign in
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}