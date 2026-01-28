import { CategoryHomeTemplate } from '../components/templates/CategoryHomeTemplate'
import { useIARouteContext } from '../navigation/iaContext'

export default function Future() {
  const routeContext = useIARouteContext()
  const features = routeContext.category?.features ?? []

  return (
    <CategoryHomeTemplate
      title="Future"
      description="Forward-looking experiments and speculative buildouts."
      features={features.map((feature) => ({
        title: feature.label,
        path: feature.route,
      }))}
    />
  )
}
