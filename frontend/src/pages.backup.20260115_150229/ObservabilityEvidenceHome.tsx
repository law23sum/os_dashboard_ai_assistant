import LegacyHomePage from '@/components/templates/LegacyHomePage'

const metrics = [
    { label: 'Status', value: 'Active', detail: 'System operational' },
    { label: 'Workflows', value: '12', detail: 'Available workflows' },
    { label: 'Alerts', value: '0', detail: 'No critical alerts' },
    { label: 'Last Run', value: '2h ago', detail: 'Most recent execution' },
  ]

export default function ObservabilityEvidenceHome() {
  return (
    <LegacyHomePage
      title="Observability Evidence Home"
      description="Aggregate observability evidence, traces, and audit exports."
      routeHint="/legacy/observability-evidence-home"
      metrics={metrics}
    />
  )
}
