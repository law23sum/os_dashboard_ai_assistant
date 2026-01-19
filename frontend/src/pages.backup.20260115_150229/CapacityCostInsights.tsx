import MvpScaffold from '@/components/MvpScaffold'

const CapacityCostInsightsPage = () => {
  return (
    <MvpScaffold
      title="Capacity & Cost Insights"
      description="MVP view for Capacity & Cost Insights. Configure inputs, environment, and execution to generate results."
      route="/personal-workstation-edition/workspaces/capacity-cost-insights"
      todo={[
        "Connect Capacity & Cost Insights KPIs and activity feed.",
        "Replace baseline metrics with live data sources.",
      ]}
    />
  )
}

export default CapacityCostInsightsPage
