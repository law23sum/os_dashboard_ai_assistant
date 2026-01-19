import MvpScaffold from '@/components/MvpScaffold'

const UseCasesMapPage = () => {
  return (
    <MvpScaffold
      title="Use Cases Map"
      description="MVP view for Use Cases Map. Configure inputs, environment, and execution to generate results."
      route="/enterprise-control-plane-add-ons/mission-architecture/use-cases-map"
      todo={[
        "Connect Use Cases Map KPIs and activity feed.",
        "Replace baseline metrics with live data sources.",
      ]}
    />
  )
}

export default UseCasesMapPage
