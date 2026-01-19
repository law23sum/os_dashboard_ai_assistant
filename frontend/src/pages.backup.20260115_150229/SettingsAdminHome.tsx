import LegacyHomePage from '@/components/templates/LegacyHomePage'

const metrics = [
    { label: 'Status', value: 'Active', detail: 'System operational' },
    { label: 'Workflows', value: '12', detail: 'Available workflows' },
    { label: 'Alerts', value: '0', detail: 'No critical alerts' },
    { label: 'Last Run', value: '2h ago', detail: 'Most recent execution' },
  ]

export default function SettingsAdminHome() {
  return (
    <LegacyHomePage
      title="Settings Admin Home"
      description="Oversee admin settings, access reviews, and system status."
      routeHint="/legacy/settings-admin-home"
      metrics={metrics}
    />
  )
}
