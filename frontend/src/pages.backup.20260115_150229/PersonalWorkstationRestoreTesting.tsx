import MvpScaffold from '@/components/MvpScaffold'

const PersonalWorkstationRestoreTestingPage = () => {
  return (
    <MvpScaffold
      title="Restore Testing"
      description="MVP view for Restore Testing. Configure inputs, environment, and execution to generate results."
      route="/personal-workstation-edition/data-knowledge/restore-testing"
      todo={[
        "Connect Restore Testing KPIs and activity feed.",
        "Replace baseline metrics with live data sources.",
      ]}
    />
  )
}

export default PersonalWorkstationRestoreTestingPage
