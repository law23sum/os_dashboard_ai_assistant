import MvpScaffold from '@/components/MvpScaffold'

const GettingStartedPage = () => {
  return (
    <MvpScaffold
      title="Getting Started"
      description="MVP view for Getting Started. Configure inputs, environment, and execution to generate results."
      route="/personal-workstation-edition/docs-spec/getting-started"
      todo={[
        "Connect Getting Started KPIs and activity feed.",
        "Replace baseline metrics with live data sources.",
      ]}
    />
  )
}

export default GettingStartedPage
