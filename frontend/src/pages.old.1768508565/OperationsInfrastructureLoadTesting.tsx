import MvpScaffold from '@/components/MvpScaffold'

const OperationsInfrastructureLoadTestingPage = () => {
  return (
    <MvpScaffold
      title="Load Testing"
      description="MVP view for Load Testing. Configure inputs, environment, and execution to generate results."
      route="/enterprise-control-plane-add-ons/operations-infrastructure/load-testing"
      todo={[
        "Connect Load Testing KPIs and activity feed.",
        "Replace baseline metrics with live data sources.",
      ]}
    />
  )
}

export default OperationsInfrastructureLoadTestingPage
