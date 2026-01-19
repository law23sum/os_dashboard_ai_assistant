import MvpScaffold from '@/components/MvpScaffold'

const GovernanceSecurityHomePage = () => {
  return (
    <MvpScaffold
      title="Governance & Security Home"
      description="MVP view for Governance & Security Home. Configure inputs, environment, and execution to generate results."
      route="/enterprise-control-plane-add-ons/governance-security"
      todo={[
        "Connect Governance & Security Home KPIs and activity feed.",
        "Replace baseline metrics with live data sources.",
      ]}
    />
  )
}

export default GovernanceSecurityHomePage
