import LegacyHomePage from '@/components/templates/LegacyHomePage'

const metrics = [
    { label: 'Status', value: 'Active', detail: 'System operational' },
    { label: 'Workflows', value: '12', detail: 'Available workflows' },
    { label: 'Alerts', value: '0', detail: 'No critical alerts' },
    { label: 'Last Run', value: '2h ago', detail: 'Most recent execution' },
  ]

export default function DriversIntegrationsHome() {
  return (
    <LegacyHomePage
      title="Drivers & Integrations Home"
      description="Manage driver health, marketplace readiness, and integration status."
      routeHint="/legacy/drivers-integrations-home"
      metrics={metrics}
    />
  )
}
