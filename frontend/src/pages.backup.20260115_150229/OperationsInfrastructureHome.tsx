import LegacyHomePage from '@/components/templates/LegacyHomePage'

const metrics = [
    { label: 'Status', value: 'Active', detail: 'System operational' },
    { label: 'Workflows', value: '12', detail: 'Available workflows' },
    { label: 'Alerts', value: '0', detail: 'No critical alerts' },
    { label: 'Last Run', value: '2h ago', detail: 'Most recent execution' },
  ]

export default function OperationsInfrastructureHome() {
  return (
    <LegacyHomePage
      title="Operations Infrastructure Home"
      description="Coordinate infrastructure capacity, uptime, and change windows."
      routeHint="/legacy/operations-infrastructure-home"
      metrics={metrics}
    />
  )
}
