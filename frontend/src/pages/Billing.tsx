import { useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { RefreshCw, CreditCard, Activity, Shield, TrendingUp } from 'lucide-react'
import apiClient, { apiPath } from '../lib/apiClient'
import type { BillingUsage } from '../types'

const fetchBillingUsage = async (): Promise<BillingUsage> => {
  const { data } = await apiClient.get<BillingUsage>(apiPath('billing/usage'))
  return data
}

const COST_PER_AGENT_RUN = 0.02

export default function Billing() {
  const billingQuery = useQuery({
    queryKey: ['billing-usage'],
    queryFn: fetchBillingUsage,
    refetchInterval: 60_000,
  })

  const usage = billingQuery.data
  const records = usage?.records ?? []

  const aggregate = useMemo(() => {
    const totalOps = records.length
    const totalCost = usage?.estimated_cost ?? totalOps * COST_PER_AGENT_RUN
    const avgCost = totalOps > 0 ? totalCost / totalOps : 0
    const latest = records[0]
    return {
      totalOps,
      totalCost,
      avgCost,
      latestAgent: latest?.agent ?? '—',
    }
  }, [records, usage?.estimated_cost])

  if (billingQuery.isLoading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="h-12 w-12 animate-spin rounded-full border-b-2 border-[color:var(--osd-accent)]" />
      </div>
    )
  }

  return (
    <div className="space-y-8 px-4 py-8 text-[color:var(--osd-text)]">
      <header className="rounded-3xl bg-gradient-to-r from-[var(--osd-accentBlue)] via-[var(--osd-accent)] to-[var(--osd-accentPurple)] p-8 shadow-2xl shadow-slate-900/40">
        <div className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.35em] text-white/70">Billing · Usage · Evidence</p>
            <h1 className="mt-2 text-3xl font-bold">Billing & Usage Fabric</h1>
            <p className="mt-2 max-w-3xl text-sm text-white/85">
              Live data from <code className="rounded bg-white/20 px-2 py-0.5 text-xs">/billing/usage</code> mirrors the Tkinter
              console. Runs appear in the ledger below and fuel Evidence Packs for finance, security, and regulators.
            </p>
          </div>
          <button
            onClick={() => billingQuery.refetch()}
            className="inline-flex items-center rounded-full bg-white/15 px-5 py-3 text-sm font-semibold text-white hover:bg-white/25"
          >
            <RefreshCw className="mr-2 h-4 w-4" />
            Refresh
          </button>
        </div>
        <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <HeroStat label="Estimated Cost" value={`$${aggregate.totalCost.toFixed(2)}`} detail={usage?.currency ?? 'USD'} />
          <HeroStat label="Agent Operations" value={aggregate.totalOps} detail="Ledger-backed records" />
          <HeroStat label="Avg Cost / Run" value={`$${aggregate.avgCost.toFixed(3)}`} detail="20¢ per 10 ops" />
          <HeroStat label="Latest Agent" value={aggregate.latestAgent} detail="Most recent ledger entry" />
        </div>
      </header>

      <section className="grid gap-4 lg:grid-cols-4">
        <InsightCard
          icon={<CreditCard className="h-5 w-5" />}
          title="Active Contract"
          body="Consumption billing aligned to Agent Runs. Each operation is logged + priced for compliance."
        />
        <InsightCard
          icon={<Activity className="h-5 w-5" />}
          title="Usage Telemetry"
          body="Combines Tkinter historical data with modern React dashboards so browser + desktop stay matched."
        />
        <InsightCard
          icon={<Shield className="h-5 w-5" />}
          title="Regulator Evidence"
          body="Records link to Ledger IDs, enabling instant Evidence Packs for audits, SOC, or BC/DR requests."
        />
        <InsightCard
          icon={<TrendingUp className="h-5 w-5" />}
          title="Cost Forecast"
          body="Estimated cost increases automatically as agent runs accumulate — no separate scripts required."
        />
      </section>

      <section className="glass-panel border border-[color:var(--osd-border)] p-6">
        <h2 className="text-lg font-semibold text-[color:var(--osd-text)]">Usage Records</h2>
        <p className="text-sm text-[color:var(--osd-muted)]">Mirrors the Tkinter HTML list and the `/billing/usage` JSON feed.</p>
        <div className="mt-4 divide-y divide-[color:var(--osd-border)]">
          {records.length === 0 && (
            <p className="py-8 text-sm text-[color:var(--osd-muted)]">No usage records available yet.</p>
          )}
          {records.map((record) => (
            <article key={`${record.id}-${record.created_at}`} className="py-4">
              <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
                <div>
                  <p className="font-semibold text-[color:var(--osd-text)]">
                    {record.agent} · {record.action_type}
                  </p>
                  <p className="text-xs uppercase tracking-[0.25em] text-[color:var(--osd-muted)]">
                    Ledger ID #{record.id}
                  </p>
                </div>
                <div className="text-sm text-[color:var(--osd-muted)]">
                  {new Date(record.created_at).toLocaleString()}
                </div>
              </div>
              <p className="mt-2 text-sm text-[color:var(--osd-muted)]">{record.output_summary || 'No summary provided.'}</p>
              <div className="mt-3 flex flex-wrap gap-3 text-xs">
                <span className="rounded-full border border-[color:var(--osd-border)] px-3 py-1 text-[color:var(--osd-muted)]">
                  Cost Impact · ${COST_PER_AGENT_RUN.toFixed(2)}
                </span>
                {record.git_commit_hash && (
                  <span className="rounded-full border border-[color:var(--osd-border)] px-3 py-1 text-[color:var(--osd-muted)]">
                    Commit {record.git_commit_hash.slice(0, 7)}
                  </span>
                )}
              </div>
            </article>
          ))}
        </div>
      </section>
    </div>
  )
}

function HeroStat({ label, value, detail }: { label: string; value: string | number; detail: string }) {
  return (
    <div className="rounded-2xl bg-white/10 p-4 text-white">
      <p className="text-xs uppercase tracking-wide text-white/75">{label}</p>
      <p className="mt-2 text-2xl font-bold">{value}</p>
      <p className="text-xs text-white/80">{detail}</p>
    </div>
  )
}

function InsightCard({ icon, title, body }: { icon: React.ReactNode; title: string; body: string }) {
  return (
    <div className="glass-panel border border-[color:var(--osd-border)] p-4">
      <div className="flex items-center gap-3 text-[color:var(--osd-text)]">
        <div className="rounded-full bg-[color:var(--osd-accentSoft)] p-2 text-[color:var(--osd-accent)]">{icon}</div>
        <p className="text-sm font-semibold">{title}</p>
      </div>
      <p className="mt-3 text-sm text-[color:var(--osd-muted)]">{body}</p>
    </div>
  )
}
