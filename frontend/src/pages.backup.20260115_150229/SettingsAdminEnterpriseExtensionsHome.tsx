import LegacyHomePage from '@/components/templates/LegacyHomePage'

const metrics = [
    { label: 'Status', value: 'Active', detail: 'System operational' },
    { label: 'Workflows', value: '12', detail: 'Available workflows' },
    { label: 'Alerts', value: '0', detail: 'No critical alerts' },
    { label: 'Last Run', value: '2h ago', detail: 'Most recent execution' },
  ]

export default function SettingsAdminEnterpriseExtensionsHome() {
  return (
    <LegacyHomePage
      title="Enterprise Extensions Home"
      description="Review enterprise extensions, configuration, and tenant alignment."
      routeHint="/legacy/settings-admin-enterprise-extensions-home"
      metrics={metrics}
    />
  )
}
