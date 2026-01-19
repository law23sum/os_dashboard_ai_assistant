import MvpScaffold from '@/components/MvpScaffold'

const GovernanceSecurityApiKeysTokensPage = () => {
  return (
    <MvpScaffold
      title="API Keys & Tokens"
      description="MVP view for API Keys & Tokens. Configure inputs, environment, and execution to generate results."
      route="/enterprise-control-plane-add-ons/governance-security/api-keys-tokens"
      todo={[
        "Connect API Keys & Tokens KPIs and activity feed.",
        "Replace baseline metrics with live data sources.",
      ]}
    />
  )
}

export default GovernanceSecurityApiKeysTokensPage
