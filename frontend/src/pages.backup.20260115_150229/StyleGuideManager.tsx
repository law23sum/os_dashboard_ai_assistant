import MvpScaffold from '@/components/MvpScaffold'

const StyleGuideManagerPage = () => {
  return (
    <MvpScaffold
      title="Style Guide Manager"
      description="MVP view for Style Guide Manager. Configure inputs, environment, and execution to generate results."
      route="/personal-workstation-edition/workspaces/style-guide-manager"
      todo={[
        "Connect Style Guide Manager KPIs and activity feed.",
        "Replace baseline metrics with live data sources.",
      ]}
    />
  )
}

export default StyleGuideManagerPage
