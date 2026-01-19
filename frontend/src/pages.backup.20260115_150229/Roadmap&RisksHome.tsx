import MvpScaffold from '@/components/MvpScaffold'

const RoadmapRisksHomePage = () => {
  return (
    <MvpScaffold
      title="Roadmap & Risks Home"
      description="MVP view for Roadmap & Risks Home. Configure inputs, environment, and execution to generate results."
      route="/enterprise-control-plane-add-ons/roadmap-risks"
      todo={[
        "Connect Roadmap & Risks Home KPIs and activity feed.",
        "Replace baseline metrics with live data sources.",
      ]}
    />
  )
}

export default RoadmapRisksHomePage
