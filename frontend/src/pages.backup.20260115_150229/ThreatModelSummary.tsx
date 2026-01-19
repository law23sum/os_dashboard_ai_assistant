import MvpScaffold from '@/components/MvpScaffold'

const ThreatModelSummaryPage = () => {
  return (
    <MvpScaffold
      title="Threat Model Summary"
      description="MVP view for Threat Model Summary. Configure inputs, environment, and execution to generate results."
      route="/enterprise-control-plane-add-ons/mission-architecture/threat-model-summary"
      todo={[
        "Connect Threat Model Summary KPIs and activity feed.",
        "Replace baseline metrics with live data sources.",
      ]}
    />
  )
}

export default ThreatModelSummaryPage
