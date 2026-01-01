import { CategoryHomeTemplate } from '../../components/templates/CategoryHomeTemplate'
import { useIARouteContext } from '../../navigation/iaContext'

export default function GovernanceSecurity() {
  const routeContext = useIARouteContext()
  const features = routeContext.category?.features ?? []

  return (
    <CategoryHomeTemplate
      title="Governance & Security"
      description="Policy, compliance, and security governance controls."
      features={features.map((feature) => ({
        title: feature.label,
        path: feature.route,
      }))}
    />
  )
}
