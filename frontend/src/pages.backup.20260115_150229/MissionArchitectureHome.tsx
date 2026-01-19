import LegacyHomePage from '@/components/templates/LegacyHomePage'

const metrics = [
    { label: 'Status', value: 'Active', detail: 'System operational' },
    { label: 'Workflows', value: '12', detail: 'Available workflows' },
    { label: 'Alerts', value: '0', detail: 'No critical alerts' },
    { label: 'Last Run', value: '2h ago', detail: 'Most recent execution' },
  ]

export default function MissionArchitectureHome() {
  return (
    <LegacyHomePage
      title="Mission Architecture Home"
      description="Assess mission architecture plans, dependencies, and risk posture."
      routeHint="/legacy/mission-architecture-home"
      metrics={metrics}
    />
  )
}
