import MvpScaffold from '@/components/MvpScaffold'

const WorkspacesEnterpriseExtensionsHomePage = () => {
  return (
    <MvpScaffold
      title="Workspaces (Enterprise Extensions) Home"
      description="MVP view for Workspaces (Enterprise Extensions) Home. Configure inputs, environment, and execution to generate results."
      route="/enterprise-control-plane-add-ons/workspaces-(enterprise-extensions)"
      todo={[
        "Connect Workspaces (Enterprise Extensions) Home KPIs and activity feed.",
        "Replace baseline metrics with live data sources.",
      ]}
    />
  )
}

export default WorkspacesEnterpriseExtensionsHomePage
