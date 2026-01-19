import MvpScaffold from '@/components/MvpScaffold'

const PersonalWorkstationBuildTestInsightsPage = () => {
  return (
    <MvpScaffold
      title="Build/Test Insights"
      description="MVP view for Build/Test Insights. Configure inputs, environment, and execution to generate results."
      route="/personal-workstation-edition/workspaces/build-test-insights"
      todo={[
        "Connect Build/Test Insights KPIs and activity feed.",
        "Replace baseline metrics with live data sources.",
      ]}
    />
  )
}

export default PersonalWorkstationBuildTestInsightsPage
