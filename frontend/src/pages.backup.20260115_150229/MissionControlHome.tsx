import MvpScaffold from '@/components/MvpScaffold'

const MissionControlHomePage = () => {
  return (
    <MvpScaffold
      title="Mission Control Home"
      description="MVP view for Mission Control Home. Configure inputs, environment, and execution to generate results."
      route="/personal-workstation-edition/mission-control"
      todo={[
        "Connect Mission Control Home KPIs and activity feed.",
        "Replace baseline metrics with live data sources.",
      ]}
    />
  )
}

export default MissionControlHomePage
