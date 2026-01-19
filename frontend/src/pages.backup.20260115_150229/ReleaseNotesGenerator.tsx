import MvpScaffold from '@/components/MvpScaffold'

const ReleaseNotesGeneratorPage = () => {
  return (
    <MvpScaffold
      title="Release Notes Generator"
      description="MVP view for Release Notes Generator. Configure inputs, environment, and execution to generate results."
      route="/personal-workstation-edition/workspaces/release-notes-generator"
      todo={[
        "Connect Release Notes Generator KPIs and activity feed.",
        "Replace baseline metrics with live data sources.",
      ]}
    />
  )
}

export default ReleaseNotesGeneratorPage
