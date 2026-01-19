import MvpScaffold from '@/components/MvpScaffold'

const SystemBoundariesNonGoalsPage = () => {
  return (
    <MvpScaffold
      title="System Boundaries & Non-Goals"
      description="MVP view for System Boundaries & Non-Goals. Configure inputs, environment, and execution to generate results."
      route="/enterprise-control-plane-add-ons/mission-architecture/system-boundaries-non-goals"
      todo={[
        "Connect System Boundaries & Non-Goals KPIs and activity feed.",
        "Replace baseline metrics with live data sources.",
      ]}
    />
  )
}

export default SystemBoundariesNonGoalsPage
