import LegacyHomePage from '@/components/templates/LegacyHomePage'

const metrics = [
    { label: 'Status', value: 'Active', detail: 'System operational' },
    { label: 'Workflows', value: '12', detail: 'Available workflows' },
    { label: 'Alerts', value: '0', detail: 'No critical alerts' },
    { label: 'Last Run', value: '2h ago', detail: 'Most recent execution' },
  ]

export default function DocsSpecHome() {
  return (
    <LegacyHomePage
      title="Docs & Spec Home"
      description="Track documentation coverage, spec updates, and release notes."
      routeHint="/legacy/docs-spec-home"
      metrics={metrics}
    />
  )
}
