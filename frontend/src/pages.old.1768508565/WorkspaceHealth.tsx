import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useMemo, useState } from 'react'
import { Activity, ClipboardList, Hammer, Loader2, RefreshCw, Shield, Terminal, Zap } from 'lucide-react'
import {
  fetchHarnessReport,
  fetchWorkspaceDoctor,
  fetchWorkspaceScan,
  runWorkspaceChecks,
  WorkspaceReport,
} from '../api/workspace'
import { toast } from '../utils/toast'

const statusBadge = (status: string) => {
  const classes: Record<string, string> = {
    passed: 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/40',
    failed: 'bg-rose-500/10 text-rose-400 border border-rose-500/40',
    skipped: 'bg-slate-500/10 text-slate-300 border border-slate-500/40',
  }
  return classes[status] || 'bg-slate-600/30 text-slate-100 border border-slate-700'
}

const formatTimestamp = (value?: number | string) => {
  if (value === undefined || value === null) return '—'
  const numeric = typeof value === 'string' ? Number(value) : value
  if (!Number.isFinite(numeric)) return '—'
  const millis = numeric < 2_000_000_000 ? numeric * 1000 : numeric
  return new Date(millis).toLocaleString()
}

const WorkspaceHealth = () => {
  const queryClient = useQueryClient()
  const [selectedCategories, setSelectedCategories] = useState<string[]>(['lint', 'test'])
  const [lastReport, setLastReport] = useState<WorkspaceReport | null>(null)

  const demoProfiles = useMemo(
    () => [
      {
        name: 'os_dashboard_ai_assistant',
        root: '/workspace/os_dashboard_ai_assistant',
        commands: {
          lint: [['python', '-m', 'flake8', 'assistant_core', 'backend_api', 'tests']],
          test: [['python', '-m', 'pytest', '-q']],
          build: [['npm', 'run', 'build', '--prefix', 'frontend']],
        },
        autofix_script: 'scripts/ai_auto_fix.py',
      },
    ],
    []
  )

  const scanQuery = useQuery({
    queryKey: ['workspace-scan'],
    queryFn: async () => {
      try {
        return await fetchWorkspaceScan()
      } catch {
        return { root: '(demo)', projects: demoProfiles }
      }
    },
    staleTime: 60_000,
  })

  const doctorQuery = useQuery({
    queryKey: ['workspace-doctor'],
    queryFn: async () => {
      try {
        return await fetchWorkspaceDoctor()
      } catch {
        return {
          checks: [
            { label: 'python', status: 'skipped', output: ['demo mode'] },
            { label: 'npm', status: 'skipped', output: ['demo mode'] },
          ],
          timestamp: Date.now() / 1000,
        }
      }
    },
    staleTime: 60_000,
  })

  const runChecks = useMutation({
    mutationFn: async (dryRun: boolean) =>
      runWorkspaceChecks({
        categories: selectedCategories,
        dry_run: dryRun,
      }),
    onSuccess: (data) => {
      setLastReport(data)
      toast.success('Workspace checks completed')
      queryClient.invalidateQueries({ queryKey: ['workspace-scan'] })
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Workspace checks failed')
    },
  })

  const harnessQuery = useQuery({
    queryKey: ['workspace-harness-report'],
    queryFn: fetchHarnessReport,
    staleTime: 60_000,
  })

  const profiles = lastReport?.profiles ?? scanQuery.data?.projects ?? demoProfiles
  const summary =
    lastReport?.summary ||
    (harnessQuery.data
      ? {
          projects: harnessQuery.data.total_projects,
          failed: harnessQuery.data.failed_checks,
          passed: harnessQuery.data.passed_checks,
          skipped: harnessQuery.data.skipped_checks,
          checks: harnessQuery.data.total_checks,
          report_path: harnessQuery.data.report_path,
          root: harnessQuery.data.root,
          generated_at: harnessQuery.data.generated_at || Date.now(),
          run_id: harnessQuery.data.run_id,
          status: harnessQuery.data.status,
          dry_run: false,
        }
      : undefined)

  const totalPlannedChecks = useMemo(
    () =>
      profiles.reduce(
        (acc, p) =>
          acc +
          selectedCategories.reduce((inner, cat) => inner + (p.commands?.[cat]?.length || 0), 0),
        0
      ),
    [profiles, selectedCategories]
  )

  const toggleCategory = (category: string) => {
    setSelectedCategories((prev) =>
      prev.includes(category) ? prev.filter((c) => c !== category) : [...prev, category]
    )
  }

  const renderStatus = (status: string) => (
    <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusBadge(status)}`}>{status}</span>
  )

  return (
    <div className="space-y-6 px-4 py-6 sm:px-6 lg:px-8">
      <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.2em] text-[color:var(--osd-muted)]">Spec §4/§11 · Reliability</p>
          <h1 className="text-2xl font-semibold">Workspace Health & Automation</h1>
          <p className="text-[color:var(--osd-muted)]">
            Scan every repo, plan checks, and keep the runbooks aligned with the governed driver fabric.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => runChecks.mutate(true)}
            className="inline-flex items-center gap-2 rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2 text-sm font-medium hover:border-[color:var(--osd-accent)]"
            disabled={runChecks.isPending}
          >
            {runChecks.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <ClipboardList className="h-4 w-4" />}
            Dry-run checks
          </button>
          <button
            onClick={() => runChecks.mutate(false)}
            className="inline-flex items-center gap-2 rounded-lg bg-[color:var(--osd-accent)] px-3 py-2 text-sm font-semibold text-black shadow-[0_10px_40px_-20px_rgba(99,102,241,0.7)] hover:opacity-90"
            disabled={runChecks.isPending}
          >
            {runChecks.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Zap className="h-4 w-4" />}
            Execute checks
          </button>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <div className="rounded-2xl border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] p-4 shadow-sm">
          <div className="flex items-center justify-between">
            <p className="text-sm text-[color:var(--osd-muted)]">Repos detected</p>
            <Activity className="h-4 w-4 text-[color:var(--osd-muted)]" />
          </div>
          <p className="mt-2 text-3xl font-semibold">{profiles.length}</p>
          <p className="text-xs text-[color:var(--osd-muted)]">{scanQuery.data?.root || 'workspace'}</p>
        </div>
        <div className="rounded-2xl border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] p-4 shadow-sm">
          <div className="flex items-center justify-between">
            <p className="text-sm text-[color:var(--osd-muted)]">Checks planned</p>
            <Terminal className="h-4 w-4 text-[color:var(--osd-muted)]" />
          </div>
          <p className="mt-2 text-3xl font-semibold">{totalPlannedChecks}</p>
          <p className="text-xs text-[color:var(--osd-muted)]">selected categories per repo</p>
        </div>
        <div className="rounded-2xl border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] p-4 shadow-sm">
          <div className="flex items-center justify-between">
            <p className="text-sm text-[color:var(--osd-muted)]">Last report</p>
            <RefreshCw className="h-4 w-4 text-[color:var(--osd-muted)]" />
          </div>
          <p className="mt-2 text-3xl font-semibold">
            {summary ? `${summary.passed ?? 0} ✓ / ${summary.failed ?? 0} ✕` : '—'}
          </p>
          <p className="text-xs text-[color:var(--osd-muted)]">
            {summary?.status ? summary.status : summary?.dry_run ? 'Dry-run' : summary ? 'Executed' : 'Awaiting run'}
          </p>
          <p className="text-[10px] text-[color:var(--osd-muted)]">
            {formatTimestamp(summary?.generated_at)} {summary?.run_id ? `· run ${summary.run_id}` : ''}
          </p>
          {summary?.report_path && (
            <p className="text-[10px] text-[color:var(--osd-muted)] truncate">
              Report: {summary.report_path}
            </p>
          )}
        </div>
        <div className="rounded-2xl border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] p-4 shadow-sm">
          <div className="flex items-center justify-between">
            <p className="text-sm text-[color:var(--osd-muted)]">Doctor</p>
            <Shield className="h-4 w-4 text-[color:var(--osd-muted)]" />
          </div>
          <p className="mt-2 text-3xl font-semibold">
            {doctorQuery.data?.checks?.filter((c) => c.status != 'skipped').length ?? 0}
          </p>
          <p className="text-xs text-[color:var(--osd-muted)]">environment checks</p>
        </div>
      </div>

      <div className="rounded-2xl border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] shadow-sm">
        <div className="flex items-center justify-between border-b border-[color:var(--osd-border)] px-4 py-3">
          <div>
            <p className="text-sm font-semibold">Execution plan</p>
            <p className="text-xs text-[color:var(--osd-muted)]">
              Toggle categories to include in the next run. Dry-run keeps commands safe.
            </p>
          </div>
          <div className="flex gap-2">
            {['lint', 'test', 'build', 'security'].map((category) => (
              <button
                key={category}
                onClick={() => toggleCategory(category)}
                className={`rounded-full px-3 py-1 text-xs font-semibold border ${
                  selectedCategories.includes(category)
                    ? 'bg-[color:var(--osd-accent)] text-black border-[color:var(--osd-accent)]'
                    : 'border-[color:var(--osd-border)] text-[color:var(--osd-muted)]'
                }`}
              >
                {category}
              </button>
            ))}
          </div>
        </div>
        <div className="divide-y divide-[color:var(--osd-border)]">
          {profiles.map((profile) => (
            <div key={profile.name} className="grid gap-3 px-4 py-3 md:grid-cols-3 md:items-start">
              <div className="space-y-1">
                <p className="font-semibold">{profile.name}</p>
                <p className="text-xs text-[color:var(--osd-muted)]">{profile.root}</p>
                {profile.autofix_script && (
                  <p className="text-[10px] uppercase tracking-wide text-[color:var(--osd-muted)]">
                    autofix: {profile.autofix_script}
                  </p>
                )}
              </div>
              <div className="md:col-span-2 space-y-2">
                {Object.entries(profile.commands || {}).map(([category, commands]) => (
                  <div key={category} className="flex items-start gap-2 text-sm">
                    <span className="mt-0.5 rounded-md bg-[color:var(--osd-surface-strong)] px-2 py-1 text-[11px] font-semibold uppercase text-[color:var(--osd-muted)]">
                      {category}
                    </span>
                    <div className="space-y-1">
                      {commands.map((cmd, idx) => (
                        <code
                          key={idx}
                          className="block rounded-md bg-[color:var(--osd-surface-strong)] px-3 py-2 text-xs text-[color:var(--osd-text)]"
                        >
                          {Array.isArray(cmd) ? cmd.join(' ') : cmd}
                        </code>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <div className="rounded-2xl border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] p-4 shadow-sm lg:col-span-2">
          <div className="mb-3 flex items-center justify-between">
            <div>
              <p className="text-sm font-semibold">Recent results</p>
              <p className="text-xs text-[color:var(--osd-muted)]">
                Live once executed; falls back to demo signals when offline.
              </p>
            </div>
            <ClipboardList className="h-4 w-4 text-[color:var(--osd-muted)]" />
          </div>
          <div className="space-y-2">
            {(lastReport?.results || harnessQuery.data?.projects || []).slice(-10).map((result: any, idx: number) => (
              <div
                key={`${result.project || result.name}-${idx}`}
                className="flex items-start justify-between rounded-xl border border-[color:var(--osd-border)] bg-[color:var(--osd-surface-strong)] px-3 py-2"
              >
                <div className="space-y-0.5">
                  <p className="text-sm font-semibold">{result.project || result.name}</p>
                  {result.category && (
                    <p className="text-xs text-[color:var(--osd-muted)]">
                      {result.category} · {Array.isArray(result.command) ? result.command.join(' ') : result.command}
                    </p>
                  )}
                  {result.error && (
                    <p className="text-[11px] text-rose-400 line-clamp-2">Error: {result.error}</p>
                  )}
                  {result.output && (
                    <p className="text-[11px] text-[color:var(--osd-muted)] line-clamp-2">{result.output}</p>
                  )}
                  {result.commands && (
                    <p className="text-[11px] text-[color:var(--osd-muted)] line-clamp-2">
                      {(result.commands || []).slice(0, 2).join(' · ')}
                    </p>
                  )}
                  <p className="text-[10px] text-[color:var(--osd-muted)]">
                    {formatTimestamp(result.ran_at || result.generated_at)}{' '}
                    {result.duration_seconds ? `· ${result.duration_seconds.toFixed(1)}s` : ''}
                    {result.timeout_seconds ? ` (timeout ${result.timeout_seconds}s)` : ''}
                    {result.run_id ? ` · run ${result.run_id}` : ''}
                  </p>
                </div>
                {renderStatus(result.status)}
              </div>
            ))}
            {!lastReport && (
              <div className="rounded-xl border border-dashed border-[color:var(--osd-border)] bg-[color:var(--osd-surface-strong)] px-3 py-6 text-center text-sm text-[color:var(--osd-muted)]">
                Run a dry-run to preview commands, then execute to capture live results.
              </div>
            )}
          </div>
        </div>
        <div className="rounded-2xl border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] p-4 shadow-sm space-y-3">
          <div className="flex items-center justify-between">
            <p className="text-sm font-semibold">Doctor</p>
            <Hammer className="h-4 w-4 text-[color:var(--osd-muted)]" />
          </div>
          <div className="space-y-2">
            {doctorQuery.data?.checks?.map((check, idx) => (
              <div key={`${check.label}-${idx}`} className="flex items-start justify-between rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface-strong)] px-3 py-2">
                <div>
                  <p className="text-sm font-semibold">{check.label}</p>
                  <p className="text-[11px] text-[color:var(--osd-muted)]">
                    {(check.output || []).join(' · ') || 'No details'}
                  </p>
                </div>
                {renderStatus(check.status)}
              </div>
            ))}
            {!doctorQuery.data && <p className="text-sm text-[color:var(--osd-muted)]">Doctor results unavailable</p>}
          </div>
          <div className="rounded-lg border border-dashed border-[color:var(--osd-border)] bg-[color:var(--osd-surface-strong)] px-3 py-2 text-xs text-[color:var(--osd-muted)]">
            Keep env templates checked in and expose health via /workspace/doctor for CI gating.
          </div>
        </div>
        <div className="rounded-2xl border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] p-4 shadow-sm space-y-3">
          <div className="flex items-center justify-between">
            <p className="text-sm font-semibold">Latest run metadata</p>
            <Clock3 className="h-4 w-4 text-[color:var(--osd-muted)]" />
          </div>
          <div className="space-y-2 text-sm">
            <div className="rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface-strong)] px-3 py-2">
              <p className="text-xs text-[color:var(--osd-muted)]">Run ID</p>
              <p className="font-mono text-[13px]">{summary?.run_id || harnessQuery.data?.run_id || '—'}</p>
            </div>
            <div className="rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface-strong)] px-3 py-2">
              <p className="text-xs text-[color:var(--osd-muted)]">Generated at</p>
              <p className="text-sm">{formatTimestamp(summary?.generated_at || harnessQuery.data?.generated_at)}</p>
            </div>
            <div className="rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface-strong)] px-3 py-2">
              <p className="text-xs text-[color:var(--osd-muted)]">Report path</p>
              <p className="text-[13px] text-[color:var(--osd-muted)] break-all">
                {summary?.report_path || harnessQuery.data?.report_path || '—'}
              </p>
            </div>
            <div className="rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface-strong)] px-3 py-2">
              <p className="text-xs text-[color:var(--osd-muted)]">Workspace root</p>
              <p className="text-[13px] text-[color:var(--osd-muted)] break-all">
                {summary?.root || scanQuery.data?.root || harnessQuery.data?.root || '—'}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default WorkspaceHealth
