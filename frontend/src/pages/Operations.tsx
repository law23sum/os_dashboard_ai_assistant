import { CategoryHomeTemplate } from '../components/templates/CategoryHomeTemplate'
import { useIARouteContext } from '../navigation/iaContext'

export default function Operations() {
  const routeContext = useIARouteContext()
  const features = routeContext.category?.features ?? []

  return (
    <CategoryHomeTemplate
      title="Operations"
      description="Runbooks, reliability controls, and execution tooling."
      features={features.map((feature) => ({
        title: feature.label,
        path: feature.route,
      }))}
    />
  )
}
