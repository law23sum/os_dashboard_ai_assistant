import MvpScaffold from '@/components/MvpScaffold'

const SettingsAdminHomePage = () => {
  return (
    <MvpScaffold
      title="Settings & Admin Home"
      description="MVP view for Settings & Admin Home. Configure inputs, environment, and execution to generate results."
      route="/personal-workstation-edition/settings-admin"
      todo={[
        "Connect Settings & Admin Home KPIs and activity feed.",
        "Replace baseline metrics with live data sources.",
      ]}
    />
  )
}

export default SettingsAdminHomePage
