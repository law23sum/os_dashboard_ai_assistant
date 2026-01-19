import MvpScaffold from '@/components/MvpScaffold'

const AIFabricHomePage = () => {
  return (
    <MvpScaffold
      title="AI Fabric Home"
      description="MVP view for AI Fabric Home. Configure inputs, environment, and execution to generate results."
      route="/personal-workstation-edition/ai-fabric"
      todo={[
        "Connect AI Fabric Home KPIs and activity feed.",
        "Replace baseline metrics with live data sources.",
      ]}
    />
  )
}

export default AIFabricHomePage
