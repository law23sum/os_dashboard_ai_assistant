import LegacyHomePage from '@/components/templates/LegacyHomePage'

const metrics = [
    { label: 'Status', value: 'Active', detail: 'System operational' },
    { label: 'Workflows', value: '12', detail: 'Available workflows' },
    { label: 'Alerts', value: '0', detail: 'No critical alerts' },
    { label: 'Last Run', value: '2h ago', detail: 'Most recent execution' },
  ]

export default function RoadmapRisksHome() {
  return (
    <LegacyHomePage
      title="Roadmap Risks Home"
      description="Track roadmap dependencies, risks, and mitigation plans."
      routeHint="/legacy/roadmap-risks-home"
      metrics={metrics}
    />
  )
}
