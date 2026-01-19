import LegacyHomePage from '@/components/templates/LegacyHomePage'

const metrics = [
    { label: 'Status', value: 'Active', detail: 'System operational' },
    { label: 'Workflows', value: '12', detail: 'Available workflows' },
    { label: 'Alerts', value: '0', detail: 'No critical alerts' },
    { label: 'Last Run', value: '2h ago', detail: 'Most recent execution' },
  ]

export default function VisionMetaStackHome() {
  return (
    <LegacyHomePage
      title="Vision Meta Stack Home"
      description="Capture strategic initiatives, vision artifacts, and meta stack updates."
      routeHint="/legacy/vision-meta-stack-home"
      metrics={metrics}
    />
  )
}
