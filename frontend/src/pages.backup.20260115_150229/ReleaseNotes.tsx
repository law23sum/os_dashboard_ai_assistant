import MvpScaffold from '@/components/MvpScaffold'

const ReleaseNotesPage = () => {
  return (
    <MvpScaffold
      title="Release Notes"
      description="MVP view for Release Notes. Configure inputs, environment, and execution to generate results."
      route="/personal-workstation-edition/docs-spec/release-notes"
      todo={[
        "Connect Release Notes KPIs and activity feed.",
        "Replace baseline metrics with live data sources.",
      ]}
    />
  )
}

export default ReleaseNotesPage
