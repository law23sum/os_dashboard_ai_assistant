import MvpScaffold from '@/components/MvpScaffold'

const WorkspacesHomePage = () => {
  return (
    <MvpScaffold
      title="Workspaces Home"
      description="MVP view for Workspaces Home. Configure inputs, environment, and execution to generate results."
      route="/personal-workstation-edition/workspaces"
      todo={[
        "Connect Workspaces Home KPIs and activity feed.",
        "Replace baseline metrics with live data sources.",
      ]}
    />
  )
}

export default WorkspacesHomePage
