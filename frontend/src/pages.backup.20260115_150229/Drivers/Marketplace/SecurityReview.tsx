import { useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { Shield, Search, FileText, Settings, RefreshCw, Radar } from 'lucide-react'
import apiClient, { apiPath } from '@/lib/apiClient'
import { toast } from '@/utils/toast'
import { SecurityStatus, SecurityReport } from '@/types'

const severityClasses: Record<string, string> = {
  low: 'bg-green-500/10 text-green-300 border border-green-500/20',
  medium: 'bg-yellow-500/10 text-yellow-300 border border-yellow-500/20',
  high: 'bg-red-500/10 text-red-300 border border-red-500/20',
  critical: 'bg-red-600/20 text-red-100 border border-red-600/40',
}

export default function Security() {
  const [scanTarget, setScanTarget] = useState('system')
  const [report, setReport] = useState<SecurityReport | null>(null)
  const [investigation, setInvestigation] = useState<string | null>(null)

  const statusQuery = useQuery({
    queryKey: ['security-status'],
    queryFn: async () => {
      const response = await apiClient.get<SecurityStatus>(apiPath('security/status'))
      return response.data
    },
    refetchInterval: 10000,
  })

  const startScan = useMutation({
    mutationFn: () =>
      apiClient.post(apiPath('security/scan/start'), {
        target: scanTarget,
      }),
    onSuccess: (payload) => {
      toast.success(payload.data?.message ?? 'Security scan initiated')
      statusQuery.refetch()
    },
    onError: () => toast.error('Failed to start threat scan'),
  })

  const viewReport = useMutation({
    mutationFn: () => apiClient.post(apiPath('security/report/view')),
    onSuccess: (payload) => {
      toast.success('Security report loaded')
      setReport(payload.data || payload)
    },
    onError: () => toast.error('Failed to fetch security report'),
  })

  const configure = useMutation({
    mutationFn: () =>
      apiClient.post(apiPath('security/configure'), {
        detection_level: 'balanced',
        auto_response: true,
      }),
    onSuccess: () => {
      toast.success('Security system configured')
      statusQuery.refetch()
    },
    onError: () => toast.error('Unable to configure security system'),
  })

  const investigate = useMutation({
    mutationFn: (eventId: string) =>
      apiClient.post(apiPath('security/event/investigate'), { event_id: eventId }),
    onSuccess: (payload) => {
      toast.success('Investigation recorded')
      setInvestigation(JSON.stringify(payload.data?.investigation ?? payload, null, 2))
    },
    onError: () => toast.error('Investigation failed'),
  })

  const status = statusQuery.data

  return (
    <div className="px-4 py-6 sm:px-0 space-y-6">
      <header className="glass-panel p-6 border border-[color:var(--osd-border)]">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.5em] text-[color:var(--osd-muted)]">Security Operations</p>
            <h1 className="text-3xl font-semibold flex items-center gap-3 text-[color:var(--osd-text)]">
              <Shield className="w-8 h-8 text-[color:var(--osd-success)]" />
              AI Security Threat Detection
            </h1>
            <p className="mt-2 text-sm text-[color:var(--osd-muted)] max-w-3xl">
              AI-driven threat detection across the stack with automated scanning, investigation, and response.
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => startScan.mutate()}
              disabled={startScan.isPending}
              className="btn-tonal bg-[color:var(--osd-accent)] text-white hover:bg-[color:var(--osd-accentHover)]"
            >
              <Search className="w-4 h-4" />
              Start Scan
            </button>
            <button
              onClick={() => viewReport.mutate()}
              className="btn-tonal border border-[color:var(--osd-border)] text-[color:var(--osd-text)]"
            >
              <FileText className="w-4 h-4" />
              View Report
            </button>
            <button
              onClick={() => configure.mutate()}
              className="btn-tonal border border-[color:var(--osd-border)] text-[color:var(--osd-text)]"
            >
              <Settings className="w-4 h-4" />
              Configure
            </button>
            <button
              onClick={() => statusQuery.refetch()}
              className="btn-tonal border border-[color:var(--osd-border)] text-[color:var(--osd-text)]"
            >
              <RefreshCw className="w-4 h-4" />
              Refresh
            </button>
          </div>
        </div>
      </header>

      <section className="glass-panel p-6 border border-[color:var(--osd-border)] space-y-4">
        <div className="flex flex-wrap items-center gap-3">
          <Radar className="w-6 h-6 text-[color:var(--osd-accent)]" />
          <p className="text-sm text-[color:var(--osd-muted)]">{status?.system_status}</p>
        </div>
        <div className="grid gap-4 md:grid-cols-3">
          <Metric label="Scans today" value={`${status?.metrics.scans_today ?? 0}`} />
          <Metric label="Threats blocked" value={`${status?.metrics.threats_blocked ?? 0}`} />
          <Metric label="Detection accuracy" value={`${(status?.metrics.detection_accuracy ?? 0).toFixed(2)}`} suffix=" %" />
        </div>
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:gap-4">
          <label className="flex-1 text-sm text-[color:var(--osd-muted)] space-y-1">
            Scoped token / target
            <input
              value={scanTarget}
              onChange={(e) => setScanTarget(e.target.value)}
              placeholder="system | network | endpoint"
              className="w-full rounded-xl bg-[color:var(--osd-surfaceAlt)] border border-[color:var(--osd-border)] px-3 py-2 text-[color:var(--osd-text)] focus:border-[color:var(--osd-accent)] focus:outline-none"
            />
          </label>
          <span className="glass-pill inline-flex items-center gap-2">
            {status?.threat_detection_enabled ? 'Auto response' : 'Manual response'}
          </span>
        </div>
      </section>

      <section className="grid gap-6 lg:grid-cols-[1.2fr,0.8fr]">
        <div className="glass-panel p-6 border border-[color:var(--osd-border)] space-y-4">
          <h2 className="text-lg font-semibold text-[color:var(--osd-text)]">Recent Events</h2>
          <div className="space-y-3 max-h-80 overflow-y-auto">
            {status?.recent_events.map((event) => (
              <div
                key={event.id}
                className={`rounded-xl border px-4 py-3 flex items-start justify-between gap-4 ${severityClasses[event.severity] ?? 'border border-[color:var(--osd-border)] text-[color:var(--osd-text)]'}`}
              >
                <div>
                  <p className="text-sm font-semibold">{event.description}</p>
                  <p className="text-xs text-[color:var(--osd-muted)]">
                    {event.type} · {event.source_ip} · {new Date(event.timestamp).toLocaleString()}
                  </p>
                </div>
                <button
                  onClick={() => investigate.mutate(event.id)}
                  className="text-xs text-[color:var(--osd-accent)] transition-colors hover:text-[color:var(--osd-accentHover)]"
                >
                  Investigate
                </button>
              </div>
            ))}
          </div>
        </div>
        <div className="glass-panel p-6 border border-[color:var(--osd-border)] space-y-4">
          <h2 className="text-lg font-semibold text-[color:var(--osd-text)]">Security Report</h2>
          {report ? (
            <div className="space-y-3 text-sm text-[color:var(--osd-muted)]">
              <p>Generated at {new Date(report.generated_at).toLocaleString()}</p>
              <p>Total scans: {report.scan_summary?.total_scans ?? 'n/a'}</p>
              <p>
                Threats found: {report.scan_summary?.threats_found ?? 'n/a'} · Critical{' '}
                {report.scan_summary?.critical_findings ?? '0'}
              </p>
              <p>Top threats:</p>
              <ul className="list-disc list-inside space-y-1">
                {report.top_threats.map((threat) => (
                  <li key={threat.type}>
                    {threat.type}: {threat.count}
                  </li>
                ))}
              </ul>
              <p>Recommendations:</p>
              <ul className="list-disc list-inside space-y-1">
                {report.recommendations.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </div>
          ) : (
            <p className="text-sm text-[color:var(--osd-muted)]">Run a report to view insights.</p>
          )}
          {investigation && (
            <div>
              <h3 className="text-sm font-semibold text-[color:var(--osd-text)]">Investigation</h3>
              <pre className="mt-2 rounded-xl bg-[color:var(--osd-surfaceAlt)] border border-[color:var(--osd-border)] p-3 text-xs text-[color:var(--osd-muted)] font-mono overflow-auto max-h-48">
                {investigation}
              </pre>
            </div>
          )}
        </div>
      </section>
    </div>
  )
}

function Metric({ label, value, suffix = '' }: { label: string; value: string; suffix?: string }) {
  return (
    <div className="rounded-xl border border-[color:var(--osd-border)] bg-[color:var(--osd-surfaceAlt)] p-3">
      <p className="text-xs text-[color:var(--osd-muted)]">{label}</p>
      <p className="text-2xl font-semibold text-[color:var(--osd-text)]">
        {value}
        {suffix && <span className="text-sm font-medium text-[color:var(--osd-muted)]">{suffix}</span>}
      </p>
    </div>
  )
}
