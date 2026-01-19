import MvpScaffold from '@/components/MvpScaffold'

const LoggingTracingOverviewPage = () => {
  return (
    <MvpScaffold
      title="Logging & Tracing Overview"
      description="MVP view for Logging & Tracing Overview. Configure inputs, environment, and execution to generate results."
      route="/enterprise-control-plane-add-ons/observability-evidence/logging-tracing-overview"
      todo={[
        "Connect Logging & Tracing Overview KPIs and activity feed.",
        "Replace baseline metrics with live data sources.",
      ]}
    />
  )
}

export default LoggingTracingOverviewPage
