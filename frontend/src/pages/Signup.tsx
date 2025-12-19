import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { signup } from '../api/auth'
import { useAuth } from '../auth/AuthContext'
import { toast } from '../utils/toast'

export default function Signup() {
  const navigate = useNavigate()
  const { refresh } = useAuth()
  const [displayName, setDisplayName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [environment, setEnvironment] = useState<'demo' | 'prod'>('demo')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!email.trim() || !password) return
    setIsSubmitting(true)
    try {
      await signup(email.trim(), password, displayName.trim(), environment)
      await refresh()
      toast.success('Account created')
      navigate('/', { replace: true })
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Signup failed')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex items-center justify-center px-4">
      <div className="w-full max-w-md rounded-3xl border border-white/10 bg-white/5 p-6 shadow-2xl">
        <div className="mb-6">
          <p className="text-xs uppercase tracking-[0.25em] text-slate-400">OS Dashboard</p>
          <h1 className="mt-2 text-2xl font-semibold">Create account</h1>
          <p className="mt-2 text-sm text-slate-300">
            Your workspace data becomes isolated, traceable, and exportable per user.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="text-xs text-slate-300">Display name</label>
            <input
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              className="mt-1 w-full rounded-xl border border-white/10 bg-black/20 px-4 py-3 text-sm text-white placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-primary-500/50"
              placeholder="Chris"
            />
          </div>
          <div>
            <label className="text-xs text-slate-300">Email</label>
            <input
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              type="email"
              autoComplete="email"
              className="mt-1 w-full rounded-xl border border-white/10 bg-black/20 px-4 py-3 text-sm text-white placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-primary-500/50"
              placeholder="you@company.com"
            />
          </div>
          <div>
            <label className="text-xs text-slate-300">Password</label>
            <input
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              type="password"
              autoComplete="new-password"
              className="mt-1 w-full rounded-xl border border-white/10 bg-black/20 px-4 py-3 text-sm text-white placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-primary-500/50"
              placeholder="At least 6 characters"
            />
          </div>
          <div>
            <label className="text-xs text-slate-300">Workspace mode</label>
            <select
              value={environment}
              onChange={(e) => setEnvironment(e.target.value as 'demo' | 'prod')}
              className="mt-1 w-full rounded-xl border border-white/10 bg-black/20 px-4 py-3 text-sm text-white focus:outline-none focus:ring-2 focus:ring-primary-500/50"
            >
              <option value="demo">Demo (seeded data)</option>
              <option value="prod">Production</option>
            </select>
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full rounded-xl bg-gradient-to-r from-blue-500 to-indigo-500 px-4 py-3 text-sm font-semibold shadow-lg shadow-blue-500/20 disabled:opacity-60"
          >
            {isSubmitting ? 'Creating…' : 'Create account'}
          </button>
        </form>

        <div className="mt-5 flex items-center justify-between text-sm">
          <span className="text-slate-400">Already have an account?</span>
          <Link className="text-primary-300 hover:text-primary-200" to="/login">
            Sign in
          </Link>
        </div>
      </div>
    </div>
  )
}

