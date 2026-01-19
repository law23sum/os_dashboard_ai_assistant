import LegacyHomePage from '@/components/templates/LegacyHomePage'

const metrics = [
    { label: 'Status', value: 'Active', detail: 'System operational' },
    { label: 'Workflows', value: '12', detail: 'Available workflows' },
    { label: 'Alerts', value: '0', detail: 'No critical alerts' },
    { label: 'Last Run', value: '2h ago', detail: 'Most recent execution' },
  ]

export default function DataKnowledgeHome() {
  return (
    <LegacyHomePage
      title="Data & Knowledge Home"
      description="Monitor data governance, lineage, and knowledge services."
      routeHint="/legacy/data-knowledge-home"
      metrics={metrics}
    />
  )
}
