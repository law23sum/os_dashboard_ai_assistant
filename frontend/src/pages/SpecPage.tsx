import { useMemo, useState } from 'react'
import { useLocation } from 'react-router-dom'
import { Code, FileText, Settings2, SlidersHorizontal } from 'lucide-react'
import PageHeader from '../components/PageHeader'
import { findRouteContext } from '../data/iaManifest'

export default function SpecPage() {
  const location = useLocation()
  const { platform, category, feature } = useMemo(
    () => findRouteContext(location.pathname),
    [location.pathname]
  )

  const [config, setConfig] = useState({
    environment: 'prod',
    mode: 'interactive',
    dataScope: 'user',
    refreshSeconds: 30,
    filters: '',
  })

  const title = feature?.label || category?.label || 'Workspace'
  const description =
    category?.label
      ? `Spec-driven workspace surface for ${category.label}.`
      : 'Spec-driven workspace surface with configurable inputs and displays.'

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow={platform ? platform.label : 'Platform'}
        title={title}
        description={description}
        icon={FileText}
      />

      <div className="grid gap-4 lg:grid-cols-3">
        <section className="glass-card p-5 lg:col-span-2">
          <div className="flex items-center gap-2 mb-3">
            <Code className="w-4 h-4 text-[color:var(--osd-muted)]" />
            <h2 className="text-sm font-semibold text-[color:var(--osd-text)]">Interface</h2>
          </div>
          <div className="grid gap-3 md:grid-cols-2">
            <div className="rounded-xl border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)]/40 p-4">
              <p className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Route</p>
              <p className="mt-1 font-mono text-sm">{location.pathname}</p>
            </div>
            <div className="rounded-xl border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)]/40 p-4">
              <p className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Backend (planned/linked)</p>
              <p className="mt-1 font-mono text-sm">{feature?.route ?? '—'}</p>
            </div>
          </div>

          <div className="mt-4 rounded-xl border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)]/30 p-4">
            <p className="text-sm text-[color:var(--osd-muted)] leading-relaxed">
              This page is generated from the navigation spec. It provides consistent UI building blocks (configuration, input
              parameters, and display panes) so every route follows the Platform → Category → Features pattern.
            </p>
          </div>
        </section>

        <aside className="glass-card p-5">
          <div className="flex items-center gap-2 mb-3">
            <Settings2 className="w-4 h-4 text-[color:var(--osd-muted)]" />
            <h2 className="text-sm font-semibold text-[color:var(--osd-text)]">Configuration</h2>
          </div>

          <div className="space-y-3">
            <label className="block text-sm">
              <span className="text-[color:var(--osd-muted)]">Environment</span>
              <select
                className="mt-1 w-full rounded-lg bg-[color:var(--osd-surface)] border border-[color:var(--osd-border)] px-3 py-2"
                value={config.environment}
                onChange={(e) => setConfig((c) => ({ ...c, environment: e.target.value }))}
              >
                <option value="prod">Production</option>
                <option value="staging">Staging</option>
                <option value="dev">Development</option>
              </select>
            </label>

            <label className="block text-sm">
              <span className="text-[color:var(--osd-muted)]">Mode</span>
              <select
                className="mt-1 w-full rounded-lg bg-[color:var(--osd-surface)] border border-[color:var(--osd-border)] px-3 py-2"
                value={config.mode}
                onChange={(e) => setConfig((c) => ({ ...c, mode: e.target.value }))}
              >
                <option value="interactive">Interactive</option>
                <option value="simulation">Simulation</option>
                <option value="audit">Audit</option>
              </select>
            </label>

            <label className="block text-sm">
              <span className="text-[color:var(--osd-muted)]">Data scope</span>
              <select
                className="mt-1 w-full rounded-lg bg-[color:var(--osd-surface)] border border-[color:var(--osd-border)] px-3 py-2"
                value={config.dataScope}
                onChange={(e) => setConfig((c) => ({ ...c, dataScope: e.target.value }))}
              >
                <option value="user">User</option>
                <option value="tenant">Tenant</option>
                <option value="admin">Admin</option>
              </select>
              <p className="mt-1 text-xs text-[color:var(--osd-muted)]">
                User scope is enforced by auth; admin scope requires admin role.
              </p>
            </label>

            <label className="block text-sm">
              <span className="text-[color:var(--osd-muted)]">Refresh (seconds)</span>
              <input
                type="number"
                min={5}
                max={600}
                className="mt-1 w-full rounded-lg bg-[color:var(--osd-surface)] border border-[color:var(--osd-border)] px-3 py-2"
                value={config.refreshSeconds}
                onChange={(e) => setConfig((c) => ({ ...c, refreshSeconds: Number(e.target.value) }))}
              />
            </label>
          </div>
        </aside>
      </div>

      <section className="glass-card p-6">
        <div className="flex items-center gap-2 mb-4">
          <SlidersHorizontal className="w-4 h-4 text-[color:var(--osd-muted)]" />
          <h2 className="text-sm font-semibold text-[color:var(--osd-text)]">Input parameters</h2>
        </div>

        <div className="grid gap-4 md:grid-cols-3">
          <label className="block text-sm md:col-span-2">
            <span className="text-[color:var(--osd-muted)]">Filters / query</span>
            <input
              className="mt-1 w-full rounded-lg bg-[color:var(--osd-surface)] border border-[color:var(--osd-border)] px-3 py-2"
              placeholder="e.g. status:open severity:high owner:me"
              value={config.filters}
              onChange={(e) => setConfig((c) => ({ ...c, filters: e.target.value }))}
            />
          </label>

          <div className="rounded-xl border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)]/40 p-4">
            <p className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Resolved scope</p>
            <p className="mt-1 text-sm text-[color:var(--osd-text)]">
              {config.dataScope === 'admin'
                ? 'Admin (all schemas)'
                : config.dataScope === 'tenant'
                  ? 'Tenant (shared)'
                  : 'User (private)'}
            </p>
            <p className="mt-1 text-xs text-[color:var(--osd-muted)]">Refresh every {config.refreshSeconds}s</p>
          </div>
        </div>
      </section>

      <section className="grid gap-4 lg:grid-cols-2">
        <div className="glass-card p-6">
          <h2 className="text-sm font-semibold text-[color:var(--osd-text)] mb-2">Displays</h2>
          <div className="grid gap-3 md:grid-cols-2">
            <div className="rounded-xl border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)]/30 p-4">
              <p className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Primary panel</p>
              <p className="mt-1 text-sm text-[color:var(--osd-text)]">Charts / tables / timelines</p>
              <p className="mt-2 text-xs text-[color:var(--osd-muted)]">
                Configure via inputs; data is scoped to the authenticated user.
              </p>
            </div>
            <div className="rounded-xl border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)]/30 p-4">
              <p className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Secondary panel</p>
              <p className="mt-1 text-sm text-[color:var(--osd-text)]">Logs / evidence / config preview</p>
              <p className="mt-2 text-xs text-[color:var(--osd-muted)]">
                In admin mode, sensitive fields should be masked unless explicitly expanded.
              </p>
            </div>
          </div>
        </div>

        <div className="glass-card p-6">
          <h2 className="text-sm font-semibold text-[color:var(--osd-text)] mb-2">Configuration preview</h2>
          <pre className="text-xs rounded-xl border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)]/40 p-4 overflow-auto">
{JSON.stringify(
  {
    route: location.pathname,
    spec: null,
    backend: feature?.route ?? null,
    environment: config.environment,
    mode: config.mode,
    scope: config.dataScope,
    refreshSeconds: config.refreshSeconds,
    filters: config.filters,
  },
  null,
  2
)}
          </pre>
        </div>
      </section>
    </div>
  )
}
