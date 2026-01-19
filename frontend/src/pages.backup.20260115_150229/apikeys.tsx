import MvpScaffold from '@/components/MvpScaffold'

const APIKeysPage = () => {
  return (
    <MvpScaffold
      title="API Keys"
      description="MVP view for API Keys. Configure inputs, environment, and execution to generate results."
      route="/personal-workstation-edition/settings-admin/api-keys"
      todo={[
        "Connect API Keys KPIs and activity feed.",
        "Replace baseline metrics with live data sources.",
      ]}
    />
  )
}

export default APIKeysPage
