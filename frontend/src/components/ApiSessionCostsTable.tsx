import { useQuery } from '@tanstack/react-query'
import { RefreshCw } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { apiSessionCostsApi } from '../services/api'

const formatCost = (value: number) => `$${value.toFixed(4)}`

export default function ApiSessionCostsTable() {
  const query = useQuery({
    queryKey: ['api-session-costs'],
    queryFn: apiSessionCostsApi.get,
    refetchInterval: 60_000,
  })

  if (query.isLoading) {
    return (
      <div className="flex h-32 items-center justify-center">
        <div className="h-10 w-10 animate-spin rounded-full border-b-2 border-[color:var(--osd-accent)]" />
      </div>
    )
  }

  if (query.error) {
    return (
      <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">
        Unable to load API session costs. Please ensure the backend server is running.
      </div>
    )
  }

  const data = query.data
  const items = data?.items ?? []

  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div>
          <p className="text-sm font-semibold text-[color:var(--osd-text)]">API Session Costs</p>
          <p className="text-xs text-[color:var(--osd-muted)]">
            Seeded estimates from the local DB. Credits are zero, so remaining time is 0.
          </p>
        </div>
        <Button
          variant="secondary"
          onClick={() => query.refetch()}
          disabled={query.isFetching}
          className="inline-flex items-center gap-2"
        >
          <RefreshCw className="h-4 w-4" />
          Refresh
        </Button>
      </div>

      {data?.error && (
        <div className="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
          {data.error}
          {data.report_path && (
            <span className="mt-2 block text-xs text-amber-700">
              Report saved to: <code>{data.report_path}</code>
            </span>
          )}
        </div>
      )}

      {items.length === 0 ? (
        <div className="rounded-xl border border-[color:var(--osd-border)]/70 bg-[color:var(--osd-surface)] px-4 py-6 text-sm text-[color:var(--osd-muted)]">
          No API session cost data available yet.
          {data?.report_path && (
            <span className="mt-2 block text-xs text-[color:var(--osd-muted)]">
              Report saved to: <code>{data.report_path}</code>
            </span>
          )}
        </div>
      ) : (
        <div className="overflow-x-auto rounded-xl border border-[color:var(--osd-border)]/60">
          <table className="min-w-full divide-y divide-[color:var(--osd-border)] text-sm">
            <thead className="bg-[color:var(--osd-surfaceAlt)]">
              <tr>
                <th className="px-4 py-3 text-left font-semibold text-[color:var(--osd-text)]">Provider</th>
                <th className="px-4 py-3 text-left font-semibold text-[color:var(--osd-text)]">Version</th>
                <th className="px-4 py-3 text-right font-semibold text-[color:var(--osd-text)]">
                  Cost / Session
                </th>
                <th className="px-4 py-3 text-right font-semibold text-[color:var(--osd-text)]">Credits</th>
                <th className="px-4 py-3 text-right font-semibold text-[color:var(--osd-text)]">
                  Remaining Time (min)
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[color:var(--osd-border)]/60">
              {items.map((item) => (
                <tr key={`${item.provider}-${item.version}`} className="bg-[color:var(--osd-surface)]">
                  <td className="px-4 py-3 text-[color:var(--osd-text)]">{item.provider_label}</td>
                  <td className="px-4 py-3 text-[color:var(--osd-muted)]">{item.version}</td>
                  <td className="px-4 py-3 text-right text-[color:var(--osd-text)]">
                    {formatCost(item.cost_per_session_usd)}
                  </td>
                  <td className="px-4 py-3 text-right text-[color:var(--osd-text)]">
                    {item.credits_remaining.toFixed(0)}
                  </td>
                  <td className="px-4 py-3 text-right text-[color:var(--osd-text)]">
                    {item.remaining_minutes}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="flex flex-wrap items-center justify-between gap-3 text-xs text-[color:var(--osd-muted)]">
        <span>Credits remaining: {data?.credits_remaining ?? 0}</span>
        {data?.generated_at && <span>Generated: {new Date(data.generated_at).toLocaleString()}</span>}
      </div>
    </div>
  )
}
