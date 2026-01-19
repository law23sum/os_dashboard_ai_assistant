import MvpScaffold from '@/components/MvpScaffold'

const DataKnowledgeHomePage = () => {
  return (
    <MvpScaffold
      title="Data & Knowledge Home"
      description="MVP view for Data & Knowledge Home. Configure inputs, environment, and execution to generate results."
      route="/personal-workstation-edition/data-knowledge"
      todo={[
        "Connect Data & Knowledge Home KPIs and activity feed.",
        "Replace baseline metrics with live data sources.",
      ]}
    />
  )
}

export default DataKnowledgeHomePage
