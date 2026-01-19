import MvpScaffold from '@/components/MvpScaffold'

const PerformanceTargetsPage = () => {
  return (
    <MvpScaffold
      title="Performance Targets"
      description="MVP view for Performance Targets. Configure inputs, environment, and execution to generate results."
      route="/enterprise-control-plane-add-ons/mission-architecture/performance-targets"
      todo={[
        "Connect Performance Targets KPIs and activity feed.",
        "Replace baseline metrics with live data sources.",
      ]}
    />
  )
}

export default PerformanceTargetsPage
